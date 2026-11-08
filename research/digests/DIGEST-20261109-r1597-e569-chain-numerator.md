# DIGEST 2026-11-09 r1597 bm-b — E569: the receipt counts itself correctly, the sentence that quotes it does not

**Card**: E569 — "Take every receipt on disk that carries both a legs array and a legs_rc0 count,
and price the numerator of the sentence that reported it."
**Face**: `results/state_tilt/CHAINNUMERATOR-2026-11-08.json` (+ `chainnumerator_latest.json`)
**Study**: `scripts/e569_chain_numerator.py` — build / check / verify / selftest (8/8)

## Reading

326 receipts are on disk under `results/_r*bm*_s6_chain.json`.

* **225 state an rc0 count** and **225 of 225 agree** with a recount of their own rows.
  Zero disagree, zero use an offset field (`nonzero_count` / `nonzero_legs` / `nonzero`).
* **101 state no count at all** (bare lists, old envelopes) — published apart, never as a
  disagreement.
* **0 understate their own rc0**, **0 claim a failing row is green**.
* Of the **38** receipts E567 joins to a printed sentence, **35** print exactly their own rc0.
  **3 do not**, and each is a different shape:

| receipt | printed | its own rows | E561 class |
|---|---|---|---|
| `_r1246bmb_s6_chain.json` | 25/25 | 28 rows, all rc=0 → rc0 28 | covers the table of its round |
| `_r1285bmb_s6_chain.json` | 7/7 | 1 row, rc0 1 | shorter than the table of its round |
| `_r406bma_s6_chain.json` | 6/36 | 36 rows, all rc=0 → rc0 36 | no runner blob reachable for that round |

## Why this is worth a face

The 225/225 self-consistency is the load-bearing negative result: the arithmetic inside the
receipt files is clean, so every remaining defect lives in the *reference* — which file a
sentence quotes, and which run that file belongs to. That removes one hypothesis (drifting
counters inside files) and localises the other (population / run identity), which is exactly the
channel E570 left open ("the remaining defect channel is population only").

The three residual rows are not one defect:

* `_r1246bmb` is the case the card was written from — a 28-row all-green file printed as 25/25,
  three legs vanishing from the prose with no failure to explain it.
* `_r1285bmb` is a family sentence (`--only star_*`) quoted against a one-leg receipt, so the
  numerator and the denominator belong to different populations.
* `_r406bma` is a file that is complete on disk while the sentence describes the death of that
  same chain at leg 6 — a rewritten receipt, or a sentence about a different run.

E572 prices exactly which of the three it is, per file, from the bytes.

## Method notes (reusable)

1. **A self-consistent file does not certify the sentence.** Keep "is the file's own arithmetic
   right" and "does anything quote the file correctly" as separate arms; a single agreement rate
   mixes them.
2. **An offset field must be converted before comparison.** `nonzero_count` states failures, so
   its rc0 is `len(rows) - value`. Comparing raw would have flipped four correct old envelopes.
3. **An absent field is not a disagreeing field.** 101 receipts state nothing; they belong in
   their own counter, not the denominator of "wrong counts".
4. **Reuse the upstream join, never re-parse the prose.** The printed numerator comes from E567's
   published claim face by `(round, machine)`, so this study cannot invent a second reader that
   drifts from the first.
5. **The receipt directory is live** — this round's own S6 leg appended `_r1597bmb_s6_chain.json`,
   so `check` compares the recount of what is on disk rather than demanding byte identity with the
   publication moment.

## Boundary

Pure static; only the receipts and two published faces are read. No runner is executed, no
receipt is rewritten, and the cause of the three disagreements is deliberately not decided here —
that is E572.