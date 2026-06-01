# Frontend Manual - Browser Endpoint explanation

 Browser Module Explanation —  SSVEP BCI · Phase 1

 ---

 # Launching the frontend

 - Just open the `index.html` file in your browser (double-click).

 # HTML - index.html
  1. There is showed first an instructions menu.
     - It appears when loading the website. Closes with button. 
     - Blinking is not been noticeable till the subject closes the menu and focuses on screen (keypad).
  2. Aferwards it is displayed the main User Interface.

 ---
 # CSS - Styles.css 
  The following design decisions are strongly supported by literature: 
  1. Blinking occurs just on numbers and not on the full cell. This event avoids a huge flickering surface inducing less visual fatigue.
      - Reference: ***Dehais*** et al. 2022 (low modulation amplitude without accuracy penalty).
  2. Smaller cells and more separated, inspired ideally in ***Cheng*** dimensions et al. 2002 (2×2.7 cm, gap 4 cm).
  3. Greys colours used; not bright or strong colours to avoid confusion.
  4. Prediction is showed up as a subtle border instead of previous version that used a bright pink tone. 

 ## NUMERICAL KEYPAD 
  - It is inspired regarding dimensionality from ***Cheng et al. 2002***: buttons 2×2.7 cm, horizontal 4 cm separation / 4.5 cm vertical.
  - Should enough wide separation is guaranteed to reduce visual interference between adyancent stimuli. Consider that the cell space and sizes depends as well on the dimension of the used PC / LAPTOP screen.

 ## BLINKING
  - It just changes the text color, in this case numbers, not the complete cell.
  - `ON STATE` → bright white number.
  - `OFF STATE` → dark grey number (nearly noticeable).
  - The cells `(#222)` remains static, which means that only the numbers flicker and less visual fatigue will be presented.
  - Action keys `(RESET, ENTER)` do not blink, just remain off for the moment. 
  - Reference: ***Dehais et al. 2022***, where it is reduced the contrast depth.

 ## PREDICTION
  - There is a slight bright border, without a lot of highlighting.
  - Informs the engineer/doctor without distracting the subject.

---
 # **JS Files**
 ---
 # App.js 
 - Main JavaScript code is displayed here in order to call other js.
 - This JavaScript will be the entry point regarding the communication pathway (WS) with the frontend.
 - It also calls the flicker engine as well as the WebSocket connection.

---
 # Flicker.js
 - It is based on the flicker engine module following the SSVEP paradigm.
 - Each number flickers at its frequency by calling the requestAnimationFrame for temporal accuracy; considering as well the screen refresh rate.
 - The frequencies are read from the `data-freq` attribute taken from the **DOM**.

---
 # Ui.js
 - Contains the functions related with the **DOM** (css).
 - Does not have any relationship with the flickering or with the WebSocket.
---
 # Websocket.js
 - This module is where the Python server connection is established.
 - It manages the WebSocket connection and automatic re-attempting connection.
 - It has dependencies with the `ui.js` (`setConnectionStatus`, `updateUI`).
