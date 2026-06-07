
"""
 Como la señal recogida contiene mucho rúido por tener un valor en µV² muy grande ~ 26111, se podrían implementar estos 
 métodos ligados a Brainflow que sirven de filtrado, para eliminar ventanas muy ruidosas:
 
 from brainflow.data_filter import DataFilter, FilterTypes, NoiseTypes

 for channel in eeg_channels:
    
    DataFilter.perform_bandpass(data[channel], sampling_rate, 
                                 1.0, 40.0,   # frecuencia baja, frecuencia alta
                                 4,            # orden del filtro
                                 FilterTypes.BUTTERWORTH, 0)
    
    DataFilter.remove_environmental_noise(data[channel], sampling_rate, 
                                           NoiseTypes.FIFTY) 
"""
 
import numpy as np
from scipy.signal import butter, filtfilt
 
from config import FS, BP_LOW, BP_HIGH, NOTCH_FREQ, FILTER_ORDER, NOISE_THRESHOLD_VAR, NOISE_THRESHOLD_ABS
 
# Existen librerías de BrainFlow para el filtrado notch y pasabanda, pero si se introducen y en el futuro se usa otro tipo
# de adquisicion no sería modular y escalable. Ademas, no se podria ejecutar correctamente el modo DEMO, por ello es mejor
# mantener la limpieza y filtrado en scipy que es más general que adaptarlo a las funciones de BrainFlow.

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

# Se añade función de filtrado de ruído para recoger una señal más nítida
# Rechaza las ventanas con ruido excesivo en los 8 canales, consistente con CCA
# Valor normal en EEG: 10-100 µV² — electrodos secos pueden superar 500 µV²

def is_noisy(eeg):
    # Criterio 1: varianza en todos canales por si se excede umbral
    # filtra amplitud de toda la ventana
    mean_var = float(np.mean(np.var(eeg, axis=1)))
    if mean_var > NOISE_THRESHOLD_VAR:
        return True
    # Criterio 2: muestra en un canal que excede umbral absoluto
    # filtra picos de ruido puntuales
    if np.any(np.abs(eeg) > NOISE_THRESHOLD_ABS):
        return True
    return False
 