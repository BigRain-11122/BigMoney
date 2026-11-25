# QA — idx_fut_carry_always_on_price (r2094, bm-c)

Date: 2026-11-25T17:3x+08:00 · Machine: bm-c · Verdict:
**PAYS_ON_ITS_WORST_RULER_BUT_THE_RATE_IS_RULER_BOUND**

## What the artefact is

`scripts/idx_fut_carry_always_on_price.py` → `results/idx_fut_carry_always_on_price.json`
→ `research/IDX_FUT_CARRY_ALWAYS_ON_PRICE.md`.

r2093 published a verdict ("hold always, do not fund as published") and no level. Three
level readings were already on that same table and had never been put side by side: the
always-on carry runs 2.76% / 9.65% / 9.68% (IC) and 5.74% / 11.96% / 11.50% (IM) across the
three roll rulers — a 5.9-6.9pp swing, wider than the timing delta the previous face was
about. This face prices one lot in CNY on every ruler, credits the cash leg on the unlocked
margin, and refuses to name a single headline rate while the rulers disagree.

| check | result | evidence |
|---|---|---|
| selftest | **10/10 PASS** | `python scripts\idx_fut_carry_always_on_price.py --selftest` |
| run | rc0 | verdict `PAYS_ON_ITS_WORST_RULER_BUT_THE_RATE_IS_RULER_BOUND` |
| check (self-verify) | rc0 `CHECK_OK` | re-derives from four inputs; names the four things it did **not** recompute |
| negative control | **6/6 PASS** | `python results\_r2094bmc_always_on_price_negative.py` |
| N1 cash 30% sinks it | ok | worst excess −0.90% → `V_NEG` |
| N2 zeroed carry sinks it | ok | worst excess −0.23% → `V_NEG` |
| N3 missing input refuses | ok | `DATA_BLOCKED`, names the missing path, never defaults |
| N4 hand-edited number | ok | `check()` returns rc3, prints `STALE`, names the field delta |
| N5 one ruler is not the answer | ok | published 2.76% vs strictest 9.68% = **6.92pp** apart |
| reuse, not rebuild | ok | notional+margin from `idx_fut_carry_margin.json`, rung from `sizing_spec.json`, levels from `bench_basis_timing_perm_masks.json`, cash from `capital_placement.json` |

## What it decides

- One IC lot: notional 1,204,840, first rung 1,129,566, margin 144,580 (12.80% of the rung),
  idle cash 984,985 earning 17,503/yr. Worst-ruler net excess **+2.72% of capital**;
  best-ruler **+10.10%**.
- One IM lot: notional 1,144,000, first rung 1,159,159, margin 137,280 (11.84%),
  idle 1,021,879 earning 18,158/yr. Worst-ruler **+5.45%**, best-ruler **+11.59%**.
- **The cash leg is additive, not a substitute.** Only ~12% of the rung is locked as margin;
  the other ~88% keeps earning. Dividing carry by the whole rung (the earlier reading)
  understates the book; comparing carry to the parking yield overstates it. Both are wrong.
- Timing adds 20,241 CNY/yr on IC and **−2,174 CNY/yr on IM** at the strictest ruler — i.e.
  IM's always-on arm beats its timed arm outright.

## What it does not decide (honest)

- **Whether a roll day counts as carry.** This face puts the three rulers side by side; it
  does not adjudicate. The lowest level (published, 2.76% IC) is the ruler that prices the
  roll jump a holder genuinely pays, so calling it noise is not free. Until this is settled,
  no single yearly rate may be quoted.
- Scale cost, exchange fees and margin-call forced sales are not deducted here.
- Only IC/IM (same universe as cell 7); IF/IH untested.
- One lot only; capacity beyond one lot is not measured for this book.

## Not done in this window (contention)

`repo_write_contention --lookback-min 45` = rc3 CONTENTION (peer interactive host pid 93460
started 15:54, still writing 33 shared faces including this machine's heartbeat). Per r1907
only new-file surfaces landed: no S6 chain, no full smoke, no shared-face edits, and
**state/heartbeat not written** this window (precedent = r2092 / r2093).
