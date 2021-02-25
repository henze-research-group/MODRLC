#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 17:47:37 2021

@author: joseleiva
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#matplotlib inline
plt.style.use('ggplot')
import warnings; warnings.simplefilter('ignore')


##STANDARIZE THE DATA 

from sklearn.preprocessing import StandardScaler


scaler = StandardScaler()


df = pd.read_csv("wrapped 2.csv")
dfs=scaler.fit_transform(df)

df1 =dfs[0:302504];
df2 =dfs[302504:605008];

U1=np.transpose(np.load('estimated_T1.npy'))
U2=np.transpose(np.load('estimated_T2.npy'))
U1=U1[:,0];
U2=U2[:,0];

y_tot1= (df1[:,13], df1[:,14], df1[:,15])
y_tot2= (df2[:,13], df2[:,14], df2[:,15])



Y1=y_tot1[0]+y_tot1[1]/0.8+y_tot1[2];
Y2=y_tot2[0]+y_tot2[1]/0.8+y_tot2[2];


#
#U1 = [df1['mod.building.weaBus.HDifHor'].values.tolist(), df1['mod.building.weaBus.HDirNor'].values.tolist(),df1['mod.building.weaBus.HGloHor'].values.tolist(), df1['mod.building.weaBus.HHorIR'].values.tolist(),df1['mod.building.weaBus.TBlaSky'].values.tolist(), df1['mod.building.weaBus.TDryBul'].values.tolist(), df1['mod.building.weaBus.TWetBul'].values.tolist(), df1['mod.building.weaBus.winSpe'].values.tolist(), df1['mod.building.weaBus.winDir'].values.tolist(),df1['mod.building.weaBus.relHum'].values.tolist(),df1['mod.corZon.fmuZon.QCon_flow'].values.tolist(),df1['mod.HVAC.hea.Q_flow'].values.tolist(),df1['mod.HVAC.fan.P'].values.tolist(),df1['mod.HVAC.volSenSup.V_flow'].values.tolist(),df1['mod.HVAC.volSenOA.V_flow'].values.tolist(),df1['mod.HVAC.senRelHum.phi'].values.tolist(),df1['mod.HVAC.senTSup.T'].values.tolist()]
#
#      
#U_1=np.array(U1)

##SPLIT THE DATA 
#
#X = dfs.drop(['mpg'], axis=1)
#y = dfs['mpg']
#
#from sklearn.model_selection import train_test_split #NOT NECESSARY 
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=10) #NOT NECESSARY 
#
#
##LASSO REGRESSION 
#
#
#from sklearn.linear_model import Lasso
#
#reg = Lasso(alpha=0.5)
#reg.fit(X_train, y_train)
#
#print('Lasso Regression: R^2 score on training set', reg.score(X_train, y_train)*100)
#print('Lasso Regression: R^2 score on test set', reg.score(X_test, y_test)*100)
#
#
## LASSO USING DIFFERENT LAMBDAS 
#
#lambdas = (0.001, 0.01, 0.1, 0.5, 1, 2, 10)
#l_num = 7
#pred_num = X.shape[1]
#
## prepare data for enumerate
#coeff_a = np.zeros((l_num, pred_num))
#train_r_squared = np.zeros(l_num)
#test_r_squared = np.zeros(l_num)
## enumerate through lambdas with index and i
#for ind, i in enumerate(lambdas):    
#    reg = Lasso(alpha = i)
#    reg.fit(X_train, y_train)
#
#    coeff_a[ind,:] = reg.coef_
#    train_r_squared[ind] = reg.score(X_train, y_train)
#    test_r_squared[ind] = reg.score(X_test, y_test)
#
#
## Plotting
#    
#plt.figure(figsize=(18, 8))
#plt.plot(train_r_squared, 'bo-', label=r'$R^2$ Training set', color="darkblue", alpha=0.6, linewidth=3)
#plt.plot(test_r_squared, 'bo-', label=r'$R^2$ Test set', color="darkred", alpha=0.6, linewidth=3)
#plt.xlabel('Lamda index'); plt.ylabel(r'$R^2$')
#plt.xlim(0, 6)
#plt.title('Evaluate lasso regression with lamdas: 0 = 0.001, 1= 0.01, 2 = 0.1, 3 = 0.5, 4= 1, 5= 2, 6 = 10')
#plt.legend(loc='best')
#plt.grid()
#
##INDENTIFY THE BEST LAMBDA AND COEFFICIENTS 
#
#df_lam = pd.DataFrame(test_r_squared*100, columns=['R_squared'])
#df_lam['lambda'] = (lambdas)
## returns the index of the row where column has maximum value.
#print(df_lam.loc[df_lam['R_squared'].idxmax()])


## Coefficients of best model
#reg_best = Lasso(alpha = 0.1)
#reg_best.fit(X_train, y_train)
#print(reg_best.coef_)
#
#from sklearn.metrics import mean_squared_error
#print(mean_squared_error(y_test, reg_best.predict(X_test)))
#
#
#
##Cross Validation 
#
#l_min = 0.05
#l_max = 0.2
#l_num = 20
#lambdas = np.linspace(l_min,l_max, l_num)
#
#train_r_squared = np.zeros(l_num)
#test_r_squared = np.zeros(l_num)
#
#pred_num = X.shape[1]
#coeff_a = np.zeros((l_num, pred_num))
#
#
#from sklearn.model_selection import cross_val_score
#
#for ind, i in enumerate(lambdas):    
#    reg = Lasso(alpha = i)
#    reg.fit(X_train, y_train)
#    results = cross_val_score(reg, X, y, cv=5, scoring="r2")
#
#    train_r_squared[ind] = reg.score(X_train, y_train)    
#    test_r_squared[ind] = reg.score(X_test, y_test)
#
## Plotting
#plt.figure(figsize=(18, 8))
#plt.plot(train_r_squared, 'bo-', label=r'$R^2$ Training set', color="darkblue", alpha=0.6, linewidth=3)
#plt.plot(test_r_squared, 'bo-', label=r'$R^2$ Test set', color="darkred", alpha=0.6, linewidth=3)
#plt.xlabel('Lamda value'); plt.ylabel(r'$R^2$')
#plt.xlim(0, 19)
#plt.title(r'Evaluate 5-fold cv with different lamdas')
#plt.legend(loc='best')
#plt.grid()
#
## IDENTIFY THE BEST MODEL AND SAVE ITS VALUES 
#
#
#df_lam = pd.DataFrame(test_r_squared*100, columns=['R_squared'])
#df_lam['lambda'] = (lambdas)
## returns the index of the row where column has maximum value.
#df_lam.loc[df_lam['R_squared'].idxmax()]
#
## Best Model
#reg_best = Lasso(alpha = 0.144737)
#print(reg_best.fit(X_train, y_train))

















