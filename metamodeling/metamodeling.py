from itertools import combinations

import matplotlib.pyplot as plt
import pandas as pd
import sippy as sp
from sippy.functionsetSIM import *
from sklearn.metrics import r2_score, mean_squared_error, median_absolute_error


class Metamodel:

    def __init__(self, datafile, step):

        self.data = self.get_dataset(datafile)
        self.step = step

    def get_dataset(self, datafile):

        origdata = pd.DataFrame(pd.read_csv(datafile, delimiter=','))
        self.include = origdata.columns

        return origdata

    def set_identification_parameters(self, estimate, method='N4SID', training=30, testing=10, start_day=0):
        step = self.step
        self.estimate = estimate
        self.method = method
        self.step = step
        day = int(3600 * 24 / step)
        self.training = training * day
        self.testing = testing * day
        self.start_day = start_day * day

    def split_dataset(self, estimate):

        X_train = self.data[self.include].iloc[self.start_day - self.training:]
        y_train = self.data[estimate].iloc[self.start_day - self.training:]
        if self.start_day != 0 and self.start_day < self.training:
            X_train = X_train.append(self.data[self.include].iloc[: self.start_day])
            y_train = y_train.append(self.data[estimate].iloc[: self.start_day])
        X_test = self.data[self.include].iloc[self.start_day: self.start_day + self.testing]
        y_test = self.data[estimate].iloc[self.start_day: self.start_day + self.testing]
        y_train = y_train.apply(toCelsius)
        y_test = y_test.apply(toCelsius)
        X_train = normalize_data(X_train)
        X_test = normalize_data(X_test)

        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

    def bss(self):
        minComb = 2
        maxComb = len(self.X_train.columns) + 1
        failed = []
        metrics = {}
        for i in range(minComb, maxComb):
            comb = list(combinations(self.X_train.columns, i))
            if i == maxComb - 1:
                comb.append(tuple(self.include))
            for j in range(len(comb)):
                if 'time' not in comb[j]:
                    try:
                        training_bss = self.X_train[list(comb[j])].to_numpy().transpose()
                        testing_bss = self.X_test[list(comb[j])].to_numpy().transpose()
                        sid = sp.system_identification(self.y_train, training_bss, self.method, IC='AICc',
                                                       SS_D_required=False)
                        x, y = sp.functionsetSIM.SS_lsim_predictor_form(sid.A_K, sid.B_K, sid.C, sid.D, sid.K,
                                                                        np.array([self.y_train]), testing_bss)
                        x, y = sp.functionsetSIM.SS_lsim_process_form(sid.A, sid.B, sid.C, sid.D, testing_bss,
                                                                      x[:, -2:])
                        metrics[comb[j]] = r2_score(self.y_test, y[0])
                    except Exception as e:
                        failed.append(comb[j])
                        continue
        bestsubset = list(max(metrics, key=metrics.get))
        print("Best combination:", max(metrics, key=metrics.get), metrics[max(metrics, key=metrics.get)])
        return bestsubset

    def fss(self):
        # todo: add FSS
        return None

    def extract(self, select='', override=None):

        if select == 'bss':
            estimators = self.bss()
        elif select == 'fss':
            estimators = self.fss()
        elif select == 'override':
            estimators = override
        else:
            estimators = self.include

        repeats = 5
        X_train_sid = self.X_train[estimators].to_numpy().transpose()
        y_train_sid = self.y_train.to_numpy()
        X_test_sid = self.X_test[estimators].to_numpy().transpose()
        y_test_sid = self.y_test.to_numpy()
        sid = sp.system_identification(y_train_sid, X_train_sid, self.method, IC='AICc', SS_D_required=False)
        x, y = sp.functionsetSIM.SS_lsim_process_form(sid.A, sid.B, sid.C, sid.D, X_train_sid)

        print('R²: ', r2_score(y_train_sid, y[0]))
        print('MAE: ', median_absolute_error(y_train_sid, y[0]))
        print('MSE: ', mean_squared_error(y_train_sid, y[0]))

        for i in range(repeats):
            x_, y_ = sp.functionsetSIM.SS_lsim_process_form(sid.A, sid.B, sid.C, sid.D, X_test_sid, x[:, -2:])

        testaxis = np.arange(1, len(self.X_test[self.X_test.columns[0]]) + 1)

        plt.figure(figsize=(20, 10))
        plt.ylabel('Temp')
        plt.plot(testaxis, y_[0], testaxis, y_test_sid)
        plt.show()

        return sid.A, sid.B, sid.C, sid.A_K, sid.B_K, sid.K, x_[:, -1]


def toInt(a):
    return int(a)


def toCelsius(a):
    return a - 273.15


def normalize_data(df):
    normalized_df = (df - df.min()) / (df.max() - df.min())
    return normalized_df
