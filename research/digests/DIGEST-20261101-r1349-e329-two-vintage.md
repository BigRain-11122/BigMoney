# DIGEST 2026-11-01 r1349 bm-b -- E329: two vintages of one family, and who picks

**Study:** `E329_two_vintage_binding` · face `results/state_tilt/TWOVINTAGE-2026-11-01.json`
**Card:** `E329-WHICH-SOURCE-READS-TWO-VINTAGES` (seeded by r1348 at E328 close, burned in-round)
**Verdict:** `the_stale_cut_loses_while_the_pointer_exists_and_no_fallback_rechecks_for_a_newer_cut`

## What was asked

E328 measured quoted numbers sitting on a cut their own family had outgrown, and assumed one file
per source. A source can name two: a `_latest` pointer plus a pinned dated fallback. Then something
has to pick, and the question is whether the stale file is what gets picked.

## What was measured

228 sources name a face; they form 597 (source, family) pairs. Nine name two vintages of one stem:

| shape | pairs | note |
|---|---|---|
| two dated cuts | 8 | 2 have both cuts actually on disk |
| pointer + dated cut | 1 | the only real resolver in the tree |
| order-decided (`fallback_chain`) | 1 | order covered by a selftest leg: **0** |
| separately named roles | 2 | `DEFAULT_ASOF` / `DEFAULT_FRESH`, `ca` / `cb` |
| ordered list, nothing decided | 1 | a fixture loop, not a resolver |
| no static winner | 4 | mentions inside fixtures and containers |

## The two real shapes

- `scripts/e242_omission_inflation_sweep.py` -- `_face_file(stem)` tries `"%s_latest.json" % stem`
  first, then a pinned `"%s-2026-10-29.json" % stem`. All four call-site stems (AGGATT, owncross,
  per_member_gamma, sharediff) are served from the pointer today, so **0 stems serve a stale cut**.
  But **2 of the 4** (owncross, sharediff) hold a `2026-10-30` cut beside the pinned `2026-10-29`
  one: if the pointer ever disappears, the fallback serves a vintage the family has outgrown. The
  order is right and nothing tests it.
- `scripts/sscombo_pit_drift_audit.py` -- `DEFAULT_ASOF = REGIME5-2026-09-30` (19 days behind) and
  `DEFAULT_FRESH = REGIME5-2026-10-19` are bound to names that state the role. The stale vintage
  cannot win by order; it is asked for by name. This is the safe shape, not a bug.

## Three things the measurement had to fix in itself

1. **Stems are not case-stable on this disk**: `OWNCROSS-2026-10-29.json` beside
   `owncross_latest.json`. An exact-case index reported "no cuts on disk" and an exposure of zero.
2. **An ordered container is not an order**: a loop over a tuple of face names has an order and
   decides nothing. Only a container the source probes with `os.path.isfile` is a fallback chain;
   the class `ordered_list` exists so a fixture is not credited with a resolution rule.
3. **One assignment of a tuple is not a rebound**: `NAMES = (a, b)` was first read as the same
   target bound twice, which printed a load-order winner for a tuple with no second assignment.

## Bound, disclosed

Static binding only (a chain read on the line its container sits on); presence is measured, never
probed by moving files; a `%s` template is a form, not a vintage. Family is keyed by stem at the
source level -- deliberately different from E328's `(directory, stem)`, because a bare literal
carries no directory and this study asks a source-level question.

## Product

- `scripts/e329_two_vintage_binding.py` -- run / verify / selftest 28/28
- `results/state_tilt/TWOVINTAGE-2026-11-01.json` + `twovintage_latest.json`
- `Tools/s6_chain_bmb.py` leg `two_vintage_binding` (verify, ~7s)
- `smoke_test.py` leg (executed standalone: PASS)
- `knowledge/METHODOLOGY_ASSETS.md` card E329
- `results/runnable_pool.json` E329 done + E330 seeded