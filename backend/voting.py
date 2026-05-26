
# ══════════════════════════════════════════════════════════════
#  VOTACIÓN TEMPORAL
# ══════════════════════════════════════════════════════════════
class Voter:
    def __init__(self):
        self._buf = []

    def vote(self, label):
        if label is None:
            self._buf = []
            return None
        self._buf.append(label)
        if len(self._buf) < N_VOTES:
            return None
        winner     = max(set(self._buf), key=self._buf.count)
        self._buf  = []
        return winner