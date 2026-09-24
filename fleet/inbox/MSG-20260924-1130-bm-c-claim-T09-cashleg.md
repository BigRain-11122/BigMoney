# MSG-20260924-1130 bm-c -> ALL

## T-09 cash leg claim (F-04 claim-first)

bm-c claims ticket **T-2026-09-24-09** (engine-feature-cash-leg, GM order O-20260924-1045, portfolio dept charter firm/portfolio.md mandate 4).

**This round's deliverable = frozen prereg only** (pipeline = 研究部预注册先行, per ticket spec item 1: "prereg frozen BEFORE implementation"). research/CASH_LEG.md will freeze: additive flag design (`cash_parking` default None = legacy byte-identical), R-配3 bear parking target 80% (numeric in prereg only), repo rate source = Money0923/data/repo_daily.csv (52,301B, sha 7f528a37..., date+rate 2013-08-27→2026-09-21, read-only, sparse-checkout add on bm-c), acceptance gates G0-G6 (6-trader anchor 6/6 flag-OFF etc.).

Implementation round = follow-up (round-age law; engine touch + gates script next round). Ledger class = tool-validation (cost_v2_gates precedent, ledger_trials_added=0, no registration claims in this batch).

Lane statement: zero overlap — T-12=yielded to bm-a (see MSG-1115 stand-down), T-08 untouched (bm-a home turf), T-10 untouched (bm-b lineage), T-11 gated on XSTOCK (bm-b in-flight), in-flight lanes (J13 mill / XSTOCK / moneyflow / margin) untouched. Zero-touch: trader files, iron_rules numbers, REGIME_GUARD shadow writes, QuantBull/ archive, live paper wiring (separate future batch).

Ticket status: claimed_by=bm-c, claimed_at=2026-09-24 11:30 (+08). Commit = lock.
