 
import asyncio
import json
 
import numpy as np
import websockets
 
from config        import MODE, WINDOW_SEC, N_HARMONICS, CONFIDENCE_THRESHOLD, N_VOTES, COOLDOWN_SEC
from eegsources    import build_source
# from preprocessing import preprocess, is_noisy
from preprocessing import preprocess
from cca           import classify_window
from voting        import Voter
 
 
#   Handler WebSocket 
async def handler(ws, source):
    
    print(f"✓ Client connected: {ws.remote_address}")
    voter = Voter()
    last_confirm = 0.0
 
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
            #   Acquisition
            raw_eeg              = source.get_window()

            # PARA DEBUGGEAR Y ENCONTRAR EL ORIGEN DEL FALLO
            var_per_channel = np.var(raw_eeg, axis=1)
            print(f"VAR por canal: {np.round(var_per_channel, 1)}")


            #   Signal quality 
            occ_var = float(np.mean(np.var(raw_eeg[-2:], axis=1))) 
            # Aqui es el sitio donde se calcula la varianza estadistica de O1 y O2 en µV². 
            
            # Nuevo filtrado en preprocesamiento para mejorar el clasificador y seleccionar mejor los digitos
            
            if is_noisy(raw_eeg):
                await ws.send(json.dumps({
                    "mode": MODE, 
                    "label": None, 
                    "label_raw": None,
                    "confidence": 0, 
                    "scores": {}, 
                    "signal_quality": round(occ_var, 2)
                }))
                await asyncio.sleep(0.5)
                continue

            in_cooldown = (time.time() - last_confirm) < COOLDOWN_SEC
            
            clean               = preprocess(raw_eeg)
            label, conf, scores = classify_window(clean)
            voted               = voter.vote(label) if not in_cooldown else None

            if voted is not None:
                last_confirm = time.time() # comienza cooldown

            await ws.send(json.dumps({
                "mode":           MODE,
                "label":          voted,
                "label_raw":      label,
                "confidence":     round(conf, 3),
                "scores":         scores,
                "signal_quality": round(occ_var, 2),
                "cooldown": in_cooldown,
            }))
 
            await asyncio.sleep(0.5)
 
    except websockets.exceptions.ConnectionClosed:
        print("✗ Client disconnected.")
 
 
#   Main 
 
async def main():
    print("=" * 50)
    print(f"  SSVEP BCI — Phase 1  |  Mode: {MODE}")
    print(f"  Window: {WINDOW_SEC}s  |  Harmonics: {N_HARMONICS}")
    print(f"  Threshold: {CONFIDENCE_THRESHOLD}  |  Votes: {N_VOTES}")
    print(f"  Cooldown: {COOLDOWN_SEC}s after each number selection")
    print("  Open the index.html file on the browser (just double click the file).")
    print("=" * 50)
 
    source = build_source()
 
    if MODE == "DEMO":
        print("  Simulated EEG — use the selector from the UI to change the desired key!\n")
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