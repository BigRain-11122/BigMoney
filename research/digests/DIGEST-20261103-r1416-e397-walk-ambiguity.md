# DIGEST — E397: which names are ambiguous only outside the census walk (r1416 bm-b)

Date: 2026-11-03 · Machine: bm-b · Face: `results/state_tilt/WALKAMBIG-2026-11-03.json`
Script: `scripts/e397_walk_ambiguity.py` (selftest 17/17, verify problems=[]) · Card: E397

## What was asked

E385 priced the merged-key split **per pair** and published, as a by-product,
`merged_names_whose_ambiguity_is_only_outside_the_walk = 0`. That sentence — *no ambiguity in the
tree belongs to the instrument* — was never tested **per name** over the whole key population, and
the tree does not contain one census walk but two with different exclusion rules.

## What was measured

Population: every key the census publishes = E350's `faces_named` read half (862 names) ∪ E383's
dump-sink write half (+22 write-only) = **884 keys**. Each key is resolved with the same suffix
index E383/E385 use, and every resolved file is tested against both rules the tree actually runs:

| walk | who runs it | what it drops |
|---|---|---|
| `e350_e353_e377` | E350/E353/E377 corpus | whole top-level trees: `Money02`, `legacy`, `media`, `Money0923` |
| `e391_py_corpus` | E390/E392/E394 reader census | any path component: `.git`, `__pycache__`, `_quarantine`, `node_modules`, `.codely-cli`, `_smoke` |

Classes per name: unique/unresolved · ambiguity collapses under every walk · ambiguity survives
every walk · ambiguity depends on which walk you use.

## Reading

- **884 keys**, of which **98 resolve to no file at all** (a published name whose document this
  checkout does not contain), **766** to exactly one file, **20** to two or more.
- Of the 20 ambiguous names: **19 survive both walks**, **1 flips class**, **0 collapse**.
- Per walk, the names with ≥2 files inside are 20 (E350 rule) vs 19 (E391 rule) — the one-name gap
  is `p1d_gates.json`, whose second file is
  `results/_quarantine/20261006-205649/results/_r782bmb_s0_worksnap/p1d_gates.json`. E391 drops the
  quarantine directory; E350's rule does not.
- The heaviest ambiguous names are unchanged from E385: `latest.json` 28 files, `judge_state.json` /
  `manifest.json` / `metrics.json` / `prep_state.json` 20 each, `probe.json` 14.
- Sibling check against `SPLITPRICE-2026-11-03.json` (same cutoff): published 19 merged names, this
  study re-derives **20**; the extra is `ledger.jsonl`, which lives only in the **write half** —
  E385's arm walked the 862 read-half names, so a name that only producers use never entered it.

## Verdict

`every_ambiguous_name_keeps_at_least_two_files_inside_every_walk_so_the_ambiguity_is_the_data_and_naming_a_member_is_a_decision_not_a_cleanup`

The repair list is **empty**. The bill is a rule, not a split: the two instruments must agree on
one skip set (their union) before any key count is compared across them, and choosing a member for a
name that keeps two files inside the walk is a *decision* (E385's 5-of-7), not a cleanup.

## Pits

1. **A by-product count is not a measurement.** E385's `..._only_outside_the_walk = 0` was true of
   the names it walked and of the one walk it used; asked per name over both walks it is still 0
   collapses but *not* 0 disagreements — one name is classified differently by the two instruments.
2. **The population has a half the read census cannot see.** 22 of 884 keys exist only in dump
   sinks; one of them (`ledger.jsonl`) is ambiguous. A split priced on the read half alone reports
   19 of 20.
3. **Memory is part of the instrument.** E350's `measure()` builds a parent map per source for its
   read rows; on this host (free RAM ~2-3 GB) that raised `MemoryError` on the full corpus. The key
   *set* is a function of the two binding helpers alone, so the study calls them directly and skips
   the row walk — same set, one tree live at a time (r1414 family: a memory fault that looks like a
   code fault).
4. **A name with no file is not a name with zero files.** 98 keys resolve to nothing here; pricing
   them as 0 documents would understate the census, and pricing them as 1 (E385's floor) is a
   different claim from "unresolved". Both are published as their own state.

## Wiring

- `scripts/e397_walk_ambiguity.py` — run / verify (re-resolves every published row) / selftest 17/17
- smoke leg E397 (`smoke_test.py`, exec'd verbatim by `scripts/run_e397_smoke_leg.py`, 1/1)
- S6 leg `walk_ambiguity` (`Tools/s6_chain_bmb.py`, rc 0, 0.35 s)
- No published face and no pointer is rewritten.