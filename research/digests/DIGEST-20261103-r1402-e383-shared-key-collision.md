# DIGEST r1402 / E383 -- how many files one face key names, and who reads the merge

**Study** `E383_shared_key_collision` · card `COLLISIONKEY-2026-11-03` · 2026-11-03 · bm-b (CPU only,
zero network, GPU parked per C-20261014-01, cloud untouched).

## The question

E381 showed the shared face keying losing a path (a `join` keyed by its operands, so a three-component
path lands under a bare basename). E382 priced repairing it. Neither asked the direct question the
fallback's own docstring raises: **when the key is a bare basename, how many DISTINCT files on disk
does one key name -- and does a published face read that key as one face?**

## The method

One corpus pass over 2,423 sources (this study excluded), reading the two halves the published key
set is built from: load bindings (`e347.load_bindings`) and `json.dump` sinks, the writer half keeping
`e350._dump_sinks`'s exact "target must be a Name" condition so a writer-only key is counted exactly
when E350 counts it. Every face-shaped value gets `e350._face_key`, and each key accumulates its
distinct normalised values plus every `source:line` that produced one.

Two measurements the naive version gets wrong, both fixed in this build:

* **Normalise before counting.** Values are compared after the same `replace('\\','/').strip('./')`
  the key helper applies, so `./results/a.json` and `results\a.json` and the absolute path are one
  file, not a collision (15 of the 24 multi-value keys are exactly this alias case).
* **Resolve by suffix, not by repo root.** A folded value like `prospect_paper/_summary.json` is
  relative to whatever directory its producer was writing into; resolving against the repo root alone
  reported 21 merges as "unresolved". One index of the tree (60k files, one walk) plus a suffix match
  turns each value into 0/1/many candidate files, and a value with two or more hits is published as
  ambiguous and never counted as one file.

## Readings

878 keys. 24 of them carry more than one distinct value, split four ways:

| state | keys | meaning |
|---|---|---|
| `two_identified_files` | 3 | each value names exactly one file, and different ones: **40 files merged** |
| `a_value_names_many_files` | 5 | a value that names several files by itself (a bare basename from a join that did not fold) |
| `one_file_two_spellings` | 15 | one file written two ways -- normalisation's job, not a collision |
| `no_value_names_a_file` | 1 | nothing resolves here: stated, unpriced |

The three `two_identified_files` keys are the trial-labor family:

| key | files |
|---|---|
| `prep_state.json` | 20 (`results/trial_labor_w*/prep_state.json`) |
| `judge_state.json` | 18 |
| `_summary.json` | 2 (`prospect_paper` / `prospect_promotion`) |

All five `a_value_names_many_files` keys are coarse for the same reason: `latest.json` (28 files),
`state-bm-c.json` (4), `probe.json` (14), `manifest.json` (20), `state.json` (6) each arrive with a
bare-basename value beside a specific one.

**Who consumes it.** 346 published faces in `results/state_tilt` were walked for a string equal to a
merged key: 226 rows, 112 of them inside a list that also holds another key. Grouped by key:

| key | files | consumer faces | counted |
|---|---|---|---|
| `state-bm-c.json` | 4 (ambiguous) | 10 | 56 |
| `probe.json` | 14 (ambiguous) | 8 | 20 |
| `manifest.json` | 20 (ambiguous) | 8 | 14 |
| `latest.json` | 28 (ambiguous) | 8 | 10 |
| `state.json` | 6 (ambiguous) | 6 | 8 |
| `judge_state.json` | 18 identified | 2 | 2 |
| `_summary.json` | 2 identified | 2 | 2 |
| `prep_state.json` | 20 identified | 0 | 0 |

The single sharpest row: **E350's own published field census** (`FIELDBRANCH-2026-11-01.json`) carries
one row each for `judge_state.json` (`$.rows[2].face`), `_summary.json` (`$.rows[35].face`),
`manifest.json` (`$.rows[39].face`) and `state-bm-c.json` (`$.rows[4].face`), and one entry for
`probe.json` at `$.unwritten_guards[6].face` -- five keys that each name between 2 and 20 files on
disk, listed once per key.

## What this study refuses to claim

* A quote is a **consumption** only when the key sits in a list that also holds another key (a list of
  key strings, or of row dicts carrying a `face` field). A key inside a sentence is a mention and is
  published in `consumer_rows` with its pointer and field name, outside the headline.
* Several consuming faces are themselves keying studies (E380/E381 report the same key set, and this
  study's own predecessor E381 quotes `latest.json` as evidence). The count is therefore a claim about
  who *lists* the key as one identity, not about many independent production readers.
* The headline under-reports: a value that resolves to many files is never counted as one identified
  file, and an unresolved key is published as such rather than dropped.

Wiring: `scripts/e383_shared_key_collision.py` (run / verify 0 problems / selftest 26/26); smoke leg
E383 (`scripts/run_e383_smoke_leg.py`, 1/1); S6 chain leg `shared_key_collision` (rc 0, 0.06 s); face
`results/state_tilt/COLLISIONKEY-2026-11-03.json` + `collisionkey_latest.json`.