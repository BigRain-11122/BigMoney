# CTA_P2_NOAU — 期货 CTA 剔 AU 复评批（机制分解）预注册

> 按 research/PREREG_TEMPLATE.md 起草；判据权威=BACKTEST_SCIENCE.md v2；三铁律照旧。
> 跑前 commit 冻结（R52 bm-a·F-04 认领 MSG-20260924-0720·commit 9d16b7a 即锁）；跑后只许回填 §7/§8，禁改判据禁重跑。

## §0 批件身份【跑前冻结】

- 批名：CTA_P2_NOAU（R50 CTA_P1 收线的续作指针「剔 AU 复评」——机制分解批，非注册猎取）
- 批内格数（N_eff 计账）：**68** ＝ 16 候选（8 冻结信号族 × {daily, r20}）＋ 50 随机 null ＋ 2 被动；×2 成本信息列不计数（CTA_P1 先例）
- 部门归属：dept:研究（C 层期货=O-1620 GM 已签 paper 域过闸制）
- 算力预算：全批 ≈35-70s 单进程（CTA_P1 同构 68 跑 64.6s 实测先例），轮内直跑；批报告带 audit 段（compute_audit 批内跑，无 audit 段不入账本）

## §1 α 机制段【D6】

- [x] **行为偏差**：趋势延续（锚定不足/处置效应）＋保证金强平放大——CN 期货散户主导品种对新信息反应不足、趋势形成后追认迟滞，谁付出代价=接飞刀/扛回调的锚定持仓者。**本批主假设不是「α 存在」而是其反面**：R50 已实锤最优族 vol_target_tsmom_60@daily 的 PnL 被 AU 黄金牛市单腿 +121.5M 支配（RB −47.6M/IF −21.2M/T −17.1M 全负）——本批剔 AU 后复评，检验「趋势 α 是否只是黄金 β」。剔除 AU 后若候选普遍塌陷 ⇒ α=AU β 定案；若仍立 ⇒ 多品种趋势 α 存在。
- **D6 同族相关性准入**：无新策略函数（8 族与 CTA_P1 逐字节同参复用）→ 新函数准入检查不适用；批内 16 格 pairwise corr 全披露（CTA_P1 先例）；在册（core48 ETF 6 员）corr 仅对 passer 计算（跨资产类，先验低相关）。

## §2 数据与面板【跑前探针事实】

- 宇宙：**8 品种主力连续**（IF/IC/IH/IM/T/TF/RB/SC）＝ R48 全量拉取 9 品种剔 AU（fr.load_panel varieties 参数过滤，AU.csv 在盘不删不碰）
- 窗口：2017-01-17 → **evidence_cutoff 2026-09-23**（与 CTA_P1 同窗同 cutoff；结果 JSON 顶层 `science_gates.cutoff_meta` 必带）
- 数据完备门（不过门禁跑批）：8 品种 CSV 在盘、末日 bar = cutoff、OHLCV 无负值、span 内 NaN 孔 ⊆ {2017-10-09, 2019-04-22}（R50 G3 修订豁免日原文）；engine 自检 G1 + null 确定性 G4 均须 PASS
- roll-gap V0 直用裁定沿用（CTA_P1 SS2）：原始连续价不平滑，候选/null/被动同面板对称注入=相对判据内部有效

## §3 方法学【冻结】

- 信号：8 族逐字节复用 cta_p1_screen.FAMILIES（tsmom_120/60/252、donchian_55_20、dual_ma_10_60、triple_ma_5_20_60、breakout_20、vol_target_tsmom_60）；评估双制式 {daily, r20(每 20 日再平衡)} 同 CTA_P1
- null 对照：K=50 同构随机 null（每 20 日每品种等概率 {−1,0,+1}/n_alive；**新 seed 基 50_500**，登记 science_gates.SEED_REGISTRY["cta_p2_noau"] 后才跑）＋ 2 被动（r20/月度等权长）
- 成本口径：V1 legacy 期货域口径（per-lot 费＋1 tick 滑点/边，FUT_META 冻结常数，G2 验证门同 CTA_P1）；×2 信息列照跑（律 8=期货成本近免费，×2 预期无损）
- 账本：`science_gates.append_ledger("cta_p2_noau", 68, "results/shortline_cta_p2_noau.json", evidence_cutoff="2026-09-23")`（dict schema 单源，禁手抄 prev）

## §4 判据【跑前写死】

- **G1' v2** ＝ `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=68, pool="cta_futures_noau", n_trades, n_entries)`：全期 Sharpe > skill_line_v2（新池分支 cta_futures_noau＝本批自身被动 strict-max＋0.10 vs 本批 null μ+σ√(2·ln N_eff) 取大）且 bootstrap CI 下界>0 且 entries≥30
- **G2 注册资格 v2** ＝ `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`（DSR 原始收益跑；PBO≤0.25 CSCV）；无 passer 则 G2 不触发
- 描述性条款批级披露照旧（年化>0/IS2 双正/dd≥−35%/无崩年）；**注意**：满保证金 dd 域特性条款在 CTA_P1 已实证（−0.66~−0.96 全灭），本批同口径如实披露不豁免
- 跑后禁调门槛禁重跑；工程修复重跑须双跑留痕；确定性引擎产物写 bug 的合法重执行口径≠结果重跑

## §5 跑前预测【写死于跑前】

1. **被动塌陷**：AU 多头是 9 品种被动 0.9337 的主要引擎 → 8 品种被动预测 r20/月度落在 **0.35-0.75**（被动项=+0.10 → 0.45-0.85）
2. **null 带近似不变**：8 品种随机 null μ 预测 −0.05~+0.05、σ 0.25-0.35（少一个品种分散化略降），null_term（N_eff≈3041）预测 0.75-1.05；判线=max(被动+0.10, null_term) 预测 **0.75-1.05**
3. **最优族塌陷方向**：vol_target_tsmom_60@daily 剔 AU 后预测 full Sharpe **0.15-0.45**（AU 腿贡献被剥离，RB/IF/T 负贡献原样保留）；族序大体保持（vol_target_tsmom 仍最优、daily>r20 律 8 延续）
4. **passer 预测 0-1**：若剔 AU 后仍有过线者 ⇒ 多品种趋势 α 主张升级；若 0 过线且最优者仍超随机带（null p95 预测 0.40-0.55）⇒ 「趋势 α=AU β＋薄多品种边缘」定案
5. ×2 信息列预测全候选几乎无损（|Δ|<0.03，律 8）

## §6 产物

- scripts/cta_p2_noau.py（复用 cta_p1_screen 构建器，零重写；gates/run/selftest）
- results/shortline_cta_p2_noau.json（顶层 evidence_cutoff＋audit 段＋prereg 双 sha）＋ research/cta_p2_noau_results.csv
- science_gates.py 加性扩池：passive_baseline 分支 `cta_futures_noau`＋SEED_REGISTRY 登记
- results/gate_attrition.json 追加一行；STRATEGY_LIBRARY C 层行回写

## §7 跑后实证【跑前为空——跑后回填 R53 bm-a】

- **G1' v2 过线 0/16（诚实判负），G2 未触发，零注册**；五门 G0-G4 全 PASS；批 61.2s；账本 2973→3041（+68，prev/total/evidence_cutoff 全核验）；audit CLEAN 零旗；prereg frozen sha==at-run sha（零修订）。
- 判线=**1.4278**（null_term 主导：μ−0.0104/σ0.3591/n_eff 3041；被动项 0.8594=strict-max 0.7594+0.10）；最优=tsmom_60@daily **0.669**、vol_target_tsmom_60@daily 0.643（原 0.7408）——**均超 null p95 0.4858 但差线 0.76+**。
- **AU 贡献剥离实测**：vol_target AU 腿=+160.18M（tsmom_60 腿=+121.51M 与 R50 记录一致）；剔 AU 后 vol_target 0.7408→0.643（−0.098）、tsmom_60 0.7158→0.669（−0.047）=**族未塌陷**，预测 3「塌陷至 0.15-0.45」判错。
- **品种归因路径依赖实证（重要）**：剔 AU 后多腿 PnL 翻号/大幅移动——IF −21.2M→+3.86M、TF −4.3M→+9.13M、RB −47.6M→−19.7M（tsmom_60 的 IM +6.75M vs −9.51M 翻号）——**per-variety 归因不是结构常量，是账本组合路径的函数**（AU +160M 不再复利全账本+保证金份额 1/8 vs 1/9+权益路径变化）；跨批比较品种归因须带此警示。
- **判线变高机制（律 9 候选）**：8 品种 null σ0.3591 > 9 品种 0.2901——**宇宙越窄随机账本越不分散→null 带越宽→v2 判线越高**（1.1463→1.4278）；「截面宽度是可行性主变量」在组合域的反向形态（P-1c 单因子版：宽截面压低因子 null 线；本版：窄宇宙抬升组合判线）。
- 描述性条款全灭 0/16（满保证金 dd 域特性延续 CTA_P1 全灭口径）；×2 信息列：正 Sharpe 族 |Δ|0.07-0.10（预测 <0.03 判错，律 8 方向成立但幅度 2-3×预测）；**breakout_20@daily ×2 −0.0725→−0.6841（|Δ|0.61）=律 8 高换手×负边缘格的显著例外**如实记。
- 批内 pairwise corr max|·|∈[0.439, 0.932]（16 格全披露在 JSON）；family PBO：六族 0.0/vol_target 0.0857/breakout 0.9143（2-cell CSCV 信息列，与 CTA_P1 同判）。

## §8 批后复盘【s7-T】

- **预测对账（§5 五条）**：①被动塌陷方向 ✓（0.9337→0.7594=−0.17）但落带上沿外 0.7594>0.75（近失）；②null 带半错（μ✓ 内、σ0.3591>带顶 0.35、null_term 1.4278>>带 0.75-1.05 大错——√(2·lnN) 在 N_eff 3041 的放大+σ 带顶双因素）；③**最优族塌陷——大错**（预测 0.15-0.45，实 0.643-0.669，多品种趋势边缘真实且非薄）；④passer 0 ✓+最优超随机带 ✓→「趋势 α=AU β＋多品种边缘」定案成立，但**「薄」字修正为「厚边缘但判线结构性不可及」**（边缘超随机带 p95 但差 v2 线 0.76，差距主因=null term 而非 α 无效）；⑤×2 近无损——错（正族 |Δ|2-3×预测+breakout 例外 0.61）。
- **损耗账**：16 候选→G1' v2 0 过线（skill_line 1.4278 为域内最高线）→淘汰 16/16；账本 N=3041。
- **判线当批读数**：line=1.4278=全项目新高（超 CTA_P1 1.1463）——**C 层期货线在窄宇宙下更严**，复活评估（R51 指针 LOW 优先级）在此基础上进一步降级：任何 8 品种趋势注册需 full Sharpe≥1.43，当前最强证据 0.669=结构性远不可及；除非新品种扩容（=P1 署名门）或降杠杆变体显著改 Sharpe 口径，否则 C 层保持收线。
- 回执：R53 bm-a 轮报告+CODELY.md 行级追加；STRATEGY_LIBRARY C 层行回写。

