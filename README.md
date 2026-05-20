# SSVEP BCI — Fase 1 (OpenBCI Cyton)

TFG · Biomedical Engineering · CEU San Pablo · Carmen Areses Sánchez

---

## Requisitos

```
pip install websockets numpy scipy scikit-learn brainflow
```

## Antes de arrancar

1. Conecta el **dongle USB** del Cyton
2. Abre el **Administrador de dispositivos** → Puertos (COM y LPT)
3. Anota el puerto: `COM3`, `COM4`, etc.
4. Edita la línea en `server.py`:
   ```python
   SERIAL_PORT = "COM3"   # ← pon tu puerto aquí
   ```

## Arrancar

```bash
python server.py
```

Luego abre `index.html` en el navegador (doble clic).

## Colocación de electrodos recomendada

| Canal Cyton | Electrodo | Región |
|-------------|-----------|--------|
| CH1 | Fp1 | Frontal |
| CH2 | Fp2 | Frontal |
| CH3 | C3  | Central |
| CH4 | C4  | Central |
| CH5 | P7  | Parieto-occipital |
| CH6 | P8  | Parieto-occipital |
| **CH7** | **O1** | **Occipital ← más importante** |
| **CH8** | **O2** | **Occipital ← más importante** |

## Frecuencias por tecla

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

## Archivos

```
ssvep-fase1/
├── server.py    ← backend: Cyton + preprocesado + CCA + WebSocket
├── index.html   ← UI: flicker + visualización en tiempo real
└── README.md
```
