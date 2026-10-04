# BigMoney QA self-verification r712 (mass-trial report card face)

> Group charter: docs/qa-smoke-test-charter.md (BigMoney section). Product = 千人试用三波合账成绩单
> (scripts/mass_trial_report.py + results/mass_trial/report_card.json + docs/mass_trial/REPORT-CARD.md
> + beat_market.html §四). Report-only L1 aggregation: ZERO new judgments, ZERO engine, ZERO network,
> ZERO threshold changes (frozen wave judge files consumed verbatim).

## checklist

- [x] 1. selftest clean -- mass_trial_report.py selftest 11/11 PASS rc0 (funnel math / passer extraction / zh family map / determinism byte-equal / incomplete-wave refusal / missing-summary refusal / empty-dir refusal)
- [x] 2. run clean on real data -- rc0: 3 waves, 4/1748 G1-pass, 0 G2-eligible
- [x] 3. numbers cross-checked verbatim vs frozen judge files -- w1 975/166/166/0, w2 4836/806/805/1, w3 4814/785/777/3, totals 10625/1757/1748/4; passers W2-23057 (oos 1.93, dsr 0.53), W3-23027 (1.44, 0.49), W3-27009 (2.30, 0.24), W3-46133 (1.27, 0.49); G2 gate 0/4 (DSR 0.24-0.53 vs 0.95; PBO 0.19-0.37 vs 0.25)
- [x] 4. honesty face present -- negative-leaning outcome reported as-is (0 hires; direction clue sentiment.turnover_surge x2 disclosed as clue NOT promotion); evidence_cutoff 2026-09-22 carried top-level in JSON (C2 legal key)
- [x] 5. CEO visibility wired -- beat_market.html §四 (MASS-SECTION markers, YTD-append convention) + plain-language md face

## evidence pointers

- generator: scripts/mass_trial_report.py (run | selftest)
- machine twin: results/mass_trial/report_card.json
- plain-language face: docs/mass_trial/REPORT-CARD.md
- CEO page section: results/beat_market.html §四
