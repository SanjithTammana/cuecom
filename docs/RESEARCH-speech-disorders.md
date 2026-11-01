# Who cuecom is for: speech, voice and language disorders in depth (2026-11-01)

Read-only research for Sanjith and Abhiram. Nothing here was run on cuecom's data, and nothing here is clinical or
diagnostic advice. Tags: **[E]** stated by a listed source, **[X]** arithmetic on a cited number, **[J]** my judgment.
Refs like [S3] point to Sources. First-person accounts are labelled *testimony* and are never used as rates.

Builds on, does not redo: `RESEARCH-mapping.md` (communication dictionaries, AllyAAC, ReCANVo base rates, Triple C),
`RESEARCH-datasets.md` (TORGO, UASpeech, Speech Accessibility Project, AphasiaBank access), `RESEARCH-interpretation.md`
(LLM as wording layer, agency risks) and `RESEARCH-bayes-gap.md`.

## 0. Bottom line

1. **"Speech disorder" is four different breakdowns, and each leaves different signals intact.** Language (aphasia),
   motor planning (apraxia), motor execution (dysarthria) and the sound source (voice, laryngectomy) fail in different
   places between an intention and a sound. A gesture survives a voice disorder, often survives dysarthria, may fail
   with apraxia, and may carry no more meaning than speech in severe aphasia. cuecom's "the user defines the signals"
   principle is right because the usable channel depends on *where* the chain broke, not on the diagnosis label. [J]
2. **The hardest moment for many of these users is cuecom's enrollment step.** Apraxia is defined partly by
   automatic actions being easier than deliberate ones [E: S2], dyspraxia in autism extends to gestures on command
   [E: S37], and Rett involves loss of purposeful hand use [E: S39]. "Perform your signal five times now" asks for
   exactly the volitional, on-demand movement these conditions impair. Signals should also be harvested from
   confirmed real use, which `MotifLearner` already supports in principle. [J]
3. **For some users, trying harder makes the noise worse.** In dyskinetic cerebral palsy, dystonia and
   choreoathetosis are both higher during activity than at rest [E: S27]. The involuntary movement is correlated with
   the attempt to signal, so it cannot be treated as independent background noise. [J]
4. **The confirm step is itself a communication act and costs the same scarce channel.** In locked-in syndrome eye
   movements "may be inconsistent, very small, and easily exhausted" [E: S19]; in ALS, eye-gaze tiredness was the
   most-reported barrier among low daily users of eye-tracking (72.7%) [E: S10]. Every confirmation spends the signal
   the user has least of. Confirmation design is a budget problem, not a UI detail. [J]
5. **Authorship is the risk that history has already demonstrated.** Facilitated communication produced messages that
   came from the facilitator, and in controlled experiments people answering "through" someone else used their own
   knowledge while attributing the answers to the other person [E: S62, S63]. ASHA says messages produced through
   the Rapid Prompting Method "should not be assumed to be the communication of the person" [E: S9]. A cuecom confirm
   key that a partner can press reproduces this failure. [J]
6. **Slow and right beats fast and wrong, by the partner's own judgement.** Typical AAC output is 8 to 10 words per
   minute for direct selection and about 1.7 for switch scanning, against 120 to 185 for conversation [E: S69].
   Unfamiliar partners nonetheless rated slowly delivered relevant messages higher than quickly delivered,
   partly relevant ones [E: S67, S68]. That is direct support for abstain-then-confirm. [J]
7. **Familiar partners understand far more than strangers, and that gap is what cuecom can carry.** Listener
   familiarization raises dysarthric intelligibility [E: S28, S29]; parent and professional agree on a child's
   communication level at only 0.49 [E: S26]. A per-user model is a portable "familiar listener" for the stranger at
   the pharmacy. [J]
8. **Many of the people who most need cuecom also have vision, hearing, attention or comprehension limits that affect
   the confirm screen.** One in 10 children with CP is blind and 1 in 25 deaf [E: S23]; about a quarter of children with
   Down syndrome have permanent hearing loss [E: S46]; hemispatial neglect affects 43% of right-hemisphere and 20% of
   left-hemisphere acute strokes [E: S51]. Options shown on one side of a screen, or only read aloud, will be missed by
   some users. [J]
9. **Progressive conditions need a signal-retirement plan.** In bulbar-onset ALS, speech intelligibility typically
   falls below 90% within 18 to 24 months of onset [E: S10, a review], and late in invasively ventilated ALS, eye
   signals pass through a "communicative ambiguity" phase where they persist but can no longer be reliably attributed
   to intention [E: S11]. A system that learns signals must also detect when a signal is decaying. [J]

## 1. A frame for reading the rest

Speech from intent to sound passes through layers. Where it breaks predicts what survives. [J, built from the ASHA
definitions in S1-S4, S7]

| Layer | What it does | Disorder (examples) | Typically spared, often usable | Typically lost or unreliable |
|---|---|---|---|---|
| Intent and cognition | Wanting to say something, knowing the topic | Severe intellectual disability, late-stage dementia, disorders of consciousness | Affect, preferences, presence/absence of distress | Abstract or future reference |
| Language | Choosing words and grammar; understanding them | Aphasia, PPA, developmental language disorder | Often: gesture, intonation, facial affect, automatic phrases | Words in any modality: speech, writing, signing, reading |
| Motor planning | Sequencing the movements | Apraxia of speech (AOS), CAS, limb apraxia | Automatic and emotional actions; comprehension | Deliberate, on-demand, novel movements |
| Motor execution | Muscles doing it | Dysarthria (CP, ALS, PD, stroke, MS), LIS | Language; sometimes gesture, eye movement | Intelligibility, rate, loudness; with LIS nearly all movement |
| Sound source | Making voice | Voice disorders, laryngectomy, spasmodic dysphonia | Language, articulation, gesture, mouthing | Voice quality, loudness, or voice itself |
| Fluency and social gating | Getting speech out in context | Stuttering, selective mutism | Language, gesture, writing; speech in safe contexts | Speech in specific situations |

Two consequences for cuecom [J]:
- **Language damage reaches every modality.** cuecom does not get around aphasia by moving from speech to gesture,
  because gestures that carry meaning draw on overlapping systems (section 2.3). Motor and source damage, by contrast,
  can often be bypassed.
- **Planning damage is the odd one.** The person knows what to say and the muscles work, but deliberate production
  fails while automatic production may succeed. This inverts the usual assumption that a deliberate, rehearsed
  signal is more reliable than a spontaneous one.

## 2. Per-condition reports

Each section: mechanism; how communication is affected; variability and fatigue; progression; co-occurring factors;
signals that remain usable; what it implies for cuecom.

### 2.1 Dysarthria (all subtypes)

**Mechanism.** A group of neurogenic speech disorders from sensorimotor problems: weakness or paralysis,
incoordination, involuntary movements, or abnormal muscle tone [E: S1]. ASHA's classification by lesion site [E: S1]:

| Type | Lesion site [E: S1] | Characteristic sound (Mayo system) [J, see Could not verify] |
|---|---|---|
| Flaccid | Lower motor neurons and motor units | Breathy, hypernasal, weak consonants, short phrases |
| Spastic | Bilateral upper motor neurons | Slow, effortful, strained-strangled voice |
| Ataxic | Cerebellar control circuit | Irregular articulatory breakdowns, equalised stress, "drunken" quality |
| Hypokinetic | Basal ganglia | Quiet, monopitch, fast short rushes (Parkinson's) |
| Hyperkinetic | Basal ganglia | Unpredictable interruptions from involuntary movement (Huntington's, dystonia) |
| Unilateral UMN | One-sided upper motor neurons | Usually milder imprecision (stroke) |
| Mixed | Combinations | ALS is classically flaccid-spastic |

**Causes and how common it is.** Congenital (cerebral palsy), degenerative (ALS, Parkinson's, Huntington's, MSA),
demyelinating (MS), infectious, neoplastic, toxic, traumatic and vascular [E: S1]. Reported prevalence within
conditions [E: S1]: Huntington's 78-93%, Parkinson's 44-88%, MS 40-51%, acute stroke 22-58%, acute-subacute TBI
30-86%, neuromuscular disease 26-62%. The ranges are wide because they depend on severity, lesion and measurement
[E: S1].

**How communication is affected.** Intelligibility (percent of words a listener gets), comprehensibility (with context:
topic, gesture, face) and efficiency (intelligible words per minute) are measured separately [E: S1]. ASHA notes that
severity does not determine disability; functional impact depends on communication needs and comprehensibility in
important contexts [E: S1]. Standard supplementation strategies are alphabet-based (point to first letter while
speaking), topic-based (show topic first) and gestural [E: S1].

**Variability and fatigue.** ASHA lists effort varying "when fatigued", by time of day and by medication schedule, and
adaptability varying with noise, multiple partners and unfamiliar listeners [E: S1]. In Parkinson's, levodopa
"on" states produced louder, faster speech but also faster loudness decay, with pitch and articulation unchanged
[E: S55]; in other words medication changes the signal, not just its quality.

**Listener effects.** Brief familiarization with a speaker's phrases raised intelligibility for hypokinetic and
ataxic dysarthria [E: S29]; for CP dysarthria, intelligibility rose over four familiarization trials, and adding
video helped only one of five speakers (the most severe) [E: S28].

**Progression.** Depends entirely on the cause: static in CP, progressive in ALS, PD, HD, MSA; recovering in stroke
and TBI [E: S1]. ASHA recommends introducing AAC and voice banking "as early as possible" in progressive disease
[E: S1].

**Usable signals.** Language is intact unless something else is damaged, so partial speech carries real lexical
content [E: S1 for language being a separate system; J for use]. Gestures survive when the limbs are less affected
than the bulbar muscles, which is common in bulbar-onset disease and the reverse in limb-onset [J].

**Implications for cuecom.** [J]
- Partial speech is a high-value signal here, and the right input for the existing faster-whisper path, but a
  generic recognizer degrades badly on atypical speech (section 3.4). Treat ASR words as evidence with a confidence
  weight, not as the message. Alphabet- and topic-supplementation map naturally onto cuecom: a gesture or first
  letter narrows the candidate set and speech fills it in.
- Expect the user's own voice templates to drift with medication timing and fatigue. Per-session recalibration of
  the vocalization detector matters more than a larger initial enrollment.
- Hyperkinetic users produce involuntary movement that looks like signal. The "none" class must be trained on
  their own movement at rest *and* during effort (see 2.4).

### 2.2 Apraxia of speech: acquired (AOS) and childhood (CAS)

**Mechanism.** Impaired planning or programming of the movements for speech; muscle strength and tone are normal
[E: S2, S3].

**Acquired AOS.** Core features: distortions, slow rate with unintended pauses, equalised stress, syllables
collapsing together, inconsistent errors, visible groping, and accuracy dropping as utterances get longer [E: S2].
Crucially, "automatic speech (e.g., counting) is often easier than generative language" [E: S2]. Usually from stroke,
TBI, tumour or surgery; 44% of people with chronic aphasia are estimated to have some AOS, and in one acute-stroke
chart review 11% had AOS, all of them with aphasia [E: S2]. Pure AOS is rare: 5 confirmed cases at Mayo in 14 years
[E: S2]. A progressive form (primary progressive AOS) is most often tied to corticobasal degeneration and progressive
supranuclear palsy [E: S2, S71].

**CAS.** Three consensus features: inconsistent errors on repeated productions, disrupted transitions between sounds
and syllables, and inappropriate prosody [E: S3]. About 1 in 1,000 children aged 4-8 [E: S3]. Over 95% also have an
expressive language disorder; motor coordination delays, limb and oral apraxia and literacy problems are common;
more than 30 genes account for about a third of cases [E: S3]. Children do not "grow out" of it [E: S3]. Higher
rates are reported in Down syndrome, 22q11.2 deletion, galactosemia and FOXP2 disruption [E: S3].

**Variability.** Inconsistency is part of the definition [E: S2, S3]. The same target comes out differently on
repeated attempts.

**Co-occurring.** Limb apraxia often travels with aphasia after left-hemisphere stroke: in one 50-patient sample half
had both, 24% had aphasia without apraxia, and 4% had apraxia without aphasia [E: S49].

**Usable signals.** Automatic and emotional vocalizations and gestures; comprehension (often); pointing and choosing
from options more easily than producing [J, from S2's automatic/volitional dissociation].

**Implications for cuecom.** [J]
- **Enrollment is the weak point.** A protocol that prompts "make your HELP sign now" measures exactly the deliberate
  production these users find hardest. Low enrollment hit rates under `RESEARCH-mapping.md` section 3.3's admission
  rule would wrongly reject signals the person uses fine in the moment. Prefer passive enrollment from confirmed use
  for these users, and treat prompted trials as a lower bound.
- Inconsistency is by definition, so a template learned from five trials will have high within-signal variance. Use
  wide per-user tolerances and keep collecting examples from confirmed use.
- Recognition (choose one of three) is easier than production. cuecom's three-option confirm design fits.

### 2.3 Aphasia (stroke and progressive)

**Mechanism.** An acquired language disorder, usually from left-hemisphere injury, affecting speaking, writing,
understanding and reading "to varying degrees" [E: S4]. About 100,000-180,000 people acquire it each year in the US
and 2-4 million live with it; 25-50% of strokes cause aphasia, and the rate after a first ischaemic stroke rises from
about 15% under 65 to 43% at 85 and older [E: S4].

**Types.** Broadly nonfluent (short, effortful utterances) or fluent (longer utterances with less meaningful content);
Broca's, Wernicke's and anomic are examples. A person may not fit one type, and presentation changes during recovery
[E: S4]. Word-finding difficulty (anomia) is essentially universal [E: S4]. Fluent types can produce jargon,
invented words and word substitutions [E: S4].

**Comprehension is often damaged.** Difficulty with complex grammar, long or fast speech, speech without visual
support and nonliteral language is common [E: S4]. ASHA states aphasia does not by itself imply cognitive deficits
[E: S4].

**Gesture is not a guaranteed bypass.** Some therapies rely on "intact gesture abilities" for some people [E: S4], but
lesion studies find overlapping substrates: in one study, anterior temporal lesions impaired both pantomime of tool
use and every language test [E: S17, abstract only], and half of a 50-patient stroke sample had both aphasia and apraxia [E: S49]. Hemiparesis can limit pointing, writing and
gesturing [E: S4].

**Automatisms.** A case of progressive nonfluent aphasia produced involuntary "yes" and "right" automatisms whose
occurrence tracked apraxic errors and disinhibition rather than meaning [E: S50; single case].

**Primary progressive aphasia (PPA).** A language-led dementia [E: S53]. Functional communication interventions build
on strategies the person already uses and practise them with a partner [E: S53].

**Variability and fatigue.** ASHA lists fatigue among factors to consider [E: S4]. Post-stroke fatigue was present in
35% of patients at 2 months and 33% at 1.5 years in one cohort [E: S52].

**Co-occurring.** AOS and dysarthria, hemiparesis, visual field cuts and neglect, hearing loss, depression [E: S4,
S51]. Neglect is in 43% of right- and 20% of left-hemisphere acute strokes at presentation [E: S51].

**Usable signals.** Intonation and affect, pointing and choice among presented options, drawing, partial writing,
automatic phrases (with the caveat that they may not mean what they say) [J from S4].

**Implications for cuecom.** [J]
- **Do not assume the confirm screen is understood.** Three written options assume reading; three spoken options
  assume auditory comprehension of each. Pair each option with a picture or a referent, keep them short, and let the
  partner's speech context (already used in `cuecom/inference/meaning.py`) narrow options rather than lengthening them.
- **A "yes" vocalization may be an automatism.** Word-level evidence from ASR in aphasia should be down-weighted
  until the user's own patterns are known. A user-specific table that learns "this person says yes to everything"
  is more useful than a general YES detector.
- **Yes/no reliability is itself uncertain in severe aphasia.** No published rate was found, but a registered study
  exists to build a test separating reliable from unreliable yes/no responders after stroke (see Could not verify),
  which says clinicians treat this as a real distinction. cuecom should not let a single yes/no confirm commit a
  consequential message for these users.
- Present options centrally or on the user's attended side, and read them aloud too.

### 2.4 Cerebral palsy (CP)

**Mechanism.** Not a disease but a description of people sharing a non-progressive brain injury or lesion acquired
before, around or soon after birth, with highly variable movement disorders [E: S22]. About 1 in 500 neonates; about
17 million people worldwide [E: S22]. Subtypes include spastic, dyskinetic (dystonia and choreoathetosis) and ataxic
[E: S22, S27].

**How common communication problems are.** From a meta-analysis of population-based studies: 1 in 4 children with
CP could not talk, 1 in 2 had intellectual disability, 1 in 4 had epilepsy, 3 in 4 were in pain, 1 in 10 were blind,
1 in 25 were deaf [E: S23]. A Swedish population study found 21% had a speech disorder and a further 32% were
nonverbal, so 53% had one or the other [E: S24; X for the sum]. A UK register found 36% motor speech problems and 42%
communication impairments at 5 years, both linked to poorer gross motor function and intellectual impairment
[E: S25].

**Involuntary movement scales with effort.** In 55 people with dyskinetic CP, median dystonia scores were 70.2% and
choreoathetosis 26.7% of scale maximum, and both were significantly higher during activity than at rest [E: S27].

**Partner agreement is low.** On the Communication Function Classification System, two professionals agreed at 0.66
and a parent and a professional at 0.49 [E: S26]. Families and clinicians see different children.

**Variability.** Pain, fatigue, seizures and positioning all change performance [J; pain and epilepsy rates E: S23].

**Progression.** The lesion does not progress, but function changes over the lifespan and research has focused on
children [E: S22].

**What adults with CP who use AAC report** (testimony, small samples). Eighteen adults with CP ranked aided
communication among their primary modes but named many unaided modes as important too, and raised "major concerns
about reliability" of devices [E: S30]. Adults using AAC in medical appointments reported time barriers and
"inappropriate assumptions", and all but one brought a caregiver [E: S66].

**Usable signals.** Highly individual: head movement, eye gaze, a reliable hand or foot, vocalizations, facial
expression, partial speech [J]. Speech may be intelligible to family and not to strangers [E: S26 shows the
partner gap; S28 the familiarization effect].

**Implications for cuecom.** [J]
- **Model the noise during effort, not just at rest.** The `rest` set in `RESEARCH-mapping.md` should include trials
  where the user is trying to do something else (reach, talk, attend), because that is when dyskinetic movement
  peaks. Otherwise the "none" class will be learned from the calmest frames and fail in real use.
- **Prefer the user's most controlled body site**, which is often not the hands. cuecom's person/feature pipeline
  should let a signal be defined on any tracked landmark (head pitch, one foot, mouth opening).
- **Vision and hearing.** One in ten blind means the visual confirm screen is unusable for a real fraction of this
  population; options must also be spoken, and confirmation must be possible by a non-visual signal.
- Partial speech that family understand is gold. cuecom can learn it the way family did, from confirmed exposures.

### 2.5 ALS / motor neuron disease

**Mechanism.** Progressive degeneration of upper and lower motor neurons; speech becomes flaccid-spastic dysarthria
[J for the type label; E: S1 lists ALS among degenerative causes]. Around 25% of patients present with bulbar onset,
where dysarthria is often an early symptom; around 75% have limb onset with more gradual speech decline [E: S10].

**Timeline.** A 2025 review states that in most cases intelligibility falls below 90% within 18-24 months of symptom
onset and that complete loss of speech typically occurs by the third year, varying with phenotype [E: S10, review
statement]. ASHA lists neuromuscular disease (including ALS) dysarthria rates of 26-62% across studies [E: S1].
The two are not in conflict: one is a cross-section, the other a trajectory [J].

**Cognition.** Mild to moderate cognitive impairment in 35-45% over the disease course, with about 15% meeting
criteria for frontotemporal dementia [E: S11]; revised consensus criteria describe neuropsychological deficits in
over 50% [E: S12]. In one study the only AAC rejections were from FTD-related cognitive impairment [E: S10].

**Eyes are usually the last channel, but not always a stable one.** Oculomotor function is relatively preserved, but
ophthalmoparesis is reported, especially with long survival [E: S13]. In a German cohort with long-term ventilation
withdrawn, 41% had complete or partial ophthalmoplegia [E: S11]. A 2026 case-based review describes a phase of
"communicative ambiguity": ocular signals persist but cannot be reliably attributed to intentional control, and
"the distinction between intentional, fatigue-related, and reflexive movements becomes progressively difficult"
[E: S11]. In the completely locked-in state no voluntary eye movement or communication is possible [E: S16].

**Fatigue.** Among low daily users of eye-tracking systems, the reported barriers were eye-gaze tiredness (72.7%) and
oculomotor dysfunction (18.2%) [E: S10].

**Communication effectiveness depends on the situation.** Speakers with ALS and their frequent listeners agreed
closely on effectiveness, and both reported a range across 10 social situations depending on how adverse they were
[E: S15]. Eye-tracking devices improved communication and quality of life in 35 late-stage users with tetraplegia and
anarthria [E: S14].

**Usable signals over time.** Early: speech plus voice and message banking [E: S1, S10]. Middle: residual speech,
gesture from whichever limbs are spared, head movement. Late: eye gaze, blink, small facial movements [J, consistent
with S10's stage model].

**Implications for cuecom.** [J]
- **cuecom's per-user, user-defined signals fit ALS best of all the conditions here**, because the user is often
  cognitively intact, literate, motivated, and loses channels in sequence. A system that re-learns as the body
  changes is the stated gap.
- **Add signal-health tracking.** For each enrolled signal, track its hit rate and confusion over weeks from confirmed
  and rejected uses; flag a signal whose separability is falling, and prompt enrollment of the next channel *before*
  the old one fails. This is the software version of ASHA's "start AAC early".
- **Detect the ambiguity phase rather than paper over it.** If a signal's reliability drops below a floor, cuecom
  should say so to the user and partner and refuse to treat it as confirmation, rather than keep producing ranked
  options from noise. Abstention is the right behaviour, and it should be visible.
- Confirmation should cost one cheap action, and the confirm signal should be the user's most reliable, least
  fatiguing one, possibly different from the content signals.

### 2.6 Locked-in syndrome (LIS)

**Mechanism.** Usually a ventral pontine (brainstem) lesion; patients are awake and conscious but cannot produce
speech, limb or facial movement [E: S19]. Bauer's classes: *classic* (only vertical eye movements and blinking),
*incomplete* (other voluntary movement remnants), *total* (no eye movement, with preserved cortical function)
[E: S18]. Brainstem stroke is the most frequent cause; ALS is a chronic cause [E: S21].

**Recognition is delayed and families notice first.** More than half the time the family, not the physician, first
realised the patient was aware; diagnosis took on average over 2.5 months, and in some cases 4-6 years [E: S19].

**Early communication is fragile.** In acute LIS, eye-coded communication is limited because "vigilance is
fluctuating and eye movements may be inconsistent, very small, and easily exhausted" [E: S19].

**Life with LIS.** Life expectancy can be decades with medical care [E: S19]. In a French survey of chronic LIS,
91 of 168 responded, 26 were excluded for missing data, 47 reported happiness and 18 unhappiness [E: S20], i.e. 72%
and 28% of the 65 analysed [X]. The authors note answers were relayed through caregivers, which could bias them
[E: S20]. Unhappiness was associated with anxiety and dissatisfaction with mobility, recreation and recovery of speech
[E: S20]. Quality of life is often in the same range as healthy age-matched people, and perceived social support is
the strongest predictor of adjustment [E: S21].

**Usable signals.** Vertical eye movement and blink (classic); plus whatever remnant movement exists (incomplete);
none behaviourally (total) [E: S18].

**Implications for cuecom.** [J]
- cuecom's camera pipeline can see blinks and vertical gaze, so classic LIS is in scope technically. But the signal
  set is tiny, so the "ranked phrases" interface becomes a scanning interface: the user's few signals must drive
  navigation (next / select / back) rather than each mapping to a meaning. That is a different interaction model from
  the 8-intent table, and worth designing for explicitly.
- Voluntary blink must be separated from reflexive blink. Duration and double-blink patterns are the usual answers;
  per-user enrollment of *their* deliberate blink fits cuecom's model.
- Because exhaustion is fast, every unnecessary confirmation is costly. Auto-abstain silently on ambiguous evidence;
  never make the user reject wrong options one at a time.

### 2.7 Autism with minimal speech

**How many.** About 30% of autistic children remain minimally verbal after years of intervention, by Tager-Flusberg
and Kasari's estimate [E: S31]; a community programme found 26.3% left early intervention with fewer than five
functional words, with figures ranging by definition [E: S32]. The population is "highly variable" with no single
profile and is hard to assess reliably [E: S31].

**Not only an oral-motor problem.** Deaf autistic children of Deaf parents, exposed to ASL from birth, can remain
minimally *signing*, with small repertoires of echolalic or idiosyncratic signs, which rules out hearing or language
access as necessary explanations [E: S38]. Children with ASD show dyspraxia not only in imitation but also in gestures
to command and tool use [E: S37].

**Echolalia carries function.** Immediate echolalia served seven functional categories [E: S34], delayed echolalia
fourteen, varying in interactiveness and relevance [E: S35], and echoes can mark stance through intonation
[E: S36].

**Interventions.** In a randomized trial with 61 minimally verbal children aged 5-8, starting treatment with a
speech-generating device improved spontaneous communicative utterances, novel words and comments over
spoken-words-only treatment [E: S33]. Adding a device did not hold these children back on those measures. [J for the
reading]

**Behaviour as communication.** ReCANVo base rates (most vocalizations are affect or self-talk; about 6% requests)
are already covered in `RESEARCH-mapping.md` section 2 and are not redone here.

**Implications for cuecom.** [J]
- **An echo of the partner's question is not an answer.** If the partner asks "Do you want juice?" and the user says
  "want juice", the ASR transcript looks like a yes. cuecom's conversation layer should treat a near-verbatim repeat of
  the partner's last turn as its own evidence type (possible echo) with a user-specific mapping learned from
  confirmations, not as lexical agreement.
- Idiosyncratic signs and sounds are the expected case, which is cuecom's design centre. The ReCANVo finding that
  most vocalizations are not requests is the reason the "none" class must dominate the prior.
- Gestures to command are impaired for some autistic users, so passive enrollment from confirmed use applies here too
  (see 2.2).

### 2.8 Rett syndrome

**Mechanism and course.** Almost all classic cases are MECP2 mutations; about 1 in 9,000-10,000 females; 6 to 18
months of apparently typical development, then regression with loss of purposeful hand use and repetitive hand
wringing, washing or clapping; breathing abnormalities and seizures can develop [E: S39]. Diagnostic criteria include
loss of acquired hand skills and of spoken language, impaired gait and hand stereotypies [E: S40]. Average life
expectancy is around 50 years [E: S40].

**Communication.** Eye gaze is the most common communicative form [E: S41] and described as the predominant expressive
modality, though "it lacks sustained attentional control" [E: S40]. In 120 people, informants reported social
convention, commenting, answering, requesting and choice-making functions; "problematic topographies" such as
self-injury and screaming were used communicatively in 10-41% [E: S41]. Parents in 16 interviews all reported their
daughters expressed discomfort and pleasure and made requests and choices via vocalizations, body movements and
eye gaze, and said success depended on the partner [E: S43]. Comprehension studies suggest recognition mainly of
names, key words and simple sentences, strongly helped by visual or contextual cues [E: S40]. The RSBQ includes
"expressionless facial features" among core symptoms [E: S40]. Vocalization declines progressively even with
airflow present, alongside increased hand-to-mouth stereotypies [E: S40].

**Eye-gaze technology.** In a Dutch survey of 63 families, 20 had experience with eye-gaze systems; after trials, 11
were funded and 2 families decided against because the child was "too mobile or suffered from too many seizures";
satisfaction with the systems exceeded satisfaction with the support, and families reported frustration at the time
needed to build vocabularies [E: S42].

**Usable signals.** Eye gaze and eye pointing, vocalization, whole-body approach and withdrawal, laughing and smiling
[E: S41, S43].

**Implications for cuecom.** [J]
- **Hand gestures are the wrong primary channel**: purposeful hand use is lost and stereotypies are constant. A hand
  detector will be busy all day. Hand features should be excluded or heavily tempered for these users, with gaze,
  head and body orientation as the main channels.
- **Gaze must be read with attention fluctuation in mind.** A gaze held on a target is evidence; a gaze that drifts
  is not a "no". Long dwell windows and tolerance of latency are needed.
- **Behaviour that looks like distress may be a message.** The 10-41% figure argues for letting families enroll
  "screaming means X for her" as a signal with a meaning, rather than filtering it as noise.
- The family-built vocabulary burden is a reported pain point [E: S42]. cuecom's learn-from-confirmations approach is
  a direct answer if it really keeps setup short.

### 2.9 Down syndrome

**Speech and language.** Speech patterns combine developmental delay with errors not seen in typical development
[E: S44]; intelligibility problems are widespread, worse in sentences and conversation than single words, and worse
with unfamiliar adults (937 parent reports) [E: S45]. Language deficits are broad, not limited to expression, with
associated verbal short-term memory deficits [E: S48]; production and syntax are particularly affected [E: S47].
CAS is reported at a higher rate [E: S3].

**Hearing.** Permanent hearing loss in 24.9% of 308 children, transient loss in 22-30% [E: S46].

**Usable signals.** Speech that family understand; manual signs and gestures (sign-supported communication is widely
used clinically [J, not verified with a fetched source]); pointing; pictures.

**Implications for cuecom.** [J]
- This is a population with real speech that strangers miss. The highest-value path is the "familiar listener"
  role: learn the user's own word forms from confirmed exchanges and offer them to strangers as ranked options.
- Hearing loss means the partner's speech, which cuecom uses as context, may also not be heard by the user. The
  options must be visual as well as spoken.
- Users may already sign (key word signing). The optional sign pack in `RESEARCH-datasets.md` is relevant, but the
  user's personal versions of signs matter more than citation forms.

### 2.10 Shorter sections

**Parkinson's disease (hypokinetic dysarthria).** Speech disorder in 44-88% [E: S1]; one review gives 90% [E: S56].
Levodopa raises loudness and rate but loudness decays faster [E: S55]. People with PD showed reduced *spontaneous*
facial expression, while *posed* expression and their felt emotion were relatively intact (n=12) [E: S54].
Implication [J]: facial affect features under-read PD users' feelings, so a population affect model would label
them flat; but deliberate facial signals may still be enrollable. Speech enrollment should be time-stamped against
medication if the user wants that.

**Huntington's disease.** Dysarthria in 78-93% [E: S1]. Speech in HD clustered into four subgroups including
abnormally fast and abnormally slow rates, not one hyperkinetic pattern [E: S57]. Implication [J]: chorea creates
constant involuntary movement, the same "noise correlated with life" problem as dyskinetic CP; HD also involves
cognitive decline [J, not verified here], so the confirm-step design for cognition (2.3) applies.

**Stuttering.** Lifetime prevalence 0.72% (2002 estimate); 0.81% of adults with childhood onset (0.53% overt, 0.28%
covert); about 88-91% of children recover [E: S6]. Secondary behaviours during stuttering moments include head
nodding, eye blinking and jaw tightening [E: S6]. Severity varies by setting [E: S6]. Implication [J]: people who
stutter are mostly not AAC users, but two points carry over: a head nod or blink during a block is not a "yes"
(secondary behaviours look like signals), and speech recognizers that cut off at pauses mis-segment blocks. No
peer-reviewed ASR-and-stuttering evaluation was retrieved here.

**Selective mutism.** An anxiety disorder: consistent failure to speak in specific social situations despite speaking
elsewhere [E: S5]; prevalence estimates 0.2-1.6% [E: S5], 0.71% in one school sample [E: S58]; onset typically 3-6
years [E: S5]. DSM-5 placed it among the anxiety disorders, though reviewers raise critical points about that
classification [E: S59]. Children may use eye gaze, nods, pointing, writing; AAC may be used early and faded, or kept long term
by preference [E: S5]. Implication [J]: this is the one group where the *setting*, not the body, gates speech. cuecom
would be a context-specific tool; a visible camera and a speaking device may raise anxiety rather than lower it.
Design and testing should involve clinicians before any use with children.

**Voice disorders and spasmodic dysphonia.** About 1 in 13 US adults has a voice problem annually; symptoms include
quality varying through the day and fatigue with prolonged use [E: S7]. Adductor spasmodic dysphonia responds to
botulinum toxin, averaging 90% of normal function for about 15 weeks per injection [E: S61]. Implication [J]: mostly
not AAC users, but they show voice *cycling* over weeks; any voice-based signal learned at one point in the cycle will
drift.

**Laryngectomy.** Rehabilitation most often uses an electrolarynx, oesophageal speech and/or tracheoesophageal speech;
AAC may be temporary after surgery or long-term with extensive resection [E: S8]. In 63 laryngectomized patients, 78%
achieved voice with an indwelling voice prosthesis, 80% were satisfied with voice quality, and voice quality
correlated with fatigue and anxiety about speaking [E: S60]. Implication [J]: language and articulation are intact, so
mouthed words and lip shapes are a strong visual signal; cuecom's face landmarks could support a small personal
lip-word vocabulary, which no other group here can use as well.

## 3. Cross-cutting comparison

### 3.1 Table

Ratings are my judgement from the sections above [J], except where a cell cites a source.

| Condition | Layer broken | Comprehension | Deliberate movement on demand | Involuntary movement | Fatigue / within-day variability | Trajectory | Vision / hearing / attention risk | Best residual channels | Confirm-step risk |
|---|---|---|---|---|---|---|---|---|---|
| Dysarthria (stroke, MS, TBI) | Execution | Usually intact | Good if limbs spared | Low (except hyperkinetic) | High; medication, fatigue [E: S1] | Recovering or progressive | Neglect after stroke [E: S51] | Partial speech, gesture | Low |
| Apraxia (AOS, CAS) | Planning | Usually intact (AOS); language disorder >95% in CAS [E: S3] | **Poor** [E: S2] | Low | Inconsistency by definition [E: S2, S3] | Recovering (stroke), progressive (PPAOS) | With aphasia: neglect, hemiparesis | Automatic sounds, pointing, choosing | Low to medium |
| Aphasia | Language | **Often impaired** [E: S4] | Varies; limb apraxia common [E: S49] | Low | Post-stroke fatigue ~1/3 [E: S52] | Recovering (stroke), progressive (PPA) | Neglect, field cuts, hemiparesis | Intonation, affect, pointing, pictures | **High**: options may not be understood |
| CP | Execution (± cognition) | Varies; 1 in 2 ID [E: S23] | Varies widely | **High in dyskinetic; worse with effort** [E: S27] | Pain 3 in 4 [E: S23], seizures | Static lesion, changing function | **1 in 10 blind, 1 in 25 deaf** [E: S23] | Head, gaze, best limb, family-known speech | Medium |
| ALS | Execution → all motor | Intact in many; 35-45% cognitive change [E: S11] | Good early, lost progressively | Fasciculation, spasticity | **High; eye-gaze tiredness** [E: S10] | **Progressive**, ~2-3 years to anarthria in bulbar onset [E: S10] | Late oculomotor decline [E: S11, S13] | Speech → limbs → head → eyes | High late (ambiguity phase) [E: S11] |
| LIS | Execution (near total) | Intact | Eyes/blink only (classic) [E: S18] | Low | **Eye movements easily exhausted** [E: S19] | Chronic, can be stable for decades [E: S19] | Low cognitive risk | Vertical gaze, blink | **High: confirm uses the only channel** |
| Autism, minimal speech | Language + social + praxis | Varies widely [E: S31] | Dyspraxia on command [E: S37] | Stereotypies | Arousal, sensory load | Developmental | Sensory sensitivity | Idiosyncratic sounds, signs, pulling, objects | Medium; echolalia in ASR |
| Rett | All (regression) | Names, key words with context [E: S40] | **Hand use lost** [E: S39] | **Constant hand stereotypies** [E: S39] | Attention fluctuates [E: S40]; seizures | Regression then plateau | Seizures [E: S39] | Eye gaze, vocalization, body approach [E: S41] | High |
| Down syndrome | Speech + language | Broad deficits [E: S48] | Usually good | Low | Moderate | Developmental | **~1 in 4 permanent hearing loss** [E: S46] | Speech known to family, signs | Medium |
| Parkinson's | Execution (hypokinetic) | Usually intact early | Good | Tremor, dyskinesia | **Medication on/off** [E: S55] | Progressive | **Reduced spontaneous facial expression** [E: S54] | Speech (quiet), deliberate gestures | Low to medium |
| Laryngectomy | Source | Intact | Good | Low | Voice fatigue [E: S60] | Stable | Low | Mouthed words, electrolarynx speech, writing | Low |
| Stuttering | Fluency | Intact | Good | Secondary behaviours [E: S6] | Situational [E: S6] | Mostly stable in adults | Low | Speech | Low |
| Selective mutism | Social gating | Intact | Good | Low | Situational | Usually improves | Low | Gesture, writing in anxious settings [E: S5] | Low (anxiety risk instead) |

### 3.2 Four groups by what cuecom must do differently

[J] Grouping the table by design consequence rather than diagnosis:

1. **"Clear mind, failing body"**: ALS, LIS, Parkinson's, many adults with CP, laryngectomy. Literate, intact
   language. Bottleneck is bandwidth and fatigue. cuecom should optimise for few, cheap actions, letter or word
   entry when available, signal-health tracking, and the user's own phrases.
2. **"The words are the problem"**: aphasia, PPA, CAS with language disorder, Down syndrome. More channels do not
   fix missing words. cuecom should offer recognition over recall (choose among pictured options), learn the user's
   approximations, and keep options short and multimodal.
3. **"Deliberate movement is the problem"**: apraxia, Rett, autistic dyspraxia, dyskinetic CP. On-demand
   enrollment under-measures them, and involuntary movement over-produces candidate signals. cuecom should enroll
   passively from confirmed use, model effort-time noise, and use long windows.
4. **"Speech exists but is gated or atypical"**: stuttering, selective mutism, mild dysarthria, voice disorders.
   cuecom is a supplement at most; speech recognition quality and social acceptability matter more than the
   gesture pipeline.

### 3.3 Where AAC technology commonly fails these users

- **Support and fit, more than the device.** Clinicians rated not maintaining or adjusting the system, attitude, lack
  of training, lack of support and poor fit as the factors most related to inappropriate abandonment (275 AAC
  clinicians) [E: S64]. For young children, parental grief and loss was raised as a contributor [E: S65]. Families of
  girls with Rett were happier with eye-gaze devices than with the support around them [E: S42].
- **Reliability.** Adults with CP raised major concerns about device reliability [E: S30].
- **Setup burden.** Building vocabularies and page-sets falls to parents [E: S42]; dictation software for dysarthric
  speech needed retraining that one AAC user found "frustratingly high" (testimony, [E: S69]).
- **Speed.** 8-10 wpm direct selection, ~1.7 wpm switch scanning, against 120-185 wpm conversation [E: S69]: a 12x
  to 23x gap for direct selection and roughly 70x to 110x for scanning [X].
- **Authorship drift.** Generic sentence prediction produces sentences a user "would never type themselves"; the AAC
  user in Waller et al. describes seeing her own words predicted as "the first time I feel like I'm communicating with
  my voice" (testimony, [E: S69]).
- **Medical settings.** Time pressure and wrong assumptions about the person [E: S66].

### 3.4 Speech recognition on atypical speech

On Speech Accessibility Project data (Parkinson's-only at that stage, per `RESEARCH-datasets.md` section 3.3), an off-the-shelf recognizer with 3.4% word
error rate on typical speech had 36.3% on the test speakers; fine-tuning on the project data brought it to 23.7%
[E: S70]. So even after adaptation, roughly one word in four is wrong at that point in the project [X]. For more
severe dysarthria the number will be worse [J]. Dataset access is covered in `RESEARCH-datasets.md` section 3.3.

## 4. Non-obvious insights

Each item says what the common assumption is, what the evidence says, and why it matters for cuecom.

1. **Assumption: a deliberate, rehearsed signal is the most reliable kind. Evidence: for apraxia it is the least
   reliable kind.** Automatic speech beats generative speech in AOS [E: S2]; dyspraxia in autism affects gesture to
   command [E: S37]; Rett removes purposeful hand use [E: S39]. And in Parkinson's the reverse holds for faces:
   spontaneous expression is reduced and posed expression is relatively intact [E: S54]. *Consequence* [J]: which
   kind of signal (spontaneous or deliberate) is reliable is itself user-specific. Enrollment should test both and
   keep whichever works.
2. **Assumption: involuntary movement is background noise. Evidence: in dyskinetic CP it rises with activity**
   [E: S27]. *Consequence* [J]: noise and signal are correlated in time, which breaks the independence that naive
   fusion assumes (`RESEARCH-interpretation.md` B2's tempering helps but does not fix this). Enroll the "none" class
   during effort.
3. **Assumption: "yes" is the easiest thing to communicate. Evidence: yes can be an automatism** [E: S50], a stuttering
   secondary behaviour can be a nod [E: S6], an echo can look like agreement [E: S34], and people who answer "for"
   someone else answer from their own knowledge [E: S62]. *Consequence* [J]: cuecom's Yes intent needs the most
   per-user calibration, not the least, and a single yes should not commit consequential messages.
4. **Assumption: confirmation is free. Evidence: the confirming channel fatigues** [E: S10, S19]. *Consequence* [J]:
   budget confirmations. Abstain silently on weak evidence, offer the most likely option first so one action
   suffices most of the time, and allow a pre-chosen floorholder (for example "give me a moment") that the user set
   up in advance; floorholders were rated well by partners when delivery was slow [E: S67, S68].
5. **Assumption: more modalities make communication more robust. Evidence: aphasia damages language across
   modalities, and limb apraxia co-occurs in about half of left-stroke aphasia** [E: S4, S49]; minimally verbal autism
   can be minimally signing too [E: S38]. *Consequence* [J]: adding gesture does not rescue a language-level
   impairment. For these users the gain comes from recognition (pick among offered meanings) and context, which is
   where cuecom's conversation layer earns its keep.
6. **Assumption: the person nearest the user knows what they mean. Evidence: they often do know more, but they also
   disagree with professionals** (0.49 parent-professional agreement on CFCS [E: S26]) **and can unknowingly author
   messages** [E: S62, S63, S9]. *Consequence* [J]: partner knowledge is valuable evidence for priors and dictionary
   entries, and dangerous as confirmation. Record in the trace whether a confirm came from the user's signal or from
   a keyboard, and design so the partner cannot confirm on the user's behalf.
7. **Assumption: a clear-headed user can always tell you a signal is failing. Evidence: in late ALS, ocular signals
   pass through an ambiguous phase where intention and fatigue or reflex can no longer be told apart** [E: S11].
   *Consequence* [J]: cuecom should compute signal reliability from data (confirm/reject history, separation over
   time) and surface it to the user and partner while the user can still weigh in, which is also what that review
   recommends for advance care planning [E: S11].
8. **Assumption: faces carry affect for everyone. Evidence: reduced spontaneous expression in Parkinson's** [E: S54]
   **and "expressionless facial features" as a core Rett symptom** [E: S40]. *Consequence* [J]: any population-trained
   facial affect or emotion feature should be off by default and per-user if on.
9. **Assumption: consciousness and competence are visible. Evidence: in LIS, families noticed awareness first in more
   than half of cases and diagnosis averaged over 2.5 months** [E: S19]. *Consequence* [J]: cuecom must never be
   presented as a way to judge awareness or capacity. That is a clinical judgement, and the project's "no clinical
   claims" rule should be stated in any demo.
10. **Assumption: users want speed first. Evidence: partners prefer slow relevant messages over fast partly relevant
    ones** [E: S67, S68], **and AAC users value their own words** (testimony, [E: S69]). *Consequence* [J]: the LLM
    wording layer in `RESEARCH-interpretation.md` should be judged first on whether the user recognises the phrasing
    as theirs, and only then on latency.
11. **Assumption: a progressive disease means a declining user. Evidence: in chronic LIS most respondents reported
    happiness, and longer time in LIS correlated with happiness** [E: S20]; **social support was the strongest
    predictor of adjustment** [E: S21]. *Consequence* [J]: cuecom's value is social participation, not only
    needs-based requests (water, bathroom). The phrase database should weight social and personal messages, which
    ALS caregivers also asked for ("stay connected" as mandatory or desirable for 80%) [E: S10].
12. **Assumption: behaviour labelled "challenging" is to be ignored. Evidence: in Rett it is used communicatively by
    10-41%** [E: S41]. *Consequence* [J]: let families enroll it as a signal with a meaning.

## 5. Design implications for cuecom, in priority order

All [J]. Each line names the condition groups it serves (section 3.2 numbering).

1. **Confirm only by the user's own signal, and trace it.** Keyboard confirm stays for testing, but the trace should
   record confirm source, and the product framing should say partner confirmation is not the user's message. (All
   groups; authorship.)
2. **Passive enrollment from confirmed use, alongside prompted trials.** Relax the admission rule for users whose
   prompted hit rate is low but whose confirmed-use examples are consistent. (Groups 3, 2.)
3. **Rest/none trials during effort**, not only at rest. (Group 3, hyperkinetic dysarthria.)
4. **Per-signal health tracking over sessions**, with a visible warning when separability falls and a prompt to
   enroll the next channel. (Group 1, especially ALS.)
5. **A scanning mode for one- and two-signal users** (next / select), so LIS and late ALS are in scope. (Group 1.)
6. **Multimodal, short, centrally placed options**: picture or referent + text + spoken readout, with the user's own
   phrasing. (Groups 2, 3; neglect, hearing and vision loss.)
7. **Echo detection in the conversation layer**: repeats of the partner's last turn become their own evidence type.
   (Autism; aphasia.)
8. **Per-user priors for Yes**, never a population YES detector, and two-step confirmation for consequential messages
   in users flagged as unreliable yes/no responders. (Groups 2, 3.)
9. **Session-level recalibration** of vocal and visual detectors (time of day, medication, fatigue). (Group 1,
   dysarthria.)
10. **Facial affect features off by default.** (Parkinson's, Rett, CP.)
11. **Phrase database weighting toward social and personal messages**, with the user's own confirmed phrases first.
    (All.)
12. **Mouthed-word lip vocabulary as an optional channel** for intact-language users without voice. (Laryngectomy,
    some ALS and dysarthria.)

What not to claim: none of the above makes cuecom a diagnostic, capacity-assessment or awareness-detection tool, and
nothing here measures cuecom's accuracy for any of these groups.

## Could not verify

- **Dysarthria type characteristics** in the section 2.1 table (third column) are the standard Mayo-system
  descriptions from general clinical knowledge. ASHA's type-by-type page returned "not found" and no fetched source
  confirmed the feature lists. Lesion sites are [E: S1].
- **Yes/no reliability in severe aphasia:** no published rate was found. A French diagnostic study registered to
  classify reliable vs unreliable yes/no responders after stroke (ClinicalTrials.gov NCT03257696) lists no results.
- **Gesture-language overlap:** the anterior-temporal finding [S17] is from the abstract; the paper was not read in
  full.
- **ALS timeline (intelligibility below 90% in 18-24 months; anarthria by year 3)** is a statement in a 2025 review
  [S10], not a primary cohort. A 2022 Scientific Reports cohort (166 people, 30 bulbar onset) estimating 23-32 months to
  speech loss in bulbar onset was seen only through a search summary.
- **Key word signing in Down syndrome** is common clinical practice but no source was fetched for usage rates.
- **Cognitive change in Huntington's** was not checked against a source here.
- **Stuttering and ASR:** no peer-reviewed evaluation was retrieved.
- **Reported eye-gaze barrier figures (72.7%, 18.2%)** come from the ALS review [S10] citing an underlying study I did
  not read.
- Facilitated communication and RPM: I used ASHA's position and two classic papers; I did not review newer
  proponent studies.

## Sources

ASHA Practice Portal and policy
- [S1] ASHA. Dysarthria in Adults. https://www.asha.org/practice-portal/clinical-topics/dysarthria-in-adults/
- [S2] ASHA. Acquired Apraxia of Speech. https://www.asha.org/practice-portal/clinical-topics/acquired-apraxia-of-speech/
- [S3] ASHA. Childhood Apraxia of Speech. https://www.asha.org/practice-portal/clinical-topics/childhood-apraxia-of-speech/
- [S4] ASHA. Aphasia. https://www.asha.org/practice-portal/clinical-topics/aphasia/
- [S5] ASHA. Selective Mutism. https://www.asha.org/practice-portal/clinical-topics/selective-mutism/
- [S6] ASHA. Fluency Disorders. https://www.asha.org/practice-portal/clinical-topics/fluency-disorders/
- [S7] ASHA. Voice Disorders. https://www.asha.org/practice-portal/clinical-topics/voice-disorders/
- [S8] ASHA. Head and Neck Cancer. https://www.asha.org/practice-portal/clinical-topics/head-and-neck-cancer/
- [S9] ASHA (2018). Rapid Prompting Method [Position statement]. https://www.asha.org/policy/ps2018-00351/

ALS and locked-in syndrome
- [S10] Jackson MC et al. (2025). Stage-based communication rehabilitation in ALS: a review. doi:10.26502/aimr.0230 (PMC12857845)
- [S11] Bublitz SK et al. (2026). Ethical challenges in treatment-goal transitions in invasively ventilated ALS. Neurol Res Pract. doi:10.1186/s42466-026-00522-3 (PMC13425970)
- [S12] Strong MJ et al. (2017). ALS-frontotemporal spectrum disorder: revised diagnostic criteria. ALS FTD. doi:10.1080/21678421.2016.1267768
- [S13] Sharma R et al. (2011). Oculomotor dysfunction in ALS: a comprehensive review. Arch Neurol. doi:10.1001/archneurol.2011.130
- [S14] Caligari M et al. (2013). Eye tracking communication devices in ALS. ALS FTD. doi:10.3109/21678421.2013.803576
- [S15] Ball LJ, Beukelman DR, Pattee GL (2004). Communication effectiveness of individuals with ALS. J Commun Disord. doi:10.1016/j.jcomdis.2003.09.002
- [S16] Murguialday AR et al. (2011). Transition from the locked in to the completely locked-in state. Clin Neurophysiol. doi:10.1016/j.clinph.2010.08.019
- [S18] Bauer G, Gerstenbrand F, Rumpl E (1979). Varieties of the locked-in syndrome. J Neurol. doi:10.1007/bf00313105
- [S19] Laureys S et al. (2005). The locked-in syndrome: what is it like to be conscious but paralyzed and voiceless? Prog Brain Res. doi:10.1016/s0079-6123(05)50034-7
- [S20] Bruno MA et al. (2011). A survey on self-assessed well-being in chronic locked-in syndrome. BMJ Open. doi:10.1136/bmjopen-2010-000039
- [S21] Lulé D et al. (2009). Life can be worth living in locked-in syndrome. Prog Brain Res. doi:10.1016/s0079-6123(09)17723-3

Cerebral palsy and dysarthria listeners
- [S22] Graham HK et al. (2016). Cerebral palsy. Nat Rev Dis Primers. doi:10.1038/nrdp.2015.82
- [S23] Novak I et al. (2012). Clinical prognostic messages from a systematic review on cerebral palsy. Pediatrics. doi:10.1542/peds.2012-0924
- [S24] Nordberg A et al. (2013). Speech problems affect more than one in two children with cerebral palsy. Acta Paediatr. doi:10.1111/apa.12076
- [S25] Parkes J et al. (2010). Oromotor dysfunction and communication impairments in children with CP. Dev Med Child Neurol. doi:10.1111/j.1469-8749.2010.03765.x
- [S26] Hidecker MJ et al. (2011). Developing and validating the Communication Function Classification System. Dev Med Child Neurol. doi:10.1111/j.1469-8749.2011.03996.x
- [S27] Monbaliu E et al. (2016). Clinical patterns of dystonia and choreoathetosis in dyskinetic CP. Dev Med Child Neurol. doi:10.1111/dmcn.12846
- [S28] Hustad KC, Cahill MA (2003). Effects of presentation mode and repeated familiarization on intelligibility of dysarthric speech. Am J Speech Lang Pathol. doi:10.1044/1058-0360(2003/066)
- [S29] Liss JM et al. (2002). Effects of familiarization on intelligibility and lexical segmentation in hypokinetic and ataxic dysarthria. J Acoust Soc Am. doi:10.1121/1.1515793
- [S30] Smith MM, Connolly I (2008). Roles of aided communication: perspectives of adults who use AAC. Disabil Rehabil Assist Technol. doi:10.1080/17483100802338499

Autism
- [S31] Tager-Flusberg H, Kasari C (2013). Minimally verbal school-aged children with ASD: the neglected end of the spectrum. Autism Res. doi:10.1002/aur.1329
- [S32] Rose V et al. (2016). The proportion of minimally verbal children with ASD in a community-based early intervention programme. J Intellect Disabil Res. doi:10.1111/jir.12284
- [S33] Kasari C et al. (2014). Communication interventions for minimally verbal children with autism: a SMART. J Am Acad Child Adolesc Psychiatry. doi:10.1016/j.jaac.2014.01.019
- [S34] Prizant BM, Duchan JF (1981). The functions of immediate echolalia in autistic children. J Speech Hear Disord. doi:10.1044/jshd.4603.241
- [S35] Prizant BM, Rydell PJ (1984). Analysis of functions of delayed echolalia in autistic children. J Speech Hear Res. doi:10.1044/jshr.2702.183
- [S36] Sterponi L, Shankey J (2014). Rethinking echolalia. J Child Lang. doi:10.1017/s0305000912000682
- [S37] Mostofsky SH et al. (2006). Developmental dyspraxia is not limited to imitation in children with ASD. J Int Neuropsychol Soc. doi:10.1017/s1355617706060437
- [S38] Shield A, Parnes G, Chenausky K (2026). Minimally-signing autism in deaf children of Deaf parents: a case series. doi:10.1177/23969415261416767

Rett syndrome
- [S39] MedlinePlus Genetics. Rett syndrome. https://medlineplus.gov/genetics/condition/rett-syndrome/
- [S40] Voniati L et al. (2025). Communication abilities, assessment procedures, and intervention approaches in Rett syndrome: a narrative review. Brain Sci. doi:10.3390/brainsci15070753
- [S41] Didden R et al. (2010). Communication in individuals with Rett syndrome: an assessment of forms and functions. J Dev Phys Disabil. doi:10.1007/s10882-009-9168-2
- [S42] Townend GS et al. (2016). Eye gaze technology as AAC for individuals with Rett syndrome: experiences of families in the Netherlands. J Dev Phys Disabil. doi:10.1007/s10882-015-9455-z
- [S43] Urbanowicz A et al. (2016). Parental perspectives on the communication abilities of their daughters with Rett syndrome. Dev Neurorehabil. doi:10.3109/17518423.2013.879940

Down syndrome
- [S44] Kent RD, Vorperian HK (2013). Speech impairment in Down syndrome: a review. J Speech Lang Hear Res. doi:10.1044/1092-4388(2012/12-0148)
- [S45] Kumin L (1994). Intelligibility of speech in children with Down syndrome in natural settings. Percept Mot Skills. doi:10.2466/pms.1994.78.1.307
- [S46] Nightengale E et al. (2017). Understanding hearing and hearing loss in children with Down syndrome. Am J Audiol. doi:10.1044/2017_aja-17-0010
- [S47] Roberts JE, Price J, Malkin C (2007). Language and communication development in Down syndrome. Ment Retard Dev Disabil Res Rev. doi:10.1002/mrdd.20136
- [S48] Næss KA et al. (2011). Language and verbal short-term memory skills in children with Down syndrome: a meta-analytic review. Res Dev Disabil. doi:10.1016/j.ridd.2011.05.014

Aphasia, apraxia, stroke
- [S17] Goldenberg G, Randerath J (2015). Shared neural substrates of apraxia and aphasia. Neuropsychologia. doi:10.1016/j.neuropsychologia.2015.05.017
- [S49] Weiss PH et al. (2016). Where language meets meaningful action: a combined behavior and lesion analysis of aphasia and apraxia. Brain Struct Funct. doi:10.1007/s00429-014-0925-3
- [S50] Code C, Tree JJ, Dawe K (2009). Opportunities to say 'yes': rare speech automatisms in progressive nonfluent aphasia and apraxia. Neurocase. doi:10.1080/13554790902911634
- [S51] Ringman JM et al. (2004). Frequency, risk factors, anatomy, and course of unilateral neglect in an acute stroke cohort. Neurology. doi:10.1212/01.wnl.0000133011.10689.ce
- [S52] Snaphaan L, van der Werf S, de Leeuw FE (2011). Time course and risk factors of post-stroke fatigue. Eur J Neurol. doi:10.1111/j.1468-1331.2010.03217.x
- [S53] Volkmer A et al. (2020). Effects of functional communication interventions for people with PPA and their caregivers: a systematic review. Aging Ment Health. doi:10.1080/13607863.2019.1617246
- [S71] Josephs KA et al. (2006). Clinicopathological and imaging correlates of progressive aphasia and apraxia of speech. Brain. doi:10.1093/brain/awl078

Parkinson's, Huntington's, voice
- [S54] Smith MC, Smith MK, Ellgring H (1996). Spontaneous and posed facial expression in Parkinson's disease. J Int Neuropsychol Soc. doi:10.1017/s1355617700001454
- [S55] Ho AK, Bradshaw JL, Iansek R (2008). For better or worse: the effect of levodopa on speech in Parkinson's disease. Mov Disord. doi:10.1002/mds.21899
- [S56] Brabenec L et al. (2017). Speech disorders in Parkinson's disease: early diagnostics and effects of medication and brain stimulation. J Neural Transm. doi:10.1007/s00702-017-1676-0
- [S57] Diehl SK et al. (2019). Motor speech patterns in Huntington disease. Neurology. doi:10.1212/wnl.0000000000008541
- [S58] Bergman RL, Piacentini J, McCracken JT (2002). Prevalence and description of selective mutism in a school-based sample. J Am Acad Child Adolesc Psychiatry. doi:10.1097/00004583-200208000-00012
- [S59] Muris P, Ollendick TH (2015). Children who are anxious in silence: a review on selective mutism. Clin Child Fam Psychol Rev. doi:10.1007/s10567-015-0181-y
- [S60] Ackerstaff AH et al. (1994). Communication, functional disorders and lifestyle changes after total laryngectomy. Clin Otolaryngol. doi:10.1111/j.1365-2273.1994.tb01234.x
- [S61] Blitzer A, Brin MF, Stewart CF (1998). Botulinum toxin management of spasmodic dysphonia: a 12-year experience in more than 900 patients. Laryngoscope. doi:10.1097/00005537-199810000-00003

Authorship, AAC use and technology
- [S62] Wegner DM, Fuller VA, Sparrow B (2003). Clever hands: uncontrolled intelligence in facilitated communication. J Pers Soc Psychol. doi:10.1037/0022-3514.85.1.5
- [S63] Mostert MP (2001). Facilitated communication since 1995: a review of published studies. J Autism Dev Disord. doi:10.1023/a:1010795219886
- [S64] Johnson JM et al. (2006). Perspectives of speech language pathologists regarding success versus abandonment of AAC. Augment Altern Commun. doi:10.1080/07434610500483588
- [S65] Moorcroft A, Scarinci N, Meyer C (2019). Speech pathologist perspectives on the acceptance versus rejection or abandonment of AAC systems for children with complex communication needs. Augment Altern Commun. doi:10.1080/07434618.2019.1609577
- [S66] Morris MA, Dudgeon BJ, Yorkston K (2013). A qualitative study of adult AAC users' experiences communicating with medical providers. Disabil Rehabil Assist Technol. doi:10.3109/17483107.2012.746398
- [S67] Bedrosian JL, Hoag LA, McCoy KF (2003). Relevance and speed of message delivery trade-offs in AAC. J Speech Lang Hear Res. doi:10.1044/1092-4388(2003/063)
- [S68] Hoag LA et al. (2004). Trade-offs between informativeness and speed of message delivery in AAC. J Speech Lang Hear Res. doi:10.1044/1092-4388(2004/096)
- [S69] Waller A, Griffiths T, Kristensson PO (2025). "What I think about when I type about talking": reflections on text-entry acceleration interfaces. Commun ACM 68(5). doi:10.1145/3703451
- [S70] Hasegawa-Johnson M et al. (2024). Community-supported shared infrastructure in support of speech accessibility. J Speech Lang Hear Res. doi:10.1044/2024_jslhr-24-00122
