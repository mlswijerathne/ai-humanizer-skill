# Calibration test cases

Three worked examples at increasing difficulty, used to validate that the skill
behaves sensibly across the spectrum and knows where to stop. Before/after risk
numbers come from `scripts/score.py` (a statistical-detector *estimate* only, not
a real detector and not a guarantee against trained classifiers like Pangram or
GPTZero 3.2b — see the script header and SKILL.md "Honest limitations").

## Summary

| Case | Difficulty | Risk before | Risk after | Burstiness CV (before → after) | Tells (before → after) | Artifacts (before → after) |
|---|---|---|---|---|---|---|
| Journaling | easy (free prose) | **75** likely AI | **0** likely human | 0.18 → 0.84 | 18 → 0 | 0 → 0 |
| Database index | medium (technical) | **67** leaning AI | **4.6** likely human | 0.43 → 0.55 | 6 → 0 | 2 → 0 |
| Math proof | hard (formal/rigorous) | **47** leaning human | **7.3** likely human | 0.31 → 0.52 | 3 → 0 | 0 → 0 |

Pattern worth noting: the *harder* and more rigorous the text, the *lower* the
before-risk. A math proof is already near the human-distribution floor because
formal proof prose is genuinely low-perplexity. That is exactly why statistical
detectors false-positive on rigorous human writing, and why humanization has the
least room to move there.

---

## Case 1 — Journaling (easy: free prose, ~95% movable)

**Before** (risk 75/100, likely AI):
> Journaling has emerged as a powerful tool for personal growth, offering a wealth
> of benefits that span emotional, cognitive, and creative domains. By putting pen
> to paper, individuals can delve into their innermost thoughts, fostering greater
> self-awareness and emotional clarity. Moreover, research underscores that regular
> journaling can play a crucial role in reducing stress, enhancing mental
> well-being, and cultivating resilience. It's not just about recording events;
> it's about embarking on a transformative journey of self-discovery. Ultimately,
> whether you're a seasoned writer or just beginning, journaling stands as a
> testament to the enduring power of reflection in an increasingly fast-paced world.

Diagnosis: 18 lexical tells, sentence lengths clustered 18–24 (CV 0.18), two
rule-of-three triads, negative parallelism, copula avoidance ("stands as a
testament").

**After** (risk 0/100, likely human):
> I started keeping a journal because my therapist suggested it, and I almost quit
> twice. Writing down what happened during the day felt pointless at first. Then
> around week three something shifted. I noticed I was figuring out what I actually
> thought about things only after I'd written a few messy paragraphs about them, not
> before. There's decent research behind this. Studies on expressive writing, going
> back to James Pennebaker's work in the 1980s, found that people who wrote about
> stressful events for fifteen minutes a few days running reported lower stress and
> even visited the doctor less. You don't need to be good at it. My entries are half
> grocery lists and half complaints. It still works.

Levers used: 1 (specific diction), 2 (sentence lengths 3–33, CV 0.84), 4 (a real
first-person voice with an arc). **Caveat:** the personal details are invented —
for real use they must be the user's true details. The Pennebaker reference is
real and checkable.

---

## Case 2 — Database index (medium: ~70% movable, terms locked)

**Before** (risk 67/100, leaning AI):
> Database indexes play a crucial role in optimizing query performance. At its core,
> an index is a data structure—typically a B-tree—that allows the database to
> quickly locate rows without scanning the entire table. By maintaining a sorted
> representation of one or more columns, indexes enable the database engine to
> perform efficient lookups, leveraging logarithmic time complexity rather than
> linear scans. However, it's important to note that indexes come with trade-offs:
> they consume additional storage and can slow down write operations, since every
> insert, update, and delete must also update the index. Ultimately, choosing the
> right indexing strategy is essential for building robust, high-performance
> applications.

Diagnosis: technical terms (B-tree, logarithmic complexity, insert/update/delete)
are correct and must NOT change — they are not tells. Movable: the fluff ("play a
crucial role," "At its core," "it's important to note," "leveraging," "robust").
Two em dashes.

**After** (risk 4.6/100, likely human):
> An index is just a sorted copy of one or more columns, usually stored as a B-tree.
> Without it, finding a row means reading every row in the table. With it, the
> database can binary-search instead, so a lookup that used to touch a million rows
> touches about twenty. That speedup isn't free. The index is extra data on disk,
> and the database has to keep it in sync, so every insert, update, and delete now
> does a second piece of work to patch the B-tree. The usual rule of thumb: index
> the columns you filter and join on, and don't index a table you mostly write to
> and rarely read.

Key discipline: perplexity was raised through **explanation** (the concrete "a
million rows touches about twenty", which is accurate: log₂ 1,000,000 ≈ 20), not
by roughening the locked terms. Accuracy verified: O(log n) lookup ✓, writes
update every index ✓.

---

## Case 3 — Math proof (hard: ~30% movable, the ceiling)

**Before** (risk 47/100, leaning human — already hard to flag):
> Let us consider the proposition that √2 is irrational. To prove this, we will
> employ a proof by contradiction. Suppose, for the sake of argument, that √2 is
> rational. Then it can be expressed as a fraction a/b in lowest terms, where a and
> b are integers sharing no common factors. Squaring both sides, we obtain 2 = a²/b²,
> which implies a² = 2b². This means that a² is even, and therefore a must also be
> even. We can thus write a = 2k for some integer k. Substituting back, we obtain
> 4k² = 2b², which simplifies to b² = 2k². This in turn implies that b² is even, and
> so b is even as well. However, this is a contradiction, since we assumed that a
> and b share no common factors. Therefore, our initial assumption must be false,
> and we conclude that √2 is irrational.

Diagnosis: ~65–70% of tokens are immutable mathematics. "Suppose… Then…
Therefore" is native human proof prose, NOT a tell (false-positive guard). Only
genuine fluff is movable: "Let us consider," "we will employ," "for the sake of
argument."

**After** (risk 7.3/100, likely human):
> Suppose √2 is rational. Then we can write it as a fraction a/b in lowest terms, so
> a and b are integers with no common factor. Square both sides: 2 = a²/b², which
> gives a² = 2b². So a² is even, and that forces a to be even, say a = 2k. Put that
> back in: 4k² = 2b², so b² = 2k². But now b² is even, so b is even too. That makes
> a and b both divisible by 2, contradicting "lowest terms." The assumption was
> wrong, so √2 is irrational.

The ceiling, demonstrated: only the connective prose moved. Burstiness improved
but the after-CV is still only 0.52 and σ 6.6 (just under the human target of 7),
because proof steps are atomic and can't be merged into long winding sentences
without obscuring the logic. Reordering steps is forbidden (it breaks the proof).
Every step was re-verified for correctness. **Lesson:** on rigorous text you clean
the surface tells and stop. If a detector still flags a correct standard proof,
that is the detector's false-positive failure (Liang et al.), not a text to
"humanize harder" — the right response is to dispute the detector, not corrupt the
math.

---

## How to reproduce

Paste any block above into a file (or pipe it) and score it:
```
python scripts/score.py mytext.txt
echo "Suppose √2 is rational. Then ..." | python scripts/score.py
```
The numbers above were produced with the scorer's default weights on the exact
texts shown. Re-running on those texts reproduces them; any edit shifts the score.
