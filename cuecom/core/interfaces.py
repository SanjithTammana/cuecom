"""The stage interfaces. Any object with these methods fits; nothing has to subclass them.

To add a sensor, detector, transcriber or LLM, implement the matching protocol and pass the object in
where the current implementation is constructed (`SessionEngine`, `ClipAssessmentService`). Tests use
small fakes against the same protocols.
"""
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class FrameObserver(Protocol):
    """Video stage: one frame in, the per-frame observation and any completed events out."""
    def observe(self, frame: Any, at_s: float) -> tuple[dict, list[dict]]: ...
    def close(self) -> None: ...


@runtime_checkable
class AudioEncoder(Protocol):
    """Audio stage: a 16 kHz mono waveform to one embedding vector."""
    def __call__(self, wave: Any) -> Any: ...


@runtime_checkable
class Transcriber(Protocol):
    """Speech stage: partner speech to timed turns on the session clock."""
    def transcribe_turns(self, wave_data: Any, start_s: float = 0, speaker_id: str | None = None) -> list[dict]: ...


@runtime_checkable
class Learner(Protocol):
    """Learning stage: events in; meanings grounded only through the user's confirmations."""
    def observe(self, event: dict) -> dict: ...
    def pair(self, audio_event: dict, visual_event: dict, max_lag_s: float | None = None) -> dict: ...
    def posterior(self, event_ids: list[str], now_s: float) -> dict: ...
    def confirm(self, event_ids: list[str], text: str, at_s: float) -> dict: ...
    def reject(self, option_ids: list[str], event_ids: list[str] | None = None, at_s: float | None = None) -> Any: ...
    def undo(self) -> Any: ...
    def save(self, path: Any = None) -> Any: ...


@runtime_checkable
class Assessor(Protocol):
    """Interpretation stage: an evidence packet (plus optional media) to validated options."""
    def assess(self, packet: dict, video_path: Any = None, audio_path: Any = None) -> dict: ...


@runtime_checkable
class Speaker(Protocol):
    """Output stage: speak confirmed text."""
    def say(self, text: str) -> Any: ...


@runtime_checkable
class Tracer(Protocol):
    """Debug log every stage writes to (see cuecom.core.trace)."""
    def emit(self, stage: str, event: str, /, **data: Any) -> None: ...
