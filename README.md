# SSVEP BCI — Phase 1 (OpenBCI Cyton)

Bachelor Thesis · Biomedical Engineering · Carmen Areses Sánchez

---

## Requirements

```
pip install websockets numpy scipy scikit-learn brainflow
```

## Before beginning

1. Connect the **USB Dongle** with the Cyton board
2. Open the **Device manager** → Ports (COM and LPT)
3. Note down the port: usually `COM3`, `COM4`,  `COM5` or similar.
4. Edit the line in `server.py` file:
   ```python
   SERIAL_PORT = "COM3"   # ← write down the port here
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

## Project Files

```
ssvep-fase1/
├── server.py    ← backend: Cyton + preprocessing + CCA + WebSocket
├── index.html   ← UI: flicker + real-time visualization
└── README.md
```
