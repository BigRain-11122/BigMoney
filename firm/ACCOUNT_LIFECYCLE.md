# Bigmoney 账户生命周期正典 ACCOUNT_LIFECYCLE（v1.0）

> **定位声明（唯一职责）**：把「判决→纸盘→CEO 认可→模拟盘→实盘」五环串明成一册（O-20260926-1355 · T-83 s3 件②；s1 L5 靶=「四环机制全部已建、无一册串明」，本册即串明面）。**薄法指针**：每环机制唯一权威=§二各行载体，本册零阈值复制零机制重述；判据路由=`firm/JUDGMENT_MATRIX.md`（s3 件①·同批落地）。

## §一 生命周期链总图（五环）

```
R1 判决（回测门禁+注册） → R2 纸盘（前向观察） → R3 CEO 认可（台账） → R4 模拟盘（live 网关） → R5 实盘（CEO 唯一门）
```

环门不可跳；CEO 直令例外=令内留痕+本册行级追加注记（§五.1）。

## §二 五环载体表

| 环 | 门（准入判据面） | 唯一权威载体 | 自动化执行面 |
|---|---|---|---|
| R1 判决 | G1'/G2/G3 门禁链（判据宪法+α 机制段四选一+D6 同族拒收+前向锁盒） | `research/BACKTEST_SCIENCE.md` + `scripts/science_gates.py` + `research/CE_ADMISSION_V1.md`（稳定优先准入正典层） | 批 runner+损耗账 `results/gate_attrition.json` |
| R2 纸盘 | anchor gates（注册组合字节恒等·锚漂移即中止不碰注册件）+月度聚合考核 | `research/PAPER_GUARD_DUAL_RAIL.md` + `firm/hr.py`（阶梯/淘汰执行面） | `live/paper` 引擎 + PROSPECT 车道（`scripts/t24_prospect_paper.py`/`t24_prospect_promotion.py`）+ 回放（`research/RETRO_PAPER_2026_PREREG.md`·T-79） |
| R3 CEO 认可 | 认可台账在册（呈报=待决策项+证据+一句话方案） | `docs/CEO_APPROVALS.md`（O-1326 认可+模拟盘网关队列） | GM 呈报·CEO 署名（人类决策环） |
| R4 模拟盘 | 锚定门禁+REGIME_GUARD（v3 enforce=2026-10-01 三重门：批准件+日期门+环境请求）+成交验证 | `live/`（gateway/paper 三面）+ `firm/risk/` | `python -m live.paper` + t35 链（S6 有新 bar 轮）+ `scripts/t35_paper_export.py`（城侧只读导出） |
| R5 实盘 | CEO 唯一门（保留面·2027-04 判据未触发=不呈请） | `firm/RULES.md` §2 | 无（人类决策环） |

## §三 晋升/淘汰（环内推进）

数值唯一权威=`firm/hr.py`（INTERN→TRAINEE→TRADER→SENIOR→PRINCIPAL 阶梯+淘汰条款）；PROSPECT→INTERN 晋升门=`scripts/t24_prospect_promotion.py` 三腿（纸面月≥1·hr 阈值共享 + G2 证据包 + T-22 虚拟时点 beat_rate_6m≥0.70）；管线说明=`firm/review/promotion.md`。本册不复制任何阈值。

## §四 账户族 × 环覆盖表（车道归属+报告面）

| 族 | 目录（results/） | 环覆盖 | 报告归属 |
|---|---|---|---|
| 真账本 paper（6 员） | `paper/` | R1→R5 全链候选 | t35/daily_scorecard/CEO 面 |
| PROSPECT 观察池（22 员） | `prospect_paper/`+`prospect_g2/`+`prospect_promotion/` | R1→R2 观察（构造性排除 CEO 面·O-2045） | 观察面+晋升门评估 |
| AGGR 激进（5 账户 ×¥1M） | `aggr_paper/`+`aggr_capacity_face/` | R2 实验观察车道 | 独立车道（marks 非试验账本·不入 t35/scorecard CEO 面） |
| ALLOC 配置（7 账户） | `alloc_paper/`+`alloc_s2_cells/`+`allocation/` | R2 mirror frozen cells | 独立车道（marks 观察账本） |
| GRID 网格（5 cells） | `grid_paper/`（已接线·09-28 首跑窗·未物化如实） | R2 实验观察 | 独立车道 |
| CN-* 原生组合 | T-73 s3 纸盘族 | R1→R2（prereg→判决台→纸盘） | 判决台+独立车道 |
| 回放纸盘（17 台账） | `retro_paper_2026/` | R2 离线回放（非前向·一页榜） | 呈 CEO 一页榜 |
| 城侧导出 | `paper_export/` | R4 只读消费面 | 城侧只读 |

## §五 纪律

1. **环门不可跳**：任何账户族不得绕过在环门直达下一环；CEO 直令例外须令内留痕+本册行级追加注记。
2. **marks 非试验账本**：实验观察车道（AGGR/ALLOC/GRID）marks 计数=+0，判定走各自 prereg——防观察数据污染试验账本（O-1126/O-1145 接线纪律聚合）。
3. **本册=串明面非执行面**：环门机制变更=各载体正典流程（T2 立法+7 天否决窗），本册随之改指针；族增殖（新车道）=§四加行+注册规范。

> 落款：GM（quant 专管会话）亲执 · O-20260926-1355 · T-83 s3 件② · 2026-09-26 · 复审锚=本文件（post_review 行 T-83-S3-GM-DELIVERABLES）
