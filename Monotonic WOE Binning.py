import os
import numpy as np
import pandas as pd
import scipy.stats as stats
import warnings

warnings.filterwarnings("ignore")
### YAY I'M NOW IN DEV!

def WOE_Binning(Y, dataset, sign=False, n_threshold=100, Y_threshold=30, p_threshold=0.05):
    column = dataset.columns[dataset.columns != Y][0]

    summary = dataset.groupby([column]).agg({"goodbad": {"means": "mean",
                                                         "nsamples": "size",
                                                         "std_dev": "std"}})

    summary.columns = summary.columns.droplevel(level=0)

    summary = summary[["means", "nsamples", "std_dev"]]
    summary = summary.reset_index()

    summary["del_flag"] = 0
    summary["std_dev"] = summary["std_dev"].fillna(0)

    summary = summary.sort_values([column], ascending=sign)

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
                        s = np.sqrt((summary.iloc[j].nsamples * ((summary.iloc[j].std_dev) ** 2) +
                                     summary.iloc[i].nsamples * ((summary.iloc[i].std_dev) ** 2)) / n)

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

        condition = (summary["nsamples"] < n_threshold) | (summary["nsamples_lead"] < n_threshold) | (
                    summary["means"] * summary["nsamples"] < Y_threshold) | (
                                summary["means_lead"] * summary["nsamples_lead"] < Y_threshold)

        summary[condition].p_value = summary[condition].p_value + 1

        summary["p_value"] = summary.apply(
            lambda row: row["p_value"] + 1 if (row["nsamples"] < n_threshold) | (row["nsamples_lead"] < n_threshold) | (
                        row["means"] * row["nsamples"] < Y_threshold) | (
                                                          row["means_lead"] * row["nsamples_lead"] < Y_threshold)
            else row["p_value"], axis=1)

        max_p = max(summary["p_value"])
        row_of_maxp = summary['p_value'].idxmax()
        row_delete = row_of_maxp + 1

        if max_p > p_threshold:
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

    WOE_summary = summary[[column, "nsamples", "means"]]

    WOE_summary["bads"] = WOE_summary["means"] * WOE_summary["nsamples"]
    WOE_summary["goods"] = WOE_summary["nsamples"] - WOE_summary["bads"]

    TotalGoods = np.sum(WOE_summary["goods"])
    TotalBads = np.sum(WOE_summary["bads"])

    WOE_summary["dist_good"] = WOE_summary["goods"] / TotalGoods
    WOE_summary["dist_bad"] = WOE_summary["bads"] / TotalBads

    WOE_summary["WOE_" + column] = np.log(WOE_summary["dist_good"] / WOE_summary["dist_bad"])

    WOE_summary["IV_components"] = (WOE_summary["dist_good"] - WOE_summary["dist_bad"]) * WOE_summary["WOE_" + column]

    print(WOE_summary)
    Total_IV = np.sum(WOE_summary["IV_components"])
    print(Total_IV)

    def dummy(row):
        return "-".join(map(str, np.sort([row[column], row[column + "_shift"]])))

    WOE_summary = WOE_summary.sort_values(by=[column]).reset_index(drop=True)

    if sign == False:
        shift_var = 1
        bucket = True
    else:
        shift_var = -1
        bucket = False

    WOE_summary[column + "_shift"] = WOE_summary[column].shift(shift_var)

    if sign == False:
        WOE_summary.loc[0, column + "_shift"] = -np.inf
        bins = np.sort(list(WOE_summary[column]) + [-np.Inf])
    else:
        WOE_summary.loc[len(WOE_summary) - 1, column + "_shift"] = np.inf
        bins = np.sort(list(WOE_summary[column]) + [np.Inf])

    WOE_summary["labels"] = WOE_summary.apply(dummy, axis=1)

    dataset["bins"] = pd.cut(dataset[column], bins, labels=WOE_summary["labels"], right=bucket, precision=0)

    dataset["bins"] = dataset["bins"].astype(str)
    dataset['bins'] = dataset['bins'].map(lambda x: x.lstrip('[').rstrip(')'))

    final_table = dataset.set_index("bins").join(WOE_summary[["WOE_" + column, "labels"]].set_index("labels"))
    final_table = final_table.reset_index().rename(index=str, columns={"index": column + "_buckets"})

    return final_table


import os
import numpy as np
import pandas as pd
import scipy.stats as stats
import warnings

warnings.filterwarnings("ignore")

os.getcwd()

os.chdir('C:\\Users\\jstep\\Downloads\\Credit Risk Analytics Pack\\Probablity of Default\\Supplements')

credit = pd.read_excel("PD.xls")
duration_WOE = WOE_Binning("goodbad", credit[["goodbad", "duration"]], sign=False)
