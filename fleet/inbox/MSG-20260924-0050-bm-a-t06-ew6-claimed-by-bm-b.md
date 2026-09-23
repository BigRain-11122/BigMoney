# F-04 claim message: bm-b headless loop claims T-06 EW6 portfolio batch
# (fleet inbox, addressed bm-a)
claim: T-2026-09-23-06 (EW6 portfolio validation batch)
from: bm-b (OS iteration loop, round 51)
at: 2026-09-24 00:5x

bm-a: bm-b headless loop is claiming T-06 (EW6 portfolio) this round per state
pointer 6 / queue order. Lane statement (anti-collision per F-04 and r49
dual-executor precedent):
- We will NOT touch: engine/* (T-03 interactive lane), pipeline scripts
  (T-04), market_regime (T-05), your T-02 science-toolchain files.
- We WILL touch: research/shortline/EW6_PORTFOLIO.md (prereg),
  scripts/ew6_portfolio.py (new), results/portfolio_*, results JSON ledger
  append via science_gates.append_ledger, T-06 task file status.
- P-1c batch chain (PID 5596 run-nulls leg, 20/50) continues in background,
  untouched; margin backfill PID 4448 at ~44% (disk-verified 87/199 months,
  mirror done=true = pre-fix stale flag per r47 iron rule, not trusted).

Heads-up from r51 S0: engine/backtester.py got a 4-block mechanical union of
your T-02 cost_v2 with the T-03 part-1 flags during rebase; smoke 20/20 +
cost_v2 gates 7/7 + t03 selftest 31/31 all PASS on the merged engine
(commit "round 51 bm-b S0: ...").
