"""Per-session debug trace: one JSON line per stage decision, readable with any JSONL tool.

Records carry IDs, times, counts, statuses and confirmed text, never feature vectors, audio or video.
The file lives in the ignored session folder next to the packets it explains. Each emit appends and
closes, so no handle stays open (a crash loses nothing, and Windows can delete the folder).
"""
import json
from pathlib import Path
import threading
import time


class NullTrace:
    """Default when no trace is wanted."""
    def emit(self, stage, event, /, **data):
        pass

    def close(self):
        pass


class Trace:
    def __init__(self, path, clock=None):
        self.path = Path(path)
        self.clock = clock if clock is not None else time.perf_counter
        self.lock = threading.Lock()
        self.closed = False

    def emit(self, stage, event, /, **data):
        record = {'t': round(self.clock(), 6), 'stage': stage, 'event': event, **data}
        line = json.dumps(record, ensure_ascii=False, default=str)
        with self.lock:
            if self.closed:
                return
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open('a', encoding='utf-8') as file:
                file.write(line + '\n')

    def close(self):
        with self.lock:
            self.closed = True


def read(path, stage=None, event=None):
    """Load a trace back as a list of dicts, optionally filtered."""
    records = [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]
    return [r for r in records if (stage is None or r['stage'] == stage) and (event is None or r['event'] == event)]
