# E135 — the production candidate survives the repair-count fix, and the flip count is now on the face

2026-10-26 — bm-c r1284 — tool `scripts/etf_nobond_vt.py` (re-run, unchanged) →
evidence `results/etf_nobond_vt.json` (pre-fix snapshot kept at
`.codely-cli/tmp/etf_nobond_vt.pre_r1284.json`)

## The open item this closes

E133 (r1282) fixed `A.repair_flips`: it measured returns with `close.pct_change()`, and
pandas 3 stopped filling across a suspension bar, so a split print sitting behind a halt
was flattened but never **counted** (and a small real move on that bar was eaten with it).
The panel's repair count moved 134 → 168. E133 closed with an explicit "not verified":
*the bridge, the equity-alpha headline and the E81 leg faces were all computed on the
old code and were never re-run.*

The money surface is the one that matters, because the published production candidate —
bond-free pool + 8% vol target — is quoted from a JSON built on **2026-10-25 23:03**,
i.e. before the fix.

## Result — nothing moves, and that is the finding

| arm | CAGR | Sharpe | max DD | vol | IS CAGR/SR/DD | OOS CAGR/SR/DD |
|---|---|---|---|---|---|---|
| bond-free, no VT | 15.56% | 1.002 | -16.04% | 16.38% | 10.22 / 0.685 / -14.18 | 23.64 / 1.489 / -16.04 |
| **bond-free, 8% VT (production candidate)** | **11.49%** | **1.132** | **-10.56%** | 10.50% | 5.81 / 0.621 / -8.80 | 20.14 / 1.836 / -10.56 |
| bond-free, 12% VT | 13.31% | 1.008 | -14.99% | 13.88% | 6.59 / 0.553 / -12.66 | 23.64 / 1.638 / -14.99 |

- **Every field of all three arms is identical to the pre-fix JSON**, at the precision the
  file publishes (3 dp), and the live picks are the same five names in the same order
  (515450 / 515300 / 511180 / 510760 / 511380, as_of 2026-10-23).
- Universe is unchanged (1,499 instruments bond-free).
- The one thing that *does* change is the provenance of the panel: the run now reports
  **168 flips repaired** where the old code reported 134. The 34 newly-counted prints were
  post-suspension bars; their flattened levels rebuild from the previous *priced* close, so
  the small real move on each of those bars is now preserved instead of dropped.

## Why identical is the correct answer (not a null result being waved through)

A repair-count fix can move a book in either direction, so this had to be measured, not
assumed. The mechanism here: the extra 34 prints belong to names that the bond-free book —
5 holdings, re-decided every 20 bars, 8% vol target — **never held**, and a repaired name
that is not held contributes nothing to an open-to-open equity curve. The fix therefore
changes the panel's audit trail, not its holdings.

The reading rule that follows: quote the production headline **with its repair count**
(`168 flips repaired, 1499-name bond-free universe`), so the next panel generation is
auditable and a future re-run that *does* move can be attributed rather than argued about.

## Reproduction

```
python scripts\etf_nobond_vt.py     # ~3min, prints "bond-free universe 1499 flips repaired 168"
```

## Still not verified (carried, not dropped)

`etf_equity_alpha.py`'s own headline, `etf_robust_pf.py`'s 18-cell grid and
`etf_walkforward_capacity.py`'s walk-forward chain were last built on 2026-10-25 / 07:33
today, i.e. also before the count fix. They are the next re-prices; the bond-free candidate
is the only one that had a published money number riding on it, and it is clear.