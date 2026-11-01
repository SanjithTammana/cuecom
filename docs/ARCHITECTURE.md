# Architecture

cuecom is a pipeline of stages. Each stage hides behind a small interface in `cuecom/core/interfaces.py`,
and the values that cross between stages have types in `cuecom/core/types.py`. The interfaces are
`typing.Protocol`s: any object with the right methods fits, so a new component, or a fake in a test,
does not have to subclass anything.

## The pipeline (session spine)

```
sensors            perception                 learning        session                   llm / output
camera  ─frame─▶  FrameObserver (VisualSession) ─Event─▶ Learner ─▶ SessionEngine ─packet─▶ Assessor ─Option─▶ user confirms ─▶ Speaker
mic     ─wave──▶  AudioEncoder (voc2vec) ──────Event─▶ (MotifLearner)     ▲                     (Gemini)
                  Transcriber (whisper / Muse) ─turns──────────────────────┘ ConversationState
```

`ClipAssessmentService` (`cuecom/session/assessment.py`) runs this for one recorded clip:
`prepare()` loads the local stages, `observe(frame, t)` feeds video, `packet(clip, capture)` finalizes local
evidence (no network), `assess()` asks the `Assessor` for three options, and `confirm()` speaks one and
grounds its evidence. `apps/session.py` and `apps/assessment.py` are OpenCV surfaces over the same objects;
any other frontend calls the service the same way.

The older `apps/live.py` loop (video → Bayesian fusion → meaning → retrieval) is kept as an app. Its parts
(`inference/`, `perception/audio/vocalization.py`, `context/conversation.py`) are components the spine can
adopt; they are not a second spine.

## Seams

| Producer | Crosses as | Consumer | Checked by |
|---|---|---|---|
| `VisualSession.observe`, mic segmenter | `Event` (dict on the wire) | `MotifLearner.observe` via `SessionEngine.observe` | `Event.from_dict` |
| `SessionEngine.packet`, `ClipAssessmentService.packet` | packet dict (JSON, ≤240 KB) | `Assessor.assess` | `cuecom/llm/assessment.py` schema |
| `Assessor.assess`, `SessionEngine.suggest_local` | `Option` | `SessionEngine.present`, the UI | `Option.from_dict` |
| `Transcriber.transcribe_turns` | turn dicts on the session clock | `ConversationState.add_turn` | `ConversationState` |
| `SessionEngine.confirm_text` | text | `Speaker.say` | — |

`Event.from_dict` and `Option.from_dict` raise `ValueError` naming the bad field, so a malformed value fails
at the seam that produced it. `to_dict()` gives the JSON form stored in packets and profiles.

## Adding a component

1. Find the protocol for its stage in `cuecom/core/interfaces.py` (`FrameObserver`, `AudioEncoder`,
   `Transcriber`, `Learner`, `Assessor`, `Speaker`).
2. Implement those methods in a module under the matching package (`perception/`, `llm/`, ...).
3. Pass an instance in where the current one is built: `SessionEngine(learner=..., speaker=...)`,
   `ClipAssessmentService(assessor=...)`. Leaving the argument out keeps the current default.
4. Add an offline test under `tests/` with a fake for anything that needs a sensor, model or network.
   `tests/test_core.py` checks that every current implementation still satisfies its protocol.

## Debugging with the trace

Every engine and assessment decision is one JSON line in the session folder (ignored by git):

- recorded assessment: `.scratch_session/<profile>/trace-<session id>.jsonl`
- live session: `.scratch_session/<profile>/<session id>/trace.jsonl`

Each record has `t` (seconds on the session clock), `stage`, `event` and the IDs involved: `observe`
(event id, modality, motif status), `paired`, `present` (options shown), `stale` (why suggestions were
discarded), `confirm` (text and grounded evidence), `reject`, `undo`, `role_reset`, and for assessments
`prepare`, `packet`, `assess`, `assess_failed`, `confirm`. Records never contain features, audio or video.

```python
from cuecom.core import trace
records = trace.read('.scratch_session/default/trace-<id>.jsonl', stage='engine', event='stale')
```

To trace something new, take a `trace=None` argument, default to `NullTrace()`, and call
`self.trace.emit('<stage>', '<event>', **ids_and_counts)`.

## Conventions

- Only `sensors/` opens cameras and microphones; only `llm/` and `perception/speech/` call the network.
- `apps/` holds entry points and drawing, never logic a frontend would need.
- Paths come from `cuecom.config` (`ROOT`, `Settings`). Runtime output goes to ignored paths
  (`models/`, `.scratch*`, `data/signs/`, `data/dialogue/`, `data/confirmations.jsonl`); keep new
  runtime output there, and check `git status` before committing after a live session.
- Run modules from the repository root with `python -m`, for example `python -m apps.session --assessment`.

## Not yet unified (follow-up PRs)

Each is a separate, reviewable change:

1. One person-lock: `video.TargetSelector`, `person_lock.TargetLock`, `auto_target.AutomaticTarget`.
2. One audio classifier: `vocalization.VocalizationClassifier` vs `events.TemplateClassifier` / `Voc2VecEncoder`.
3. One LLM provider interface over `llm/gemini.py` and `llm/composer.py`.
4. One `.env` reader: `llm/gemini._settings` and `transcribe.meta_settings` parse the same file separately
   (security-relevant; change with review).
5. Bayesian fusion (`BayesianFusion`, `BeliefFilter`) moved from `perception/audio/vocalization.py` to
   `inference/fusion.py` once the spine adopts it.
