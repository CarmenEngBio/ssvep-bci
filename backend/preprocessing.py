

#  preprocessing.py  —  Preprocessing EEG Chain 
#
#  Pipeline: bandpass → notch → CAR (Common Average Reference)
#  All the parameters established came from the config.py file.

 
import numpy as np
from scipy.signal import butter, filtfilt
 
from config import FS, BP_LOW, BP_HIGH, NOTCH_FREQ, FILTER_ORDER
 
 
#   Filters Design 
 
def _butter_coeffs(low: float, high: float, btype: str):
    """
    Calculates the Butterworth coefficients normalized at the Nyquist frequency. 
    
    Parameters --> low, high : Hz limitation
                   btype     : 'band' | 'bandstop'
    """
    nyq  = FS / 2
    b, a = butter(FILTER_ORDER, [low / nyq, high / nyq], btype=btype)
    return b, a
 
 
#   Individual Filters 
 
def bandpass(signal: np.ndarray) -> np.ndarray:
    """
    Bandpass filter [BP_LOW – BP_HIGH] Hz.
    Erases DC offset and high frequency artifacts.
    signal: array 1-D (one window of one channel)
    """
    b, a = _butter_coeffs(BP_LOW, BP_HIGH, "band")
    return filtfilt(b, a, signal)
 
 
def notch(signal: np.ndarray) -> np.ndarray:
    """
    Notch filter ±1 Hz around the NOTCH_FREQ (50 Hz).
    Erases the power line interference. 
    signal: array 1-D (one window of one channel)
    """
    b, a = _butter_coeffs(NOTCH_FREQ - 1, NOTCH_FREQ + 1, "bandstop")
    return filtfilt(b, a, signal)
 
 
def car(eeg: np.ndarray) -> np.ndarray:
    """
    Common Average Reference: substracts the spatial average to each sample.
    Reduces common artifacts to all the electrodes (movement, EMG).
    eeg: ndarray (N_CHANNELS, WINDOW)
    """
    return eeg - eeg.mean(axis=0, keepdims=True)
 
 
#   Full Pipeline
 
def preprocess(eeg: np.ndarray) -> np.ndarray:
    """
    Applies the full chain: bandpass → notch → CAR.
    eeg: ndarray (N_CHANNELS, WINDOW)
    Returns: ndarray (N_CHANNELS, WINDOW) filtered
    """
    filtered = np.array([notch(bandpass(ch)) for ch in eeg])
    return car(filtered)