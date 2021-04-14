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

#MODEL 1 of N4SID: FIRST 3 MONTHS OF THE DATASET (JAN-FEB-MARCH)

print (df)

#ts1 = 60; "Time in seconds: 60 seconds "
#tfin1 = 302504*60-1

#Time1 = np.linspace(0, tfin1, 302504)
#Time_months1=Time1/24/3600/30;
df1 =df.iloc[0:100000];
df1_test =df.iloc[100000:151252];
df1=df1.fillna(df1.mean())
df1_test=df1_test.fillna(df1_test.mean())
print(df1)
print(df1_test)


Time1 = np.array([df1['Time'].values.tolist()])
Time_months1=Time1/24/3600/30;

Time1_test = np.array([df1_test['Time'].values.tolist()])
Time_months1_test=Time1_test/24/3600/30;

#Defining the vectors inputs (u) and outputs (y)#
#tfin = 500
#npts = int(old_div(tfin, ts)) + 1
#Time = np.linspace(0, tfin, npts)

        
U1 = [df1['mod.building.weaBus.HDirNor'].values.tolist(),df1['mod.building.weaBus.TBlaSky'].values.tolist(), df1['mod.building.weaBus.TDryBul'].values.tolist(), df1['mod.building.weaBus.relHum'].values.tolist(),df1['mod.corZon.fmuZon.QCon_flow'].values.tolist(),df1['mod.HVAC.hea.Q_flow'].values.tolist(),df1['mod.HVAC.fan.P'].values.tolist(),df1['mod.HVAC.volSenSup.V_flow'].values.tolist(),df1['mod.HVAC.volSenOA.V_flow'].values.tolist(),df1['mod.HVAC.senTSup.T'].values.tolist()]
#df1['mod.HVAC.senRelHum.phi'].values.tolist(),
U1_test = [df1_test['mod.building.weaBus.HDirNor'].values.tolist(),df1_test['mod.building.weaBus.TBlaSky'].values.tolist(), df1_test['mod.building.weaBus.TDryBul'].values.tolist(), df1_test['mod.building.weaBus.relHum'].values.tolist(),df1_test['mod.corZon.fmuZon.QCon_flow'].values.tolist(),df1_test['mod.HVAC.hea.Q_flow'].values.tolist(),df1_test['mod.HVAC.fan.P'].values.tolist(),df1_test['mod.HVAC.volSenSup.V_flow'].values.tolist(),df1_test['mod.HVAC.volSenOA.V_flow'].values.tolist(),df1_test['mod.HVAC.senTSup.T'].values.tolist()]
#df1_test['mod.HVAC.senRelHum.phi'].values.tolist(),
      
U_1=np.array(U1)
U_1_test=np.array(U1_test)

y_tot1= [df1['mod.HVAC.temSenRet'].values.tolist()]
y_tot1=np.array(y_tot1)


y_tot1_test= [df1_test['mod.HVAC.temSenRet'].values.tolist()]
y_tot1_test=np.array(y_tot1_test)


#System identification
method = 'N4SID'
sys_id1 = system_identification(y_tot1, U_1, method, SS_fixed_order=1)
print(sys_id1)
xid1_test, yid1_test = fsetSIM.SS_lsim_process_form(sys_id1.A, sys_id1.B, sys_id1.C, sys_id1.D, U_1_test,sys_id1.x0)
print(xid1_test,yid1_test)
xid1_train, yid1_train = fsetSIM.SS_lsim_process_form(sys_id1.A, sys_id1.B, sys_id1.C, sys_id1.D, U_1,sys_id1.x0)
print(xid1_train,yid1_train)

error_test=yid1_test-y_tot1_test
#Calculate the metrics 

#corr_coeff_1=r2_score(y_tot1[0],yid1[0]);
mae_1=median_absolute_error(y_tot1_test[0,500:51252],yid1_test[0,500:51252]);
mape_1= mean_absolute_percentage_error(y_tot1_test[0,500:51252],yid1_test[0,500:51252]);
mse_1=mean_squared_error(y_tot1_test[0,500:51252],yid1_test[0,500:51252]);

import matplotlib.pyplot as plt

plt.close("all")
plt.figure(0)
plt.plot(Time_months1_test[0,0:51252], y_tot1_test[0,0:51252]-273.15)
plt.plot(Time_months1_test[0,0:51252], yid1_test[0,0:51252]-273.15)
plt.plot(Time_months1[0,0:100000], y_tot1[0,0:100000]-273.15)
plt.plot(Time_months1[0,0:100000], yid1_train[0,0:100000]-273.15)
plt.ylabel("Indoor Air Temperature (ºC)")
plt.grid()
plt.xlabel("Time (months)")

plt.title("Comparison of original data and the N4SID model 1")
plt.legend(['Original system Testing', 'Identified system Testing, ' + method,'Original System Training',  'Identified system Training, ' + method])
positions = (0, 1, 2, 3)
labels = ("January", "February", "March", "April")
plt.xticks(positions, labels)
plt.ylim([15, 27])



plt.figure(1)
plt.plot(Time_months1_test[0], U_1_test[1]-273.15)
plt.ylabel("Temperature Dry Bulb (ºC)")
plt.grid()
plt.xlabel("Time (months)")
plt.title("Input of the N4SID model")
#plt.ylim([0, 30])
positions = (0, 1, 2,3)
labels = ("January", "February", "March", "April")
plt.xticks(positions, labels)
plt.show()
r2_m1=(r2_score(yid1_test[0,500:51252], y_tot1_test[0,500:51252]))
print(r2_m1)
 


#MODEL 2 of N4SID: SECOND 3 MONTHS OF THE DATASET (APRIL,MAY, JULY)


print (df)



#Defining the vectors inputs (u) and outputs (y)#
df2 =df.iloc[151252:251252];
print(df2)

df2_test =df.iloc[251252:302504];
print(df2_test)
#ts2 = 60; "Time in seconds: 60 seconds "
#tfin2 = 605008*60-1
#
#Time2 = np.linspace(302504, tfin2, 302504)
#Time_months2=Time2/24/3600/30;

Time2 = np.array([df2['Time'].values.tolist()])
Time_months2=Time2/24/3600/30;

Time2_test = np.array([df2_test['Time'].values.tolist()])
Time_months2_test=Time2_test/24/3600/30;

       
U2 = [ df2['mod.building.weaBus.HDirNor'].values.tolist(), df2['mod.building.weaBus.TBlaSky'].values.tolist(), df2['mod.building.weaBus.TDryBul'].values.tolist(), df2['mod.building.weaBus.winDir'].values.tolist(),df2['mod.building.weaBus.relHum'].values.tolist(),df2['mod.corZon.fmuZon.QCon_flow'].values.tolist(),df2['mod.HVAC.hea.Q_flow'].values.tolist(),df2['mod.HVAC.fan.P'].values.tolist(),df2['mod.HVAC.volSenSup.V_flow'].values.tolist(),df2['mod.HVAC.volSenOA.V_flow'].values.tolist(),df2['mod.HVAC.senTSup.T'].values.tolist()]
U2_test = [ df2_test['mod.building.weaBus.HDirNor'].values.tolist(), df2_test['mod.building.weaBus.TBlaSky'].values.tolist(), df2_test['mod.building.weaBus.TDryBul'].values.tolist(), df2_test['mod.building.weaBus.winDir'].values.tolist(),df2_test['mod.building.weaBus.relHum'].values.tolist(),df2_test['mod.corZon.fmuZon.QCon_flow'].values.tolist(),df2_test['mod.HVAC.hea.Q_flow'].values.tolist(),df2_test['mod.HVAC.fan.P'].values.tolist(),df2_test['mod.HVAC.volSenSup.V_flow'].values.tolist(),df2_test['mod.HVAC.volSenOA.V_flow'].values.tolist(),df2_test['mod.HVAC.senTSup.T'].values.tolist()]

      
U_2=np.array(U2)
U_2_test=np.array(U2_test)

y_tot2= [df2['mod.HVAC.temSenRet'].values.tolist()]
y_tot2=np.array(y_tot2)

y_tot2_test= [df2_test['mod.HVAC.temSenRet'].values.tolist()]
y_tot2_test=np.array(y_tot2_test)

#System identification
method = 'N4SID'
sys_id2 = system_identification(y_tot2, U_2, method, SS_fixed_order=8)
print(sys_id2)
xid2_test, yid2_test = fsetSIM.SS_lsim_process_form(sys_id2.A, sys_id2.B, sys_id2.C, sys_id2.D, U_2_test,sys_id2.x0)
print(xid2_test,yid2_test)
xid2_train, yid2_train = fsetSIM.SS_lsim_process_form(sys_id2.A, sys_id2.B, sys_id2.C, sys_id2.D, U_2,sys_id2.x0)
print(xid2_train,yid2_train)

error_test_2=yid2_test-y_tot2_test;



#Calculate the metrics 

#corr_coeff_2=r2_score(y_tot2[0],yid2[0]);
mae_2=median_absolute_error(y_tot2_test[0,1000:51252],yid2_test[0,1000:51252]);
mape_2= mean_absolute_percentage_error(y_tot2_test[0,1000:51252],yid2_test[0,1000:51252]);
mse_2=mean_squared_error(y_tot2_test[0,1000:51252],yid2_test[0,1000:51252]);




#plt.close("all")
plt.figure(2)
plt.plot(Time_months2_test[0,0:51252], y_tot2_test[0,0:51252]-273.15)
plt.plot(Time_months2_test[0,0:51252], yid2_test[0,0:51252]-273.15)
plt.plot(Time_months2[0,0:100000], y_tot2[0,0:100000]-273.15)
plt.plot(Time_months2[0,0:100000], yid2_train[0,0:100000]-273.15)
plt.ylabel("Indoor Air Temperature (ºC)")
plt.grid()
plt.xlabel("Time (months)")

plt.title("Comparison of original data and the N4SID model 2")
plt.legend(['Original system Testing', 'Identified system Testing, ' + method,'Original System Training',  'Identified system Training, ' + method])
positions2 = (3, 4, 5,6)
labels2 = ("April", "May", "June", "July")
plt.xticks(positions2, labels2)
plt.ylim([15, 27])




plt.figure(3)
plt.plot(Time_months2_test[0,0:51252], U_2_test[2,0:51252]-273.15)
plt.ylabel("Temperature (ºC)")
plt.grid()
plt.xlabel("Time (months)")
plt.title("Input: Outdoor Temperature Dry Bulb")
#plt.ylim([0, 30])
positions2 = (3, 4, 5,6)
labels2 = ("April", "May", "June", "July")
plt.xticks(positions2, labels2)
plt.ylim([0, 35])
plt.show()
r2_m2=(r2_score(yid2_test[0,1000:51252], y_tot2_test[0,1000:51252]))
print(r2_m2)


#MODEL 3 of N4SID: THIRD 3 MONTHS OF THE DATASET (JULY,AUGUST, SEPTEMBER)


print (df)



#Defining the vectors inputs (u) and outputs (y)#
df3 =df.iloc[302504:402504];
print(df3)

df3_test =df.iloc[402504:453756];
print(df3_test)

#ts2 = 60; "Time in seconds: 60 seconds "
#tfin2 = 605008*60-1
#
#Time2 = np.linspace(302504, tfin2, 302504)
#Time_months2=Time2/24/3600/30;

Time3 = np.array([df3['Time'].values.tolist()])
Time_months3=Time3/24/3600/30;

Time3_test = np.array([df3_test['Time'].values.tolist()])
Time_months3_test=Time3_test/24/3600/30;

       
U3 = [df3['mod.building.weaBus.HDifHor'].values.tolist(), df3['mod.building.weaBus.HDirNor'].values.tolist(), df3['mod.building.weaBus.HHorIR'].values.tolist(), df3['mod.building.weaBus.TBlaSky'].values.tolist(), df3['mod.building.weaBus.TDryBul'].values.tolist(),  df3['mod.building.weaBus.winSpe'].values.tolist(), df3['mod.building.weaBus.winDir'].values.tolist(),df3['mod.building.weaBus.relHum'].values.tolist(),df3['mod.corZon.fmuZon.QCon_flow'].values.tolist(),df3['mod.HVAC.hea.Q_flow'].values.tolist(),df3['mod.HVAC.fan.P'].values.tolist(),df3['mod.HVAC.volSenSup.V_flow'].values.tolist(),df3['mod.HVAC.volSenOA.V_flow'].values.tolist(),df3['mod.HVAC.senTSup.T'].values.tolist()]
U3_test = [df3_test['mod.building.weaBus.HDifHor'].values.tolist(), df3_test['mod.building.weaBus.HDirNor'].values.tolist(), df3_test['mod.building.weaBus.HHorIR'].values.tolist(), df3_test['mod.building.weaBus.TBlaSky'].values.tolist(), df3_test['mod.building.weaBus.TDryBul'].values.tolist(),  df3_test['mod.building.weaBus.winSpe'].values.tolist(), df3_test['mod.building.weaBus.winDir'].values.tolist(),df3_test['mod.building.weaBus.relHum'].values.tolist(),df3_test['mod.corZon.fmuZon.QCon_flow'].values.tolist(),df3_test['mod.HVAC.hea.Q_flow'].values.tolist(),df3_test['mod.HVAC.fan.P'].values.tolist(),df3_test['mod.HVAC.volSenSup.V_flow'].values.tolist(),df3_test['mod.HVAC.volSenOA.V_flow'].values.tolist(),df3_test['mod.HVAC.senTSup.T'].values.tolist()]

      
U_3=np.array(U3)
U_3_test=np.array(U3_test)

y_tot3= [df3['mod.HVAC.temSenRet'].values.tolist()]
y_tot3=np.array(y_tot3)

y_tot3_test= [df3_test['mod.HVAC.temSenRet'].values.tolist()]
y_tot3_test=np.array(y_tot3_test)

#System identification
method = 'N4SID'
sys_id3 = system_identification(y_tot3, U_3, method, SS_fixed_order=8)
print(sys_id3)
xid3_test, yid3_test = fsetSIM.SS_lsim_process_form(sys_id3.A, sys_id3.B, sys_id3.C, sys_id3.D, U_3_test, sys_id3.x0)
print(xid3_test,yid3_test)
xid3_train, yid3_train = fsetSIM.SS_lsim_process_form(sys_id3.A, sys_id3.B, sys_id3.C, sys_id3.D, U_3, sys_id3.x0)
print(xid3_train, yid3_train)


#Calculate the metrics 

#corr_coeff_3=r2_score(y_tot3[0],yid3[0]);
mae_3=median_absolute_error(y_tot3_test[0,500:51252],yid3_test[0,500:51252]);
mape_3= mean_absolute_percentage_error(y_tot3_test[0,500:51252],yid3_test[0,500:51252]);
mse_3=mean_squared_error(y_tot3_test[0,500:51252],yid3_test[0,500:51252]);



#plt.close("all")
plt.figure(4)
plt.plot(Time_months3_test[0,0:51252], y_tot3_test[0,0:51252]-273.15)
plt.plot(Time_months3_test[0,0:51252], yid3_test[0,0:51252]-273.15)
plt.plot(Time_months3[0,0:100000], y_tot3[0,0:100000]-273.15)
plt.plot(Time_months3[0,0:100000], yid3_train[0,0:100000]-273.15)
plt.ylabel("Indoor Air Temperature (ºC)")
plt.grid()
plt.xlabel("Time (months)")

plt.title("Comparison of original data and the N4SID model 3")
plt.legend(['Original system Testing', 'Identified system Testing, ' + method,'Original System Training',  'Identified system Training, ' + method])
positions3 = (6, 7, 8,9)
labels3 = ("July", "August", "September", "October")
plt.xticks(positions3, labels3)
plt.ylim([15, 27])




plt.figure(5)
plt.plot(Time_months3_test[0,500:51252], U_3_test[3,500:51252]-273.15)
plt.ylabel("Temperature (ºC)")
plt.grid()
plt.xlabel("Time (months)")
plt.title("Input: Outdoor Temperature Dry Bulb")
plt.ylim([-5, 30])
positions3 = (6, 7, 8,9)
labels3 = ("July", "August", "September", "October")
plt.xticks(positions3, labels3)
plt.show()
r2_m3=(r2_score(yid3_test[0,500:51252], y_tot3_test[0,500:51252]))
print(r2_m3)

plt.show()
#

#MODEL 4 of N4SID: FOURTH 3 MONTHS OF THE DATASET (OCTOBER,NOVEMBER, DECEMBER)

print (df)



#Defining the vectors inputs (u) and outputs (y)#
df4 =df.iloc[453756:553756];
print(df4)

df4_test =df.iloc[553756:605008];
print(df4_test)

#ts2 = 60; "Time in seconds: 60 seconds "
#tfin2 = 605008*60-1
#
#Time2 = np.linspace(302504, tfin2, 302504)
#Time_months2=Time2/24/3600/30;

Time4 = np.array([df4['Time'].values.tolist()])
Time_months4=Time4/24/3600/30;

Time4_test = np.array([df4_test['Time'].values.tolist()])
Time_months4_test=Time4_test/24/3600/30;

       
U4 = [df4['mod.building.weaBus.HDifHor'].values.tolist(), df4['mod.building.weaBus.HDirNor'].values.tolist(), df4['mod.building.weaBus.HHorIR'].values.tolist(), df4['mod.building.weaBus.TBlaSky'].values.tolist(), df4['mod.building.weaBus.TDryBul'].values.tolist(),  df4['mod.building.weaBus.winSpe'].values.tolist(), df4['mod.building.weaBus.winDir'].values.tolist(),df4['mod.building.weaBus.relHum'].values.tolist(),df4['mod.corZon.fmuZon.QCon_flow'].values.tolist(),df4['mod.HVAC.hea.Q_flow'].values.tolist(),df4['mod.HVAC.fan.P'].values.tolist(),df4['mod.HVAC.volSenSup.V_flow'].values.tolist(),df4['mod.HVAC.volSenOA.V_flow'].values.tolist(),df4['mod.HVAC.senTSup.T'].values.tolist()]
U4_test = [df4_test['mod.building.weaBus.HDifHor'].values.tolist(), df4_test['mod.building.weaBus.HDirNor'].values.tolist(), df4_test['mod.building.weaBus.HHorIR'].values.tolist(), df4_test['mod.building.weaBus.TBlaSky'].values.tolist(), df4_test['mod.building.weaBus.TDryBul'].values.tolist(),  df4_test['mod.building.weaBus.winSpe'].values.tolist(), df4_test['mod.building.weaBus.winDir'].values.tolist(),df4_test['mod.building.weaBus.relHum'].values.tolist(),df4_test['mod.corZon.fmuZon.QCon_flow'].values.tolist(),df4_test['mod.HVAC.hea.Q_flow'].values.tolist(),df4_test['mod.HVAC.fan.P'].values.tolist(),df4_test['mod.HVAC.volSenSup.V_flow'].values.tolist(),df4_test['mod.HVAC.volSenOA.V_flow'].values.tolist(),df4_test['mod.HVAC.senTSup.T'].values.tolist()]

      
U_4=np.array(U4)
U_4_test=np.array(U4_test)

y_tot4= [df4['mod.HVAC.temSenRet'].values.tolist()]
y_tot4=np.array(y_tot4)

y_tot4_test= [df4_test['mod.HVAC.temSenRet'].values.tolist()]
y_tot4_test=np.array(y_tot4_test)

#System identification
method = 'N4SID'
sys_id4 = system_identification(y_tot4, U_4, method, SS_fixed_order=8)
print(sys_id4)
xid4_test, yid4_test = fsetSIM.SS_lsim_process_form(sys_id4.A, sys_id4.B, sys_id4.C, sys_id4.D, U_4_test, sys_id4.x0)
print(xid4_test,yid4_test)
xid4_train, yid4_train = fsetSIM.SS_lsim_process_form(sys_id4.A, sys_id4.B, sys_id4.C, sys_id4.D, U_4, sys_id4.x0)
print(xid4_train, yid4_train)


#Calculate the metrics 

#corr_coeff_3=r2_score(y_tot3[0],yid3[0]);
mae_4=median_absolute_error(y_tot4_test[0,500:51252],yid4_test[0,500:51252]);
mape_4= mean_absolute_percentage_error(y_tot4_test[0,500:51252],yid4_test[0,500:51252]);
mse_4=mean_squared_error(y_tot4_test[0,500:51252],yid4_test[0,500:51252]);



#plt.close("all")
plt.figure(6)
plt.plot(Time_months4_test[0,0:51252], y_tot4_test[0,0:51252]-273.15)
plt.plot(Time_months4_test[0,0:51252], yid4_test[0,0:51252]-273.15)
plt.plot(Time_months4[0,0:100000], y_tot4[0,0:100000]-273.15)
plt.plot(Time_months4[0,0:100000], yid4_train[0,0:100000]-273.15)
plt.ylabel("Indoor Air Temperature (ºC)")
plt.grid()
plt.xlabel("Time (months)")

plt.title("Comparison of original data and the N4SID model 4")
plt.legend(['Original system Testing', 'Identified system Testing, ' + method,'Original System Training',  'Identified system Training, ' + method])
positions4 = (9, 10, 11,12)
labels4 = ("October", "November", "December", "January")
plt.xticks(positions4, labels4)
plt.ylim([15, 27])




plt.figure(7)
plt.plot(Time_months4_test[0,500:51252], U_4_test[3,500:51252]-273.15)
plt.ylabel("Temperature (ºC)")
plt.grid()
plt.xlabel("Time (months)")
plt.title("Input: Outdoor Temperature Dry Bulb")

positions4 = (9, 10, 11,12)
labels4 = ("October", "November", "December", "January")
plt.xticks(positions4, labels4)
plt.show()
r2_m4=(r2_score(yid4_test[0,500:51252], y_tot4_test[0,500:51252]))
print(r2_m4)

plt.show()
#

# MODELS FINISHED. NOW THE METRICS ARE CALCULATED 


metrics1=np.array([mae_1,mape_1,mse_1,r2_m1])
metrics2=np.array([mae_2,mape_2,mse_2,r2_m2])
metrics3=np.array([mae_3,mape_3,mse_3,r2_m3])
metrics4=np.array([mae_4,mape_4,mse_4,r2_m4])

#results=np.array([y_tot1_test[0],yid1_test[0],y_tot2_test0],yid2_test[0],y_tot3_test[0],yid3_test[0],y_tot4_test[0],yid4_test[0]])

np.save('metrics_model_1.npy', metrics1)
np.save('metrics_model_2.npy', metrics2)
np.save('metrics_model_3.npy', metrics3)
np.save('metrics_model_4.npy', metrics4)

Estimated_T_1=yid1_test;
Estimated_T_2=yid2_test;
Estimated_T_3=yid3_test;
Estimated_T_4=yid4_test;

# SAVE THE OUTPUTS OF THE BOTH MODELS

np.save('estimated_T1.npy', Estimated_T_1)
np.save('estimated_T2.npy', Estimated_T_2)
np.save('estimated_T3.npy', Estimated_T_3)
np.save('estimated_T4.npy', Estimated_T_4)
#np.savetxt("results_.csv", results, delimiter=",")


# GET ALL MATRICES 
A1=sys_id1.A

A2=sys_id2.A

B1=sys_id1.B

B2=sys_id2.B

C1=sys_id1.C

C2=sys_id2.C

D1=sys_id1.D

D2=sys_id2.D

A3=sys_id3.A

A4=sys_id4.A

B3=sys_id3.B

B4=sys_id4.B

C3=sys_id3.C

C4=sys_id4.C

D3=sys_id3.D

D4=sys_id4.D

# GET ALL KALMAN GAINS  

K1=sys_id1.K

K2=sys_id2.K

K3=sys_id3.K

K4=sys_id4.K

# GET ALL KALMAN MATRICES A_K AND B_K 

KA1=sys_id1.A_K

KA2=sys_id2.A_K

KA3=sys_id3.A_K

KA4=sys_id4.A_K

KB1=sys_id1.B_K

KB2=sys_id2.B_K

KB3=sys_id3.B_K

KB4=sys_id4.B_K

#
#
#
 #SAVE ALL MATRICES 
 
np.save('matrix_A1.npy', A1)

np.save('matrix_B1.npy', B1)

np.save('matrix_A2.npy', A2)

np.save('matrix_B2.npy', B2)

np.save('matrix_C1.npy', C1)

np.save('matrix_C2.npy', C2)

np.save('matrix_D1.npy', D1)

np.save('matrix_D2.npy', D2)

np.save('matrix_A3.npy', A3)

np.save('matrix_B3.npy', B3)

np.save('matrix_A4.npy', A4)

np.save('matrix_B4.npy', B4)

np.save('matrix_C3.npy', C3)

np.save('matrix_C4.npy', C4)

np.save('matrix_D3.npy', D3)

np.save('matrix_D4.npy', D4)

#
# #SAVE ALL KALMAN GAINS 
# 
#  
#np.save('matrix_K1.npy', K1)
#
#np.save('matrix_K1.npy', K2)
#
#np.save('matrix_K3.npy', K3)
#
#np.save('matrix_K4.npy', K4)
#
# #SAVE ALL KALMAN MATRICES A_K B_K 
# 
#  
#np.save('matrix_AK1.npy', KA1)
#
#np.save('matrix_AK2.npy', KA2)
#
#np.save('matrix_AK3.npy', KA3)
#
#np.save('matrix_AK4.npy', KA4)
#
#np.save('matrix_AK1.npy', KB1)
#
#np.save('matrix_AK2.npy', KB2)
#
#np.save('matrix_AK3.npy', KB3)
#
#np.save('matrix_AK4.npy', KB4)