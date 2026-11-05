# r1473 — a republish buys exactly one round

**Date:** 2026-11-06 · **Machine:** bm-b · **Dept:** research+engineering

## What was red at open

`results/_smoke_run.log` (the detached suite r1472 left in flight) closed with **330 PASS / 6 FAIL**.
Three of the six were the same sentence r1471 spent a whole window eliminating:

| leg | face | sentence |
|---|---|---|
| `product: latest.json is a convention with 232 readers` | `results/state_tilt/latestfamily_latest.json` | the study's own verify does not come back clean |
| `product: unfloored faces` | `results/state_tilt/unfloored_latest.json` | the published summary does not re-derive from the live tree |
| `product: the suite opens 232 faces/pages through 265 reader sites` | `results/state_tilt/readertiers_latest.json` | the published summary does not re-derive from the live tree; the stored verdict is not the one the live tree produces |

The remaining three are the same class seen through other instruments, plus the one face this host
must not write: `dashboard carries the marks coverage gap` (dashboard is single-writer on bm-a).

## Repair

Republished each face from its own producer, not by editing the face:

```
python scripts/e398_latest_family.py run   -> LATESTFAMILY-2026-11-04.json   (61 s)
python scripts/e409_unfloored_faces.py run -> UNFLOORED-2026-11-05.json      (~30 s)
python scripts/e411_reader_tiers.py run    -> reader tiers face              (64 s)
```

E398 now reads 232 readers, E411 266 reader sites over 233 faces/pages from 227 legs.

## The finding that matters

**r1471 republished nine of these faces eleven hours ago. Three of them are red again, with the
same sentence.** That is not a repair failure, it is the instrument's design: each of these legs
recomputes a census over the *live* python corpus and demands the published summary re-derive
**exactly**. The corpus gains a dozen files per round (a digest, a face, a runner, a round report),
so the census cannot be byte-stable at suite time — a republish is a one-round purchase.

Measured this round, not asserted: the delta between publication and the next suite run is
**growth** (a superset of the published population: 227 -> 232 readers, 265 -> 266 sites, 230 -> 233
faces), with the verdicts unchanged. The leg cannot tell that apart from a corruption, so it spends
a red every morning and a republish every morning.

Card **E455** was seeded asking for the smallest growth-tolerance rule that still catches a changed
row, a changed verdict and a shrink — i.e. what a republish actually buys.

## Evidence

- `results/_smoke_run.log` — r1472's suite: 330 PASS / 6 FAIL, the three legs above named.
- `results/_smoke_r1473.out` — this round's suite run (detached, in flight at close: 22 PASS / 0 FAIL
  at the last poll).
- `results/runnable_pool.json` — E453 flipped to done with its result_ref read off disk (15/1 lines
  of churn, no reordering); E455 seeded ready; ready 3 (E450 / E451 / E455).

## Pit (this window)

The first attempt to flip E453 inserted `"status": "done"` next to the id while the entry already
carried `"status": "ready"` further down. `json.loads` accepts duplicate keys and keeps the **last**
one, so the file parsed clean and the card read `ready` — a silent no-op that would have been
reported as a flip. Fix: assert on the loaded entry (`status`/`result_ref`), not on the write.