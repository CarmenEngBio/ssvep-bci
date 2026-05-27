
#  eegsources.py  —  EEG Signal Sources Here
#  Contains DemoEEG (fake signal) and CytonEEG (real hardware).
#  server.py instances one or the other depending on config.MODE.
 
import numpy as np
from config import MODE, SERIAL_PORT, FS, N_CHANNELS, WINDOW, FREQS
 
 
class DemoEEG:
    """
    Fake EEG for code development without hardware.
    Simulates 8 channels with SSVEP signal dominated by frequency
    of the desired ideal key. O1/O2 channels with wider amplitudes,
    same as it will occur with real occipital electrodes.
    """
 
    def __init__(self):
        self.target = "5"   # key selected by default
 
    def set_target(self, key: str) -> None:
        """Changes the dominant frequency from the simulated signal."""
        if key in FREQS:
            self.target = key
 
    def get_window(self) -> np.ndarray:
        """
        Returns a fake EEG window in ndarray format (N_CHANNELS, WINDOW)
        """
        t    = np.arange(WINDOW) / FS
        freq = FREQS[self.target]
        chs  = []
 
        for i in range(N_CHANNELS):
            amp = 1.5 if i >= 6 else 0.4   # O1, O2 highest amplitudes
            sig = (
                amp       * np.sin(2 * np.pi *     freq * t)
              + amp * 0.5 * np.sin(2 * np.pi * 2 * freq * t)
              + amp * 0.3 * np.sin(2 * np.pi * 3 * freq * t)
              + 0.5       * np.random.randn(WINDOW)
            )
            chs.append(sig)
 
        return np.array(chs)   # (N_CHANNELS, WINDOW)
 
 
class CytonEEG:
    """
    Real OpenBCI Cython acquisition via BrainFlow.
    Requires: pip install brainflow
    """
 
    def __init__(self):
        from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
 
        BoardShim.disable_board_logger()
        params             = BrainFlowInputParams()
        params.serial_port = SERIAL_PORT
 
        self.board   = BoardShim(BoardIds.CYTON_BOARD.value, params)
        all_eeg      = BoardShim.get_eeg_channels(BoardIds.CYTON_BOARD.value)
        self.eeg_chs = all_eeg[:N_CHANNELS]
 
        self.board.prepare_session()
        self.board.start_stream()
        print(f"✓ Connected Cyton at {SERIAL_PORT}")
 
    def get_window(self) -> np.ndarray:
        """
        Read the last buffer window from BrainFlow.
        Returns: ndarray with form (N_CHANNELS, WINDOW)
        """
        data = self.board.get_current_board_data(WINDOW)
        eeg  = np.array([data[ch] for ch in self.eeg_chs])
 
        if eeg.shape[1] < WINDOW:
            pad = np.zeros((N_CHANNELS, WINDOW - eeg.shape[1]))
            eeg = np.hstack([pad, eeg])
 
        return eeg[:, -WINDOW:]
 
    def stop(self) -> None:
        """Releases/frees the hardware correctly when exit."""
        self.board.stop_stream()
        self.board.release_session()
 
 
def build_source():
    """
    Factory: returns DemoEEG or CytonEEG depending on config.MODE.
    May be useful info to use on server.py in order not to import classes by hand.
    """
    if MODE == "DEMO":
        return DemoEEG()
    return CytonEEG()

