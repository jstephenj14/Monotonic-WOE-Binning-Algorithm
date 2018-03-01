# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import numpy as np
import pandas as pd
import scipy.stats.stats as stats

from sklearn.utils import check_random_state
from scipy.stats import norm

ir = IsotonicRegression()

os.getcwd()

os.chdir('C:\\Users\\jstep\\Downloads\\Credit Risk Analytics Pack\\Probablity of Default\\Supplements')

credit = pd.read_excel("PD.xls")

sample = credit[["goodbad","age"]]

y_ = ir.fit_transform(sample["age"], sample["goodbad"])

summary = sample.groupby(["age"]).agg({"goodbad":{"means":"mean",
                                                  "nsamples":"size",
                                                  "std_dev":"std"}})

summary.columns = summary.columns.droplevel(level=0)

summary = summary[["means","nsamples","std_dev"]]
summary = summary.reset_index()

summary["del_flag"] = 0
summary["std_dev"] = summary["std_dev"].fillna(0)

#summary.loc[1,"del_flag"] = 1

#summary = summary[summary.del_flag != 1]
#summary = summary.reset_index(drop=True)
    
    
#for i in range(len(summary)):   

while True:
    i = 0
    
    summary = summary[summary.del_flag != 1]
    summary = summary.reset_index(drop=True)
    while True:
        
        j = i+1
        
        print "Outside"
        print "i",i
        print "j",j
        
        if j >= len(summary):
            break
       
        if summary.iloc[j].means < summary.iloc[i].means:
            
            print "summary.iloc[i+j].means",summary.iloc[j].means        
            print "summary.iloc[i].means",summary.iloc[i].means        
            
            print("Inside If")        
            print "i",i
            print "j",j
            i = i+1
            continue
        else:  
            
            print "summary.iloc[i+j].means",summary.iloc[j].means        
            print "summary.iloc[i].means",summary.iloc[i].means    
            
            print("Inside Else")
            print "i",i
            print "j",j
            while True:        
                print("Inside While")
                print "i",i
                print "j",j
                n = summary.iloc[j].nsamples + summary.iloc[i].nsamples
                m = (summary.iloc[j].nsamples*summary.iloc[j].means +
                       summary.iloc[i].nsamples*summary.iloc[i].means)/n
                     
                if n == 2:
                    s = np.std([summary.iloc[j].means,summary.iloc[i].means])
                else:
                    s = np.sqrt((summary.iloc[j].nsamples*((summary.iloc[j].std_dev)**2)+
                                summary.iloc[i].nsamples*((summary.iloc[i].std_dev)**2))/n)
                
                summary.loc[i,"nsamples"] = n
                summary.loc[i,"means"] = m
                summary.loc[i,"std_dev"] = s
                
                print "n",n,"m",m,"s",s
                summary.loc[j,"del_flag"] = 1
                
                j = j + 1
                if summary.loc[j,"means"] < summary.loc[i,"means"]:
                   i = j
                   break
    dels = np.sum(summary["del_flag"])
    if dels == 0:
        break
#WHEW
        
summary = summary1
n_threshold = 100
defaults_threshold = 30
p_threshold = 0.05
while True:
    summary["means_lead"] = summary["means"].shift(-1)
    summary["nsamples_lead"] = summary["nsamples"].shift(-1)
    summary["std_dev_lead"] = summary["std_dev"].shift(-1)
    
    
    summary["est_nsamples"] =  summary["nsamples_lead"] +summary["nsamples"] 
    summary["est_means"] = (summary["means_lead"]*summary["nsamples_lead"] + 
                            summary["means"]*summary["nsamples"])/summary["est_nsamples"]
    
    summary["est_std_dev2"] = (summary["nsamples_lead"]*summary["std_dev_lead"]**2 + 
                              summary["nsamples"]*summary["std_dev"]**2)/(summary["est_nsamples"]-2)
     
    summary["z_value"] =  (summary["means"] - summary["means_lead"])/np.sqrt(summary["est_std_dev2"]*(1/summary["nsamples"] + 1/summary["nsamples_lead"]))
    
    summary["p_value"] = 1 - norm.cdf(summary["z_value"])
    
    condition = (summary["nsamples"]<n_threshold)|(summary["nsamples_lead"]<n_threshold)|(summary["means"]*summary["nsamples"]<defaults_threshold)|(summary["means_lead"]*summary["nsamples_lead"]<defaults_threshold)
            
    summary[condition].p_value = summary[condition].p_value + 1
    
    summary["p_value"] = summary.apply(lambda row: row["p_value"] + 1 if (row["nsamples"]<n_threshold)|(row["nsamples_lead"]<n_threshold)|(row["means"]*row["nsamples"]<defaults_threshold)|(row["means_lead"]*row["nsamples_lead"]<defaults_threshold)
             else row["p_value"], axis = 1 )
  
    max_p = max(summary["p_value"])   
    row_of_maxp = summary['p_value'].idxmax()
    row_delete = row_of_maxp + 1
    
    if max_p>p_threshold:
        summary = summary.drop(summary.index[row_delete])
        summary = summary.reset_index(drop=True)
    else:
        break
    
    summary["means"] = summary.apply(lambda row: row["est_means"] if row["p_value"] == max_p else row["means"], axis = 1 )
    summary["nsamples"] = summary.apply(lambda row: row["est_nsamples"] if row["p_value"] == max_p else row["nsamples"], axis = 1 )
    summary["std_dev"] = summary.apply(lambda row: np.sqrt(row["est_std_dev2"]) if row["p_value"] == max_p else row["std_dev"], axis = 1 )
    
WOE_summary = summary[["age","nsamples","means"]]

WOE_summary["bads"] = WOE_summary["means"]*WOE_summary["nsamples"]
WOE_summary["goods"] = WOE_summary["nsamples"] - WOE_summary["bads"]

TotalGoods = np.sum(WOE_summary["goods"])
TotalBads = np.sum(WOE_summary["bads"])

WOE_summary["dist_good"] = WOE_summary["goods"]/TotalGoods
WOE_summary["dist_bad"]  = WOE_summary["bads"]/TotalBads

WOE_summary["WOE"] = np.log(WOE_summary["dist_good"] / WOE_summary["dist_bad"]) 

WOE_summary["IV_components"] = (WOE_summary["dist_good"] - WOE_summary["dist_bad"])*WOE_summary["WOE"] 

Total_IV = np.sum(WOE_summary["IV_components"])