# P-4 民间大扩容批 · core48 海选（预注册，跑前写死）

> **预注册纪律**：本文档在批跑前写死（BACKTEST_PLAN 铁律 ③：禁止跑到达标为止；禁止跑后调门槛；禁止重跑）。
> 令链：CEO 令 O-20260923-2134（「策略和流派还是太少，好好规划一下，极大的丰富，样板数量不够多跑回测没意义」+「好好去梳理一下民间的策略什么的，多来点策略」）
> → 调研纪要 `research/digests/DIGEST-20260923-folk-strategies.md` → 动物园 §十二登记（29 行）
> → 认领 MSG-20260923-2136（F-04）。
> 批跑脚本：`scripts/p4_folk_screen.py`（`p4_batch2a_screen.py` 范式直系，零引擎改动；
> 信号单一真值源=`strategies/patterns.py`+`strategies/folk.py`，脚本 import 消费，零双实现）。

## §1 问题

民间策略图谱 26 族（经典 K 线形态 18 + 民间手法 8，全日线 OHLCV 可算、冻结参数）
能否在 core48 权益池过 G1' 记录门（i 线 0.3521 / vi 0.4004 / CE 线 max 规则），
或在低相关袖珍口径（max|corr|<0.30 vs 3 在册交易员）提供分散化素材？
CEO「极大丰富+大样本」令的批量化诚实回答——**26 入场 × 2 退出制 = 52 格 = 项目单批最大格数**。

## §2 素材裁定（反重复：逐族同族折扣预披露）

**入批 26 族**（构造逐字=`patterns.py`/`folk.py` 冻结代码，参数表见 §3）。
**同族折扣行（读结果时折扣）**：
- `needle_probe` vs 批 2A `hammer_reversal`（袖珍）：同为长下影反转，差异=needle 需**次日收复针高点确认**（构造不同但经济意图近族）；
- `box_breakout` vs 批 2A `vol_breakout`（G1' 候选@ce）与 P1 `breakout_confirm`：箱体约束+量确认突破三连近族；
- `low_suction` vs P1 `pullback_bounce`：上升趋势回踩族；
- `ma_converge_break` vs `yang_break_3ma`：批内同族对（事件 vs 状态变体）；
- `three_soldiers` vs 批 2A `streak_up`（判负 −0.976）：连阳延续族跨域单向门风险预判（士兵=实体递增+三日窗=不同构造）。

**出批（如实记）**：接力/卡位/半路/首阴/断板系（行为延续类=批 2A 深负族+打板四族在批二 B 层）；分时/竞价类（日线铁律禁项）；圆弧底/头肩/波浪/缠论（日线诚实口径构造主观性过高=出谱 D 级）。

## §3 固定网格（无搜索）

**26 入场 × 2 退出制 = 52 格**，每格 ×(1×+×2 成本压力)。

| 流派 | 函数（冻结参数） | 类/离场 |
|---|---|---|
| patterns | morning_star(−0.03/0.01) · three_soldiers(0.004) · piercing_line(−0.02) · needle_probe(−0.05/0.02) · three_methods_up(0.03) · island_reversal(0.01) · doji_at_low(−0.05) · big_yin_shakeout(−0.035) · macd_divergence(30) · obv_divergence(30) · vol_drought_reversal(0.55/−0.05) · inside_bar_breakup · yang_break_3ma(0.015) · ma_converge_break(0.015) · duck_head(8) · box_breakout(0.08/1.3/20) · immortal_guide(0.015) · n_shape(0.04) | 反转类离场=收回 MA20；延续类离场=跌破 MA10（状态机内建，逐字=代码） |
| folk | low_suction(0.8) · lian_yin_first_yang(3) · false_break_back(3) · ants_climb(0.012) · volume_mound(1.3) · second_wave(0.05) · gap_up_hold(0.01) · rsi_low_flat(14/25) | 各函数内建离场（MA5/MA10/MA20/MA60/RSI50/缺口回补），逐字=代码 |

退出制（2）：default（引擎默认）| CE（注册机契约：桥接 params time_decay 25d/5% + trailing 0.10 + ExitPatch loss_time_days=16，退出优先级零改动）。

## §4 数据与门（记录常数纪律，J19 漂移免疫范式）

- 宇宙=core48 裸码 48 只；**面板截断 evidence_cutoff=2026-09-22**（与门常数校准政体同锚：G2_NSP1/批一/批 2A 一脉；当前 raw end=09-23 → 截断为 ACTIVE no-trivial，如实记）；OOS=2025+ 恒盲；成本 13bp 恒开。
- G1' 六条款逐字 = `p2_calibration.json g1_prime_gate`。
- **default 格 i 线=记录值 0.3521**；**CE 格 i 线=max(本批 CE 随机 p95, 批一记录 0.4474, NSP1 记录 0.4229, 0.3521)**——跑前写死禁换口径。
- **vi 技能线=记录值 0.4004**。
- 随机基线：n=50/退出制（p∈{0.02,0.05}×25，seed 基 **43_000**——NSP1 40k/批一 41k/批2A 42k 后本批独立新抽样）；被动 EW48 双口径=一致性信息列。
- 锚定硬门：3 在册交易员逐位复现（member_run，注册件 evidence_cutoff=09-22 自截断不受本批截断影响）；任一破=批无效。
- 补丁硬门：self_test_patches。
- **民间自检硬门（本批新增）**：26 函数合成政体混合序列（崩窗+涨窗）上二值性+无 NaN+因果性（截断前段逐位一致）全过才许跑——实测已过 26/26（合成零触发族=island/needle/piercing/immortal/drought/big_yin/gap 结构稀疏如实记，真实面板见真章）。
- ×2 成本压力=信息列（G2 才是裁决关）；袖珍标签=信息性（!g1_pass & full>0 & OOS 双正 & ≥30 笔 & max|corr|<0.30）。

## §5 预注册预测（跑前写死，§8 对账）

1. G1' 候选 **0-3 格**（点估 1）：52 格多重检验下记录门仍严（批一 0/16、批 2A 3/16）；先验最强=结构确认类中频族（inside_bar_breakup/duck_head/second_wave/yang_break_3ma）与背离类（macd/obv divergence——批 2A rsrs@ce OOS 0.84 同为择时背离谱系）。
2. **低频形态族条款 iv 风险**：island/needle/piercing/immortal_guide/vol_drought/big_yin/gap_up_hold/morning_star 中 **3-6 族 <30 笔诚实判负于条款 iv**（合成面板触发 0-4 日实证稀疏性）。
3. 反转族全期低于 vi、OOS 或正（批 2A 预测⑤谱系）→ 袖珍候选主产地；engulf 例外（形态确认类）→ needle（带确认构造）小概率复制。
4. 连阳延续族跨域单向门风险（streak −0.976 先例）→ three_soldiers 预期弱。
5. 高频状态族 ×2 深红预测（lian_yin_first_yang/yang_break_3ma/inside_bar_breakup churn 厚，J15 弹性律）。
6. 低吸/蚂蚁/量堆「吸筹类」=新经济意图（非追涨非反转）→ 与在册 3 员相关中等，袖珍可期。
7. 随机 null 带：default p95 ∈[0.28,0.45]、CE ∈[0.39,0.50]（历史 0.3064/0.3521/0.4193 与 0.4074/0.4229/0.4474 邻域）。
8. 批非无效（锚定 3/3 预期全绿：两模块纯新增零引擎改动）。

## §6 判决规则（跑后禁改）

- 幸存者=**G1' 候选，本批不注册**（G2 深化另开预注册：±邻域+×2/×3 成本+逐年）。
- 0 候选=诚实判负收线，动物园 §十二 26 行判负记档；排队池（CCI/威廉/收缩系）不受影响。
- 禁跑后调阈值/禁重跑/禁换口径；袖珍候选若出现 → P3 类并入决策另开预注册（SLEEVE_P3 修正案条款）。

## §7 试验账本（引擎试验记账，研究线 N 连续口径）

prev_total=**2090**（`results/shortline_p4_batch2.json` trials_ledger.total=链头：本 spec 起草时 bm-b R43 恰收口 P-4 批二 B 层 70 跑 0/19 幸存（2020+70），如实衔接）
+ 本批 **209**（52 格×(1×+×2)=104 引擎跑 + 100 随机 + 3 锚定 + 2 被动）= **total 2299**。
账本以本批 JSON `trials_ledger.total` 为真值源（build_status 链接线）。

## §8 跑后对账（跑后填，本节跑前为空）

（待跑批后回填：批有效性硬门、结果全景、§5 预测逐条对账、机制读数、收线。）

—— quant 专管 GM 会话 · 研究部（P-4 民间大扩容批） · 2026-09-23 21:48 预注册
