# r1362 bm-c -- the width sign does not travel, and the family's width direction is what noise produces

**Date** 2026-10-30 · **Round** 1362 · **Machine** bm-c · **Dept** 研究/策略

## The question r1361 left open

E275 closed with exactly one quotable direction: *wider books earn more* (+0.69 → +1.56pp
median CAGR, rank corr **+1.000** with the toll). It also said the sign was quotable and the
size was not — but it was measured inside **one grid** (names {3,5,8} × cadence {10,40}) on
**one panel** (the 1653-name ETF pool). A sign that exists only there is this family's naming,
not a mechanism. So: does it survive on a panel the atlas never touched?

Panel chosen before any number was read: the 18 usable names of the E198 cross (510880 and
510180 have no local file and are published as missing, never substituted). Widths 3/5/8/12,
cadence fixed at 20, costs 0 and 8bp/side, decision phases 0/4/8/12/16 — and a **seeded
random-score control** (20 seeds × 2 phases × 4 widths = 160 engine runs), because a width
sign and a volatility sign are otherwise the same number.

## Readings

Real book (8bp/side, median of 5 phases):

| width | CAGR | vol | Sharpe | MaxDD | turnover |
|---|---|---|---|---|---|
| 3 | **12.76%** | 13.8% | **1.060** | −21.5% | 0.89 |
| 5 | 9.04% | 15.5% | 0.710 | −29.1% | 0.79 |
| 8 | 8.77% | 17.0% | 0.600 | −30.6% | 0.56 |
| 12 | 6.34% | 18.5% | 0.441 | −36.0% | 0.33 |

Zero-cost arm is the same ordering (13.69 / 9.87 / 9.38 / 6.67%).

* **The sign flips, on both cost arms.** Rank corr(width, CAGR) = **−1.000** at 0bp and at
  8bp; the paired phase share is **0.0** (0 of 5 phases, widest beats narrowest in *none*):
  narrow 3 names beats wide 12 names by **6.4pp/yr** at the production toll.
* **Volatility rises with width here** (13.8 → 18.5%), the opposite of diversification: the
  composite's negative-sign factors (`vol_60`, `intraday_range`) mean that widening the book
  adds the high-vol names, not the quiet ones. So the flip is not a "narrow book is riskier"
  artefact — Sharpe falls monotonically too (1.06 → 0.44).
* **The noise control runs the other way.** A random score on the same panel, same engine,
  same widths: CAGR 1.25 / 1.76 / 2.85 / 3.04%, i.e. **wider is better** (rank corr **+1.000**)
  and vol *falls* 22.8 → 20.5%, Sharpe 0.169 → 0.255 — pure diversification arithmetic. That is
  exactly the direction E275 quoted. So the family's width sign is the direction a signal-free
  book produces on a rising panel, and it cannot be credited to the family's signal until the
  null runs on the family panel. **That is the next round, not a claim made here.**
* **Real minus null decays monotonically**: 11.51 / 7.28 / 5.92 / 3.30pp across widths
  (rank corr −1.000). The edge lives in the top 3 names; by width 12 almost none of it is left
  over what noise plus a vol tilt already earns.

## Consequence published

`WIDTH_SIGN_IS_FAMILY_NAMING`. Two sentences change in how the book is described:

1. "Add names and you earn more" is not portable — on a clean 18-name cross-section, breadth
   costs 6.4pp/yr and 0.6 of Sharpe. Neither direction is universally right, which is the
   point: width is an instrument-dependent knob, not a mechanism.
2. E275's width sentence is now on notice. It has the sign that noise has. Until a null runs on
   the 1653-name pool and the real-minus-null delta still rises with width, "wider is better"
   should be read as *the book gets less noisy*, not *the signal gets better expressed*.

## Mechanism

`scripts/etf_book_width_cross.py` (selftest **25/25**):

* the panel, widths, cadence, costs, phases, thresholds and the verdict rule are frozen
  constants declared before any number is read; `--check` refuses an edited `spec`, an arm
  state that no longer follows from its rank corr / paired share, and **a rung that never
  traded** (turnover 0 = not a measurement);
* the phase draws are paired by phase index, never by row order, and unpaired phases are
  counted rather than silently zeroed;
* the null keeps the real book's eligibility mask, so breadth is compared across the same
  universe rather than across a wider one;
* the `attrs` block separates "the null reproduces the sign" (arithmetic) from "it does not"
  (the sign belongs to the score), and the face publishes **both** cost arms' states, so a
  cost-dependent answer comes out as `WIDTH_SIGN_ARM_DEPENDENT` instead of being rounded to
  the friendlier arm;
* the smoke leg re-derives every arm state and every real-minus-null delta from the published
  columns — a face that agrees with itself but not with its own numbers is red.

Card: `knowledge/METHODOLOGY_ASSETS.md` **E276**. Face: `results/etf_book_width_cross.json`
(+ `.md`). Chain leg: `etf_book_width_cross`.

## Honest limits

18 names is a thin cross-section and 80 monthly bars is thin for a CAGR claim; the phase draws
reuse the same bars, so the phase range is a stability read, not a p-value. The score is
re-ranked inside 18 names, so this is a *different instrument* — a null here says the sign does
not travel, not that the family reading was wrong. Both are published in the face.