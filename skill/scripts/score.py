#!/usr/bin/env python3
"""
ai-humanizer detection-risk estimator.

Produces a transparent, computable ESTIMATE of how a STATISTICAL AI detector
(perplexity/burstiness family: GPTZero's stat component, DetectGPT, Binoculars,
most free tools) is likely to score a passage, plus the raw features behind it.

IMPORTANT — what this is NOT:
  * Not a real detector and not calibrated. Detector vendors themselves say their
    0-100 outputs are ranking signals, not true probabilities. So is this.
  * It cannot replicate a TRAINED NEURAL CLASSIFIER (Pangram, GPTZero 3.2b,
    Originality, Turnitin, Copyleaks). A low score here does NOT guarantee those
    will pass the text. The only ground truth is the detector-feedback workflow:
    run the real detector and paste back its sentence-level highlights.

Use it to (a) show before/after movement on the measurable signals, and
(b) locate which signal is still weak so you know which lever to pull.

Usage:
    python score.py path/to/file.txt
    echo "some text" | python score.py
    python score.py --json path/to/file.txt
"""
import sys
import re
import json
import math

# High-precision AI lexical tells. Density-based scoring means one stray hit
# barely moves the needle; clusters do. Substring match, case-insensitive.
TELLS = [
    "crucial", "delve", "underscore", "leverage", "tapestry", "pivotal",
    "intricate", "seamless", "robust", "foster", "realm", "navigate the",
    "testament", "vibrant", "nestled", "boasts", "showcase", "emerged as",
    "at its core", "it's important to note", "it is important to note",
    "in today's", "when it comes to", "plays a crucial role", "rich tapestry",
    "wealth of", "transformative", "for the sake of argument", "let us consider",
    "we will employ", "moreover", "furthermore", "evolving landscape",
    "fast-paced world", "not just about", "comes with trade-offs",
    "putting pen to paper", "innermost thoughts", "self-discovery",
    "ultimately,", "in conclusion", "the future looks bright", "a wealth of",
    "play a crucial role", "stands as", "serves as", "wide range of",
]

# Unicode artifact tells that survive copy-paste (em/en dash, curly quotes,
# zero-width chars, NBSP, narrow NBSP, ellipsis char). Math/legit glyphs excluded.
ARTIFACTS = "—–“”‘’​‌⁠  …"


def split_sentences(text):
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p for p in parts if p.strip()]


def word_count(s):
    return len(re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?", s))


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def score(text):
    sents = split_sentences(text)
    lengths = [word_count(s) for s in sents if word_count(s) > 0]
    total_words = sum(lengths)
    n = len(lengths)

    if total_words < 25 or n < 3:
        return {
            "estimated_detection_risk": None,
            "band": "too short to score",
            "note": "Need at least ~25 words and 3 sentences; statistical signals "
                    "are meaningless on shorter text (real detectors agree).",
            "features": {"sentences": n, "words": total_words},
        }

    mu = total_words / n if n else 0.0
    if n > 1:
        var = sum((l - mu) ** 2 for l in lengths) / (n - 1)
        sigma = math.sqrt(var)
    else:
        sigma = 0.0
    cv = sigma / mu if mu else 0.0  # coefficient of variation == burstiness index

    words = re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower())
    ttr = len(set(words)) / len(words) if words else 0.0

    low = text.lower()
    tell_hits = []
    for t in TELLS:
        c = low.count(t)
        if c:
            tell_hits.append((t, c))
    tell_total = sum(c for _, c in tell_hits)
    tell_density = (tell_total / total_words * 100) if total_words else 0.0

    artifact_count = sum(text.count(ch) for ch in ARTIFACTS)

    # --- composite estimated detection risk (0-100, higher = more AI-like) ---
    # Burstiness: CV>=0.60 human, <=0.20 AI (per detector literature). Weight 35.
    burst_risk = clamp((0.60 - cv) / (0.60 - 0.20), 0, 1) * 35
    # Lexical tells: 0/100w none, >=4/100w saturated. Weight 40 (strongest signal).
    tell_risk = clamp(tell_density / 4.0, 0, 1) * 40
    # Artifacts: +6 each, capped 15.
    art_risk = min(artifact_count * 6, 15)
    # Vocabulary richness: TTR>=0.55 rich, <=0.35 repetitive. Weight 10.
    ttr_risk = clamp((0.55 - ttr) / (0.55 - 0.35), 0, 1) * 10
    risk = clamp(burst_risk + tell_risk + art_risk + ttr_risk, 0, 100)

    if risk < 25:
        band = "likely human"
    elif risk < 50:
        band = "leaning human"
    elif risk < 75:
        band = "leaning AI"
    else:
        band = "likely AI"

    return {
        "estimated_detection_risk": round(risk, 1),
        "band": band,
        "features": {
            "sentences": n,
            "words": total_words,
            "mean_sentence_len": round(mu, 1),
            "stdev_sentence_len": round(sigma, 1),
            "burstiness_cv": round(cv, 3),
            "type_token_ratio": round(ttr, 3),
            "lexical_tells": tell_total,
            "tell_density_per_100w": round(tell_density, 2),
            "unicode_artifacts": artifact_count,
        },
        "components": {
            "burstiness_risk": round(burst_risk, 1),
            "tell_risk": round(tell_risk, 1),
            "artifact_risk": round(art_risk, 1),
            "ttr_risk": round(ttr_risk, 1),
        },
        "tell_hits": tell_hits,
    }


def fmt(r):
    if r["estimated_detection_risk"] is None:
        return f"  {r['band']}: {r['note']}\n  (sentences {r['features']['sentences']}, words {r['features']['words']})"
    f, c = r["features"], r["components"]
    out = []
    out.append(f"  Estimated detection risk: {r['estimated_detection_risk']}/100  ({r['band']})")
    out.append(f"    (statistical-detector estimate only; NOT a guarantee vs trained classifiers)")
    out.append(f"  Burstiness CV: {f['burstiness_cv']}  (AI ~0.15-0.30, human ~0.60-1.00)  "
               f"[sentence-len stdev {f['stdev_sentence_len']}, target >7]")
    out.append(f"  Lexical tells: {f['lexical_tells']}  ({f['tell_density_per_100w']}/100w)")
    out.append(f"  Vocab richness (TTR): {f['type_token_ratio']}")
    out.append(f"  Unicode artifacts: {f['unicode_artifacts']}")
    out.append(f"  Sentences/words: {f['sentences']}/{f['words']}  mean len {f['mean_sentence_len']}")
    out.append(f"  Risk breakdown -> burst {c['burstiness_risk']} + tells {c['tell_risk']} "
               f"+ artifacts {c['artifact_risk']} + ttr {c['ttr_risk']}")
    if r["tell_hits"]:
        hits = ", ".join(f"{t}×{n}" if n > 1 else t for t, n in r["tell_hits"])
        out.append(f"  Tells found: {hits}")
    return "\n".join(out)


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv
    if args:
        with open(args[0], encoding="utf-8") as fh:
            text = fh.read()
    else:
        text = sys.stdin.read()
    r = score(text)
    print(json.dumps(r, ensure_ascii=False, indent=2) if as_json else fmt(r))


if __name__ == "__main__":
    main()
