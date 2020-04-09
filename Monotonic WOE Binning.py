
import os
import pandas as pd
import scipy.stats as stats
import warnings
import numpy as np

desired_width = 320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns', 130)
warnings.filterwarnings("ignore")
os.getcwd()

class Binning:

    def __init__(self, y, dataset, n_threshold, y_threshold, p_threshold,sign=False):
        self.n_threshold = n_threshold
        self.y_threshold = y_threshold
        self.p_threshold = p_threshold
        self.y = y
        self.dataset = dataset
        self.column = self.dataset.columns[self.dataset.columns != self.y][0]
        self.sign = sign

        self.init_summary = pd.DataFrame()
        self.bin_summary = pd.DataFrame()
        self.pvalue_summary = pd.DataFrame()

        self.total_iv = object
        self.woe_summary = object
        self.bins = object

    def generate_summary(self):

        self.init_summary = self.dataset.groupby([self.column]).agg({self.y: {"means": "mean", "nsamples": "size","std_dev": "std"}})

        self.init_summary.columns = self.init_summary.columns.droplevel(level=0)

        self.init_summary = self.init_summary[["means", "nsamples", "std_dev"]]
        self.init_summary = self.init_summary.reset_index()

        self.init_summary["del_flag"] = 0
        self.init_summary["std_dev"] = self.init_summary["std_dev"].fillna(0)

        self.init_summary = self.init_summary.sort_values([self.column], ascending=self.sign)

    def combine_bins(self):
        summary = self.init_summary.copy()

        while True:
            i = 0
            summary = summary[summary.del_flag != 1]
            summary = summary.reset_index(drop=True)
            while True:

                j = i + 1

                if j >= len(summary):
                    break

                if summary.iloc[j].means < summary.iloc[i].means:
                    i = i + 1
                    continue
                else:
                    while True:
                        n = summary.iloc[j].nsamples + summary.iloc[i].nsamples
                        m = (summary.iloc[j].nsamples * summary.iloc[j].means +
                             summary.iloc[i].nsamples * summary.iloc[i].means) / n

                        if n == 2:
                            s = np.std([summary.iloc[j].means, summary.iloc[i].means])
                        else:
                            s = np.sqrt((summary.iloc[j].nsamples * (summary.iloc[j].std_dev ** 2) +
                                         summary.iloc[i].nsamples * (summary.iloc[i].std_dev ** 2)) / n)

                        summary.loc[i, "nsamples"] = n
                        summary.loc[i, "means"] = m
                        summary.loc[i, "std_dev"] = s
                        summary.loc[j, "del_flag"] = 1

                        j = j + 1
                        if j >= len(summary):
                            break
                        if summary.loc[j, "means"] < summary.loc[i, "means"]:
                            i = j
                            break
                if j >= len(summary):
                    break
            dels = np.sum(summary["del_flag"])
            if dels == 0:
                break

        self.bin_summary = summary.copy()

    def calculate_pvalues(self):
        summary = self.bin_summary.copy()
        while True:
            summary["means_lead"] = summary["means"].shift(-1)
            summary["nsamples_lead"] = summary["nsamples"].shift(-1)
            summary["std_dev_lead"] = summary["std_dev"].shift(-1)

            summary["est_nsamples"] = summary["nsamples_lead"] + summary["nsamples"]
            summary["est_means"] = (summary["means_lead"] * summary["nsamples_lead"] +
                                    summary["means"] * summary["nsamples"]) / summary["est_nsamples"]

            summary["est_std_dev2"] = (summary["nsamples_lead"] * summary["std_dev_lead"] ** 2 +
                                       summary["nsamples"] * summary["std_dev"] ** 2) / (summary["est_nsamples"] - 2)

            summary["z_value"] = (summary["means"] - summary["means_lead"]) / np.sqrt(
                summary["est_std_dev2"] * (1 / summary["nsamples"] + 1 / summary["nsamples_lead"]))

            summary["p_value"] = 1 - stats.norm.cdf(summary["z_value"])

            summary["p_value"] = summary.apply(
                lambda row: row["p_value"] + 1 if (row["nsamples"] < self.n_threshold) |
                                                  (row["nsamples_lead"] < self.n_threshold) |
                                                  (row["means"] * row["nsamples"] < self.y_threshold) |
                                                  (row["means_lead"] * row["nsamples_lead"] < self.y_threshold)
                else row["p_value"], axis=1)

            max_p = max(summary["p_value"])
            row_of_maxp = summary['p_value'].idxmax()
            row_delete = row_of_maxp + 1

            if max_p > self.p_threshold:
                summary = summary.drop(summary.index[row_delete])
                summary = summary.reset_index(drop=True)
            else:
                break

            summary["means"] = summary.apply(lambda row: row["est_means"] if row["p_value"] == max_p else row["means"],
                                             axis=1)
            summary["nsamples"] = summary.apply(
                lambda row: row["est_nsamples"] if row["p_value"] == max_p else row["nsamples"], axis=1)
            summary["std_dev"] = summary.apply(
                lambda row: np.sqrt(row["est_std_dev2"]) if row["p_value"] == max_p else row["std_dev"], axis=1)

        self.pvalue_summary = self.bin_summary.copy()

    def calculate_woe(self):
        woe_summary = self.pvalue_summary[[self.column, "nsamples", "means"]]

        woe_summary["bads"] = woe_summary["means"] * woe_summary["nsamples"]
        woe_summary["goods"] = woe_summary["nsamples"] - woe_summary["bads"]

        total_goods = np.sum(woe_summary["goods"])
        total_bads = np.sum(woe_summary["bads"])

        woe_summary["dist_good"] = woe_summary["goods"] / total_goods
        woe_summary["dist_bad"] = woe_summary["bads"] / total_bads

        woe_summary["WOE_" + self.column] = np.log(woe_summary["dist_good"] / woe_summary["dist_bad"])

        woe_summary["IV_components"] = (woe_summary["dist_good"] - woe_summary["dist_bad"]) * woe_summary[
            "WOE_" + self.column]

        self.total_iv = np.sum(woe_summary["IV_components"])
        self.woe_summary = woe_summary

    def generate_bin_labels(self,row):
        return "-".join(map(str, np.sort([row[self.column], row[self.column + "_shift"]])))

    def generate_final_dataset(self):
        if self.sign == False:
            shift_var = 1
            bucket = True
        else:
            shift_var = -1
            bucket = False

        self.woe_summary[self.column + "_shift"] = self.woe_summary[self.column].shift(shift_var)

        if self.sign == False:
            self.woe_summary.loc[0, self.column + "_shift"] = -np.inf
            self.bins = np.sort(list(self.woe_summary[self.column]) + [np.Inf,-np.Inf])
        else:
            self.woe_summary.loc[len(self.woe_summary) - 1, self.column + "_shift"] = np.inf
            self.bins = np.sort(list(self.woe_summary[self.column]) + [np.Inf,-np.Inf])

        self.woe_summary["labels"] = self.woe_summary.apply(self.generate_bin_labels, axis=1)

        self.dataset["bins"] = pd.cut(self.dataset[self.column], self.bins, right=bucket, precision=0)
        #self.dataset["bins"] = pd.cut(self.dataset[self.column], self.bins, labels=self.woe_summary["labels"], right=bucket, precision=0)

        self.dataset["bins"] = self.dataset["bins"].astype(str)
        self.dataset['bins'] = self.dataset['bins'].map(lambda x: x.lstrip('[').rstrip(')'))

    def __call__(self):
        self.generate_summary()
        self.combine_bins()
        self.calculate_pvalues()
        self.calculate_woe()
        self.generate_final_dataset()

        return self.dataset

#duration_WOE = WOE_Binning("goodbad", credit[["goodbad", "duration"]], sign=False)
#def WOE_Binning(Y, dataset, sign=False, n_threshold=100, Y_threshold=30, p_threshold=0.05):

os.chdir('C:\\Users\\jstep\\Downloads\\Credit Risk Analytics Pack\\Probablity of Default\\Supplements')
credit = pd.read_excel("PD.xls")

bin_object = Binning("goodbad", credit[["goodbad", "duration"]],n_threshold = 100,y_threshold = 30,p_threshold = 0.05)
final_data = bin_object()