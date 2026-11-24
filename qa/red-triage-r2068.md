# QA — block-red triage (r2068, bm-c)

対象: `scripts/block_red_triage.py` / `results/block_red_triage.json` /
`research/BLOCK_RED_TRIAGE.md`

## What the face claims

| claim | value | where it is computed |
|---|---|---|
| the board's reds | 25 rows / **3 red** | `board.red` (read from `results/quant_block_board.json`) |
| D6_cash_rate | **UNINFORMATIVE** — modal bar 2026-11-20, printed lag 5d vs today's weekday, honest lag 4d vs last complete bar 2026-11-24, **2 sessions** behind, allowance 4d | `cash_panel.*` |
| W1_supply | **FALSE_RED_READER** — bank 20 items `{queued: 18, blocked: 2}`, shipped reader counts **0**, patched predicate counts **18** → row would be GREEN | `reds[W1_supply].producer_wrote`, `.proof` |
| G6_ingest | **FALSE_GREEN_PRODUCER** — 15/15 lanes identical, machine `FLUXGROUP` on both sides, `generated` identical on both sides | `reds[G6_ingest].producer_wrote` |
| real gap(s) / false red(s) / untrusted verdict(s) | `D6_cash_rate` / `W1_supply` / `G6_ingest` | `real_gaps`, `false_reds`, `untrusted_verdicts` |
| line state | printed **STARVING** → honest **BUSY** (bench pending 0, bank claimable 18) | `board.line_state_*` |
| vocabulary evidence | `a0c6e52f {queued:13, open:4}` → `61f1bc85 {queued:17}` → `bfb43120 {queued:18, blocked:2}` | `history` (git revisions of `research/WORK-BANK.json`) |

## Why each class is the honest one

- **W1_supply / FALSE_RED_READER**: `block_board.probe_supply` counts
  `status == "open"`; the producer renamed the same four questions to `"queued"` in
  `61f1bc85` ("the bank is now drained and says so") and has added fourteen more since.
  The reader's word list and the producer's word list were never the same contract, so the
  row has been red with eighteen startable questions behind it.
- **G6_ingest / FALSE_GREEN_PRODUCER**: `research/INGEST/DIFF-latest.json` compares a tree
  with itself — both sides carry machine `FLUXGROUP`, the same `generated` timestamp, and
  15/15 lanes with `file_delta == 0 && byte_delta == 0 && theirs.modified == ours.modified`.
  Its `verdict: COMPLETE` is a tautology; the board's refusal is right, its label
  ("no handover received") hides that the ingest lane has never measured anything.
- **D6_cash_rate / UNINFORMATIVE**: the panel really is behind, but the board's reference is
  `expected_last_weekday()` = today (2026-11-25), and a bar dated today cannot exist before
  the 15:30 close. Against the honest horizon (2026-11-24) the lag is 4 days, which the
  block's own `holiday_allow_days: 4` lets through — so the same spec would print GREEN on a
  two-session gap. Red today, green tomorrow on the same gap: the number is not usable in
  either direction.

## Evidence

| leg | result | file |
|---|---|---|
| offline selftest (calendar, vocabulary, provenance, classification) | **25/25 PASS** | `python scripts/block_red_triage.py --selftest` |
| write run | rc0, 3 rows classified, face + doc block written | `results/block_red_triage.json`, `research/BLOCK_RED_TRIAGE.md` |
| re-derive and compare (`--check`) | rc0 `CHECK OK 3 red rows re-derived` | `--check` |
| negative control | **7/7** — each branch fires on an input whose right answer is the opposite of the live one; poisoning the face's bar makes `--check` return **rc3 with the word STALE**; restore is byte-identical and then clean | `results/_r2068bmc_red_triage_negative.py` |

## Honest gaps (not claimed)

- No smoke leg and no S6 leg this round: the tree is under `rc=3 CONTENTION` (peer
  interactive host `pid 79608` alive since 2026-11-24 22:39, 9 shared faces written before
  the round started). Both are shared faces; recorded as the next round's pointer.
- The patches are **proven, not applied** — `scripts/block_board.py` and
  `research/QUANT-BLOCKS.json` are shared faces and were not edited.
- The D6 gap itself is a collector fact (bm-a lane, `scripts/update_repo.py`); this face
  only says the board's colour cannot be trusted on it, not that the panel is fine.
- `UNCLASSIFIED` is a real terminal state for any future probe type this face does not
  implement; it is not silently counted as green.
