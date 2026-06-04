 
import asyncio
import json
 
import numpy as np
import websockets
 
from config        import MODE, WINDOW_SEC, N_HARMONICS, CONFIDENCE_THRESHOLD, N_VOTES
from eegsources    import build_source
from preprocessing import preprocess, is_noisy
from cca           import classify_window
from voting        import Voter
 
 
#   Handler WebSocket 
async def handler(ws, source):
    
    print(f"✓ Client connected: {ws.remote_address}")
    voter = Voter()
 
    try:
        while True:
            #   Incoming Messages
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=0.01) # el timeout es suficiente o debe ser más grande?
                msg = json.loads(raw) #parsear los datos a JSON es buena estrategia?creo q si son: scores, confianza, eeg signal
                if msg.get("type") == "set_target" and MODE == "DEMO":
                    source.set_target(str(msg["key"]))
            except (asyncio.TimeoutError, json.JSONDecodeError):
                pass
 
            #   Classification Pipeline
            raw_eeg              = source.get_window()
            
            #   Signal quality 
            occ_var = float(np.mean(np.var(raw_eeg[-2:], axis=1)))
            
            # Nuevo filtrado en preprocesamiento para mejorar el clasificador y seleccionar mejor los digitos
            """
            if is_noisy(raw_eeg):
                await ws.send(json.dumps({
                    "mode": MODE, "label": None, "label_raw": None,
                    "confidence": 0, "scores": {}, "signal_quality": round(float(np.mean(np.var(raw_eeg[-2:], axis=1))), 2)
                }))
                await asyncio.sleep(0.5)
                continue
            """
 
            clean               = preprocess(raw_eeg)
            label, conf, scores = classify_window(clean)
            voted               = voter.vote(label)
 
            await ws.send(json.dumps({
                "mode":           MODE,
                "label":          voted,
                "label_raw":      label,
                "confidence":     round(conf, 3),
                "scores":         scores,
                "signal_quality": round(occ_var, 2),
            }))
 
            await asyncio.sleep(0.5)
 
    except websockets.exceptions.ConnectionClosed:
        print("✗ Client disconnected.")
 
 
#    Main 
 
async def main():
    print("=" * 50)
    print(f"  SSVEP BCI — Phase 1  |  Mode: {MODE}")
    print(f"  Window: {WINDOW_SEC}s  |  Harmonics: {N_HARMONICS}")
    print(f"  Threshold: {CONFIDENCE_THRESHOLD}  |  Votes: {N_VOTES}")
    print("  Open the index.html file on the browser (just double click the file).")
    print("=" * 50)
 
    source = build_source()
 
    if MODE == "DEMO":
        print("  Simulator of EEG — use the selector from the UI to change the desired key!\n")
    else:
        print("  Waiting 2 s to fill the EEG buffer...")
        await asyncio.sleep(2)
        print("  Ready! Focus your attention on the desired number.\n")
 
    try:
        async with websockets.serve(
            lambda ws: handler(ws, source),
            "localhost", 8765
        ):
            await asyncio.Future()
    finally:
        if MODE == "HARDWARE":
            source.stop()
            print("Cyton correctly disconnected.")
 
 
asyncio.run(main())