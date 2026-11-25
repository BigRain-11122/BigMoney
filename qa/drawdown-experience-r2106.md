# QA — idx_fut_carry_drawdown_experience (r2106 · bm-c)

- **date**: 2026-11-25T22:5x+08:00 (CONTENTION round — read-only inputs, new-file-only landing)
- **artifact**: `scripts/idx_fut_carry_drawdown_experience.py`
- **face**: `results/idx_fut_carry_drawdown_experience.json`
- **page**: `research/IDX_FUT_CARRY_DRAWDOWN_EXPERIENCE.md`
- **negative control**: `results/_r2106bmc_drawdown_experience_negative.py`
- **evidence_cutoff**: 2026-11-25

## What this face adds

`IDX_FUT_CARRY_LADDER_RISK.md` (r2105) prices each rung as vol + drawdown **depth** + Sharpe on
the daily series. This face re-expresses the same rung series in the units a client lives in —
**worst month, share of positive months, longest underwater run (bars), max-drawdown recovery
(bars), Calmar** — none of which any face computed before.

## Verification

| check | result |
|---|---|
| `--selftest` | **64/64** |
| `check` (re-derive, idempotent) | **CHECK_OK rc0** (16 rungs, engine 1/1, band 0/1) |
| negative control N1–N8 | **8/8 ALL_CONTROLS_PASS** |
| cross-face reconciliation vs r2105 | **CROSS_FACE_DOUBLE_SCALED** (see below) |

### Negative-control coverage (each proven to bite on a poisoned in-memory copy)

- N1 hand-edit Calmar → `CHECK FAILED`, and the word **STALE must not appear** (a real defect
  is not a stale face — r1934 contract);
- N2 ladder face bytes drift → `STALE`;
- N3 the r2105 risk face this reconciles against drifts → `STALE` (cross-face pin);
- N4 equity-arm (`etf_nobond_vt.json`) drifts → `STALE`;
- N5 instructed rung shortened to 10 bars → `CHECK FAILED` (never silently green);
- N6 ladder face absent → `STALE` (refuse, never default to 0);
- N7 the published face itself is green;
- N8 the verdict token is one of the frozen set.

## Cross-face finding (r2106 自捕)

r2105's `idx_fut_carry_ladder_risk.measure` builds the equity-sleeve daily contribution as
`m = k * sleeve` and then multiplies by `k` **again** (`daily = k*m[d] + ...` = `k²·sleeve`),
under-weighting the equity sleeve (0.189 instead of 0.435).  The rung return is
`k·sleeve + (notional/nav)·spread` — a **single** `k`, which is what this face uses.

Proof (three-way, same 1052-day grid, k=0.4347, k²=0.18896):

| construction | 1/1 annual % | 1/1 MDD % |
|---|---|---|
| single-k (correct, this face) | **26.667** | **-10.975** |
| double-k (r2105, as published) | 22.336 | -11.063 |

The ~4.33 pp gap is exactly the equity sleeve re-weighting (`k·11.054% = 4.80%` vs
`k²·11.054% = 2.09%`; realised sleeve ann = 11.054%).  **Not repaired there** — that face is
another window's shared surface during a contention window (r1907); this face records the
divergence in `cross_face` and a reader is never told two annual returns without the reason.

## Declarations kept as declarations

- the rung series compounds the equity sleeve at the ladder's `k`; the sleeve daily series is
  rebuilt at run time (~sleeve cost) and `check` pins it by digest, never re-derives it;
- monthly compounding drops the first and last calendar month (partial edges);
  `month_edges_dropped` names them; 51 months used on every rung (shared grid).

## Honest limits

- the ladder's rungs are whole-lot; fractional sizing is out of scope (r2100);
- `recovery_bars` is `None` for a rung whose max-drawdown trough never heals within the sample
  (printed as `n/a`, not 0);
- this is a research face; it makes no admission or live-trading claim.
