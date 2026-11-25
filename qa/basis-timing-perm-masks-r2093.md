# QA — basis_timing_perm_masks (r2093, bm-c)

Date: 2026-11-25T17:2x+08:00 · Machine: bm-c · Verdict: **MONEY_IS_A_MASK_ARTIFACT**

## What the artefact is

`scripts/bench_basis_timing_perm_masks.py` → `results/bench_basis_timing_perm_masks.json`
→ `research/BENCH-BASIS-TIMING-PERM-MASKS.md`. Three published faces disagreed
(GO +7.36pp / mask artifact +1.68pp / SIGNIFICANT p=0.0000); this face asks the missing
question: does the significance survive the same three roll rulers the money was measured on?

| check | result | evidence |
|---|---|---|
| selftest | 6/6 PASS | `python scripts\bench_basis_timing_perm_masks.py --selftest` |
| run | rc0, 3s | verdict `MONEY_IS_A_MASK_ARTIFACT`; IM strictest delta **-0.19pp** |
| numbers are derived, not copied | ok | table + null sentence read from `products[*].rulers[*]` |
| negative control (verdict fn) | ok | selftest legs 2-3 force "strictest loses p" / "strictest loses money" |
| behaviour control (mask) | ok | a ruler that excludes every day cannot keep money (leg 5) |
| reuse, not rebuild | ok | reuses `bench_basis_timing_perm` (weights/curve/annualised) and `bench_basis_timing_size_masks` (three rulers) |
| delivery | ok | commit **e892e694ff** on origin/main, `rev-list --left-right --count` = 0/0, three paths in `git ls-tree` |

## What it decides

The published GO was an all-legs verdict, and one leg stops paying under the union ruler
(IM -0.19pp). IC keeps 1.68pp of carry (≈1.76pp of capital ≈ 19,831 CNY/yr per lot, the
masks-face caliber). So the line cannot be funded **as published**; it can only exist as an
IC-only line with the other leg declared dead.

## What it does not decide (honest)

- Only IC/IM; IF/IH untested (thinner discount).
- Shift null keeps the weight path's autocorrelation and destroys its alignment — it does not
  test the 250-day window choice. What this face adds is that the null itself loses 2.10-6.36pp,
  so p=0.0000 is nearly guaranteed and cannot be used as the funding gate.
- Gross carry caliber (no margin, no funding cost), same as cell 7 / masks.

## Not done in this window (contention)

`repo_write_contention --lookback-min 45` = rc3 CONTENTION (peer interactive host pid 93460,
started 15:54, still writing shared faces). Per r1907 only new-file surfaces landed:
no S6 chain, no full smoke, no shared-face edits, and **state/heartbeat not written** (the peer
host owns them this window; precedent = r2092).
