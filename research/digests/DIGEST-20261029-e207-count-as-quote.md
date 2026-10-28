# E207 — the classifier's blind spot has a volume

Date: 2026-10-29 | round r1235 (bm-b) | dept: research + engineering
Face: `results/e79/QUOTECOUNT-2026-10-28.json`
Code: `scripts/e97_routing.py` mode `quotecount` (selftest 107/107)
Pool: E207-COUNT-AS-QUOTE-AUDIT (done) | card: `knowledge/METHODOLOGY_ASSETS.md` E207

## What was asked

E180 classifies numeric leaves **by name** and files them as book levels, gaps, or derived
sums. E206 admitted in its own honest block that the delta-token test cannot see a delta
spelled `engine_gap_bp`. The pool row asked for the same admission to be **counted**: sweep
`results/` for measurement-named cells that could not be a bp quote at all, so a name-based
audit can be told apart from a real quote instead of inventing one.

## What the sweep found

| | |
|---|---|
| faces scanned | 12,111 (4 skipped by size cap, 56 unreadable, 7 are this leg's own face) |
| measurement-named cells | 71,245 |
| candidates that cannot be a bp quote | **37,817** across **667** faces |
| — `count_word` (the name says "number of things") | 30,357 |
| — `small_integer` (no count word, ceiling 100 bp) | 5,732 |
| — `boolean` (a flag under a measurement name) | 1,728 |
| non-integral (`quote_shaped`) | 27,601 |
| integral but quote-sized (`integral_quote_sized`) | 5,827 |
| inside the two dirs the existing auditor scans | 3,759 |
| outside them | 34,058 |
| distinct leaf names | 915 |

Headline names: `gapped_kept` 15,682 occurrences over 65 faces, `gap_sessions` 11,619 over 58.
`level_class("gap_sessions")` returns `offset` — the auditor would print it as an offset of
11,619 bp.

## The ceiling is a line, so the face publishes the line's sensitivity

Integrality is a signature, not proof: `exit_fwd_bp = 5776.0` is a real reading and is filed as
`integral_quote_sized`, not charged to the page.

| ceiling | integral notes without a count word |
|---|---|
| 10 bp | 4,186 |
| 100 bp | 5,732 |
| 1000 bp | 9,446 |

## Two defects the leg found in its own plumbing

1. `evidence_cutoff` is not always a date. `results/_r1023bmc_w20_supply_audit.json` stores
   `"panel 2026-10-14 (bars 10-15 due 15:30)"`; copied into a filename the colon produced a
   **zero-byte face**. The published cutoff now comes from strict ISO dates only, and the two
   pages that misuse the field are named in `non_iso_evidence_cutoffs`.
2. The face publishes into a directory it scans, so its own study (and its previous file) must be
   excluded or the audit counts itself — E180's 25 -> 26 lesson. Both are excluded and counted
   (`skipped_this_leg_publishes_here = 7`).

## What it does not claim

No number is rewritten and no number is re-derived. This is an inventory of a name-channel
hazard: it answers "could a reader quote this as bp", never "is this number wrong". The
follow-up that changes code is seeded as E208 (teach `level_class` the count vocabulary and
measure the class-count delta), with E209 (prove counts by sibling length) and E210 (test the
numbers on the CEO-facing pages) behind it.