# AI Detector Landscape & Research Reference

Detailed teardown of how each major detector decides, what defeats it, and the
research behind the techniques in `SKILL.md`. Current as of mid-2026.

## The two families (why one strategy never covers both)

Detectors split into two mechanically different groups. A humanization pass that
beats one can be invisible to the other, so robust output has to satisfy both.

### Family A — Statistical / zero-shot detectors

No training on labeled examples; they score the text's *probability profile* under
a reference model.

- **Perplexity detectors** (the original GPTZero signal, many free tools): AI text
  has uniformly low perplexity because LLMs emit the most-probable next token.
  Beaten by genuinely raising perplexity (specific diction, concrete detail).
- **Burstiness**: variance of perplexity / sentence length across the document. AI
  is too even. Beaten by violently varied sentence and paragraph lengths.
- **DetectGPT** (Mitchell et al., 2023): perturbs the text and checks whether the
  original sits at a local maximum of model log-probability. AI text does; human
  text doesn't. Beaten by rebuilding sentence *logic*, not just words — so many
  alternative phrasings would have been roughly as probable.
- **Binoculars** (Hans et al., 2024, arXiv:2401.12070): ratio of an observer LLM's
  log-perplexity to the *cross-perplexity* between two LLMs. ~90%+ accuracy at a
  0.01% false-positive rate and notably **robust to stylistic noise and simple
  adversarial edits**. Implication: you cannot fool it by sprinkling rare words;
  the high-perplexity choices must be coherent human choices. This is why real
  structural variance and real voice matter even against a "statistical" detector.

### Family B — Trained neural classifiers

A transformer fine-tuned on millions of human-vs-AI samples; it learns the LLM
fingerprint directly and largely ignores hand-built perplexity features.

- **Pangram** (arXiv:2402.14873; "how it works" page): tokenize → embed → neural
  net → binary human/AI. Trained on ~1M docs, then hardened with **hard-negative
  mining** (repeatedly retrain on its own false positives toward a near-zero FPR)
  and **synthetic mirrors** (for each human sample, generate matched AI text on
  many axes, *including running it through humanizer tools like QuillBot*). So
  generic humanizer/paraphraser output is literally trained in as the AI class.
  Pangram 3.0 (Dec 2025) returns sentence-level tags + a confidence histogram and
  a four-tier label: Fully Human / Lightly AI-Assisted / Moderately AI-Assisted /
  Fully AI-Generated. Even light AI assistance flags.
- **GPTZero** (Model 3.2b, March 2025): a 7-component end-to-end deep-learning
  system — deep classifiers, a student-essay education module, sentence-level AND
  document-level prediction, mixed-content detection (which spans are AI), and an
  **ESL debiasing layer**. Explicitly shields against paraphrasing and homoglyph
  attacks. Retrained on recent LLM output including GPT-4.1, o3, Gemini 2.5,
  Claude/Sonnet 4.
- **Originality.ai, Turnitin, Copyleaks**: commercial trained classifiers in the
  same family; specifics undisclosed, behavior similar.

Takeaway: against Family B, perplexity/burstiness tricks and synonym swaps are
weak (they're adversarially trained in). The levers that work are matching a real
human distribution (voice-matching a real sample) and detector-feedback iteration.

## Watermarking (a separate axis)

Watermarks are inserted at generation time by the model owner; they're not a
property of "AI-ness" the way perplexity is.

- **Kirchenbauer green/red list** (2023): at each position, hash the preceding
  token to split the vocabulary into "green" and "red" sets and add a positive
  logit bias to green tokens. Detection counts the green-token surplus.
- **Google DeepMind SynthID-Text** (2024): tournament sampling via pseudorandom
  functions; same red-green family, less perceptible.
- **Vulnerability:** because the partition is keyed on the *preceding token*, any
  meaning-preserving rewrite that changes token order breaks detection —
  paraphrasing, copy-paste edits, and **back-translation** all degrade it
  substantially. A full architectural rebuild removes it incidentally.

## The research behind the techniques

- **Sadasivan et al., "Can AI-Generated Text be Reliably Detected?"**
  (arXiv:2303.11156, 2023). Paraphrasing attacks break watermarking, neural, and
  zero-shot detectors alike. **Recursive paraphrasing** (DIPPER applied multiple
  times, keeping the worst detection score) defeats even watermark and
  retrieval-based defenses. Proves a **theoretical impossibility result**: as an
  LLM approaches the human text distribution, the best-possible detector's
  accuracy approaches a random classifier.
- **Krishna et al., "Paraphrasing evades detectors... but retrieval is an
  effective defense"** (arXiv:2303.13408). The DIPPER paraphraser. Note the
  defense: providers who keep a database of their own generations can catch
  paraphrases by *retrieval* even when stylistic detection fails — relevant only
  when the text came from a provider running such a service.
- **Cheng, Sadasivan, et al., "Adversarial Paraphrasing: A Universal Attack for
  Humanizing AI-Generated Text"** (arXiv:2506.07001, NeurIPS 2025). Training-free
  attack: an instruction-following LLM paraphrases *under the guidance of a
  detector*, producing examples optimized to bypass it. Broadly effective and
  **transferable** across detectors, with little quality loss. Key insight:
  high-performing detectors converge toward a common "human text" distribution, so
  optimizing against one transfers to others. This is the basis for the
  detector-feedback workflow in SKILL.md.
- **Liang et al., "GPT detectors are biased against non-native English writers"**
  (arXiv:2304.02819; *Patterns*, 2023). Detectors flagged **61.3%** of non-native
  TOEFL essays as AI vs ~5.1% for native samples — because limited lexical variety
  lowers perplexity. Confirms lexical richness/variability is the human signal and
  grounds the legitimate-use framing.
- **SilverSpeak** (arXiv:2406.11239): homoglyph substitution evades some
  detectors — but GPTZero/Pangram now detect it, so it backfires. Only ever
  *remove* homoglyphs, never add them.

## Practical decision guide

- **User doesn't know which detector / wants general robustness** → apply all six
  levers; lead with voice-matching (Lever 4) and structural rebuild.
- **Target is a perplexity/zero-shot detector (Binoculars, DetectGPT, free tools)**
  → Levers 1-3 (perplexity, burstiness, logic rebuild) carry the most weight.
- **Target is a trained classifier (Pangram, GPTZero, Originality, Turnitin)** →
  Lever 4 (real voice) + the detector-feedback loop; accept it may not fully clear.
- **Text may carry a watermark (came from a known provider)** → add Lever 6
  (recursive paraphrase / back-translation) on top.
- **Always** finish with Lever 5 (strip artifacts) and verify meaning held.

## Source list

- GPTZero — perplexity/burstiness, technology, Model 3.2b notes: gptzero.me
- Pangram — how-it-works, technical report (arXiv:2402.14873), Pangram 3.0
- Binoculars — arXiv:2401.12070
- DetectGPT — Mitchell et al., openreview UiAyIILXRd
- Can AI Text Be Reliably Detected? — arXiv:2303.11156
- Paraphrasing evades detectors / DIPPER — arXiv:2303.13408
- Adversarial Paraphrasing (NeurIPS 2025) — arXiv:2506.07001
- GPT detectors biased against non-native writers — arXiv:2304.02819
- SilverSpeak homoglyph evasion — arXiv:2406.11239
- LLM watermarking surveys & SynthID analysis — arXiv:2603.03410, ACM CSUR 3691626
