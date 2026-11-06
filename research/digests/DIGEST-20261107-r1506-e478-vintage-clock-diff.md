# DIGEST 2026-11-07 r1506 bm-b — E478: what the vintages still hold once the clock is removed

Card: `knowledge/METHODOLOGY_ASSETS.md` E478.
Producer: `scripts/e478_vintage_clock_diff.py` (run / check / verify / selftest).
Faces: `results/state_tilt/vintageclock_latest.json`, `VINTAGECLOCK-2026-11-07.json`.

## Reading

Population: E472's 97 unread vintage families (571 member files). Only the 36 families that publish a
resolvable `*_latest.json` twin can be compared; the twin is the reference, never part of the
population. Frozen clock names, removed from the top level of both sides: `generated`, `ts`,
`timestamp`, `elapsed_sec`.

| class | files | bytes |
|---|---|---|
| identical after top-level clock strip | 31 | 2,141,178 |
| differs beyond the frozen clock names | 145 | 10,721,884 |
| not a JSON object (csv/md/jsonl — unmeasured) | 16 | 30,743 |
| unreadable member | 0 | 0 |
| family has no resolvable twin (61 families) | 379 | 15,659,199 |
| **total** | **571** | **28,553,004** |

Comparable population 176 files; **17.6 % of the comparable vintages are semantically their own
latest twin** once four clock names are forgiven → 2,141,178 bytes carry no second measurement.

The recursive arm (clock names stripped at every depth) is identical to the top-level arm: +0 files.
No family in this population hides a per-row timestamp one level down.

## Robustness (the bound, published not folded in)

`evidence_cutoff` is a date-shaped name that the card does **not** forgive. It appears in all 145
differing rows — but **zero** rows differ from their twin on that name alone. So the frozen four-name
set is not hiding redundancy: every vintage that is not identical also states something different
about its payload. The block is re-derived by `check` and by the smoke leg, not restated.

## What this does and does not license

E477 priced byte identity (25.36 MB lost if the vintages were retired); E478 prices semantic
redundancy (2.14 MB collapsible under the frozen definition). The two sets do not overlap: E477's
copy classes are byte-identical pairs, E478's are clock-only differences.

Neither is a deletion licence. 379 of the 571 members live in families with no twin at all, so their
redundancy is unmeasured from the twin side; and whether a twin is read at all is E479's question —
a twin nobody opens retires whole, which no clock comparison can decide.

## Legs

- producer: run rc0, `check` problems=0, `verify` identical rebuild problems=0, **selftest 30/30**
- S6: `vintage_clock_diff` rc0 0.05s (`python Tools/s6_chain_bmb.py 1506 --only vintage_clock_diff`)
- smoke: `scripts/run_e478_smoke_leg.py` → 1/1 green; `--doctor` (invented verdict) → 1/1 red, face
  restored sha-identical (`b4959086718b` in = out)