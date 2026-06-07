#psd.py - SSVEP Clasificador alternativo basado en Potrncia de Densidad 
# Spectral (PSD) combinada con filtrado Welch
# Este algoritmo es mas robusto que el CCA si la SNR es baja, esto mismo
# es lo que ocurre con electrodos secos
# Para introducir este modulo en el servidor tan solo hay que cambiar:
# Reemplazar: from cca import classify_window
#             from psd import classify_window

import numpy as np
from scipy.signal import welch

from config import FS, WINDOW, FREQS, N_HARMONICS, CONFIDENCE_THRESHOLD

def _psd(signal):
    # Usa Welch para la PSD, la formula nperseg balancea la resolucion frecuencial y la varianza 
    freqs, power = welch(signal, fs=FS, nperseg=WINDOW // 2)
    return freqs, power

def _freq_index(freqs, target_hz, tolerance=0.15):
    # Retorna el indice de los valores cercanos a target_hz respecto a una tolerancia
    idx = np.argmin(np.abs(freqs - target_hz))
    if np.abs(freqs[idx] - target_hz) > tolerance:
        return None
    return idx

def _score_for_freq(freqs, power, freq):
    # Suma normalizada respecto a la potencia en f y sus armonicos
    total = np.sum(power) + 1e-10 #evita division por cero
    score = 0.0
    for n in range(1, N_HARMONICS + 1):
        idx = _freq_index(freqs, n * freq)
        if idx is not None:
            score += power[idx] / total
    return score

def classify_window(eeg):
    # Classifica una ventana EEG usando Welch y PSD 
    # Parametros: eeg: ndarray (N_CHANNELS, WINDOW), preprocesado
    # Retorna: label, conf y scores, igual que el CCA.

    f, p = _psd(eeg) # p: (N_CHANNELS, N_FREQS)
    
    freqs = f
    power = np.mean(p, axis=0)

    scores = {}
    for label, freq in FREQS.items():
        scores[label] = round(_score_for_freq(freqs, power, freq), 4)

    top = max(scores, key=scores.get)
    conf = scores[top]
    label = top if conf >= CONFIDENCE_THRESHOLD else None

    return label, conf, scores