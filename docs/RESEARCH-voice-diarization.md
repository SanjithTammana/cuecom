# Keeping voices apart in a live group conversation (2026-11-01)

Read-only research for Sanjith and Abhiram. No model was downloaded or run, and no number below was measured on cuecom's
data. Tags: **[E]** stated by a listed source, **[X]** arithmetic on a cited number, **[J]** my judgment. Refs like [S3]
point to Sources. Benchmarks run by the vendor or the authors of the system being ranked are labelled as such.

Scope agreed with Sanjith: **who spoke when**, from **one laptop or phone microphone**, with voices defining the
participants and faces attaching only when visible. Re-identifying people across days, separating overlapped speech and
extracting one target speaker are out of scope and appear only where they constrain the design.

Builds on, does not redo: `ARCHITECTURE.md` (stages, seams, trace), `LAYER-audio.md` (the communicator's sound-event
layer, its segmenter and its `speech`/`other` negative classes), `RESEARCH-speech-disorders.md` (who the users are; open
in PR #2) and `RESEARCH-datasets.md`.

## 0. Bottom line

1. **Two open systems run in real time on one CPU thread at about one second of latency: diart and FASTDIAR.** In the
   FASTDIAR authors' own comparison, diart has a real-time factor of 0.16 and FASTDIAR 0.19 on one thread, at 1000 ms and
   960 ms latency [E: S5]. Both are MIT-licensed [E: S1, S6]. diart's default models are gated on Hugging Face [E: S1];
   FASTDIAR's weights are a plain GitHub release [E: S6]. NVIDIA's Streaming Sortformer is the most accurate of the three
   when overlapped speech is scored, but the same table gives it a real-time factor of 1.54 and the paper says it "needs a
   GPU" [E: S5]. It is also capped at four speakers [E: S4]. It is not an option for a laptop CPU. [J]
2. **Streaming costs accuracy, and the cost is speaker confusion.** diart at 1 s latency scores 27.6 / 30.4 / 20.1% DER on
   DIHARD III / AMI / VoxConverse, against 19.3 / 19.9 / 11.1% for the offline topline in the same paper [E: S3], and
   the authors report confusion "consistently increases as the latency decreases" while misses and false alarms stay flat
   [E: S3]. The < 0.5 s speaker-change target is not met by any CPU system at its published operating point. cuecom
   should publish a provisional label within 0.5 s and a settled one within about 1 s, and treat every label as
   revisable. [J]
3. **The short turns that matter most to cuecom are where speaker embeddings are worst.** "Yes?", "What?" and "Do you want
   juice?" last one or two seconds. One 2026 paper reports a WavLM + ECAPA-TDNN baseline at 0.97% EER on full VoxCeleb1-O
   trials, 5.24% on 2 s trials and 18.44% on 1 s trials [E: S16], about 19 times worse at 1 s [X]. A one-second turn
   should never open a new speaker on its own. [J]
4. **The communicator must be a declared participant, not a cluster the diarizer discovers.** Diarizers are trained on
   typical speech. An x-vector verifier trained on VoxCeleb had 15.56% EER on dysarthric speakers against 2.07% on
   control speakers in the same corpora [E: S18], about 7.5 times worse [X]. Off-the-shelf pyannote scored 34.9% DER on
   sessions with minimally verbal autistic children against 15.6% for a fine-tuned model [E: S19], and LENA was "<50%
   reliable" at detecting the vocalizations of autistic 5 to 18 year olds [E: S20]. I found no diarization study on
   dysarthric speech at all. cuecom's own sound-event path (`events.py`) should claim the communicator's sounds first;
   only what it rejects as `speech` should reach the diarizer. [J]
5. **cuecom's own TTS is already muted out of the microphone, and the diarizer must sit behind the same mute.** The
   session loop drops audio blocks that overlap TTS playback plus a 0.7 s guard (`apps/session.py`, `tts.Speaker.overlaps`),
   and `ConversationState` drops turns that repeat recent TTS text. A synthetic voice that leaked through would form a very
   consistent cluster and be counted as a new person. [J]
6. **First prototype:** FASTDIAR and diart side by side behind a new `SpeakerTracker` protocol, run on WAV replay, scored
   per held-out session. Adopt one only if, on held-out own recordings and the NOTSOFAR-1 single-device eval set, it
   attributes finalized partner turns of at least 1 s to the right voice at least 85% of the time, gets the speaker count
   exactly right in at least 70% of sessions, and keeps the whole audio stack below a real-time factor of 0.5 on the
   i7-1355U (section 6). These thresholds are my proposal, not a published standard. [J]

## 1. What cuecom does today

- **One microphone, no speaker identity.** Every audio event has `person_id` None unless the operator passes `--user-mic`
  to assert a dedicated communicator input (`apps/session.py`). `LAYER-audio.md` §4 states that a single microphone
  cannot say who made a sound. [E: repo]
- **Fixed 6-second ASR chunks.** The loop concatenates capture blocks until `asr_n >= 6 * SR`, then submits the chunk if
  its RMS is above -55 dBFS and it does not overlap TTS. faster-whisper (`base.en`, int8, CPU) transcribes it with its
  own VAD filter on, and every turn gets `speaker_id` 'unknown' and `speaker_role` 'unknown' (`transcribe.py`). [E: repo]
- **ASR results are tied to the camera lock.** A transcription result is accepted only if `engine.person_id` still equals
  the person locked when the chunk started, and the ASR buffer restarts when the lock changes (`role_since`). Partner
  speech is therefore dropped when the camera switches person, even though partners may never be on camera. [E: repo + J]
- **The cloud path has chunk-local labels.** The Meta Muse transcriber in `transcribe.py` asks for `DIARIZATION` mode and gets speaker labels, but cuecom scopes
  each label to a fresh UUID per request (`speaker_scope: 'recording'`), so "speaker A" in one 6-second chunk is not
  "speaker A" in the next. That is correct given what the API promises; it means nothing tracks voices across chunks. [E: repo]
- **`ConversationState` is already ready for diarized input.** Turns carry `speaker_id`, `speaker_role`, `speaker_scope`,
  `speaker_uncertain`, `overlap`, `overlap_known`, `final` and `revision`; a turn with the same `turn_id` and a higher
  revision replaces the old one, and a final turn cannot be replaced by a partial. `pending_question` only considers
  finalized, non-overlapped turns with role `partner`. [E: repo]
- **Silero VAD is already installed.** faster-whisper bundles Silero VAD v6 and `tools/bench_audio.py` already uses it for
  the speech gate [E: repo]. Silero is MIT-licensed and processes a 30 ms chunk in under 1 ms on one CPU thread, per its
  README [E: S21].

## 2. Streaming diarization on a laptop CPU

### 2.1 Candidates

| System | How it works | Latency | CPU real-time? | Speakers | Licence / access | Fit for cuecom |
|---|---|---|---|---|---|---|
| **diart** [S1, S2, S3] | pyannote segmentation on a 5 s rolling buffer, updated every 0.5 s; incremental clustering of per-speaker embeddings with thresholds `tau_active`, `rho_update`, `delta_new` | Adjustable from 500 ms to 5 s [E: S3]; default `latency = step = 0.5` s [E: S2] | Yes. One 500 ms step took 165 ms on a 20-core Xeon [E: S3]; RTF 0.16 on one thread in the FASTDIAR table [E: S5] | `max_speakers=20` default [E: S2]; up to 4 per 5 s chunk [E: S3] | Code MIT [E: S1]. Default `pyannote/segmentation` and `pyannote/embedding` are gated (accept conditions, HF token) [E: S1]. WhisperLiveKit marks diart "[Not recommended]" and notes diart 0.9.2 needs NumPy < 2 [E: S10] | Baseline. cuecom pins `numpy==1.26.4`, so the NumPy pin does not block it [E: repo] |
| **FASTDIAR** [S5, S6] | Causal frame-level speaker encoder (distilled from ReDimNet2-B6) emits one embedding per 80 ms from a 2 s past window; Silero VAD; online clustering with a confidence gate, new-cluster threshold and merge threshold | Fixed 960 ms (emit delay M = 12 frames) [E: S5] | Yes. "five times faster than real time on a single CPU thread" [E: S5]; RTF 0.19 on one Threadripper PRO 5995WX thread [E: S5] | No maximum stated [E: S6] | Code MIT; weights (2.4M / 4.6M / 10.4M params) on the v0.1.0 GitHub release, no separate weights licence stated [E: S6]. Paper submitted 2 Oct 2026 [E: S5] | Primary candidate: ungated, no speaker cap, small. One month old; all numbers are the authors' own |
| **Streaming Sortformer 4spk-v2** [S4] | End-to-end streaming model with a speaker cache and FIFO | 0.32 s to 30.4 s configs; RTF figures measured on an RTX 6000 Ada GPU [E: S4] | No. RTF 1.54 in the FASTDIAR table and "needs a GPU" [E: S5] | Max 4; "performance degrades on recordings with 5 and more speakers" [E: S4] | CC-BY-4.0, NeMo [E: S4] | Not on a laptop CPU. A cuecom group often has 4+ voices once bystanders are counted [J] |
| **pyannote community-1** [S7] | Offline: segmentation + WeSpeaker embeddings + VBx clustering; also an "exclusive" one-speaker-per-frame output | Offline only; the card does not mention streaming [E: S7] | Not stated | `num_speakers`, `min_speakers`, `max_speakers` options [E: S7] | CC-BY-4.0, gated (accept conditions, HF token), can run offline from a local clone [E: S7] | Not live. Useful to draft reference labels for own recordings (section 5.3) |
| **pyannoteAI Live-1** [S8, S9] | Hosted streaming over WebSocket, 100 ms chunks of 16 kHz mono | "sub-300ms" end-to-end, vendor claim with no method given [E: S8] | Runs on the vendor's "shared infrastructure" [E: S8] | Up to 8 per stream [E: S8] | Commercial API [E: S8, S9] | Sends every bystander's voice to a third party. Comparison point only [J] |
| **WhisperLiveKit** [S10] | Streaming Whisper (SimulStreaming or LocalAgreement policy) plus a diarization backend (Sortformer default, diart optional) and VAD | No figures; benchmarks on an H100 [E: S10] | CPU install exists; Canary "works but is slow" on CPU [E: S10] | Sortformer's 4, asserted not estimated [E: S10] | Repo Apache-2.0; component models carry their own licences [E: S10] | Reference for streaming ASR policy, not a dependency |

### 2.2 Accuracy, read carefully

**FASTDIAR authors' comparison (Table 1, DER %, collar 0)** [E: S5]. Each cell is "overlap scored / overlap excluded":

| System | Latency | RTF | NOTSOFAR all | NOTSOFAR ≥5 spk | VoxConverse all | DIHARD III all | AMI |
|---|---|---|---|---|---|---|---|
| diart | 1000 ms | 0.16 | 54.16 / 48.01 | 59.89 / 54.16 | 18.20 / 16.12 | 26.73 / 22.04 | 33.37 / 28.79 |
| Streaming Sortformer | 1040 ms | 1.54 | 27.63 / 23.39 | 37.49 / 33.45 | 20.08 / 19.15 | 20.36 / 17.34 | 30.25 / 25.56 |
| FASTDIAR | 960 ms | 0.19 | 39.63 / 21.58 | 44.25 / 24.25 | 15.07 / 12.35 | 32.57 / 26.06 | 33.36 / 22.15 |

What this table says, and what it does not:

- **FASTDIAR's lead depends on excluding overlap.** It assigns one label per frame, so overlapped regions count as misses;
  the authors say this explains most of the gap between the two protocols [E: S5]. On NOTSOFAR it goes from 39.63% to
  21.58%, while Sortformer goes from 27.63% to 23.39% [E: S5]. In a conversation with interruptions, the second speaker's
  overlapped words will be attributed to the first speaker or missed. [X + J]
- **It is not a blind test.** FASTDIAR's thresholds and checkpoints were tuned on VoxConverse and NOTSOFAR dev sets, which
  the authors say are "not fully unseen" [E: S5]. Sortformer was trained on AMI and VoxConverse among others [E: S4].
  DIHARD III is the only column that is out of domain for FASTDIAR, and there it ranks last [E: S5]. [J]
- **The hardware statement is clear only for FASTDIAR.** The paper states FASTDIAR's RTF was measured on one thread
  including VAD and clustering [E: S5]. I could not confirm that diart and Sortformer were timed on the same single thread
  (see Could not verify).
- **diart's own paper is a second source.** At 1 s latency (hyperparameters re-tuned for 1 s): 27.6% DIHARD III, 30.4%
  AMI, 20.1% VoxConverse; at 5 s: 25.0 / 27.5 / 16.8%; offline VBx with overlap-aware resegmentation: 19.3 / 19.9 /
  11.1% (no collar, overlap scored) [E: S3]. The gap from offline to 1 s streaming is 8 to 10.5 points of DER [X].

**NVIDIA's own card (Sortformer v2, DER %)** at 1.04 s latency with post-processing: 18.91% DIHARD III full, 13.24% for
DIHARD III files with ≤4 speakers, 42.56% for ≥5 speakers, collar 0 [E: S4]. At 0.32 s, 19.28% / 13.44% / 43.73% [E: S4].
These are vendor-run. The ≥5-speaker column is the one that matters for groups and is more than three times the ≤4 figure
[X]. NVIDIA also warns of degradation "in noisy conditions" [E: S4].

**Offline reference points.** pyannote reports community-1 at 19.9% DER on AMI single distant microphone and 20.2% on
DIHARD III, collar 0, overlap scored [E: S7]; these are vendor-run (pyannote benchmarking its own pipeline).
"Benchmarking Diarization Models" (an independent 2025 study of five offline systems over 196.6 h in five languages)
found pyannoteAI best at 11.2% DER and DiariZen at 13.3%, with missed speech the main error, followed by confusion,
"especially in high-speaker count settings" [E: S12]. SDBench (Interspeech 2025, 13 datasets, 6 systems) evaluated
no streaming system and lists streaming clustering as future work [E: S11]; its authors build a competing product
(SpeakerKit), so its rankings are not fully independent [E: S11]. Neither benchmark answers the streaming-on-CPU
question.

**pyannoteAI's streaming benchmark** (vendor-run, on its own blog) reports 19.8% DER on DIHARD III for its hosted
streaming model against 31.3% Speechmatics, 39.1% Deepgram and 39.2% AssemblyAI, and 44.6% on the DIHARD "meeting"
domain [E: S9]. It does not state the collar, excludes latency, and scores completed output rather than partial
results that are revised while audio arrives [E: S9].

### 2.3 What to take from section 2

- The DER numbers for meetings at 1 s latency sit between 20 and 55% depending on corpus and overlap scoring. A group
  conversation in a kitchen, on a laptop microphone, is closer to NOTSOFAR, CHiME-6 and DIHARD "meeting" / "restaurant"
  (44.6% and 54.4% DER for the best hosted system in the vendor's own table [E: S9]) than to VoxConverse. [J]
- So cuecom should not consume diarizer output as truth. Every voice label on a turn carries `speaker_uncertain`, and
  the decisions that depend on it (above all `pending_question`) should prefer "unknown" to a wrong guess. [J]
- DER is time-weighted. A model can score well while getting the short turns wrong, because a one-second "yes?" is a
  small share of the total time. cuecom consumes turns, not frames, so turn-level attribution is the number that matters
  (section 5.2). [J]

## 3. Counting voices online and detecting new ones

### 3.1 How the two CPU candidates decide "new speaker"

- **diart:** each local speaker in the 5 s buffer is active if its segmentation probability exceeds `tau_active` once in
  the chunk; its embedding updates a matched centroid only if its active duration exceeds `rho_update` ("the minimum
  duration below which a speaker embedding is considered to be too noisy"); it becomes a new global speaker if its distance
  to the nearest centroid exceeds `delta_new` [E: S3]. Defaults are 0.6 / 0.3 / 1.0 [E: S2]; the README's tuned values
  differ by corpus, for example `rho_update` 0.006 on AMI and 0.915 on VoxConverse [E: S1]. Two local speakers in one
  chunk cannot be merged into one global speaker (cannot-link constraint) [E: S3].
- **FASTDIAR:** a frame is "confident" if its embedding is within cosine 0.8 of the embedding 10 frames earlier; only
  confident frames join or create clusters; a new cluster opens when similarity to every cluster median is below 0.4;
  when a new cluster gets its first frame, any pair of clusters above 0.8 is merged; unconfident frames take the nearest
  median without updating it [E: S5]. One fixed set of thresholds was tuned once on dev data [E: S5].

### 3.2 How these fail, and what each failure does in cuecom

| Failure | Mechanism | Effect in cuecom | Mitigation [J] |
|---|---|---|---|
| **Split** (one person becomes two voices) | Short or emotional turns, a turn spoken while moving away from the laptop, or the same person shouting vs murmuring falls past the new-speaker threshold | Speaker count too high; a partner's question is credited to "voice-4" and their next line to "voice-2" | Do not open a voice from < 1.5 s of confident speech; keep it "pending" and attach it to the nearest voice; run a merge pass every few seconds; let the user merge |
| **Merge** (two people become one voice) | Similar voices, a far-away speaker whose embedding is noisy, `rho_update` too low | Two partners look like one; a question from one "answered" by the other's statement | Keep merges reversible; let the user split; report merges in the trace |
| **Late new speaker** | A newcomer's first turns are short and get absorbed into an existing voice until enough confident speech accumulates | Their first question is attributed to someone else | Re-label retroactively; `ConversationState` already accepts a higher revision of the same `turn_id` |
| **Return after silence** | A person quiet for minutes, then speaking from a new position or at a new loudness, can fail to match their old centroid | Count drifts upward over a long session | Keep centroids for the whole session, not a sliding window; prefer merge to new when a pending voice is close to a dormant one |
| **Overlap** | FASTDIAR assigns one label per frame [E: S5]; diart's local segmentation sees up to 4 speakers per chunk [E: S3] but incremental clustering is less accurate than offline | Interruptions attributed to one person | Mark `overlap: true` when VAD energy and two voices' activity coincide, or when the tracker reports it; `pending_question` already ignores overlapped turns |
| **Non-speech sounds and TTS leakage** | Embedding models are trained on speech; laughter, hums, coughs, cuecom's TTS voice or a TV become clusters | Phantom participants; worst for the communicator (section 4) | Gate the diarizer behind the communicator sound path and the TTS mute (section 4) |

### 3.3 Embedding models for 1 to 2 second segments

| Model | Size | Full-length result | Short-segment result | Licence | Notes |
|---|---|---|---|---|---|
| ECAPA-TDNN (SpeechBrain) [S13] | 20.8M in 3D-Speaker's table [E: S14] | 0.80% EER, VoxCeleb1 cleaned test [E: S13] | Not on the card. A WavLM + ECAPA-TDNN baseline in another paper: 5.24% at 2 s, 18.44% at 1 s, 0.97% full, VoxCeleb1-O [E: S16] | Apache-2.0, not gated [E: S13] | The 2 s / 1 s figures are for that paper's own WavLM-fed baseline, not the SpeechBrain checkpoint |
| ERes2NetV2 (3D-Speaker) [S14, S15] | 17.8M [E: S14] | 0.61% EER VoxCeleb1-O [E: S14, S15] | 0.98% at 3 s, 1.48% at 2 s; 1 s not reported [E: S15] | Apache-2.0 toolkit [E: S14] | Designed for short-duration verification [E: S15]. 2.4x its full-length EER at 2 s [X] |
| CAM++ (3D-Speaker) [S14] | 7.2M [E: S14] | 0.65% VoxCeleb1-O [E: S14] | Not found | Apache-2.0 [E: S14] | Smallest of the three |
| WeSpeaker ResNet34-LM (pyannote wrapper) [S17] | Not stated | None on the card [E: S17] | Not found | CC-BY-4.0, no gating shown [E: S17] | Default embedding in pyannote's pipelines; 150 ms per call on CPU in diart's timing table vs 26 ms for `pyannote/embedding` (Ryzen 9) [E: S1] |
| FASTDIAR frame encoder [S5] | 2.4M to 10.4M [E: S6] | EER 1.51 vs 0.44 for the chunked baseline (paper's Table 2) [E: S5] | Built for a 2 s window | MIT code [E: S6] | Worse verifier, better streaming diarizer, per the authors [E: S5] |

Two cautions. First, better verification numbers do not mean better diarization: Jung et al. found that improving
verification benchmarks "does not lead to better diarisation performance" [E: S28]. Second, ECAPA's "Lite" variant from
the starting leads was not found in a primary source and is not used here (see Could not verify). The practical rule for
cuecom is the same for every model: treat a 1 s segment as weak evidence of identity and let it update a voice only when
it agrees with what came before. [J]

## 4. The cuecom-specific problem: the communicator, atypical speech and cuecom's own voice

### 4.1 What diarizers do with these sounds

- **Dysarthric speech.** I found no diarization evaluation on dysarthric speech. The nearest evidence is speaker
  verification: an x-vector system trained on VoxCeleb1, tested on TORGO and UA-Speech, had 15.56% EER on dysarthric
  speakers and 2.07% on control speakers; by severity, 11.39% low, 16.67% medium, 17.95% high [E: S18]. Slowing the
  training speech (duration modification) lowered dysarthric EER to 12.17% [E: S18]. The authors call verification for
  dysarthric speakers "an unexplored area" [E: S18]. So a typical-speech embedding is a poor fingerprint for the
  communicator's voice, and a dysarthric turn is likely to be split off as a new voice or merged with a partner. [J]
- **Minimally verbal autistic children.** On 73 child-parent sessions with minimally verbal autistic children aged 49 to
  95 months, off-the-shelf pyannote scored 34.9% DER (16.1% confusion), and a Whisper-Medium encoder fine-tuned on that
  data scored 15.6% (5.2% confusion) [E: S19]. The annotation separated intelligible speech, unintelligible speech,
  nonverbal vocalization and singing, and the authors used a 100 ms collar because "most child audio segments in this
  dataset are very short" [E: S19]; the paper does not say how nonverbal vocalizations were scored. With 5 s windows
  (the streaming-sized option) DER rose to 18.8% from 16.7% at 20 s [E: S19].
- **Older autistic children and adolescents.** LENA's automated algorithms were "<50% reliable" at detecting vocalizations
  of 5 to 18 year olds with ASD, and speaker misclassification rose with age [E: S20].
- **Non-speech vocalizations in general.** A summary of work by the same USC group reports speech vs nonverbal-vocalization
  classification at 67.8% macro F1 in natural language samples [search summary only; see Could not verify]. The earlier
  lead that child turns are undercounted is consistent with the LENA finding but was not stated as such in
  the sources I read. [J]

### 4.2 Routing: claim the communicator's sounds before the diarizer sees them

The communicator is the one person cuecom knows is present, has enrolled sounds for, and may have a voice profile for.
Discovering them as "voice-3" from typical-speech embeddings throws that knowledge away and invites the failures above.
Proposed routing, every step [J]:

```
mic ─▶ capture (ring buffer, sample clock) ─▶ TTS mute (existing Speaker.overlaps + 0.7 s guard)
        │
        ├─▶ EnergySegmenter + Voc2VecEncoder + TemplateClassifier (events.py, existing)
        │      match to an enrolled communicator class ─▶ communicator sound Event (never ASR, never diarizer)
        │      `speech` winner or unknown ─────────────┐
        │                                              ▼
        └─▶ Silero VAD speech segments ─▶ SpeakerTracker ─▶ voice spans ─┐
                                                                         ├─▶ turn assembler ─▶ ConversationState
              faster-whisper on the open VAD segment (partials) ─────────┘
```

1. **The sound-event path wins ties.** A segment that `TemplateClassifier` accepts as one of the communicator's enrolled
   classes is masked out of the diarizer's input (zeroed frames, or marked non-speech for clustering). The existing rule
   stands: on a shared microphone this does not prove the communicator made the sound, so `person_id` stays None.
2. **Only speech reaches clustering.** Segments the VAD and the `speech` negative class agree are speech go to the
   tracker. Hums, cries, laughter and coughs do not open voices. A sound neither path claims is dropped, not clustered.
3. **The communicator's speech, if any, is a reserved voice.** If the communicator speaks, a `communicator` voice is
   seeded from segments the user has confirmed (passive enrollment, as `RESEARCH-speech-disorders.md` recommends for
   signals), never from a "read these sentences now" step. Segments near that centroid get `speaker_id 'communicator'`
   and `speaker_uncertain true`, and they are excluded from new-speaker creation so a dysarthric turn cannot become a
   phantom partner.
4. **Audio never makes communicator speech authoritative.** Turns from the reserved voice keep `speaker_role 'unknown'`.
   The only communicator turns in `ConversationState` remain `confirm_user` records. That keeps the existing rule that
   suggestions and transcripts are never the user's message, and it protects against the authorship failure the
   speech-disorders report describes.
5. **Partner role needs evidence.** A voice gets `speaker_role 'partner'` only when it is a settled (not pending) voice
   that is not the reserved communicator voice. Otherwise role stays 'unknown', and `pending_question` ignores the turn.

### 4.3 cuecom's own TTS

- Keep the half-duplex mute and feed the tracker a `gap()` for muted spans, so it never bridges audio across a mute and
  never sees the TTS voice. [J]
- Add a reserved `cuecom-tts` voice as a second guard. cuecom knows the exact samples it synthesizes, so it can embed its
  own TTS output directly and label any leaked segment that matches as `cuecom-tts`, discard it, and count it in the trace.
  A leaked TTS segment then becomes a measured event, not a new participant. [J]
- The cost of half-duplex muting is that a partner who talks over cuecom's voice is lost. Acoustic echo cancellation
  would allow barge-in, but laptop speaker-to-microphone echo cancellation was not researched here; it is a separate
  change. [J]

## 5. Plugging diarization into the real-time loop

### 5.1 Replace 6-second chunks with VAD-cut segments

- Cut ASR segments at speech pauses from Silero VAD (for example ≥ 0.4 s of silence), with a forced split at about 8 s
  so a long monologue still yields partials and finals. [J]
- While a segment is open, re-decode it every 0.5 to 1 s and publish a partial turn (`final: false`, `revision` + 1);
  publish the final turn when the segment closes. This is the LocalAgreement / SimulStreaming idea WhisperLiveKit uses
  [E: S10]. The re-decode cost of `base.en` int8 on the i7-1355U is not known and must be measured before promising a
  partial within 1 s. [J]
- Split a segment at a tracker change point: if voice A's span ends and voice B's begins inside one VAD segment, the turn
  assembler closes A's turn and opens B's at the change time.
- Stop tying ASR acceptance to the camera lock. Accept a result if the capture clock stayed valid and the segment does not
  overlap TTS; remove the `window[2] == engine.person_id` and `role_since` conditions for partner speech. Voices are the
  participants; the camera is not. [J]

### 5.2 The `SpeakerTracker` protocol

A sketch in the style of `cuecom/core/interfaces.py` [J]:

```python
@runtime_checkable
class SpeakerTracker(Protocol):
    """Who spoke when, on the session sample clock. Voice IDs are session-scoped and revisable."""
    def feed(self, start_sample: int, wave: Any, mask: Any = None) -> list[dict]: ...  # span and relabel updates
    def gap(self, start_sample: int, end_sample: int) -> None: ...  # capture gap or TTS mute; never bridge it
    def constrain(self, kind: str, voice_a: str, voice_b: str, at_s: float) -> list[dict]: ...  # 'merge' / 'split' from the user
    def close(self) -> list[dict]: ...  # final updates; drops every embedding held for the session
```

Updates are of two kinds. A **span** `{'kind': 'span', 'span_id', 't_start', 't_end', 'voice_id', 'final', 'revision',
'overlap', 'confidence', 'pending'}` says which voice holds an interval; a **relabel** `{'kind': 'relabel', 'from',
'into', 'at_s', 'reason'}` says one voice was merged into another. The turn assembler maps spans onto turns:

| `ConversationState` field | Value |
|---|---|
| `turn_id` | `vad:<session>:<start_sample>`, stable across partials and relabels |
| `speaker_id` | `voice-<n>`, `communicator`, or `unknown` while the span is pending |
| `speaker_scope` | `session` |
| `speaker_uncertain` | true while pending, while the voice has < ~10 s of confident speech, or after a relabel within the last few seconds |
| `speaker_role` | `partner` only for a settled non-communicator voice; otherwise `unknown` |
| `overlap`, `overlap_known` | from the tracker; `overlap_known` false for a tracker that cannot report overlap (FASTDIAR) |
| `final`, `revision` | from the ASR segment and every relabel |
| `backend` | `fastdiar` / `diart` |

A relabel re-emits each affected turn with `revision + 1` and the new `speaker_id`. `ConversationState.add_turn` already
accepts that. Options built on a pending question whose speaker changed should be discarded; the engine already discards
suggestions whose version moved on and traces it as `stale` [E: repo], so a relabel is one more reason. [J]

A tracker that only emits "voice X from t1 to t2" can be faked with a scripted list in tests, which matches the
`tests/` convention. [J]

### 5.3 Latency targets, restated against the evidence

| Target | Evidence | Proposal [J] |
|---|---|---|
| Speaker change < 0.5 s | diart can run at 0.5 s latency [E: S2, S3] but its DER at 0.5 s is not in the paper's text; FASTDIAR is fixed at 960 ms [E: S5]; Sortformer's 0.32 s config needs a GPU [E: S4, S5] | Provisional label ≤ 0.5 s after the change (default: "unknown" or "same voice continuing"), settled label ≤ 1.0 s at the tracker's native delay, relabels any time later |
| Partial transcript < 1 s | Not measured for cuecom's faster-whisper on this laptop | Measure re-decode time per 1 s of audio before committing; drop to `tiny.en` for partials if needed |
| Whole stack real-time | LAYER-audio measured 865 ms per 4 s chunk for the audio candidate under load [E: repo], an RTF of about 0.22 [X]; FASTDIAR adds 0.19 per thread on a workstation core [E: S5] | Budget a combined audio RTF ≤ 0.5 on the i7-1355U with video running, measured, not assumed |

### 5.4 User correction

- Two keys in the session UI: **merge** ("these two voices are one person") and **split** ("this turn was someone else").
  Each calls `constrain`, which turns into must-link / cannot-link constraints and a relabel. [J]
- Optional names. A partner can be renamed from `voice-2` to "Mum" for the session. Names are display labels in the UI,
  not identity claims sent to the LLM, and they do not persist. [J]
- Every correction is a trace record (`stage 'speaker'`, events `relabel`, `merge_user`, `split_user`, `voice_new`,
  `voice_pending`, `tts_leak`) with IDs and counts only, as the trace rules already require. The correction rate per hour
  is then a field metric for free. [J]

### 5.5 Faces attach to voices, never the reverse

The companion camera research owns how faces are detected. On this side, a voice is the primary key; a face track can be
attached to a voice when lip motion or speaking activity repeatedly coincides with that voice's spans, and is detached
when it stops coinciding. A face never creates or renames a voice, and a voice with no face is a normal participant. [J]

### 5.6 Privacy

- Bystander voice embeddings live in the tracker's memory for the session only, are never written to profiles, packets
  or traces, and are dropped on `close()`. [J]
- The reserved communicator voice and `cuecom-tts` embeddings may persist in the communicator's profile, with the same
  consent as their enrolled sounds. [J]
- No hosted diarizer by default. Live-1, Muse and Gemini audio send every person's voice to a third party; they stay
  opt-in, as `--gemini-asr` is today, and their labels stay chunk- or stream-local. [J]
- `--record` remains the only path that stores raw audio, and own recordings for evaluation need consent from everyone
  in the room (section 6.3). [J]

## 6. Evaluation

### 6.1 Datasets

| Dataset | Why | Single-mic condition | Licence / access | Caveat |
|---|---|---|---|---|
| **NOTSOFAR-1** [S24] | 315 meetings of about 6 min, 4 to 8 attendees, 35 speakers [E: S24]; about 30 rooms, about 5 single-channel devices per meeting, eval speakers and rooms disjoint from train/dev (search summary of the challenge paper) | Single-channel device streams [E: S24] | CC BY 4.0 [E: S24] | FASTDIAR tuned on its dev set [E: S5]; use the eval set only |
| **AMI** [S22] | Meetings, 4 people typical | SDM (single distant mic) | CC BY 4.0 [E: S22] | In Sortformer's training data [E: S4] |
| **VoxConverse** [S23] | Many-speaker YouTube audio | Broadcast, not a room mic | CC BY 4.0 for research, copyright with video owners [E: S23] | Tuning set for FASTDIAR [E: S5], training set for Sortformer [E: S4] |
| **CHiME-6** [S25] | Dinner-party conversation, overlapping and casual | Use one far-field channel | CC BY-SA 4.0 on OpenSLR [E: S25]; the older CHiME-5 Sheffield licence process is unclear (search summary) | About 97 GB training archive (search summary of S25) |
| **DIHARD III** [S26] | 11 domains including clinical, meeting, restaurant | Mixed | LDC licence, fee for non-members [E: S26, search summary for fee] | Not free; skip unless a lab membership covers it |
| **MSDWild** [S27] | In-the-wild multi-person video | Mixed | Not verified; a mirror says CC-BY-NC-4.0 | Check the agreement PDF before use |

None of these has AAC users, dysarthric speakers or nonverbal vocalizations in a group. The Xu et al. corpus [S19] is the
closest population match and its availability was not checked. The communicator side must therefore be tested on own
recordings. [J]

### 6.2 Metrics

- **DER**, reported with collar 0 and 0.25 s, overlap scored and excluded, per session and pooled. [J]
- **Turn attribution accuracy**: of finalized partner turns ≥ 1 s, the share whose `speaker_id` maps to the right person
  under the best one-to-one mapping for that session; reported separately for turns < 1 s. This is the number
  `ConversationState` consumes. [J]
- **Speaker-count error**: |estimated − true| per session at session end, and the share of sessions exactly right. A
  vendor blog notes that DER weights errors by seconds and can hide count errors (search summary). [J]
- **Speaker-change latency**: from a true change to the first correct provisional label, and to the settled label;
  median and 90th percentile. **New-speaker latency**: from a newcomer's first speech to their first correct voice ID. [J]
- **Phantom voices per hour**: voices with no true person, split by cause (communicator sound, TTS leak, split of a
  real person). [J]
- **Real-time factor** of the whole audio stack on the target laptop, with video running, and capture drops (the
  existing `dropped_blocks` counter). [J]

### 6.3 Split by session, always

The audio layer found that random clip splits inflated classifier scores about twofold because clips from one recording
session share acoustics (recorded for `LAYER-audio.md` §3a, which is not yet on `main`). Diarization is more
exposed to this, because thresholds such as `delta_new` and FASTDIAR's 0.4 / 0.8 are tuned to a room and a set of
voices. Rules [J]:

- Tune every threshold on dev sessions; report on held-out sessions recorded on different days, in different rooms, with
  at least some different people.
- Report per session, with the spread, not only a pooled number.
- For public corpora, use the official eval split and say which systems saw which corpus in training or tuning
  (section 2.2).

### 6.4 Own-recording protocol

- **Sessions:** 8 to 10 sessions of about 10 minutes, 3 to 5 people around one laptop, in at least three rooms (quiet room,
  kitchen with appliance noise, a room with a TV or street noise). Hold 3 sessions back as the test set, recorded on
  separate days. [J]
- **Scripted events per session:** someone joins after 2 to 3 minutes; someone leaves; one person silent for at least 2
  minutes, then speaks again; one person never on camera; at least ten one-word turns ("yeah", "what?", "no"); at least
  five interruptions; cuecom TTS speaking at least five times; a stand-in communicator producing enrolled sounds from the
  audio lab (hums, "ah") and some dysarthric-style slowed speech, labelled as a proxy, not as AAC-user data. [J]
- **Reference labels:** draft with pyannote community-1 offline [S7] with `num_speakers` set to the known count, then
  correct by hand in Audacity or ELAN labels; annotate turn boundaries, overlap, communicator sounds and TTS spans
  separately. [J]
- **Consent and storage:** written consent from everyone recorded; recordings under ignored `.scratch*` paths, never
  committed; delete on request. [J]

### 6.5 Recommended first prototype and the number that would justify it

1. `tools/bench_diarization.py`: replay WAVs (own recordings and NOTSOFAR-1 eval single-channel files) through
   FASTDIAR (`StreamingDiarizer.push`, `--device cpu` [E: S6]) and diart (default config, plus WeSpeaker ResNet34 if the
   gated `pyannote/embedding` is unwanted) behind one `SpeakerTracker` adapter each, with the masking and TTS rules of
   section 4. Score with the metrics above, per held-out session. No change to the live app. [J]
2. Measure RTF on the i7-1355U with the audio lab's voc2vec path and faster-whisper running at the same time. [J]
3. Adopt the better tracker into `apps/session.py` only if, on held-out sessions [J]:
   - finalized partner turns ≥ 1 s attributed correctly ≥ 85%;
   - speaker count exactly right in ≥ 70% of sessions, mean absolute count error ≤ 0.5;
   - settled speaker label median ≤ 1.0 s after a change;
   - zero phantom voices from cuecom TTS, and fewer than one phantom voice per 10 minutes from communicator sounds;
   - whole audio stack RTF ≤ 0.5 with video running and no capture drops.

   The anchor for "good enough" is today's behaviour: every turn is `unknown`, so any attribution that is right more
   often than it is wrong, and abstains when it is not sure, gives `pending_question` something it does not have now.
   85% is set high because a wrong attribution can make cuecom answer the wrong person. [J]

If neither tracker passes on the kitchen and TV rooms, the next step is not a bigger model but a narrower promise: track
two or three close voices and leave the rest `unknown`. [J]

## Could not verify

- **Whether diart and Sortformer were timed on the same single CPU thread as FASTDIAR** in the FASTDIAR table. The paper
  states the hardware for FASTDIAR's RTF; for the others I read only the table values.
- **diart's DER at 0.5 s latency.** The paper's latency curve (Figure 5) is an image; only 1 s, 3 s and 5 s values appear in
  the text. diart's README results table is also an image.
- **diart's latest release and maintenance status.** PyPI did not load; the "0.9.2 needs NumPy < 2" detail comes from
  WhisperLiveKit's README.
- **FASTDIAR model-weights licence** separate from the MIT code licence; and any independent reproduction (the paper is a
  month old and every number in it is the authors' own).
- **Streaming Sortformer on CPU** beyond the FASTDIAR paper's RTF 1.54 and "needs a GPU"; NVIDIA's card does not state CPU
  support either way, and NeMo-Speech.cpp's CPU performance was not checked.
- **pyannoteAI Live-1 latency, pricing and data retention.** The "sub-300ms" claim has no stated method; the benchmark blog
  has no collar.
- **"ECAPA-TDNN Lite"** from the starting leads: no primary source found. Short-segment EER for the SpeechBrain ECAPA
  checkpoint itself (the 1 s / 2 s figures are for another paper's WavLM + ECAPA baseline). ERes2NetV2 at 1 s. WeSpeaker
  ResNet34 short-segment EER and embedding dimension.
- **Non-speech vocalization handling** in the Xu et al. scoring, and the 67.8% macro-F1 speech vs nonverbal result (seen
  only in a search summary). Availability of the Xu et al. corpus.
- **Diarization on dysarthric speech**: no study found. This is a fact about my searches, not proof none exists.
- **Licences and access**: CHiME-5 Sheffield process vs OpenSLR CC BY-SA 4.0; DIHARD III fee; MSDWild agreement; NOTSOFAR
  eval disjointness (from a search summary of the challenge paper); CHiME-6 archive size.
- **The ~2x random-split inflation** in `LAYER-audio.md` §3a: passed on in the research request; that section is not on `main`
  and I did not read it.
- **Re-decode latency of faster-whisper `base.en` on the i7-1355U**, and whether echo cancellation can run on laptop
  speakers well enough for barge-in.

## Sources

- [S1] diart README (licence, gated models, tuned hyperparameters, CPU/GPU timing table): https://github.com/juanmc2005/diart
- [S2] diart `SpeakerDiarizationConfig` defaults (duration 5, step 0.5, latency = step, tau 0.6, rho 0.3, delta 1, max_speakers 20): https://github.com/juanmc2005/diart/blob/main/src/diart/blocks/diarization.py
- [S3] Coria, Bredin, Ghannay, Rosset (2021). Overlap-aware low-latency online speaker diarization based on end-to-end local segmentation. ASRU 2021. https://arxiv.org/abs/2109.06483 (full text via https://ar5iv.labs.arxiv.org/html/2109.06483)
- [S4] NVIDIA Streaming Sortformer 4spk-v2 model card (licence, params, latency configs, DER, limitations): https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2
- [S5] Torgashov, Köpüklü (2026). FASTDIAR: Frame-level speaker encoder for Streaming Diarization. arXiv:2610.02941, submitted to ICASSP 2027. https://arxiv.org/abs/2610.02941 ; https://arxiv.org/html/2610.02941v1
- [S6] microsoft/fastdiar repository (MIT, release weights, CPU flag, streaming API): https://github.com/microsoft/fastdiar
- [S7] pyannote speaker-diarization-community-1 model card (CC-BY-4.0, gated, vendor DER table): https://huggingface.co/pyannote/speaker-diarization-community-1
- [S8] pyannoteAI, Introducing Live-1 streaming diarization (vendor claims): https://www.pyannote.ai/blog/introducing-live-1-streaming-diarization
- [S9] pyannoteAI, Streaming diarization benchmark (vendor-run): https://www.pyannote.ai/blog/streaming-diarization-benchmark
- [S10] WhisperLiveKit README (Apache-2.0, backends, policies): https://github.com/QuentinFuxa/WhisperLiveKit
- [S11] Argmax authors (2025). SDBench: A Comprehensive Benchmark Suite for Speaker Diarization. Interspeech 2025. https://arxiv.org/abs/2507.16136 ; https://arxiv.org/html/2507.16136v2
- [S12] Lanzendörfer, Grötschla, Blaser, Wattenhofer (2025). Benchmarking Diarization Models. https://arxiv.org/abs/2509.26177
- [S13] SpeechBrain ECAPA-TDNN VoxCeleb model card: https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb
- [S14] 3D-Speaker toolkit (Apache-2.0; ERes2NetV2 / ECAPA / CAM++ table): https://github.com/modelscope/3D-Speaker
- [S15] Chen et al. (2024). ERes2NetV2: Boosting Short-Duration Speaker Verification Performance with Computational Efficiency. https://arxiv.org/abs/2406.02167
- [S16] Beyond Short Segments: Expanding Speaker Embeddings with Vector Archives (2026), Korea University. https://arxiv.org/html/2609.25007
- [S17] pyannote wespeaker-voxceleb-resnet34-LM model card: https://huggingface.co/pyannote/wespeaker-voxceleb-resnet34-LM
- [S18] Salim, Shahnawazuddin, Ahmad (2022). Automatic Speaker Verification System for Dysarthria Patients. Interspeech 2022. https://www.isca-archive.org/interspeech_2022/salim22_interspeech.pdf
- [S19] Xu, Huang, Feng, Shen, Tager-Flusberg, Narayanan (2024). Exploring Speech Foundation Models for Speaker Diarization in Child-Adult Dyadic Interactions. Interspeech 2024. https://arxiv.org/abs/2406.07890 ; https://arxiv.org/html/2406.07890v1
- [S20] Jones et al. (2019). How effective is LENA in detecting speech vocalizations and language produced by children and adolescents with ASD in different contexts? Autism Research 12(4):628-635. doi:10.1002/aur.2071. https://pubmed.ncbi.nlm.nih.gov/30638310/
- [S21] Silero VAD README: https://github.com/snakers4/silero-vad
- [S22] AMI Meeting Corpus licence: https://groups.inf.ed.ac.uk/ami/corpus/license.shtml
- [S23] VoxConverse repository: https://github.com/joonson/voxconverse
- [S24] NOTSOFAR dataset card: https://huggingface.co/datasets/microsoft/NOTSOFAR ; challenge paper https://arxiv.org/abs/2401.08887
- [S25] CHiME-6 on OpenSLR (SLR150): https://openslr.org/150
- [S26] Third DIHARD Challenge Development, LDC2022S12: https://catalog.ldc.upenn.edu/LDC2022S12
- [S27] MSDWild repository: https://github.com/X-LANCE/MSDWILD
- [S28] Jung et al. (2022). In search of strong embedding extractors for speaker diarisation. https://arxiv.org/abs/2210.14682
- [repo] cuecom `main` at 3a47ca9: `apps/session.py`, `cuecom/context/state.py`, `cuecom/core/interfaces.py`, `cuecom/perception/speech/transcribe.py`, `cuecom/perception/audio/events.py`, `cuecom/output/tts.py`, `tools/bench_audio.py`, `docs/LAYER-audio.md`, `requirements.txt`
