# 供给面：池子空着，是因为没有活，还是因为没人把活放进池子

判词 **AGENDA_DEBT** —— no candidate passes its calendar (4 refused): nobond_vt08_adopted: CONDITIONAL via Y4_top2_share; nobond_base: UNADJUDICABLE_PHASE via Y4_top2_share, Y3_worst_year (phase spread 22.37pp vs margin 14.78pp -- the phases do not agree on the verdict); nobond_vt08_floor_050: UNADJUDICABLE_PHASE via Y4_top2_share (phase spread 15.64pp vs margin 12.79pp -- the phases do not agree on the verdict); all_classes_published: CONDITIONAL via Y4_top2_share (never measured: C1_capacity) | ruler: 3 refusal(s) survive a self-adjudicable caliber (nobond_vt08_adopted, nobond_base, nobond_vt08_floor_050) | no phase set, ruler not re-read (all_classes_published) | reason: nobond_vt08_adopted refused at years_for_half median 1 vs line 3 (FAIL); nobond_base refused at years_for_half median 2 vs line 3 (FAIL); nobond_vt08_floor_050 refused at years_for_half median 2 vs line 3 (FAIL) | window: years_for_half median 2/3 vs line 3, 3 fail/2 undecidable/0 pass over 5 starts -> a wider window changes nothing where it can be judged (widest start 2013-01-01 cagr 8.060% maxdd -16.850%; plain arm only, exploratory -- decides nothing) | half_year: nobond_vt08_adopted: half of its 7-year net (+78.08pp) is supplied by 2025 +43.06pp, which is the newest FULL year (the last row is a partial year) (dominant year 2025 = +43.06pp = 55.1% of net) -> one year supplies the half [phase set: one_year 3/5 phases] (exploratory -- decides nothing)。另一层：即使有一个候选过闸，已定价的最高上限 13,794,151 也只有地板的 69.0%（差 6,205,849），该上限出自 priced_envelope_R20

| 来源 | 数 | 能不能立刻点火 |
|---|---|---|
| 池内 ready | 0 | 是（已入池） |
| 任务板 open 未认领 | 0 | 是（认领即开动） |
| 队列活草稿（状态列是 open/pending/draft） | {"tech.md": 0, "explore.md": 0} | 否，每行还要先过预注册冻结 |
| 队列已消耗行（状态列 done/closed，含 rNNN 后缀） | {"tech.md": 27, "explore.md": 31} | 无需动作 |
| 队列状态不可读行（状态列里是测量值，按名列出） | {"tech.md": [], "explore.md": [["E16", "0.455 ＞ null family p95 0.077·n_ok 200/200·CENSUS-2026-10-09.json·refuse-if-exis"], ["E26", "23.98bp on the 83 entry bars."]]} | 不是草稿，是队列卫生项 |
| backlog 未认领行 | 5 | 否，跨公司 backlog，行内有属主 |

地板 3，当前差 **3** 个批次。

读法：池子空是一种状态，两种原因。有活没入池=机制故障（该入池）；根本没活=选题债（该开题）。把两种都印成 supply_floor，红就一直红着、而且没人能对着它做事。

## 归因：calendar

已判过的候选，一个都没过自己的日历闸：

| 候选 | 判决 | 未过的检查 | 没测的列 | 收据 | 被取代的读数 |
|---|---|---|---|---|---|
| nobond_vt08_adopted | CONDITIONAL | Y4_top2_share | — | results/etf_book_phase_gate.json | CONDITIONAL via Y4_top2_share [single_phase · results/etf_book_year_gate/YEAR-GATE.json] |
| nobond_base | UNADJUDICABLE_PHASE | Y4_top2_share, Y3_worst_year | — | results/etf_book_phase_gate.json | CONDITIONAL via Y4_top2_share [single_phase · results/etf_book_year_gate/YEAR-GATE.json] |
| nobond_vt08_floor_050 | UNADJUDICABLE_PHASE | Y4_top2_share | — | results/etf_book_phase_gate.json | — |
| all_classes_published | CONDITIONAL | Y4_top2_share | C1_capacity | results/etf_book_year_gate/YEAR-GATE.json | — |


## 地板：日历过了也不够

| 读法 | 数 | 出处 |
|---|---|---|
| 地板（产能门槛） | 20,000,000 | scripts/candidate_year_gate.py::CAPACITY_FLOOR_CNY |
| 已定价的最高上限 | 13,794,151 | priced_envelope_R20 |
| 缺口 | 6,205,849 | results/etf_book_capacity_floor_gap.json |
| 上限／地板 | 69.0% | FLOOR_BEYOND_PRICED_ENVELOPE |

即使有一个候选过闸，已定价的最高上限 13,794,151 也只有地板的 69.0%（差 6,205,849），该上限出自 priced_envelope_R20
