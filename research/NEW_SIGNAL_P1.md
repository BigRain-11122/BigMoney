# NSP1 新信号设计 · P1 mini 海选（预注册，跑前写死）

> 2026-09-23 12:25 写死于任何回测运行之前。本批=LFC fail_branch 续作二选一之
> (b) 分支执行（上轮指针原文：「品种族续作二选一须另开预注册：货币现金腿
> （引擎特性+池外零相关）vs 新信号设计」）。预注册纪律：跑后不改门、不换口径、
> 不重跑（BACKTEST_PLAN 铁律③）。

## 〇、问题定义

3 在册交易员全部做多 core48 权益池，P3 实证 OOS 相关结构性抬升（全期 0.36→OOS
0.58，C1|C2 0.87），组合真独立风险引擎仅 1.5 个。问题：core48 上（a）P1 36 骨架中
**从未与 CE 软化退出机交叉过**的入场族（迁移探针——J19 只迁移了 composite 两员，
LFC 只在 5 资产弱池上测过 tsmom/donchian），与（b）四个现网格外新设计信号，
能否立起过 G1' 的候选，或与在册 3 员低相关的分散化袖珍。

## 一、二选一裁定（预注册决策，跑前定死）

**选 (b) 新信号设计；(a) 货币现金腿不入本批**：
- (a) exit-to-asset=引擎特性（LFC §一已写死「引擎不支持须另开预注册」）=新引擎
  功能，触碰本回测节点职责边界（禁新功能/新子系统），且与在册锚定链共享引擎
  代码面，风险劣于先挖纯策略层；
- (b) 零引擎改动：入场信号纯 pandas 构造 + 既有 ExitPatch/CostPatch 范式，
  J7 策略工厂 P1 海选直接派生，回测节点全权范围。
- (a) 素材路径留档供未来预注册引用：511880/511990 前缀复制裸码+并入
  update_daily 维护名单（J9a D2 零新数据源路径）。

## 二、策略网格（固定，12 入场 × 2 退出制 = 24 格）

**迁移探针 8**（入场构造与 P1 海选逐字节同构，params={} 引擎默认 sizing
5×10%；J7 坑遵守：±1 状态 (pos>0) 二值化）：
- tsmom_200 / donchian_20_10 / donchian_55_20 / dual_ma_5_20 /
  triple_ma_5_20_60 / double_bottom_20（sym 状态或事件）；
- price_volume_trend_20 / amount_rank_20_10（panel，exit=(w<=0)）。
- 弃选如实记录：month_end_3（default OOS -0.47 负先验，CE 不翻符号）、
  macro 四格（MA 交叉底=432 死族）、parabolic/supertrend/vol_breakout/
  mean_reversion 族（default 全期深度负，CE 增量不足以达技能线）。
  low_vol/composite 不入网格（=3 员在册入场，重复即 dredging）。

**新设计 4**（现网格外，脚本内纯 pandas 实现，零引擎改动）：
- high252_prox_top5_r20：52 周高点接近度（George-Hwang 2004），
  score=close/rolling(252,min_periods=200).max()，top5、20d 非重叠冻结成员
  （low_vol_long rebal_days 同款范式）；
- sharpe_mom_120_top5_r20：风险调整动量 score=120d 收益/120d 日收益 std；
- trend_r2_120_top5_r20：趋势质量 score=R²×sign(slope)（log 价对时间 OLS，
  向量化滚动和实现，R² 有界免尺度病）；
- tsmom_consensus_200_50：时序双确认状态 (close>MA200)&(MA20>MA60)，params={}。
- 前三格 sizing=0.95/5（composite 注册惯例 fully-invested），第四格引擎默认。

退出制（2）：default（引擎默认）| CE（注册机契约：桥接 params time_decay
25d/5% + trailing 0.10 + ExitPatch loss_time_days=16，退出优先级零改动）。
同格附带 ×2 成本压力信息列（CostPatch(2)，**非本批门**）。

## 三、基线与 null（core48 既有账 + 本批补 CE 缺口）

- 随机入场 n=50/退出制（p∈{0.02,0.05}×25 seed，rng=default_rng(40_000+k)，
  CE 制 seed=40_050+k 错开；exit=False panel 纯引擎退出，与 LFC 配方同款）。
- **门常数=记录常数不改一字**（J19 防数据增长门漂移范式，自
  results/p2_calibration.json g1_prime_gate 读入）：
  - default 格 i 线=0.3521（n=100 校准实证值）；
  - CE 格 i 线=max(本批 CE p95, 0.3521)——core48 从无 CE null，本批实测即建账，
    floor=记录常数防 n=50 小样本放松门；
  - vi 线=0.4004（被动 EW48+0.10，与退出制无关）。
- 一致性核对信息列（不动门）：本批 default p95（预期 0.3521±n50 噪声）；
  被动 EW48 buyhold/月度本批复算（J8 公式原样，预期 ≈0.300/0.379）。

## 四、G1' 六条款（J8 §3 常数原样）

i 全期 Sharpe>上述 i 线；ii 年化>0；iii 回撤≥-35%；iv ≥30 笔；v OOS 双正；
vi 全期>0.4004。**本批幸存者=G1' 候选，不注册**——注册须经完整 G2
（±邻域+成本 ×2/×3+逐年，BACKTEST_PLAN §三），留待下轮预注册裁定。
跑后禁看结果选口径。

## 五、Sleeve-tag（信息标签，不注册不算幸存）

!g1_pass 且全期>0 且 OOS 双正 且 ≥30 笔 且与 3 员锚定 equity 日收益
max|相关|<0.30 → 记「袖珍候选」（LFC 教训：core48 多头内相关线结构性难达，
如实记 0）。

## 六、预测（跑前诚实预判，跑后对照）

1. 本批 default 随机 p95 ∈ [0.28, 0.45]（记录值 0.3521 核对带）。
2. **CE 随机 p95 ∈ [0.35, 0.85]**——core48 关键新数据。LFC 金池 1.285 为高漂移
   政体（被动 0.99）极端值；core48 被动仅 0.30 → 预判显著低于 LFC 但可能
   高于 default 线（CE 软化+权益池上行漂移的合成）。
3. CE 增益（default→CE 全期 Sharpe）：+0.25~+0.55（实测谱：low_vol +0.50、
   composite +0.38、tsmom-LFC +0.52、donchian-LFC +0.36）。
4. 主判：G1' 候选 0-2 个（60% 猜 ≤1）。最有机会：triple_ma×CE、tsmom_200×CE、
   donchian_55_20×CE、amount_rank×CE；若 CE p95>0.7 则大概率全灭（i 线抬杀）。
5. 新设计 4 格：三个 rotation 格面临 composite 族同款 churn 病（预测 0-1 格
   过 vi 线）；tsmom_consensus 状态格 OOS 可能正但全期中庸。
6. 袖珍 0-1 个（core48 内相关线结构性拦截）。
7. ×2 信息列：高 churn 迁移格（pvt 1451 笔/double_bottom 1465 笔/
   amount_rank 1012 笔）×2 大概率深负（J14 弹性），如实记录不构成本批门。

## 七、记账与产物

- N += 153（24 格 ×(1x+x2) + 100 随机 + 3 锚定 + 2 被动），872 → 1025。
  随机基线同批同跑（铁律②），一次定稿（铁律③）。
- **硬门（批无效条件）**：patch 自检 FAIL 或 3 员锚定逐位不复现
  （_evidence_matches vs 注册件）→ 批 void，零裁定零回填。
- 产物：research/new_signal_p1_results.csv + results/new_signal_p1.json
  （含 trials_ledger 累计账本）+ 本文件 §九 实证回填。

## 八、禁令重申

禁未来数据（信号收盘算+引擎 T+1 开盘执行；新设计滚动窗只用当日及以前数据）；
成本恒开 13bp（×2 仅信息列）；禁改 engine/exit_rules.py 退出优先级与 T+1/成本
模型；禁跑到达标为止；跑后禁调门槛；本批不注册交易员、不改 strategies/
既有模块（composite_rotation 锚定依赖逐字节不动）。

---

## 九、实证回填（跑后填，本行以下跑前为空）
