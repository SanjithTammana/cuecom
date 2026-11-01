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
& .\.venv\Scripts\python.exe cuecom_session.py --assessment
```
In the OpenCV window: **SPACE** records audio/video, **ENTER** stops and assesses, **1-3** confirms and
speaks an option, **R** retries, **P** opens the packet and **Q** quits. See
[recorded assessment](docs/RECORDED-ASSESSMENT.md). Hosted suggestions need a key in the ignored `.env`
([Gemini setup](docs/GEMINI-SETUP.md)).

### Learning lab
```powershell
& .\.venv\Scripts\python.exe cuecom_session.py --record
```
Combines person selection, face/body/hand features, anonymous audiovisual motifs, the ASL alphabet reader,
conversation context and confirmation before local speech. See [the layer-test guide](docs/SESSION-LAB.md).

### Live pipeline (earlier entry point)
```bash
.venv/bin/python run.py --camera 0 --audio          # macOS
.venv\Scripts\python.exe run.py --camera 0 --audio  # Windows
```
Optional conversation model (dialogue corpora are downloaded, not committed; DailyDialog is CC BY-NC-SA 4.0):
```bash
python conversation.py fetch
python conversation.py build
```
Enroll your own signs (each recorded 4 times; recordings stay in `data/signs/`, not in git):
```bash
python signs.py enroll --signs YES NO HELP MORE WATER BATHROOM
python signs.py check
```
Dialogue-act model (Switchboard, CC BY-NC-SA 3.0, downloaded not committed):
```bash
python acts.py fetch
python acts.py train
python conversation.py soften
python conversation.py fit
```
Keys: **1–3** confirm and speak, **0** rejects all, **N** switches which person is the user, **Q** quits.
Fingerspelling: **A** adds the stable letter, **SPACE** a space, **D** deletes, **C** clears, **S** speaks.
`--video file.mp4` replaces the camera; `--headless --max-frames N` runs without a window.

## Tests
Offline tests open no sensors and make no provider calls:
```bash
python -m unittest discover -s tools -p "test_*.py"
```

## Layout
| File | Role |
|---|---|
| `video.py` | person tracking (YOLO11n-pose + ByteTrack), Envision LightGBM gesture probability, MediaPipe gestures/face on the selected user |
| `video_layer.py`, `visual_session.py`, `person_selection.py`, `automatic_target.py` | visual feature layer and choosing which person is the user |
| `audio_text.py` | voc2vec vocalization classifier, mic pipeline, `BayesianFusion` |
| `audio_layer.py` | standalone nonverbal audio events, before fusion (one microphone cannot say who made a sound) |
| `transcribe.py` | speech transcription (local faster-whisper; optional hosted provider) |
| `motif_learning.py` | anonymous audiovisual motifs learned from confirmed choices |
| `retrieval.py` | phrase database, MiniLM embeddings, phrase ranker |
| `meaning.py` | partner-question context, referents from pointing, mixed-signal clarify, sentence composer |
| `conversation.py`, `conversation_state.py` | conversation model: (partner turn -> reply) pairs give P(reply type \| partner) and real replies |
| `acts.py` | Switchboard dialogue acts: P(act \| text), act transitions, act -> intent map |
| `asl.py` | ASL fingerspelling (A-Z): EfficientNet-B0 classifier + stability voting |
| `signs.py` | enrolled keyword signs: guided recording, DTW spotting with a no-sign option |
| `assessment_service.py`, `assessment_capture.py`, `assessment_session.py` | recorded clip -> evidence packet -> three options; UI-independent service plus OpenCV surface |
| `gemini_client.py`, `gemini_assessment.py`, `llm.py` | optional hosted LLM layers with validation and timeouts |
| `cuecom_session.py`, `session_engine.py`, `session_capture.py` | session entry point and engine |
| `tts.py` | offline text-to-speech |
| `simulate.py` | simulator and evaluations (synthetic signals, held-out dialogues, AAC corpus coverage) |
| `run.py` | earlier live loop and panel |
| `config/` | likelihood tables (placeholders), phrase database, LLM profiles |
| `tools/` | tests, benches and layer labs |
| `docs/` | plan, evaluation, layer notes and research |

Phrase data includes messages from Vertanen & Kristensson (2011), CC BY 4.0. See `data/aac_corpus/README.md`.
