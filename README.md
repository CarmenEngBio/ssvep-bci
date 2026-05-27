# SSVEP BCI — Phase 1 (OpenBCI Cyton)

Bachelor Thesis · Biomedical Engineering · Carmen Areses Sánchez

---

## Requirements

```
pip install websockets numpy scipy scikit-learn brainflow
```

## Before begin
 
1. Connect the **USB Dongle** with the Cyton board.
2. Open the **Device Manager** → Ports (COM y LPT)
3. Note down the port: usually `COM3`,`COM4`, `COM5` or similar.
4. Edit `backend/config.py`:
   ```python
   MODE        = "HARDWARE"   # change from "DEMO" to "HARDWARE"
   SERIAL_PORT = "COM5"       # write down your port linked to the OpenBCI equipment 
   ```
   ```

## Running the program

```bash
python server.py
```

Then open the `index.html` file in your browser (double-click).

## Electrodes placement arrangement

| Channel | Electrode | Region |
|-------------|-----------|--------|
| CH1 | Fp1 | Frontal |
| CH2 | Fp2 | Frontal |
| CH3 | C3  | Central |
| CH4 | C4  | Central |
| CH5 | P7  | Parieto-occipital |
| CH6 | P8  | Parieto-occipital |
| **CH7** | **O1** | **Occipital ← most important** |
| **CH8** | **O2** | **Occipital ← most important** |

## Frequencies associated per channel 

| Tecla | Hz  |
|-------|-----|
| 0     | 8.0 |
| 1     | 8.5 |
| 2     | 9.0 |
| 3     | 9.5 |
| 4     | 10.0 |
| 5     | 10.5 |
| 6     | 11.0 |
| 7     | 11.5 |
| 8     | 12.0 |
| 9     | 12.5 |

## Project Files (initial sketch)

```
ssvep-fase1/
├── server.py    ← backend: Cyton + preprocessing + CCA + WebSocket
├── index.html   ← UI: flicker + real-time visualization
└── README.md
```

## Project Ideal Architecture & Structure
 
```
ssvep-fase1/
├── backend/
│   ├── config.py          ← ★ todos los parámetros aquí
│   ├── eegsources.py      ← DemoEEG + CytonEEG
│   ├── preprocessing.py   ← bandpass · notch · CAR
│   ├── cca.py             ← señal de referencia + clasificador CCA
│   ├── voting.py          ← votación temporal por mayoría
│   └── server.py          ← WebSocket + main (punto de entrada)
│
└── frontend/
    ├── index.html
    └── assets/
        ├── css/
        │   └── styles.css
        └── js/
            ├── app.js         ← punto de entrada (importa los demás)
            ├── flicker.js     ← motor de parpadeo SSVEP (rAF)
            ├── websocket.js   ← conexión WebSocket + reconexión
            └── ui.js          ← actualización del DOM
```
 
### Modules Functionalities
 
| Archivo | Responsabilidad |
|---|---|
| `config.py` | Parámetros del sistema (FS, ventana, frecuencias, umbrales…) |
| `eegsources.py` | Abstracción de fuente EEG (demo o hardware real) |
| `preprocessing.py` | Filtros: paso-banda, notch 50 Hz, CAR |
| `cca.py` | Señal de referencia sinusoidal + clasificación por CCA |
| `voting.py` | Votación por mayoría para reducir falsos positivos |
| `server.py` | Handler WebSocket y arranque del servidor |
| `flicker.js` | Parpadeo de teclas a frecuencias SSVEP exactas |
| `websocket.js` | Conexión/reconexión WebSocket, envío de tecla simulada |
| `ui.js` | Toda la manipulación del DOM (barras, scores, buffer…) |
| `app.js` | Punto de entrada: importa y arranca flicker + websocket |