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

## §8 跑后对账（2026-09-23 21:54 · 一次定稿 69s/209 跑 · N=2090→2299）

**批有效**：补丁自检 PASS + 民间自检 26/26 PASS（二值/无NaN/因果）+ 锚定 3/3 逐位复现（0.8114/0.6099/1.2578）+ 面板截断 09-22（raw end 09-23 → 截断 ACTIVE）✓；52 格零 signal_error。

### 8.1 结果全景（要点；全表=`p4_folk_results.csv`）

**G1' 候选 6=3 族双制**：

| 格 | full | OOS | 笔数 | ×2 | 判 |
|---|---|---|---|---|---|
| **needle_probe def** | **0.662** | 0.409 | 73 | **0.574** | **G1'√（×2 存活）** |
| **needle_probe CE** | **0.639** | 0.402 | 63 | **0.564** | **G1'√（CE i 线 0.4474 过·×2 存活）** |
| **vol_drought_reversal def** | **0.686** | **1.230** | 145 | **0.525** | **G1'√（×2 存活）** |
| **vol_drought_reversal CE** | **0.724** | **1.213** | 120 | **0.590** | **G1'√** |
| **duck_head def** | **0.682** | 0.823 | 947 | 0.258 | G1'√（×2 弱=G2 先验劣势知情） |
| **duck_head CE** | **0.535** | 0.606 | 798 | 0.210 | G1'√（同上） |

**袖珍 12=6 族双制**（full>0+OOS 双正+≥30 笔+max|corr|<0.30）：three_methods_up（54/49 笔）、doji_at_low、inside_bar_breakup（OOS 1.112/1.375）、ma_converge_break、immortal_guide、ants_climb。
**诚实判负 16 格（8 族双制）**：piercing_line（−0.346 深负）/island_reversal（−0.306）/big_yin_shakeout/macd_divergence（−0.611 深负·873 笔）/obv_divergence/yang_break_3ma（×2 −1.10）/three_soldiers（−0.159·streak 同病）/lian_yin_first_yang（−0.540·2109 笔 churn 深红）/second_wave/volume_mound/gap_up_hold（全期负 OOS 1.09=IS 拖累）/rsi_low_flat/n_shape（全期负 OOS 1.40）/low_suction（0.390/0.435 差 vi/CE 线一线惜败）/morning_star（0.017/0.054 平）/obv 同上/false_break_back（0.149/0.298 弱正未达）。
- 随机 null：default p95=**0.2898**（记录门 0.3521 不动）；CE p95=**0.336** → **CE i 线=0.4474**（批一记录线为最严）。被动复算 0.300/0.379 与 J8 逐位一致。

### 8.2 预测对账（§5 逐条）

| 预测 | 结果 | 判 |
|---|---|---|
| 1. G1' 候选 0-3（点估 1），先验最强结构确认类 | 实 **6 格（3 族全双制）**；点名中 duck ✓、inside=袖珍、背离类全负 | 部分对（**量级低估大错**） |
| 2. 低频形态 3-6 族 <30 笔判负条款 iv | 全部过 iv（最低 island 44 笔）——真实面板触发密度远超合成 | **错** |
| 3. 反转族低于 vi、袖珍主产地 | doji/低位类低于 vi ✓；needle/drought 越 vi（确认构造例外第三次）；袖珍 12 ✓ | 大体对 |
| 4. three_soldiers 弱（streak 同病） | −0.159/−0.118 负 | ✓ |
| 5. 高频族 ×2 深红 | lian_yin ×2 −1.75/yang_break −1.10 ✓；needle/drought（低频低换手）×2 存活 | ✓（换手刻度律复证） |
| 6. 吸筹类袖珍可期 | ants_climb 袖珍 ✓；low_suction 差一线惜败 | 部分对 |
| 7. null 带 [0.28,0.45]/[0.39,0.50] | 0.2898/0.336 | ✓ 双落带内 |
| 8. 批非无效 | 锚定 3/3+全自检过 | ✓ |

### 8.3 机制读数（四条定案）

1. **确认构造=反转族分水岭（第三次实证）**：engulf（实体吞没，批 2A）→ needle（次日收复针高点）→ vol_drought（地量+首阳）——无确认同族全弱（hammer 袖珍/doji 弱/piercing 深负）；「形态确认类>形态+语境类>指标超卖类」谱系固化入动物园法。
2. **民间谚语首证两条过门**：「地量出地价」vol_drought（0.686/0.724·×2 0.525/0.590 全绿=本批最厚）、「老鸭头」duck_head（过 G1'，×2 0.258/0.210=churn 厚先验劣势）；反向如实降级：MACD 背离（−0.611）、「低吸富三代」（0.39 差 vi 一线）在 core48 不立。
3. **低频≠低证据**：needle 73/63、drought 145/120、三法 54/49 笔全过 30 笔条款——事件形态族在 48 池×6.7 年样本充分（预测 2 反证=合成触发密度不可外推真实面板）。
4. **袖珍池大扩容**：+12 格（6 族）→ 全项目袖珍池累计 21 格（NSP1 6+批 2A 3+本批 12），P3 类并入决策预注册时机成熟（SLEEVE_P3 修正案条款照走：成员 ×2 存活+全期>0 才可并）。

### 8.4 收线

民间大扩容批收账：**G1' 候选 6（3 族双制：needle_probe·vol_drought·duck_head）+袖珍 12（6 族）+8 族诚实判负**。**0 注册**（§6：G2 深化另开预注册——3 候选 ±邻域+×2/×3+逐年；needle/vol_drought ×2 已存活=历史上第 2/3 个过 ×2 线的入场族，G2 通过先验显著优于历史候选）；袖珍 P3 类预注册=开放池。禁本批回头调参/换口径/重跑。

—— 2026-09-23 21:54 跑后一次定稿
