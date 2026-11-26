# QA — bench_donchian_unit_audit (r2142, bm-c)

## What was checked

| # | check | evidence |
| --- | --- | --- |
| 1 | the local state machine reproduces `bench_generic.sig_donchian` bit-for-bit on the card's own inputs | `fidelity_long`/`fidelity_ls` = true for all 6 combos in `results/bench_donchian_unit_audit.json`; printed in the page's Reading 2 pipeline |
| 2 | the printed donchian arms are 100% short, not breakout rules | `printed_state.share_short` = 1.0 and `long_bars` = 0 for all 6 combos |
| 3 | flipping `long_only` changes nothing | `flags_identical` = true for all 6 combos (identical series, not merely equal summary stats) |
| 4 | the two series really are two units | `unit_gap_median_high_over_close` per product: 96x–6980x |
| 5 | the card tokens move | `census_commodity` CENSUS_SIGN_MIXED → CENSUS_LEANS_POSITIVE once the 4 artifact rows are dropped (`card_tokens`) |
| 6 | the reproduction of the card's own number | card -4.54% vs reproduced -4.52% (commodity 20/10), card -13.35% vs -13.58% (fut_trend); differences are the vintage gap (cards 11-24/23, panel now 11-25) |
| 7 | determinism | `--check` leg "deterministic payload" builds the payload twice and compares after dropping `generated` |
| 8 | published face equals a fresh recomputation | `python scripts/bench_donchian_unit_audit.py --verify` → `MATCH` |

## Commands run

```
python scripts/bench_donchian_unit_audit.py --check    # 16/16 PASS
python scripts/bench_donchian_unit_audit.py           # writes json + page
python scripts/bench_donchian_unit_audit.py --verify   # MATCH
```

## Not verified (honest)

- The unit-fixed column is a size-of-error reference, not a re-run: raw `high`/`low`
  still contain contract rolls, and no random-sign control was run on it.
- The audit does not repair `bench_generic.build_signals`. Handing `sig_donchian`
  one unit is a shared code face; this round was a contention window (`rc=3`), so
  only new-file faces were written.
- Nothing here re-opens `bench_verdict_book` (r2140) or `bench_live_thread_dedupe`
  (r2141); the donchian rows they counted as EXHAUSTED evidence remain in those
  faces until the fix lands and the cards are re-derived.
