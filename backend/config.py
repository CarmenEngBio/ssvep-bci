

# Selection of the execution MODE
MODE        = "HARDWARE"   
SERIAL_PORT = "COM5"  
 
#  Acquisition Hardware
FS         = 250   
N_CHANNELS = 8     
 
# Classification Window
WINDOW_SEC = 4
WINDOW     = FS * WINDOW_SEC
 
#   Filtering 
BP_LOW       = 6.0    # Hz
BP_HIGH      = 40.0   # Hz
NOTCH_FREQ   = 50.0   # Hz (Power Line Interference EU~50 Hz)
FILTER_ORDER = 4
 
#   Stimuli Frequencies 
FREQS = {
    "0": 8.0,  "1": 8.5,  "2": 9.0,  "3": 9.5,  "4": 10.0,
    "5": 10.5, "6": 11.0, "7": 11.5, "8": 12.0, "9": 12.5,
}
 
#   CCA 
N_HARMONICS  = 3   
N_COMPONENTS = 1   
 
#  Confidence threshold
#CONFIDENCE_THRESHOLD = 0.25
CONFIDENCE_THRESHOLD = 0.35
 
#  Temporal Voting 
N_VOTES = 2