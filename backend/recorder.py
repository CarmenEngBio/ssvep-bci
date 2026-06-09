# Modulo creado por incompatibilidad de usar la OpenBCI GUI a la vez que est eproyecto para hacer pruebas.

"""
recorder.py — Grabación de EEG en formato OpenBCI GUI
------------------------------------------------------
Guarda los datos crudos (sin filtrar) en .txt compatible con OpenBCI GUI
para análisis posterior en Jupyter Notebook.
 
Uso desde server.py:
    from recorder import EEGRecorder
    recorder = EEGRecorder()
 
WebSocket messages soportados:
    {"type": "start_recording", "label": "celda1"}
    {"type": "stop_recording"}
    {"type": "set_marker", "value": 1}   ← persiste hasta el siguiente set_marker
"""
 
import os
import re
import threading
from datetime import datetime
 
 
class EEGRecorder:
    """
    Grabador thread-safe. Escribe en formato OpenBCI GUI .txt
    con soporte de marcadores persistentes para segmentar condiciones.
    """
 
    _COLUMN_HEADER = (
        "Sample Index, EXG Channel 0, EXG Channel 1, EXG Channel 2, "
        "EXG Channel 3, EXG Channel 4, EXG Channel 5, EXG Channel 6, "
        "EXG Channel 7, Accel Channel 0, Accel Channel 1, Accel Channel 2, "
        "Not Used, Digital Channel 0 (D11), Digital Channel 1 (D12), "
        "Digital Channel 2 (D13), Digital Channel 3 (D17), Not Used, "
        "Digital Channel 4 (D18), Analog Channel 0, Analog Channel 1, "
        "Analog Channel 2, Timestamp, Marker Channel, Timestamp (Formatted)"
    )
 
    def __init__(self, output_dir="recordings", sample_rate=250, n_channels=8):
        self.output_dir = output_dir
        self.sample_rate = sample_rate
        self.n_channels = n_channels
 
        self._lock = threading.Lock()
        self._file = None
        self._recording = False
        self._marker = 0.0        # persiste hasta llamar set_marker() de nuevo
        self._sample_count = 0
        self.current_filename = None
 
    # ------------------------------------------------------------------ #
    #  Control público                                                     #
    # ------------------------------------------------------------------ #
 
    def start(self, label="sesion"):
        """Abre un nuevo fichero y escribe la cabecera."""
        os.makedirs(self.output_dir, exist_ok=True)
        ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"{label}_{ts_str}.txt")
 
        with self._lock:
            if self._recording:
                print("[Recorder] Ya está grabando.")
                return None
 
            # Abrimos con buffer de línea para no perder datos si hay crash
            self._file = open(filename, "w", buffering=1, encoding="utf-8")
            self._file.write("%OpenBCI Raw EXG Data\n")
            self._file.write(f"%Number of channels = {self.n_channels}\n")
            self._file.write(f"%Sample Rate = {self.sample_rate} Hz\n")
            self._file.write("%Board = OpenBCI_GUI$BoardCytonSerial\n")
            self._file.write(self._COLUMN_HEADER + "\n")
 
            self._recording = True
            self._marker = 0.0
            self._sample_count = 0
            self.current_filename = filename
 
        print(f"[Recorder] Grabando en: {filename}")
        return filename
 
    def stop(self):
        """Cierra el fichero y termina la grabación."""
        with self._lock:
            if not self._recording:
                return
            self._recording = False
            if self._file:
                self._file.close()
                self._file = None
 
        print(f"[Recorder] Fichero guardado: {self.current_filename}")
 
    def set_marker(self, value: float):
        """
        Establece el marcador para todas las muestras siguientes.
        Ejemplo: set_marker(1) durante celda 1, set_marker(9) durante celda 9.
        set_marker(0) para limpiar.
        """
        with self._lock:
            self._marker = float(value)
        print(f"[Recorder] Marcador → {value}")
 
    @property
    def is_recording(self) -> bool:
        with self._lock:
            return self._recording
 
    # ------------------------------------------------------------------ #
    #  Escritura de muestras                                               #
    # ------------------------------------------------------------------ #
 
    def write_chunk(self, eeg_uv, timestamps, accel=None):
        """
        Escribe un bloque de muestras en el fichero.
 
        Parámetros
        ----------
        eeg_uv     : np.ndarray  shape (n_channels, n_samples) — µV sin filtrar
        timestamps : np.ndarray  shape (n_samples,)            — Unix epoch en segundos
        accel      : np.ndarray | None  shape (3, n_samples)   — acelerómetro (opcional)
        """
        with self._lock:
            if not self._recording or self._file is None:
                return
 
            n_samples = eeg_uv.shape[1]
            current_marker = self._marker
 
            for i in range(n_samples):
                # Sample Index: rueda de 1 a 255 (igual que el hardware Cyton)
                sample_idx = float((self._sample_count % 255) + 1)
                self._sample_count += 1
 
                eeg_cols = ", ".join(repr(float(v)) for v in eeg_uv[:, i])
 
                if accel is not None:
                    a0 = float(accel[0, i])
                    a1 = float(accel[1, i])
                    a2 = float(accel[2, i])
                else:
                    a0, a1, a2 = 0.0, 0.0, 0.0
 
                ts = float(timestamps[i])
                ts_sci = self._to_java_sci(ts)         # p.ej. 1.7809145720382528E9
                dt = datetime.fromtimestamp(ts)
                ts_fmt = (
                    dt.strftime("%Y-%m-%d %H:%M:%S.")
                    + f"{dt.microsecond // 1000:03d}"
                )
 
                row = (
                    f"{sample_idx}, {eeg_cols}, "
                    f"{a0}, {a1}, {a2}, "
                    f"192.0, "               # Not Used — STOP_BYTE del paquete Cyton
                    f"0.0, 0.0, 0.0, 0.0, " # Digital Ch 0-3
                    f"0.0, "                 # Not Used
                    f"0.0, "                 # Digital Ch 4
                    f"0.0, 0.0, 0.0, "       # Analog Ch 0-2
                    f"{ts_sci}, {current_marker}, {ts_fmt}\n"
                )
                self._file.write(row)
 
    # ------------------------------------------------------------------ #
    #  Utilidades privadas                                                 #
    # ------------------------------------------------------------------ #
 
    @staticmethod
    def _to_java_sci(value: float) -> str:
        """
        Formatea un float en notación científica al estilo Java/OpenBCI GUI:
          Python:  1.7809145720382528E+09
          Java:    1.7809145720382528E9
        """
        s = f"{value:.16E}"
        s = re.sub(r"E\+0*(\d+)", r"E\1", s)
        s = re.sub(r"E-0*(\d+)",  r"E-\1", s)
        return s