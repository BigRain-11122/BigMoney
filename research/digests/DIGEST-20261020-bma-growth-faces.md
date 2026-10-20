# DIGEST-20261020-bma-growth-faces — 成长族数据面建成 + 财报面板 avail_date 缺陷发现

- 机器：bm-a（r1092）
- 授权上下文：O-20261019-2230-bm-b §2 item 5「基本面族滚动立项（回撤/成长/股东行为/季节性等）·五步制·每族带数据可达性审计」
- 状态：数据可达性审计完成；**非** prereg、**非** judged 批、零烧录、零账本行

## 一、这一轮做了什么

成长族此前在仓内**没有任何数据面**（`data/fund_history_export/` 只有 value / quality / div_events 三面），
所以无法按 quality P1 骨架接线。本轮补齐了 prerequisite：

- 新脚本 `scripts/build_growth_faces.py`（`build` / `verify` / `selftest` 三子命令，selftest 19/19 全绿、
  零网络、确定性幂等）
- 产出 `data/fund_history_export/growth_faces.parquet`：4,557,415 字节，
  `code / period_end / avail_date / np_yoy(float32) / rev_yoy(float32)`，
  与 `quality_faces.parquet` 同契约（一 code 一 period_end 一行、avail 单调、无重复期）
- 回执 `results/_growth_faces_build.json`（GREEN）

## 二、实测读数

| 项 | 值 |
|---|---|
| 源 | `data/fund_statement_export/income_faces.parquet`（461,679 行） |
| 输出 | 426,789 行 / 11,757 只 / 86 个报告期 |
| 期覆盖 | 2005-03-31 → 2026-06-30（最新期 11,449 只） |
| PIT 锚 | 法定披露日（Q1→04-30 / H1→08-31 / Q3→10-31 / 年报→次年 04-30） |
| 单调违例 | 0 |
| 重复期 | 0 |
| 空值率 | np_yoy 0.01% / rev_yoy 0.48% |
| 丢弃 | 双面全空 34,890 行（如实计数，非填充） |

## 三、真发现（本轮最值钱的部分）：源面板 `avail_date` 有系统性 +1 年偏移

对全量 461,629 行可解析行做了 observed(=源 avail_date) 与法定日期的距离分布：

| 分类 | 占比 |
|---|---|
| on_time（0–120 天） | 1.68% |
| **year_shifted（300–430 天）** | **84.38%** |
| other_late（>430 天） | 6.42% |
| early（<0 天，早于法定截止） | 7.52% |

中位距离 **360 天**。抽样核对（600519）：`2005-03-31 → 2006-04-22`、`2005-06-30 → 2006-08-23`、
`2006-12-31 → 2008-03-13`，而最新行 `2025-09-30 → 2025-10-30` 正常。
结论：**历史区间的 avail_date 不是披露日，而是被整体推后约一年**（最新行不复现，故为采集器历史区段缺陷，
非源头字段语义）。

后果与处置：
1. 若按「avail = max(法定日, 源 avail_date)」做 PIT，会让**每一条历史财务行晚一年可见** = 面被废掉；
2. 本面因此**只用法定披露日**（与 quality 面同契约），缺陷只测不用；
3. `income_faces` 同族（cashflow/balance）很可能同病——已登记 P2 技术队 T27 待核（采集器车道 bm-a）。

## 四、诚实边界

- 因子口径尚未裁剪：`np_yoy` / `rev_yoy` 是累计口径同比（YTD 同期比较），不是单季；
  稳定性/趋势类变换留给 runner 层，本面不加派生列（保持与 quality 面同构）。
- 未做 D6 邻接审计、未登记种子、未起草 prereg、未入池：这些属于下一窗的冻结窗口件。
- 2026-06-30 之后的报告期尚未入库（法定 08-31 截止，面板自然只到 H1）。
- 家族仍未判负/判正：growth 不在 `science_gates.CLOSED_FAMILIES`（已核 9 族无命中）。

## 五、下一步指针

1. `scripts/fund_growth_p1.py`：镜像 `fund_quality_p1.py` 骨架（universe/ST/cost 单源 import 不变），
   只换 `_load_growth_faces()` + 排名方向（growth 为降序）。
2. 冻结窗口五条件：probe GREEN / D6 / SEED_REGISTRY 行 / banned_direction_gate ADMIT / 冻结 commit。
3. T27：核查 income/cashflow/balance 三面板 avail_date 偏移，修采集器并重导出（bm-a 车道）。
## 六、T27 结案（r1093 本轮实测·三面 avail_date 缺陷图谱）

`scripts/fund_avail_audit_t27.py`（确定性·零网络·只读）对三面逐做「面板 avail_date − 法定披露截止日」距离分布，
按报告期类型拆分。回执=`results/_r1093bma_t27_avail_audit.json`。

| 面 | 行数 | 区间 | 中位偏移(天) | 年报外一年化占比（Q1 / H1 / Q3 / 年报） |
|---|---|---|---|---|
| income | 461,679 | 2005-03-31..2026-06-30 | +360 | 87.6% / 88.5% / 87.3% / 75.1% |
| cashflow | 292,537 | 2005-03-31..2026-06-30 | +360 | 88.5% / 87.9% / 88.1% / 73.4% |
| balance | 283,955 | 2005-03-31..2026-06-30 | −2 | 0.4% / 0.2% / 0.1% / **72.9%** |

定谳三条：
1. **income / cashflow 全线坏**（四类报告期皆 ~75-89% 被推后约一年），2015-2025 年段最重（93-99%），2026 年段正常。
2. **balance 只有年报坏**（12-31 行 72.9% 被推后约一年），季报面（0.1-0.4%）可用。三面缺陷形态不同=不是同一个全局 ffill 错，更可能是「年报 announce 列取到了下一财年」的取列/取行口径问题。
3. **消费面安全边界已核**：`quality_faces.parquet`（32 面 PIT 消费主源）实测 avail_date 与法定日均值偏移 0 天、≥300 天占比 0.0%，即法定日烘焙正确；`fund_divlowvol_p2_*` / `fund_trio_p1_diagnostics` / `fund_vq_p2_probe` 全部吃 quality 面，无越界风险。**本轮零消费者受害**，缺陷只在 statement 三面本体。

处置：
- 本面（growth/quality）继续只用法定日烘焙 PIT，禁用面板 avail_date（growth builder 已是此口径）。
- 三面 avail_date 列为**已知坏列**：任何新 prereg 若要消费 statement 面，必须自行按法定日重算 PIT；修复采集器（更新 `update_fund_statements.py` 的年报 announce 列取法）排在 T27 修法切片，需重导出全史并过 overlap 校验。
- 该发现不改任何判线与账本：本面仍未 prereg、未烧录、未判负判正。
