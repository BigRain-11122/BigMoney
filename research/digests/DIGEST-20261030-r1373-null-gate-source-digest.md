# r1373 — the gate that could not tell "refresh me" from "someone edited me"

Window: 2026-10-30T23:30+08:00 · bm-c · round 1373 · product, no inheritance owed.

## What was open

r1372 closed the mtime family by sweeping five gates in `scripts/etf_book_phase_atlas_arms.py`
and left one named debt on the page: *"`scripts/etf_book_rule_null.py` still re-implements the
cutoff read instead of importing `_source_moved`, which is where the two copies can drift
apart."* The duplicated read was the smaller half of the problem.

## The defect

`etf_book_rule_null.check()` decided stale-vs-inconsistent by one signal only: *is the arms face
priced on a later bar than this one?* That question cannot see the commonest way this source
moves. The arms face is re-derived on the **same** bar all day (`results/etf_book_phase_atlas_arms.json`
was regenerated at 14:05 and again at 14:20 on 2026-10-29 during r1361). When that happens the
null face's own numbers change — every label frequency is simulated from the arms rows — while
the cutoff does not move at all. The gate then reports:

    face is inconsistent: N field(s) disagree and no source is priced later

i.e. rc=1, "somebody hand-edited this face", which by its own contract must stay red and must not
be re-derived. The truth is rc=2, "my source was regenerated, refresh me". Left alone, that is a
chain leg that goes permanently red the first time the arms face is rebuilt on a bar it already
carries — and the plausible "fix" under time pressure is to re-derive it anyway, which is exactly
the laundering the split exists to prevent.

## The fix

Stop guessing from one date and compare the **input** this face consumed:

- `source_digest(payload)` hashes the exact inputs read off the arms face — the bar, every cell's
  baseline band, and each arm's own `(n_hold, rebal, delta_pp, band_pp)` rows plus its verdict.
  Canonical JSON, sha256.
- `build()` publishes it as `source.inputs_sha256` next to the face it describes.
- `check()` asks one question: does the arms face still hash the same?
  - same → no source moved → rc=1 `inconsistent` (a hand edit; re-deriving would launder it).
  - different (or absent, or the source file is gone) → rc=2 `stale` (the chain pays the refresh).

The cutoff comparison stays, but as a second signal and imported from the arms module
(`_source_advanced`), so this file no longer owns a copy of the staleness rule at all — the exact
debt r1372 named.

## Verification

- `scripts/etf_book_rule_null.py --selftest` **14 legs, 0 failed** (was 10). New legs:
  - the recorded digest equals what the arms face hashes to today;
  - **an arms face regenerated on the SAME bar reads stale (rc=2), not hand-edited** — the defect
    above, demonstrated by rebuilding the null face against a perturbed band and then pointing the
    gate back at the real source;
  - a face published before the digest existed reads stale (rc=2), not inconsistent;
  - a missing source face reads stale, never a traceback (the old path would have raised inside
    `build()`).
- published face refreshed (`python scripts/etf_book_rule_null.py run`): +4 lines, every reading
  byte-identical — `REJECT_IS_THE_DEFAULT`, REJECT 96.48% / NOT-SEPARABLE 3.52% under the null.
- chain leg `etf_book_rule_null` rc=0 (`results/_r1372bmc_s6_chain.only-etf_book_rule_null.json`,
  23:35:15).
- `python -m smoke_test`: see round report row (the suite runs detached on this host, RAM-bound).

## The rule, stated for reuse

A gate that must tell "my source moved" from "I was edited" cannot answer with a clock, and cannot
answer with a date alone either — a source can be regenerated on the bar it already carries. What
it can answer is: *do the inputs I consumed still hash the same?* That is positive evidence about
the source, it survives checkout/clone/rebase, and it degrades honestly (missing digest → stale,
never "no drift").