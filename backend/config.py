

# Selection of the execution MODE
MODE        = "HARDWARE" 
# MODE        = "DEMO"   
SERIAL_PORT = "COM5"  
 
#  Acquisition Hardware
FS         = 250   
N_CHANNELS = 8     
 
# Classification Window
WINDOW_SEC = 4
WINDOW     = FS * WINDOW_SEC

# Umbrales de limpieza - Debido a la introducción de ruído en la señal de entrada por usar electrodos secos 
# NOISE_THRESHOLD_VAR = 50000  # µV² 
# NOISE_THRESHOLD_ABS = 1000    # µV
NOISE_THRESHOLD_VAR = 150000   # µV² por encima del reposo (~50k)
NOISE_THRESHOLD_ABS = 1500     # µV por encima de picos habituales
 
#   Filtering 
BP_LOW       = 6.0    # Hz
BP_HIGH      = 40.0   # Hz
NOTCH_FREQ   = 50.0   # Hz (Power Line Interference EU~50 Hz)
FILTER_ORDER = 4

#  Cooldown despues de confirmar la seleccion
COOLDOWN_SEC = 2.0 
#segundos de espera despues de q un digito se ha confirmado antes de aceptar un nuevo input
#previene de falsos positivos entre selecicones de digitos consecutivas

#   Stimuli Frequencies 
FREQS = {
    "0": 8.0,  "1": 8.5,  "2": 9.0,  "3": 9.5,  "4": 10.0,
    "5": 10.5, "6": 11.0, "7": 11.5, "8": 12.0, "9": 12.5,
}
 
#   CCA 
N_HARMONICS  = 3   
N_COMPONENTS = 1   
 
#  Confidence threshold
#CONFIDENCE_THRESHOLD = 0.25 #El problema no era esto, sino que se ha acabado la batería de la placa.
CONFIDENCE_THRESHOLD = 0.35
 
#  Temporal Voting 
N_VOTES = 2