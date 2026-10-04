# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 16:27:01 2026

@author: simme
"""

# import necessary packages
from scipy.stats import ttest_ind, shapiro
import pandas as pd
import numpy as np
import itertools

# import mapping packages
import matplotlib.pyplot as plt
from matplotlib.pyplot import subplots, savefig, close

data_categorised = pd.read_excel('../MY_INPUTS/regional_seasonal_data.xlsx', 
                                 header=[0, 1, 2], index_col=0)

#%% testing for normal distribution

# for each column, plot a figure to check normal distribution
#for col in data_categorised.columns:
#    plt.figure()
    
#    plt.hist(data_categorised[col].dropna(),
#             bins=250,
#             color='Black',
#             edgecolor='Black')
    
#    plt.xlabel('Values')
#    plt.ylabel('Frequency')                                                 
    
#    plt.savefig(f'./PLOTS/testplot{col}.png', dpi=300)
#    close()
    
#print("[DONE] Saved map for plot") 
#%% shapiro-wilk test



#%% student t-test

# create a dictionary
t_results = {}
shapiro_results = {}

# for each unique combination of region and season...
for (region, season), subset in data_categorised.groupby(level=[0, 1], axis=1):
    
    # get the two spraying options
    cols = subset.columns
    
    # for both and unsprayed columns...
    for class1, class2 in itertools.combinations(cols, 2):

        # get data for sprayed points
        sprayed_data = subset[class1].dropna()
        # get data for unsprayed points
        unsprayed_data = subset[class2].dropna()
        
        # don't go ahead if there isn't much/is no data
        if len(sprayed_data) < 3 or len(unsprayed_data) <3:
            continue
        
        # get shapiro test scores & p values for sprayed data
        st_1, sp_1 = shapiro(
            sprayed_data)
        
        # get shapiro test scores & p values for unsprayed data
        st_2, sp_2 = shapiro(
            unsprayed_data)
        
        # do a student's t-test to assess difference b/w sprayed/unsprayed
        t_statistic, p_value = ttest_ind(
            sprayed_data,
            unsprayed_data,
            nan_policy='omit',
            alternative='greater'
            )
        
        key = (region, season)
        
        shapiro_results[key] = {
            'Shapiro p-value for sprayed': sp_1,
            'Sample size sprayed': len(sprayed_data),
            'Shapiro p-value for unsprayed': sp_2,
            'Sample size unsprayed': len(unsprayed_data)
            }
        
        t_results[key] = {
            't-stat': t_statistic,
            'p-value': p_value
            }
        
# define statistically significant threshold
threshold = 0.05
length = 30

# create a dataframe for the shapiro wilk test
shapiro_data = pd.DataFrame(shapiro_results).T

# define whether the shapiro tests were significant or not
normal_distribution = (shapiro_data['Shapiro p-value for sprayed'] > threshold) # i.e., data is normally distributed
abnormal_small = (shapiro_data['Shapiro p-value for sprayed'] < threshold & shapiro_data['Sample size sprayed'] < length)
abnormal_large = (shapiro_data['Shapiro p-value for sprayed'] < threshold & shapiro_data['Sample size sprayed'] > length)

shapiro_data.loc[normal_distribution, 'Use t-test?'] = 'Yes' #b/c data is normally distributed 
shapiro_data.loc[abnormal_large, 'Use t-test?'] = 'Yes' #b/c data is not normally distributed but sample size is <30 (large)
shapiro_data.loc[abnormal_small, 'Use t-test?'] = 'No' #b/c data is not normally distributed AND sample size is >30 (large)

# define whether the shapiro tests were significant or not
normal_distribution = (shapiro_data['Shapiro p-value for sprayed'] > threshold) # i.e., data is normally distributed
abnormal_small = (shapiro_data['Shapiro p-value for sprayed'] < threshold & shapiro_data['Sample size sprayed'] < length)
abnormal_large = (shapiro_data['Shapiro p-value for sprayed'] < threshold & shapiro_data['Sample size sprayed'] > length)

shapiro_data.loc[normal_distribution, 'Use t-test?'] = 'Yes' #b/c data is normally distributed 
shapiro_data.loc[abnormal_large, 'Use t-test?'] = 'Yes' #b/c data is not normally distributed but sample size is <30 (large)
shapiro_data.loc[abnormal_small, 'Use t-test?'] = 'No' #b/c data is not normally distributed AND sample size is >30 (large)


unsprayed_insig = (shapiro_data['Shapiro for unsprayed'] > threshold)
unsprayed_sig = (shapiro_data['Shapiro for unsprayed'] < threshold)

shapiro_data.loc[unsprayed_insig, 'Shapiro Uns Sig?'] = 'Not significant' # i.e., normally distributed
shapiro_data.loc[unsprayed_sig, 'Shapiro Uns Sig?'] = 'Significant'   #i.e., not normally distributed


t_test_data = pd.DataFrame(t_results).T




insignificance = (t_test_data['p-value'] > threshold)
significant = (t_test_data['p-value'] < threshold)

t_test_data.loc[insignificance, 't-test Significant?'] = 'Not significant'
t_test_data.loc[significant, 't-test Significant?'] = 'Significant'

t_test_data.to_excel('./testfordata.xlsx')

# MIGHT WANNA CHECK WITH SPSS MANUALLY, JUST IN CASE?