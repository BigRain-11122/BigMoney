# BigMoney QA self-verification r713 (month-exam readiness probe)

> Group charter: docs/qa-smoke-test-charter.md (BigMoney section). Product = 10-31 月界首考准备度探针
> (scripts/month_exam_readiness.py + results/month_exam_readiness.json +
> docs/month_exam/READINESS-2026-10-05.md). Read-only L1 aggregation: ZERO new
> trials, ZERO marks writes, ZERO engine, ZERO network, ZERO threshold faces
> (all numbers import-derived from in-repo artifacts).

## checklist

- [x] 1. selftest clean -- month_exam_readiness.py selftest 13/13 PASS rc0 (ETF-calendar floor parse / spm face / traders RED-path / accounts floor-lag AMBER path / trio 3-shard worst-of / v3 / four-piece / anchors / nav_series+state_hist extraction variants / md byte-idempotency)
- [x] 2. run clean on real data -- rc0, verdict=AMBER (8 GREEN + 1 AMBER fund-trio), days_to_exam=26, expected_marks_floor=2026-09-30 (holiday-stale = legal, resumes 10-08)
- [x] 3. numbers cross-checked vs source artifacts -- traders=6 @ export 2026-09-30; paper accounts 20 AGGR + 7 ALLOC + 5 GRID + 2 SYSV1 all marks_last=2026-09-30 (no floor lag); mass card 10,625/1,757/1,748/4/0 verbatim from results/mass_trial/report_card.json totals; trio NULLS shard states verbatim from results/runnable_pool.json (ready+owner bm-b 07:16:12 = in-flight AMBER)
- [x] 4. honesty face present -- fund-trio AMBER (bm-b canonical in-burn) reported as-is, NOT a blocker; exam-time floor requirement (2026-10-30) stated as forward gap; t28 last verdict carried verbatim (NOT-DEMONSTRATED honest negative); JSON carries top-level honesty face (+0 trials +0 marks)
- [x] 5. CEO visibility wired -- plain-language md face (一句话结论 + per-face table + 当前活/下个里程碑), same-day regen byte-idempotent (SHA256 equal on double run), zh content per CEO 白话律

## evidence pointers

- generator: scripts/month_exam_readiness.py (run | selftest)
- machine twin: results/month_exam_readiness.json
- plain-language face: docs/month_exam/READINESS-2026-10-05.md
- law refs: 意义律 O-20260930-1901 (queue-by-consumer-urgency: REEVAL→纸盘 top lane) + PLAN.md L220 (2026-10-31 首次自动晋升检查) + firm/STABLE_PROFIT_MODEL.md L24 (10-31 正式验收复跑窗)
