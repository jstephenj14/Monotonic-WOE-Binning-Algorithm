from monotonic_woe_binning import Binning
import os
import pandas as pd

# Sample data set 1
os.chdir('C:\\Users\\jstep\\Downloads\\Credit Risk Analytics Pack\\Probablity of Default\\Supplements')
credit = pd.read_excel("PD.xls")

train_data = credit.iloc[0:900]
test_data = credit.iloc[900:]

bin_object = Binning("goodbad", n_threshold = 100,y_threshold = 30,p_threshold = 0.05, sign=True)
bin_object.fit(train_data[["goodbad", "age"]])

# Sample data sets 2 German data
train = pd.read_csv("Training50.csv")
test = pd.read_csv("Test50.csv")

var = "Age..years."
bin_object = Binning("Creditability", n_threshold = 100, y_threshold = 10, p_threshold = 0.05, sign=False)
bin_object.fit(train[["Creditability", var]])

# train.groupby([var]).size()

test_transformed = bin_object.transform(test)