
#  cca.py  —  SSVEP Classifier based on CCA
#
#  Canonical Correlation Analysis (CCA):
#  For each candidate frequency, it it built a sinusoidal reference signal 
#  with N harmonics and it is calculated the canonical with the EEG window. 
#  The frequency with mayor correlation will be the prediction.
 
import numpy as np
from sklearn.cross_decomposition import CCA
 
from config import FS, WINDOW, FREQS, N_HARMONICS, N_COMPONENTS, CONFIDENCE_THRESHOLD
 
 
# Reference Signal
 
def ref_signal(freq: float) -> np.ndarray:
    """
    Builds the sinusoidal reference matrix for one frequency.
    Includes N_HARMONICS harmonics (sine + cosine per harmonic).
 
    Parameters --> freq : fundamental frequency in Hz
 
    Returns --> ndarray with the form (2·N_HARMONICS, WINDOW)
    """
    t   = np.arange(WINDOW) / FS
    ref = []
    for n in range(1, N_HARMONICS + 1):
        ref.append(np.sin(2 * np.pi * n * freq * t))
        ref.append(np.cos(2 * np.pi * n * freq * t))
    return np.vstack(ref)
 
 
#   Classification per window
 
def classify_window(eeg: np.ndarray) -> tuple[str | None, float, dict]:
    """
    Classifies one EEG window with CCA against all the SSVEP frequencies.
 
    Parameters --> eeg : ndarray (N_CHANNELS, WINDOW) already preprocess
 
    Returns --> label  : predicted key (str) or None if conf < CONFIDENCE_THRESHOLD
                conf   : maximal canonical correlation [0, 1]
                scores : dict {key: correlation} for all the frequencies
    """
    X      = eeg.T   # (WINDOW, N_CHANNELS)
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
