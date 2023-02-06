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

def readAndCurateCurve(file):
    with open(file, 'rb') as f2:
         return processFile(f2)

def processFile(file, EPS=0.0001):
    curve = pd.read_csv(file, delimiter=" ", skiprows=1, names=['nm', 'ignore', 'value'])
    curve = curve.loc[(curve['nm'] >= 350) & (curve['nm'] <= 750)]
    curve = curve.groupby(np.arange(len(curve)) // 5).agg({"nm": 'mean', 'value': 'mean'})
    curve[curve < 0] = 0
    log10_curve = np.log10(curve['value'] + EPS)
    return curve, log10_curve


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
    Zstar = 1.96
    lcb = m - Zstar * sd
    ucb = m + Zstar * sd

    my_min = 1000
    my_max = -1
    total = []
    for i in range(0, 10):
        if lcb[i] < 0:
            lcb[i] = 0
        if ucb[i] > 200:
            ucb[i] = 200
        if lcb[i] < my_min:
            my_min = lcb[i]
        if ucb[i] > my_max:
            my_max = ucb[i]
        #print(lcb[i], ucb[i])
        tmp_range = np.arange(int(lcb[i]), int(ucb[i]), findOptimalNumberForSplit(abs(int(lcb[i]) - int(ucb[i]))))
        tmp_range = sklearn.utils.shuffle(tmp_range)
        total.append(tmp_range)
    return total, my_min, my_max


def findLSRTenNumberRange(log_10_curve):
    device = "cpu"
    model = Predict10(curve_size=161)
    model.to(device)
    model.load_state_dict(torch.load("LSR/best_model.pth"))
    model.eval()

    solutions = []
    for i in range(0, 1000):
        sampl = np.random.uniform(low=-1, high=1, size=(161,))
        noisy = np.array(log_10_curve + sampl, dtype="float")
        predicted_ten_nums = model(torch.FloatTensor(noisy))
        predicted_ten_nums = [int(10 ** (item - 0.0001)) for item in predicted_ten_nums]
        solutions.append(predicted_ten_nums)
    return pd.DataFrame(solutions)
