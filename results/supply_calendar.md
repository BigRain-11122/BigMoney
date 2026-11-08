# 供给日历面：池子空着，是没题，还是题都过不了自己的日历

判词 **NO_CANDIDATE_PASSES_CALENDAR** —— every candidate the desk has judged was refused by its own calendar: the empty pool is not a missing topic, it is a missing year of evidence

| 候选 | 读数 | 判决 | 未过的检查 | 收据 |
|---|---|---|---|---|
| nobond_vt08_adopted | phase | CONDITIONAL | Y4_top2_share | results/etf_book_phase_gate.json |
| nobond_base | phase | UNADJUDICABLE_PHASE | Y3_worst_year, Y4_top2_share | results/etf_book_phase_gate.json |
| nobond_vt08_floor_050 | phase | UNADJUDICABLE_PHASE | Y4_top2_share | results/etf_book_phase_gate.json |
| all_classes_published | single_phase | CONDITIONAL | Y4_top2_share | results/etf_book_year_gate/YEAR-GATE.json |

## 拒的是书还是尺子（r1426 口径复读）

- 尺子可自判且同样拒：nobond_vt08_adopted, nobond_base, nobond_vt08_floor_050 —— 拒是真的，处置是等证据或重切书
- 无相位集、尺子未复读：all_classes_published

## 拒的理由用的是哪把尺子（r1431 采纳：years_for_half）

- nobond_vt08_adopted refused at years_for_half median 2 vs line 3 (FAIL)
- nobond_base refused at years_for_half median 2 vs line 3 (FAIL)
- nobond_vt08_floor_050 refused at years_for_half median 2 vs line 3 (FAIL)
- all_classes_published has no years_for_half reading on record

选举来自 `scripts/etf_book_admission_ruler_election.py`（fixtures 上选出，不在本书上挑）；每本候选的读数抄自相位闸收据的 caliber 裁定块，本面不重算。判决词不变：换的只是「拒的理由」，不是「拒」本身。

## 这个拒法换个大点的窗还在吗（r1433 探针 · 只印不改）

- window: years_for_half median 2/3 vs line 3, 3 fail/2 undecidable/0 pass over 5 starts -> a wider window changes nothing where it can be judged (widest start 2013-01-01 cagr 8.060% maxdd -16.850%; plain arm only, exploratory -- decides nothing)

| 起点 | 尺子中位 | 状态 | 年数 | 年化% | 夏普 | 回撤% |
|---|---|---|---|---|---|---|
| 2013-01-01 | 3 | UNADJUDICABLE_CALIBER | 14 | 8.060 | 0.850 | -16.850 |
| 2015-01-01 | 2 | UNADJUDICABLE_CALIBER | 12 | 8.310 | 0.871 | -16.060 |
| 2017-01-01 | 2 | FAIL | 10 | 8.100 | 0.845 | -15.870 |
| 2019-01-01 | 2 | FAIL | 8 | 9.700 | 1 | -12.560 |
| 2020-01-01 | 2 | FAIL | 7 | 8.530 | 0.886 | -12.990 |

读数抄自 `results/etf_book_window_sensitivity.json`（arm=plain · cutoff 2026-11-06），只重排不重算；这是**探索性**探针：无预注册、无判决、不入账本——它不安检任何人，只是让读者知道「2 年」这个数是不是换个窗就变。

读法：只有字面 `ADMIT` 算过。CONDITIONAL / REFUSE / UNADJUDICABLE_PHASE 在本面一律是拒——日历闸不肯放行的候选，不能当作「今天就能点火」的供给。「没人写题」要开题，「题都过不了日历」要等证据或重切书，两件事的处置相反，把两种都印成 agenda debt 等于没说。
