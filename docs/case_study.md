# Same failure, different sector: building an evidence-grounded atlas of AI incidents

*A case study of the AI Incident Atlas — what it found, and the engineering decisions that made the findings
trustworthy. By Jonathan Doane.*

## Why another look at AI incidents?

The AI Incident Database (AIID) is the best public record of AI systems going wrong: almost 1,800 incidents and
thousands of linked news reports, curated by the Responsible AI Collaborative. But it is built for *looking things
up*, not for *reasoning across* incidents. Descriptions are free text. Expert classifications exist, but each covers
a different slice of the database with a different vocabulary — the MIT AI Risk Repository's domains, the
Goals-Methods-Failures (GMF) taxonomy, CSET's harm taxonomy. Nothing tells you that a facial-recognition false
arrest and a biased welfare risk score are, mechanically, the same failure.

I wanted a tool that answers questions like *which failures recur everywhere?* and *what changed when generative
AI arrived?* — and, for any single incident, *show me similar ones and tell me why*. The constraint I set myself:
every label has to be traceable to evidence, and every number in the write-up has to come from a generated report.

## Three findings

**1. After ChatGPT, the incident record flipped from "AI fails" to "people misuse AI."** Of the 1,001 incidents I
coded, deliberate misuse — scams, deepfakes, harassment, disinformation — was the central mechanism in about one in
ten incidents before 30 November 2022 and in about half (50.7%) after it. Over the same split, robustness failures
fell from 44.5% to 15.7% of the mix and bias from 24.7% to 3.4%. Image and video generation went from 7% to 38% of
incidents; voice cloning from 2% to 18%. These are shares, not counts: bias incidents did not disappear, they were
swamped by a wave of misuse. And AIID records what journalists report and volunteers submit, so this is a shift in
the *visible* incident record, not a measured shift in the world.

**2. Some failures are genuinely sector-agnostic — and they are governance failures.** Ranking failure modes by
how evenly they spread across sectors, *inadequate testing or oversight* tops the list: it appears in all 20
sectors with a normalized entropy of 0.91. Bias and disparate performance and privacy violations (18 sectors each)
follow. At the other end, *harmful or unsafe output* is concentrated in consumer apps and social media. In the
constellation, the "Recurring failure modes" view links incidents that fail the same way, and the edge
explanations say so in plain words: *"same failure mode: bias & disparate performance; both use facial
recognition; one in policing, one in retail."*

**3. Severity is not attention.** I coded severity (0–4) separately from media coverage on purpose. They turn out
to be almost unrelated: Spearman ρ = 0.09 between the number of news reports and coded severity. Many of the most
covered incidents are embarrassments; several fatal ones have a single report. The app offers both as separate
size encodings, rather than letting report count masquerade as importance.

## Engineering decisions that mattered

### Evidence over impressions: verbatim grounding

The extraction step uses an LLM to read up to three report excerpts per incident and return a structured record:
summaries, multi-label tags across nine dimensions, severity, roles. The key design choice is the evidence
contract. A tag is either *inferred* (a reasonable reading) or *confirmed* — and a confirmed tag must carry a quote
of at most 25 words, which code then checks **verbatim** against the full cached report text, after normalizing
case, Unicode quotes, punctuation and whitespace.

Failures don't silently pass. They block loading until repaired by one of three logged rules: *reattribute* (the
quote is verbatim, but in a different report of the same incident), *snap* (a near-verbatim match is replaced by
the exact span), or *downgrade* to inferred. Across 4,763 quotes, 99.5% were verbatim on the first pass. The
validator caught two paraphrases that looked plausible — one quietly dropped the words "this week" from the middle
of a sentence — and fixed one misattributed citation. The other 17 downgrades were deliberate: verbatim quotes
that named a private person, which the privacy rule removes.

### Pilot first, then scale

Before coding at scale, I ran a 20-incident pilot stratified across years, report counts and risk domains, with
two models on the same prompt. It changed the design. Mapping my *failure mechanism* onto MIT's *risk domain*
turned out to be lossy (a facial-recognition false match is a robustness failure mechanically but a discrimination
risk), so I added a risk-domain dimension aligned to MIT's published taxonomy and adopted MIT's own definitions of
intent and cause. The pilot also showed the mid-size model was both faster and cheaper per batch than the small
one, which decided the bulk model.

### Evaluation as the differentiator

Because AIID ships expert labels, the coding can be graded. The coder never saw them. On 876 incidents with MIT
labels, the coded risk domain matches the expert domain 84.4% of the time (Cohen's κ = 0.80; majority baseline
30.1%). Sector agreement with CSET (Jaccard 0.71) is on par with how well CSET's own annotators agree with each
other (0.70) — a useful reminder that "ground truth" is itself noisy. Agreement with GMF's technical failure
labels is lower (Jaccard 0.42), and the disagreement analysis explains why: GMF codes low-level technical causes
that reports often don't state, while my prompt prefers a missing tag to a confident guess. A different model
re-coded a random sample of 30 incidents blind: risk-domain κ = 0.87 and severity weighted κ = 0.84, with every
severity within one band. Since both coders share the prompt, this measures the reliability of the *instructions*,
not independent judgement.

### Honest about coverage

Within the run's budget I coded 1,001 of 1,783 incidents. Rather than pretend otherwise, the batch planner ordered
work so that any stopping point is useful: the pilot, then every incident with CSET or GMF expert labels (so
evaluation is complete), then a stratified-random remainder (so the coded set is representative). The other 783
incidents get *predicted* tags from their nearest coded neighbours, cross-validated (65.3% risk-domain accuracy
against a 30.2% baseline) and labelled "predicted" everywhere, with a switch to turn them off. They never enter the
statistics above.

### Clusters you can defend

Clusters are chosen by silhouette in the original feature space times bootstrap stability, with seed stability
reported. My first run picked k = 7 with a perfect bootstrap ARI of 1.0 — suspicious. The cause: a one-hot
risk-domain block in the features split the space into seven islands, so the "clusters" just reproduced one
label. After removing that block and down-weighting tag features, the clusters read cleanly — voice-clone scams,
political deepfakes, non-consensual imagery, chatbot hallucinations, autonomous-vehicle failures, opaque
automated decisions, AI agents — but the honest finding is that the selection curve is *flat* (scores 0.088–0.097
for k = 8–19). The rule picks k = 18; adding nine incidents moved an earlier run from 8 to 18. So k is a
resolution choice, and the atlas says so. A perfect score that is too good is a bug report; a flat curve is a
limitation to state, not hide.

### A graph that doesn't jump

The 3-D constellation uses fixed positions from a 3-D UMAP projection, so nothing is simulated and nothing moves.
Filters only restyle. That held until a Playwright test checked it: dragging the year slider recreated hundreds of
node objects, because the graph library's visibility accessor removes hidden objects from the scene and rebuilds
them when they return. The fix was to toggle `object.visible` on cached three.js objects directly. The test now
asserts that all 1,784 node objects survive slider and colour changes with identical positions.

### Privacy by default

Incident entity lists name real people — often the people who were harmed. Every one of 5,934 entities was
classified (organization, government, product, group, public figure, private individual; private when in doubt).
1,055 private individuals are hidden from entity lists and redacted from titles and summaries, and tests assert
that no private name reaches the published summaries. Report text, which publishers own, never leaves the build
machine except as short, attributed, linked quotes.

## What I'd do next

Code the remaining 782 incidents (the pipeline is resumable and the plan is fixed); merge entity aliases such as
Facebook/Meta using AIID's entity relationships; extend excerpts beyond the first 2,500 characters for long
investigations; and add an "explain this cluster" view that surfaces the most typical incidents and their quotes.
The broader lesson holds regardless: with LLM-assisted coding, the interesting engineering is not the prompt — it
is the contract around it.
