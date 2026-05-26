"""
server.py  —  SSVEP BCI · Fase 1
---------------------------------
Ejecutar:  python server.py
Requiere:  pip install websockets numpy scipy scikit-learn
           pip install brainflow        ← solo si MODE = "HARDWARE"

CAMBIAR MODO AQUÍ ↓
"""

MODE = "DEMO"       # "DEMO" | "HARDWARE"
SERIAL_PORT = "COM5"  # solo importa si MODE = "HARDWARE"
                      # Administrador de dispositivos → Puertos → COMx

# ══════════════════════════════════════════════════════════════
#  PARÁMETROS SSVEP
# ══════════════════════════════════════════════════════════════

FS           = 250      # Hz — Cyton fijo a 250 Hz
N_CHANNELS   = 8       # canales: Fp1 Fp2 C3 C4 P7 P8 O1 O2

# Ventana de clasificación
# TRADEOFF: más segundos → mejor accuracy, peor ITR
# Valores típicos en literatura: 1–4 s. Probar 1, 2, 3 s experimentalmente.
WINDOW_SEC   = 2
WINDOW       = FS * WINDOW_SEC   # muestras

# Filtrado
BP_LOW       = 6.0    # Hz
BP_HIGH      = 40.0   # Hz
NOTCH_FREQ   = 50.0   # Hz (red eléctrica española)
FILTER_ORDER = 4

# Frecuencias de estímulo (8–12.5 Hz, separación 0.5 Hz)
# Separación mínima = 1/WINDOW_SEC → con 2 s = 0.5 Hz justo
FREQS = {
    "0": 8.0,  "1": 8.5,  "2": 9.0,  "3": 9.5,  "4": 10.0,
    "5": 10.5, "6": 11.0, "7": 11.5, "8": 12.0, "9": 12.5,
}

# CCA
N_HARMONICS  = 3      # armónicos en referencia (f, 2f, 3f)
N_COMPONENTS = 1      # componentes canónicas (estándar SSVEP)

# Umbral de confianza
# Si correlación máxima < THRESHOLD → no se emite predicción
# Rango típico: 0.2–0.4. Ajustar experimentalmente con señal real.
CONFIDENCE_THRESHOLD = 0.25

# Votación temporal
# Acumula N_VOTES clasificaciones y emite la ganadora por mayoría
# Latencia real ≈ N_VOTES × WINDOW_SEC segundos
# Demo: 1 (sin votación) | Uso real: 2–3
N_VOTES = 2

# ══════════════════════════════════════════════════════════════
#  FUENTE EEG — DEMO o HARDWARE
# ══════════════════════════════════════════════════════════════

class DemoEEG:
    """
    EEG sintético para desarrollo sin hardware.
    Simula 8 canales con señal SSVEP dominada por la frecuencia
    de la tecla objetivo. O1/O2 (canales 6,7) con mayor amplitud.
    """
    def __init__(self):
        self.target = "5"

    def set_target(self, key):
        if key in FREQS:
            self.target = key

    def get_window(self):
        t    = np.arange(WINDOW) / FS
        freq = FREQS[self.target]
        chs  = []
        for i in range(N_CHANNELS):
            amp = 1.5 if i >= 6 else 0.4   # O1, O2 más amplitud
            sig = (amp * np.sin(2 * np.pi * freq * t)
                 + amp * 0.5 * np.sin(2 * np.pi * 2 * freq * t)
                 + amp * 0.3 * np.sin(2 * np.pi * 3 * freq * t)
                 + 0.5 * np.random.randn(WINDOW))
            chs.append(sig)
        return np.array(chs)   # (N_CHANNELS, WINDOW)


class CytonEEG:
    """Adquisición real desde OpenBCI Cyton vía BrainFlow."""
    def __init__(self):
        from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
        BoardShim.disable_board_logger()
        params = BrainFlowInputParams()
        params.serial_port = SERIAL_PORT
        self.board   = BoardShim(BoardIds.CYTON_BOARD.value, params)
        all_eeg      = BoardShim.get_eeg_channels(BoardIds.CYTON_BOARD.value)
        self.eeg_chs = all_eeg[:N_CHANNELS]
        self.board.prepare_session()
        self.board.start_stream()
        print(f"✓ Cyton conectado en {SERIAL_PORT}")

    def get_window(self):
        data = self.board.get_current_board_data(WINDOW)
        eeg  = np.array([data[ch] for ch in self.eeg_chs])
        if eeg.shape[1] < WINDOW:
            pad = np.zeros((N_CHANNELS, WINDOW - eeg.shape[1]))
            eeg = np.hstack([pad, eeg])
        return eeg[:, -WINDOW:]

    def stop(self):
        self.board.stop_stream()
        self.board.release_session()

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

# ══════════════════════════════════════════════════════════════
#  VOTACIÓN TEMPORAL
# ══════════════════════════════════════════════════════════════
class Voter:
    def __init__(self):
        self._buf = []

    def vote(self, label):
        if label is None:
            self._buf = []
            return None
        self._buf.append(label)
        if len(self._buf) < N_VOTES:
            return None
        winner     = max(set(self._buf), key=self._buf.count)
        self._buf  = []
        return winner

# ══════════════════════════════════════════════════════════════
#  WEBSOCKET
# ══════════════════════════════════════════════════════════════
import asyncio, json
import websockets

async def handler(ws, source):
    print(f"✓ Cliente conectado: {ws.remote_address}")
    voter = Voter()
    try:
        while True:
            # Mensajes entrantes — en DEMO permiten cambiar la tecla simulada
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=0.01)
                msg = json.loads(raw)
                if msg.get("type") == "set_target" and MODE == "DEMO":
                    source.set_target(str(msg["key"]))
            except (asyncio.TimeoutError, json.JSONDecodeError):
                pass

            # Pipeline
            raw_eeg          = source.get_window()
            clean            = preprocess(raw_eeg)
            label, conf, scores = classify_window(clean)
            voted            = voter.vote(label)

            # Calidad de señal: varianza de O1, O2 (µV²)
            occ_var = float(np.mean(np.var(raw_eeg[-2:], axis=1)))

            await ws.send(json.dumps({
                "mode":           MODE,
                "label":          voted,
                "label_raw":      label,
                "confidence":     round(conf, 3),
                "scores":         scores,
                "signal_quality": round(occ_var, 2),
            }))
            await asyncio.sleep(0.5)

    except websockets.exceptions.ConnectionClosed:
        print(f"✗ Cliente desconectado.")

# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
async def main():
    print("=" * 50)
    print(f"  SSVEP BCI — Fase 1  |  Modo: {MODE}")
    print(f"  Ventana: {WINDOW_SEC}s  |  Armónicos: {N_HARMONICS}")
    print(f"  Umbral: {CONFIDENCE_THRESHOLD}  |  Votos: {N_VOTES}")
    print("  Abre index.html en el navegador")
    print("=" * 50)

    if MODE == "DEMO":
        source = DemoEEG()
        print(f"  EEG simulado — usa el selector en la UI para cambiar tecla\n")
    else:
        source = CytonEEG()
        print("  Esperando 2 s para llenar buffer EEG...")
        await asyncio.sleep(2)
        print("  ¡Listo! Fija la mirada en el número deseado.\n")

    try:
        async with websockets.serve(
            lambda ws: handler(ws, source),
            "localhost", 8765
        ):
            await asyncio.Future()
    finally:
        if MODE == "HARDWARE":
            source.stop()
            print("Cyton desconectado correctamente.")

asyncio.run(main())
