
# ══════════════════════════════════════════════════════════════
#  CCA
# ══════════════════════════════════════════════════════════════
from sklearn.cross_decomposition import CCA

def ref_signal(freq):
    t   = np.arange(WINDOW) / FS
    ref = []
    for n in range(1, N_HARMONICS + 1):
        ref.append(np.sin(2 * np.pi * n * freq * t))
        ref.append(np.cos(2 * np.pi * n * freq * t))
    return np.vstack(ref)   # (2·N_HARMONICS, WINDOW)

def classify_window(eeg):
    X      = eeg.T
    scores = {}
    for label, freq in FREQS.items():
        Y = ref_signal(freq).T
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
