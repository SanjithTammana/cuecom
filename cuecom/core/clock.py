"""One monotonic origin for video, delivered audio and conversation turns."""
import time
import uuid


class SessionClock:
    def __init__(self, source=time.perf_counter):
        self.source, self.origin = source, source()
        self.session_id = uuid.uuid4().hex

    def now(self):
        return self.source() - self.origin
