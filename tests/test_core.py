"""Contracts for cuecom.core: boundary types, trace, stage interfaces. Offline; no sensors or models."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cuecom.core import interfaces, trace
from cuecom.core.types import Event, Option
from cuecom.session.engine import SessionEngine


def event(**overrides):
    value = {'event_id': 'e1', 'session_id': 's1', 'modality': 'video', 't_start': 1., 't_end': 2.,
             'person_id': 'p1', 'ownership_valid': True, 'clock_valid': True, 'features': [3., 4.]}
    return {**value, **overrides}


class EventTests(unittest.TestCase):
    def test_normalizes_and_fingerprints(self):
        record = Event.from_dict(event()).to_dict()
        self.assertEqual(record['features'], [.6, .8])
        self.assertTrue(record['ownership_valid'] and record['clock_valid'] and record['complete'])
        self.assertEqual(record['quality'], {'tts': False, 'overlap': False, 'tracking_lost': False,
                                             'source_lost': False, 'confirmed_by_user': False})
        self.assertEqual(record['fingerprint'], Event.from_dict(event()).to_dict()['fingerprint'])
        self.assertNotEqual(record['fingerprint'], Event.from_dict(event(t_end=3.)).to_dict()['fingerprint'])

    def test_ownership_needs_a_person(self):
        self.assertFalse(Event.from_dict(event(person_id=None)).ownership_valid)

    def test_rejections_name_the_field(self):
        cases = [(event(modality='speech'), 'modality'), (event(t_end=.5), 'end precedes start'),
                 (event(features=[0., 0.]), 'zero'), (event(features=[1.]), 'features'),
                 (event(modality='paired'), 'two provenance'), (event(source_event_ids=['e1']), 'own source'),
                 (event(context_id=-1), 'context_id'), (event(event_id=''), 'event_id')]
        for raw, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                Event.from_dict(raw)

    def test_context_id_is_kept_only_when_given(self):
        self.assertNotIn('context_id', Event.from_dict(event()).to_dict())
        self.assertEqual(Event.from_dict(event(context_id=4)).to_dict()['context_id'], 4)


class OptionTests(unittest.TestCase):
    def test_round_trip_keeps_provider_fields(self):
        option = Option.from_dict({'text': 'Water, please.', 'kind': 'hypothesis', 'id': 2, 'rationale': 'pointing'})
        self.assertEqual(option.evidence_ids, ())
        self.assertEqual(option.to_dict(), {'id': 2, 'rationale': 'pointing', 'text': 'Water, please.',
                                            'kind': 'hypothesis', 'evidence_ids': []})

    def test_rejects_unknown_kind_and_non_text(self):
        for raw in [{'text': 'x', 'kind': 'shout'}, {'text': 3, 'kind': 'message'},
                    {'text': 'x', 'kind': 'message', 'evidence_ids': 'e1'}]:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                Option.from_dict(raw)


class TraceTests(unittest.TestCase):
    def test_writes_filters_and_stops_after_close(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'nested' / 'trace.jsonl'
            log = trace.Trace(path, clock=lambda: 1.5)
            log.emit('engine', 'observe', event_id='e1', kind='video')
            log.emit('assessment', 'packet', clip_id='c1')
            log.close()
            log.emit('engine', 'late')
            records = trace.read(path)
            self.assertEqual([r['event'] for r in records], ['observe', 'packet'])
            self.assertEqual(records[0], {'t': 1.5, 'stage': 'engine', 'event': 'observe', 'event_id': 'e1', 'kind': 'video'})
            self.assertEqual(len(trace.read(path, stage='assessment')), 1)

    def test_engine_traces_its_decisions(self):
        class Learner:
            def observe(self, event): return {'status': 'new_motif', 'motif_id': 'm1'}
            def pair(self, audio, video, max_lag_s=None): return {'pair_status': 'unpaired'}
            def posterior(self, ids, now_s): return {'items': []}
            def confirm(self, ids, text, at_s): return {'status': 'confirmed', 'evidence_ids': ids}
            def reject(self, option_ids, event_ids=None, at_s=None): pass
            def undo(self): return False
            def save(self, path=None): pass

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'trace.jsonl'
            engine = SessionEngine('s1', Learner(), trace=trace.Trace(path, clock=lambda: 0.))
            engine.set_role('p1', True)
            engine.observe(event())
            engine.suggest_local(2.5)
            engine.confirm(0, 2.6)
            kinds = [r['event'] for r in trace.read(path)]
            self.assertEqual(kinds, ['observe', 'present', 'confirm'])
            self.assertEqual(trace.read(path, event='confirm')[0]['event_ids'], ['e1'])


class InterfaceTests(unittest.TestCase):
    def test_current_implementations_satisfy_the_stage_protocols(self):
        from cuecom.learning.motifs import MotifLearner
        from cuecom.llm.assessment import AssessmentClient
        from cuecom.output.tts import Speaker
        from cuecom.perception.speech.transcribe import MetaTranscriber, Transcriber
        from cuecom.perception.vision.session import VisualSession
        pairs = [(MotifLearner, interfaces.Learner), (AssessmentClient, interfaces.Assessor),
                 (Speaker, interfaces.Speaker), (Transcriber, interfaces.Transcriber),
                 (MetaTranscriber, interfaces.Transcriber), (VisualSession, interfaces.FrameObserver),
                 (trace.Trace, interfaces.Tracer), (trace.NullTrace, interfaces.Tracer)]
        for implementation, protocol in pairs:
            with self.subTest(implementation=implementation.__name__):
                self.assertTrue(issubclass(implementation, protocol))


if __name__ == '__main__':
    unittest.main()
