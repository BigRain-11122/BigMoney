# P-S v2：lhb_pair 转正预注册（PS2_SYNTH）· 跑前写死

> 认领：**MSG-20260923-2012（先于本批任何跑数）**·车道：P-S 线第二眼（v1 主合成死于 V1、报告列 pair 最强）。
> **多重性声明（诚实前置）**：本批=该素材家族第二眼，pair 的选择效应由 28 对全枚举 null 校验（见 §3）——非跑到达标为止；跑后禁令照旧（禁调门槛/换口径/重跑）。
> 性质：因子层 IC 批（零引擎跑→引擎账本 N 不动）。

## §1 数据与面板（与 P-S v1 完全同源）

P-1c Stage-A 缓存切片 2007-01-01→cutoff；LHB 事件/去重/滞后 1 交易日=PA_LHB_IC §1 逐字；内部因子=engine 注册表直调（v1 同款）；代码自 pb_synth.py 复制（已交付批件冻结），复现性由 §4 确定性锚保障。

## §2 主配方（写死）

- **primary = lhb_pair_2**：lhb_count_20（定向 −1）+ lhb_amt_share_20（定向 +1）两员定向 z 等权均值，**min_valid=2**，掩码 A（与 v1 次要报告列同配方——本批转正为唯一门控对象）
- v1 六员主合成与 internal_4 不再入批（v1 已判负，不重复计门）

## §3 null 与门禁（写死）

- **nullA（28 对全枚举）**：8 员货架（count_20/days_since/amt_share_20/netbuy_60/vol_60/intraday_range/mom_12_1/price_position，各自冻结定向）两两组合 C(8,2)=28 对，同配方（K=2 等权定向 z、min_valid=2）→ 28 个 IS |IC| 的 **p95**。**枚举优于抽样**（无抽样噪声）；primary 自身在 28 对之内=同偏同秤诚实（P-2 先例条款）
- **nullB（白噪声 K=2）**：50 组 2 员噪声面板（A 掩码，随机号）同配方 → p95 |IS IC|
- 门（P-1a/P-S 原文）：**V1**=|primary IS IC| > max(0.02, nullA_p95, nullB_p95)；**V2**=|IS IC_IR| ≥ 0.30；**V3**=OOS 同号且留存 ≥50%；IS 期数 ≥500；h10 唯一门控期限
- 过门者补 h5/h20 报告列（非门控）

## §4 自检门禁（任一 FAIL=中止/VOID）

1. 等价门禁：探针 −60d 动量@A 快 IC vs composite_ic.ic_series ≤1e-6（v1 同款）
2. 配方锚：合成单调小面板 IC≈+1（1e-9）
3. **确定性锚（VOID 级）**：primary IS IC/IR/OOS IC 须复现 v1 记录（results/shortline/pb_synth.json lhb_pair_2 行：IS 0.0943/0.728、OOS 0.0834/1.02，tol 5e-5）
4. nullA 锚：28 对全部出有限值

## §5 预测（跑前写死，跑后对账；v1 已见 pair 读数=预测的诚实形态=复现+null 位置）

1. 确定性锚通过 95%（同缓存同代码路径）
2. primary 在 28 对中 |IS IC| 排名 **1-3**（75% 信心；最强对候选=count+share 自身、range 类组合）
3. nullA(28) p95 |IS IC| **0.055-0.085**
4. nullB(50, K=2) p95 **0.002-0.010**
5. 主判 PASS 概率 **65%**（pair 若 top1-2/28 则 V1 大余量过；若排名 4-8 则边缘）
6. 若 PASS：h5/h20 报告列预计同向（v1 单因子 h20 加深先例）；若死于 V1：「两条强信号」主张收缩为「货架效应」，LHB 材料保持单因子用法，本线收线

## §6 账本与产物

- 零引擎跑→N 不动；IC 计算数=1 primary+28 nullA+50 nullB（+过门补 2）≈81 记 JSON audit 段
- `scripts/ps2_synth.py` → `research/shortline/ps2_synth_results.csv` + `results/shortline/ps2_synth.json`；§7 跑后一次追加

## §7 跑后实证（2026-09-23 20:35 实跑一次定稿，353s，确定性可复现）

- 硬门全过：等价门禁 PASS + **确定性锚三项 Δ=0.0 全复现**（IS IC 0.0943/IR 0.728、OOS IC 0.0834 对 v1 记录）
- **主判：诚实判负于 V1——primary IS IC 0.0943 < v1_thr 0.0957（nullA 28 对 p95）**；V2 PASS（IR 0.728）、V3 PASS；**primary 排名 3/28**，被 lhb_amt_share_20+intraday_range（**0.111**）与 lhb_netbuy_amt_60+intraday_range（0.0965）反超
- nullB（50 组 K=2 噪声）p95=0.0007；IC 计数 79 记 JSON audit
- **机制定案（收线读数）**：①**强货架内「任意双强员对」即达 ~0.09-0.11 IC**（双 0.064 级成员等权均值的 √2 分散化增益）——选定对无选择边际（3/28）→「两条强信号」主张收缩为「货架效应」，§5 fail 分支精确兑现；②**pair IR 0.728 < lhb_count_20 单兵 |IR| 0.84**——合成增益在 IC 不在 IR，**lhb_count_20 仍为全项目最强单因子证据**；③nullA 带随 K 缩小不降反升（K=6 0.0785→K=2 0.0957）=抽样越集中、强员命中密度越高（与 v1 机制②同源）
- **预测对账**：锚 ✓；排名预测 1-3→实 3（区间下沿）✓；nullA 预测 0.055-0.085→实 0.0957 高于区间（强货架低估第三现）✗；nullB 0.002-0.010→0.0007 略低 ✗；PASS 65%→实 FAIL ✗（方向乐观）
- **P-S 线收线**（按 §5 fail 分支执行）：LHB 材料保持**单因子用法**（count_20 主力 + amt_share/days_since 辅助，B 层 lhb_follow/mood 族以本线因子级证据为输入）；顶部对（amt_share+range 0.111）=**封闭线观察记录，禁直接采信**——任何后续使用须全新预注册+独立多重性记账；跑后禁令照旧

