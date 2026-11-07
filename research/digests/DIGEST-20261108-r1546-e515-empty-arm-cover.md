# DIGEST 2026-11-08 · r1546 bm-b · E515 empty-arm cover

Card: `E515-DO-THE-OTHER-CALLERS-OF-A-BRANCHING-CALLEE-GUARD-THE-EMPTY-ARM`
Product: `scripts/e515_empty_arm_cover.py`, `results/state_tilt/EMPTYARMCOVER-2026-11-08.json`,
`results/state_tilt/emptyarmcover_latest.json`, smoke leg `# E515`,
`scripts/run_e515_smoke_leg.py`, S6 leg `empty_arm_cover`,
`knowledge/METHODOLOGY_ASSETS.md` card E515.

## What the question was

E512 published one callee (`card_config_ticket`) that names nothing on some paths and a value on
others, and all three of its published sites happened to be safe because a terminating guard sat
between the call and the read. Three guarded sites are only evidence about three sites. The next
caller — or the fourth site today — inherits nothing from them.

## What was measured

The population is the callee, not an upstream row list: every module-level function in the corpus
(`scripts`, `Tools`, `monitor`, `live`, `firm`, `engine`, `content`, plus `smoke_test.py`) that
returns both a nothing value (bare `return` / `return None`) and a value, and every call site of
those functions resolved through the calling module's own import aliases.

Per site, published independently (this is what makes a guarded sibling non-evidence):

* does a terminating guard (`return` / `raise` / `continue` / `break` in one arm) filter the empty
  arm between the call and the first read;
* does the result reach a subscript with no such guard;
* is the site reachable from production code at all, or only from a selftest / entry point.

## Reading

| axis | count |
| --- | --- |
| sources parsed | 2,718 (22 parse failures, published) |
| branching callees | 1,186 (920 called at least once) |
| call sites | 4,406 |
| reach: production / module-level | 3,187 / 47 |
| reach: test-only | 1,158 |
| reach: nothing in the corpus calls it | 61 |
| verdict: guard filters the empty arm | 617 |
| **production sites reading the empty arm unguarded** | **199** (97 of them subscript immediately) |
| verdict: read only from a test / entry point | 1,156 |
| verdict: handed onward without a read here | 713 |
| verdict: never read again | 1,671 |

`card_config_ticket` in particular: **4 sites — 1 production (`etf_book_order.py:1015`,
`run_card`, guarded), 3 test-only (`selftest:1439/1454/1466`)**. The three "guarded sites" E512
used were all self-test call sites; the one production site carries its own guard.

## Pitfalls

1. **A test site is not production evidence.** Splitting `reach` from `guard` turned "three guarded
   sites" into "three test sites". Any "all sites of class X are safe" claim should first ask
   whether those sites are reachable from production code at all.
2. **Reach is a per-site fact, not a per-callee label.** `run` has 26 sites, 3 of them test-only;
   `validate_rows` has 49 sites, 40 of them test-only. Tagging the callee "reachable" would have
   pushed 40 test sites into the production risk table.
3. **Three outcomes need three class names.** Merging "no caller at all" into "test only" reads
   orphan code and test fixtures as the same thing; this study added
   `no_corpus_caller_reaches_the_site` for the 61 orphans.
4. **Scanner cost (E442 family, fourth occurrence).** The first build called `ast.walk(tree)` twice
   per `Call` node (enclosing function, import alias) and produced no output in 5 minutes on 2,718
   sources; it was cancelled. Per-file indexes (function spans, parent map, import maps, and one
   Name/If cache per function) finish in seconds. Any "walk the whole tree for each node" pass
   should be replaced by a per-file index first.

## Verification

`selftest 25/25`; `run` rc0; `check problems=[]`; `verify problems=[]` (rebuild identical);
S6 leg `empty_arm_cover` rc0 0.37s; smoke leg `# E515` extracted verbatim via
`scripts/run_e515_smoke_leg.py` (1/1 green, `--doctor` 1/1 red with the face restored
byte-identically, sha `a336b282b8fb`).

Not run and not claimed: the full smoke suite, the remaining S6 chain legs, the collector family,
and the market/paper chain.