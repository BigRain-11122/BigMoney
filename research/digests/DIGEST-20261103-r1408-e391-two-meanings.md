# DIGEST r1408 (bm-b) -- E391: which key name carries two meanings across published faces?

Face: `results/state_tilt/TWOMEANINGS-2026-11-03.json` (verdict `at_least_one_identifier_shaped_key_name_carries_two_structural_meanings_and_in_repo_sites_read_that_literal_but_this_census_does_not_show_those_sites_open_the_face_that_carries_it`)
Producer: `scripts/e391_key_name_two_meanings.py` (selftest 43/43, verify problems=[])
Parent: `results/state_tilt/WRONGSIDE-2026-11-03.json` (E390, the name-match rule this census had to obey)

## What it measures

Every key name in every published JSON face under `results/` (quarantine and >1 MiB faces skipped
and counted, never silently dropped), with the *shape* of the value stored under it: `null`,
`bool`, `int`, `float`, `str` (with `str:timestamp` and `str:path` sub-kinds), `list[<element
shape>]`, `dict`. A key whose shapes span more than one structural class is a conflict: a reader
that keys by name is right on one face and raises on the other.

| | rows |
|---|---|
| faces scanned / parse errors / skipped | 12,313 / 57 / 461 (91 quarantine, 370 too large, 2 own) |
| distinct key names | 80,411 |
| structural conflicts | **7,797** |
| — field-shaped names | 3,877 |
| — row-map index keys | 3,920 |
| field-shaped conflicts named by ≥1 literal in repo | **2,216** (132,604 sites) |
| field-shaped conflicts nobody names | 1,661 |

Other classes, published apart and never added to the conflict count: 789 string-kind conflicts
(`str` vs `str:path`), 660 null-beside-a-value, 235 int/float widths, 60 list-element conflicts,
70,870 single-shape keys.

The heaviest name conflicts by face count are `evidence_cutoff` (7,479 faces: timestamp string, bool,
dict, null), `n_trades` (6,111), `note` (5,361), `sharpe` (4,786), `elapsed_sec` (4,675). By reader
count: `verdict` (5,590 sites over 1,491 faces), `ts` (4,409), `legs` (3,950), `a` (3,137),
`status` (3,065).

## The defect that had to be fixed before the number was publishable

The first build reported 7,797 conflicts and would have published them. Half of them are not
names: `{"0": 5}` in one face and `{"0": {...}}` in another is one digit indexing two different
row maps. The split is measured, not assumed: 3,920 rows are index-shaped (`0`, `000001`,
`2026-11-03`, `+ 19,`, `-bm-a`), 3,877 are field-shaped. Only field-shaped keys can carry the
verdict, and the two counts are published side by side so the split itself is auditable.

## The bound, published as a bound

`reader_sites` counts literal subscripts and `.get`/`pop`/`setdefault` calls anywhere in the repo
that name the key. That is exactly the shortcut E390 rejected: a matching name is not a face read.
So the number is published as `read_sites_on_conflicted_keys = 132,604` together with
`read_bound_is_name_matched_not_face_resolved: true`, and the verdict string says the census does
not show those sites open the face that carries the key. The successor study (E392) is the one
that resolves the load path.

## Face size

The untrimmed face lists all 80,411 keys and is 33 MB. The published face lists the 7,797 conflict
rows (3.5 MB, written compact) and states `rows_policy` + `rows_counted_only = 72,614`, so a reader can tell a count
from a listing without trusting either.

## Wiring

* `scripts/e391_key_name_two_meanings.py` -- run / verify problems=[] (0.12 s) / selftest 43/43
* smoke leg E391 via `scripts/run_e391_smoke_leg.py` (1/1, exec'd verbatim from `smoke_test.py`)
* S6 chain leg `key_name_two_meanings` in `Tools/s6_chain_bmb.py` (registered; the full chain was
  not re-run this window, so its rc is owed to the next round)
* pool: E391 done with `result_ref`; floor refilled to 3 ready by seeding `E392-WHICH-NAME-MATCHED-
  READ-ACTUALLY-OPENS-THE-FACE-THAT-CARRIES-THE-KEY`