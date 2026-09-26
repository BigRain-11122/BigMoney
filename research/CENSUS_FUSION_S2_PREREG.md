# CENSUS_FUSION_S2_PREREG — T-86 s2 因子级融合组合普查（wave-1 core48 面）

> 权威链：research/BACKTEST_SCIENCE.md + BACKTEST_PLAN.md 三铁律 + COMPUTE_AUDIT.md 批件纪律 + research/FACTOR_CENSUS_REGISTRY.md（单源母面·零发明律）。
> **批性声明（票 spec 原文锚）**: CENSUS = EXPLORATION FACE——zero judgment claims / zero paper eligibility / all outputs labeled exploration；本批不产生任何注册/纸盘资格，唯一出口=§4 冻结的排序与家族聚合规则产出「top candidate fusion-factor families list」喂 T-23 intake funnel（judged 消费面自带独立 prereg+判据门）。
> 反重复：P-1/P-2 单因子线已闭（r271 verified）不入本批；本批=COMBINATORIAL FUSION 面；FACTOR_BLEND_V2 归档头注尊重（新血统非重开）。

## §0 批件身份【跑前】

- 批名/批号: **CENSUS_FUS_S2_W1**（wave-1；wave-2 见 §2.2）；批内格数（计入 N_eff）= 候选组合 4,060 + 对照 pair 58 + null 400 = **N=4,518**（每组合一格，扩容即买单）
- 认领: F-04 先行——fleet/inbox/MSG-20260927-0230-bm-a.json（本轮已发）；票据引用 T-2026-09-26-86-P1 s2（CEO 直令 O-20260926-2320 因子级融合普查）
- 部门归属: dept:研究（因子普查·供给面）
- 算力预算: 预估 20-40min（4,518 格 × 双统计面 · workers_plan 4 × BelowNormal · 每 200 组合一 checkpoint 跨轮续跑）；批报告必带 audit 段（无 audit 段结果件不入账本）

## §1 α 机制段【四选一+论证】

- [x] **行为偏差**（主）+ 风险溢价（辅）：注意力稀缺/锚定——低关注度、低振幅、被趋势确认滞后面承载的条件溢价由追涨杀跌的注意力梯度付出代价；组合面的机制主张=两个正交行为面同向对齐时条件溢价放大（quick-strike 探索先验：lowamp×trend 族 +8.1pp vs EW19，perm p=0.035 EXPLORATORY·票 spec 原文锚）
- 逐面经济先验=scripts/factor_registry.py ENGINE_FACES sign priors（文档化经济先验，非回测拟合）；G 行 lowamp20 prior −（低振幅=稳定溢价）
- **D6 同族相关性准入【探索面适配声明】**: 本批无 judged 注册主张→D6 拒收门（≥0.7）不作为批准入门；本批自身的产出之一=因子对相关性结构（pair rank-IC/条件收益矩阵）=未来 judged 消费面的 D6 证据底座；wave-1 全部 4,060 候选格全量序列化落盘（top-M 仅决定「详细矩阵序列化面」，非入选面）——零选择性披露。

## §2 数据与面板【跑前探针事实】

- 宇宙: **core48**=data/daily 裸码 CSV 48 员（loader 语义=research/shortline/screening/p1_factor_screen.py load_core48：裸码+≥60 行）；2026-09-27 02:2x 实测=48/48 员、全员末日 2026-09-24（中秋 09-25 休市=面板完备）
- **evidence_cutoff = 2026-09-24**（前向锁盒 D2）：面板一律截断到 cutoff，cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta(2026-09-24)`（缺字段=C2 VIOLATION）
- 数据完备门（fail-closed，不过门禁跑）: ①裸码成员数==48 ②每员≥60 行 ③每员末行日期==2026-09-24 ④OHLCV+amount 列齐 ⑤volume>0 掩码（vwap=amount/volume）
- **§2.2 wave-2（wide universe·规则冻结·跑前另行追加冻结）**: 门=T-87 A 股日线面板 complete（bm-b 采集器·ETA 周一 09:15 前）+ B-layer mask 再生；原子面=B4+D8+E2+C 三族各 top-10（按 P-1/P-2 在档筛查产物 IC IR 排序·工件锚）≈44 面；精确 roster+组合数于 research/FACTOR_CENSUS_REGISTRY.md §wave-2 规则下在 **wave-2 追加节（本文件 §9，append-only）** 冻结后跑——R99 每 wave 一冻，禁用 wave-1 冻结面跑 wave-2。

## §3 方法学【冻结】

- 因子定义: A 行 28 面=engine/factors.py `FACTORS` 逐员 OHLCV 计算（源码锚·frozen）；G 行 lowamp20=20 日 mean((high−low)/close)（登记簿 G 行锚）；截面 z-score 逐日。
- 滞后规则: 因子用 ≤t 日收盘数据；IC 面=close→close 前向 5 日收益（`close.shift(-5)/close−1`·与 P-1/P-2 记录线同估计算子 ic_series）；blend 面=信号日 t 次日（t+1）收盘入场保守 T+1 代理、持有 5 交易日、双腿换手成本。
- 组合枚举: 候选 29 面→pairs C(29,2)=406 + triples C(29,3)=3,654=**4,060**；对照 58（每候选面×每 bench rs 面 pair）；组合分数=Σ z(f_i)·s_i（s_i=ENGINE_FACES sign prior·G 行 prior −）。
- 统计面（每组合冻结）: ①rank-IC 全窗 mean/ICIR+逐日历年 IC 表 ②dual-sort 条件收益（pairs：z(f1)×z(f2) 独立三分位 3×3 前向 5 日均值矩阵；triples：组合分三分位 1×3）——全量计算，|全窗 IC| top-50 序列化详细矩阵 ③含成本多头腿 blend：周频（5 交易日）再平衡、多头腿=组合分 top 三分位（16/48 员）等权，成本 **V2**（knowledge/rules.py cost_v2_slippage/cost_v2_side_rate·ADV20 三层 2/5/10bp+1%ADV 帽）+ **×2 压测列**（票 spec 原文「with x2 cost」）；指标=年化/波动/Sharpe/maxDD/月度胜率 vs EW48 基准。
- null 对照: **K=400** 同结构 null（200 随机 pair+200 随机 triple：随机抽面+随机 ± 号指派，同一 blend/成本机器）；seed 基=**census_fusion_s2=20274500**（band 20274500..20274900·SEED_REGISTRY 本冻结 commit 同步登记·R250 一步律）；RANDOM_LARGE_SAMPLE_LAW v1.0 照绑（null 同掩码同机器同成本面）。
- **s3 不确定面（同 prereg 管辖·独立池批）**: 每候选组合 block bootstrap B=200（block=20 交易日）x2 blend Sharpe CI + sign-flip 置换 P=200 IC p 值；同组合=同格 derivation 面→**ledger +0**（NAV 推导面先例）；跑全量候选（票 spec「per combo」），非 top-M。
- 成本口径: **V2 主口径 + ×2 压测列**（新批建议 V2；×2=票 spec 点名面）。
- 账本: `science_gates.append_ledger("CENSUS_FUS_S2_W1", 4518, "census_fusion_s2/w1_results.json", evidence_cutoff="2026-09-24")`（dict schema 唯一禁手抄 prev）。

## §4 判据【探索面协议·跑前写死】

- **G1'v2/G2 注册门不适用**（EXPLORATION FACE·票 spec 原文）——本批禁产生任何注册/纸盘资格宣称；任何组合的「过线」读数在批产物中一律标 exploration。
- 输出排序规则（防事后摘樱桃·跑前冻结）: 主排序键=×2 成本面全窗 blend Sharpe；全量 4,060 候选格+全部统计列序列化 CSV（零选择性披露）；top-50 by |mean IC| 序列化 dual-sort 矩阵（其余矩阵计算但不序列化=体积面非选择面）。
- §4 出口（s4 家族清单）冻结规则: 按 ENGINE_FACES 七分类（momentum/trend/breakout/reversal/low_vol/volume/mean_reversion）逐族聚合=该族成分参与的候选格 ×2 Sharpe 中位数+覆盖数；跨族 top-10 组合另列；产出=「top candidate fusion-factor families list」喂 T-23 intake funnel（judged 消费面独立 prereg+判据，本清单零注册效力）。
- 硬界设计三件套适配声明: 本批=探索披露面无健康判线；条件矩阵/blend 的极端日尾部=披露面非门（见 §5 极端日先验）；分布面（median/p99）承担序列化描述主责，禁裸 max 单列叙事。

## §5 跑前预测【≥3 条·写死于跑前·跑后对账】

1. **lead 连续性**: lowamp×trend 族组合（lowamp20/vol_20/intraday_range × mom_*/ma_*/adx_14）预期落入 ×2 Sharpe top 十分位且年化>EW48（quick-strike 先验 +8.1pp·方向面）。
2. **null 分布**: 随机组合 blend Sharpe 中位数≈EW48 穿越≈0 附近、离散小；候选面 p95 预期高于 null p95（否则配对面无结构=普查定谳「无融合溢价」照报不翻案）。
3. **反转×动量符号互作**: rev_5/rev_10 与 mom 族 pair 的 IC 呈负向互作，dual-sort 矩阵非对角格不对称（行为面先验）。
4. **极端日先验（硬界三件套 (c)）**: 2015-07 救市（宽基单日 ±9~10%）、2016-01 熔断、2024-02 微盘崩、2024-09-24/30 政策脉冲（宽基单日 +10~20% 极端日）——条件矩阵与 blend 序列在这些窗的尾部 |日收益|>8% 属预期披露面非腐坏；本批无 max 硬门=尾部照登不判红。

## §6 产物

- runner: scripts/census_fusion_s2.py（subcommands: run/selftest；workers_plan 4 BelowNormal；每 200 组合 checkpoint；hermetic selftest 含非原生类型注入腿 r286 律+面板缺员 fail-closed 腿）
- 产物: results/census_fusion_s2/w1_results.json（顶层 evidence_cutoff+audit 段）+ w1_nulls.json + w1_summary.json（§4 家族聚合）+ w1_cells.csv（全量格）+ w1_top_matrices.json；s3 面另批=results/census_fusion_s2/w1_unc.json（池第二入口）
- 池入口: CENSUS-FUS-S2-W1（s2 面）→ 完成后 CENSUS-FUS-S2-W1-UNC（s3 面·依赖 s2 产物=物理依赖票内留痕合法排序）

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（一次定稿；工程修复重跑双跑留痕；确定性引擎产物写 bug 的合法重执行≠结果重跑）

**R290 bm-a 一次定稿（跑落地 2026-09-27 03:00:11·autofill launch-claim 1150732c→checkpoint 续跑→末段 elapsed 2.1s）**：

- N=4,518 全格入账（候选 4,060+对照 58+null 400）；trials ledger 200,900+4,518=**205,418**；数据门 48/48 员·末行 2026-09-24 唯一·全 gate ok；网格首信号 2020-12-29·279 信号·top_k 16·面板 1,633 交易日。
- EW48 锚（行内 delta 列反推·全行一致）：x1 年化 **0.0266**·×2 Sharpe **0.1532**。
- 候选面 ×2 Sharpe：median 0.0583·p95 0.4164·max **0.7249**（T:extreme_freq|return_skew|lowamp20·×1 Sharpe 0.7581·IC 0.0294）。
- null 面（400·seed band 20274500..20274899）：median **0.0388**·p95 0.3526·min −0.4662·max 0.5653；候选超 null p95=**363/4,060（8.9% vs 基率 5%）**。
- §4 家族聚合（×2 Sharpe 中位数·n_combos）：low_vol 0.1399（2,036）> trend 0.1040（1,135）> volume 0.0561（1,760）> momentum 0.0427（2,520）> breakout 0.0164（784）> mean_reversion 0.0126（784）> reversal **−0.0096**（1,135）；跨族 top-10 前三=T:extreme_freq|return_skew|lowamp20 0.7249／T:mom_20|vol_20|vol_60 0.7023／P:up_day_ratio|vol_60 0.6987。
- **批性声明照锚：EXPLORATION FACE——零注册主张零纸盘资格；唯一出口=§4 家族清单喂 T-23 intake funnel（judged 消费面独立 prereg）。**

## §8 批后复盘【必填·s7-T】

（预测对账+门禁链损耗账 results/gate_attrition.json 追加一行+回执入轮报告；本批无判线读数=探索面注记 null）

**R290 bm-a 对账（§5 四预测 vs 实测）**：

1. **P1 lowamp×trend top 十分位+年化>EW48：CONFIRMED**——306 组中 74 组（**24.2% vs 基率 10%=2.4× 富集**）落 ×2 top 十分位且**全部 74 组同时 x1 年化>EW48 0.0266**（联合=单条件）；top 组合携带 lowamp 面（T:mom_20|vol_20|vol_60 0.7023·T:extreme_freq|ma_slope_20|lowamp20 0.6857）。
2. **P2 null 近零小离散+候选 p95>null p95：CONFIRMED**——null median 0.0388（近零区·低于 EW48 0.1532）；null p95 0.3526 < 候选 p95 0.4164；超 null p95 者 363/4,060=8.9%（基率 5%）=**结构存在但温和**（探索先验不作注册证据）。
3. **P3 rev×mom IC 负向互作：NOT-CONFIRMED**——208 rev×trend pair IC median **+0.0103**·负向占比 30%（无系统性负互作）；矩阵面 top-50 |IC| 序列化中含 rev 面仅 1 件——core48 面行为先验不成立，如实照登不翻案。
4. **P4 极端日尾部披露面：满足**——全量 CSV 序列化（含 maxDD/月度胜率列）·本批无 max 硬门（§5.4 设计面）·尾部照登未判红。
- **判线读数：无（EXPLORATION FACE）→ 注记 null**；G1'v2/G2/D6 全不适用（§4 探索面协议）。
- 损耗账：results/gate_attrition.json 追加 CENSUS_FUS_S2_W1 行（kind=measurement·探索面零 judged 格·cells_ledger_delta 4,518·ledger_total_after 205,418）。
- 回执：bm-a R290 轮报告；post_review 行 T-86-S2-CENSUS-FUS-W1 注册（锚稳定产物件·R264 律）。

## §9 追加冻结节【append-only·跑前另行冻结面】

### §9.1 s3 不确定面（UNC）种子冻结【R290 bm-a·跑前·先于 runner build commit】

- 家族基：**`census_fusion_s2_unc = 20275000`**（science_gates.SEED_REGISTRY 本冻结 commit 同步登记·R250 一步律；全表无撞·20274500 null 带不重叠）。
- 派生律：每候选组合 i（i=组合枚举序 0..4,059）确定性流 = `np.random.default_rng([20275000, i])`（PCG64 seed-sequence 双整数派生·零 band 占用·重跑字节恒等）。
- 用途钉死：rng 流仅供 §3 s3 已冻规则的两个重采样面——①block bootstrap B=200（block=20 交易日·循环块·拼样截回 n 长度）×2 blend Sharpe 分布 → CI=[p2.5, p97.5]（观测 Sharpe 落带披露·ci_pos=ci_lo>0 旗）；②sign-flip 置换 P=200（逐日 IC 符号独立翻转·双侧）→ p=(1+Σ|μ_p|≥|μ|)/(P+1)。禁挪用他面。
- 语义锚：同组合=同格 derivation 面→ledger +0（§3 原文）；跑全量候选 4,060（pairs+triples·对照/null 不入）；产物=results/census_fusion_s2/w1_unc.json+unc_checkpoint.jsonl（200 组合 cadence）。
