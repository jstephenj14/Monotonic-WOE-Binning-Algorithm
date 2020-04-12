from monotonic_binning.monotonic_woe_binning import Binning
import os
import pandas as pd

# Data available at https://online.stat.psu.edu/stat508/resource/analysis/gcd
train = pd.read_csv("Training50.csv")
test = pd.read_csv("Test50.csv")

var = "Age..years." # variable to be binned
y_var = "Creditability" # the target variable

bin_object = Binning(y_var, n_threshold = 50, y_threshold = 10, p_threshold = 0.35, sign=False)
bin_object.fit(train[[y_var, var]])

# Print WOE summary
print(bin_object.woe_summary)

# The bin cut-points in an array
print(bin_object.bins)

test_transformed = bin_object.transform(test)