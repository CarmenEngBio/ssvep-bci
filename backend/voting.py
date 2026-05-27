

#  voting.py  —  Majority Temporal Votation 
#
#  Acumulates N_VOTES consecutive predictions and elicits the winner.
#  Reduces false detentions caused by punctual artifacts.
#  Added latency ≈ N_VOTES × WINDOW_SEC seconds.
 
from config import N_VOTES
 
 
class Voter:
    """
    Votation with simple majority respect to a sliding window of predictions. 
 
    Use: voter = Voter()
         winner = voter.vote(label)   # returns str o None
 
    - If label is None (low confidence), the buffer resets.
    - Till there are no acumulated N_VOTES, it returns None.
    - Once completing N_VOTES, emits a more frequent label and resets.
    """
 
    def __init__(self):
        self._buf: list[str] = []
 
    def vote(self, label: str | None) -> str | None:
        """
        Registers a new prediction and returns the voting result.
 
        Parameters --> label : classifier prediction or None if it did not surpass the threshold.
 
        Returns --> Winner label (str) once acumulated N_VOTES are obtained, o.w. None.
        """
        if label is None:
            self._buf = []
            return None
 
        self._buf.append(label)
 
        if len(self._buf) < N_VOTES:
            return None
 
        winner    = max(set(self._buf), key=self._buf.count)
        self._buf = []
        return winner