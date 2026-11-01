# cuecom

Assistive communication from voluntary signals. The user chooses their own signals (a gesture, a sound,
a sign, a look), cuecom reads them from video and audio, and ranks a few things the user might mean.
Nothing is spoken until the user confirms one.

## Principles
- **The user defines the signals.** Signals are enrolled by the user, not assumed from a fixed vocabulary.
  `config/mapping_provisional.json` is a placeholder for simulation only.
- **Abstain when unsure.** "Nothing is being communicated" is a real outcome, not an error.
- **The user confirms every utterance.** Suggestions are hypotheses; the confirm step is the output.
- **Evidence is fused, not guessed.** Video gives an initial distribution over intents, audio and the
  conversation partner's speech update it (Bayesian), and the posterior ranks phrases.
- **Local first.** The core pipeline runs offline. Hosted models (Gemini, Claude) and hosted speech
  transcription are optional layers with local fallbacks.
- **No accuracy or clinical claims** beyond what `docs/EVALUATION.md` measures.

## Setup (Python 3.11)
**macOS** (Apple Silicon or Intel; needs Homebrew):
```bash
bash setup_mac.sh
```
Then allow Camera and Microphone for your terminal or IDE in System Settings → Privacy & Security.

**Windows** (clone into a short path such as `C:\code\cuecom`):
```powershell
.\setup_windows.ps1
```

Both scripts install `requirements.txt` and then `envisionhgdetector` with `--no-deps`.
Then follow [session model setup](docs/SESSION-SETUP.md) to prepare local model assets.
The session modes require prepared local models and do not download them implicitly.

## Run

### Recorded assessment (three options to confirm)
```powershell
& .\.venv\Scripts\python.exe -m apps.session --assessment
```
In the OpenCV window: **SPACE** records audio/video, **ENTER** stops and assesses, **1-3** confirms and
speaks an option, **R** retries, **P** opens the packet and **Q** quits. See
[recorded assessment](docs/RECORDED-ASSESSMENT.md). Hosted suggestions need a key in the ignored `.env`
([Gemini setup](docs/GEMINI-SETUP.md)).

### Learning lab
```powershell
& .\.venv\Scripts\python.exe -m apps.session --record
```
Combines person selection, face/body/hand features, anonymous audiovisual motifs, the ASL alphabet reader,
conversation context and confirmation before local speech. See [the layer-test guide](docs/SESSION-LAB.md).

### Live pipeline (earlier entry point)
```bash
.venv/bin/python -m apps.live --camera 0 --audio          # macOS
.venv\Scripts\python.exe -m apps.live --camera 0 --audio  # Windows
```
Optional conversation model (dialogue corpora are downloaded, not committed; DailyDialog is CC BY-NC-SA 4.0):
```bash
python -m cuecom.context.conversation fetch
python -m cuecom.context.conversation build
```
Enroll your own signs (each recorded 4 times; recordings stay in `data/signs/`, not in git):
```bash
python -m cuecom.perception.vision.signs enroll --signs YES NO HELP MORE WATER BATHROOM
python -m cuecom.perception.vision.signs check
```
Dialogue-act model (Switchboard, CC BY-NC-SA 3.0, downloaded not committed):
```bash
python -m cuecom.context.acts fetch
python -m cuecom.context.acts train
python -m cuecom.context.conversation soften
python -m cuecom.context.conversation fit
```
Keys: **1–3** confirm and speak, **0** rejects all, **N** switches which person is the user, **Q** quits.
Fingerspelling: **A** adds the stable letter, **SPACE** a space, **D** deletes, **C** clears, **S** speaks.
`--video file.mp4` replaces the camera; `--headless --max-frames N` runs without a window.

## Tests
Offline tests open no sensors and make no provider calls:
```bash
python -m unittest discover -s tests -t .
```

## Layout
The pipeline is a set of stages behind small interfaces; [architecture](docs/ARCHITECTURE.md) explains
the seams, how to add a component, and how to read a session trace.

```
cuecom/
  core/        types.py (Event, Option), interfaces.py (stage protocols), clock.py, trace.py, validate.py
  config.py    repository paths (Settings)
  sensors/     camera.py (LiveCapture), microphone.py (shared-clock mic, WAV replay), clip.py (recorded clips)
  perception/  vision/  video.py (YOLO11n-pose + ByteTrack, Envision, MediaPipe), features.py, session.py
                        (VisualSession), person_lock.py, auto_target.py, envision.py, asl.py, signs.py
               audio/   events.py (segmenter, voc2vec, template classifier), vocalization.py (classifier + fusion)
               speech/  transcribe.py (faster-whisper, optional Meta Muse)
  learning/    motifs.py (MotifLearner: motifs grounded only through confirmations)
  context/     state.py (ConversationState), conversation.py (reply model), acts.py (dialogue acts)
  inference/   meaning.py (referents, clarify, composer), retrieval.py (phrase database + ranker)
  llm/         gemini.py, assessment.py (three validated options), composer.py (Anthropic/other providers)
  session/     engine.py (SessionEngine), assessment.py (ClipAssessmentService)
  output/      tts.py
  debug/       overlay.py (landmark/tracking drawing)
apps/          session.py, assessment.py (OpenCV surfaces), live.py (earlier loop), labs/ (layer test labs)
tests/         offline contract tests
tools/         simulate.py, pool_oracle.py, benches, check_gemini.py
config/        likelihood tables (placeholders), phrase database, LLM profiles
docs/          architecture, plan, evaluation, layer notes and research
```

Phrase data includes messages from Vertanen & Kristensson (2011), CC BY 4.0. See `data/aac_corpus/README.md`.
