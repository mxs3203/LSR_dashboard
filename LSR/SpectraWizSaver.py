import time

import pyautogui
import re

def get_spectra_window():
    windows = pyautogui.getAllWindows()
    spectra = None
    for w in windows:
        if w.title == "SpectraWiz  Spectrometer OS v5.33 (c) 2014    www.StellarNet.us  ":
            spectra = w
    spectra.activate()
    return spectra

def save_curve(cnt, time_between = 0.001):
    spectra_window = get_spectra_window()
    pyautogui.keyDown("altleft")
    time.sleep(time_between)
    pyautogui.press("f") # file
    time.sleep(time_between)
    pyautogui.press("s") # save
    time.sleep(time_between)
    pyautogui.press("s") # sample
    pyautogui.keyUp('altleft') # release
    time.sleep(time_between)
    pyautogui.typewrite(cnt)
    time.sleep(time_between)
    pyautogui.press("enter")
    time.sleep(time_between)
    pyautogui.keyDown("altleft")
    pyautogui.press("y")
    pyautogui.keyUp('altleft')
    time.sleep(time_between)