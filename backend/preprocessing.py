
 
import numpy as np
from scipy.signal import butter, filtfilt
 
from config import FS, BP_LOW, BP_HIGH, NOTCH_FREQ, FILTER_ORDER
 
 
#  Filters Design 
def _butter_coeffs(low: float, high: float, btype: str):
    nyq  = FS / 2
    b, a = butter(FILTER_ORDER, [low / nyq, high / nyq], btype=btype)
    return b, a
 
 
#  Individual Filters 
def bandpass(signal: np.ndarray) -> np.ndarray:
    b, a = _butter_coeffs(BP_LOW, BP_HIGH, "band")
    return filtfilt(b, a, signal)
 
 
def notch(signal: np.ndarray) -> np.ndarray:
    b, a = _butter_coeffs(NOTCH_FREQ - 1, NOTCH_FREQ + 1, "bandstop")
    return filtfilt(b, a, signal)
 
 
def car(eeg: np.ndarray) -> np.ndarray:
    return eeg - eeg.mean(axis=0, keepdims=True)
 
 
#  Full Pipeline
def preprocess(eeg: np.ndarray) -> np.ndarray:
    filtered = np.array([notch(bandpass(ch)) for ch in eeg])
    return car(filtered)