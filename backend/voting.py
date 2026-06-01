
 
from config import N_VOTES
 
class Voter:
 
    def __init__(self):
        self._buf: list[str] = []
 
    def vote(self, label: str | None) -> str | None:
        if label is None:
            self._buf = []
            return None
 
        self._buf.append(label)
 
        if len(self._buf) < N_VOTES:
            return None
 
        winner    = max(set(self._buf), key=self._buf.count)
        self._buf = []
        return winner