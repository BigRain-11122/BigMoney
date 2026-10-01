# PERPETUAL-N3-R1 预注册 · N3 neighborhood robustness grid 波 1（T-2026-09-30-133 s2 波级冻结件）

> 令源：CEO 直令 O-2026-09-30-2340（机队满负荷·常供面）→ 面级法典=research/PERPETUAL_FACES.md v1.0（bm-b r484 面级冻结·起草序 N1-W2→**N3-R1**→N2-W15→N4-B1）；本件=N3 面**波级 prereg**（R99 纪律）。种子带=法典 §4 未预占 N3（N3 非预指派面）→ 本波**先行 SEED_REGISTRY 登记** `perpetual_n3_r1=70_000`（2026-10-01 09:2x r509 bm-a 登记+registry/rg 双扫 500 宽净域实证；R250 one-step 律=冻结后禁再挑）。
> 性质=**测量加深面**（法典 §2：N3 对在册成员冻结参数做邻域应力网格重测，产物=更深 G2 置信面〔neighborhood/cost_x3/per_year/bootstrap CI/当期线复测〕**非新注册件**，不入候选漏斗，不占语法消耗登记簿行；本波零除名效应——读出面=应力披露，任何在册成员的去留归月界注册管线，本波判读**不触发**成员状态变化；D6 同族相关性与闭合族对号约束=N2 专属，本面豁免如实注记）。
> 复用基=verbatim import 禁重写：`scripts/t24_g2_pack.py`（PROS 面 G2 pack 既有机器：member_run 引擎约定/中心锚门/JSONL checkpoint/OAT 判读/arithmetic）推广到注册面；`live/paper.py` SIGNAL_BUILDERS + ExitPatch + dd_control（**注册面正典 run 约定**=paper_run 引擎调用逐字：params 去 entry 全传＋exit_overrides patch＋dd_control 透传）；`science_gates`（recorded_lines/bootstrap_ci_sharpe/deflated_sharpe_ratio/g2_registration_v2/skill_line_v2/append_ledger——判线机器链接零手抄）。

## §0 批件身份【必填·跑前】

- 批名=**PERPETUAL-N3-R1**。宇宙=**在册 6 员**（firm/traders/ 非 PROS 全体：COMPOSITE-CE-01/02、DROUGHT-CE-01、ENGULF-CE-01、NEEDLE-DE-01、VOLATILITY-CE-01；evidence_cutoff=2026-09-22 逐员断言）。
- 引擎格=**34 引擎胞**＝6 中心（1x）＋6 成本 ×3 ＋22 邻域 OAT 胞；**账本 +28**（新证据胞=22 邻域+6 x3 全部；复演胞 +0=6 中心〔在册证据 recorded-cell replay=锚门逐位复现实证，t24 先例〕）。x3 全数判新证的分类依据（冻结前实证）：①NEEDLE x3 录值 0.4833=G2_FOLK 批纪构造（p4 73 笔构造）≠注册面构造（68 笔）——冻结前 write-path 冒烟烧录实测 0.3729≠录值=复演否定实证；②VOLATILITY/DROUGHT x3 录值 provenance 未逐位验证——未验证复演一律从新证（保守侧：账本 N 抬升=DSR 更严，永不低计）；③COMPOSITE-01/02/ENGULF x3=「re-derived 2026-09-26 with T-78 overlay」=当前冻结参数面与录值异构→新证。
- **冻结前冒烟披露**（如实留痕·判据零改动）：NEEDLE-DE-01 单分片 6 胞已于冻结前烧录（r497/r506 真跑律=新 runner 落地必真跑 write-path 一次；产物=probe-class 证据，判据/线/容差全部冻结前设计且未被冒烟结果改动）；账本分类修正=provenance 实证非结果驱动（r251/r280 零跑修正案先例同源：如实留痕）。其余 5 员=冻结后池烧。
- 认领：T-2026-09-30-133 s2（bm-a r494 起源票·faces lane 任意健康机合法）；部门=dept:研究。
- 算力预算=**长活入池**（O-20260924-2100·禁轮内内联代跑）：6 分片（每片=1 员全胞 center+x3+nbhd；池条目=逐片一 entry）× workers_plan={"workers": 1, "priority": "BelowNormal", "note": "per-cell engine run ~5-10s, member shard ~40-80s = light batch; single-core per shard honest (light 批不套多核壳)"}；checkpoint=逐员 JSONL 胞件（presence=done 证据；确定性重跑字节恒等=断点续跑语义）；跑批宿主门=core48 in-repo 数据（worker_class=self-contained·lane_owner=ANY·R31/R65 合法）。
- 物化条款（法典冻结签名行「runner 落地一批物化一批」）：本波=生成器 supply 物化（法典 §1 三腿触发：池饿 ∧ py<70% ∧ 无同面在飞波）；per-wave prereg 在场=物化前置条件（缺失=诚实拒绝物化）。

## §0.5 禁开方向硬闸【必填·跑前】

- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N3_R1_PREREG.md` → exit 0=放行（回执入轮报告；fail-closed）。
- 人工预读结论：**零命中**——本波=对在册成员冻结参数的邻域应力重测（纯测量基础设施加深），零新机制宣称、零新候选面、零新信号定义、零前置条件类规则。
- 例外三件套（正文「邻域应力网格」词面=BAN-04 字面命中的假阳性披露，r494 合同）：
  1. 逐 matched id 引证：**BAN-04**（本件正文「网格」=采样格点/参数邻域面语义，非网格交易族）。
  2. 例外类型 token：**new_data**。
  3. 不可能看见：原证伪判面（GRID-SLEEVE 网格触发交易族·T-54 八分片判负收口）构造上只覆盖「以网格触发为入场机制的交易策略候选」；本批 34 胞全部=在册成员（low_vol/composite/drought/engulf/needle 五族）冻结参数的邻域应力重测胞，零网格触发入场构造，原判面对本批新面在构造上不可见。

## §1 机制段

- 本面非候选漏斗面：模板 §1 机制四选一不适用（法典 §2 测量面豁免如实注记）。被加深对象=在册成员的 G2 证据面（邻域稳健性/成本厚度/逐年稳定/置信区间/当期技能线）；本波不产生任何注册宣称，三态判定面=N/A。

## §2 数据与锚面

- 宇宙=core48 bare codes（48 员）；装载=`live.paper.load_core` ＋ **2026-09-22 硬截断**（t24 同窗律）；面板断言=**48 员**＋末行==2026-09-22（漂移=FAIL-CLOSED 拒烧）。
- run 约定=**注册面正典**（paper_run 引擎调用逐字）：`run_backtest(prices, {params 去 entry}, entry_signal=SIGNAL_BUILDERS 变体, exit_signal=(state<=0), dd_control=成员件 dd_control)` ＋ `ExitPatch(成员件 exit_overrides)`；成本腿=`CostPatch(3.0)`（t24 同源）。
- 中心锚门（冻结判读·探针实证 r509 bm-a `_r509bma_n3r1_anchor_probe.json` 6/6 双段全对）：in_sample sharpe 与 out_sample sharpe 对成员件 recorded 值 **|Δ|<0.002**（ANCHOR_TOL=J14/J15 项目标准）∧ 双段 trades 逐员精确恒等；**锚断员**=该员邻域/x3/逐年腿全拒（t24 锚门约定逐字：锚断员仅贡献中心胞，判读面 anchor_broken）。
- evidence_cutoff=**2026-09-22**（结果 JSON 顶层字段＋`science_gates.cutoff_meta` 双写）。
- DATA_GAP 对号：不涉（core48 legacy 面板在仓覆盖全窗）。

## §3 方法学【冻结】

- **OAT 邻域表**（冻结参数 ±1 步·逐字冻结禁跑后再挑；仓位口径=G2_DEEPENING §1 实验控制先例：top_k/top_n 扰动胞以 max_positions=k、position_size_pct=round(该员注册总敞口/k,4) 恒定总敞口，禁把暴露效应混进信号稳健性）：
  - VOLATILITY-CE-01（low_vol_long n=60, top_k=5；敞口 0.50）：n∈{50,70}，top_k∈{4,6} → 4 胞
  - COMPOSITE-CE-01（top_n_rotation n=5, rebal=20；敞口 0.95）：n∈{4,6}，rebal_days∈{15,25} → 4 胞
  - COMPOSITE-CE-02（top_n_rotation n=8, rebal=20；敞口 0.9496）：n∈{6,10}，rebal_days∈{15,25} → 4 胞
  - DROUGHT-CE-01（vol_drought_reversal vol_floor=0.55, drop_th=-0.05）：vol_floor∈{0.50,0.60}，drop_th∈{-0.04,-0.06} → 4 胞
  - ENGULF-CE-01（engulf_reversal drop_th=-0.05）：drop_th∈{-0.04,-0.06} → 2 胞
  - NEEDLE-DE-01（needle_probe drop_th=-0.05, shadow_pct=0.02）：drop_th∈{-0.04,-0.06}，shadow_pct∈{0.015,0.025} → 4 胞
- **成本 ×3 腿**：center 构造逐字 × CostPatch(3.0)（t24 x3 同源；整员全史窗）。
- 判读线（机器链接零手抄）：邻域红点线=recorded_lines()：CE 员（params 含 time_decay_period）=`ce_null_p4_batch1`，DE 员（NEEDLE-DE-01）=`i_line`；成本条款 VI_BAR=`recorded_lines()["vi_bar"]`；逐年地板=-0.35（注册标准 WORST_YEAR_FLOOR）。
- **bootstrap CI 面**：每员中心全史日收益 `bootstrap_ci_sharpe(returns, seed=70_000+员序)`（1000 重采样/block 10 日/法典登记带）；每邻域胞同员种子同面读出（CI 面=测量产物，非门）。
- **当期线复测**：每员中心 full sharpe vs `skill_line_v2(batch_cells=28)`（活线·r508 落账后 N_eff 面）——读出面=「今日重考是否过线」的应力披露，非除名门。
- 确定性律：同输入重跑字节恒等（JSONL append-only；胞 id 含员+kind+point 幂等）；分片=逐员独立（一员一 JSONL，锚断员零外溢）；种子带 disjoint=SEED_REGISTRY selftest 腿强制（70_000..70_005 vs 全注册值零交）。
- 复演/新证分类（账本面冻结）：§0 表逐字——复演 +0（6 中心）；新证 +28（22 邻域+6 x3 全部，分类依据=§0 三条实证）。

## §4 判据/读出面（测量面=数字读出，零注册门）

- **邻域条款**（G2_FOLK clause 2 逐字/t24 同源）：red=full_sharpe ≤ 员判读线；pass=red×2 ≤ points；points=0（无可扰参数）=REFUSED 如实。
- **成本条款**（t24 同源三合取）：x3 full>0 ∧ x3 oos>0 ∧ 该员 recorded x2 > VI_BAR（recorded=成员件 cost_x2.sharpe）。
- **逐年条款**：center 逐年最差 > −0.35（p3_portfolio.yearly_returns）。
- **注册 G2 列复测**（g2_registration_v2 共享库）：g1_pass=当期线复测过线（§3）；dsr=`deflated_sharpe_ratio(center 全史日收益, n_trials=活账本 total)`（raw returns 注册级路径）；pbo=**None 诚实缺省**（族内 CSCV 需同族多构型网格，本波单员族不构成合法 PBO 样本——missing_inputs=['family_pbo'] 如实披露，eligible_v2 因缺输入恒 False=设计内拒绝非判负）。
- 账本：finalize 步 `science_gates.append_ledger(batch_name="PERPETUAL-N3-R1", batch_trials=28, file_name="results/perpetual_faces/n3_r1_results.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev）。
- 无 pass/fail 注册门（测量面三态=N/A 如实）；锚断/红点/成本不存活=应力披露，非除名。

## §5 跑前预测【必填·写死于跑前】

1. **中心锚门 6/6 PASS**（探针实证 6/6 双段全对 d<5e-5、trades 逐位恒等——重跑确定性下预测=复现探针事实；锚断=0 员）。
2. **当期线复测**：6 员中 **1 员**（VOLATILITY-CE-01，full_s=1.2534 探针实测）过当期线 ~1.15；其余 5 员低于线（探针 full_s 0.9948/0.9649/0.6678/0.5467/0.4431 全在线下）——应力披露主读数。
3. **邻域条款**：低换手族（VOLATILITY/COMPOSITE/NEEDLE/DROUGHT）多数过邻域（red 稀疏先验：参数 ±1 步对全史 sharpe 影响温和）；ENGULF 2 胞小样本面五五开。
4. **成本 ×3**：VOLATILITY x3 已录 −0.1903 不存活（成员件注记·批纪构造）→ x3 腿预期 FAIL 如实（若注册面构造下翻正=如实披露差异）；NEEDLE（冻结前冒烟实测 x3 full=0.3729/oos=0.0355 双正，x2 0.574>vi）预期 PASS；DROUGHT 已录 0.4542 过线、构造同族预期 PASS；三员新 x3 未知（overlay 后成本面变厚，预测=COMPOSITE 两员存活概率低、ENGULF 存活概率低）。
5. **逐年**：6 员注册时已过 no-crash-year 条款，重测预测全过（数据窗未变）。

## §6 产物

- runner=`scripts/perpetual_faces_n3.py`（run --member <ID>（逐员分片自含＋池握手）＋status＋probe（只读中心锚探针=§2 实证件再生产＋真跑冒烟面）＋finalize（全波合并）/finalize --member（单员包再生）＋selftest）。
- 件：`results/perpetual_faces/n3_r1/cells-<ID>.jsonl`（逐员 append-only 胞件）＋ `results/perpetual_faces/n3_r1_results.json`（finalize 合并件：顶层 evidence_cutoff＋cutoff_meta＋audit 段＋34 胞全读出）＋ 逐员 pack `results/perpetual_faces/n3_r1/<ID>.json`（neighborhood/cost_x3/per_year/bootstrap_ci/当期线复测/g2_registration_v2 六面）。
- 波账=`results/perpetual_faces_state.json` waves[] append（生成器 §3 契约）；attrition 账本完整性 tripwire 覆盖本波产物件（r448 律）。
- 池握手=worker 侧 pool_claims 三调用点（r497 律：burn 完成/幂等 no-op/selftest 守卫 write=False）。

## §7 跑后实证【跑前必须为空——写数字即造假】

- 锚门 6/6 PASS（d_in≤1.4e-5/d_oos≤6e-6·trades 双段逐位恒等·finalize 后 anchor_reverify 全员 pass=true）。
- 邻域（G2_FOLK clause 2）6/6 过：红点 COMPOSITE-01 0/4·COMPOSITE-02 0/4·DROUGHT 2/4（最高应力员）·ENGULF 1/2·NEEDLE 1/4·VOLATILITY 0/4；红×2≤points 全员成立。
- 成本 x3 4/6 存活：COMPOSITE-01 +0.2259/+0.2896 PASS·COMPOSITE-02 +0.3635/+0.8175 PASS·DROUGHT +0.4108/+0.9045 PASS·NEEDLE +0.3729/+0.0355 PASS；ENGULF full +0.1684/oos −0.166 FAIL·VOLATILITY full −0.1182 FAIL。
- 逐年 6/6：worst_year −0.0380/+0.0056/−0.0179/−0.0319/−0.0078/−0.0065 全 > −0.35。
- 当期线复测 1/6：VOLATILITY-CE-01 g1_pass=true（full_s 1.2534·CI95[0.4444,2.0495]·DSR 0.0712）；其余 5 员 g1=false（0.9948/0.9649/0.6678/0.5467/0.4431 全在线下）；eligible_v2 0/6（pbo=None 设计内缺省·missing_inputs=['family_pbo'] 如实）。
- 账本行回执：append_ledger(batch="PERPETUAL-N3-R1", batch_trials=28, prev=375,419 → total=375,447, file="perpetual_faces/n3_r1_results.json", evidence_cutoff="2026-09-22")；finalize 2026-10-01T09:53:37+08:00 幂等门在（BATCH_JSON complete 复跑零重复）。

## §8 批后复盘【必填·s7-T·跑后回填】

- §5 预测对账 5 条：①锚门 6/6=对（探针复现事实）；②当期线 1/6 VOLATILITY=对（员名+full_s 1.2534 逐位命中）；③邻域 6/6 过=对（ENGULF 2 胞 1 红落在「五五开」过侧·红点 1/2 如实应力披露；DROUGHT 2/4 红为本波最高应力员）；④成本 x3=部分错：VOLATILITY FAIL（预测 −0.1903 不存活→实 −0.1182 同向✓）·NEEDLE PASS（冒烟 0.3729 命中✓）·DROUGHT PASS（同族构造✓）·ENGULF FAIL（预测低存活✓）·**COMPOSITE 两员预测「存活概率低」→实际双双 PASS（+0.2259/+0.3635 full·oos +0.2896/+0.8175）=方向保守面错**（overlay 后成本面未如预期变厚致死——预测错如实记，不回收改写）；⑤逐年 6/6=对（数据窗未变）。计分：对 4/部分错 1。
- 应力面主读数：邻域稳健 6/6 全过（DROUGHT 2/4 红为邻域最弱点）；成本 x3 存活 4/6；当期线 1/6；中心 CI95 下界>0 仅 COMPOSITE-01/COMPOSITE-02/VOLATILITY 3 员；三态注册判读 N/A（测量面零注册门）；eligible_v2 0/6=PBO 设计内拒绝非判负。
- 波状态：waves[] `n3_r1`（生成器 §3 契约·2026-10-01 09:33 supply 时点 append）；池 6 entry entry 层翻面 ready→done 同轮（r489 双层律）；引擎胞 34（22 OAT nbhd 新证+6 x3 新证+6 center 重放）；trials +28（x3 供给面 provenance 未验证计保守新证·NEEDLE 冒烟非重放 0.3729 vs recorded 0.4833 已 §0 披露）。
- 回执入轮报告+CODELY.md 行级追加：r509 bm-a（本行）；finalize commit=本轮提交哈希（git 可验）。

## 冻结签名

- 冻结时刻：2026-10-01 09:4x bm-a r509（N1-W2→N3-R1 法典起草序次位）；探针先行=锚面实证 `_r509bma_n3r1_anchor_probe.json` 在案；冻结前 write-path 冒烟=NEEDLE-DE-01 单分片（§0 披露·判据零改动）；种子带先行登记=SEED_REGISTRY `perpetual_n3_r1=70_000`（冻结 commit 内可验）；冻结 commit=本波提交哈希（git 可验）。
