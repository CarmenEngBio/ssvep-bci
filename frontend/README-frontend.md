
/* styles.css SSVEP BCI
   
   DESIGN DECISIONS (supported by literature): 
   · Blinking just on numbers and not on the full cell. 
     This event avoids a huge flickering surface inducing less visual fatigue.
     Reference: Dehais et al. 2022 (low modulation amplitude improving UX without accuracy penalty).
   · Smaller cells and more separated, inspired in Cheng dimensions 
     et al. 2002 (2×2.7 cm, gap 4 cm).
   · Greys colours used; not bright or strong colours to avoid confusion.
   · Prediction: is showed up as a subtle border instead of previous pink tone 

 */

 /* Numerical Keypad */
/*
  Inspired Dimensionality from Cheng et al. 2002:
  buttons 2×2.7 cm, horizontal 4 cm separation / 4.5 cm vertical.
  Enough wide separation is guaranteed to reduce visual interference 
  between adyancent stimuli.
*/

/*
  BLINKING: just changes the text color (numbers), not the complete cell
  ON STATE → bright white number
  OFF STATE → dark grey number (nearly noticeable)  
  The cell (#222) remains static → less visual fatigue will be presented
  Reference: Dehais et al. 2022 — reduces the contrast depth.
*/

/*
  PREDICTION: slight bright border, without highlighting 
  Informs the engineer/doctor without distracting the subject
*/

/* Action keys (RESET, ENTER) - no blinking, just remain off */

---

/* Here it will be displayed the main JavaScript code that will call the other js */

//  This JavaScript will be the entry place regarding the communication pathway with the frontend
//  Calls the flicker engine and the Websocket connection

---

// FLICKER ENGINE SSVEP
//  Each number flickers at its frequency by calling the requestAnimationFrame for temporal accuracy
//  The frequencies are read from the data-freq attribute taken from the DOM.

---

// UI --> INTERFACE UPDATE 
//  Contains the functions related with the DOM
//  Does not have any relationship with the flickering or with the WebSocket

---

// WEBSOCKET - Where Python server connection is established

//  Manages the WebSocket connection and automatic re-attempting connection.
//  Has dependencies with the ui.js (setConnectionStatus, updateUI).