from itertools import combinations
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json
import uuid

# ACTB
sys.path.insert(0, str(Path(__file__).parent.absolute().parent / 'actb_client'))
from actb_client import ActbClient
from historian import Conversions, Historian

# Math and data
import random
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from joblib import dump

# Machine learning
import sippy as sp
from sippy.functionsetSIM import *
from sklearn.metrics import r2_score, mean_squared_error, median_absolute_error
from sklearn import linear_model
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline



class Metamodel:

    def __init__(self, step, config, method):
        self.config = config
        self.step = step
        self.historian = Historian(time_step=int(step/60))
        self.method = method
        day = int(3600 * 24 / step)

        start_sec = self.config.training['start']
        length = self.config.training['length']
        training_frac = self.config.training['training']
        freefloat_frac = self.config.training['freefloat']
        rbc_frac = self.config.training['rbc']
        randomized_frac = 1 - freefloat_frac - rbc_frac
        tr_len = length / 24 / 3600
        self.training = int(training_frac * tr_len * day)
        self.testing = int((1 - training_frac) * tr_len * day)
        self.start_day = self.training

        self.training_split = dict(freefloat=[], rbc=[], randomized=[])
        self.training_split['freefloat'] = [start_sec, int(start_sec + freefloat_frac * training_frac * length)]
        self.training_split['rbc'] = [self.training_split['freefloat'][1],
                                      self.training_split['freefloat'][1] + int(rbc_frac * training_frac * length)]
        self.training_split['randomized'] = [self.training_split['rbc'][1],
                                             self.training_split['rbc'][1] + int(randomized_frac * training_frac * length)]
        self.testing_split = [self.training_split['randomized'][1], start_sec + length]

    def create_id_and_folders(self):
        self.id = uuid.uuid4().hex
        folder_num = 1
        while os.path.isdir(str(Path(__file__).parent.absolute().parent / 'testcases' / 'SpawnResources' / self.config.metamodel / 'metamodels' / str(folder_num))):
            folder_num += 1
        self.outdir = str(Path(__file__).parent.absolute().parent / 'testcases' / 'SpawnResources' / self.config.metamodel / 'metamodels' / str(folder_num))
        os.makedirs(self.outdir)
        self.metaparams = {
            'SpawnModel' : self.config.metamodel,
            'id' : self.id,
            'step' : self.step,
            'outputs' : list(self.config.outputs.keys()),
        }

    def select_method(self):
        if self.method is None:
            print("No method specified. Please select a method in this list:\n1. N4SID (state-space model)\n2. Linear regression\n3. Polynomial linear regression\n4. LASSO regression\n5. Support vector regression\n6. Random forest regressor\n---More methods will be supported in the future.")
            method_in = int(input("Enter your choice (1-5)"))
            while method_in not in [1, 2, 3, 4, 5, 6]:
                method_in = int(input("Method not recognized. Please input a number between 1 and 3."))
            if method_in == 1:
                self.method = 'N4SID'
            elif method_in == 2:
                self.method = 'LREG'
            elif method_in == 3:
                self.method = 'PLREG'
            elif method_in == 4:
                self.method = 'LASSO'
            elif method_in == 5:
                self.method = 'SVR'
            else: 
                self.method = 'CART'
        if self.method == 'N4SID':
            self.n4sid()
        elif self.method == 'LREG':
            self.linear_regression()
        elif self.method == 'PLREG':
            self.polynomial_regression()
        elif self.method == 'LASSO':
            self.lasso_regression(alpha=0.1)
        elif self.method == 'SVR':
            self.svr()
        else:
            self.rcart()

    def pre_process_data(self):
        files = os.listdir(str(Path(self.outdir).parent.absolute()))
        if 'spawnDataset.csv' not in files:
            print("No dataset available in the output directory for metamodel ID %s, generating new one."%(self.id))
            self.generate_data()
        else:
            print("Found spawnDataset.csv in the output directory for ID %s.\nThe model will be extracted from that data. If you do not want to use that data, please delete it from the metamodel directory.")
        self.split_dataset()

    def write_metaparams(self):
        
        self.metaparams['uvect'] = list(self.X_train.columns)
        self.metaparams['tvps'] = [item for item in self.metaparams['uvect'] if item not in self.config.inputs.keys()]
        self.metaparams['method'] = self.method
        #self.metaparams['R^2 score'] = r2
        with open(self.outdir + '/' + 'config.json', 'w') as outjson:
            json.dump(self.metaparams, outjson)

    def n4sid(self):
        print("You have selected N4SID. Please choose a model selection method:\n1. Best subset selection. \n\tVery long, especially for >10 inputs, but more accurate.\n2. Forward step-wise selection. \n\tFaster, but might be trapped in a local optimum\n3. None.\n\tJust use all available inputs. Sub-optimal unless you have already identified the best inputs.")
        model_select = int(input("Your choice (1-3):"))
        while model_select not in [1, 2, 3]:
            model_select = int(input("Model selection method not recognized. Please input a number between 1 and 3."))
        if model_select == 1:
            method = 'N4SID-BSS'
            A, B, C, AK, BK, K, x, uvect, r2 = self.extract_n4sid(select='bss')
        elif model_select == 2:
            method = 'N4SID-FSS'
            A, B, C, AK, BK, K, x, uvect, r2 = self.extract_n4sid(select='fss')
        else:
            method = 'N4SID-NoSelection'
            A, B, C, AK, BK, K, x, uvect, r2 = self.extract_n4sid(select='')
        np.save(os.path.join(self.outdir, 'A'), A)
        np.save(os.path.join(self.outdir, 'B'), B)
        np.save(os.path.join(self.outdir, 'C'), C)
        np.save(os.path.join(self.outdir, 'AK'), AK)
        np.save(os.path.join(self.outdir, 'BK'), BK)
        np.save(os.path.join(self.outdir, 'K'), K)
        np.save(os.path.join(self.outdir, 'x0'), x)
        self.write_metaparams(uvect, method, r2)

    def linear_regression(self, **kwargs):

        print("Fitting model using ordinary least squares regression")
        lin_reg = linear_model.LinearRegression(**kwargs).fit(self.X_train, self.y_train)
        print("Debug - Training accuracy: %.2f"%(lin_reg.score(self.X_train, self.y_train)))
        print("The model's prediction R2 coefficient is: %.3f"%(lin_reg.score(self.X_test, self.y_test)))
        train = lin_reg.predict(self.X_train)
        test = lin_reg.predict(self.X_test)
        plt.figure()
        plt.ylabel('Prediction')
        plt.xlabel('Steps')
        plt.plot(self.y_test.to_numpy(), label='Ground truth')
        plt.plot(test, label='Prediction')
        plt.legend()
        plt.show()
        dump(lin_reg, self.outdir + '/' + 'lin_reg_params.joblib')
        np.save(os.path.join(self.outdir, 'lin_coeffs'), lin_reg.coef_)
        np.save(os.path.join(self.outdir, 'lin_intercepts'), lin_reg.intercept_)

    def polynomial_regression(self, **kwargs):
        print("Fitting model using poynomial regression")
        degree = int(input("Please select a degree for the regression\n"))
        pol_reg = Pipeline([('poly', PolynomialFeatures(degree=degree)),('linear', linear_model.LinearRegression())])
        pol_reg.fit(self.X_train, self.y_train)
        print("Debug - Training accuracy: %.2f"%(pol_reg.score(self.X_train, self.y_train)))
        print("The model's prediction R2 coefficient is: %.3f"%(pol_reg.score(self.X_test, self.y_test)))
        train = pol_reg.predict(self.X_train)
        test = pol_reg.predict(self.X_test)
        plt.figure()
        plt.ylabel('Prediction')
        plt.xlabel('Steps')
        plt.plot(self.y_test.to_numpy(), label='Ground truth')
        plt.plot(test, label='Prediction')
        plt.legend()
        plt.show()
        dump(pol_reg, self.outdir + '/' + 'lin_reg_params.joblib')
        np.save(os.path.join(self.outdir, 'lin_coeffs'), pol_reg.named_steps['linear'].coef_)
        np.save(os.path.join(self.outdir, 'lin_intercepts'), pol_reg.named_steps['linear'].intercept_)
        print(pol_reg.named_steps['linear'].coef_)
        print(pol_reg.named_steps['linear'].intercept_)

    def lasso_regression(self, **kwargs):

        print("Fitting model using LASSO regression")
        lasso_reg = linear_model.Lasso(**kwargs).fit(self.X_train, self.y_train)
        print("Debug - Training accuracy: %.2f"%(lasso_reg.score(self.X_train, self.y_train)))
        print("The model's prediction R2 coefficient is: %.3f"%(lasso_reg.score(self.X_test, self.y_test)))
        train = lasso_reg.predict(self.X_train)
        test = lasso_reg.predict(self.X_test)
        plt.figure()
        plt.ylabel('Prediction')
        plt.xlabel('Steps')
        plt.plot(self.y_test.to_numpy(), label='Ground truth')
        plt.plot(test, label='Prediction')
        plt.legend()
        plt.show()
        dump(lasso_reg, self.outdir + '/' + 'lasso_reg_params.joblib')
        np.save(os.path.join(self.outdir, 'lasso_coeffs'), lasso_reg.coef_)
        np.save(os.path.join(self.outdir, 'lasso_intercepts'), lasso_reg.intercept_)

    def svr(self, **kwargs):

        print('Fitting model using support vector regression')
        svreg = svm.SVR().fit(self.X_train, self.y_train)
        print("Debug - Training accuracy: %.2f"%(svreg.score(self.X_train, self.y_train)))
        print("The model's prediction R2 coefficient is: %.3f"%(svreg.score(self.X_test, self.y_test)))
        train = svreg.predict(self.X_train)
        test = svreg.predict(self.X_test)
        plt.figure()
        plt.ylabel('Prediction')
        plt.xlabel('Steps')
        plt.plot(self.y_test.to_numpy(), label='Ground truth')
        plt.plot(test, label='Prediction')
        plt.legend()
        plt.show()
        dump(svreg, self.outdir + '/' + 'svreg_params.joblib')

    def rcart(self, **kwargs):
        X_train = self.X_train.to_numpy()
        y_train = self.y_train.to_numpy()
        X_test = self.X_test.to_numpy()
        y_test = self.y_test.to_numpy()
        randomforest = RandomForestRegressor(random_state=0)
        randomforest.fit(X_train, y_train)
        test = randomforest.predict(X_test)
        plt.figure()
        plt.ylabel('Prediction')
        plt.xlabel('Steps')
        plt.plot(y_test, label='Ground truth')
        plt.plot(test, label='Prediction')
        plt.legend()
        plt.show()

        dump(randomforest, self.outdir + '/' + 'randomforest_params.joblib')
        


    def generate_matrices(self, generatedata, modelselection, override=None):

        if generatedata:
            self.generate_data()
        self.split_dataset()
        A, B, C, AK, BK, K, x, uvect = self.extract(select=modelselection, override=override)
        outpath = str(Path(__file__).parent.absolute().parent / 'testcases' / 'SpawnResources' / self.config.metamodel / 'metamodel')
        np.save(os.path.join(outpath, 'A'), A)
        np.save(os.path.join(outpath, 'B'), B)
        np.save(os.path.join(outpath, 'C'), C)
        np.save(os.path.join(outpath, 'AK'), AK)
        np.save(os.path.join(outpath, 'BK'), BK)
        np.save(os.path.join(outpath, 'K'), K)
        np.save(os.path.join(outpath, 'x0'), x)
        config = {'uvect' : uvect,
                  'tvps' : [item for item in uvect if item not in self.config.inputs.keys()],
                  'outputs' : list(self.config.outputs.keys()),
                  'step' : self.step}
        with open(outpath + '/' + 'config.json', 'w') as outjson:
            json.dump(config, outjson)


    def generate_data(self):
        print('Generating data, using Spawn simulation')
        self.datetime = datetime.strptime(self.config.start, '%y/%m/%d %H:%M:%S')
        self.client = ActbClient(url=self.config.url)#, metamodel=self.config.metamodel)
        for sensor in self.config.sensors:
            self.historian.add_point(sensor, None, sensor)
        for input in self.config.inputs.keys():
            self.historian.add_point(input, None, input)
        for forecast in self.config.forecasts:
            self.historian.add_point(forecast, None, forecast)
        for output in self.config.outputs.keys():
            self.historian.add_point(output, None, output)
        self.historian.add_point('timestamp', None, None)

        initparams = {'start_time': self.config.training['start'], 'warmup_period': 0}
        self.res = self.client.initialize(self.config.metamodel, **initparams)
        self.client.set_step(step=self.step)

        self.get_spawn_data(self.training_split['freefloat'], 'freefloat')
        self.get_spawn_data(self.training_split['rbc'], 'rbc')
        self.get_spawn_data(self.training_split['randomized'], 'randomized')
        self.get_spawn_data(self.testing_split, 'randomized')
        self.historian.save_csv(str(Path(self.outdir).parent.absolute()), 'spawnDataset.csv')
        self.client.stop()


    def new_u(self, res, u):

        violation = False
        changed = False
        for output in self.config.outputs.keys():
            if self.config.outputs[output]['min'] > res[output] > self.config.outputs[output]['max']:
                violation = True
        for input in u.keys():
            if 'activate' not in input and input in self.config.inputs:
                if self.config.inputs[input]['type'] == 'float':
                    if violation:
                        u[input] = self.config.inputs[input]['min']
                    elif self.lastchange >= 3600:
                        changed = True
                        u[input] = max(self.config.inputs[input]['min'],
                                   min(round(random.uniform(u[input] * (1 - self.config.var),
                                                            max(self.config.var, u[input] * (1 + self.config.var))), 3),
                                       self.config.inputs[input]['max']))

                else:
                    if violation:
                        u[input] = 0
                    elif self.lastchange >= 3600:
                        changed = True
                        u[input] = max(0, min(round(random.uniform(u[input] * (1 + self.config.var),
                                                                u[input] * (1 - self.config.var)), 3),
                                              1)
                                       )
        if changed:
            self.lastchange = 0
        return u

    def get_spawn_data(self, interval, controltype):
        start = interval[0]
        stop = interval[1]
        if start == stop:
            return
        u = {}
        if controltype == 'freefloat':
            print('Generating data in free floating mode')
        elif controltype == 'rbc':
            print('Generating data using underlying rule-based controls')
        else:
            print('Generating data using randomized inputs.')
        for input in self.config.inputs.keys():
            if self.config.inputs[input]['type'] == 'float':
                u[input] = self.config.inputs[input]['min']
            else:
                u[input] = 0
            if controltype == 'freefloat' or controltype == 'randomized':
                u[input.replace('_u', '_activate')] = 1
            elif controltype == 'rbc':
                u[input.replace('_u', '_activate')] = 0
        for deactivated in self.config.deactivate.keys():
            if self.config.deactivate[deactivated]['type'] == 'float':
                u[deactivated] = self.config.deactivate[deactivated]['min']
            else:
                u[deactivated] = 0
                u[deactivated.replace('_u', '_activate')] = 1
        if controltype == 'randomized':
            self.lastchange = 0
        for i in range(0, stop - start + self.step,
                       self.step):
            if controltype == 'randomized':
                u = self.new_u(self.res, u)
                self.lastchange += self.step
            self.res = self.client.advance(control_u=u)
            forecasts = self.client.get_forecasts()
            self.historian.add_data({forecast: forecasts[forecast][0] for forecast in forecasts})
            self.historian.add_data(self.res)
            self.historian.add_data(u)
            self.datetime += timedelta(seconds=self.step)
            self.historian.add_datum('timestamp', self.datetime)

            print('\rProgress: {}%'.format(round(100 * i / (stop - start + self.step), 2)), end='')
        print('\rDone.              ')

    def get_dataset(self, datafile):

        origdata = pd.DataFrame(pd.read_csv(datafile, delimiter=','))
        origdata.drop(['timestamp'], axis=1, inplace=True)
        origdata.set_index(origdata.columns[0])
        origdata.drop(origdata.columns[0], axis=1, inplace=True)

        return origdata

    def split_dataset(self):
        filepath = str(Path(__file__).parent.absolute().parent / 'testcases' /
                       'SpawnResources' / self.config.metamodel / 'metamodels' / 'spawnDataset.csv')
        self.data = self.get_dataset(filepath)
        self.data = self.data.loc[:, (self.data != self.data.iloc[0]).any()] # remove constant columns
        self.include = []
        self.estimate = []
        for sensor in self.config.sensors:
            self.include.extend([sensor])
        for input in self.config.inputs.keys():
            self.include.extend([input])
        for output in self.config.outputs.keys():
            self.estimate.extend([output])
        for forecast in self.config.forecasts:
            self.include.extend([forecast])

        X_train = self.data[self.include].iloc[self.start_day - self.training:]
        y_train = self.data[self.estimate].iloc[self.start_day - self.training:]
        if self.start_day != 0 and self.start_day < self.training:
            X_train = X_train.append(self.data[self.include].iloc[: self.start_day])
            y_train = y_train.append(self.data[self.estimate].iloc[: self.start_day])
        X_test = self.data[self.include].iloc[self.start_day: self.start_day + self.testing]
        y_test = self.data[self.estimate].iloc[self.start_day: self.start_day + self.testing]
        y_train = y_train.apply(toCelsius)
        y_test = y_test.apply(toCelsius)
        #X_train = normalize_data(X_train)
        #X_test = normalize_data(X_test)

        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test


    def bss(self):
        minComb = 2
        maxComb = len(self.X_train.columns) + 1
        failed = []
        metrics = {}
        repeats = 10
        print('Selecting model using best subset selection.')
        for i in range(minComb, maxComb):
            comb = list(combinations(self.X_train.columns, i))
            print('Testing {} combinations of {} inputs'.format(len(comb), i))
            if i == maxComb - 1:
                comb.append(tuple(self.include))
            for j in range(len(comb)):
                if 'time' not in comb[j]:
                    try:
                        training_bss = self.X_train[list(comb[j])].to_numpy().transpose()
                        testing_bss = self.X_test[list(comb[j])].to_numpy().transpose()
                        sid = sp.system_identification(self.y_train, training_bss, self.method, IC='AICc',
                                                       SS_D_required=False)
                        x, y = sp.functionsetSIM.SS_lsim_process_form(sid.A, sid.B, sid.C, sid.D, testing_bss)
                        for i in range(repeats):
                            x, y = sp.functionsetSIM.SS_lsim_process_form(sid.A, sid.B, sid.C, sid.D, testing_bss,
                                                                          x[:, -1:])
                        metrics[comb[j]] = r2_score(self.y_test, y[0])
                    except Exception as e:
                        failed.append(comb[j])
                        continue
                print('\r Testing combination {} of {}...'.format(j, len(comb)))
            print('Best score so far: ', max(metrics, key=metrics.get), metrics[max(metrics, key=metrics.get)])
        bestsubset = list(max(metrics, key=metrics.get))
        print("Best combination overall:", max(metrics, key=metrics.get), metrics[max(metrics, key=metrics.get)])
        return bestsubset

    def fss(self):

        selected = []
        scores = []
        identifiers = []
        repeats = 10
        print('Selecting model using forward stepwise selection.')

        while len(selected) < len(self.X_train.columns):
                for identifier in self.X_train.columns:
                    new = selected.copy()
                    if identifier not in new:
                        new.extend([identifier])
                        training_fss = self.X_train[new].to_numpy().transpose()
                        testing_fss = self.X_test[new].to_numpy().transpose()
                        sid = sp.system_identification(self.y_train, training_fss, self.method, IC='AICc',
                                                       SS_D_required=False)
                        x, y = sp.functionsetSIM.SS_lsim_process_form(sid.A, sid.B, sid.C, sid.D, testing_fss)
                        # for i in range(repeats):
                        #     x, y = sp.functionsetSIM.SS_lsim_process_form(sid.A, sid.B, sid.C, sid.D, testing_fss, x[:, -2:])
                        r2 = r2_score(self.y_test, y.transpose())
                        if scores == [] or r2 > max(scores):
                            scores.extend([r2])
                            identifiers.append(new)

                for score, identifier in zip(scores, identifiers):
                    if score == max(scores):
                        scores = [score]
                        identifiers = [identifier]
                if selected == identifiers[0]:
                    break
                else:
                    selected = identifiers[0].copy()
                print(scores, selected)
        print('Best combination: ', selected)
        print('Best score: ', scores[0])
        return selected

    def extract_n4sid(self, select='', override=None):

        if select == 'bss':
            estimators = self.bss()
        elif select == 'fss':
            estimators = self.fss()
        elif select == 'override':
            estimators = override
        else:
            estimators = self.include

        repeats = 200
        uvect = list(self.X_train[estimators].columns)
        X_train_sid = self.X_train[estimators].to_numpy().transpose()
        y_train_sid = self.y_train.to_numpy().transpose()
        X_test_sid = self.X_test[estimators].to_numpy().transpose()
        y_test_sid = self.y_test.to_numpy().transpose()
        sid = sp.system_identification(y_train_sid, X_train_sid, self.method, SS_fixed_order=12, SS_A_stability=True)#IC='AICc', SS_D_required=False)
        x, y = sp.functionsetSIM.SS_lsim_process_form(sid.A, sid.B, sid.C, sid.D, X_test_sid)
        xp, yp = sp.functionsetSIM.SS_lsim_innovation_form(sid.A, sid.B, sid.C, sid.D, sid.K, y_test_sid, X_test_sid)
        for i in range(repeats):
            x, y = sp.functionsetSIM.SS_lsim_process_form(sid.A, sid.B, sid.C, sid.D, X_test_sid, x[:, -1:])
            xp, yp = sp.functionsetSIM.SS_lsim_innovation_form(sid.A, sid.B, sid.C, sid.D, sid.K, y_test_sid,
                                                               X_test_sid, xp[:, -1:])

        r2 = r2_score(y_test_sid, y)
        print('R²: ', r2)
        print('MAE: ', median_absolute_error(y_test_sid, y))
        print('MSE: ', mean_squared_error(y_test_sid, y))

        testaxis = range(len(y.transpose()))

        plt.figure(figsize=(20, 10))
        plt.ylabel('Temp')
        plt.plot(testaxis, y.transpose(), label='predicted - process')
        #plt.plot(testaxis, yp.transpose(), label='predicted - innovation')
        plt.plot(testaxis, y_test_sid.transpose(), label='ground truth')
        plt.legend()
        plt.show()

        return sid.A, sid.B, sid.C, sid.A_K, sid.B_K, sid.K, x[:, -1], uvect, r2


def toInt(a):
    return int(a)


def toCelsius(a):
    return a - 273.15


def normalize_data(df):
    normalized_df = (df - df.min()) / (df.max() - df.min())
    return normalized_df
