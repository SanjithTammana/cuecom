"""Camera capture that records continuously while inference reads the latest timestamped frame."""
import json
import threading
import time

import cv2
import numpy as np


class LiveCapture:
    """Record continuously while inference reads the latest timestamped frame.

    Preview landmarks belong to the analyzed frame. Raw recording includes frames
    inference skips. The clock is host camera-read time, not sensor exposure time.
    """
    def __init__(self, cap, folder=None, label='unlabeled', time_source=None, frame_callback=None):
        self.cap, self.folder, self.label = cap, folder, label
        self.condition, self.stop = threading.Condition(), threading.Event()
        self.latest, self.done, self.error = None, False, None
        self.captured = 0
        self.time_source = time_source
        self.frame_callback = frame_callback
        self.thread = threading.Thread(target=self._run, name='video-lab-capture', daemon=True)

    def start(self):
        self.thread.start()
        return self

    def _run(self):
        writer = times = None
        origin = time.perf_counter()
        try:
            if self.folder is not None:
                times = (self.folder / 'capture_times.jsonl').open('w', encoding='utf-8')
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            if not np.isfinite(fps) or fps <= 0:
                fps = 30.
            while not self.stop.is_set():
                ok, frame = self.cap.read()
                t = self.time_source() if self.time_source is not None else time.perf_counter() - origin
                if not ok:
                    break
                if self.frame_callback is not None:
                    self.frame_callback(frame, t)
                with self.condition:
                    label = self.label
                index = self.captured
                if self.folder is not None:
                    if writer is None:
                        writer = cv2.VideoWriter(str(self.folder / 'capture.mp4'), cv2.VideoWriter_fourcc(*'mp4v'), fps,
                                                 (frame.shape[1], frame.shape[0]))
                        if not writer.isOpened():
                            raise RuntimeError('could not create camera recording')
                    writer.write(frame)
                    times.write(json.dumps({'frame': index, 't_capture': t, 'label': label}) + '\n')
                with self.condition:
                    self.captured += 1
                    self.latest = index, t, frame, label
                    self.condition.notify_all()
        except Exception as error:
            self.error = error
        finally:
            if times:
                times.close()
            if writer:
                writer.release()
            self.cap.release()
            with self.condition:
                self.done = True
                self.condition.notify_all()

    def read_after(self, index):
        with self.condition:
            self.condition.wait_for(lambda: self.done or (self.latest is not None and self.latest[0] > index))
            if self.error:
                raise RuntimeError('camera capture failed') from self.error
            return self.latest if self.latest is not None and self.latest[0] > index else None

    def set_label(self, label):
        with self.condition:
            self.label = label

    def close(self):
        self.stop.set()
        self.thread.join(timeout=3.)
        if self.thread.is_alive():
            self.cap.release()
            self.thread.join(timeout=2.)
        if self.thread.is_alive():
            raise RuntimeError('camera did not stop; recording finalization is unconfirmed')
        if self.error:
            raise RuntimeError('camera recording failed') from self.error
