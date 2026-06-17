
# TO DO: research of FBCCA ALGORITHM IMPLEMENTATION OR ATTEMPTING WITH THE PSD ANALYSIS INSTEAD
import numpy as np
from sklearn.cross_decomposition import CCA
 
from config import FS, WINDOW, FREQS, N_HARMONICS, N_COMPONENTS, CONFIDENCE_THRESHOLD
 
 
# Reference Signal
# Construye la matriz de referencia sinusoidal para una frecuencia.
def ref_signal(freq: float) -> np.ndarray:
    t   = np.arange(WINDOW) / FS
    ref = []
    for n in range(1, N_HARMONICS + 1):
        ref.append(np.sin(2 * np.pi * n * freq * t))
        ref.append(np.cos(2 * np.pi * n * freq * t))
    return np.vstack(ref)
 
 
#  Classification per window
# Clasifica una ventana EEG con CCA comparando todas las frecuencias SSVEP
def classify_window(eeg: np.ndarray) -> tuple[str | None, float, dict]:
    # X      = eeg.T   # (WINDOW, N_CHANNELS)
    # CCA evaluando todos los canales disponibles es más concluyente que usando solo 2 canales, donde la operacion es peor
    # Este enfoque es estándar en la literatura: Chen et al. 2015 y Nakanishi et al. 2018.
    X = eeg[-4:].T  # antes: eeg.T (8 canales) → ahora solo P7, P8, O1 y O2 (parietales + occipitales) para ver si clasifica mejor la señal
    scores = {}
 
    for label, freq in FREQS.items():
        Y = ref_signal(freq).T   # (WINDOW, 2·N_HARMONICS)
        try:
            cca = CCA(n_components=N_COMPONENTS, max_iter=1000)
            cca.fit(X, Y)
            U, V = cca.transform(X, Y)
            r    = float(np.corrcoef(U.T, V.T)[0, 1])
            scores[label] = round(r if np.isfinite(r) else 0.0, 3)
        except Exception:
            scores[label] = 0.0
 
    top   = max(scores, key=scores.get)
    conf  = scores[top]
    label = top if conf >= CONFIDENCE_THRESHOLD else None
 
    return label, conf, scores

    # label representa la prediccion respecto al intervalo de confianza
    # conf se refiere a la correlacion canonica maxima [0, 1]
    # scores se refiere al diccionario tecla-->correlacion para todas las frecuencias
