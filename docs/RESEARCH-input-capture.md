# Capturing the user's input with one webcam and one microphone, per disorder group (2026-11-01)

Read-only research for Sanjith and Abhiram. Nothing here was run on cuecom's data, and nothing here is clinical or
diagnostic advice. Tags: **[E]** stated by a listed source, **[X]** arithmetic on a cited number, **[J]** my judgment.
Refs like [C3] point to Sources at the end; [S#] refs point to the Sources of `docs/RESEARCH-speech-disorders.md`
(PR #2).

Builds on, does not redo: `docs/RESEARCH-speech-disorders.md` (13 conditions, the four design groups of its §3.2,
the 12 design implications of its §5, issues #3-#17), `RESEARCH-datasets.md` (TORGO, UASpeech, Speech Accessibility
Project, AphasiaBank, sign datasets), `RESEARCH-mapping.md` (enrollment admission rule, ReCANVo base rates),
`LAYER-audio.md` and `LAYER-video.md` (what the labs measure today).

**Scope.** Camera and microphone only: what cuecom can capture better inside video and audio, per design group. One
paragraph (§7) notes where a condition clearly needs other hardware. Partner speech and who-spoke-when are covered by
the companion diarization work and are left out here, except where the user's own voice is mistaken for noise.

## 0. Bottom line

1. **The cheapest, most certain capture fix is in the audio gate, not in a model.** People with Parkinson's used
   their voice 6.7 dB (men) to 8.11 dB (women) quieter than matched controls in daily life [E: C14]. cuecom's
   `EnergySegmenter` opens only at +9 dB over the room floor, and while it stays closed it pulls the floor toward
   whatever it hears with a time constant of about 4 s [X: 20 ms frame / 0.005 weight, from
   `cuecom/perception/audio/events.py`]. A soft voice that sits a few dB under the gate therefore raises the floor
   and makes itself harder to detect the longer the user tries. Per-user onset thresholds measured from the user's
   own softest enrolled take, and freezing the floor while near-threshold sound is present, fix this without any new
   model. [J]
2. **cuecom does not listen to the user's words at all today.** `cuecom/perception/speech/transcribe.py` is the
   partner's transcriber. For dysarthria, the group with the most residual signal, partial speech is the highest-value
   input (`RESEARCH-speech-disorders.md` §2.1), and personalized recognition is well past proof of concept:
   personalized models reached a median 4.6% word error rate on short phrases against 31% for speaker-independent
   ones across 432 speakers [E: C11], and the best 2025 challenge system reached 8.11% WER on held-out disordered
   speakers against 17.82% for Whisper-large-v2 [E: C12]. A user-speech path, with the words treated as evidence, is
   the largest missing capture channel. [J]
3. **For one- and two-signal users the right camera inputs already exist in `features.py`; what is missing is a
   switch detector, not a sensor.** MediaPipe's face landmarker already gives cuecom 52 blendshapes, eye aspect ratio
   and head angles every frame. Google's Project Gameface built a complete face-switch and head-pointer product on
   exactly these outputs, with a 500 ms hold trigger and short smoothing kernels [E: C6], and published no
   evaluation that I could find [E: C6, README]. Issue #8 (scanning mode) can be fed by a deliberate long blink, a
   brow raise or a mouth movement chosen per user, but it must be judged by false activations per hour of talking and
   rest, which no source reports for disabled users. [J]
4. **Under involuntary movement, simpler per-user thresholds beat learned temporal models in the one webcam study
   found.** In two people with dyskinetic CP using webcam head tracking, a position threshold scored AUC 0.892 and
   0.947 while hidden Markov models scored 0.657 and 0.772, and the authors called the HMM approach "unfeasible" for
   this population [E: C9]. In children with dyskinetic CP, dropping the least controllable muscles did not help, and
   the authors recommended filtering in time rather than in space [E: C10, EMG not video]. For group 3, long windows,
   per-user thresholds and effort-time negatives (#10) come before any bigger model. [J]
5. **Webcam gaze is good enough for a handful of large targets, not for a keyboard, and that matches what cuecom needs.**
   A recent webcam system reached 1.4° accuracy in typical adults, about 0.5° worse than a lab tracker [E: C2], or
   about 1.5 cm on the screen at 60 cm [X]. That is enough to choose among three options (#13) or to step a scanner (#8). It
   is not tested in Rett, late ALS or LIS from a webcam, and in Rett children found targets in under half of search
   trials even with an infrared tracker [E: C16]. [J]
6. **Visual speech is feasible as a small personal vocabulary, and the design that works mirrors cuecom's audio lab.**
   LipLearner froze a lip encoder and fine-tuned only a logistic regression on the phone, reaching 81.7% one-shot and
   98.75% five-shot accuracy on 30 user-defined commands in 16 users [E: C17]. Open-vocabulary lip reading is still
   about one word in five wrong on LRS3 with a 250-million-parameter model [E: C18]. For #15 the target is
   "enrolled mouthed phrases with a negative class", not "lip reading". [J]
7. **No public dataset matches cuecom's users and sensors.** There is no public webcam gaze, blink-switch or
   facial-gesture dataset from people with motor impairments that I could find; TORGO excludes its video [E: C21];
   dysarthric speech corpora are audio-only and gated (`RESEARCH-datasets.md` §3.3). Evaluation has to come from
   cuecom's own recorded sessions, grouped by session, as the ReCANVo result already showed (§6). [J]

## 1. What cuecom captures today

| Path | Code | What it gives | Capture assumption that matters here |
|---|---|---|---|
| Camera | `cuecom/sensors/camera.py` (`LiveCapture`) | Latest frame plus host read time; full recording | One frontal webcam; no framing or lighting check |
| Person lock | `vision/person_lock.py`, `auto_target.py`, `video.py` | One selected person crop | User is upright, separable from others |
| Face | `vision/features.py` (`face_features`) via MediaPipe Face Landmarker in `vision/session.py` | 52 blendshapes, pitch/yaw/roll, per-eye EAR, coarse iris ratio | Face visible and roughly frontal |
| Hands | `features.py` (`hand_features`), `signs.py` (DTW keyword signs) | Canned gesture scores, joint angles, enrolled signs | Purposeful hand use; hands in frame |
| Pose | `features.py`, `envision.py` | Envision gesture/move/no-gesture heads | Upper body visible, sitting |
| Events | `features.py` (`Segment`) | One event per activation: on 0.6, off 0.35, min 0.25 s, release 0.3 s | Lab defaults, not per user |
| Mic | `sensors/microphone.py`, `perception/audio/events.py` | 16 kHz segments: gate +9 dB on, +5 dB off, min 120 ms, release 260 ms; voc2vec L5 cosine templates | Room-quiet calibration second; typical loudness |
| Words | `perception/speech/transcribe.py` | faster-whisper `base.en` (or Muse) transcripts | **Partner speech only** |

[E for the values: the code at `main`, commit 3a47ca9]

## 2. Group 1, "clear mind, failing body" (ALS, LIS, Parkinson's, many adults with CP, laryngectomy)

### 2.1 What is capturable

**Soft and atypical voice.** Parkinson's hypophonia lowers the signal the gate sees. In a voice-accumulator study,
people with PD spoke 6.7 dB (men) and 8.11 dB (women) quieter than matched controls in daily life, and 3.0 to 4.1 dB
quieter in studio spontaneous speech [E: C14]. A laptop mic is also farther away than a headset: each doubling of
distance costs about 6 dB by the inverse-square law [X]. The two together can remove most of the margin a +9 dB gate
assumes. [J]

What the current gate does with a soft voice [E: code; X for the time constant]:

- It opens only when a 20 ms frame is 9 dB above `noise_db`, and closes after 260 ms below +5 dB.
- While closed, every frame updates `noise_db = 0.995 * noise_db + 0.005 * level`, a first-order average with a
  time constant of about 0.02 s / 0.005 = 4 s [X]. Sound that stays under +9 dB is averaged into the floor.
- So a user murmuring at +6 dB raises the floor toward their own voice within a few seconds, and the next attempt
  needs to be louder still. [J]
- Once open, a quiet speaker whose syllables dip below +5 dB for 260 ms is split into several short segments, and
  segments with fewer than 120 ms of active frames are dropped. [J from the code]

**Speech words.** Personalized ASR is the strongest published result in this whole area:

- Green et al. 2021: 432 people with self-reported disordered speech recorded at least 300 short phrases;
  personalized models had median WER 4.6% against 31% for speaker-independent models, and beat human transcribers by
  a median 9% (up to 80%), with the largest gains for the most severely affected speakers [E: C11].
- Tobin et al. 2022: 195 speakers; for home-automation phrases, 79% of speakers reached the target WER with 18-20
  minutes of their own speech and 63% with 3-4 minutes [E: C13].
- Speech Accessibility Project challenge 2025: speaker-disjoint splits of about 415 h from 524 participants (PD
  73.4% of training audio). Whisper-large-v2 scored 17.82% WER on the hidden test; the top team 8.11% WER and 88.44%
  semantic score; 12 of 22 teams beat the baseline on WER. Per speaker, the top team's mean WER was 9.61% for PD and
  5.05% for ALS [E: C12]. These are people able to record hundreds of prompts, so the milder end of each group [J].
- Project Relate, Google's app built on this work, asked users to record 500 phrases and did not keep learning from
  daily use, by press accounts [E: C15, press]. Tobin et al. report similar gains on conversational and unprompted
  phrases [E: C13], but all of these were recorded close to the speaker; laptop far-field audio is untested. [J]

**Face switches.** Every ALS, LIS and CP user who keeps some facial movement can use a blendshape as a switch. Project
Gameface's Windows build lets any of the 52 MediaPipe blendshapes trigger a key or click; its Android build offers
eight (open mouth, mouth left/right, roll lower lip, raise or lower each eyebrow); defaults are a 500 ms hold to
trigger, a 6-frame Hamming-weighted pointer smoother and a 10-frame blendshape smoother, with the cursor driven by
face-mesh vertex 8 between the eyebrows [E: C6, code at `Windows/configs/default/cursor.json`,
`Windows/src/utils/smoothing.py`, `BlendshapeEventTriggerConfig.java`]. The repository was archived on 5 September
2025 [E: C6]. cuecom's `features.py` already computes all 52 coefficients; the gap is a per-user switch detector with
hold time and refractory period. [J]

**Blink.** Classic LIS keeps vertical eye movement and blinking only [S18]. A deliberate blink is long: voluntary
blinks in 25 adults filmed at 600 fps took 572 ± 25 ms (mean ± s.e.) to full reopening [E: C8], while the same paper
gives about 1/3 s as a typical blink [E: C8]. Duration alone is a weak separator because a per-user voluntary blink in
a fatigued LIS user will not look like a healthy volunteer's [J]. The standard answer is a deliberate long closure
(held well past a normal blink) or a double blink, enrolled per user [J]. cuecom's per-eye EAR is the right raw
feature; the `Segment` defaults (min 0.25 s) would accept ordinary blinks as events. [J from the code]

**Head pointing.** Camera Mouse tracks a facial feature by template correlation; in its first evaluation, 9 of 12
people with severe CP or TBI used it successfully [E: C4]. In a 2024 single case with CP, Camera Mouse plus a
spelling interface gave higher intelligibility than her natural speech, while natural speech was faster [E: C5].
For jitter versus lag, the One Euro filter (cutoff rises with speed) was designed for exactly this and had less lag
than the compared filters at a reference jitter reduction [E: C7]. [J: a head pointer choosing among three large
options with dwell is a better fit for cuecom than a cursor.]

**Lips without voice (laryngectomy, voiceless ALS).** See §5; this is the group it serves.

### 2.2 Reliability from a laptop

- Personalized ASR: strong for short phrases in people who can record many prompts [E: C11, C12, C13]; unknown for
  laptop far-field audio, since these corpora were recorded close to the mouth on the speaker's own device [J].
- Face switches: no published false-activation rates for disabled users found (see Could not verify). [J]
- Blink: EAR is reliable on a frontal, well-lit face [J]; drooping lids, ptosis and partial closures in late ALS are
  untested here [J].
- Gaze: §4.1.

### 2.3 What breaks it

| Breaker | Why [J unless cited] |
|---|---|
| Hypophonia, distance | Margin under the +9 dB gate; floor creep (§2.1) [E: C14; X] |
| Medication on/off (PD) | Loudness rises "on" but decays faster [S55]; thresholds set in "on" fail in "off" |
| Fatigue | Eye-gaze tiredness was the most-reported barrier for low daily eye-tracker users in ALS (72.7%) [S10]; blink and brow switches spend the same muscles |
| Reduced spontaneous facial expression (PD) | Population blendshape thresholds under-read deliberate signals too [S54]; per-user thresholds |
| Ophthalmoparesis (late ALS) | Eye signals become ambiguous [S11]; the switch, not just the meaning, decays (#11) |
| Ventilation mask, tracheostomy, electrolarynx | Mask hides the mouth and the lower blendshapes; electrolarynx buzz is broadband energy the gate will treat as a sound |
| Glasses glare, low light | Iris and EAR noise |

### 2.4 What cuecom should change

1. **Gate per user, not per room** (`perception/audio/events.py`, `sensors/microphone.py`; #12). During enrollment,
   record each take's peak level above the floor; set `on_db` a few dB under the user's softest accepted take
   (bounded below by the measured floor noise), and store it in the profile. Freeze floor adaptation when the level is
   within a few dB of `on_db`, so a soft voice cannot raise the floor. Report the onset margin per event, and count
   "near-gate" frames per minute so a miss is visible. [J]
2. **Add a user-speech ASR path, as evidence** (`perception/speech/transcribe.py`). Same `Transcriber` protocol,
   tagged `speaker: user`, n-best kept, weighted by confidence; the words narrow candidates rather than becoming the
   message (`RESEARCH-speech-disorders.md` §2.1). Personal adaptation can come later; even an unadapted Whisper plus
   the user's confirmed phrases as a recognition prior is a start. [J] Measure with a meaning metric (did the right
   option rank first), not WER alone, as the 2025 challenge did with its semantic score [E: C12 for the metric].
3. **Per-user face-switch detector for scanning** (`vision/features.py` `Segment`, `vision/session.py`; #8, #7).
   The user (or a clinician) picks the movement; enrollment records the user's own hold time; defaults start at a
   500 ms hold as in Gameface [E: C6] and a refractory window; ordinary blinks, talking and yawning recorded as
   negatives (#10). Keep blink detection on both eyes and a single-eye option for users with asymmetric weakness. [J]
4. **Head pointer for three-option choice** (`vision/features.py` pitch/yaw). One Euro filter on yaw/pitch [E: C7],
   per-user neutral and range, dwell to select. This serves CP and PD users whose hands are unreliable and gives #13 a
   non-hand selector. [J]
5. **Confirm with the cheapest switch** (#7): in ALS the confirm signal should be whichever enrolled switch shows the
   lowest false-activation rate in that session's calibration, which may change over weeks (#11). [J]

## 3. Group 3, "deliberate movement is the problem" (apraxia, Rett, autistic dyspraxia, dyskinetic CP)

### 3.1 What is capturable

- **Head displacement and orientation**, read as a coarse direction held over a long window. [J]
- **Gaze direction to a few targets**, the predominant expressive modality in Rett [S40, S41]. [E via S40/S41]
- **Whole-body approach or withdrawal** (pose torso lean, distance to camera). [J]
- **Vocalizations as idiosyncratic signals**, enrolled from confirmed use (#9), not prompted. [J]
- **Hands: often the wrong channel.** Rett involves loss of purposeful hand use and constant stereotypies [S39];
  dyskinetic movement rises with activity [S27]. [E via S27/S39]

### 3.2 Reliability under involuntary movement

The only webcam study of head-movement AAC in dyskinetic CP found:

- Two participants with CP (one mostly choreodystonia, one mostly choreoathetosis) and four without; 640×480 webcam;
  Viola-Jones face detection, mean-shift tracking and a constant-velocity Kalman filter [E: C9].
- Per-participant AUC with CP: position threshold 0.892 and 0.947; HMM on position and velocity 0.657 and 0.772, with
  large standard deviations (up to ±0.599) [E: C9].
- Involuntary movement raised false positives and "prevented the acquisition of longer segments"; the authors judged
  the HMM approach unfeasible for this population [E: C9].
- Sample size is two, so this is a direction, not a rate [J].

From the EMG side, removing less controllable muscle synergies did not improve control in five children with
dyskinetic CP; the authors concluded that loss of control "affects all components of movement" and recommended
temporal filtering instead [E: C10]. [J: the same logic applies to landmarks: do not expect to find a "clean" subset of
keypoints; filter and integrate over time instead.]

In Rett, even with an infrared tracker, 28 girls found search targets in under 50% of trials against 80% for
controls, and took 392-574 ms longer when they did [E: C16]. Gaze-based attention measures did reach acceptable
reliability once six to nine trials were aggregated [E: C19]. Families of girls with Rett who decided against eye-gaze
systems cited the child being "too mobile" or having too many seizures [S42]. [J: aggregate several gaze looks before
treating gaze as a choice, and expect slow responses.]

### 3.3 What breaks it

| Breaker | Why |
|---|---|
| Effort-correlated movement | Dystonia and choreoathetosis are higher during activity than at rest [S27]; negatives captured at rest underestimate noise (#10) |
| Hand stereotypies (Rett) | A hand-shape or wave detector fires all day [S39] |
| Fluctuating attention (Rett) | A gaze that drifts is not a "no" [S40] |
| Seizures, breathing episodes (Rett) | Sudden movement and gaze aversion that are not messages [S39] |
| On-demand enrollment | Volitional production is the impaired act [S2, S37]; prompted takes under-measure the signal |
| Person lock | Large sudden movements trip `person_lock` "large jump" resets in `LAYER-video.md`, withholding observations [E: LAYER-video.md] |

### 3.4 What cuecom should change

1. **Per-user channel selection** (`vision/session.py`; extends the opt-in idea of #4 to all channels). A profile
   switch to turn off hand channels (Rett) or weight them down (dyskinetic CP), so stereotypies never become
   candidate events. [J]
2. **Simple, per-user, long-window detectors first** (`vision/features.py` `Segment`). Expose `on`, `off`,
   `min_duration`, `release` per signal in the profile; for this group default to longer minimum durations and a
   held-direction rule (displacement from the user's neutral beyond a per-user radius for a per-user time), which is
   what won in C9. Learned temporal models only after the threshold baseline is measured. [J]
3. **Effort-time negatives** (#10). Record "no signal" while the user reaches, vocalizes, watches the partner and is
   moved in the chair; for Rett, during stereotypies. Report false activations per hour in each condition
   separately (§6). [J]
4. **Enroll from confirmed use** (#9), and for Rett let gaze evidence accumulate across several looks within a
   choice window before it counts, with response windows of seconds, not the 0.3 s release. [J, C16 and C19 for the
   latency and aggregation]
5. **Person-lock tolerance** (`vision/person_lock.py`; Architecture follow-up 1). For a user whose movement is large
   and sudden, the "large jump clears selection" rule should be relaxed when only one person is in frame. [J]

## 4. Cross-group camera techniques

### 4.1 Webcam gaze

- Kaduk et al. 2024 recorded a webcam system (Labvanced) simultaneously with an EyeLink 1000 in typical adults:
  webcam accuracy 1.4°, precision 1.1°, about 0.5° worse than the EyeLink; 1.3° for central targets [E: C2].
- At a 60 cm viewing distance, 1.4° is about 1.5 cm on screen [X: 600 mm × tan 1.4°]. Three to four large targets on
  a laptop screen are well within that; a full on-screen keyboard is not [J].
- cuecom's current `*_iris_ratio` is a raw position of the iris between the eye corners, not a calibrated gaze
  estimate [E: code]. Coarse left/centre/right and up/down regions need a per-session calibration of that ratio
  against head pose [J].
- Dwell is the standard selection method; Majaranta et al. state that "a thousand milliseconds is usually long enough
  to prevent false selections" and that 700 ms or less suffices for simple tasks, while long dwell is uncomfortable
  [E: C20]. The underlying "Midas touch" problem (everything looked at gets selected) is Jacob's [E: C20 citing
  Jacob 1991].
- No study of webcam gaze in ALS, LIS or Rett with accuracy figures was verified (Could not verify). [J]

### 4.2 Camera placement and framing (wheelchair, lying down)

No primary source on webcam framing for AAC users was found; the following is [J], from how the models used by cuecom
behave.

- **Face size.** Face landmarks and iris need the face to fill a reasonable share of the frame; a laptop on a table in
  front of a wheelchair user with a tray, or on a stand beside a bed, often puts the face small and off-axis. The
  BlazeFace model card reportedly treats faces smaller than 20% of the image side and distances beyond 2 m as out of
  scope (not verified from the official card; see Could not verify).
- **Lying down.** The face appears rotated by up to 90° in the image. Rotating the frame by the user's known
  orientation before inference (a profile setting: camera roll 0°/90°/270°) is cheap and keeps the detectors in the
  upright range they were trained on. Pose-based channels (Envision, torso lean) assume sitting and should be off for
  a lying user.
- **Mounting.** Wheelchair users move with the chair; a camera fixed to the chair keeps framing stable, one on a
  desk does not. Above-eye-level placement hides the eyes under the lids, which hurts EAR and vertical gaze.
- **Lighting.** Backlight from a window behind the user is the common failure; face-lit, even light matters more
  than camera resolution.
- **Session-start check** (`sensors/camera.py`, `vision/session.py`; #12): measure face box size, roll, mean face
  luminance, and achieved inference fps, write them to the trace, and refuse to start calibration when they are out
  of range, telling the partner what to move. This is cheap and turns silent failures into instructions.

### 4.3 Mouth movement as a voice-activity cue

A mic segment that coincides with the user's lips moving is more likely the user's; one that does not is more
likely the partner or the room. `jawOpen` and other mouth blendshapes are already computed. This is a capture aid for
quiet voices (§2) and a weak attribution cue; full attribution belongs to the diarization work. [J]

## 5. Visual speech for voiceless users (laryngectomy, voiceless ALS, some dysarthria)

- **Open vocabulary is not ready for this use.** Auto-AVSR, a strong public lip-reading system, reached 19.1% WER
  visual-only on LRS3 and 14.6% on LRS2, with a 250.4M-parameter model trained on 3,448 hours [E: C18]. No inference
  cost was reported [E: C18]; [J] a model of that size is a poor fit for cuecom's CPU budget next to MediaPipe, where
  the face model alone took a median 121.7 ms per frame on this laptop [E: LAYER-video.md].
- **Small personal vocabularies are.** LipLearner (CHI 2023) cropped the mouth to an 88×88 grayscale region, encoded
  it with a frozen contrastively trained encoder into a 500-d embedding, and fine-tuned only a logistic regression on
  the phone [E: C17]:
  - 16 users, 30 commands (10 predefined, 20 the users' own, in several languages): 81.7% one-shot, 96.04% three-shot,
    98.75% five-shot [E: C17].
  - About 422 ms per recognition on an iPhone 13 Pro; model update about 2.2 s [E: C17].
  - Cross-lighting three-shot F1 0.939, cross-posture 0.960 [E: C17].
  - Mouth-opening triggers misfired when users talked to others or smiled; the system learned from reported
    misactivations, and its false-positive rate fell from 0.26% to 0.07% after about seven reports [E: C17; the unit of
    that rate was not checked].
  - Participants were experienced voice-assistant users; speech impairment was not reported [E: C17].
- **Fit with cuecom** [J]: this is the same shape as `perception/audio/events.py` (frozen encoder, per-user templates,
  explicit negative classes, cosine thresholds). A prototype for #15 behind `FrameObserver` would: crop the mouth from
  the existing face landmarks, embed with a frozen encoder, match against enrolled mouthed phrases plus negatives
  (talking to the partner, smiling, yawning, chewing), and emit one event per phrase. The encoder's training data and
  licence decide whether it can ship (Could not verify).
- **Group caveats** [J]: in laryngectomy, articulation and language are intact [S8], so this is the best-matched group;
  in voiceless ALS, oral weakness reduces lip movement and the vocabulary will drift (#11); a tracheostomy tie, mask
  or beard occludes the region.

## 6. Group 2, "the words are the problem" (aphasia, PPA, CAS with language disorder, Down syndrome)

Capture is not the bottleneck here [J]. Language damage reaches every modality (`RESEARCH-speech-disorders.md` §1),
so a better gesture detector does not supply missing words. What capture can do:

- **Recognize choices, not productions.** Pointing (index-finger direction from `hand_features`), head turn or gaze
  toward one of three pictured options (#13) are recognition acts; the webcam techniques of §4 serve them. [J]
- **Keep partial speech and gesture together.** An approximate word plus a gesture plus partner context narrows
  candidates better than any one alone. The user-speech path of §2.4 item 2 helps here too, with the caveat that ASR
  words in aphasia can be automatisms or substitutions [S50] and should be down-weighted until the user's own patterns
  are known (#6). [J]
- **Down syndrome:** speech known to family but not strangers [S45] is a personalized-recognition problem like
  dysarthria; hearing loss in about a quarter [S46] means options must be visual too (#13). [J]
- **Neglect and hemiparesis after stroke** [S51, S4]: the camera may see only the unaffected side's gestures;
  per-user channel selection (§3.4 item 1) covers this. [J]

Group 4 ("speech exists but is gated or atypical": stuttering, selective mutism, mild dysarthria, voice disorders) is
served by the audio-gate and user-speech changes in §2.4 and needs no separate capture work [J]; for stuttering,
secondary head nods and blinks [S6] are exactly the negatives the face-switch detector must reject.

## 7. Where camera and microphone are not enough

[J] Total locked-in state leaves no eye movement [S18, S16]; no camera or microphone method applies, and BCI is the
only route discussed in the literature. Late ALS with ophthalmoparesis [S11, S13] and people who cannot be framed
reliably (severe seizures, constant large movement) will be better served by a mechanical or proximity switch, which
cuecom could accept as just another `Event` source. A gaze keyboard at typing accuracy needs an infrared tracker, not
a webcam (§4.1). None of these is in scope here.

## 8. Comparison table

Reliability is my rating from laptop webcam and mic [J], with sources where a cell cites one. Groups as in
`RESEARCH-speech-disorders.md` §3.2: 1 clear mind/failing body, 2 words are the problem, 3 deliberate movement is the
problem, 4 speech gated/atypical.

| Signal | Main groups | Reliability from laptop | Main failure modes | Evidence |
|---|---|---|---|---|
| Vocalization (energy gate + voc2vec) | 1, 3, 4 | Medium for loud sounds; **low for hypophonic voices with current gate** | Gate margin, floor creep, distance, medication cycle, electrolarynx buzz | C14; code; LAYER-audio §3a |
| User speech words (ASR) | 1, 4, 2 | High after personalization for short phrases in milder speakers; low unadapted for severe | Far-field audio, conversational speech, aphasic substitutions | C11, C12, C13 |
| Deliberate long blink | 1 (LIS, ALS) | Medium-high on frontal lit face | Ordinary blinks, fatigue, ptosis, glasses | C8 |
| Brow / mouth blendshape switch | 1, 4 | Medium; unknown false-activation rate | Talking, smiling, yawning; reduced expression in PD; mask | C6; S54 |
| Head-pose pointing / direction | 1, 3 | Medium-high with smoothing for tremor; medium with per-user threshold in dyskinetic CP | Involuntary bursts, posture shifts, person-lock resets | C4, C5, C7, C9 |
| Webcam gaze regions (2-4 targets) | 1, 3 (Rett), 2 | Medium for large targets in typical users; untested in target groups | Calibration drift, head movement, attention fluctuation, fatigue, low light | C2, C16, C19, C20 |
| Hand shapes / keyword signs | 2, 4, some 1 | Medium-high when hand use is purposeful | Stereotypies (Rett), dyskinesia, hemiparesis | S27, S39 |
| Whole-body approach / lean | 3 | Low-medium | Chair movement, seizures, lying down | [J] |
| Mouthed phrases (visual speech) | 1 (laryngectomy, voiceless ALS) | Medium-high for small personal vocabularies in typical users; untested in target groups | Talking/smiling misfires, occlusion, oral weakness | C17, C18 |

## 9. Ranked recommendations

Ranked by value for cost [J]. Each maps to modules and to existing issues where they overlap.

| # | Change | Modules | Issues | Groups | Why first |
|---|---|---|---|---|---|
| 1 | Per-user audio gate: onset from the user's softest take, freeze floor near threshold, log onset margin and near-gate frames | `perception/audio/events.py`, `sensors/microphone.py` | #12 | 1, 4 | Removes a silent failure for PD users with no model change [E: C14; X] |
| 2 | Session-start capture check: face size, roll, luminance, fps, mic floor and test-utterance margin, written to the trace | `sensors/camera.py`, `vision/session.py`, `sensors/microphone.py` | #12 | All | Turns framing and loudness failures into instructions |
| 3 | Per-user face-switch detector (blink / brow / mouth) with hold time, refractory, and talking/blink negatives; feeds scanning | `vision/features.py` (`Segment`), `vision/session.py` | #8, #7, #10 | 1 | Makes one-signal users possible with features already computed [E: C6] |
| 4 | Per-user signal parameters and channel selection (thresholds, min duration, release, hands off) | `vision/features.py`, `vision/session.py` | #4, #10 | 3, 2 | Simple thresholds beat HMMs under dyskinesia [E: C9] |
| 5 | Effort-time and stereotypy negatives, reported per condition | `vision/signs.py` (`NO_SIGN`), `perception/audio/events.py` (`NEGATIVES`) | #10 | 3 | Noise rises with effort [S27] |
| 6 | User-speech ASR as evidence, n-best kept, meaning-level metric | `perception/speech/transcribe.py` | new; relates to #9 | 1, 4, 2 | Largest missing channel [E: C11, C12] |
| 7 | Head pointer with One Euro filter and dwell for three-option choice | `vision/features.py` | #13, #7 | 1, 3 | Non-hand selector for #13 [E: C7] |
| 8 | Calibrated coarse gaze regions with long, aggregated dwell for Rett | `vision/features.py` | #8, #13 | 3, 1 | Gaze is Rett's main channel [S40]; slow, unreliable per look [E: C16, C19] |
| 9 | Orientation setting (rotate frames for lying users; pose channels off) | `sensors/camera.py`, `vision/session.py` | #12 | 1 | Cheap; keeps detectors in their trained range [J] |
| 10 | Mouthed-phrase channel on the LipLearner pattern | new `FrameObserver` under `perception/vision/` | #15 | 1 | Feasible small-vocabulary design [E: C17] |

Signal health (#11) applies to every row: each detector's onset margin, false activations and confirm/reject history
are the inputs it needs. The simulator (#17) should add a hypophonia scenario (voice at +4 to +8 dB over the floor,
drifting with a medication cycle) and an effort-correlated movement scenario.

## 10. How capture should be evaluated, per group

### 10.1 Rules for all groups

1. **Split by session, never by clip.** In cuecom's own ReCANVo run, within-person UAR fell from about .44-.49 with
   random clips to about .24-.27 when folds were grouped by recording, because clips from one recording share room and
   microphone acoustics [E: `LAYER-audio.md` §3a on branch `eval/recanvo-grouped`, not yet on `main`]. The same applies
   to video: enrollment and test from one sitting share lighting, framing and posture. Enroll in one session, test in
   another. [J]
2. **False activations per hour, in separate conditions**: idle rest, ordinary talking (user and partner), effort
   (reaching, being moved, eating), and for group 3 stereotypies and dyskinetic bursts. A single pooled number hides
   the condition that matters. The audio lab's zero false events in four minutes of synthetic speech
   (`LAYER-audio.md` §3) is an example of a result that is not yet an hourly rate. [J]
3. **Misses per attempt**, with the attempt marked by the operator key in the labs, not inferred. [J]
4. **Fatigue over a session**: hit rate, onset margin (audio) and activation peak (video) in successive thirds of a
   20-30 minute session; and between morning and evening, or medication on/off where relevant. [J; the ALS eye-gaze
   tiredness finding S10 is the reason]
5. **Time to select** and **confirm cost** (actions per committed message), for #7. [J]
6. **Report per user**, with the number of sessions, not pooled across users; most of these signals are personal. [J]

### 10.2 Per group

| Group | Primary capture metrics | Conditions that must be included |
|---|---|---|
| 1 Clear mind, failing body | Switch false activations/hour while talking and at rest; misses per attempt; onset margin for soft voice; ASR meaning accuracy | Start vs end of session; PD medication on/off; mask/trach if present; lying vs sitting |
| 2 Words are the problem | Correct option chosen among three by point/gaze/head; ASR-word usefulness after down-weighting | Partner speaking at the same time; hemiparesis side |
| 3 Deliberate movement | False activations/hour during effort and stereotypies; hit rate on confirmed-use examples vs prompted takes (#9) | Effort, stereotypies, chair movement, seizures excluded and logged |
| 4 Gated/atypical speech | Gate misses; ASR on the user's speech; nod/blink rejection during dysfluency | Situational speech differences |

### 10.3 Public datasets and what they can test

| Dataset | What it has | Licence / access | Use for capture evaluation |
|---|---|---|---|
| MPIIGaze | 213,659 images of 15 people from their own laptop cameras over three months [E: C22] | CC BY-NC-SA 4.0, non-commercial scientific use only [E: C22] | Webcam gaze calibration and drift on typical users; not disabled users |
| TORGO | Audio (array mic at 61 cm and head-mounted) + EMA from speakers with CP or ALS; **video excluded** [E: C21] | Free for academic non-profit use [E: C21] | Far-field vs close-mic dysarthric speech; gate and ASR tests |
| UASpeech | Isolated-word audio, CP dysarthria; recorded under an audiovisual project title but no video release found [E: C23] | Request; academic and government labs only; no commercial use or redistribution [E: C23] | ASR on severe dysarthria |
| Speech Accessibility Project | ~415 h, 524 participants in the challenge release; PD, ALS, CP, DS, stroke; speaker-disjoint splits [E: C12] | DUA and proposal (`RESEARCH-datasets.md` §3.3) | User-speech ASR; personalization curves |
| LRW / LRS2 | BBC broadcast lip-reading video | Non-commercial research under a BBC agreement, per a secondary source [E: C24, secondary] | Lip encoder pretraining only |
| LRS3 | TED lip-reading video | Licence statements conflict (Could not verify) | Same |
| CNVVE, ReCANVo | Nonverbal vocalizations | See `LAYER-audio.md`, `RESEARCH-mapping.md` | Gate and vocalization tests; session-grouped only |
| AphasiaBank | Video of aphasic discourse | CC BY-NC-SA via TalkBank (`RESEARCH-datasets.md` §3.1) | Speech-plus-gesture co-occurrence in aphasia |

Not found: any public webcam dataset of facial-gesture switches, blink switches, head pointing or gaze from people
with ALS, LIS, CP or Rett. cuecom's own recorded lab sessions, labelled with the operator keys and grouped by session,
are the evaluation set. [J]

## Could not verify

- **"Beyond Accuracy: Auditing Allocative Harms in Facial-Gesture Recognition for People with Motor Impairments"**
  (CHI 2026, doi:10.1145/3772318.3791927) compares MediaPipe Face Mesh with OpenFace 3.0 for motor-impaired users per
  a search summary; the ACM page returned 403. It is the most relevant missing source for face-switch reliability.
- **False-activation rates of blendshape or blink switches in disabled users**: none found.
- **Webcam gaze in disabled users.** A small study (ICoRD 2019, three children with severe speech and motor
  impairment) comparing webcam and infrared trackers was seen only through a search summary. No webcam gaze study in
  ALS, LIS or Rett with accuracy figures was read.
- **Rett calibration rate**: an 80% (35 of 44) eye-tracker calibration figure attributed to Djukic et al. 2012 was
  seen only in a search summary.
- **BlazeFace model card limits** (faces under 20% of the image side and beyond 2 m out of scope; head-orientation
  limits) were seen only on a third-party mirror; the official PDF did not extract here.
- **Fox and Ramig 1997** (PD 2-4 dB SPL lower at 30 cm) was seen only through a search summary; C14 is used instead.
- **ASR on tracheoesophageal and electrolaryngeal speech**: a 36.9% ± 18.0% word accuracy figure for post-laryngectomy
  speech was seen only in a search summary.
- **LipLearner encoder**: its pretraining data and licence, and whether the trained encoder is released, were not
  checked; the unit of the reported false-positive rate was not checked.
- **LRS3 licence** (CC BY 4.0 vs CC BY-NC-ND 4.0 in different listings) and the BBC terms for LRW/LRS2 from the BBC
  itself.
- **GazeCapture** terms: the project site refused the connection.
- **Project Relate's current status** (invitation, platforms) beyond 2021-2022 press reports.
- **Windows microphone processing** (noise suppression, automatic gain) suppressing soft voice or non-speech
  vocalizations on this laptop: plausible, not checked.
- **Vertical vs horizontal webcam gaze accuracy** (relevant to classic LIS, which keeps vertical movement): no source
  read.

## Sources

Webcam gaze, head pointing, face switches, blink
- [C2] Kaduk T, Goeke C, Finger H, König P (2024). Webcam eye tracking close to laboratory standards: comparing a new webcam-based system and the EyeLink 1000. Behav Res Methods. doi:10.3758/s13428-023-02237-8 (PMC11289017)
- [C4] Betke M, Gips J, Fleming P (2002). The Camera Mouse: visual tracking of body features to provide computer access for people with severe disabilities. IEEE Trans Neural Syst Rehabil Eng. doi:10.1109/tnsre.2002.1021581
- [C5] MacLellan LE et al. (2024). Evaluating Camera Mouse as a computer access system for AAC in cerebral palsy: a case study. Assist Technol. doi:10.1080/10400435.2023.2242893 (PMC10927611)
- [C6] Google. Project Gameface (repository, archived 5 Sep 2025; Apache-2.0). https://github.com/google/project-gameface ; files read: `Windows/configs/default/cursor.json`, `Windows/src/shape_list.py`, `Windows/src/utils/smoothing.py`, `Windows/src/detectors/facemesh.py`, `Android/.../BlendshapeEventTriggerConfig.java`
- [C7] Casiez G, Roussel N, Vogel D (2012). 1€ filter: a simple speed-based low-pass filter for noisy input in interactive systems. CHI '12. doi:10.1145/2207676.2208639
- [C8] Kwon et al. (2013). High-speed camera characterization of voluntary eye blinking kinematics. J R Soc Interface 10:20130227. doi:10.1098/rsif.2013.0227 (PMC4043155)
- [C20] Majaranta P, MacKenzie IS, Aula A, Räihä KJ (2006). Effects of feedback and dwell time on eye typing speed and accuracy. Univ Access Inf Soc 5:199-208. https://www.yorku.ca/mack/uais2006.html ; cites Jacob RJK (1991), ACM Trans Inf Syst 9(2):152-169

Involuntary movement, Rett
- [C9] Gonçalves CWP, Richa RA, Bo APL (2022). Tracking and classification of head movement for augmentative and alternative communication systems. Sensors 22(2):435. doi:10.3390/s22020435 (PMC8780700)
- [C10] Borish CN et al. (2021). Can spatial filtering separate voluntary and involuntary components in children with dyskinetic cerebral palsy? PLoS One 16(4):e0250001. doi:10.1371/journal.pone.0250001 (PMC8046213)
- [C16] Rose SA, Wass S, Jankowski JJ, Feldman JF, Djukic A (2019). Impaired visual search in children with Rett syndrome. Pediatr Neurol. doi:10.1016/j.pediatrneurol.2018.10.002 (PMC6397679)
- [C19] Rose SA, Wass SV, Jankowski JJ, Djukic A (2021). Measures of attention in Rett syndrome: internal consistency reliability. Neuropsychology. doi:10.1037/neu0000744

Voice and speech recognition
- [C11] Green JR et al. (2021). Automatic speech recognition of disordered speech: personalized models outperforming human listeners on short phrases. Interspeech 2021. https://www.isca-archive.org/interspeech_2021/green21_interspeech.html
- [C12] Zheng et al. (2025). The Interspeech 2025 Speech Accessibility Project Challenge. arXiv:2507.22047
- [C13] Tobin J, Tomanek K (2022). Personalized automatic speech recognition trained on small disordered speech datasets. ICASSP 2022. arXiv:2110.04612
- [C14] Körner Gustafsson J, Södersten M, Ternström S, Schalling E (2019). Voice use in daily life studied with a portable voice accumulator in individuals with Parkinson's disease and matched healthy controls. J Speech Lang Hear Res. PMID 31830844
- [C15] Press coverage of Project Relate (2021): 9to5Google, https://9to5google.com/2021/11/09/google-project-relate-app/ ; The Batch, https://www.deeplearning.ai/the-batch/project-relate

Visual speech
- [C17] Su Z, Fang S, Rekimoto J (2023). LipLearner: customizable silent speech interactions on mobile devices. CHI '23. doi:10.1145/3544548.3581465 (arXiv:2302.05907)
- [C18] Ma P et al. (2023). Auto-AVSR: audio-visual speech recognition with automatic labels. ICASSP 2023. arXiv:2303.14307

Datasets
- [C21] TORGO database. https://www.cs.toronto.edu/~complingweb/data/TORGO/torgo.html
- [C22] MPIIGaze. https://www.mpi-inf.mpg.de/departments/computer-vision-and-machine-learning/research/gaze-based-human-computer-interaction/appearance-based-gaze-estimation-in-the-wild
- [C23] UA-Speech. https://speechtechnology.web.illinois.edu/uaspeech/
- [C24] Wav2Lip evaluation filelists README (states LRS2/LRW filelists are BBC copyright, non-commercial research under BBC agreement). https://huggingface.co/spaces/pragnakalp/Wav2lip-ZeroGPU/blob/main/evaluation/test_filelists/README.md

cuecom internal
- `cuecom/perception/audio/events.py`, `cuecom/perception/vision/features.py`, `cuecom/perception/speech/transcribe.py`, `cuecom/sensors/camera.py`, `cuecom/sensors/microphone.py` at commit 3a47ca9
- `docs/LAYER-audio.md` (§3, §4; §3a on branch `eval/recanvo-grouped`), `docs/LAYER-video.md`, `docs/RESEARCH-speech-disorders.md` (PR #2)
