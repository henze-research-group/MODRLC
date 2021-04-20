#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 18:25:17 2021

@author: joseleiva
"""
from __future__ import division

#Import all the metrics to evaluate the accuracy of the N4SID Algorithm with the selected order 

from sklearn.metrics import r2_score
from sklearn.metrics import median_absolute_error
#from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import mean_squared_error


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
import math
from sippy import functionset as fset
from sippy import functionsetSIM as fsetSIM
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('science')
def secondYear(a):
    return a + 365*24*3600
def toInt(a):
    return int(a)
def toMonths(a):
    return a/3600/24/30

def toCelsius(a):
    return a - 273.15
    
def toKelvin(a):
    return a + 273.15

def theMax(a):
    return max(a, 0)
    
def importNformat(modpath, eppath, columns, epCols, names, days):
    
    data = pd.DataFrame(pd.read_csv(modpath))
    
    #drop duplicates and keep only 60s samples
    data = data.drop_duplicates(subset=['Time'])
    data = data.drop(data[data['Time'] % 60 > 0].index)
    origCol = data.columns.tolist()
    data['Time'] = data['Time'].apply(toInt)
    #replace modelica variable names by the ones defined in the "varDict" dict   
    newCol = [names[origCol[i]] if origCol[i] in names else origCol[i] for i in range(len(origCol))]     
    data.columns = newCol
    
    
    dataS = data.filter(columns, axis=1) #keep only the columns indicated in the "inputVars" list    
    
    # make sure the data is exactly 1 year long by appending the last x days that make up for one year. 
    #This is necessary because Spawn crashes shortly before the change of year, this is a known bug.
    last_day = (dataS.iloc[-1, dataS.columns.get_loc("Time")])/3600/24 #find the last day
    if last_day > days:
        curtim = last_day
        ind = -1
        while curtim > days:
            curtim = (dataS.iloc[-1, dataS.columns.get_loc("Time")])/3600/24
            ind -= 1
        dataSnip = dataS.iloc[:ind].copy()
    elif last_day < days:
        snip = math.ceil(days - last_day) # round it up one day
        ind = -1 #len(dataS['Time'])
        cur = last_day
        while cur > (days - snip):
            ind -= 1
            cur = dataS['Time'].iloc[ind] / 3600 / 24
        
        dataSnip = dataS.iloc[:ind].copy() #copy only up to the last full day
        copySnip = dataSnip.iloc[(ind - int(snip / 24 / 3600 / 60)):].copy() #re-copy the last x days that will complete the year
    #dataSnip = dataSnip.append(copySnip, ignore_index = True) #finalize the one-year dataset

        dataSnip = pd.concat([dataSnip, copySnip], axis=0)
    
    # fix the time vector
        for i in range(ind + len(dataSnip['Time']), len(dataSnip['Time'])): 
            dataSnip.iloc[i, dataSnip.columns.get_loc("Time")] = dataSnip.iloc[i-1, dataSnip.columns.get_loc("Time")] + 60

    #TODO: smoothen out the stiching point

    #TODO: import gains, occupancy, etc. from EP results and Vdot from SOM3 results
    epData = pd.DataFrame(pd.read_csv(eppath))
    epData = epData.filter(epCols, axis=1)

    epData['time'] = [int(i*60) for i in range(len(epData.index))]
    if len(epData.index) < len(dataSnip.index):
        
        eplast_day = (epData.iloc[-1, epData.columns.get_loc("P1_OccN")])/3600/24 #find the last day
        epsnip = math.ceil(days - eplast_day) # round it up one day
        epind = -1# len(epData['P1_OccN'])
        epcur = eplast_day
        
        while epcur > (days - epsnip):
            epind -= 1
            epcur = dataS['Time'][ind] / 3600 / 24
    
        epdataSnip = epData.iloc[:epind].copy() #copy only up to the last full day
        epcopySnip = epdataSnip.iloc[(epind - int(epsnip / 24 / 3600 / 60)):].copy() #re-copy the last x days that will complete the year
        epdataSnip = pd.concat([epdataSnip, epcopySnip], axis=0)
        for i in range(ind + len(epdataSnip['time']), len(epdataSnip['time'])): 
            epdataSnip.iloc[i, epdataSnip.columns.get_loc("time")] = epdataSnip.iloc[i-1, epdataSnip.columns.get_loc("time")] + 60

    else:
        epdataSnip = epData.iloc[:len(dataSnip['Time'])].copy()
    
    tDS = dataSnip.copy().set_index('Time', drop = False)
    epdataSnip = epdataSnip.copy().set_index('time')

    NdataSnip = pd.concat([tDS, epdataSnip], axis = 1)
    dataSnip = NdataSnip.reset_index(drop = True)
    #TODO: create new columns for hea_term, coo_term, infiltration, delta_t, etc.
    dataSnip['Hea_term_P1'] = ((dataSnip['P1_heaSetT'] - dataSnip['P1_T'].shift(periods=1, fill_value=273.15 + 15.6)).apply(theMax))
    dataSnip['Coo_term_P1'] = ((dataSnip['P1_T'].shift(periods=1, fill_value=273.15 + 15.6) - dataSnip['P1_cooSetT']).apply(theMax))
    dataSnip['Inf_term_P1'] = (dataSnip['T_OA'] - dataSnip['P1_T'].shift(periods=1, fill_value=273.15 + 15.6))
    dataSnip['Delta_P1'] = dataSnip['P1_T'].shift(periods=1, fill_value=273.15 + 15.6) - dataSnip['P1_T'].shift(periods=2, fill_value=273.15 + 15.6)

    #append the "second" year, to allow training up to 1 year in the past
    secYea = dataSnip.copy()
    secYea['Time'] = secYea['Time'].apply(secondYear)
    #dataSnip = dataSnip.append(secYea, ignore_index = True)
    dataSnip = pd.concat([dataSnip, secYea], axis=0)
        
#    Normalize data

#    cols_to_norm = ['P1_heaPow', 'P1_QconFlow']
#    dataSnip[cols_to_norm] = dataSnip[cols_to_norm].apply(lambda x: (x - x.min()) / (x.max() - x.min()))


    return dataSnip




epCols = ['P1_IntGaiTot', 'P1_OccN']
inputVars = ['Time', 'T_OA','HgloHor', 'P1_heaSetT', 'P1_cooSetT', 'P1_T', 'P1_heaPow', 'P1_cooPow']
varDict = {'Time' : 'Time', 
           'mod.weaBus.TDryBul' : 'T_OA',
           'mod.weaBus.HGloHor' : 'HgloHor',
           'mod.HVAC1.heaPowDem' : 'P1_heaPow',
           'mod.HVAC1.cooPowDem' : 'P1_cooPow',
           'mod.perZon1.fmuZon.QCon_flow' : 'P1_QconFlow',
           'senTRoom1_y' : 'P1_T',
           'mod.HVAC1.controls.add4.y' : 'P1_heaSetT',
           'mod.HVAC1.controls.add5.y' : 'P1_cooSetT',
           'mod.HVAC1.controls.outHeaSet' : 'P1_heaSet',
           'mod.HVAC1.controls.outCCSet' : 'P1_cooSet'}
           
daysInAYear = 364 #yep

df = importNformat('training_random2.csv', 'epData.csv', inputVars, epCols, varDict, daysInAYear)
df_test = importNformat('training_semi_random.csv', 'epData.csv', inputVars, epCols, varDict, daysInAYear)
#df_test.to_csv('2y_mild_rand.csv', index = False)
df.mean();
df=df.fillna(df.mean())
with pd.option_context('display.max_columns', None):  # more options can be specified also
    print(df)
#MODEL 1 of N4SID: FIRST 4 MONTHS OF THE DATASET (JAN-FEB-MARCH-)

m=df.shape[0]

center = 0.5 #where is the real center of the dataset, in percentage, once we appended two years
total_time = (df.iloc[-1, df.columns.get_loc("Time")])
starting_time = 0 + 0.5 * total_time 
training_time = 12 * 4 * 7 * 24 * 3600
testing_time =  1 * 4 * 7 * 24 * 3600
offset = starting_time - training_time
steps = int(total_time / testing_time)
timestep = 60 #dataset timestep #TODO: find timestep automatically

for i in range (1):

    print("Model number: ",i)
    t_0 = int((starting_time - training_time) / timestep)
    t_1 = t_0 + int(training_time / timestep)
    t_2 = t_1 + int(testing_time / timestep);

    df1=df.iloc[t_0:t_1];
    df1_test =df_test.iloc[t_1:t_2];
#
    df1=df1.fillna(df1.mean())
    df1_test=df1_test.fillna(df1_test.mean())

    Time_months1 = np.array([df1['Time'].apply(toMonths).values.tolist()])
##
    Time_months1_test = np.array([df1_test['Time'].apply(toMonths).values.tolist()])

## Definition of the Inputs Vector. Training dataset

   
    U1=[
    df1['T_OA'].values.tolist(),
    df1['HgloHor'].values.tolist(),
#    df1['P1_T'].shift(periods=1, fill_value=0).values.tolist(),
    df1['Hea_term_P1'].values.tolist(),
#    df1['P1_heaPow'].values.tolist(),
#    df1['P1_cooPow'].values.tolist(),
    df1['Coo_term_P1'].values.tolist(),
#    df1['P1_IntGaiTot'].shift(periods=1, fill_value=0).values.tolist(),
#    df1['P1_OccN'].values.tolist(),
#    df1['Delta_P1'].values.tolist(),
    df1['Inf_term_P1'].values.tolist()
    ]
        
    U1_test=[
    df1_test['T_OA'].values.tolist(),
    df1_test['HgloHor'].values.tolist(),
#    df1_test['P1_T'].shift(periods=1, fill_value=0).values.tolist(),
    df1_test['Hea_term_P1'].values.tolist(),
#    df1_test['P1_heaPow'].values.tolist(),
#    df1_test['P1_cooPow'].values.tolist(),
    df1_test['Coo_term_P1'].values.tolist(),
#    df1_test['P1_IntGaiTot'].shift(periods=1, fill_value=0).values.tolist(),
#    df1_test['P1_OccN'].values.tolist(),
#    df1_test['Delta_P1'].values.tolist(),
    df1_test['Inf_term_P1'].values.tolist()
    ]
    #print(len(U1), len(U1[0]))
    U_1=np.array(U1);
    U_1_test=np.array(U1_test);

    y_tot1= [df1['P1_T'].values.tolist()]
    y_tot1=np.array(y_tot1)

    y_tot1_test= [df1_test['P1_T'].values.tolist()]
    y_tot1_test=np.array(y_tot1_test)
     
    method = 'N4SID'
    sys_id1 = system_identification(y_tot1, U_1, method, IC='AIC')#IC='AIC')#
    #print(sys_id1.A_K, sys_id1.B_K, sys_id1.C, sys_id1.D)
    
    #SS_fixed_order=3

    xid1_train, yid1_train = fsetSIM.SS_lsim_process_form(sys_id1.A, sys_id1.B, sys_id1.C, sys_id1.D, U_1,sys_id1.x0)
    
#    print(xid1_train,yid1_train) 
#
#
####
#    a=xid1_train[0,len(xid1_train[0])-1];
#    b=xid1_train[1,len(xid1_train[0])-1];
#    c=xid1_train[2,len(xid1_train[0])-1];
#    d=xid1_train[3,len(xid1_train[0])-1];
#    e=xid1_train[4,len(xid1_train[0])-1];
#    f=xid1_train[5,len(xid1_train[0])-1];
#    g=xid1_train[6,len(xid1_train[0])-1];#    a=xid1_train[0,len(xid1_train[0])-1];
#    b=xid1_train[1,len(xid1_train[0])-1];
#    c=xid1_train[2,len(xid1_train[0])-1];
#    d=xid1_train[3,len(xid1_train[0])-1];
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
#    sys_id1.x1=np.array([[a],[b],[c],[d]])
    ## TRY ORDER=5
#    sys_id1.x1=np.array([[a],[b],[c],[d],[e]])
    ## TRY ORDER=6
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
       
    
    xid1_test, yid1_test = fsetSIM.SS_lsim_predictor_form(sys_id1.A_K, sys_id1.B_K, sys_id1.C, sys_id1.D, sys_id1.K, yid1_train, U_1_test,sys_id1.x0)

    mae_z1=median_absolute_error(y_tot1_test[0,60:t_2-t_1],yid1_test[0,60:t_2-t_1]);
    #mape_z1= mean_absolute_percentage_error(y_tot1_test[0,0:t_2-t_1],yid1_test[0,0:t_2-t_1]);
    mse_z1=mean_squared_error(y_tot1_test[0,60:t_2-t_1],yid1_test[0,60:t_2-t_1]);
    r2_z1=(r2_score(yid1_test[0,60:t_2-t_1], y_tot1_test[0,60:t_2-t_1]));
    
    print(r2_z1)
    

    print("Mean Absolute Errors: ")

    print(mae_z1)

    print("Mean Square Errors: ")

    print(mse_z1)

    print(yid1_test)
    
    y_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,13,14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,26]
    text_values = ["February1", "March1", "April1","May1", "June1", "July1", "August1","September1", "October1", "November1", "December1", "January2","February2", "March2", "April2","May2", "June2", "July2", "August2","September2", "October2", "November2", "December2", "January3"]
    x_values = np.arange(1, len(text_values) + 1, 1)
 
    
    
    plt.figure(i)
    plt.plot(Time_months1[0,2:t_1-t_0], y_tot1[0,2:t_1-t_0]-273.15,linewidth=3, color='steelblue')
    plt.plot(Time_months1[0,2:t_1-t_0], yid1_train[0,2:t_1-t_0]-273.15, linestyle='dashed',linewidth=1.5, color='cyan')
    plt.plot(Time_months1_test[0,0:t_2-t_1], y_tot1_test[0,0:t_2-t_1]-273.15,linewidth=3, color='forestgreen')
    plt.plot(Time_months1_test[0,0:t_2-t_1], yid1_test[0,0:t_2-t_1]-273.15, linestyle='dashed',linewidth=1.5, color='lightgreen')
    plt.ylabel("Indoor Air Temperature (ºC)",size=18)
    plt.grid()
    plt.xlabel("Time (months)",size=10)
    #
    plt.yticks(size=18)
    plt.xticks(x_values, text_values,size=10)
    plt.title("Comparison of original data and the output of the N4SID model. ZONE 1",size=20)
    plt.legend(['Original system Testing', 'Identified system Testing, ' + method,'Original System Training',  'Identified system Training, ' + method])
#    positions = (0, 1, 2, 3, 4)
#    labels = ("January", "February", "March", "April","May")
#    plt.xticks(positions, labels)
    plt.ylim([5, 35])
    plt.show()
    
    plt.figure(i)
    plt.plot(Time_months1[0,2:t_1-t_0], y_tot1[0,2:t_1-t_0]-273.15,linewidth=3, color='steelblue')
    plt.plot(Time_months1[0,2:t_1-t_0], yid1_train[0,2:t_1-t_0]-273.15, linestyle='dashed',linewidth=1.5, color='cyan')
    plt.ylabel("Indoor Air Temperature (ºC)",size=18)
    plt.grid()
    plt.xlabel("Time (months)",size=10)
    #
    plt.yticks(size=18)
    plt.xticks(x_values, text_values,size=10)
    plt.title("Comparison of original data and the output of the N4SID model. ZONE 1",size=20)
    plt.legend(['Original System Training',  'Identified system Training, ' + method])
#    positions = (0, 1, 2, 3, 4)
#    labels = ("January", "February", "March", "April","May")
#    plt.xticks(positions, labels)
    plt.ylim([5, 35])
    plt.show()


    plt.figure(i)
    plt.plot(Time_months1_test[0,0:t_2-t_1], y_tot1_test[0,0:t_2-t_1]-273.15,linewidth=3, color='forestgreen')
    plt.plot(Time_months1_test[0,0:t_2-t_1], yid1_test[0,0:t_2-t_1]-273.15, linestyle='dashed',linewidth=1.5, color='lightgreen')
   
    plt.ylabel("Indoor Air Temperature (ºC)",size=18)
    plt.grid()
    plt.xlabel("Time (months)",size=10)
    #
    plt.yticks(size=18)
    plt.xticks(x_values, text_values,size=10)
    plt.title("Comparison of original data and the output of the N4SID model. ZONE 1",size=20)
    plt.legend(['Original system Testing', 'Identified system Testing, ' + method,])
#    positions = (0, 1, 2, 3, 4)
#    labels = ("January", "February", "March", "April","May")
#    plt.xticks(positions, labels)
    plt.ylim([5, 35])
    plt.show()

    f=int(1*4.3);

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
#
#
##titles = ("Core Zone", "Zone 1", "Zone 2", "Zone 3","Zone 4")
#np.savetxt("moving_model.csv", metrics, header="MAE, MAPE, MSE, R2",delimiter=",")
#
#

B1=sys_id1.B

with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(pd.DataFrame(B1))

# GET ALL MATRICES 
A1=sys_id1.A



C1=sys_id1.C

D1=sys_id1.D


# GET ALL KALMAN GAINS  

K1=sys_id1.K


# GET ALL KALMAN MATRICES A_K AND B_K 

KA1=sys_id1.A_K

KB1=sys_id1.B_K

#
 #SAVE ALL MATRICES 
 
np.save('matrix_A1.npy', A1)

np.save('matrix_B1.npy', B1)

np.save('matrix_C1.npy', C1)

np.save('matrix_D1.npy', D1)


 #SAVE ALL KALMAN GAINS 
 
  
np.save('matrix_K1.npy', K1)


 #SAVE ALL KALMAN MATRICES A_K B_K 
 
  
np.save('matrix_AK1.npy', KA1)

np.save('matrix_BK1.npy', KB1)

