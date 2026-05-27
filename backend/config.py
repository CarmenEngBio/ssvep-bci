
#  config.py  —  Global Parameters SSVEP BCI
#  All the system adjustments are placed here.
 
# Selection of the execution MODE
MODE        = "DEMO"   # "DEMO" | "HARDWARE"
SERIAL_PORT = "COM5"   # It matters if MODE = "HARDWARE"
                       # To see the port: Device Manager → Ports → COMx
 
#  Acquisition Hardware
FS         = 250   # Hz — Cyton fs is around 250 Hz
N_CHANNELS = 8     # Fp1 Fp2 C3 C4 P7 P8 O1 O2
 
# Classification Window
# TRADEOFF: more seconds → better accuracy, worst ITR
# Typical literature values: 1–4 s. Could be tried experimentally 1, 2, 3 s.
WINDOW_SEC = 2
WINDOW     = FS * WINDOW_SEC   # number of samples
 
#   Filtering 
BP_LOW       = 6.0    # Hz
BP_HIGH      = 40.0   # Hz
NOTCH_FREQ   = 50.0   # Hz (Power Line Interference EU~50 Hz)
FILTER_ORDER = 4
 
#   Stimuli Frequencies 
# 8–12.5 Hz, separation of 0.5 Hz
# Minimal separation = 1/WINDOW_SEC → with 2 s = 0.5 Hz 
FREQS = {
    "0": 8.0,  "1": 8.5,  "2": 9.0,  "3": 9.5,  "4": 10.0,
    "5": 10.5, "6": 11.0, "7": 11.5, "8": 12.0, "9": 12.5,
}
 
#   CCA 
N_HARMONICS  = 3   # reference harmonics (f, 2f, 3f)
N_COMPONENTS = 1   # canonical components (follows standard SSVEP)
 
#  Confidence threshold
# If there is a maximal correlation < THRESHOLD → prediction not elicited 
# Typical range: 0.2–0.4. Experimentally adjust these values with real-time signal.
CONFIDENCE_THRESHOLD = 0.25
 
#  Temporal Voting 
# Accumulates N_VOTES classifications and elicits the one that wons due to majority votes
# Real latency ≈ N_VOTES × WINDOW_SEC seconds
# Demo: 1 (without vote) | Real use: 2–3
N_VOTES = 2