# r2168 — tail dependence had no way to say "I am old"

## What was wrong (found mechanically, not by reading)

`scripts/chain_contract_word_audit.py` lists the checks whose text describes a moved input
("drifted", "moved", "behind") without ever saying **STALE**. `etf_book_tail_dependence`
was on that list, and the reason matters: `run_leg` only pays a refresh when the probe's
text contains `stale` (r1850/r1934 contract). So this face could not be rebuilt by the chain
at all.

Concrete symptom on 2026-11-27 09:35:

| face | evidence_cutoff | panel last bar |
| --- | --- | --- |
| `results/etf_book_tail_dependence.json` | 2026-10-30 | 2026-10-30 |
| live panel | — | 2026-11-26 |

19 bars of drift, and `--check` still printed `CURRENT` because it only re-derived the
verdict from the face's own `bars_series` — a guard that only re-reads itself never has an
"I am old" state (r1935).

## What changed

1. `scripts/etf_book_tail_dependence.py`
   - `run()` now records `inputs.panel_last_bar` (the bar the writer actually priced).
   - `check()` asks the outside question first: `F.check_panel_bar()` (0.3s, cheap) and falls
     back to `F.check_panel_stamp()` (~47s) only when the face cannot answer. A moved panel
     returns rc 2 with the word **STALE**.
   - The self-contradiction sentence changed from `DRIFT` to `CHECK FAILED` and deliberately
     does **not** carry the word stale — a face disagreeing with itself is a defect, not an
     invitation to rebuild (r1934).
   - Three behaviour selftests: current bar → green; old bar → rc 2 + "stale"; poisoned
     verdict → rc 1 and no "stale".

2. `scripts/chain_contract_word_audit.py`
   - A leg **leaving** the candidate list is a fix (a check learned the word), so `--check`
     now prints `STALE the candidate set moved: left [...], joined [...]` instead of
     `CHECK FAILED`. The classification moved into `_list_verdict()` so both branches can be
     proved on synthetic inputs (r2168: the previous test had to poison the live face, which
     now genuinely drifts).
   - New selftest leg for the departing/joining directions.

3. `Tools/s6_chain_bmc.py` — the audit is wired as a leg
   (`chain_contract_word_audit`, check 0.3s, run 24s paid only on the word stale). It was
   published in r2159 and unread since — the r1282 orphan class.

## Evidence

- `python scripts/etf_book_tail_dependence.py --selftest` → `selftest 13/13`
- `... --check` before rebuild → `CHECK FAIL: the panel moved under this face -- stale: it
  priced panel a1a42aee64453839, the live panel is fdb64c20030d2fb9`
- `... run` → `ROBUST_TO_TAILS | top10 share 6.3% | cagr 8.47% -> drop5 6.24% (placebo p0.0)
  | 1671 bars to 2026-11-26 | 56.9s`
- `... --check` after rebuild → `verdict ROBUST_TO_TAILS (stored ROBUST_TO_TAILS) OK | top
  share reproduced OK` rc 0
- `python scripts/chain_contract_word_audit.py --selftest` → `selftest 9/9`
- `... --check` before rebuild → `{"ok": false, "problems": ["STALE the candidate set moved:
  left [etf_book_tail_dependence], joined [-]", ...]}` rc 1 (and the chain then paid the 24s
  rebuild by itself: `+refresh(rc=0,25.5s)`)
- after rebuild → `{"ok": true, "problems": [], "n_candidates": 13}` rc 0
- chain legs: `etf_book_tail_dependence` 1.4s rc0, `chain_contract_word_audit` 0.2s rc0,
  `chain_writer_audit_check` 0.2s rc0 (its face republished for the new 393-leg table)

## What this does not fix

The audit still lists 13 checks that cannot tell the chain they are stale. They are now a
tracked list that goes red the round a 14th joins — not a document.
