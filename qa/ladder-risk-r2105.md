# QA — the return ladder's risk column, measured (r2105, bm-c)

Round: r2105 · machine bm-c · window 2026-11-25T22:2x+08:00 · mode **CONTENTION**
(`results/_repo_write_contention.bm-c.json` rc3) → new-file faces only, no shared-face
edits, no S6 chain re-run, no smoke_test edit, no `state-bm-c.json` / heartbeat write.

Deliverables under test
- `scripts/idx_fut_carry_ladder_risk.py`
- `results/idx_fut_carry_ladder_risk.json`
- `research/IDX_FUT_CARRY_LADDER_RISK.md` (rendered by `run`)
- `results/_r2105bmc_ladder_risk_negative.py` (negative control)

## 1. Does it run, and is it deterministic?

| check | command | result |
|---|---|---|
| self-test | `python scripts\idx_fut_carry_ladder_risk.py --selftest` | **16/16 ALL_PASS** |
| run | `python scripts\idx_fut_carry_ladder_risk.py run` | rc 0, writes face + page |
| check (idempotent) | `python scripts\idx_fut_carry_ladder_risk.py check` | **rc 0**, `CHECK_OK rungs=16 engine=1/1 measured=13.66pp declared=10.46pp` |
| negative control | `python results\_r2105bmc_ladder_risk_negative.py` | **10/10 ALL_CONTROLS_PASS** |

## 2. Is the judgment falsifiable?

Every leg of the negative control corrupts exactly one thing and shows the real `check`
answering the right way, with the words as contract (r1850/r1934):

- tampered measured vol → `CHECK FAILED` **and no `STALE` word** (N1)
- tampered L2 vol (formula no longer matches) → `CHECK FAILED` (N2)
- flipped verdict → `CHECK FAILED` (N3)
- ladder digest drift → `STALE` (N4)
- equity-arm digest drift → `STALE` (N5)
- leg length drift → `STALE` (N6)
- missing face → `STALE`, never a silent green (N7)
- refusal face → `STALE` (N8)
- missing ladder → `STALE` (N9)

## 3. Are the numbers computed, not copied?

The face is derived at run time from
`idx_fut_carry_risk.product_spread("IC"|"IM")` and `idx_fut_carry_risk.adopted_book()`
by import — no leg is re-implemented. One lot of each product (1,153,800 / 1,086,880 CNY)
is read out of the ladder's own `(1,0)` / `(0,1)` rungs, not re-declared.

Cross-check: the equity sleeve alone measures 11.02 %/yr ann, 10.35 % vol, −10.56 % MDD,
which is exactly what `idx_fut_carry_risk.adopted_book()` publishes — the sleeve leg is
the authority's number, not a second reading.

## 4. What the face says (2026-11-25, cutoff = 2026-11-25, 1,052 common days)

| rung | expected %/yr | declared vol % | **measured vol %** | Δ pp | measured MDD % | measured Sharpe |
|---|---|---|---|---|---|---|
| 0/0 (no futures) | 5.17 | 4.57 | **1.85** | −2.72 | −2.07 | 0.726 |
| 0/1 *(in band)* | 9.05 | 6.61 | **7.53** | +0.92 | **−5.41** | **1.661** |
| 1/1 **<- instruction** | 17.38 | 10.46 | **13.66** | **+3.20** | **−11.06** | 1.533 |

- IC leg vol **5.92 %/yr**, IM leg vol **6.82 %/yr** (the ladder declares 4.0 for both).
- IC/IM correlation **0.833** (the ladder assumes 0.10 — the two legs are nearly the
  same trade, and the ladder's model cannot express a correlation at all: it treats
  IC+IM as one notional block).
- equity sleeve vs futures correlation **−0.038** (declared 0.10 — this one is fine;
  the face does not cry wolf where the declaration holds).

Judgments: `DECLARED_RISK_UNDERSTATES_MEASURED` · `BAND_CUT_ALSO_CUTS_RISK` ·
`SHARPE_DISAGREES_WITH_RETURN` (best Sharpe rung = 0/1, best expected return = 3/3).

Practical reading: the in-band rung (IM 1 lot) is **also** the best Sharpe of the 16
and half the drawdown; the instructed rung earns 8.33 pp more expected return for
1.81× the vol and 2.04× the drawdown, with a *lower* Sharpe.

## 5. Known limitations (stated on the face, not hidden)

1. The rung series is **close-to-close**; r2104's `exec_vs_close` warns that a
   next-open fill convention is the implementable one. The measured ann/vol here
   therefore carry the same convention as the ladder they are compared against — the
   comparison is like-for-like, but neither is an execution-priced number.
2. `check` re-probes both futures legs (0.3 s) and digests the equity arm; the equity
   sleeve itself costs ~65 s to rebuild and is **not** re-derived by `check`. That
   scope is printed in the face (`check_scope`).
3. The equity sleeve is still sized by the ladder's `k` — that is a capital statement,
   not a measurement of the sleeve.
4. Not wired into `Tools/s6_chain_bmc.py` or `smoke_test.py`: both are shared faces and
   this is a CONTENTION round. The face is check-only and standalone until a clean
   window wires it.

## 6. Honest not-done

- Full `python -m smoke_test` (570+ legs) not run — contention window, and `smoke_test.py`
  is a shared face that may not be edited this round.
- The ladder's two constants (`L2_CARRY_VOL`, `RHO`) were **not** changed: rebasing a
  published shared face onto these measurements is a clean-window job.
- `state-bm-c.json` and `fleet/machines/bm-c.json` were not written (multi-host
  co-write faces; the peer host holds them).
