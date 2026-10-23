# Digest 2026-10-24 bm-a -- does the high-roe fallback tail survive four artifacts?

Evidence: `results/fund_avail_tail_probe.json` (cutoff 2026-06-30, 423821 income rows, 2010+ era, fallback 53130 = 12.54%). Script `scripts/fund_avail_tail_probe.py` (selftest 14/14). Pure measurement on committed faces: no row re-dated, no parquet rewritten.

## Question

r1105 published a 24.6pp spread: income deadline-fallback is 9.5% in the bottom roe decile and 34.1% in the top, stable inside every report quarter. Four artifacts could produce that without any filing behaviour.

## Answers (decile spread = top minus bottom, percentage points)

| artifact | test | spread | verdict |
|---|---|---|---|
| A1 ratio-specific | rank by net profit / by revenue (alone) | -7.64 / -19.89 | big firms file EARLIER |
| A1b size control | roe spread INSIDE revenue band / profit band | 17.528 / 22.139 | survives size control |
| A2 denominator | drop degenerate roe (|roe|>200 or bps<=0) | 8.13 (clean) / 11.31 (winsor 1-99) | survives |
| A3 restatement | drop rows revised >365d after availability | 8.84 | survives |
| A4 quarter mix | roe spread inside each report quarter | 03:8.389, 06:6.415, 09:9.576, 12:18.071 | already pinned in r1105 |

## Numbers worth reading twice

- Restatement is not the driver: the top roe decile is 40.38% rows whose stored stamp is more than 365d past their availability, and dropping exactly those rows moves the spread from 11.31 to 8.84 pp (top decile 40918 -> 24421 rows).
- Degenerate denominators are too rare to carry it but they ARE the densest concentrator: 24589 rows (5.80% of scope) have |roe|>200 or non-positive book value and their fallback share is 73.94% against 8.754% for the clean universe, i.e. a 8x lift. The clean-universe spread stays 8.13 pp, so the tail is not manufactured by them -- but a consumer that ranks raw roe will put degenerate rows at the top AND on the deadline bound, which is the worst pair.
- Size and roe point in OPPOSITE directions, so size cannot explain the tail: ranking by revenue alone gives -19.89 pp (big firms file EARLY) and by profit alone -7.64 pp, while inside a revenue band the roe spread RISES to 17.528 pp and inside a profit band to 22.139 pp -- conditioning on size uncovers the roe effect instead of absorbing it.
- Fallback rows ARE slower to be revised too, but in the other direction from the hypothesis: median revision lag 363.0 d (fallback) vs 365.0 d (verified), p90 787.0 vs 377.0.

## Consumer decision

The residual fallback block is behavioural and small (12.54% of 2010+ income rows, 1.87% of the last 8 periods a live panel consumes), and it is not manufactured by the ratio, the denominator, or restatement. So: keep `avail_event` as the ranking date, carry the existing `fallback` boolean through as a confidence column, and do NOT exclude fallback rows -- excluding them would cut the high-return tail selectively (r1103 already measured that direction: 10% of the sample, 38% of the top decile) and bias the panel downward.

## Left open

- Why high-roe names file late is still unexplained (auditor workload? more complex recognition?). This probe only rules out the four artifacts.
- pre-2010 era (42.4% fallback) is out of scope by construction: too few in-window stamps to separate behaviour from missing data.
