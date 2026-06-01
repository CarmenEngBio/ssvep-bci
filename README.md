# SSVEP BCI — Phase 1 (OpenBCI Cyton)

Bachelor Thesis · Biomedical Engineering · Carmen Areses Sánchez

---

## Requirements

```
pip install websockets numpy scipy scikit-learn brainflow
```

## Before beginning
 
1. Connect the **USB Dongle** with the Cyton board.
2. Open the **Device Manager** → Ports (COM y LPT)
3. Note down the port: usually `COM3`,`COM4`, `COM5` or similar.
4. Edit `backend/config.py`:
   ```python
   MODE        = "HARDWARE"   # change from "DEMO" to "HARDWARE"
   SERIAL_PORT = "COM5"       # write down your port linked to the OpenBCI equipment 
   ```

## Running the program

```bash
python server.py
```

Then open the `index.html` file in your browser (double-click).

## Electrodes placement

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

| Key | Hz  |
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
│   ├── config.py          ← parameters are declared here
│   ├── eegsources.py      ← DemoEEG + CytonEEG
│   ├── preprocessing.py   ← bandpass + notch + CAR
│   ├── cca.py             ← reference signal + CCA classifier
│   ├── voting.py          ← temporal majority voting algorithm
│   └── server.py          ← WebSocket + main (entry endpoint)
│
└── frontend/
    ├── index.html
    └── assets/
        ├── css/
        │   └── styles.css (website visualization)
        └── js/
            ├── app.js         ← entry endpoint
            ├── flicker.js     ← flickering SSVEP engine (rAF)
            ├── websocket.js   ← WebSocket connection + re-connection
            └── ui.js          ← update of DOM
```
 
## Modules Functionalities
 
| File | Functionality |
|---|---|
| `config.py` | System paremeters (fs, window, frequencies, thresholds, …) |
| `eegsources.py` | Abstraction of EGG source (DEMO or real HARDWARE) |
| `preprocessing.py` | Filters: bandpass, notch 50 Hz, CAR |
| `cca.py` | Sinusoidal reference signal + CCA classification |
| `voting.py` | Majority voting procedure to reduce false positives |
| `server.py` | Handler WebSocket and launch of server |
| `flicker.js` | Key flickering at SSVEP exact frequencies |
| `websocket.js` | Connection/re-connection of the WebSocket / simulated sent key |
| `ui.js` | The DOM management and manipulation (bars, scores, buffer, …) |
| `app.js` | Entry main point that launches the flickering and the websocket communication |