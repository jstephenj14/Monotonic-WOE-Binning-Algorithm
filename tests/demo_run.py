from monotonic_binning.monotonic_woe_binning import Binning
import os
import pandas as pd

# Available at https://online.stat.psu.edu/stat508/resource/analysis/gcd

train = pd.read_csv("Training50.csv")
test = pd.read_csv("Test50.csv")

var = "Age..years."
bin_object = Binning("Creditability", n_threshold = 50, y_threshold = 10, p_threshold = 0.35, sign=False)
bin_object.fit(train[["Creditability", var]])

# Print WOE summary
print(bin_object.woe_summary)

test_transformed = bin_object.transform(test)