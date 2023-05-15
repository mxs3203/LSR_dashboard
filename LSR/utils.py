import os
import random
import time

import numpy as np
#import pygad
import pandas as pd
import sklearn as sklearn
import torch
from werkzeug.datastructures import FileStorage

#import admin
#from LSR_comm import LSR_comm
from LSR.SpectraWizSaver import save_curve
import matplotlib.pyplot as plt

from LSR.Predict10 import Predict10


def generate_random(max):
    return np.array(random.sample(range(0, max), 10), dtype="int")

def readAndCurateCurve(file, sensor='other'):
    with open(file, 'rb') as f2:
         return processFile(f2,sensor=sensor)

def processFile(file, EPS=0.0001, sensor='other'):
    curve = pd.read_csv(file, delimiter=" ", skiprows=1, names=['nm', 'ignore', 'value'])
    curve = curve[curve['nm'].between(350, 750)]#curve.loc[(curve['nm'] >= 350) & (curve['nm'] <= 750)]
    if sensor == 'apogee':
        curve = curve.groupby(np.arange(len(curve)) // 5).agg({"nm": 'mean', 'value': 'mean'})
    curve[curve < 0] = 0
    lsr_peaks = findLSRPeaks(curve)
    log10_curve = np.log10(curve['value'] + EPS)
    return curve, log10_curve, lsr_peaks


def findOptimalNumberForSplit(diff):
    #print("Diff:",diff)
    if diff < 50:
        return 2
    if diff >= 50 and diff < 100:
        return 3
    else:
        return 5

def scale_curve(x_in):
    mn, mx = 0, 500
    x_scaled = (x_in - mn) / (mx - mn)
    return x_scaled


def computeRange(ten_num_range_):
    m = ten_num_range_.mean()
    sd = ten_num_range_.std()
    n = len(ten_num_range_)
    Zstar = 2.56
    lcb = m - Zstar * sd
    ucb = m + Zstar * sd

    my_min = 1000
    my_max = -1
    total = []
    for i in range(0, 10):
        if lcb[i] < 0:
            lcb[i] = 0
        if ucb[i] > 500:
            ucb[i] = 500
        if lcb[i] < my_min:
            my_min = lcb[i]
        if ucb[i] > my_max:
            my_max = ucb[i]
        #print(lcb[i], ucb[i])
        tmp_range = np.arange(int(lcb[i]), int(ucb[i]), findOptimalNumberForSplit(abs(int(lcb[i]) - int(ucb[i]))))
        tmp_range = sklearn.utils.shuffle(tmp_range)
        total.append(tmp_range)
    return total, my_min, my_max


def findLSRTenNumberRange(log_10_curve, ref_auc):
    device = "cpu"
    curve_size = 11
    model = Predict10(curve_size=curve_size)
    model.to(device)
    model.load_state_dict(torch.load("LSR/best_model_11nums.pth"))
    model.eval()

    if ref_auc < 1:
        sd = 1
    elif ref_auc >= 1 and ref_auc < 5:
        sd = 5
    elif ref_auc >= 5 and ref_auc < 20:
        sd = 10
    elif ref_auc >= 20 and ref_auc < 40:
        sd = 45
    elif ref_auc >= 40 and ref_auc < 60:
        sd = 50
    else:
        sd = 60

    solutions = []
    for i in range(0, 5000):
        noisy = np.array([np.random.normal(i,sd ) for i in log_10_curve], dtype="float")
        predicted_ten_nums = model(torch.FloatTensor(noisy))
        predicted_ten_nums = [int(10 ** (item - 0.0001)) for item in predicted_ten_nums]
        solutions.append(predicted_ten_nums)
    return pd.DataFrame(solutions)

def findLSRPeaks(curve_df):
    first = curve_df.loc[(curve_df['nm'] >= 363) & (curve_df['nm'] <= 376), 'value'].mean()
    second = curve_df.loc[(curve_df['nm'] >= 383) & (curve_df['nm'] <= 396), 'value'].mean()
    third = curve_df.loc[(curve_df['nm'] >= 456) & (curve_df['nm'] <= 468), 'value'].mean()
    fourth = curve_df.loc[(curve_df['nm'] >= 436) & (curve_df['nm'] <= 446), 'value'].mean()
    fifth = curve_df.loc[(curve_df['nm'] >= 516) & (curve_df['nm'] <= 536), 'value'].mean()
    six = curve_df.loc[(curve_df['nm'] >= 441) & (curve_df['nm'] <= 448), 'value'].mean()
    six2 = curve_df.loc[(curve_df['nm'] >= 568) & (curve_df['nm'] <= 638), 'value'].mean()
    seven = curve_df.loc[(curve_df['nm'] >= 591) & (curve_df['nm'] <= 596), 'value'].mean()
    eight = curve_df.loc[(curve_df['nm'] >= 626) & (curve_df['nm'] <= 631), 'value'].mean()
    nine = curve_df.loc[(curve_df['nm'] >= 653) & (curve_df['nm'] <= 661), 'value'].mean()
    ten = curve_df.loc[(curve_df['nm'] >= 728) & (curve_df['nm'] <= 741), 'value'].mean()
    return np.array([first,second, third,fourth, fifth, six, six2,seven,eight,nine,ten])

