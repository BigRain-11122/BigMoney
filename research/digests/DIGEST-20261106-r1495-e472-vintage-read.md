# DIGEST — E472: how much of the daily face output is vintages no study opens (r1495 bm-b)

**Face.** `results/state_tilt/VINTAGEREAD-2026-11-06.json` (+ `vintageread_latest.json`)
**Producer.** `scripts/e472_vintage_read.py` (run rc0 / `check` problems=[] / `verify` identical /
selftest 18/18)
**Population source.** the live tree: every file under `results/` whose basename carries a date
stamp (1,276 dated files), plus the `.py` corpus (8,015 sources scanned, token prefilter)

## Question

E471 (r1494) showed 11 never-opened pointer targets whose peers exist but are only ever opened by a
smoke leg or a one-off round script. Those are members of *families* re-emitted with a new date
stamp every round — `WIDTHLADDER-20261029` through `WIDTHLADDER-20261106` all exist. Nobody had
measured the volume: how much of the daily face output belongs to a family with no study reader, and
does the unread part grow every cutoff or sit still?

## Reading

| channel | families | files |
|---|---|---|
| vintage families (≥2 distinct dates on disk) | 97 | 571 (28.5 MB) |
| **opened by a study that does not write it** | **0** | **0** |
| a study names it but no opener call uses the name | 17 | — |
| only a smoke leg / runner / one-off round script opens it | 7 | — |
| nothing outside the producer names it at all | 73 | — |
| carry a `_latest` pointer | 36 | — |
| single-vintage stems (counted, never scored) | 624 stems | 675 (42.0 MB) |

Unread byte share of dated vintage output: **1.0**. Emissions of unread families over the last six
cutoffs: 10, 11, 11, 11, 11, 10 — the daily output is not a one-off residue, it is the routine.
Verdict: `no_vintage_family_is_opened_by_a_study_that_does_not_write_it`.

The residue is stratified in a useful way. `REPORT` (44 vintages, `results/post_review/`) is named
by `Money02`'s probe/rerender and opened by two round scripts — measured, not consumed. `MIDSWEEP`
emits several vintages per day (`-c0_3`, `-s20130101`, `-burnin`) so "vintages" is larger than the
date count. 36 families publish a `_latest` pointer, which is the cheap retrieval channel: it exists
and still no study reads through it.

## What would have made the answer look better

1. **Counting distinct dates as files.** The row guard first required `len(dates) == vintages` and
   went red on legitimate rows that emit several vintages in one day. The corrected bound is one
   member per vintage, `len(dates) <= vintages`, no repeated dates, and the date set exactly equal
   to what the members' basenames name — so the guard still catches a truncated date list.
2. **Trusting a red leg.** The smoke leg's detail string was only assigned on the exception path, so
   the NameError surfaced only once the face became correct (the `or _d472` short-circuit had hidden
   it). A red leg proves nothing about whether the leg can pass; the leg is proved when it passes,
   and proved honest when a doctored face still makes it red.
3. **Resolving imported constants.** A family opened through a constant imported from another module
   is not followed beyond one hop, so the failure direction of this measurement is "calls a read
   family unread". That limit is published in the face, not implied.

## Wiring

`check` re-derives every residue class and every tally (including the emission table) from the rows;
`verify` re-derives the whole face from the live tree and compared identical; the S6 leg
`vintage_read` runs `check`; the smoke leg
`e472 vintage families are only counted unread when no study opens them (r1495 bm-b)` proves 1/1 and
1/1 red on an inflated vintage count with the face restored byte-identical
(`scripts/run_e472_smoke_leg.py --doctor`).

## How to apply

Before publishing another dated family into `results/`, name the study that opens it. A `_latest`
pointer is not a reader, and a smoke leg is not a consumer: what a leg proves is that the face
re-derives, not that anything downstream depends on it. The stable convention this face argues for:
one retrieval path per family (`_latest`), consumed by a study, and dated vintages kept only as long
as something can name why they exist.