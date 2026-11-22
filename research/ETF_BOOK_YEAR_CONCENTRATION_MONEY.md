# 判决里的钱：三本候选的一年集中度（etf_book_year_concentration_money）

证据截止 **2026-11-20**；源面 `results/etf_book_year_gate/YEAR-GATE.json`（asof 2026-11-20T15:54:19+0800）；本金 **1,000,000 元**；年集中线 **70%** 从 `candidate_year_gate.TOP2_SHARE_MAX` 导入。

## 一句话

- nobond_vt08_adopted: best year 2025 at 43.06% is worth 610,819 of the lifetime gain (59.3% of it); -6.31pp on that one year (-89,146 on the capital standing then) flips to a pass — top-2 share now 72.38% against the 70.00% line
- nobond_base: best year 2025 at 53.73% is worth 897,861 of the lifetime gain (57.2% of it); +0.32pp on that one year (5,257 on the capital standing then) flips to a fail — top-2 share now 69.91% against the 70.00% line
- all_classes_published: best year 2025 at 36.34% is worth 480,961 of the lifetime gain (59.8% of it); -16.70pp on that one year (-219,401 on the capital standing then) flips to a pass — top-2 share now 77.61% against the 70.00% line
- 最薄的那一本是 nobond_base：top-2 份额 69.91% 对 70.00% 的线，只差 0.09pp；换成钱，就是 2025 年那一年只要多印（或少印）0.32pp、当时本金上 5,257 元，判词就翻面。这不是能力测量，是一次舍入测量。

## 逐本读数

| 书 | 已发布判词 | 全期倍数 | 年化(年桶重算/在印) | 百万本金到 2026-11-20 | 最好一年 | 该年值多少钱 | 占全期总赚 | 到线的距离 | 该距离值多少钱 |
|---|---|---|---|---|---|---|---|---|---|
| nobond_vt08_adopted | CONDITIONAL | 2.0293× | 10.64% / 11.16% | 2,029,260 | 2025 43.06% | 610,819 | 59.3% | -6.312pp | -89,146 |
| nobond_base | ADMIT | 2.5688× | 14.43% / 15.18% | 2,568,837 | 2025 53.73% | 897,861 | 57.2% | +0.323pp | 5,257 |
| all_classes_published | CONDITIONAL | 1.8045× | 8.80% / — | 1,804,463 | 2025 36.34% | 480,961 | 59.8% | -16.700pp | -219,401 |

## 去掉最好那一年还剩什么（leave-one-out·百万本金）

**nobond_vt08_adopted**（已发布判词 CONDITIONAL）

| 去掉哪一年 | 保留比例 | 年化(其余年) | 百万本金剩 | 该年部分年 |
|---|---|---|---|---|
| 2020 | 0.9469 | 11.50% | 1,921,517 | 否 |
| 2021 | 0.9291 | 11.15% | 1,885,437 | 否 |
| 2022 | 0.9724 | 11.99% | 1,973,235 | 否 |
| 2023 | 0.9481 | 11.52% | 1,923,962 | 否 |
| 2024 | 0.8730 | 10.00% | 1,771,513 | 否 |
| 2025 **（最好的一年）** | 0.6990 | 6.00% | 1,418,441 | 否 |
| 2026 | 0.9956 | 12.44% | 2,020,410 | 是 |

**nobond_base**（已发布判词 ADMIT）

| 去掉哪一年 | 保留比例 | 年化(其余年) | 百万本金剩 | 该年部分年 |
|---|---|---|---|---|
| 2020 | 0.8184 | 13.18% | 2,102,256 | 否 |
| 2021 | 0.9148 | 15.30% | 2,350,067 | 否 |
| 2022 | 0.9772 | 16.58% | 2,510,313 | 否 |
| 2023 | 0.9500 | 16.03% | 2,440,292 | 否 |
| 2024 | 0.8852 | 14.67% | 2,273,931 | 否 |
| 2025 **（最好的一年）** | 0.6505 | 8.93% | 1,670,977 | 否 |
| 2026 | 0.9727 | 16.49% | 2,498,828 | 是 |

**all_classes_published**（已发布判词 CONDITIONAL）

| 去掉哪一年 | 保留比例 | 年化(其余年) | 百万本金剩 | 该年部分年 |
|---|---|---|---|---|
| 2020 | 0.8716 | 7.84% | 1,572,791 | 否 |
| 2021 | 0.9568 | 9.53% | 1,726,594 | 否 |
| 2022 | 1.0118 | 10.55% | 1,825,826 | 否 |
| 2023 | 0.9734 | 9.84% | 1,756,511 | 否 |
| 2024 | 0.9266 | 8.95% | 1,672,038 | 否 |
| 2025 **（最好的一年）** | 0.7335 | 4.78% | 1,323,503 | 否 |
| 2026 | 0.9927 | 10.20% | 1,791,209 | 是 |


## 这条线分不分得开「一年书」

判词 **THE_LINE_SEPARATES_ONE_YEAR_DEPENDENCE**

口径：share_of_lifetime_gain（最好一年占全期总赚的比例）对比 top-2 份额是否过线。

| 书 | 最好一年占总赚 | top-2 过线 |
|---|---|---|
| nobond_vt08_adopted | 59.3% | 否 |
| nobond_base | 57.2% | 是 |
| all_classes_published | 59.8% | 否 |

the book that clears the top-2 line also depends least on a single year, so the share line happens to sort the same way -- by 2.56pp on the safe side of the failing range -- and every book in the set still takes at least half its lifetime gain from one year (nobond_vt08_adopted, nobond_base, all_classes_published)

## 诚实话（逐条）
- 货币读数只在写明本金时出现（本面 1,000,000 元，与在册书同种子）；换个本金，全部金额按比例缩放，pp 与倍数不变。
- 最好一年的归因是**乘积的分解**，不与其它年份相加；同一年在 leave-one-out 里的保留比例才是可加的口径，两者不可混读。
- 这本书每本都有一个部分年（本批是 2026），它出现在最好一年或 leave-one-out 时会改变倍数——表里逐行标了「部分年」，没有把它当完整年用。
- 本面不动任何判词：它只重读年门的 top-2 这一行，并把到线的距离换成钱；判词以 YEAR-GATE 为正身。
- 年化有两把尺：在印的是「净值曲线 ÷ bar 数」，本表重算的是「日历年的乘积开 N 次方」，2026 是部分年，所以两者有可见差：nobond_vt08_adopted -0.52pp；nobond_base -0.75pp。倍数与金额用的是年桶这把尺，判词与在印年化以源面为准。

