# DIGEST 2026-11-01 r1372 -- E351 product-gate state census

**Question (seeded by r1369 at E348 close).** E348 found one `product:` smoke gate green for 279
commits against a face with a single blob.  How many of the family are like that?

**Product.** `scripts/e351_gate_state_census.py` (build / verify / selftest) ->
`results/state_tilt/GATESTATE-2026-11-01.json` + `gatestate_latest.json`.

## Method

- gates = distinct `check("product: ...")` labels in `smoke_test.py`;
- subject = every path-shaped literal in the check's enclosing `try` body (+ the check's own
  arguments); wildcards published, never expanded;
- history = one `git log --raw --no-abbrev --no-merges -n 300 <replay_head> -- <union of paths>`;
- state at commit k = subject blobs as of k (ABSENT before first write);
- class = `unresolved_subject` | `never_evaluated` | `frozen_subject` (1 state) | `live_subject`.

## Readings (window 300 non-merge commits, replay_head 47e9996f)

| class | gates |
|---|---|
| unresolved_subject | 55 |
| frozen_subject | 6 |
| live_subject | 31 |
| never_evaluated | 0 |
| **product: gates** | **92** |

- green-by-freeze share **16.2%** of the 37 evaluated gates;
- **all 6 frozen subjects are younger than the 50-commit maturity threshold** (present 6/6/9/9/11/42
  commits) -- so the verdict is *no gate has been green against a subject that stopped moving long
  ago*, not *16.2% of green runs are vacuous*;
- most-moved subject: `product: dashboard carries the marks coverage gap` (221 distinct states);
- 55 gates name no literal face (computed paths), so any state count for them is out of scope --
  that population is the natural next card.

## Bounds

- a glob literal is a fact about the disk, not a subject;
- `data/` companions are tracked by blob, so a byte-identical rewrite does not register;
- nothing is executed: "live" means the subject moved, not that the gate ever failed.

## Defects caught in this study's own drafts

1. scope too wide -- the enclosing function body made a literal from an unrelated statement the
   subject (selftest leg);
2. `git log --raw` abbreviates blob ids -- a strict 40-hex parse matched nothing and reported 0
   evaluated gates; `--no-abbrev` fixed it and the leg pins the shape;
3. a fixture asserted `frozen` on a subject that was absent in every commit (that state is
   `never_evaluated`) -- the assertion was wrong, not the code;
4. the verdict claimed green-by-freeze before the maturity split existed; the leg now refuses a
   young-only freeze reported as green-by-freeze;
5. self-inclusion -- the leg this study adds to `smoke_test.py` is itself a `product:` gate, so it
   is excluded and the exclusion is published.

## Not run

Full ~340-leg smoke suite (the new leg was executed standalone), full S6 chain, lane collectors,
`market_regime`/`update_*`, paper/scorecard faces.  GPU untouched (parked C-20261014-01), cloud
untouched, nothing deleted, no quarantine action.
