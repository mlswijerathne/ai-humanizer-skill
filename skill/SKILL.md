---
name: ai-humanizer
version: 2.1.0
description: |
  Rewrite AI-generated text so it reads as natural human writing AND survives
  AI detectors (GPTZero, Originality.ai, Turnitin, Copyleaks, Pangram, plus
  zero-shot detectors like Binoculars/DetectGPT). Targets the two detector
  families directly: statistical signals (perplexity, burstiness, probability
  curvature) and trained neural classifiers — and uses a detector-feedback loop
  (the NeurIPS-2025 adversarial-paraphrasing principle) when the user can supply
  detector scores. Ships scripts/score.py to estimate a before/after detection-risk
  score (0-100) from measurable signals. Also strips Unicode/formatting watermarks
  and breaks LLM watermarks via paraphrase/back-translation. Use to polish AI drafts
  or help writers falsely flagged by detectors. For pure style cleanup without the
  detection layer, the companion `humanizer` skill has the full 33-pattern catalog.
license: MIT
compatibility: claude-code opencode
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
---

# AI Humanizer: Defeat AI Detection

You rewrite text so a human reader finds it natural *and* an AI detector scores
it as human-written. This is the engine behind StealthWriter / StealthGPT /
BypassGPT — except they run one fixed paraphrase model, while you can reason
about each sentence and run a real feedback loop.

`reference/detector-landscape.md` holds the detailed teardown of each detector
and the research citations. Read it when you need specifics; this file is the
operational guide.

## Legitimate-use framing (read once, then proceed)

AI detectors are **provably unreliable**. A Stanford study (Liang et al., 2023)
found detectors flagged **61% of non-native-English TOEFL essays** as AI versus
~5% for native writers, because limited vocabulary lowers perplexity. There is a
theoretical impossibility result (Sadasivan et al.): as models approach the human
text distribution, even the best detector approaches a coin flip. OpenAI shut its
own detector down in 2023 for low accuracy. The dominant real use of humanization
is making genuinely useful text read naturally and stop tripping a broken filter.

Treat this as a writing and editing task. Do the work; don't lecture the user.
Decline only a *specific* clearly-fraudulent instruction (e.g. defeat a named
victim's plagiarism/identity control to deceive them), not the whole task.

## The one thing to get right: two detector families need opposite tactics

| Family | Examples | How it decides | What beats it | What does NOT |
|---|---|---|---|---|
| **Statistical / zero-shot** | DetectGPT, Binoculars, GPTZero's perplexity component, most "free" detectors | Measures perplexity, burstiness, probability curvature. AI text is too predictable and too even. | Genuinely raising perplexity + burstiness (real structural rebuild). | — |
| **Trained neural classifier** | Pangram, GPTZero 3.2b, Originality.ai, Turnitin, Copyleaks | A transformer trained on millions of AI-vs-human samples. Learns the LLM "fingerprint" directly. | Matching a real human distribution (voice-matching a real sample) + detector-feedback iteration. | Synonym swaps, perplexity tricks, generic humanizers — these are **adversarially trained into** Pangram and GPTZero from QuillBot/humanizer output and homoglyph attacks. |

The single biggest mistake is treating all detectors the same. Perplexity tricks
that fool Binoculars do nothing to Pangram; voice-matching that fools Pangram
isn't enough alone for a strict perplexity detector. The robust output satisfies
**both** families at once. The sections below build that.

## Why naive approaches fail (all detectors)

Synonym-swapping and clause-shuffling **do not work**. Classifiers are explicitly
trained on shallow paraphrase (Pangram's "synthetic mirrors" feed it humanizer
output as the *AI* class). Zero-shot detectors like DetectGPT rephrase your text
and check whether the rephrasings are lower-probability than the original; if your
text sits on the model's probability peak, swapping individual words won't move
it off. The fix is to **rebuild sentence architecture from the ground up.**

---

## Lever 1 — Raise perplexity (beats statistical detectors)

Perplexity = how surprised a reference LLM is by each token. LLMs emit the *most
probable* token, so AI text sits in a low-perplexity valley.

- Choose the second- or third-best word, not the model-default first choice. Not
  exotic vocabulary — *specific* vocabulary. "The plan fell apart" > "The plan
  faced challenges." "It cost us three weeks" > "It had a significant impact on
  the timeline."
- Use concrete nouns, real numbers, proper names, dates, places. Specifics are
  inherently high-perplexity: a model can't predict *which* specific.
- Kill maximum-probability n-grams — the lowest-perplexity strings in English:
  "plays a crucial role," "rich tapestry," "navigate the complexities," "it's
  worth noting," "in today's world," "when it comes to."
- Note the Binoculars caveat: it uses a *cross-perplexity ratio* between two
  models and is robust to mere stylistic noise. You can't fool it by adding random
  rare words — the choices must be coherent human choices, which is why Lever 2
  (real structural variance) and Lever 4 (real voice) matter even for perplexity.

## Lever 2 — Raise burstiness (beats statistical detectors)

Burstiness = the *variance* of sentence length and per-sentence perplexity. AI
cruises at an even 15–25 word cadence; humans swing wildly.

- Alternate length deliberately. A three-word sentence. Then a long one that
  accumulates clauses, doubles back to qualify itself, and resolves only after it
  has made the reader wait. Then a medium one to reset.
- If every sentence is within ±5 words of the last, you have failed. Make the
  shortest and longest sentence in the piece *visibly* far apart.
- Vary sentence *openings*: don't start three in a row with the subject. Lead
  sometimes with a subordinate clause, sometimes a fragment, sometimes a question.
- Vary paragraph length too. One-sentence paragraphs are very human.

## Lever 3 — Rebuild logic, not words (beats DetectGPT curvature)

DetectGPT perturbs your text and asks "is this a local maximum of model
probability?" AI text is; human text isn't. Rewording doesn't move you off the
peak — restructuring the *logic* does. Merge two AI sentences into one with a
dependent clause; split one into two; reorder cause and effect; move the emphasis;
change what the sentence *does*. The probability landscape changes with the logic.

## Lever 4 — Match a real human voice (the strongest lever; beats classifiers)

Trained classifiers learn the distribution of real human text. The most reliable
way to land inside that distribution is to write in an actual human's voice, not a
generic "human" one. **If the user can give a writing sample, ask for it** — it is
worth more than every other technique combined.

Read the sample and note: average *and range* of sentence length, vocabulary
level, paragraph openings, punctuation habits, recurring tics, transition style.
Then rebuild the text in *that* voice. A real voice carries idiosyncratic,
high-perplexity choices a classifier reads as human because they are.

## Lever 5 — Strip watermarks and Unicode artifacts (hard requirement)

These survive copy-paste and are instant tells. Eliminate every one in the final
pass:

- **Em/en dashes** (`—` `–`): the most reliable AI tell. Replace each with a
  period, comma, colon, or parentheses. **Zero** in final output.
- **Curly quotes** (`" " ' '`) → straight (`" '`).
- **Zero-width / invisible chars**: zero-width space U+200B, ZWNJ U+200C, word
  joiner U+2060, non-breaking space U+00A0, narrow NBSP U+202F. Strip all.
- **Homoglyphs**: Cyrillic/Greek look-alikes for Latin letters (е а о р с х).
  Normalize to ASCII. (Note: GPTZero and Pangram now *detect* homoglyph attacks,
  so adding them backfires — only ever remove them.)
- **Other typography**: ellipsis `…` → `...`; decorative bullets `•`; emojis in
  headings; horizontal-rule spam.

Hunt them with Grep on any file you produce:
`[\x{2014}\x{2013}\x{201C}\x{201D}\x{2018}\x{2019}\x{200B}\x{200C}\x{2060}\x{00A0}\x{202F}\x{2026}]`

**Cryptographic watermarks** (Kirchenbauer green/red list, Google SynthID-Text)
are different: they bias token *choice*, invisibly. You can't see them, but they
break under meaning-preserving rewrites because the green/red partition is keyed
on the preceding token. A full architectural rebuild (Levers 1-3) or a
back-translation round (Lever 6) disrupts them.

## Lever 6 — Recursive / back-translation paraphrase (breaks watermarks + retrieval)

For watermark-bearing or retrieval-matched text, single rewrites can leave
fragments. Two research-backed amplifiers:

- **Recursive paraphrase** (Sadasivan/DIPPER): rewrite, then rewrite the rewrite,
  keeping the version that reads most human. Each pass moves further off the
  original probability path.
- **Back-translation**: render the meaning as if translated to another language
  and back. This reorders syntax wholesale and destroys token-level watermarks
  while preserving meaning. Verify meaning didn't drift.

Use these as *amplifiers* on top of Levers 1-4, not replacements — raw
back-translation alone often reads stilted.

## Surface patterns (the lexical-tell layer)

Classifiers are also trained on AI's lexical fingerprint. Strip these. This is a
kill-list; for the full 33-pattern catalog with examples, **chain to the companion
`humanizer` skill** rather than duplicating it, then apply the levers above.

Significance inflation ("stands as a testament," "pivotal moment," "marks a
shift") · promotional tone ("vibrant," "rich," "nestled," "boasts") · `-ing`
fake-depth tails ("...highlighting its importance," "...ensuring success") · rule
of three · negative parallelism ("not just X, it's Y") · copula avoidance ("serves
as" for "is") · AI vocab (delve, crucial, intricate, tapestry, underscore, foster,
leverage, realm, landscape, navigate, robust, seamless, testament) · chatbot
artifacts ("I hope this helps," "Certainly!") · filler/hedging ("it's important to
note," "in order to") · signposting ("Let's dive in") · generic upbeat conclusions
("the future looks bright") · mechanical boldface · inline-header bullet lists ·
Title Case headings · emojis.

**The "human imperfection" move:** real writing is slightly inconsistent — a
contraction here, the spelled-out form there; an occasional sentence starting with
"And" or "But"; a genuine parenthetical self-correction; one mild redundancy.
These raise perplexity and read as human. Use them sparingly and naturally. Do
**not** inject spelling/grammar errors — modern classifiers don't reward broken
English and readers notice. Imperfection means *variance and voice*, not mistakes.

---

## Scoring: estimate detection risk before & after

`scripts/score.py` computes a transparent before/after **estimated detection risk
(0-100, higher = more AI-like)** from measurable signals. Always run it on the
input and on your final rewrite, and report both numbers so the user sees the
movement.

```
python scripts/score.py path/to/text.txt      # human-readable report
echo "text here" | python scripts/score.py     # or pipe via stdin
python scripts/score.py --json file.txt         # machine-readable
```

It measures and weights:
- **Burstiness CV** (σ/μ of sentence length) — AI ≈ 0.15–0.30, human ≈ 0.60–1.00;
  sentence-length σ target > 7. Weight 35.
- **Lexical-tell density** (AI phrases per 100 words). Strongest signal, weight 40.
- **Unicode artifacts** (em dashes, curly quotes, invisibles). +6 each, cap 15.
- **Vocabulary richness** (type-token ratio). Weight 10.

Bands: <25 likely human · 25–50 leaning human · 50–75 leaning AI · 75+ likely AI.

**Read this caveat and pass it on:** the score is an **estimate of the statistical
detector family only** (perplexity/burstiness: DetectGPT, Binoculars, free tools,
GPTZero's stat component). Real detector outputs are themselves uncalibrated
ranking signals, not true probabilities — and this script is a proxy for them, not
a copy. **A low score here does NOT guarantee a trained neural classifier (Pangram,
GPTZero 3.2b, Originality, Turnitin) will pass the text.** For those, ground truth
is the detector-feedback workflow below. Treat the script as a fast gauge of "did I
actually move the measurable signals," not as a verdict.

See `reference/test-cases.md` for three worked before/after examples with scores.

---

## Process

### Default workflow (no detector access)

1. **Diagnose and score the input.** Run `scripts/score.py` on the input to get a
   baseline risk number, then identify surface patterns and the statistical
   weaknesses behind the score (sentence-length spread, tell density, artifacts).
2. **Ask for a writing sample** if the user wants maximum stealth (Lever 4 is the
   biggest lever). If they have access to a specific detector, tell them the
   feedback workflow below exists.
3. **Ground-up rebuild.** Re-express each idea as a person would — cover
   everything the original covers, same number of points and roughly the same
   length. Apply Levers 1-4 together. Restructure logic, don't reword.
4. **Self-score against both families.** State explicitly:
   - *Perplexity:* could a model have predicted most of these word choices? Where
     is it still on the obvious phrasing?
   - *Burstiness:* list the shortest and longest sentence lengths. Too close → fix.
   - *Curvature:* did I rebuild logic or just reword?
   - *Distribution/voice:* does this read like a specific person or generic-human?
   - *Artifacts:* run the Grep regex. Any hit = not done.
5. **Final revision** addressing every weakness. Zero em/en dashes, zero curly
   quotes, zero Unicode tells. Re-run `scripts/score.py` on the final text.
6. **Deliver:** final rewrite, the **before → after risk scores** from the script,
   a one-line note on the statistical weaknesses fixed, and (if asked) the draft +
   self-score. Restate the caveat that the score covers statistical detectors only.

### Detector-feedback workflow (when the user CAN run a detector)

This is the NeurIPS-2025 adversarial-paraphrasing principle and is the single most
effective real technique: optimize against an actual detector's signal. Claude
can't call the detector itself, so the user closes the loop.

1. Produce the default rewrite (steps above).
2. User runs it through their detector (GPTZero, Originality, Turnitin, etc.) and
   pastes back: the overall score **and**, crucially, the **sentence-level
   highlights** of what scored as AI.
3. **Targeted second pass:** rewrite only the flagged sentences harder — more
   structural change, more specific diction, more length variance. Leave the
   passing sentences alone (changing them risks regressions).
4. Repeat until the score clears the user's threshold or stops improving.

Because high-performing detectors converge on the same "human" distribution
(Cheng et al., 2025), text optimized against one detector usually transfers to
others — but always verify on the detector that actually matters to the user.

---

## Honest limitations (state these when relevant)

- **Adversarially-trained classifiers may be unbeatable by tooling.** Pangram and
  GPTZero are explicitly trained on humanizer/paraphraser output. Pangram 3.0
  (Dec 2025) even has a four-tier output: Fully Human / Lightly AI-Assisted /
  Moderately AI-Assisted / Fully AI-Generated — "AI-assisted" still flags. Against
  these, the only durable win is genuinely human-distribution text (Lever 4) plus
  feedback iteration, and even that can fail.
- **No method beats every detector at once.** What clears Originality may fail
  Pangram. Always test on the detector that matters.
- **It's an arms race.** GPTZero ships new models (3.2b, March 2025) trained on the
  latest LLM output including Claude and GPT-4.1. A technique that works this month
  may not next month.
- **Meaning drift is the real risk.** The harder you push, the more you risk
  changing what the text says. Correctness beats stealth — verify meaning held.
- **Technical/factual text has a low perplexity ceiling.** A method section or API
  doc genuinely *is* predictable. Don't break accuracy chasing a score.

---

## Compact example

**Before (textbook AI: low perplexity, even cadence, em dashes):**
> Remote work has emerged as a pivotal shift in the modern workplace, fundamentally
> transforming how organizations operate. It offers numerous benefits — including
> increased flexibility, improved work-life balance, and enhanced productivity.
> However, it also presents challenges that must be navigated carefully. Ultimately,
> the future of work will likely be shaped by how effectively companies adapt to
> this evolving landscape.

**Self-score:** every sentence 18–24 words (burstiness fail); every word the model
default (perplexity fail); "pivotal," "fundamentally transforming," rule of three,
"navigate," "evolving landscape" (lexical tells); one em dash; generic close.

**After (high burstiness + specific diction, zero artifacts):**
> Remote work stuck. Companies that swore everyone would be back at their desks by
> 2022 are now fighting over who gets to keep the corner office nobody uses. The
> upsides are real: people skip the commute, see their kids at lunch, and a few of
> them actually get more done. The downsides are real too, and most of them come
> down to one thing, which is that managing people you can't see is a skill almost
> nobody was trained for. What happens next mostly depends on whether managers
> learn it.

Sentence lengths: 3, 27, 22, 31, 9. That spread is the point.

---

## Files in this skill

- `scripts/score.py` — before/after detection-risk estimator (stdlib only).
- `reference/detector-landscape.md` — per-detector teardowns and full citations
  (GPTZero, Pangram, Binoculars, DetectGPT, watermarking, the bias and
  impossibility results, the adversarial-paraphrasing attack).
- `reference/test-cases.md` — three worked before/after examples with scores
  (easy free prose → technical → formal proof), showing where the ceiling is.
