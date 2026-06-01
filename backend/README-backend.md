 # Backend Manual - Server Endpoint explanation

 Server Module Explanation —  SSVEP BCI · Phase 1

 ---

 ## Requirements

 **Python** language **must** be **installed** to run the server:

 ```
 pip install websockets numpy scipy scikit-learn brainflow
 ```
---

 # Server.py

 It is the entry point of the backend. It just contains:

  - The **WebSocket handler**: it receives the messages from the navigator and sends the predictions.
  - The **main()** function launches the server. 
 
 All the specified parameters are declared and initialised at the `config.py` file.
 The signal logics is split among the different specialised modules.
 
 For this module: 
 1. Execute:  `python server.py`.
 2. Requires: 
    ```
    pip install websockets numpy scipy scikit-learn
    pip install brainflow   ← if MODE = "HARDWARE"
    ```

 ## Handler WebSocket

 Manages the **connection** with a **client** (website / browser ).
 
 - It listens to incoming messages to change the simulated key if the `mode = DEMO`. 
 - Each 0.5 s it applies the **window** of the signal, then it **preprocess** the signal, it applies the **classification** 
   process, then the **voting** procedure and lasting the data is **sent**.
 - It includes the **quality signal** metrics through **variance** levels (µV²) at electrodes **O1** / **O2**.

---

# Config.py 

 Where the system **global parameters** of the SSVEP BCI are placed.

 For this module:
 1. Selection of the execution MODE:
    ```python
    MODE        = "HARDWARE"   # "DEMO" | "HARDWARE"
    SERIAL_PORT = "COM5"   # It matters if MODE = "HARDWARE" # To see the port: Device Manager → Ports → COMx
    ```
 2. Acquisition Hardware
 ```python
    FS         = 250   # Cyton fs is around 250 Hz
    N_CHANNELS = 8     # Fp1 Fp2 C3 C4 P7 P8 O1 O2
 ```
 3. Classification Window
 - **TRADEOFF**: the more seconds, the better is the accuracy and worst the ITR
 - The typical literature values are between 1–4 s.
 ```python
    WINDOW_SEC = 2
    WINDOW     = FS * WINDOW_SEC   # number of samples
 ```
 4. Filtering:
 ```python
    BP_LOW       = 6.0    # Hz
    BP_HIGH      = 40.0   # Hz
    NOTCH_FREQ   = 50.0   # Hz (Power Line Interference EU~50 Hz)
    FILTER_ORDER = 4
 ```
 5. Stimuli Frequencies 
 - They oscillate within 8–12.5 Hz, with a separation of 0.5 Hz
 - Also the minimal separation is `= 1/WINDOW_SEC` → with 2 s = 0.5 Hz 

 6. CCA:
 ```python
    N_HARMONICS  = 3   # number of reference harmonics (f, 2f, 3f)
    N_COMPONENTS = 1   # number of canonical components (follows standard SSVEP)
 ```
 7. Confidence threshold
 - If there is a maximal correlation < THRESHOLD → the prediction is not elicited. 
 - The typical range is: 0.2–0.4. Experimentally it is adjusted this value with the real-time signal used.
 ```python
 CONFIDENCE_THRESHOLD = 0.25
 ```
 8. Temporal Voting 
 - It accumulates N_VOTES classifications and elicits the one that wons due to majority votes
 - The real latency ≈ N_VOTES × WINDOW_SEC seconds.
 - With `DEMO`: 1 (without vote), but the real use is between 2–3.

---

 # Eegsources.py 
 The EEG signal source is placed here. It contains the **DemoEEG** (fakes the signal) and the **CytonEEG** (real hardware).
 Then the `server.py` instances one or the other depending on the `config.MODE`. 

 ## DemoEEG

 - Fakes the EEG for code development without hardware.
 - Simulates 8 channels with SSVEP signal dominated by the frequency of the desired ideal key. O1/O2 channels are the ones with  wider amplitudes,same as it will occur with real occipital electrodes.

 On this module fucntion:
 1. `set_target(self, key: str)` changes the dominant frequency from the simulated signal.
 2. `get_window(self)` returns a fake EEG window in ndarray format ``(N_CHANNELS, WINDOW)`.

 ## CythonEEG
 - It is the real OpenBCI Cython acquisition via BrainFlow.
 - It requires: 
 ```
 pip install brainflow
 ```
 On this module function:
 1. `get_window(self)`, reads the last buffer window from BrainFlow. It returns a ndarray with the form (N_CHANNELS, WINDOW).
 2. `stop(self)`, releases / frees the hardware correctly when exit.

 ## Function build_source()
 - Returns DemoEEG or CytonEEG depending on config.MODE.
 - It may be useful info to use on server.py in order not to import classes by hand.

 ---

 # Preprocessing.py
 - It owns the preprocessing EEG Chain.
 - The pipeline contains the bandpass, notch and CAR (Common Average Reference) filters.
 - All the parameters established came from the `config.py` file.
 
 On this module:
 1. `_butter_coeffs(low: float, high: float, btype: str)`, calculates the Butterworth coefficients normalized at the Nyquist frequency. The parameters are refering to Hz limitation and btype to `band` or `bandstop`.
 2. `bandpass(signal: np.ndarray)`:
    - It is a Bandpass filter [BP_LOW – BP_HIGH] Hz.
    - It erases the DC offset and high frequency artifacts.
    - Signal used is a one dimensional array (one window of one channel).
 3. `notch(signal: np.ndarray)`:
    - The Notch filter is around the NOTCH_FREQ (50 Hz).
    - It erases the power line interference. 
    - Signal used is a one dimensional array (one window of one channel).
 4. `car(eeg: np.ndarray)`:
    - Common Average Reference: it substracts the spatial average to each sample.
    - It reduces the common artifacts to all the electrodes (movement, EMG).
    - eeg is an ndarray: `(N_CHANNELS, WINDOW)`.
 5. `preprocess(eeg: np.ndarray)`:
    - It applies the full chain: bandpass, then notch and CAR.
    - It returns a ndarray ``(N_CHANNELS, WINDOW)` filtered.

 ---

 # CCA.py
 - It is the SSVEP Classifier based on Canonical Correlation Analysis (CCA).
 - For each candidate frequency, it is built a sinusoidal reference signal with N harmonics and it is calculated the canonical one with the EEG window. 
 - The frequency with mayor correlation will be the prediction.

 On this module:
 1. `ref_signal(freq: float)`:
    - Builds the sinusoidal reference matrix for one frequency.
    - Includes `N_HARMONICS` harmonics (sine + cosine per harmonic).
    - The parameters are: freq, which is the fundamental frequency in Hz and it returns a ndarray with the form of `(2·N_HARMONICS, WINDOW)`.
 2. `classify_window(eeg: np.ndarray)`:
    - It classifies one EEG window with CCA against all the SSVEP frequencies.
    - The parameters are: eeg, which is a ndarray `(N_CHANNELS, WINDOW)` already preprocessed.
    - It returns: `label`, which is the predicted key (str) or None if conf < CONFIDENCE_THRESHOLD
                  `conf`, which is the maximal canonical correlation [0, 1].
                  `scores` which is a dict {key: correlation} for all the frequencies.

 ---

 # Voting.py
 - It is the majority temporal votation procedure. 
 - It acumulates `N_VOTES` consecutive predictions and elicits the winner.
 - It reduces false detections caused by punctual artifacts.
 - The added latency ≈ N_VOTES × WINDOW_SEC seconds.

 On this module:
 1. `class Voter`, is encharged of the votation with simple majority respect to a sliding window of predictions. 
    - It uses `voter = Voter()`
              `winner = voter.vote(label)` which returns str o None
 
    - If the label is None (low confidence), the buffer resets.
    - Till there are no acumulated N_VOTES, it returns None.
    - Once completing N_VOTES, it emits a more frequent label and resets.

 2. Inside this class it exists the function `vote(self, label: str | None)`:
    - It registers a new prediction and returns the voting result.
    - The parameters are: `label`, it is a classifier prediction or None if it did not surpass the threshold.
    - It returns the winner label (str) once acumulated N_VOTES are obtained, o.w. None.


    
 
 

 