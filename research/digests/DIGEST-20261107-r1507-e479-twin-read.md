# DIGEST 2026-11-07 r1507 bm-b -- E479: who reads the twin a vintage retirement would leave behind

## The question E477 left open

E477 priced a retirement of the 97 unread vintage families by bytes: 40 files (3,190,685 B) are
exact copies of a `*_latest.json` twin, so "keep the twin, drop the dated members" looks free.
But the whole family is one that **no study opens** (E472), so the twin inherits that status
unless something actually opens it. E479 asks that, per twin, with an opener-call scan.

## Population

E472's 36 families that carry a latest pointer: 36 distinct twin paths and **36 distinct
basenames** (`ADDOS_latest.json`, `CALL_latest.json`, ...). No plain `latest.json` exists in this
set, so a basename is family-specific -- enough to attribute a read to a family, not enough to
prove the directory a program opens.

## Reading

| residue | families | members | bytes |
|---|---|---|---|
| opened only by a smoke/runner leg | 30 | 144 | 11,880,041 |
| opened by a source that writes neither the twin nor its family | 4 | 27 | 829,282 |
| opened only by the script that writes it | 1 | 21? | 30,743 |
| reached only through a glob | 0 | - | - |
| never opened by any site | 1 | 5 | 94,798 |

The four cross-study readers are concrete: **GRANULARITY** read by `e236_share_difference`,
**LOOBOOK** by `e239_own_vs_cross` and `e240_aggregate_attenuation`, **OWNCROSS** by `e240`,
**STARLAGBAND** by `e249_lead_counterfactual`. The never-opened one is **BASISRECOVERY**; the
writer-only one is **CALL** (market_clock).

Consequence for a retention policy: **2 of 36 families can retire whole** (21 members, 125,541 B --
CALL and BASISRECOVERY). The other 34 need either the twin kept or a leg decision, because 30 of
them are read by `smoke_test.py` itself (deleting the face breaks the suite) and 4 by a live study.

Sanity channel: **147 sources / 689 opener sites** name a `*_latest.json` that belongs to none of
these 36 families. The scan is not blind; those faces simply are not in this population, and
crediting them to a family would be the E444 error (a zero must say whether nothing was found or
nothing could be looked at).

## Five pits, all measured in-window

1. **A shared-tail matcher merges the population.** `e470.match_kind` accepts any literal ending in
   `/<basename>`, which is right when targets have distinct names; here it made `famD/latest.json`
   a tail-match for `famA/latest.json`. A tail must carry the family directory (E366's
   one-address-form law, at the matcher).
2. **The producer set decides the headline.** The first build used only e464's stem channel, and a
   runtime-composed name (`OUT_STEM + "_latest.json"`) has no stem -- 22 of 36 twins were then
   reported as read by an unrelated study. Three channels (literal write site / module constant /
   composed `_latest` + family token) brought it to 4.
3. **A test harness is not a producer.** `smoke_test.py` writes fixtures with `*_latest.json`
   spellings in temp dirs, so the composed channel named it the writer of two twins and swallowed
   their real cross-readers. Legs are excluded from the producer set.
4. **"The directory is mentioned" is too loose a family test.** A neighbour writing its own face in
   the same directory (e236 writes `owncross_latest.json`) became the producer of `GRANULARITY`.
   The family token must appear in a **module constant** (e303's `OUT_STEM = "BASISRECOVERY"`).
5. **A fall-through precedence misreads leg-only rows.** e470's `residue_of` returns "producer" when
   the non-producer openers are neither smoke nor round, so `smoke_test.py` + `_tmp_r1275_smoke_leg.py`
   read as writer-only. The precedence is now explicit (outsider > smoke > round > writer > glob >
   never), and "retirable whole" excludes the smoke class because a leg that reads a face breaks
   when the face is deleted.

## Product

- `scripts/e479_twin_read.py` -- run rc0 / check problems=0 / verify problems=0 (same-tree rebuild) /
  selftest 16/16
- `results/state_tilt/TWINREAD-2026-11-07.json` + `twinread_latest.json` (36 rows)
- S6 leg `twin_read` (rc0 0.07s) and smoke leg `E479 the twins an unread retirement would leave
  behind re-derive their readers from their rows` (1/1 green, 1/1 red doctored, face sha restored)
- `scripts/run_e479_smoke_leg.py` (verbatim-leg extractor, same shape as the E478 one)
- methodology card E479

## Limits

Opener evidence is one AST hop plus e470's four-round name resolution: a path assembled through a
function argument or an environment variable is invisible, so "never opened" means "no opener in
this corpus spells it". The face prices the twin only; whether a twin carries the same measurement
as its dated members is E478 (clock) and E481 (conclusions).