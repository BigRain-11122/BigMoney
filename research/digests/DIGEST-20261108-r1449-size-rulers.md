# DIGEST r1449 — one size, three rulers (bm-c, 2026-11-08 23:5x)

**Face:** `scripts/etf_book_size_rulers_decision.py` → `results/etf_book_size_rulers_decision.json`
+ `research/ETF_BOOK_SIZE_RULERS.md`. selftest 10/10 · `--check` 7 fields re-derived, 0 mismatch, 0.1s
· `run` 73s on the warm panel.

**Why:** r1448 priced each ruler separately and left "combine them into one decision for 2026-11-11"
as the next pointer. A desk cannot hold four numbers for one position.

**Readings (same rule, same panel, beta target 0.20, money at k=0.460253 = CNY 460,253):**

| cell | beta | k | vs money |
|---|---|---|---|
| baseline published (all classes, expanding) | 0.434543 | 0.460253 | +0.00pp |
| window (306-bar common window) | 0.484650 | 0.412669 | −4.76pp |
| universe (graded only: equity/commodity/convertible) | 0.462754 | 0.432195 | −2.81pp |
| **window × universe (never measured before)** | **0.508811** | **0.393073** | **−6.72pp** |
| denominator (today's 5 names, 100% invested, ÷ covered weight) | 0.367361 | 0.544424 | +8.42pp |

Range 15.14pp; floor CNY 393,073; three readings below the money, one above it. The rulers are not
additive: 2.81pp + 4.76pp of single-ruler movement becomes 6.72pp when both are applied.

**Identity legs (6, all pass):** k_from_beta reproduces the engine's k; expanding beta re-derived
at the last decision bar (self-caught: the schedule steps every REBAL bars, so the last decision
bar is *not* the last panel bar — a full-sample OLS comparison would have failed for a reason that
is not a ruler); ticket k reproduced; book_amount = k·nav − nav·underspend_pct/100 (self-caught:
the ticket's CNY 459,796.3 is 456.7 short of k·nav because of lot rounding, and that 456.7 is
exactly the printed 0.0457% of NAV); window recomputed from the ticket names equals the r1448
receipt (2025-07-09..2026-10-14, limited by 159263); graded k reproduces the split receipt.

**Self-catch worth keeping:** the first version printed "and the money is at the ceiling" as prose
while the same table's ceiling (0.5444) sat above the money. Flag was right, sentence was wrong —
prose is now generated from the flags, and selftest L10 fails if the two disagree.

**Wired:** S6 leg `etf_book_size_rulers` (check form, 0.1s, before `etf_book_registry` so the
register reads a fresh row); 2 smoke legs.

**Not adopted / not claimed:** the size in force is unchanged (changing it is a risk-budget change
needing a signature plus the 2026-11-11 decision bar). The four prereg requirements are printed on
the face. Full smoke was still running at close (0 real FAILs at the tail I read).