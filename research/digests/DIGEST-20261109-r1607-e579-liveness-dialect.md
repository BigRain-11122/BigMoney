# DIGEST 2026-11-09 r1607 bm-b — E579: the shipped liveness line under the dialect it cannot read

**Card.** E579 (seeded by E578 at r1606). E578 stopped at a row count; a row count is not a
verdict. This round re-ran the *shipped* verdict and changed exactly one thing.

**Method.** `Tools/lane_round_liveness.py` is imported, never re-implemented. Two row readers are
compared over the same ledger text:

- strict — `ledger_times_text` as shipped: a row counts only if the line starts with `|`
- wide — the same row shape (`^\|?\s*<ISO stamp>`) with the leading pipe optional

Everything else is shared: same files, same text source (peers through `git show origin/main:<path>`,
bm-b through its worktree), same state/heartbeat faces, same `verdict_of`, and the thresholds are
`import`ed from the module (a selftest leg pins them at 25 / 360 / 90 so this study cannot drift).

**Readings.**

| machine | strict | wide | invisible | rounds_24h | worst 7d gap (min) |
|---|---|---|---|---|---|
| bm-a | DEAD 107 rows | DEAD 491 rows | 384 | 0 → 0 | 3509.0 → 3509.0 |
| bm-b | ALIVE 663 rows | ALIVE 1363 rows | 700 | 61 → 66 | **977.9 → 355.8** |
| bm-c | ALIVE 141 rows | ALIVE 653 rows | 512 | 6 → 6 | 1833.2 → 1833.2 |

Totals: 911 strict rows vs 2,507 wide rows → **1,596 rows invisible to the shipped reader**
(63.6%). `machines_whose_newest_row_has_a_pipe` = 3.

**Verdict.** `no_machine_flips_a_verdict_but_1_of_3_machines_publish_a_gap_or_round_count_the_wide_
reader_does_not_reproduce` — no machine flips between the dialects, yet **bm-b's published 7 day gap
is overstated by 622.1 minutes (10.4 h)**: the "16.3 hour silence" is manufactured by rows the
reader cannot see, exactly E577's `a_row_the_index_cannot_read_closes_this_gap` class, now shown to
be landing on the module that decides whether a peer is dead.

**The two machines whose loss moves nothing.** bm-a loses 384 rows and bm-c 512, and neither
`rounds_24h` nor `worst_gap_7d_min` changes by a minute. They are published under their own class
(`rows_are_lost_without_moving_a_published_number`), never as "the dialect costs nothing" — the
study's own `face_problems` caught the first draft doing exactly that, and it is now a selftest leg.

**Published faces are undateable.** All three `results/lane_liveness.<machine>.json` faces carry a
verdict and **no timestamp** (`published_faces_without_a_timestamp` = 3), and **2 of 3 disagree with
a strict recompute in the same minute** (bm-a face says ALIVE where a recompute says DEAD; bm-c face
says DEAD where a recompute says ALIVE). A verdict a reader cannot date is not a verdict it can use.

**Why no flip today, and when it would flip.** The verdict is driven by the age of the *newest* row;
all three machines' newest rows carry a pipe, so the daylight went to the disclosure instead. The
margin is published rather than assumed: `invisible_rows_within_alive_min` = 0. A single machine
whose newest row is written without a leading pipe is called NO-EVIDENCE/DEAD within 25 minutes —
that fixture is selftest leg S2.

**Bounds.** Static, read-only: no runner executed, no heartbeat written, no peer contacted, the tool
itself unchanged (changing it would move D-20261101-15's acceptance face, which needs its own
round). Agreement between the two dialects is agreement about *this text*; a row never written is
invisible to both.

**Evidence.** `scripts/e579_liveness_dialect.py` (build / check problems=[] / verify rebuild
identical / selftest 27/27) · `results/state_tilt/LIVENESSDIALECT-2026-11-09.json` +
`livenessdialect_latest.json` · S6 leg `liveness_dialect` (rc=0 0.04 s) · smoke `#E579` +
`scripts/run_e579_smoke_leg.py` (1/1 green, `--doctor` 1/1 red) · card E579 in
`knowledge/METHODOLOGY_ASSETS.md` · pool E579 done + E580 seeded.