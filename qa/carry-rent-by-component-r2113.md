# QA — carry book: which arm pays the rent (r2113, bm-c)

Face: `scripts/idx_fut_carry_rent_by_component.py`
Surface: `results/idx_fut_carry_rent_by_component.json`
Page: `research/IDX_FUT_CARRY_RENT_BY_COMPONENT.md`
Round: r2113 · machine bm-c · contention round (new-file-only landing)

## What the face measures

For the ladder's instructed rung (**1/1**) and the in-band rung (**0/1**), on the 1,052 bars where
the equity sleeve, IC and IM all quote (2022-07-25 .. 2026-11-25), each arm's daily contribution
to the book is computed (`weight × series`), then:

* annual contribution (arithmetic mean × trading days),
* **return share** (contribution / total) and **risk share** (cov(arm, total) / var(total)),
* **rent** = return share / risk share,
* standalone vol, correlation with the book, leave-one-out book,
* beta / R² of the futures legs against the equity arm,
* equal-risk-share counterfactual, capped so the largest implied notional is 100% of NAV.

## Headline readings (instructed rung 1/1)

| arm | weight×NAV | ann contribution (pp) | return share | risk share | rent |
|---|---|---|---|---|---|
| equity sleeve | 0.4347 | 6.257 | 25.0% | 7.5% | **3.327** |
| IC basis leg | 1.1538 | 7.793 | 31.1% | 44.3% | **0.703** |
| IM basis leg | 1.0869 | 10.578 | 42.2% | 48.2% | **0.876** |
| cash (riskless) | 0.0000 | 0.413 | 1.7% | 0.0% | n/a |

Book: 27.191% compound / 25.041% arithmetic / vol 14.053% / Sharpe 1.836 / MDD −10.964%.

Judgments: `MIXED_RENT` (equity arm pays 3.3× its risk share; IC 0.70 and IM 0.88 do not pay
theirs — IM sits above the 0.80 underpaid line, so the honest token is MIXED, not "equity only"),
`CARRY_LEGS_MARKET_NEUTRAL` (equity arm explains R² 0.32% of the carry legs' daily variance;
beta −0.182 × 4.259% equity vol = −0.776 pp against 18.371 pp of carry),
`REBUDGETING_WOULD_HELP` (Sharpe +0.2077 at equal risk share with a 100% NAV notional cap:
23.431% / 10.784% / 2.043 / −9.294% — a trade, not a free lunch: −3.760 pp of annual return).

Band rung 0/1: 18.639% / 8.315% / 2.074 / −5.776%; equity rent 1.537, IM rent 0.791,
`REBUDGET_NOT_APPLICABLE` (IC weight is zero, so 1/cov has no value — refused rather than called
a wash).

## Verification evidence

* `python scripts/idx_fut_carry_rent_by_component.py --selftest` → **SELFTEST 30/30**
  (share identities sum to 1; riskless arm carries no risk share and no rent; rent identity;
  doubling an arm doubles its contribution; subtractive leave-one-out lowers a constant arm's
  book by about its own contribution; proportional carry → R² = 1; verdict tokens incl. the
  boundary at NEUTRAL_R2 and the not-applicable third state; risk-parity cap binds exactly once;
  zero-series arithmetic == compound while a positive constant compounds above it; mdd ≤ 0).
* `python scripts/idx_fut_carry_rent_by_component.py check` → **CHECK_OK** rc0
  (re-derives every share / rent / verdict from the stored component moments; input digests gate
  staleness).
* `python results/_r2113bmc_rent_negative.py` → **NEG 21/21 ALL_CONTROLS_PASS**:
  inflated component → `CHECK FAILED` **without** the word STALE; drifted input digest → rc3
  **STALE**; flipped verdict → `CHECK FAILED`; moved risk share → `CHECK FAILED` naming it;
  broken share sum → `CHECK FAILED`; restored bytes → green again; page prints all three engine
  tokens, the word "rent" and the "100% NAV" cap; module selftest passes; published face
  byte-identical after the whole control.
* Cross-face: `idx_fut_carry_drawdown_experience` (r2106) prices rung 1/1 **without** the cash
  arm at **26.667%**; this face's leave-the-cash-out column is **26.667%** → `CROSS_FACE_MATCHES`
  (delta 0.0000 pp). This face's book with cash is 27.191%, and both numbers are printed.

## Bugs caught in this window (all by the face's own guards)

1. Three selftest legs were red on numbers I "knew": leave-one-out is **subtractive, not
   multiplicative** (dropping a constant positive arm lowers the compounded book by roughly that
   arm's share), a constant daily +0.1% **compounds above** its arithmetic sum (28.64% vs 25.20%),
   and the underpaid line at 0.80 means a rent of 0.85 is not underpaid. The ruler was right; my
   test data was wrong. Fixing the test, not the threshold.
2. The band rung's equal-risk-share solve returns `None` (zero-weight arm → zero covariance →
   no 1/c_i), and the first version silently printed `REBUDGETING_IS_A_WASH` for it — silence
   read as "tested and harmless". Added the third state `REBUDGET_NOT_APPLICABLE` plus a selftest
   leg that a non-solvable re-budget is never reported as a wash.

## Not done (honest)

* Not wired into `Tools/s6_chain_bmc.py` or `smoke_test.py` — both are another window's
  uncommitted surfaces; this is a contention round (r1907 law: new files only).
* The equal-risk-share arm ignores the equity book's own capacity and the futures margin line;
  it is a re-budgeting counterfactual for today's book, not a recommendation.
* `state-bm-c.json` and the heartbeat were not written (multi-host shared state; peer holds them).
* Full smoke suite not run (contention round).
