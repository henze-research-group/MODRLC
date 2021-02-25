#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 18:25:17 2021

@author: joseleiva
"""
from __future__ import division

#Import all the metrics to evaluate the accuracy of the N4SID Algorithm with the selected order 

from sklearn.metrics import r2_score
from sklearn.metrics import median_absolute_error
from sklearn.metrics import mean_absolute_percentage_error
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
from sippy import functionset as fset
from sippy import functionsetSIM as fsetSIM
import pandas as pd

data = pd.read_csv("wrapped 2.csv")
df=pd.DataFrame(data)
df.mean();
df=df.fillna(df.mean())

#MODEL 1 of N4SID: FIRST HALF OF THE DATASET

print (df)

#ts1 = 60; "Time in seconds: 60 seconds "
#tfin1 = 302504*60-1

#Time1 = np.linspace(0, tfin1, 302504)
#Time_months1=Time1/24/3600/30;
df1 =df.iloc[0:302504];
print(df1)
Time1 = np.array([df1['Time'].values.tolist()])
Time_months1=Time1/24/3600/30;

#Defining the vectors inputs (u) and outputs (y)#


        
U1 = [df1['mod.building.weaBus.HDifHor'].values.tolist(), df1['mod.building.weaBus.HDirNor'].values.tolist(),df1['mod.building.weaBus.HGloHor'].values.tolist(), df1['mod.building.weaBus.HHorIR'].values.tolist(),df1['mod.building.weaBus.TBlaSky'].values.tolist(), df1['mod.building.weaBus.TDryBul'].values.tolist(), df1['mod.building.weaBus.TWetBul'].values.tolist(), df1['mod.building.weaBus.winSpe'].values.tolist(), df1['mod.building.weaBus.winDir'].values.tolist(),df1['mod.building.weaBus.relHum'].values.tolist(),df1['mod.corZon.fmuZon.QCon_flow'].values.tolist(),df1['mod.HVAC.hea.Q_flow'].values.tolist(),df1['mod.HVAC.fan.P'].values.tolist(),df1['mod.HVAC.volSenSup.V_flow'].values.tolist(),df1['mod.HVAC.volSenOA.V_flow'].values.tolist(),df1['mod.HVAC.senRelHum.phi'].values.tolist(),df1['mod.HVAC.senTSup.T'].values.tolist()]

      
U_1=np.array(U1)


y_tot1= [df1['mod.HVAC.temSenRet'].values.tolist()]
y_tot1=np.array(y_tot1)



#System identification
method = 'N4SID'
sys_id1 = system_identification(y_tot1, U_1, method, SS_fixed_order=9,IC='AICc')
print(sys_id1)
xid1, yid1 = fsetSIM.SS_lsim_process_form(sys_id1.A, sys_id1.B, sys_id1.C, sys_id1.D, U_1,sys_id1.x0)
print(xid1,yid1)

#Calculate the metrics 

#corr_coeff_1=r2_score(y_tot1[0],yid1[0]);
mae_1=median_absolute_error(y_tot1[0],yid1[0]);
mape_1= mean_absolute_percentage_error(y_tot1[0],yid1[0]);
mse_1=mean_squared_error(y_tot1[0],yid1[0]);

import matplotlib.pyplot as plt

plt.close("all")
plt.figure(0)
plt.plot(Time_months1[0], y_tot1[0])
plt.plot(Time_months1[0], yid1[0])
plt.ylabel("Indoor Air Temperature (K)")
plt.grid()
plt.xlabel("Time (months)")

plt.title("Comparison of original data and the N4SID model")
plt.legend(['Original system', 'Identified system, ' + method])
plt.xlim([1, 8])
plt.ylim([250, 320])



plt.figure(1)
plt.plot(Time_months1[0], U_1[5])
plt.ylabel("Temperature Dry Bulb (K)")
plt.grid()
plt.xlabel("Time (months)")
plt.title("Input of the N4SID model")
plt.xlim([1, 8])

plt.show()

#MODEL 2 of N4SID: SECOND HALF OF THE DATASET


print (df)



#Defining the vectors inputs (u) and outputs (y)#
df2 =df.iloc[302504:605008];
print(df2)

#ts2 = 60; "Time in seconds: 60 seconds "
#tfin2 = 605008*60-1
#
#Time2 = np.linspace(302504, tfin2, 302504)
#Time_months2=Time2/24/3600/30;

Time2 = np.array([df2['Time'].values.tolist()])
Time_months2=Time2/24/3600/30;

       
U2 = [df2['mod.building.weaBus.HDifHor'].values.tolist(), df2['mod.building.weaBus.HDirNor'].values.tolist(),df2['mod.building.weaBus.HGloHor'].values.tolist(), df2['mod.building.weaBus.HHorIR'].values.tolist(),df2['mod.building.weaBus.TBlaSky'].values.tolist(), df2['mod.building.weaBus.TDryBul'].values.tolist(), df2['mod.building.weaBus.TWetBul'].values.tolist(), df2['mod.building.weaBus.winSpe'].values.tolist(), df2['mod.building.weaBus.winDir'].values.tolist(),df2['mod.building.weaBus.relHum'].values.tolist(),df2['mod.corZon.fmuZon.QCon_flow'].values.tolist(),df2['mod.HVAC.hea.Q_flow'].values.tolist(),df2['mod.HVAC.fan.P'].values.tolist(),df2['mod.HVAC.volSenSup.V_flow'].values.tolist(),df2['mod.HVAC.volSenOA.V_flow'].values.tolist(),df2['mod.HVAC.senRelHum.phi'].values.tolist(),df2['mod.HVAC.senTSup.T'].values.tolist()]

      
U_2=np.array(U2)


y_tot2= [df2['mod.HVAC.temSenRet'].values.tolist()]
y_tot2=np.array(y_tot2)



#System identification
method = 'N4SID'
sys_id2 = system_identification(y_tot2, U_2, method, SS_fixed_order=9,IC='AICc')
print(sys_id2)
xid2, yid2 = fsetSIM.SS_lsim_process_form(sys_id2.A, sys_id2.B, sys_id2.C, sys_id2.D, U_2, sys_id2.x0)
print(xid2,yid2)



#Calculate the metrics 

#corr_coeff_2=r2_score(y_tot2[0],yid2[0]);
mae_2=median_absolute_error(y_tot2[0],yid2[0]);
mape_2= mean_absolute_percentage_error(y_tot2[0],yid2[0]);
mse_2=mean_squared_error(y_tot2[0],yid2[0]);

import matplotlib.pyplot as plt

plt.close("all")
plt.figure(2)
plt.plot(Time_months2[0], y_tot2[0])
plt.plot(Time_months2[0], yid2[0])
plt.ylabel("Indoor Air Temperature (K)")
plt.grid()
plt.xlabel("Time (months)")

plt.title("Comparison of original data and the N4SID model")
plt.legend(['Original system', 'Identified system, ' + method])
plt.ylim([280, 307])



plt.figure(3)
plt.plot(Time_months2[0], U_2[5])
plt.ylabel("Temperature (K)")
plt.grid()
plt.xlabel("Time (months)")
plt.title("Input: Outdoor Temperature Dry Bulb")

plt.show()

metrics=np.array([mae_1,mae_2,mape_1,mape_2,mse_1,mse_2])
np.save('metrics_order_9.npy', metrics)
Estimated_T_1=yid1;
Estimated_T_2=yid2;


np.save('estimated_T1.npy', Estimated_T_1)
np.save('estimated_T2.npy', Estimated_T_2)








