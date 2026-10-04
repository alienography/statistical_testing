# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 16:27:01 2026

@author: simme
"""

# import necessary packages
from scipy.stats import ttest_ind, shapiro, mannwhitneyu
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
mann_whitney_results = {}

# for each unique combination of region and season...
for (region, season), subset in data_categorised.groupby(level=[0, 1], axis=1):
    
    # get the two spraying options
    cols = subset.columns
    
    # for both and unsprayed columns...
    for class1, class2 in itertools.combinations(cols, 2):
        
        # define the identifiers
        key = (region, season)
        
        # get data for sprayed points
        sprayed_data = subset[class1].dropna()
        # get data for unsprayed points
        unsprayed_data = subset[class2].dropna()
        
        # don't go ahead if there isn't much/is no data
        if len(sprayed_data) < 3 or len(unsprayed_data) <3:
            continue
        #============ SHAPIRO-WILK TEST FOR NORMALITY ====================
        # get shapiro test scores & p values for sprayed data
        st_1, sp_1 = shapiro(
            sprayed_data)
        
        # get shapiro test scores & p values for unsprayed data
        st_2, sp_2 = shapiro(
            unsprayed_data)
        
        # create a dictionary with the results from the shapiro-wilk
        # and sample sizes
        shapiro_results[key] = {
            'Shapiro p-value for sprayed': sp_1,
            'Sample size sprayed': len(sprayed_data),
            'Shapiro p-value for unsprayed': sp_2,
            'Sample size unsprayed': len(unsprayed_data)
            }
        #============ STUDENT'S T-TEST ====================
        # do a student's t-test to assess difference b/w sprayed/unsprayed
        t_statistic, p_value = ttest_ind(
            sprayed_data,
            unsprayed_data,
            nan_policy='omit',
            #alternative='less'
            )
        # create a dictionary with the results from the t-test
        t_results[key] = {
            't-stat': t_statistic,
            'p-value': p_value
            }
        
        #============ MANN-WHITNEY U TEST ====================
        # do a mann-whitney u test
        mann_statistic, mann_p = mannwhitneyu(
            sprayed_data,
            unsprayed_data,
            #alternative='less',
            nan_policy='omit')
        
        # make a dictionary with the mann-whitney results
        mann_whitney_results[key] = {
            'mann-statistic': mann_statistic,
            'p-value': mann_p
            }
# =================== DEFINING THRESHOLDS =====================        
# define statistically significant threshold
threshold = 0.05
length = 50

# =============== SHAPIRO-WILK PROCESSING =====================        

# create a dataframe for the shapiro wilk test
shapiro_data = pd.DataFrame(shapiro_results).T

# define whether the shapiro tests were significant or not
normal_distribution = (
    (shapiro_data['Shapiro p-value for sprayed'] > threshold) &
    (shapiro_data['Shapiro p-value for unsprayed'] > threshold)
    )# i.e., sprayed & unsprayed data is normally distributed

# define cases where t-test can still be peformed
abnormal_large = (
    (
     (shapiro_data['Shapiro p-value for sprayed'] < threshold) &
     (shapiro_data['Sample size sprayed'] > length) &
     (shapiro_data['Shapiro p-value for unsprayed'] < threshold) &
     (shapiro_data['Sample size unsprayed'] > length)
     )
    |
                  
    (
     (shapiro_data['Shapiro p-value for sprayed'] > threshold) &
     (shapiro_data['Shapiro p-value for unsprayed'] < threshold) &
     (shapiro_data['Sample size unsprayed'] > length)
     )
    |
                  
    (
     (shapiro_data['Shapiro p-value for sprayed'] < threshold) &
     (shapiro_data['Sample size sprayed'] > length) &
     (shapiro_data['Shapiro p-value for unsprayed'] > threshold)
     )
                  )

# set a column with a default of not using a t-test
shapiro_data['Use t-test?'] = 'No'

# overrrule this in certain cases
shapiro_data.loc[normal_distribution, 'Use t-test?'] = 'Yes, ND' #b/c data is normally distributed 
shapiro_data.loc[abnormal_large, 'Use t-test?'] = 'Yes, LSS' #b/c data is not normally distributed but sample size is <30 (large)

# export shapiro-wilk data to excel
shapiro_data.to_excel('./testfornormality.xlsx')

# ============ STUDENT'S T-TEST PROCESSING =====================        

# create a dataframe from the results of the t-test
t_test_data = pd.DataFrame(t_results).T

# define whether the results are significant
insignificance = (t_test_data['p-value'] > threshold)
significant = (t_test_data['p-value'] < threshold)

# make a column saying whether the results are significant or not
t_test_data.loc[insignificance, 't-test Significant?'] = 'Not significant'
t_test_data.loc[significant, 't-test Significant?'] = 'Significant'

# export the data to excel
t_test_data.to_excel('./testfordata.xlsx')

# ============ MANN-WHITNEY U PROCESSING =====================        
# make a dataframe from mann-whitney u test
mann_whitney = pd.DataFrame(mann_whitney_results).T

# define the significance of the results
insignificance = (mann_whitney['p-value'] > threshold)
significant = (mann_whitney['p-value'] < threshold)

# make a column saying whether the results are significant or not
mann_whitney.loc[insignificance, 'Mann-Whitney U test Significant?'] = 'Not significant'
mann_whitney.loc[significant, 'Mann-Whitney U test Significant?'] = 'Significant'

# export the data to excel
mann_whitney.to_excel('./mannwhitney.xlsx')

# ============== MERGE THE DATAFRAMES ==========================
tests_merged = pd.merge(shapiro_data, t_test_data, how='inner', left_index=True, right_index=True)
tests_merged2 = pd.merge(tests_merged, mann_whitney, how='inner', left_index=True, right_index=True)

tests_merged2.to_excel('./mergedtest_2tail.xlsx')

# MIGHT WANNA CHECK WITH SPSS MANUALLY, JUST IN CASE?