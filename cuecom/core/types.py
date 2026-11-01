"""Typed objects that cross stage boundaries.

Producers may still hand plain dicts across a seam; the consumer passes them through `from_dict`, so a
malformed value fails at the seam with the field named, not two stages later. `to_dict` gives the
JSON-ready form that packets, profiles and the trace store.
"""
from dataclasses import dataclass, field
import hashlib
import json

from cuecom.core.validate import ids, name, time, unit

MODALITIES = ('audio', 'video', 'paired')
BAD_FLAGS = ('tts', 'overlap', 'tracking_lost', 'source_lost')
OPTION_KINDS = ('message', 'clarify', 'hypothesis')


@dataclass(frozen=True)
class Event:
    """One measured signal on the shared session clock. Features are unit-normalized."""
    event_id: str
    session_id: str
    modality: str
    t_start: float
    t_end: float
    person_id: str | None
    ownership_valid: bool
    clock_valid: bool
    complete: bool
    features: tuple
    feature_schema: str
    source_event_ids: tuple
    group_id: str | None
    quality: dict
    confirmed_negative: bool
    context_id: int | None = None

    @classmethod
    def from_dict(cls, event):
        if not isinstance(event, dict):
            raise ValueError('event must be an object')
        identity = name(event.get('event_id'), 'event_id')
        session = name(event.get('session_id'), 'session_id', 128)
        modality = event.get('modality')
        if modality not in MODALITIES:
            raise ValueError('modality must be audio, video or paired')
        start, end = time(event.get('t_start'), 't_start'), time(event.get('t_end'), 't_end')
        if end < start:
            raise ValueError('event end precedes start')
        person = event.get('person_id')
        if person is not None:
            person = name(person, 'person_id', 128)
        quality = event.get('quality') or {}
        if not isinstance(quality, dict):
            raise ValueError('quality must be an object')
        quality = {key: quality.get(key) is True for key in (*BAD_FLAGS, 'confirmed_by_user')}
        features = unit(event.get('features')).tolist()
        feature_schema = name(event.get('feature_schema', 'unspecified-v1'), 'feature_schema', 256)
        sources = ids(event.get('source_event_ids') or [], 'source_event_id', 2)
        if len(sources) > 2:
            raise ValueError('a paired observation may contain at most two source events')
        for source in sources:
            name(source, 'source_event_id')
            if source == identity:
                raise ValueError('an event cannot be its own source')
        if modality == 'paired' and len(sources) != 2:
            raise ValueError('paired events require two provenance IDs')
        group = event.get('group_id')
        if group is not None:
            group = name(group, 'group_id')
        negative = quality['confirmed_by_user'] and (
            event.get('negative') is True or event.get('is_communicative') is False
            or event.get('confirmed_negative') is True)
        context = event.get('context_id')
        if context is not None and (not isinstance(context, int) or isinstance(context, bool) or context < 0):
            raise ValueError('context_id must be a nonnegative integer')
        return cls(identity, session, modality, start, end, person,
                   event.get('ownership_valid') is True and person is not None,
                   event.get('clock_valid') is True, event.get('complete', True) is True,
                   tuple(features), feature_schema, tuple(sources), group, quality, bool(negative), context)

    def to_dict(self):
        """Normalized record plus a fingerprint over its canonical JSON (features rounded to 8 places)."""
        value = {'event_id': self.event_id, 'session_id': self.session_id, 'modality': self.modality,
                 't_start': self.t_start, 't_end': self.t_end, 'person_id': self.person_id,
                 'ownership_valid': self.ownership_valid, 'clock_valid': self.clock_valid,
                 'complete': self.complete, 'features': list(self.features), 'feature_schema': self.feature_schema,
                 'source_event_ids': list(self.source_event_ids), 'group_id': self.group_id,
                 'quality': dict(self.quality), 'confirmed_negative': self.confirmed_negative}
        if self.context_id is not None:
            value['context_id'] = self.context_id
        canonical = {**value, 'features': [round(x, 8) for x in self.features]}
        value['fingerprint'] = hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(',', ':'),
                                                        allow_nan=False).encode('utf-8')).hexdigest()
        return value


@dataclass(frozen=True)
class Option:
    """One possibility offered to the user. Only `message` and `hypothesis` options can be spoken."""
    text: str
    kind: str
    evidence_ids: tuple = ()
    option_id: str | None = None
    extra: dict = field(default_factory=dict)  # provider fields kept as received (rationale, id, ...)

    @classmethod
    def from_dict(cls, option):
        if not isinstance(option, dict):
            raise ValueError('option must be an object')
        if not isinstance(option.get('text'), str):
            raise ValueError('option text must be a string')
        if option.get('kind') not in OPTION_KINDS:
            raise ValueError(f"option kind must be one of {', '.join(OPTION_KINDS)}")
        evidence = option.get('evidence_ids', [])
        if not isinstance(evidence, (list, tuple)):
            raise ValueError('option evidence_ids must be a list')
        extra = {k: v for k, v in option.items() if k not in {'text', 'kind', 'evidence_ids', 'option_id'}}
        return cls(option['text'], option['kind'], tuple(evidence), option.get('option_id'), extra)

    def to_dict(self):
        value = {**self.extra, 'text': self.text, 'kind': self.kind, 'evidence_ids': list(self.evidence_ids)}
        if self.option_id is not None:
            value['option_id'] = self.option_id
        return value
