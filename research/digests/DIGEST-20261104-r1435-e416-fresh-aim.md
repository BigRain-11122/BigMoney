# E416 (r1435 bm-b) -- the four freshness tests price a copy lag or a frozen constant, not age

**Face:** `results/state_tilt/FRESHAIM-2026-11-04.json` (+ `freshaim_latest.json`)
**Script:** `scripts/e416_fresh_aim.py` -- run / verify `problems=[]` / selftest 21/21
**Card:** `E416-DO-THE-FOUR-FRESHNESS-TESTS-SIT-ON-THE-FACES-THAT-NEED-THEM-MOST`
**Upstream:** E411 (`readertiers_latest.json`), E410 (`freshnessbound_latest.json`)

## What was asked

E411 priced 232 reader sites over 200 faces and published four as red-capable on age, 196 faces as
having no reader that can go red. The card asks whether those four are aimed where age matters: a
freshness test on a face the chain rewrites every round can never fire, and a face with no chain
writer and no pricing reader is blind.

## What was measured

Each of the four sites' **own source block** was re-read and classified, instead of trusting the
tier name:

| site (E411's tier) | face | what the block compares | kind |
|---|---|---|---|
| `smoke_test.py:22` (`asks_the_clock`) | `results/dashboard_status.json` | `getmtime(machine-health.json) > getmtime(panel)` | copy lag |
| `smoke_test.py:8xxx` (`dates_the_face_in_a_gate`) | `printcov_latest.json` | `evidence_cutoff != "2026-10-31"` | frozen constant |
| `smoke_test.py:9xxx` (`dates_the_face_in_a_gate`) | `zerotolprune_latest.json` | `evidence_cutoff != "2026-10-31"` | frozen constant |
| `smoke_test.py:36xx` (`dates_the_face_in_a_gate`) | `starlagband_latest.json` | `len(lag_column) < 6` | no date logic |

- **0 of 4** prices the age of the face it reads; the `<` E411 read as a date comparison in the
  starlagband block compares a column count.
- The mtime arm reds when the panel is **behind its input**, so an arbitrarily old panel stays
  green. The two frozen-constant arms red when the producer **refreshes** the face.
- After reclassification: **0 of 200 faces** carry a reader that can go red on age (published: 4
  protected / 196 blind).

## The second hop that matters

E411's `writers_on_chain` counts a writer whose *script* is in the chain. The chain runs most study
scripts with `verify`, which refuses a moved face instead of republishing it. Measured over
`Tools/s6_chain_bmb.py` LEG argv on the 13 priced faces: the chain **runs** a writer for 3 and only
**verifies** 6 -- and both frozen gates sit on faces in the verify-only set. The face is pinned at
`2026-10-31` by an equality gate while its own chain leg is forbidden to move it; a manual `run` is
the only way forward and it reds the suite.

Also published: 45 blind faces have no writer on the round chain, and only 2 of the 200 faces
declare any freshness expectation at all (E410's two bounds, both on faces this table never
priced).

## Rules worth keeping

1. A tier is a claim about a gate; the gate's own lines are the measurement. When a census
   publishes "N tests can go red", price at least one of them from source before quoting N.
2. "The chain refreshes it" needs the argv, not the script name: `verify` is a refusal to move a
   face, and counting it as a refresh turns a frozen face into a protected one.
3. A gate pinning a date literal protects the literal, not the data.

## Wiring / not done

Smoke leg `# E416` (executed verbatim by `scripts/run_e416_smoke_leg.py`, 1/1); S6 leg `fresh_aim`
(rc 0, 0.35 s); card E416 in `knowledge/METHODOLOGY_ASSETS.md`; pool row E416 done, E418 seeded.
No reader and no leg was edited — the repair card (a real bounded age gate on the faces that can
actually stale) is seeded, not executed.