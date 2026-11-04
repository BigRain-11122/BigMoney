# DIGEST 2026-11-04 r1426 -- E408: a writer in the tree is not a refresh on the signal that reads the face

## What the card asked

E407 ended with "13 of 13 input faces have a writer in the tree, and no leg of the suite executes
one of them". The card asks the question that leaves open: **does every in-tree writer of a face also
refresh it on the same signal?**

## What was measured

Two passes, both static, zero network, zero burn.

**Pass 1 -- re-test the inherited population.** E407's writer list comes from `writers_of()`, whose
docstring is explicit: "A face is written by the module that names its basename." Re-testing the 26
named modules with a scope-aware dataflow question (does a write call reach a path naming the face,
directly or through `FACE`/`LATEST` constants, aliased locals, or `for name in (FACE, LATEST)`):

| class | count |
|---|---|
| actually writes the face | 14 |
| names it but never writes (only reads) | 7 |
| round-scoped one-off tool (`_r506bmc…`, `_postscript`) | 5 |

The 7 mention-only modules are `e327` (reads `banddeflate`), `e356` (reads `reachwide`), `e250`'s
co-named peer `e407`, and `build_status`/`e308`/`e313`/`e407` on the `t35` face. All 13 faces still
have at least one real writer, so E407's conclusion survives while its arithmetic does not.

**Pass 2 -- which surface runs each real writer.**

| surface | real writers |
|---|---|
| standing round chain (`Tools/s6_chain_bmb.py`, 183 legs) | 12 |
| session script only (`e321` → `quantityname`; `t35_open_fill_verify` → `t35`) | 2 |
| registered task | 0 |
| none | 0 |

The readers are 13 legs of `smoke_test.py`. They open the faces in-process; the suite's 54 script
dispatch tuples are all selftest-shaped and **0 publish**. So refresh and read are different
schedulers: a face can be read at any moment between rounds, and 2 of the 13 have no standing
refresh at all.

Verdict (recomputed by the gate, not written by hand):
`the_seed_population_counts_mentions_as_writes_and_no_face_in_this_set_is_refreshed_on_the_signal_that_reads_it`

## Why it matters

This is the mechanism behind the E305/E387 red family: a leg that demands the published face equal a
live re-derivation is comparing an artefact produced on the round chain against a read that happens
whenever the suite runs. It re-reds by construction whenever the chain has not run in between.

## Instrument lessons

1. **Re-test an inherited population before extending it.** Inheriting E407's list would have
   published "all 26 writers are wired into the chain"; 5 are one-off tools and 7 never write.
2. **A write is a dataflow, not a string.** The publish shapes are constant + local alias + loop
   binding; taint must be scope-aware, or a reader's local `face` becomes a writer (it did).
3. **The defect was in the first line of the seed's own docstring.** Nobody had read that sentence
   against the question being asked.
4. **Cost is part of wiring.** v1 scanned every `.py`/`.ps1` against every module name: 81 s per
   chain round. Narrowing the scan to the 26 seed basenames: 3.0 s. A correct leg that costs 81 s a
   round gets disabled.

## Artefacts

- `scripts/e408_writer_refresh_signal.py` (run / verify problems=[] / selftest 20/20)
- `results/state_tilt/REFRESHSIGNAL-2026-11-04.json` + `refreshsignal_latest.json`
- `scripts/run_e408_smoke_leg.py`, smoke leg E408 (1/1)
- S6 leg `writer_refresh_signal` (rc 0, 3.0 s)
- `knowledge/METHODOLOGY_ASSETS.md` card E408

## Next

E409 is seeded from this face: the two session-only writers mean `quantityname_latest.json` and
`results/t35_open_fill_verify.json` are read by legs that no standing surface refreshes. E403 and
E406 remain ready and untouched.