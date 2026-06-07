
 
import numpy as np
from config import MODE, SERIAL_PORT, FS, N_CHANNELS, WINDOW, FREQS
 
 
class DemoEEG:
 
    def __init__(self):
        self.target = "5"   # key selected by default
 
    def set_target(self, key: str) -> None:
        if key in FREQS:
            self.target = key
 
    def get_window(self) -> np.ndarray:
        t    = np.arange(WINDOW) / FS
        freq = FREQS[self.target]
        chs  = []
 
        for i in range(N_CHANNELS):
            amp = 1.5 if i >= 6 else 0.4   # O1, O2 highest amplitudes --> porque estos valores?
            sig = (
                amp       * np.sin(2 * np.pi *     freq * t)
              + amp * 0.5 * np.sin(2 * np.pi * 2 * freq * t)
              + amp * 0.3 * np.sin(2 * np.pi * 3 * freq * t)
              + 0.5       * np.random.randn(WINDOW)
            )
            chs.append(sig)
 
        return np.array(chs) 
 
 
class CytonEEG:
 
    def __init__(self):
        from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
 
        BoardShim.disable_board_logger()
        params             = BrainFlowInputParams()
        params.serial_port = SERIAL_PORT
 
        self.board   = BoardShim(BoardIds.CYTON_BOARD.value, params)
        all_eeg      = BoardShim.get_eeg_channels(BoardIds.CYTON_BOARD.value)
        self.eeg_chs = all_eeg[:N_CHANNELS]
        #Este comando es típico de BrainFlow --> investigar porqué no se implementa
        #sampling_rate = BoardShim.get_sampling_rate(BoardIds.CYTON_BOARD)  # devuelve 250
 
        self.board.prepare_session()
        self.board.start_stream()
        print(f"✓ Connected Cyton at {SERIAL_PORT}")
 
    def get_window(self) -> np.ndarray:
        
        data = self.board.get_current_board_data(WINDOW) # creo que es porque aqui ya se incluye la FS
        # A traves de esa funcion propia de BrainFlow internammente se realiza la conversion ADC a µV² 
        eeg  = np.array([data[ch] for ch in self.eeg_chs])
 
        if eeg.shape[1] < WINDOW:
            pad = np.zeros((N_CHANNELS, WINDOW - eeg.shape[1]))
            eeg = np.hstack([pad, eeg])
 
        return eeg[:, -WINDOW:]
 
    def stop(self) -> None:
        self.board.stop_stream()
        self.board.release_session()
 
 
def build_source():
    if MODE == "DEMO":
        return DemoEEG()
    return CytonEEG()

