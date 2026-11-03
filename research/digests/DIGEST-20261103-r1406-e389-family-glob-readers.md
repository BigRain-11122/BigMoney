# DIGEST r1406 (bm-b) -- E389: what do the 18 family-glob readers compute?

Face: `results/state_tilt/FAMILYGLOBREAD-2026-11-03.json` (verdict `some_members_compute_something`)
Producer: `scripts/e389_family_glob_readers.py` (selftest 14/14, verify problems=[])
Parent: `results/state_tilt/MERGEDCOST-2026-11-03.json` (E386, `family_glob_rows`, machine-read)

## What changed

E386's headline was `family_glob_readers: 18`, produced by a regex over raw source text. Counted on
tokens instead, of those 18:

| class | n | example |
|---|---|---|
| reads the results family | 2 | `glob.glob(os.path.join(root, "results", "trial_labor_w*"))` in E386/E388 |
| comment only | 14 | seven wave runners carry the same `.gitignore .../checkpoint/ covers w9` note |
| other family (runner sources) | 1 | `results/_r434bmc_capture_weld.py` globs `scripts/trial_labor_w*.py` |
| pattern definition | 1 | E386's own `re.compile(r"trial_labor_w\*")` |

Four path constants named `FAMILY_GLOB` are dead: the glob call site re-types the literal.

## Why it matters

The number E386 published answers "who mentions the family", not "who computes from it". Two readers
is still a real cost, so E386's COSTLY branch is not overturned -- but it was reached with a population
that was 89% prose, and the arithmetic of an aggregate reader is what a successor study still owes.

## Rules

1. A name is a use only at a word boundary (`FAMILY_GLOB_RX` is not `FAMILY_GLOB`).
2. The stem is not the population: `trial_labor_w*` names both `results/` dirs and `scripts/*.py`.
3. A star must touch the stem, or docstrings that merely discuss the family enter the census.

## Receipts

- `results/state_tilt/FAMILYGLOBREAD-2026-11-03.json` + `familyglobread_latest.json`
- card: `knowledge/METHODOLOGY_ASSETS.md` E389
- pool: E389 done with result_ref; E390 still ready
