# P-4 批 2A · 技术分析/操作风格 A 层迁族 core48 mini 海选（预注册）

> **预注册纪律**：本文档在批跑前写死（BACKTEST_PLAN 铁律 ③：禁止跑到达标为止；禁止跑后调门槛；禁止重跑）。
> 令链：CEO 令 O-20260923-1828（技术分析+操作风格策略族建设）→ 调研纪要 `research/digests/DIGEST-20260923-ta-styles.md`
> → playbook §6 P-4 增批 2A（GM 会话车道）→ 认领 MSG-20260923-1841（F-04 认领纪律：开工前 inbox 声明）。
> 批跑脚本：`scripts/p4_batch2a_screen.py`（`p4_batch1_screen.py` 范式直系，零引擎改动；
> 信号单一真值源=`strategies/ta.py`，脚本 import 消费，**零双实现**——F-05 教训入法）。

## §1 问题

动物园技术分析风格缺位（经典指标系/K 线形态系/量价确认系，zoo §十一）中 8 个族，
能否在 core48 权益池过 G1' 记录门（i 线 0.3521 / 技能线 vi 0.4004 / CE 线 max 规则），
或在低相关袖珍口径（max|corr|<0.30 vs 3 在册交易员）上提供分散化素材？
CEO 令「搜技术分析，操作风格分析等，好好建立各种策略。满足短线 3-15 天」的批量化诚实回答。

## §2 素材裁定（反重复：已筛族禁重跑、已有机制禁重建）

**入批 8 族**（6 迁 + 2 新设计，M0923 语义冻结 + 经典定义）：

| # | 族 | 处置 | 理由 |
|---|---|---|---|
| zoo#24 | RSRS 择时 `rsrs_timing` | 迁（M0923 `RsrsTiming`） | 光大研报族；**面板化适配预注册**：M0923 单 target 语义→逐 ETF 自算 β z 态；z_win 600→250（core48 2020 锚定面板长度，如实披露口径差） |
| zoo#25 | 连阳 `streak_up` | 迁（M0923 `Streak`） | 与累计动量不同维度；本仓 36 骨架无此构造 |
| zoo#25 | 放量突破 `vol_breakout` | 迁（M0923 `VolBreak`） | **同族变体折扣预注册**：P1 已筛 `breakout_confirm`（突破新高+放量，经济意图同域）；构造差=破前 N 日 **high** 滚动高+独立破位退出；读结果按同族折扣 |
| zoo§1.2 | 尾盘强势 `strong_close` | 迁（M0923 `StrongClose`） | playbook A 层第一优先行；收盘位置+放量日频诚实近似 |
| 新 | MACD 趋势 `macd_trend` | 迁（M0923 `MacdTrend`） | 经典 TA 指标系两库皆缺；Appel 金叉+零轴双条件 |
| 新 | KDJ 超卖 `kdj_reversal` | 迁（M0923 `KdjReversal`） | 中国市场经典振荡指标；J 超卖+趋势过滤 |
| 新 | 锤子线 `hammer_reversal` | **新设计** | 经典 K 线形态（Wikipedia 定义逐字：小实体+下影≥2×实体+近无上影+下跌语境）；两库皆无 K 线形态族=真实缺口 |
| 新 | 阳包阴 `engulf_reversal` | **新设计** | 同上（阳线实体吞没前阴实体+下跌语境） |

**出批（如实记）**：
- `high_52`：NSP1 `high252_prox_top5_r20@ce` 已立 G1' 候选（full 0.438/OOS 0.889）——同族再筛=dredging；
- `resid_mom`：动量域变体已双筛（`xsec_mom_120` P1 + `sharpe_mom_120` NSP1 0.028≈0）——三筛=dredging 风险；
- `BollingerRev`：≡ `strategies/mean_reversion.bollinger_breakout` 同构（z-score 下轨回归），P1 已筛；
- 打板四族/次新/lhb/mood：批二 B 层（O-20260923-1738 链，bm-b 车道）；
- GridTrade/补仓摊薄：需引擎分批建仓支持，批三 spec 线照旧。

## §3 固定网格（无搜索）

**8 入场 × 2 退出制 = 16 格**，每格 ×(1×+×2 成本压力)。

**构造逐字 = `strategies/ta.py`（冻结参数表如下，与代码逐字一致；syms 逐只 Series 应用，
批一 `sym_panel` 约定 (pos>0) 二值化，J7 坑遵守）**：

| 族 | 冻结参数 | 状态语义 |
|---|---|---|
| `strong_close` | pos_th=0.85, vol_mult=1.5, vol_len=20 | entry=收盘位置≥0.85&量≥1.5×MA20&收阳；exit=位置<0.5；ffill 状态机 |
| `macd_trend` | fast=12, slow=26, signal=9 | condition-state：DIF>DEA 且 DIF>0（M0923 逐字，日频重估） |
| `kdj_reversal` | kdj_n=9, entry_j=0, exit_j=80, trend_ma=60 | entry=MA60 上&J<0；exit=J>80；ffill 状态机 |
| `rsrs_timing` | window=18, z_win=250, buy_z=0.8, exit_z=−0.8 | entry=z>0.8；exit=z<−0.8；ffill 状态机 |
| `streak_up` | streak_n=3, min_up=0.0 | entry=连 3 阳计数；exit=断阳；ffill 状态机 |
| `vol_breakout` | brk_len=20, vol_mult=1.5, vol_avg_len=20, exit_len=10 | entry=破前 20 日 high&量确认；exit=破前 10 日 low；ffill 状态机 |
| `hammer_reversal` | body_max=0.35, shadow_mult=2.0, drop_th=−0.05 | entry=锤子形+5 日跌≥5%；exit=收回 MA20；ffill 状态机 |
| `engulf_reversal` | drop_th=−0.05 | entry=阳包阴+5 日跌≥5%；exit=收回 MA20；ffill 状态机 |

退出制（2）：default（引擎默认）| CE（注册机契约：桥接 params time_decay 25d/5% + trailing 0.10 + ExitPatch loss_time_days=16，退出优先级零改动）。

## §4 数据与门（记录常数纪律，J19 漂移免疫范式）

- 宇宙=core48 裸码 48 只；面板截断 evidence_cutoff=**2026-09-22**（G2_NSP1/批一范式：批只判当日证据，此后数据增长永不破锚）；OOS=2025+ 恒盲；成本 13bp 恒开。
- G1' 六条款逐字 = `p2_calibration.json g1_prime_gate`。
- **default 格 i 线 = 记录值 0.3521**（p2_calibration n=100）；**CE 格 i 线 = max(本批 CE 随机 p95, 批一记录 CE 线 0.4474, NSP1 记录 0.4229, 0.3521)**——取最严可辩护线，跑前写死，禁跑后换口径。
- **vi 技能线 = 记录值 0.4004**（被动+0.1，政体无关）。
- 随机基线：n=50/退出制（p∈{0.02,0.05}×25，seed 基 **42_000**（批一 41_000、NSP1 40_000，本批独立新抽样））；被动 EW48 双口径（J8 公式）=一致性信息列。
- 锚定硬门：3 在册交易员逐位复现注册证据（member_run，evidence_cutoff 截断）；任一破=**批无效**。
- 补丁硬门：self_test_patches（Cost/Exit 补丁咬合+恢复）。
- **TA 自检硬门（本批新增）**：8 函数合成序列二值性+无 NaN+因果性（截断前段逐位一致）全过才许跑批（NSP1 跑前自检范式，实测已过）。
- ×2 成本压力=信息列（G2 才是裁决关）；袖珍标签=信息性（!g1_pass & full>0 & OOS 双正 & ≥30 笔 & max|corr|<0.30）。

## §5 预注册预测（跑前写死，§8 对账）

1. G1' 候选 **0-2 格**（点估 0-1）：8 族全状态制→批一机制读数「状态制 CE 增益≈0」适用；先验最强=strong_close（M0923 游资族在 A 股短线文献最稳健）与 macd_trend@default（趋势态），但 vi 0.4004 是高墙（P1 36 骨架仅 3 员在册级通过）。
2. **反转族（kdj/hammer/engulf）全期 Sharpe 预期低于 vi**（批一预测⑤同源：IS 段拖累），OOS 或双正 → 袖珍候选主产地；若 hammer/engulf 5% 跌语境在 core48 触发<30 笔→条款 iv 诚实判负（形态族在宽基 ETF 的低频性=真实边界）。
3. `vol_breakout` **同族折扣**：P1 已筛 breakout_confirm 未过 G1' → 本族过线概率低；×2 预期深红（churn×成本，J15 弹性律）。
4. `macd_trend` condition-state 高换手（NSP1 dual_ma 迁移先例 default 深负 −0.129 类似族）→ default 全期中低、CE 砍笔或有小增益（批一机制：增益=砍笔量）。
5. `rsrs_timing` z_win=250 暖机吃 ~1 年面板 → 有效信号窗缩短；面板化（48 标的）vs 光大单指数语义差=读数折扣；笔数风险中等。
6. `streak_up`/`strong_close` 短持有事件族→与在册 3 员低相关可期（NSP1 族依赖修正：事件/短趋势族可达），袖珍候选。
7. 随机 null：default p95 预期 0.35-0.45 带（记录门 0.3521 不动）；CE p95 预期 0.42-0.50 带（历史 0.4229/0.4474 邻域）。
8. 批非无效（锚定预期全绿：ta.py 零引擎改动+管线零改动）。

## §6 判决规则（跑后禁改）

- 幸存者=**G1' 候选，本批不注册**（G2 深化=另开预注册：±邻域+×2/×3 成本+逐年）。
- 0 候选=诚实判负收线，动物园 §十一 TA 系批 2A 线关账；排队族（#48 CCI/晨星/收缩系）不受影响。
- 禁跑后调阈值/禁重跑/禁换口径；袖珍候选若出现 → P3 类并入决策另开预注册（SLEEVE_P3 修正案条款：成员须 ×2 存活+全期>0，单低相关条款不足立分散化）。

## §7 试验账本（引擎试验记账，研究线 N 连续口径）

prev_total=**1883**（`results/p5_random_entry.json` trials_ledger.total，r13 现值）+
本批 **137**（16 格×(1×+×2)=32 引擎跑 + 100 随机 + 3 锚 + 2 被动）= **total 2020**。
账本以本批 JSON `trials_ledger.total` 为面板真值源（build_status 链接线）。

## §8 跑后对账（跑后填，本节跑前为空）

（待跑批后回填：批有效性硬门、结果全景、§5 预测逐条对账、机制读数、收线。）

—— quant 专管 GM 会话 · 研究部（P-4 批 2A） · 2026-09-23 18:52 预注册
