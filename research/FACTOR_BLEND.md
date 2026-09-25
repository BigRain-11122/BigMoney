# FACTOR_BLEND — 因子混合模型批预注册 v1.0（跑前冻结）

> CEO 直令 O-20260925-0855（组合策略因子混合模型·因子层）· 票 T-2026-09-25-48（P1·immediate，bm-b 认领 commit 79b09c40）。
> 层级链：O-1702 策略混合层（T-27 已交付）→ **本批=因子混合层** → 复合格入三军替补席（军备前置律）。
> 模板=research/PREREG_TEMPLATE.md · 判据权威=research/BACKTEST_SCIENCE.md ＋ BACKTEST_PLAN.md 三铁律。
> **跑前冻结：本文件 commit 先于任何评估跑批；跑后只许回填 §7/§8，禁改判据禁重跑。**

## §0 批件身份【跑前】

- 批名 / 批号：T48-factor-blend（N_eff 计数 135 格：30 引擎格＋15 排名帧格＋90 窗口格，见 §3 账本节）。
- 认领：票 T-2026-09-25-48 claim lock commit 79b09c40（bm-b，2026-09-25 08:52，先推先到）；F-04 MSG=fleet/inbox/MSG-20260925-0900-bm-b-T48-claimed.md。
- 部门归属：dept:研究+交易（票面 owner；bm-b 执行）。
- 算力预算：15 复合格 × x1/x2 双面引擎 sleeve（≤5min 级，>5min 则入 results\runnable_pool.json 后台化，批执行纪律 O-20260924-2100）；workers=min(worker_cap(),8)；分离后台跑＋自写日志（零窗律）。
- 复用面（反重复铁律）：T-27 runner 范式（scripts/t27_blend_tournament.py）／动物园登记簿（results/factor_registry.json，本批交付①）／预注册模板／T-33 军种表（results/corps_roster.json 只读消费，bm-c 车道）／T-22 分段机（scripts/t22_virtual_timepoints.py）。

## §1 α 机制段【D6】

- [x] **行为偏差＋风险溢价（复合面）**：因子面本身承载文献在档溢价——横截面动量（追涨杀跌行为对手方）、低波异象（彩票偏好过度付费方）、短期反转（过度反应修正）。混合不创造 α：复合格的候选收益=面间分散化（横跨面特异风险的重组）＋面内加权规则的制度段稳健性；由行为人群付费，无人为构造套利。诚实边界：若面溢价在本面板不存在，混合只会平均出零（T-27 §1 同款裁定：「IV 只缩风险」）。
- **同族相关性准入检查【D6·硬门】**：15 复合格=新策略函数——每格日收益 sleeve 对**在册 6 员**（COMPOSITE-CE-01/02、DROUGHT/ENGULF/NEEDLE/VOLATILITY）算 `max|corr|`（日收益序列口径，sleeve-tag 先例）；`max|corr| ≥ 0.7` → **该格拒收**（数值与逐对清单全披露）。**同批 15×15 两两 corr 矩阵=描述性披露，不作门**（T-27 §1 先例原文同款裁定：同批候选=同一组冻结面上的权重规则，方法族冗余由 §4 家族 PBO 承担，不由 D6 承担）。
- 结构性风险预告（先验披露非结果）：进攻军格与 COMPOSITE-CE-01（J6 复合旋转=动量面同族在册员）存在高相关结构风险——若 D6 拒收成立即为诚实的「进攻面已在册冗余」结论，禁降门禁改判据。

## §2 数据与面板【跑前事实】

- 宇宙/池：core48 bare-codes（load_core 正典）；因子面=engine/factors.py FACTORS 28 键（登记簿 results/factor_registry.json engine_factor_faces 全映射，零未映射）。
- 窗口与 evidence_cutoff：**2026-09-24**（面板当前完整 bar 日；15:30 今日新 bar 不回流本批）；IS/OOS 分界=**OOS_START 2025-01-01**（仓内正典常数）；mom_12_1 需 240 日预热（面板起点后 ~1 年首信号，诚实披露）。
- 结果 JSON 顶层必须带 `science_gates.cutoff_meta("2026-09-24")`（缺字段=science_audit C2 VIOLATION）。
- 数据完备门（不过门禁跑批，exit 2 诚实中止）：①登记簿在位且 engine_faces=28、roster=28；②短名单键 ⊆ FACTORS 注册键逐键核验；③core48 面板 bar 覆盖至 cutoff（末端缺口 ≤5 交易日）；④15 复合格参数冻结面逐字节由本文件派生（构建器禁外部参数）。

## §3 方法学【冻结】

- **三军短名单【≤12 因子/军·选择证据=登记簿在档经济先验（zoo 谱系/在册员血缘/文献面），非回测排名】**（sign=复合打分中的方向先验；z=逐日横截面 z-score，composite_rotation._xs_zscore 原语，min_n=5）：
  - **进攻军 attack（趋势/动量/突破面，10 员）**：mom_12_1(+)·mom_60(+)·mom_20(+)·mom_accel(+)·ma_slope_20(+)·adx_14(+)·up_day_ratio(+)·price_position(+)·gap_overnight(+)·extreme_freq(−)。先验：横截面动量持续性与趋势强度溢价（zoo §四在役主力族；J6 复合血缘 mom_12_1/price_position；高开确认门变体先验 zoo §四 #25）。
  - **防空军 defense（反转/低波/地量面，10 员）**：rev_5(+)·rev_10(+)·drawdown_60(−)·vol_60(−)·vol_20(−)·intraday_range(−)·return_kurt(−)·return_skew(−)·amt_20(−)·ma_bias_20(−)。先验：短期反转溢价（过度反应修正，zoo §二）＋低波异象（VOLATILITY-CE-01 在册血缘；zoo §五）＋地量见底（DROUGHT-CE-01 民谚已过 G2 门）＋深水锚定池。
  - **震荡军 chop（均值回归/区间面，9 员）**：ma_bias_20(−)·ma_bias_60(−)·price_position(−)·drawdown_60(−)·extreme_freq(−)·intraday_range(+)·volume_trend(−)·vol_price_diverge(+)·gap_overnight(−)。先验：区间回归收割（乖离衰减/区间低位买/high 区间宽度养收割，COMPOSITE-CE-02 chop 归属血缘；zoo §六轮动配置族）。
  - 事后加因子=新版本新预注册（O-0855 §三.1 禁樱桃律原文）；同因子跨军异号=军种先验差异，随格冻结披露。
- **五法权重规则【O-0855 §一·全部 IS 段估计，因果；x2 面沿用 x1 冻结权重】**（blend(t)=Σ w_j·z_j(t)；权重在 rebalance 日更新）：
  - **a. 等权 EW**：w_j=1/K（K=该军短名单员数）。
  - **b. IC 加权**：w_j ∝ IC_IS,j（符号随 IC，负 IC 面自动翻向；IC_IS,j=IS 段逐日横截面 corr(z_j, 次日收益)均值；Σ|w|=1 归一）。
  - **c. 逆波动率**：w_j ∝ 1/σ_IS,j（σ_IS,j=IS 段 z_j 池化标准差；Σ|w|=1）。
  - **d. 因子动量**：rebalance 日 t 权重 w_j ∝ 前 60 交易日（ fwd 窗已收口 ≤t，因果）横截面 corr(z_j, 次日收益)均值——轮动到近期有效因子；全负回退 EW 并披露。
  - **e. 政体条件权重**：state(t−1)=regime_proxy（t22_virtual_timepoints.regime_proxy 冻结原语：510300 close vs MA200）——bear→取 b 法 IS 冻结权重（承压段靠实证有效面），chop/bull→EW；首日缺省=EW 披露。
- **复合格构造（COMPOSITE-CE-01 血缘逐字移植）**：blend 分数 → `top_n_rotation(blend, n=5, rebal_days=20)`（非重叠窗成员资格+持有）；CE 退出机器原样（loss_time 16＋decay 25d/5%＋trail 0.10，max_positions=5，position_size_pct=0.19）——**退出优先级零改动**（铁律）；引擎次日开盘执行、真实 T+1。
- null 对照：**零**（15 固定候选零搜索；skill_line_v2 以 batch_cells=135 计多重试验线——T-27 §3 同款裁定原文）；无新随机族 → SEED_REGISTRY 零登记（g1_prime_v2 内嵌 bootstrap CI 用库正典 ci_seed=20260923）。
- 成本口径：**V1 legacy（13bp×2 压测，x1/x2 双面）**——COMPOSITE-CE-01/02 注册口径血缘复现恒用 V1。
- 账本：`science_gates.append_ledger("T48-factor-blend", 135, "results/factor_blend_cells.json", evidence_cutoff="2026-09-24")`（dict schema 唯一，实际计数只在 finalize 落）。**135 计数构成：引擎格 30（15 格×x1/x2）＋排名帧格 15（3 军×5 法×3 排名面）＋窗口格 90（15 格×IS/IS2/OOS/bear/chop/bull 六窗）**。

## §4 判据【跑前写死，禁看结果调线】

- **主门（逐格，全满足才 eligible）＝G1' v2**：`science_gates.g1_prime_v2(sharpe_full, 日收益, batch_cells=135, n_trades, n_entries)`——line_ok＋平稳 bootstrap CI 下界>0＋entries≥30（F6 双口径）；六条款（EW6 先例 g1_clauses：i>p95 线·ii 年化>0·iii dd≥门·iv 交易数≥门·v IS2 双正·vi>被动）；benefit>0；DR>1；x2 存活（x2 full Sharpe>vi_bar 且 x2 IS2 Sharpe>0）；稳健（IS Sharpe>0 且 worst_year>−0.30）。诚实零过线=合法批读数。
- **三面排名（仅对 eligible 集，逐军）**：benefit（降序）／drawdown=full max_drawdown（降序=更浅）／x2 margin=x2 full Sharpe−vi_bar（降序）；**winner=三面中位秩最优，平手→benefit 面秩**（T-27 §4 逐字范式）。零 eligible→该军无 winner（诚实披露，不降门）。
- **D6 硬门（§1）先于排名**：对在册 6 员 max|corr|≥0.7 的格从候选集剔除（拒收格入 §7 披露，不占 winner 面）。
- **军种替补席入编门（winner 格专属）＝G2 全门＋军种段专项**：G2 v2=`science_gates.g2_registration_v2(g1_pass, DSR, PBO)`（DSR≥0.95 原始收益跑；家族 PBO≤0.25=CSCV 8 块，家族=该军 5 法 sleeve 集，g25_retro 先例）；军种段专项=T-33 §3 冻结口径逐字：目标行情段 beat_rate_12m≥0.50 且 n_startpoints≥30 且 no_blowup（全段全窗 worst_dd≥−0.35）——评估载体=**T-22 harness 机（t22_virtual_timepoints 虚拟起点腿）适配到 winner 格 sleeve**（winner 格以 PROSPECT 候选信号形态接线后跑 6m/12m/24m 虚拟起点窗）；若接线不可行（机制性阻断）→ 诚实回退=全窗 regime_proxy 分段统计+回退披露，禁静默换判据。段证据缺=候选不入席（T-33 candidate 状态语义）。
- **裁决报告**：results/factor_blend_verdict.json（逐军逐法逐门读数＋D6 矩阵＋排名面＋winner 裁定＋军种门读数）；零 winner 全军=合法结论。
- 同预注册同网格禁重跑；成本 ×2/×3 面（×3=G2 pack 层复用既有管线）；零未来数据。

## §5 跑前预测【冻结】

1. **进攻军 D6 拒收风险兑现**：至少 1 个进攻军格对 COMPOSITE-CE-01 的 |corr|≥0.7（同动量面 top5 20d 旋转构造血缘重叠）——若兑现即证明「进攻面已在册冗余」，为诚实科学结论非批失败。
2. **EW ≥ IC 加权（x2 margin 面）**：IS 段（~4.7 年）IC 估计噪声大，b 法权重过拟合 IS 微结构 → x2 成本压测下 a 法余量不劣于 b 法（T-27 D 腿防守先验同向）。
3. **防空军最强段=bear 段 excess**（反转+低波面构造先验；T-33 在册 cohort bear 段 beat 0.53-0.66 实证面承接），但防空军格 OOS（2025 后牛段）full Sharpe 可能被牛段动量机会成本拖低——段面与全期面背离=预期形态。
4. **15 格中 ≥6 格倒在 G1' 主门**（135 格 N_eff 抬线＋面混合稀释单面信号强度；复合格≠单因子格）。
5. **极端日先验（硬界三件套 (c)）**：批窗含 2015-07 救市（510300 涨停 +9.99% vs 指数 +6.40%）、2016-01 熔断、2024-09-24 起爆炸修复行情——top5 20d 旋转格极端日受持仓集中度放大（5×19%=95% 满仓），单日 |r| 可达 ±5-8%：max_drawdown 面将出现危机日主导的深坑，属真实市场极端非数据腐坏（REGIME_GUARD_DEEP_REPLAY D-C 批三方佐证先例）；worst_year 门（−0.30）在含熔断段的格上可能诚实翻红。

## §6 产物

scripts/factor_blend.py（run/status/selftest 子命令，hermetic 夹具）＋ results/factor_blend_cells.json（15 格 sleeve+门读数+audit 段+evidence_cutoff+cutoff_meta）＋ results/factor_blend_runs.jsonl（逐格 checkpoint）＋ results/factor_blend_verdict.json ＋ research/shortline/factor_blend_results.csv ＋ gate_attrition.json 追加行 ＋ 本文件 §7/§8 回填。

## §7 跑后实证【跑前为空——占位纪律：写数字即造假】

批跑 2026-09-25 09:21（bm-b，scripts/factor_blend.py selftest 27/27 → 冻结 commit f5a73cd6 → 引擎 36 跑＝30 格 x1/x2＋6 D6 成员腿；账本 60,880→61,015 恰合冻结 135；evidence_cutoff=2026-09-24；run-time prereg sha256 记录于产物）。

- **eligible 1/15（进攻 0／防空军 1／震荡 0）**：唯一过 G1' 主门＝**defense|b_IC**（IC 加权防空军格）：full S **1.3084**·ann 0.0744·dd −0.1335·IS 1.3502·IS2 1.1415·worst_year −0.0705·x2 full 0.8671（survive，margin +0.4667）·六条款全过·CI 下界>0·entries 过门；ADJ-1 面读数 benefit **1.008**／DR **4.36**（被动基线 0.3004）。
- **G2 不入册（诚实负）**：defense winner DSR **0.4966**<0.95（PBO 0.0 过）→ g2_registration_v2 eligible_v2=**false**——**零注册零入席**；军种段专项=冻结回退面（T-22 接线=PROSPECT onboarding 另立预注册线；候选不入席，T-33 candidate 语义）。
- **D6 拒收 4/15（全对 COMPOSITE-CE-02）**：attack|b_IC 0.7518·attack|e_REGIME 0.7562·chop|b_IC 0.8706·chop|e_REGIME 0.7070——结构冗余结论兑现但**载体错位**：§5 预测 1 猜 CE-01（动量面），实为 CE-02（复合 z-blend 同构面），且只打 IC/政体加权变体（EW 变体 0.32-0.39 全活）——「同构加权规则收敛」是新机理注记。
- **EW 全军覆没（§5 预测 2 反向兑现）**：attack|a_EW 0.075·defense|a_EW −0.366·chop|a_EW −0.164——IS 段 IC 加权在本面板显著优于等权，「IC 估计噪声大」先验不成立（miss 披露）。
- **§5 预测 3 miss**：defense|b_IC 分段=bear 0.4691（最弱）／chop 2.2154／bull 2.2762——反转+低波 blend 的边际不在承压段（T-33 在册 cohort bear 0.53-0.66 面未承接），在平稳段收割；段面与全期面背离形态成立但方向反。
- **§5 预测 4 兑现**：14/15 倒在 G1'（≥6 预测线远超）；**预测 5 部分兑现**：15 格最深 dd −0.6083、worst_year 尾部含 −0.3471/−0.3101（crash 线 −0.30 翻红格存在）。
- 全 15 格 full S 分布：defense|b_IC 1.308 一枝独秀，chop|b_IC 0.665 次之，其余 ≤0.34 或负。
- 15×15 同批描述性 corr 矩阵已披露（产物键 batch_corr_matrix_descriptive，非门）。

## §8 批后复盘【跑后回填·s7-T】

1. **ADJ-1/ADJ-2 跑前裁定生效**：benefit/DR 被动基线与 OOS locked-box 面均按裁定落地（产物 adjudications 键全披露，r71 双读法律族）；事后看裁定中性未偏置任何格。
2. **实现坑（本轮三连修，零判据改动）**：blend_score 须按 W 自列遍历（跨军 z 超集撞列 KeyError）；run_cells_parallel 按散参调用 worker 签名须镜像元组字段；checkpoint 行必须带 "key" 字段（缺键行被 _load_done 静默跳过=成员腿假缺失）；REFINALIZE 账本头须重建正典 dict schema+防偷头守卫。
3. **科学结论**：因子混合层在本面板产出 1 个 G1'-过线候选（防空军 IC 加权），但 DSR 不足→不注册；进攻/震荡两军零过线+D6 同构拒收=「进攻面已在册冗余」以 CE-02 载体兑现。复合格入列三军替补席的唯一路径=新预注册版本（DSR 缺口与段专项为下版必修面），本批按 SS4 语义收线不降门。
