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
| File | Role |
|---|---|
| `cuecom/perception/vision/video.py` | person tracking (YOLO11n-pose + ByteTrack), Envision LightGBM gesture probability, MediaPipe gestures/face on the selected user |
| `cuecom/perception/vision/features.py`, `cuecom/perception/vision/session.py`, `cuecom/perception/vision/person_lock.py`, `cuecom/perception/vision/auto_target.py` | visual feature layer and choosing which person is the user |
| `cuecom/perception/audio/vocalization.py` | voc2vec vocalization classifier, mic pipeline, `BayesianFusion` |
| `cuecom/perception/audio/events.py` | standalone nonverbal audio events, before fusion (one microphone cannot say who made a sound) |
| `cuecom/perception/speech/transcribe.py` | speech transcription (local faster-whisper; optional hosted provider) |
| `cuecom/learning/motifs.py` | anonymous audiovisual motifs learned from confirmed choices |
| `cuecom/inference/retrieval.py` | phrase database, MiniLM embeddings, phrase ranker |
| `cuecom/inference/meaning.py` | partner-question context, referents from pointing, mixed-signal clarify, sentence composer |
| `cuecom/context/conversation.py`, `cuecom/context/state.py` | conversation model: (partner turn -> reply) pairs give P(reply type \| partner) and real replies |
| `cuecom/context/acts.py` | Switchboard dialogue acts: P(act \| text), act transitions, act -> intent map |
| `cuecom/perception/vision/asl.py` | ASL fingerspelling (A-Z): EfficientNet-B0 classifier + stability voting |
| `cuecom/perception/vision/signs.py` | enrolled keyword signs: guided recording, DTW spotting with a no-sign option |
| `cuecom/session/assessment.py`, `cuecom/sensors/clip.py`, `apps/assessment.py` | recorded clip -> evidence packet -> three options; UI-independent service plus OpenCV surface |
| `cuecom/llm/gemini.py`, `cuecom/llm/assessment.py`, `cuecom/llm/composer.py` | optional hosted LLM layers with validation and timeouts |
| `apps/session.py`, `cuecom/session/engine.py`, `cuecom/sensors/capture.py` | session entry point and engine |
| `cuecom/output/tts.py` | offline text-to-speech |
| `tools/simulate.py` | simulator and evaluations (synthetic signals, held-out dialogues, AAC corpus coverage) |
| `apps/live.py` | earlier live loop and panel |
| `config/` | likelihood tables (placeholders), phrase database, LLM profiles |
| `tools/` | tests, benches and layer labs |
| `docs/` | plan, evaluation, layer notes and research |

Phrase data includes messages from Vertanen & Kristensson (2011), CC BY 4.0. See `data/aac_corpus/README.md`.
