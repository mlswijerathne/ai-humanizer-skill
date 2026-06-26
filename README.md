# ai-humanizer-skill

[![npm version](https://img.shields.io/npm/v/ai-humanizer-skill.svg)](https://www.npmjs.com/package/ai-humanizer-skill)
[![npm downloads](https://img.shields.io/npm/dm/ai-humanizer-skill.svg)](https://www.npmjs.com/package/ai-humanizer-skill)
[![license](https://img.shields.io/npm/l/ai-humanizer-skill.svg)](./LICENSE)
[![install](https://img.shields.io/badge/install-npx%20ai--humanizer--skill-blue)](https://www.npmjs.com/package/ai-humanizer-skill)

A [Claude](https://claude.com/claude-code) skill that rewrites AI-generated text so it reads as natural human writing **and** holds up against AI detectors. It goes beyond surface "signs of AI writing" and targets the signals detectors actually measure, then ships a scorer that estimates a before/after detection-risk number.

> **Honest disclaimer.** AI detectors are unreliable and uncalibrated. A Stanford study (Liang et al., 2023) found they flagged **61% of non-native-English essays** as AI. There is a proven impossibility result: as models approach human text, the best detector approaches a coin flip. This tool is for legitimate writing improvement — polishing AI-assisted drafts and helping people who are falsely flagged. No method beats every detector, and trained classifiers (Pangram, GPTZero 3.2b) may be unbeatable by tooling. Use it honestly.

## Install

```bash
# install for your user (~/.claude/skills)
npx ai-humanizer-skill install

# or into the current project (./.claude/skills)
npx ai-humanizer-skill install --project
```

Then restart Claude Code and run `/ai-humanizer`, or just ask Claude to "humanize this text".

Other commands:

```bash
npx ai-humanizer-skill where        # show install destination
npx ai-humanizer-skill uninstall    # remove it
npx ai-humanizer-skill --help
```

### Use on Claude.ai (web / desktop app)

`npx` installs into **Claude Code** only. To use the skill in the **Claude.ai web app**, upload it as a ZIP:

1. Download [`ai-humanizer.zip`](https://github.com/mlswijerathne/ai-humanizer-skill/releases/latest/download/ai-humanizer.zip) from the latest release.
2. In Claude.ai, go to **Settings → Customize → Skills** (also labeled "Capabilities" on some plans).
3. Click **+ Create skill** and upload `ai-humanizer.zip`.
4. Toggle the skill **on**, then ask Claude to humanize text.

**Requirements:** custom skill uploads need a **Pro / Max / Team / Enterprise** plan with **code execution enabled** (Settings → Capabilities). Code execution also lets the bundled `score.py` run in the web sandbox, so before/after scoring works there too. Uploaded skills are private to your account.

## What it does

AI detectors split into two families that need opposite tactics. The skill handles both:

| Family | Examples | Beaten by |
|---|---|---|
| **Statistical / zero-shot** | DetectGPT, Binoculars, GPTZero's perplexity component, most free tools | Genuinely raising **perplexity** (specific diction) and **burstiness** (varied sentence length), plus a real structural rebuild |
| **Trained neural classifier** | Pangram, GPTZero 3.2b, Originality.ai, Turnitin, Copyleaks | Matching a **real human voice** + a detector-feedback loop. Synonym swaps and generic humanizers are adversarially trained *into* these. |

Six levers: raise perplexity, raise burstiness, rebuild logic (not words), match a real voice, strip Unicode/formatting watermarks, and recursive/back-translation paraphrase for watermark removal. It refuses to break facts or over-edit formal writing.

## Before/after detection scoring

The skill bundles `scripts/score.py` (Python 3, standard library only). It estimates a **0–100 detection-risk score** from measurable signals — burstiness (σ/μ of sentence length), lexical-tell density, Unicode artifacts, and vocabulary richness.

```bash
python ~/.claude/skills/ai-humanizer/scripts/score.py mytext.txt
echo "some text" | python ~/.claude/skills/ai-humanizer/scripts/score.py
```

Example movement from the included test cases:

| Case | Risk before | Risk after |
|---|---|---|
| Free prose | 75/100 (likely AI) | 0/100 (likely human) |
| Technical | 67/100 | 4.6/100 |
| Math proof | 47/100 | 7.3/100 |

**Caveat:** the score estimates the *statistical* detector family only. A low score does **not** guarantee a trained classifier (Pangram, GPTZero) will pass the text. The only ground truth is running a real detector and feeding its sentence-level highlights back in — the skill's detector-feedback workflow does exactly that.

## Contents

```
skill/
├── SKILL.md                    operational guide (the skill Claude loads)
├── scripts/score.py            before/after detection-risk estimator
└── reference/
    ├── detector-landscape.md   per-detector teardowns + research citations
    └── test-cases.md           three worked before/after examples with scores
```

## Requirements

- Node.js >= 16 (for the installer)
- Python 3 (only for the optional `score.py`)
- Claude Code, or any host that loads `~/.claude/skills`

## License

MIT © mlswijerathne
