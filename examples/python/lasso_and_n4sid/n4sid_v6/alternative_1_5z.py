#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 18:25:17 2021
@author: joseleiva
"""
from __future__ import division

#Import all the metrics to evaluate the accuracy of the N4SID Algorithm with the selected order
import os
from sklearn.metrics import r2_score
from sklearn.metrics import median_absolute_error
#from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import mean_squared_error
import datetime
import matplotlib.dates as mdates

from past.utils import old_div

# Checking path to access other files
try:
    from sippy import *
except ImportError:
    import sys, os

    sys.path.append(os.pardir)
    from sippy import *
import matplotlib.pyplot as plt
import numpy as np
from sippy import functionset as fset
from sippy import functionsetSIM as fsetSIM
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('science')
# Not sure how to get this to work. Document the command line call if you can.
# plt.style.use('science')
#def gap(a):
#    return a + 86460
data_file = "SOM3N4SID_clean3_v2.csv"
if not os.path.exists(data_file):
    print("*************** Input data file does not exist! *****************")
    print("Download from here: https://drive.google.com/open?id=1Bkl0lqUO57Ft-yoFbLtZYS4kK5-F0b94")
    print(f"Unzip (`7z x {data_file}.7z) and place resulting CSV into the same folder as this file.")
    exit(1)

data = pd.read_csv(data_file)  # dataset from January to January 12 months
df = pd.DataFrame(data)
df.mean()
df = df.fillna(df.mean())

# Sample at 300 seconds
df = df.loc[df['Time'] % 300.0 == 0]
#print ()
#print ('Check')
#print(df[['Core_T','P1_T']])

# Create a date time column based on Jan 1, 2019 data (no leapyear)
basetime = 1546300800  # 1/1/2019 00:00:00 (epoch time in seconds)
#df[df['Time'] > 31449540] = df[df['Time'] > 31449540].apply(gap)
df['datetime'] = pd.to_datetime(basetime + df['Time'], unit='s', errors='coerce')
print(df['P1_T'])

# Set when you want to start the test data (actual data start). The
# 2020 year is a misnomer and is really just the same weather data ran twice (TODO: verify this)
#   ** The dates below are from the original period, when shifting to 2020/1/1, the model doesn't hold
#   ** up nearly as well.
#   ** [Train Data Set] Start: 2019-01-31 02:20:00 End: 2019-12-28 04:35:00
#   ** [Test Data Set] Start: 2019-12-28 04:40:00 End: 2020-01-27 06:55:00
# test_date_start = datetime.datetime(2019, 12, 28, 4, 40, 0)
# test_date_end = datetime.datetime(2020, 1, 27, 6, 55, 0)
# train_date_start = datetime.datetime(2019, 1, 31, 2, 20, 0)

test_date_start = datetime.datetime(2020, 1, 4, 0, 0, 0)
test_date_end = test_date_start + datetime.timedelta(days=4)
train_date_start = test_date_start - datetime.timedelta(days=26)

#MODEL 1 of N4SID: FIRST 4 MONTHS OF THE DATASET (JAN-FEB-MARCH-)

# The methods below are no long
# m=df.shape[0]
# starting_month=1; # 1=JANUARY, 2=FEBRUARY, 3=MARCH..., 12= DECEMBER #
# months_offset=1+(starting_month-1);
# week_number=0;
# offset=((months_offset)*4.3);
# k=11*4.3; #number of weeks of data for the estimationand training the N4SID
# f=1*4.3; # number of estimated weeks with the N4SID algorithm
# w_y=2*52;  # Number of weeks during the year
# j=int((w_y-k-offset)/(f));

for p in range(1):
    print("Model number: ", p)
    # t_0 = int(i*4.3*m/w_y)+int(offset*m/w_y)
    # t_1 = t_0+int(m*k/w_y)
    # t_2 = t_1+int(m*f/w_y)

    df1 = df[(df['datetime'] >= train_date_start) & (df['datetime'] < test_date_start)]
    # df1=df.iloc[t_0:t_1];
    print(f"[Train Data Set] Start: {df1.iloc[0]['datetime']} End: {df1.iloc[-1]['datetime']}")

    df1_test = df[(df['datetime'] >= test_date_start) & (df['datetime'] < test_date_end )]
    # df1_test =df.iloc[t_1:t_2]
    print(f"[Test Data Set] Start: {df1_test.iloc[0]['datetime']} End: {df1_test.iloc[-1]['datetime']}")

    # Save off the training and test dataset for 100 records to allow for easy inspection
    # starting at t_1.
    dfsmall = df1.iloc[0:100]
    dfsmall.to_csv('SOM3N4SID_clean3_train_downsampled.csv')
    dfsmall = df1_test.iloc[0:100]
    dfsmall.to_csv('SOM3N4SID_clean3_test_downsampled.csv')

    Time1 = np.array([df1['Time'].values.tolist()])
    Time_months1 = Time1/24/3600/30
    ##
    Time1_test = np.array([df1_test['Time'].values.tolist()])
    Time_months1_test = Time1_test/24/3600/30

    ## Definition of the Inputs Vector. Training dataset

    # Order matters! --- Make sure to add the variable names to the 'list_of_var_colnames' so
    # that the resulting dataframe/csv file can be read into the dompc world with ease.
    list_of_vars = [
        'T_OA', 'HgloHor1', 'P1_OccN', 'P1_IntGaiTot', 'P1_HeaPow', 'P1_FanPow', 'P1_OAVol',
    ]
    U1 = [df1[x].values.tolist() for x in list_of_vars]

    # U1=[
    #     df1['T_OA'].values.tolist(),
    #     df1['HgloHor'].values.tolist(),
    #
    #     # (df1['Hea_term_core']-df1['Core_T']).values.tolist(),
    #     # df1['Coo_term_core'].values.tolist(),
    #     # df1['Inf_term_core'].values.tolist(),
    #     # df1['Core_QconFlow'].values.tolist(),
    #     # df1['Core_OccN'].values.tolist(),
    #
    #
    #     # df1['Hea_term_P1'].values.tolist(),
    #     # df1['Coo_term_P1'].values.tolist(),
    #
    #     df1['P1_OccN'].values.tolist(),
    #     df1['P1_IntGaiTot'].values.tolist(),
    #     df1['P1_HeaPow'].values.tolist(),
    #     df1['P1_FanPow'].values.tolist(),
    #     df1['P1_OAVol'].values.tolist(),
    #
    #
    #     #
    #     # df1['Hea_term_P2'].values.tolist(),
    #     # df1['Coo_term_P2'].values.tolist(),
    #     # df1['Inf_term_P2'].values.tolist(),
    #     # df1['P2_QconFlow'].values.tolist(),
    #     # df1['P2_OccN'].values.tolist(),
    #     #
    #     # df1['Hea_term_P3'].values.tolist(),
    #     # df1['Coo_term_P3'].values.tolist(),
    #     # df1['Inf_term_P3'].values.tolist(),
    #     # df1['P3_QconFlow'].values.tolist(),
    #     # df1['P3_OccN'].values.tolist(),
    #     #
    #     # df1['Hea_term_P4'].values.tolist(),
    #     # df1['Coo_term_P4'].values.tolist(),
    #     # df1['Inf_term_P4'].values.tolist(),
    #     # df1['P4_QconFlow'].values.tolist(),
    #     # df1['P4_OccN'].values.tolist()
    #
    #     ]
    #    ,df1['HgloHor'].values.tolist(),df1['P1_IntGaiTot'].values.tolist(),df1['P1_OccN'].values.tolist(),df1['P1_HeaSet'].values.tolist(),df1['P1_CooSet'].values.tolist()
    #    ,df1['HgloHor'].values.tolist(),df1['P1_IntGaiTot'].values.tolist(),df1['P1_OccN'].values.tolist()
    #    df1['Core_T_prev'].values.tolist(),df1['P1_T_prev'].values.tolist(),df1['P2_T_prev'].values.tolist(),df1['P3_T_prev'].values.tolist(),df1['P4_T_prev'].values.tolist(),
    #U1 = [df1['OA_T'].values.tolist(),df1['Wea_HgloHor'].values.tolist(),df1['Wea_TWetBul'].values.tolist(),df1['Core_FanPow'].values.tolist(),df1['P1_FanPow'].values.tolist(),df1['P2_FanPow'].values.tolist(),df1['P3_FanPow'].values.tolist(),df1['P4_FanPow'].values.tolist(),df1['Core_HeaSet'].values.tolist(),df1['P1_HeaSet'].values.tolist(),df1['P2_HeaSet'].values.tolist(),df1['P3_HeaSet'].values.tolist(),df1['P4_HeaSet'].values.tolist(),df1['Core_CooSet'].values.tolist(),df1['P1_CooSet'].values.tolist(),df1['P2_CooSet'].values.tolist(),df1['P3_CooSet'].values.tolist(),df1['P4_CooSet'].values.tolist(),df1['Core_VFRSet'].values.tolist(),df1['P1_VFRSet'].values.tolist(),df1['P2_VFRSet'].values.tolist(),df1['P3_VFRSet'].values.tolist(),df1['P4_VFRSet'].values.tolist()]

    #    U1 = [df1['Core_T_before2'].values.tolist(),df1['P1_T_before2'].values.tolist(),df1['P2_T_before2'].values.tolist(),df1['P3_T_before2'].values.tolist(),df1['P4_T_before2'].values.tolist(),df1['OA_T'].values.tolist(),df1['Wea_HgloHor'].values.tolist(),df1['Wea_TWetBul'].values.tolist(),df1['Core_HeaSet'].values.tolist(),df1['P1_HeaSet'].values.tolist(),df1['P2_HeaSet'].values.tolist(),df1['P3_HeaSet'].values.tolist(),df1['P4_HeaSet'].values.tolist(),df1['Core_FanPow'].values.tolist(),df1['P1_FanPow'].values.tolist(),df1['P2_FanPow'].values.tolist(),df1['P3_FanPow'].values.tolist(),df1['P4_FanPow'].values.tolist(),df1['Core_CooSet'].values.tolist(),df1['P1_CooSet'].values.tolist(),df1['P2_CooSet'].values.tolist(),df1['P3_CooSet'].values.tolist(),df1['P4_CooSet'].values.tolist(),df1['Core_VFRSet'].values.tolist(),df1['P1_VFRSet'].values.tolist(),df1['P2_VFRSet'].values.tolist(),df1['P3_VFRSet'].values.tolist(),df1['P4_VFRSet'].values.tolist(),df1['Cor_MisGai'].values.tolist(),df1['P1_MisGai'].values.tolist(),df1['P2_MisGai'].values.tolist(),df1['P3_MisGai'].values.tolist(),df1['P4_MisGai'].values.tolist(),df1['Core_TotIntGai'].values.tolist(),df1['P1_TotIntGai'].values.tolist(),df1['P2_TotIntGai'].values.tolist(),df1['P3_TotIntGai'].values.tolist(),df1['P4_TotIntGai'].values.tolist()]
    #    U1 = [df1['Wea_HgloHor'].values.tolist(),df1['OA_T'].values.tolist(),df1['Core_HeaSet'].values.tolist(),df1['P1_HeaSet'].values.tolist(),df1['P2_HeaSet'].values.tolist(),df1['P3_HeaSet'].values.tolist(),df1['P4_HeaSet'].values.tolist(),df1['Core_CooSet'].values.tolist(),df1['P1_CooSet'].values.tolist(),df1['P2_CooSet'].values.tolist(),df1['P3_CooSet'].values.tolist(),df1['P4_CooSet'].values.tolist(),df1['Core_VFRSet'].values.tolist(),df1['P1_VFRSet'].values.tolist(),df1['P2_VFRSet'].values.tolist(),df1['P3_VFRSet'].values.tolist(),df1['P4_VFRSet'].values.tolist()]
    #    U1 = [df1['OA_T'].values.tolist(),df1['Wea_HgloHor'].values.tolist(),df1['hour'].values.tolist(),df1['day'].values.tolist(),df1['Core_HeaPow'].values.tolist(),df1['P1_HeaPow'].values.tolist(),df1['P2_HeaPow'].values.tolist(),df1['P3_HeaPow'].values.tolist(),df1['P4_HeaPow'].values.tolist(),df1['Core_CooPow'].values.tolist(),df1['P1_CooPow'].values.tolist(),df1['P2_CooPow'].values.tolist(),df1['P3_CooPow'].values.tolist(),df1['P4_CooPow'].values.tolist(),df1['Core_FanPow'].values.tolist(),df1['P1_FanPow'].values.tolist(),df1['P2_FanPow'].values.tolist(),df1['P3_FanPow'].values.tolist(),df1['P4_FanPow'].values.tolist(),df1['Core_HeaSet'].values.tolist(),df1['P1_HeaSet'].values.tolist(),df1['P2_HeaSet'].values.tolist(),df1['P3_HeaSet'].values.tolist(),df1['P4_HeaSet'].values.tolist(),df1['Core_CooSet'].values.tolist(),df1['P1_CooSet'].values.tolist(),df1['P2_CooSet'].values.tolist(),df1['P3_CooSet'].values.tolist(),df1['P4_CooSet'].values.tolist(),df1['Core_VFRSet'].values.tolist(),df1['P1_VFRSet'].values.tolist(),df1['P2_VFRSet'].values.tolist(),df1['P3_VFRSet'].values.tolist(),df1['P4_VFRSet'].values.tolist(),df1['Cor_MisGai'].values.tolist(),df1['P1_MisGai'].values.tolist(),df1['P2_MisGai'].values.tolist(),df1['P3_MisGai'].values.tolist(),df1['P4_MisGai'].values.tolist(),df1['Core_LigGai'].values.tolist(),df1['P1_LigGai'].values.tolist(),df1['P2_LigGai'].values.tolist(),df1['P3_LigGai'].values.tolist(),df1['P4_LigGai'].values.tolist()]
    #    U1 = [df1['OA_T'].values.tolist(),df1['Wea_HgloHor'].values.tolist(),df1['hour'].values.tolist(),df1['day'].values.tolist(),df1['Wea_TWetBul'].values.tolist(),df1['Core_HeaPow'].values.tolist(),df1['P1_HeaPow'].values.tolist(),df1['P2_HeaPow'].values.tolist(),df1['P3_HeaPow'].values.tolist(),df1['P4_HeaPow'].values.tolist(),df1['Core_CooPow'].values.tolist(),df1['P1_CooPow'].values.tolist(),df1['P2_CooPow'].values.tolist(),df1['P3_CooPow'].values.tolist(),df1['P4_CooPow'].values.tolist(),df1['Core_FanPow'].values.tolist(),df1['P1_FanPow'].values.tolist(),df1['P2_FanPow'].values.tolist(),df1['P3_FanPow'].values.tolist(),df1['P4_FanPow'].values.tolist(),df1['Core_OAVFR'].values.tolist(),df1['P1_OAVFR'].values.tolist(),df1['P2_OAVFR'].values.tolist(),df1['P3_OAVFR'].values.tolist(),df1['P4_OAVFR'].values.tolist(),df1['Core_CooSet'].values.tolist(),df1['P1_CooSet'].values.tolist(),df1['P2_CooSet'].values.tolist(),df1['P3_CooSet'].values.tolist(),df1['P4_CooSet'].values.tolist(),df1['Core_VFRSet'].values.tolist(),df1['P1_VFRSet'].values.tolist(),df1['P2_VFRSet'].values.tolist(),df1['P3_VFRSet'].values.tolist(),df1['P4_VFRSet'].values.tolist(),df1['Cor_MisGai'].values.tolist(),df1['P1_MisGai'].values.tolist(),df1['P2_MisGai'].values.tolist(),df1['P3_MisGai'].values.tolist(),df1['P4_MisGai'].values.tolist(),df1['Core_LigGai'].values.tolist(),df1['P1_LigGai'].values.tolist(),df1['P2_LigGai'].values.tolist(),df1['P3_LigGai'].values.tolist(),df1['P4_LigGai'].values.tolist()]
    #    U1 = [df1['OA_T'].values.tolist(),df1['Wea_HgloHor'].values.tolist(),df1['hour'].values.tolist(),df1['day'].values.tolist()]
    #df1['Core_T_before2'].values.tolist(),df1['P1_T_before2'].values.tolist(),df1['P2_T_before2'].values.tolist(),df1['P3_T_before2'].values.tolist(),df1['P4_T_before2'].values.tolist(),
    #    U1_test = [df1_test['OA_T'].values.tolist(),df1_test['Wea_HgloHor'].values.tolist(),df1_test['Wea_TWetBul'].values.tolist(),df1_test['Core_FanPow'].values.tolist(),df1_test['P1_FanPow'].values.tolist(),df1_test['P2_FanPow'].values.tolist(),df1_test['P3_FanPow'].values.tolist(),df1_test['P4_FanPow'].values.tolist(),df1_test['Core_HeaSet'].values.tolist(),df1_test['P1_HeaSet'].values.tolist(),df1_test['P2_HeaSet'].values.tolist(),df1_test['P3_HeaSet'].values.tolist(),df1_test['P4_HeaSet'].values.tolist(),df1_test['Core_CooSet'].values.tolist(),df1_test['P1_CooSet'].values.tolist(),df1_test['P2_CooSet'].values.tolist(),df1_test['P3_CooSet'].values.tolist(),df1_test['P4_CooSet'].values.tolist(),df1_test['Core_VFRSet'].values.tolist(),df1_test['P1_VFRSet'].values.tolist(),df1_test['P2_VFRSet'].values.tolist(),df1_test['P3_VFRSet'].values.tolist(),df1_test['P4_VFRSet'].values.tolist()]
    #,df1['Core_T_before'].values.tolist(),df1['P1_T_before'].values.tolist(),df1['P2_T_before'].values.tolist(),df1['P3_T_before'].values.tolist(),df1['P4_T_before'].values.tolist()
    #,df1['hour'].values.tolist(),df1['day'].values.tolist()
    #,df1['Core_RelHum'].values.tolist(),df1['P1_RelHum'].values.tolist(),df1['P2_RelHum'].values.tolist(),df1['P3_RelHum'].values.tolist(),df1['P4_RelHum'].values.tolist()
    #,df1['Core_TotIntGai'].values.tolist(),df1['P1_TotIntGai'].values.tolist(),df1['P2_TotIntGai'].values.tolist(),df1['P3_TotIntGai'].values.tolist(),df1['P4_TotIntGai'].values.tolist()
    #,df1['Cor_MisGai'].values.tolist(),df1['P1_MisGai'].values.tolist(),df1['P2_MisGai'].values.tolist(),df1['P3_MisGai'].values.tolist(),df1['P4_MisGai'].values.tolist()
    #,df1['Core_HeaSet'].values.tolist(),df1['P1_HeaSet'].values.tolist(),df1['P2_HeaSet'].values.tolist(),df1['P3_HeaSet'].values.tolist(),df1['P4_HeaSet'].values.tolist()
    #  ,df1['Core_VFRSet'].values.tolist(),df1['P1_VFRSet'].values.tolist(),df1['P2_VFRSet'].values.tolist(),df1['P3_VFRSet'].values.tolist(),df1['P4_VFRSet'].values.tolist()
    #,df1['Core_OAVFR'].values.tolist(),df1['P1_OAVFR'].values.tolist(),df1['P2_OAVFR'].values.tolist(),df1['P3_OAVFR'].values.tolist(),df1['P4_OAVFR'].values.tolist()
    #,df1['Core_FanPow'].values.tolist(),df1['P1_FanPow'].values.tolist(),df1['P2_FanPow'].values.tolist(),df1['P3_FanPow'].values.tolist(),df1['P4_FanPow'].values.tolist(),
    #
    U1_test = [df1_test[x].values.tolist() for x in list_of_vars]

    # U1_test = [
    #     df1_test['T_OA'].values.tolist(),
    #     df1_test['HgloHor'].values.tolist(),
    #
    #     # (df1['Hea_term_core']-df1['Core_T']).values.tolist(),
    #     # df1['Coo_term_core'].values.tolist(),
    #     # df1['Inf_term_core'].values.tolist(),
    #     # df1['Core_QconFlow'].values.tolist(),
    #     # df1['Core_OccN'].values.tolist(),
    #
    #     # df1['Hea_term_P1'].values.tolist(),
    #     # df1['Coo_term_P1'].values.tolist(),
    #
    #     df1_test['P1_OccN'].values.tolist(),
    #     df1_test['P1_IntGaiTot'].values.tolist(),
    #     df1_test['P1_HeaPow'].values.tolist(),
    #     df1_test['P1_FanPow'].values.tolist(),
    #     df1_test['P1_OAVol'].values.tolist(),
    #     #
    #     # df1_test['Hea_term_P2'].values.tolist(),
    #     # df1_test['Coo_term_P2'].values.tolist(),
    #     # df1_test['Inf_term_P2'].values.tolist(),
    #     # df1_test['P2_QconFlow'].values.tolist(),
    #     # df1_test['P2_OccN'].values.tolist(),
    #     #
    #     # df1_test['Hea_term_P3'].values.tolist(),
    #     # df1_test['Coo_term_P3'].values.tolist(),
    #     # df1_test['Inf_term_P3'].values.tolist(),
    #     # df1_test['P3_QconFlow'].values.tolist(),
    #     # df1_test['P3_OccN'].values.tolist(),
    #     #
    #     # df1_test['Hea_term_P4'].values.tolist(),
    #     # df1_test['Coo_term_P4'].values.tolist(),
    #     # df1_test['Inf_term_P4'].values.tolist(),
    #     # df1_test['P4_QconFlow'].values.tolist(),
    #     # df1_test['P4_OccN'].values.tolist()
    #
    #     ]

    #    ,df1_test['HgloHor'].values.tolist(),df1_test['P1_IntGaiTot'].values.tolist(),df1_test['P1_OccN'].values.tolist(),df1_test['P1_HeaSet'].values.tolist(),df1_test['P1_CooSet'].values.tolist()
    ## Definition of the Inputs Vector. Testing dataset
    #    df1_test['Core_T_prev'].values.tolist(),df1_test['P1_T_prev'].values.tolist(),df1_test['P2_T_prev'].values.tolist(),df1_test['P3_T_prev'].values.tolist(),df1_test['P4_T_prev'].values.tolist(),
    #U1_test = [df1_test['OA_T'].values.tolist(),df1_test['Wea_HgloHor'].values.tolist(),df1_test['hour'].values.tolist(),df1_test['day'].values.tolist(),df1_test['Core_HeaPow'].values.tolist(),df1_test['P1_HeaPow'].values.tolist(),df1_test['P2_HeaPow'].values.tolist(),df1_test['P3_HeaPow'].values.tolist(),df1_test['P4_HeaPow'].values.tolist(),df1_test['Core_CooPow'].values.tolist(),df1_test['P1_CooPow'].values.tolist(),df1_test['P2_CooPow'].values.tolist(),df1_test['P3_CooPow'].values.tolist(),df1_test['P4_CooPow'].values.tolist(),df1_test['Core_FanPow'].values.tolist(),df1_test['P1_FanPow'].values.tolist(),df1_test['P2_FanPow'].values.tolist(),df1_test['P3_FanPow'].values.tolist(),df1_test['P4_FanPow'].values.tolist(),df1_test['Core_HeaSet'].values.tolist(),df1_test['P1_HeaSet'].values.tolist(),df1_test['P2_HeaSet'].values.tolist(),df1_test['P3_HeaSet'].values.tolist(),df1_test['P4_HeaSet'].values.tolist(),df1_test['Core_CooSet'].values.tolist(),df1_test['P1_CooSet'].values.tolist(),df1_test['P2_CooSet'].values.tolist(),df1_test['P3_CooSet'].values.tolist(),df1_test['P4_CooSet'].values.tolist(),df1_test['Core_VFRSet'].values.tolist(),df1_test['P1_VFRSet'].values.tolist(),df1_test['P2_VFRSet'].values.tolist(),df1_test['P3_VFRSet'].values.tolist(),df1_test['P4_VFRSet'].values.tolist(),df1_test['Cor_MisGai'].values.tolist(),df1_test['P1_MisGai'].values.tolist(),df1_test['P2_MisGai'].values.tolist(),df1_test['P3_MisGai'].values.tolist(),df1_test['P4_MisGai'].values.tolist(),df1_test['Core_LigGai'].values.tolist(),df1_test['P1_LigGai'].values.tolist(),df1_test['P2_LigGai'].values.tolist(),df1_test['P3_LigGai'].values.tolist(),df1_test['P4_LigGai'].values.tolist()]
    #    U1_test = [df1_test['OA_T'].values.tolist(),df1_test['Wea_HgloHor'].values.tolist(),df1_test['hour'].values.tolist(),df1_test['day'].values.tolist(),df1_test['Wea_TWetBul'].values.tolist(),df1_test['Core_HeaPow'].values.tolist(),df1_test['P1_HeaPow'].values.tolist(),df1_test['P2_HeaPow'].values.tolist(),df1_test['P3_HeaPow'].values.tolist(),df1_test['P4_HeaPow'].values.tolist(),df1_test['Core_CooPow'].values.tolist(),df1_test['P1_CooPow'].values.tolist(),df1_test['P2_CooPow'].values.tolist(),df1_test['P3_CooPow'].values.tolist(),df1_test['P4_CooPow'].values.tolist(),df1_test['Core_FanPow'].values.tolist(),df1_test['P1_FanPow'].values.tolist(),df1_test['P2_FanPow'].values.tolist(),df1_test['P3_FanPow'].values.tolist(),df1_test['P4_FanPow'].values.tolist(),df1_test['Core_OAVFR'].values.tolist(),df1_test['P1_OAVFR'].values.tolist(),df1_test['P2_OAVFR'].values.tolist(),df1_test['P3_OAVFR'].values.tolist(),df1_test['P4_OAVFR'].values.tolist(),df1_test['Core_CooSet'].values.tolist(),df1_test['P1_CooSet'].values.tolist(),df1_test['P2_CooSet'].values.tolist(),df1_test['P3_CooSet'].values.tolist(),df1_test['P4_CooSet'].values.tolist(),df1_test['Core_VFRSet'].values.tolist(),df1_test['P1_VFRSet'].values.tolist(),df1_test['P2_VFRSet'].values.tolist(),df1_test['P3_VFRSet'].values.tolist(),df1_test['P4_VFRSet'].values.tolist(),df1_test['Cor_MisGai'].values.tolist(),df1_test['P1_MisGai'].values.tolist(),df1_test['P2_MisGai'].values.tolist(),df1_test['P3_MisGai'].values.tolist(),df1_test['P4_MisGai'].values.tolist(),df1_test['Core_LigGai'].values.tolist(),df1_test['P1_LigGai'].values.tolist(),df1_test['P2_LigGai'].values.tolist(),df1_test['P3_LigGai'].values.tolist(),df1_test['P4_LigGai'].values.tolist()]
    #    U1_test = [df1_test['OA_T'].values.tolist(),df1_test['Wea_HgloHor'].values.tolist(),df1_test['hour'].values.tolist(),df1_test['day'].values.tolist(),df1_test['Core_TotIntGai'].values.tolist(),df1_test['P1_TotIntGai'].values.tolist(),df1_test['P2_TotIntGai'].values.tolist(),df1_test['P3_TotIntGai'].values.tolist(),df1_test['P4_TotIntGai'].values.tolist(),df1_test['Core_HeaPow'].values.tolist(),df1_test['P1_HeaPow'].values.tolist(),df1_test['P2_HeaPow'].values.tolist(),df1_test['P3_HeaPow'].values.tolist(),df1_test['P4_HeaPow'].values.tolist(),df1_test['Core_CooPow'].values.tolist(),df1_test['P1_CooPow'].values.tolist(),df1_test['P2_CooPow'].values.tolist(),df1_test['P3_CooPow'].values.tolist(),df1_test['P4_CooPow'].values.tolist(),df1_test['Core_FanPow'].values.tolist(),df1_test['P1_FanPow'].values.tolist(),df1_test['P2_FanPow'].values.tolist(),df1_test['P3_FanPow'].values.tolist(),df1_test['P4_FanPow'].values.tolist(),df1_test['Core_HeaSet'].values.tolist(),df1_test['P1_HeaSet'].values.tolist(),df1_test['P2_HeaSet'].values.tolist(),df1_test['P3_HeaSet'].values.tolist(),df1_test['P4_HeaSet'].values.tolist(),df1_test['Core_CooSet'].values.tolist(),df1_test['P1_CooSet'].values.tolist(),df1_test['P2_CooSet'].values.tolist(),df1_test['P3_CooSet'].values.tolist(),df1_test['P4_CooSet'].values.tolist(),df1_test['Core_SupVFR'].values.tolist(),df1_test['P1_SupVFR'].values.tolist(),df1_test['P2_SupVFR'].values.tolist(),df1_test['P3_SupVFR'].values.tolist(),df1_test['P4_SupVFR'].values.tolist(),df1_test['Core_VFRSet'].values.tolist(),df1_test['P1_VFRSet'].values.tolist(),df1_test['P2_VFRSet'].values.tolist(),df1_test['P3_VFRSet'].values.tolist(),df1_test['P4_VFRSet'].values.tolist()]
    #    U1_test = [df1_test['OA_T'].values.tolist(),df1_test['Wea_HgloHor'].values.tolist(),df1_test['hour'].values.tolist(),df1_test['day'].values.tolist()]
    #    U1_test = [df1_test['Core_HeaPow'].values.tolist(),df1_test['P1_HeaPow'].values.tolist(),df1_test['P2_HeaPow'].values.tolist(),df1_test['P3_HeaPow'].values.tolist(),df1_test['P4_HeaPow'].values.tolist(),df1_test['Core_HeaSet'].values.tolist(),df1_test['P1_HeaSet'].values.tolist(),df1_test['P2_HeaSet'].values.tolist(),df1_test['P3_HeaSet'].values.tolist(),df1_test['P4_HeaSet'].values.tolist(),df1_test['OA_T'].values.tolist(),df1_test['Wea_HgloHor'].values.tolist(),df1_test['Wea_TWetBul'].values.tolist(),df1_test['Core_QconFlow'].values.tolist(),df1_test['P1_QconFlow'].values.tolist(),df1_test['P2_QconFlow'].values.tolist(),df1_test['P3_QconFlow'].values.tolist(),df1_test['P4_QconFlow'].values.tolist(),df1_test['hour'].values.tolist(),df1_test['day'].values.tolist(),df1_test['Core_TotIntGai'].values.tolist(),df1_test['P1_TotIntGai'].values.tolist(),df1_test['P2_TotIntGai'].values.tolist(),df1_test['P3_TotIntGai'].values.tolist(),df1_test['P4_TotIntGai'].values.tolist(),df1_test['Core_CooPow'].values.tolist(),df1_test['P1_CooPow'].values.tolist(),df1_test['P2_CooPow'].values.tolist(),df1_test['P3_CooPow'].values.tolist(),df1_test['P4_CooPow'].values.tolist(),df1_test['Core_FanPow'].values.tolist(),df1_test['P1_FanPow'].values.tolist(),df1_test['P2_FanPow'].values.tolist(),df1_test['P3_FanPow'].values.tolist(),df1_test['P4_FanPow'].values.tolist(),df1_test['Core_CooSet'].values.tolist(),df1_test['P1_CooSet'].values.tolist(),df1_test['P2_CooSet'].values.tolist(),df1_test['P3_CooSet'].values.tolist(),df1_test['P4_CooSet'].values.tolist(),df1_test['Core_OAVFR'].values.tolist(),df1_test['P1_OAVFR'].values.tolist(),df1_test['P2_OAVFR'].values.tolist(),df1_test['P3_OAVFR'].values.tolist(),df1_test['P4_OAVFR'].values.tolist(),df1_test['Cor_MisGai'].values.tolist(),df1_test['P1_MisGai'].values.tolist(),df1_test['P2_MisGai'].values.tolist(),df1_test['P3_MisGai'].values.tolist(),df1_test['P4_MisGai'].values.tolist(),df1_test['Core_SupVFR'].values.tolist(),df1_test['P1_SupVFR'].values.tolist(),df1_test['P2_SupVFR'].values.tolist(),df1_test['P3_SupVFR'].values.tolist(),df1_test['P4_SupVFR'].values.tolist(),df1_test['Core_VFRSet'].values.tolist(),df1_test['P1_VFRSet'].values.tolist(),df1_test['P2_VFRSet'].values.tolist(),df1_test['P3_VFRSet'].values.tolist(),df1_test['P4_VFRSet'].values.tolist(),df1_test['Core_DamSet'].values.tolist(),df1_test['P1_DamSet'].values.tolist(),df1_test['P2_DamSet'].values.tolist(),df1_test['P3_DamSet'].values.tolist(),df1_test['P4_DamSet'].values.tolist(),df1_test['Core_LigGai'].values.tolist(),df1_test['P1_LigGai'].values.tolist(),df1_test['P2_LigGai'].values.tolist(),df1_test['P3_LigGai'].values.tolist(),df1_test['P4_LigGai'].values.tolist()]
    #    U1_test = [df1_test['Core_T_before2'].values.tolist(),df1_test['P1_T_before2'].values.tolist(),df1_test['P2_T_before2'].values.tolist(),df1_test['P3_T_before2'].values.tolist(),df1_test['P4_T_before2'].values.tolist(),df1_test['OA_T'].values.tolist(),df1_test['Wea_HgloHor'].values.tolist(),df1_test['Wea_TWetBul'].values.tolist(),df1_test['Core_HeaSet'].values.tolist(),df1_test['P1_HeaSet'].values.tolist(),df1_test['P2_HeaSet'].values.tolist(),df1_test['P3_HeaSet'].values.tolist(),df1_test['P4_HeaSet'].values.tolist(),df1_test['Core_FanPow'].values.tolist(),df1_test['P1_FanPow'].values.tolist(),df1_test['P2_FanPow'].values.tolist(),df1_test['P3_FanPow'].values.tolist(),df1_test['P4_FanPow'].values.tolist(),df1_test['Core_CooSet'].values.tolist(),df1_test['P1_CooSet'].values.tolist(),df1_test['P2_CooSet'].values.tolist(),df1_test['P3_CooSet'].values.tolist(),df1_test['P4_CooSet'].values.tolist(),df1_test['Core_VFRSet'].values.tolist(),df1_test['P1_VFRSet'].values.tolist(),df1_test['P2_VFRSet'].values.tolist(),df1_test['P3_VFRSet'].values.tolist(),df1_test['P4_VFRSet'].values.tolist(),df1_test['Cor_MisGai'].values.tolist(),df1_test['P1_MisGai'].values.tolist(),df1_test['P2_MisGai'].values.tolist(),df1_test['P3_MisGai'].values.tolist(),df1_test['P4_MisGai'].values.tolist(),df1_test['Core_TotIntGai'].values.tolist(),df1_test['P1_TotIntGai'].values.tolist(),df1_test['P2_TotIntGai'].values.tolist(),df1_test['P3_TotIntGai'].values.tolist(),df1_test['P4_TotIntGai'].values.tolist()]

    #Wea_HgloHor

    #    df1_test['Core_T_before2'].values.tolist(),df1_test['P1_T_before2'].values.tolist(),df1_test['P2_T_before2'].values.tolist(),df1_test['P3_T_before2'].values.tolist(),df1_test['P4_T_before2'].values.tolist(),
    #,df1_test['Core_T_before'].values.tolist(),df1_test['P1_T_before'].values.tolist(),df1_test['P2_T_before'].values.tolist(),df1_test['P3_T_before'].values.tolist(),df1_test['P4_T_before'].values.tolist()
    #,df1_test['hour'].values.tolist(),df1_test['day'].values.tolist()
    #,df1_test['Core_RelHum'].values.tolist(),df1_test['P1_RelHum'].values.tolist(),df1_test['P2_RelHum'].values.tolist(),df1_test['P3_RelHum'].values.tolist(),df1_test['P4_RelHum'].values.tolist()
    #,df1_test['Core_TotIntGai'].values.tolist(),df1_test['P1_TotIntGai'].values.tolist(),df1_test['P2_TotIntGai'].values.tolist(),df1_test['P3_TotIntGai'].values.tolist(),df1_test['P4_TotIntGai'].values.tolist()
    #,df1_test['Core_OAVFR'].values.tolist(),df1_test['P1_OAVFR'].values.tolist(),df1_test['P2_OAVFR'].values.tolist(),df1_test['P3_OAVFR'].values.tolist(),df1_test['P4_OAVFR'].values.tolist()
    #,df1_test['Core_FanPow'].values.tolist(),df1_test['P1_FanPow'].values.tolist(),df1_test['P2_FanPow'].values.tolist(),df1_test['P3_FanPow'].values.tolist(),df1_test['P4_FanPow'].values.tolist()
    #,df1_test['Core_HeaSet'].values.tolist(),df1_test['P1_HeaSet'].values.tolist(),df1_test['P2_HeaSet'].values.tolist(),df1_test['P3_HeaSet'].values.tolist(),df1_test['P4_HeaSet'].values.tolist()
    #,df1_test['Core_VFRSet'].values.tolist(),df1_test['P1_VFRSet'].values.tolist(),df1_test['P2_VFRSet'].values.tolist(),df1_test['P3_VFRSet'].values.tolist(),df1_test['P4_VFRSet'].values.tolist()
    #,df1_test['Cor_MisGai'].values.tolist(),df1_test['P1_MisGai'].values.tolist(),df1_test['P2_MisGai'].values.tolist(),df1_test['P3_MisGai'].values.tolist(),df1_test['P4_MisGai'].values.tolist()


    U_1=np.array(U1);
    U_1_test=np.array(U1_test);
    ##
    y_tot1= [
        # df1['Core_T'].values.tolist(),
        df1['P1_T'].values.tolist(),
        # df1['P2_T'].values.tolist(),
        # df1['P3_T'].values.tolist(),
        # df1['P4_T'].values.tolist()
    ]
    y_tot1=np.array(y_tot1)
    ##df1['senTRoom_y|K'].values.tolist(),df1['senTRoom1_y|K'].values.tolist(), df1['senTRoom2_y|K'].values.tolist(), df1['senTRoom3_y|K'].values.tolist(),df1['senTRoom4_y|K'].values.tolist()
    ##
    y_tot1_test= [
        # df1_test['Core_T'].values.tolist(),
        df1_test['P1_T'].values.tolist(),
        # df1_test['P2_T'].values.tolist(),
        # df1_test['P3_T'].values.tolist(),
        # df1_test['P4_T'].values.tolist()
    ]
    y_tot1_test=np.array(y_tot1_test)
    ##
    ##df1_test['senTRoom_y|K'].values.tolist(),df1_test['senTRoom1_y|K'].values.tolist(), df1_test['senTRoom2_y|K'].values.tolist(), df1_test['senTRoom3_y|K'].values.tolist(),df1_test['senTRoom4_y|K'].values.tolist()
    ###System identification

    #
    #
    method = 'N4SID'
    sys_id1 = system_identification(y_tot1, U_1, method, SS_fixed_order=4) #IC='AICc')

    #print(sys_id1)
    #SS_fixed_order=7
    #    SS_fixed_order=5
    sys_id1.x2=np.array([[-2.85783809],  [0.14914303],  [0.19680084], [-0.12422081]])







    # xid1_train, yid1_train = fsetSIM.SS_lsim_process_form(sys_id1.A, sys_id1.B, sys_id1.C, sys_id1.D, U_1,sys_id1.x0)
    xid1_train, yid1_train = fsetSIM.SS_lsim_predictor_form(sys_id1.A_K, sys_id1.B_K, sys_id1.C, sys_id1.D, sys_id1.K, y_tot1, U_1, sys_id1.x2)
    #    print(xid1_train,yid1_train)
    #
    #
    ####
    a=xid1_train[0,len(xid1_train[0])-1];
    b=xid1_train[1,len(xid1_train[0])-1];
    c=xid1_train[2,len(xid1_train[0])-1];
    d=xid1_train[3,len(xid1_train[0])-1];
    #    e=xid1_train[4,len(xid1_train[0])-1];
    #    f=xid1_train[5,len(xid1_train[0])-1];
    #    g=xid1_train[6,len(xid1_train[0])-1];
    #    h=xid1_train[7,len(xid1_train[0])-1];
    #    i=xid1_train[8,len(xid1_train[0])-1];
    #    l=xid1_train[9,len(xid1_train[0])-1];
    #    n=xid1_train[10,len(xid1_train[0])-1];
    #    o=xid1_train[11,len(xid1_train[0])-1];
    #    q=xid1_train[12,len(xid1_train[0])-1];


    #    # TRY ORDER=1
    #    sys_id1.x1=np.array([[a]])
    ## TRY ORDER=2
    #    sys_id1.x1=np.array([[a],[b]])
    ## TRY ORDER=3
    #    sys_id1.x1=np.array([[a],[b],[c]])
    ## TRY ORDER=4
    sys_id1.x1=np.array([[a],[b],[c],[d]])
    ## TRY ORDER=5
    #    sys_id1.x1=np.array([[a],[b],[c],[d],[e]])
    #    ## TRY ORDER=6
    #    sys_id1.x1=np.array([[a],[b],[c],[d],[e],[f]])
    ## TRY ORDER=7
    #    sys_id1.x1=np.array([[a],[b],[c],[d],[e],[f],[g]]);
    ## TRY ORDER=8
    #    sys_id1.x1=np.array([[a],[b],[c],[d],[e],[f],[g],[h]])
    ## TRY ORDER=9
    #    sys_id1.x1=np.array([[a],[b],[c],[d],[e],[f],[g],[h],[i]])
    ## TRY ORDER=10
    #    sys_id1.x1=np.array([[a],[b],[c],[d],[e],[f],[g],[h],[i],[l]])
    ## TRY ORDER=11
    #    sys_id1.x1=np.array([[a],[b],[c],[d],[e],[f],[g],[h],[i],[l],[n]])
    ## TRY ORDER=12
    #    sys_id1.x1=np.array([[a],[b],[c],[d],[e],[f],[g],[h],[i],[l],[n],[o]])
    ## TRY ORDER=13
    #    sys_id1.x1=np.array([[a],[b],[c],[d],[e],[f],[g],[h],[i],[l],[n],[o],[q]])


    xid1_test, yid1_test = fsetSIM.SS_lsim_process_form(sys_id1.A, sys_id1.B, sys_id1.C, sys_id1.D, U_1_test, sys_id1.x1)

    #    print(xid1_test,yid1_test)


    #    #Calculate and analyze the errors
    #
    #    error1_test=(yid1_test-y_tot1_test)/y_tot1_test*100;
    ##
    #    plt.figure()
    #    plt.plot(Time_months1_test[0,0:t_2-t_1],error1_test[0,0:t_2-t_1]);
    #    plt.ylabel("Percentage error (%)")
    #    plt.grid()
    #    plt.title("Percentage error of the indoor air temperature estimation of core zone")
    #    plt.xlabel("Time (months)")
    ##    plt.show()
    #
    #
    #    plt.figure()
    #    plt.hist(error1_test[0]);
    #    plt.ylabel("Number of Observations")
    #
    #    plt.ylabel("Indoor Air Temperature (ºC)")
    #    plt.grid()
    #    plt.xlabel("Time (months)")
    ##    plt.show()
    #
    ##Calculate the metrics
    #Results of Temperature estimation of core zone

    #    mae_core=median_absolute_error(y_tot1_test[0],yid1_test[0])
    #   # mape_core= mean_absolute_percentage_error(y_tot1_test[0,0:t_2-t_1],yid1_test[0,0:t_2-t_1])
    #    mse_core=mean_squared_error(y_tot1_test[0],yid1_test[0])
    #    r2_core=r2_score(yid1_test[0], y_tot1_test[0])
    #    print("Determination Coefficient: ")
    #    print(r2_core)
    #    print("Mean Absolute Errors: ")
    #    print(mae_core)
    #    print("Mean Square Errors: ")
    #    print(mse_core)

    #    Results of Temperature estimation of zone 1

    mae_z1=median_absolute_error(y_tot1_test[0],yid1_test[0]);
    #    mape_z1= mean_absolute_percentage_error(y_tot1_test[1,0:t_2-t_1],yid1_test[1,0:t_2-t_1]);
    mse_z1=mean_squared_error(y_tot1_test[0],yid1_test[0]);
    r2_z1=(r2_score(yid1_test[0], y_tot1_test[0]));
    print("Determination Coefficient: ")
    print(r2_z1)
    print("Mean Absolute Errors: ")
    print(mae_z1)
    print("Mean Square Errors: ")
    print(mse_z1)
    # ##    #Results of Temperature estimation of zone 2
    # #
    #     mae_z2=median_absolute_error(y_tot1_test[2,0:t_2-t_1],yid1_test[2,0:t_2-t_1]);
    # #    mape_z2= mean_absolute_percentage_error(y_tot1_test[2,0:t_2-t_1],yid1_test[2,0:t_2-t_1]);
    #     mse_z2=mean_squared_error(y_tot1_test[2],yid1_test[2,0:t_2-t_1]);
    #     r2_z2=(r2_score(yid1_test[2,0:t_2-t_1], y_tot1_test[2,0:t_2-t_1]));
    # #
    #     print(r2_z2)
    # #
    # #
    # ##    #Results of Temperature estimation of zone 3
    # ##
    # #
    #     mae_z3=median_absolute_error(y_tot1_test[3,0:t_2-t_1],yid1_test[3,0:t_2-t_1]);
    # #    mape_z3= mean_absolute_percentage_error(y_tot1_test[3],yid1_test[3,0:t_2-t_1]);
    #     mse_z3=mean_squared_error(y_tot1_test[3,0:t_2-t_1],yid1_test[3,0:t_2-t_1]);
    #     r2_z3=(r2_score(yid1_test[3,0:t_2-t_1], y_tot1_test[3,0:t_2-t_1]));
    # #
    #     print(r2_z3)
    # #
    # ##    #Results of Temperature estimation of zone 4
    # ##
    # #
    #     mae_z4=median_absolute_error(y_tot1_test[4,0:t_2-t_1],yid1_test[4,0:t_2-t_1]);
    # #    mape_z4= mean_absolute_percentage_error(y_tot1_test[4,0:t_2-t_1],yid1_test[4,0:t_2-t_1]);
    #     mse_z4=mean_squared_error(y_tot1_test[4,0:t_2-t_1],yid1_test[4,0:t_2-t_1]);
    #     r2_z4=(r2_score(yid1_test[4,0:t_2-t_1], y_tot1_test[4,0:t_2-t_1]));
    # #
    #     print(r2_z4)
    #
    # ##


    #    y_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,13,14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,26]
    #    text_values = ["February1", "March1", "April1","May1", "June1", "July1", "August1","September1", "October1", "November1", "December1", "January2","February2", "March2", "April2","May2", "June2", "July2", "August2","September2", "October2", "November2", "December2", "January3"]
    #    x_values = np.arange(1, len(text_values) + 1, 1)

    # SAVE ALL THE RESULTS HERE BEFORE PLOTTING!
    A1=sys_id1.A
    print(f"A1 is {A1}")
    B1=sys_id1.B
    print(f"B1 is {B1}")
    C1=sys_id1.C
    print(f"C1 is {C1}")
    D1=sys_id1.D
    print(f"D1 is {D1}")
    #    print(f"X1 is {sys_id1.x1}")

    # GET ALL KALMAN GAINS
    K1=sys_id1.K
    print(f"Kalman Gain is {K1}")

    # GET ALL KALMAN MATRICES A_K AND B_K
    KA1=sys_id1.A_K
    KB1=sys_id1.B_K

    y0= y_tot1_test[:,0]

    # #SAVE ALL MATRICES
    np.save('output/matrix_A1.npy', A1)
    np.save('output/matrix_B1.npy', B1)
    np.save('output/matrix_C1.npy', C1)
    np.save('output/matrix_D1.npy', D1)
    np.save('output/sys_id1_x0.npy', sys_id1.x1)
    np.save('output/y_initial.npy', y0)

    # Save off the test data for use with the MPC problem. Only save of the variables
    # of interest, plus the time and datetime.
    df1_test[['Time', 'datetime'] + list_of_vars].to_csv('output/u1test.csv')

    # #SAVE ALL KALMAN GAINS
    np.save('output/kalman_gain_K.npy', K1)

    # #SAVE ALL KALMAN MATRICES A_K B_K
    #np.save('matrix_AK1.npy', KA1)
    #np.save('matrix_AK1.npy', KB1)

    plt.figure()
    # Time_months1_test, Time_months1, y_tot1_test, and yid1... are list of lists (array of array, so grab [0])
    plt.plot(df1_test['datetime'], y_tot1_test[0]-273.15, linewidth=3, color='forestgreen')
    plt.plot(df1_test['datetime'], yid1_test[0]-273.15, linestyle='dashed',linewidth=1.5, color='lightgreen')
    plt.plot(df1['datetime'], y_tot1[0]-273.15,linewidth=3, color='steelblue')
    plt.plot(df1['datetime'], yid1_train[0]-273.15, linestyle='dashed',linewidth=1.5, color='orange')
    # Specify the format - %b gives us Jan, Feb...
    fmt = mdates.DateFormatter('%b')
    ax = plt.gca().xaxis
    ax.set_major_locator(mdates.MonthLocator())
    ax.set_major_formatter(fmt)
    ax.set_minor_locator(mdates.DayLocator(interval=7))
    ax.set_minor_formatter(mdates.DateFormatter('%d'))
    plt.title("Comparison of original data and the output of the N4SID model. PERIMETER ZONE 1",size=20)
    plt.legend(['Original system Testing', 'Identified system Testing, ' + method,'Original System Training',  'Identified system Training, ' + method])
    plt.ylabel("Indoor Air Temperature (ºC)", size=16)
    plt.grid()
    plt.xlabel("Time (months)",size=10)
    plt.ylim([5, 35])
    plt.show()

    #    plt.text(1, 10, "R2=",r2_core,size=18)
    #    plt.yticks(size=16)
    #    plt.xticks(size=10)
    #    plt.title("Comparison of original data and the output of the N4SID model. CORE ZONE",size=20)
    #    plt.legend(['Original system Testing', 'Identified system Testing, ' + method,'Original System Training',  'Identified system Training, ' + method])
    ##    positions = (0, 1, 2, 3, 4)
    ##    labels = ("January", "February", "March", "April","May")
    ##    plt.xticks(positions, labels)
    #    plt.ylim([15, 27])
    # #SAVE ALL MATRICES
    #

##
#    plt.figure()
#    plt.plot(Time_months1[0], U1[7],linewidth=3, color='darkorange')
#    plt.ylabel("Thermal Power (W)",size=12)
#    plt.grid()
#    plt.xlabel("Time (months)",size=12)
#    #
##    plt.text(1, 10, "R2=",r2_core,size=18)
#    plt.yticks(size=12)
#    plt.xticks(x_values, text_values,size=12)
#    plt.title("Evolution of the thermal power of CORE ZONE",size=20)
##    plt.legend(['Original system Testing', 'Identified system Testing, ' + method,'Original System Training',  'Identified system Training, ' + method])
##    positions = (0, 1, 2, 3, 4)
##    labels = ("January", "February", "March", "April","May")
##    plt.xticks(positions, labels)
##    plt.ylim([15, 27])
#    plt.show()
#    #PLots of Temperature estimation of Zone 1
#    #
##
#    plt.figure()
#    plt.plot(Time_months1_test[0,0:t_2-t_1], y_tot1_test[0,0:t_2-t_1]-273.15,linewidth=3, color='forestgreen')
#    plt.plot(Time_months1_test[0,0:t_2-t_1], yid1_test[0,0:t_2-t_1]-273.15, linestyle='dashed',linewidth=1.5, color='lightgreen')
#    plt.plot(Time_months1[0,2:t_1-t_0], y_tot1[0,2:t_1-t_0]-273.15,linewidth=3, color='steelblue')
#    plt.plot(Time_months1[0,2:t_1-t_0], yid1_train[0,2:t_1-t_0]-273.15, linestyle='dashed',linewidth=1.5, color='cyan')
#    plt.ylabel("Indoor Air Temperature (ºC)",size=18)
#    plt.grid()
#    plt.xlabel("Time (months)",size=10)
#    #
#    plt.yticks(size=18)
#    plt.xticks(size=10)
#    plt.title("Comparison of original data and the output of the N4SID model. ZONE 1",size=20)
#    plt.legend(['Original system Testing', 'Identified system Testing, ' + method,'Original System Training',  'Identified system Training, ' + method])
##    positions = (0, 1, 2, 3, 4)
##    labels = ("January", "February", "March", "April","May")
##    plt.xticks(positions, labels)
#    plt.ylim([15, 27])
#    plt.show()
##
##    #PLots of Temperature estimation of Zone 2
##    #
##
#    plt.figure()
#    plt.plot(Time_months1_test[0,0:t_2-t_1], y_tot1_test[2,0:t_2-t_1]-273.15,linewidth=3, color='forestgreen')
#    plt.plot(Time_months1_test[0,0:t_2-t_1], yid1_test[2,0:t_2-t_1]-273.15, linestyle='dashed',linewidth=1.5, color='lightgreen')
#    plt.plot(Time_months1[0,2:t_1-t_0], y_tot1[2,2:t_1-t_0]-273.15,linewidth=3, color='steelblue')
#    plt.plot(Time_months1[0,2:t_1-t_0], yid1_train[2,2:t_1-t_0]-273.15, linestyle='dashed',linewidth=1.5, color='cyan')
#    plt.ylabel("Indoor Air Temperature (ºC)",size=12)
#    plt.grid()
#    plt.xlabel("Time (months)",size=12)
#    #
#    plt.title("Comparison of original data and the output of the N4SID model. ZONE 2",size=20)
#    plt.legend(['Original system Testing', 'Identified system Testing, ' + method,'Original System Training',  'Identified system Training, ' + method])
##    positions = (0, 1, 2, 3, 4)
##    labels = ("January", "February", "March", "April","May")
##    plt.xticks(positions, labels)
#    plt.yticks(size=12)
#    plt.xticks(x_values, text_values,size=12)
#    plt.ylim([15, 27])
#    plt.show()
#    #PLots of Temperature estimation of Zone 3
#    #
#
#    plt.figure()
#    plt.plot(Time_months1_test[0,0:t_2-t_1], y_tot1_test[3,0:t_2-t_1]-273.15,linewidth=3, color='forestgreen')
#    plt.plot(Time_months1_test[0,0:t_2-t_1], yid1_test[3,0:t_2-t_1]-273.15, linestyle='dashed',linewidth=1.5, color='lightgreen')
#    plt.plot(Time_months1[0,2:t_1-t_0], y_tot1[3,2:t_1-t_0]-273.15,linewidth=3, color='steelblue')
#    plt.plot(Time_months1[0,2:t_1-t_0], yid1_train[3,2:t_1-t_0]-273.15, linestyle='dashed',linewidth=1.5, color='cyan')
#    plt.ylabel("Indoor Air Temperature (ºC)",size=12)
#    plt.grid()
#    plt.xlabel("Time (months)",size=12)
#    #
#    plt.yticks(size=12)
#    plt.xticks(x_values, text_values,size=12)
#    plt.title("Comparison of original data and the output of the N4SID model. ZONE 3",size=20)
#    plt.legend(['Original system Testing', 'Identified system Testing, ' + method,'Original System Training',  'Identified system Training, ' + method])
##    positions = (0, 1, 2, 3)
##    labels = ("January", "February", "March", "April")
##    plt.xticks(positions, labels)
#    plt.ylim([15, 27])
#    plt.show()
#
#    #PLots of Temperature estimation of Zone 4
#    #
#
#    plt.figure()
#    plt.plot(Time_months1_test[0,0:t_2-t_1], y_tot1_test[4,0:t_2-t_1]-273.15,linewidth=3, color='forestgreen')
#    plt.plot(Time_months1_test[0,0:t_2-t_1], yid1_test[4,0:t_2-t_1]-273.15, linestyle='dashed',linewidth=1.5, color='lightgreen')
#    plt.plot(Time_months1[0,4:t_1-t_0], y_tot1[4,4:t_1-t_0]-273.15,linewidth=3, color='steelblue')
#    plt.plot(Time_months1[0,4:t_1-t_0], yid1_train[4,4:t_1-t_0]-273.15, linestyle='dashed',linewidth=1.5, color='cyan')
#    plt.ylabel("Indoor Air Temperature (ºC)",size=18)
#    plt.grid()
#    plt.xlabel("Time (months)",size=12)
#    #
#    plt.yticks(size=12)
#    plt.xticks(x_values, text_values,size=12)
#    plt.title("Comparison of original data and the output of the N4SID model. ZONE 4",size=20)
#    plt.legend(['Original system Testing', 'Identified system Testing, ' + method,'Original System Training',  'Identified system Training, ' + method])
##    positions = (0, 1, 2, 3, 4)
##    labels = ("January", "February", "March", "April","May")
##    plt.xticks(positions, labels)
#    plt.ylim([15, 27])
#    plt.show()
#     f=int(1*4.3);
#
# MODELS FINISHED. NOW THE METRICS AND MATRICES ARE SAVED


#metrics_zcore=np.array([mae_core,mape_core,mse_core,r2_core])
#metrics_z1=np.array([mae_z1,mape_z1,mse_z1,r2_z1])
#metrics_z2=np.array([mae_z2,mape_z2,mse_z2,r2_z2])
#metrics_z3=np.array([mae_z3,mape_z3,mse_z3,r2_z3])
#metrics_z4=np.array([mae_z4,mape_z4,mse_z4,r2_z4])
#
#
#np.save('metrics_core_zone.npy', metrics_zcore)
#np.save('metrics_zone_1.npy', metrics_z1)
#np.save('metrics_zone_2.npy', metrics_z2)
#np.save('metrics_zone_3.npy', metrics_z3)
#np.save('metrics_zone_4.npy', metrics_z4)
#
#Estimated_T=yid1_test;
#
#plt.figure()
#plt.hist(error1_test[0]);
#plt.ylabel("Number of Observations")
#plt.grid()
#plt.title("Histogram of Estimation Errors. Core Zone Temperature")
#plt.xlabel("Percentage Errors (%)")
#plt.show()

#SAVE THE OUTPUTS OF THE BOTH MODELS


#metrics=np.array([metrics_zcore, metrics_z1, metrics_z2, metrics_z3, metrics_z4])
##titles = ("Core Zone", "Zone 1", "Zone 2", "Zone 3","Zone 4")
#np.savetxt("moving_model.csv", metrics, header="MAE, MAPE, MSE, R2",delimiter=",")

# GET ALL MATRICES
