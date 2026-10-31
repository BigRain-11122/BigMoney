# DIGEST 2026-10-31 r1336 (bm-b) -- E317: the reader set is missing on the whole published corpus, not on five rows

**Study** `E317_print_coverage_census` · face `results/state_tilt/PRINTCOV-2026-10-31.json` ·
verdict `the_unit_is_missing_on_1047_of_1108_gates_and_33_of_them_are_readable_in_place_on_two_faces_both_of_them_gate_tables`

## What was asked

E316 (r1335) priced the reader set -- identifier, unit, one magnitude, the scale expression, plus
the floor where the gate is piecewise -- on five rows chosen by E315, and found 0 of 5 readable.
That is a statement about five rows. The pool card asked the census version: **run the same test on
every face in `results/` that publishes a tolerance constant, and price the same-unit substitution
for each one.**

## What was measured

289 faces carry at least one gate leaf; 1,108 gate leaves in total. The element almost nobody
prints is the **unit**:

| counter | value |
| --- | --- |
| faces scanned / faces with a tolerance leaf | 289 / 289 |
| gate leaves | 1,108 |
| leaves missing the unit | **1,047** |
| reader-complete leaves (all required elements present) | **33** (2.98%) |
| faces carrying at least one complete leaf | **2** (both of them gate tables) |
| faces with no complete leaf | 287 |
| leaves readable only from face-level keys | 923 |
| leaves publishing at least one candidate magnitude | 951 |
| leaves whose same-unit substitution spans >1 decade | 193 (>10 decades: 68) |
| largest substitution span | **19.6 orders of magnitude** |
| gates with a zero tolerance | 122 |
| faces with no gate leaf but a rejected `frac` leaf | 168 |

So the defect is not local: a reader holding a face and nothing else can evaluate **three percent**
of the gates the corpus publishes, and the two faces where it works are tables written to be read
that way -- not the faces a consumer actually opens.

The vocabulary that would have inflated this count is published rather than dropped: `frac` is
E316's token and it pulls 4,367 leaves on 176 faces that are fractions of a sample, 3.9x the gate
count itself. It is pruned, and every rejected path is listed per face so the pruning is auditable.

## Two pits found while publishing it

1. **A verify that demands a static candidate count reds on the next round's receipt.** The
   candidate pool is `results/` itself, and `results/` grows every round. The first chain run
   failed with `the candidate count moved (12218 -> 12219)` -- the +1 was this round's own S6
   receipt. The pool rule is now **asymmetric on purpose**: a face *leaving* the pool is a hard
   failure (evidence loss), a face *entering* it is disclosed (`pool grew by N ... the next run
   folds them in`). A gate that cannot survive the repo's normal traffic is noise, not evidence.
2. **The bm-b `gpu_face` leg was `audit`, and audit is not a gate.** Smoke went red on
   `fleet: GPU face self-consistent on heartbeat` with 33 aliases written at four different
   samples (free=3789 beside free=3025 MiB, spread 764 MiB) while the chain leg had been printing
   the finding and doing nothing about it. The leg now runs `apply`, so one probe rewrites every
   alias each round; on probe failure the keys are dropped with a warning rather than invented
   (r1288: a verdict no next step consumes is not a gate).

## Product

* `scripts/e317_print_coverage_census.py` -- `run` / `verify` (0 problems) / `selftest` 35/35
* `results/state_tilt/PRINTCOV-2026-10-31.json` + `printcov_latest.json` (identity checks green)
* `Tools/s6_chain_bmb.py` leg `print_coverage_census` (verify, ~20 s, rc=0)
* `Tools/s6_chain_bmb.py` leg `gpu_face` switched audit -> apply (repairs instead of observing)
* `smoke_test.py` leg (recomputes every census counter from the published rows)
* `knowledge/METHODOLOGY_ASSETS.md` card E317