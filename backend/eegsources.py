
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