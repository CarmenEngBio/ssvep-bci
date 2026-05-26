
# ══════════════════════════════════════════════════════════════
#  PREPROCESADO
# ══════════════════════════════════════════════════════════════
import numpy as np
from scipy.signal import butter, filtfilt

def _butter(low, high, btype):
    nyq  = FS / 2
    b, a = butter(FILTER_ORDER, [low / nyq, high / nyq], btype=btype)
    return b, a

def bandpass(x):
    b, a = _butter(BP_LOW, BP_HIGH, "band")
    return filtfilt(b, a, x)

def notch(x):
    b, a = _butter(NOTCH_FREQ - 1, NOTCH_FREQ + 1, "bandstop")
    return filtfilt(b, a, x)

def car(eeg):
    return eeg - eeg.mean(axis=0, keepdims=True)

def preprocess(eeg):
    filtered = np.array([notch(bandpass(ch)) for ch in eeg])
    return car(filtered)