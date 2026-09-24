# T34_EARLY_SIGNAL 预注册：前置快线半档梯 A/B（虚拟时间点全起点·军种路由面）

- **批名**：T34_EARLY_SIGNAL（前置信号研究批·CEO 直令 O-20260924-2030 §三·票 T-2026-09-24-34 immediate）
- **认领**：r113 bm-b 认领（F-04 MSG-20260924-2038 + commit d88f2a6；候选登记册 C1-C4 已在票面 note 逐字枚举）；本预注册=r114 跑前冻结（J18 序法：冻结早于一切 harness 跑动）。
- **部门**：dept:研究+风控（票面 owner dept）。
- **算力预算**：Stage A 曲线重派生 16,566 引擎格（6 员 × 2,761 起点 × base 面）≈ 80-110min @ 12 workers BelowNormal 分离批（R41 后台化+逐格 checkpoint）；Stage B 包络叠加 <2min 纯向量化。批报告必带 audit 段。

## §0 批件身份

- **批内格数（N_eff）＝5,522**（包络格：2 臂 × 2,761 起点＝2×(1,255 legacy + 1,506 deep)）。**Stage A 成员曲线格不计账**——同一 (member,startpoint) 格已由 T22_VIRTUAL_TIMEPOINTS 批计数（16,572 格），本批=已计格的曲线面重派生（反重复计数纪律；t22 finalize dprobe 先例）；确定性探针格不计账（dprobe 先例）。
- **零新注册**：本批不注册任何新交易员/不动 PAPER_LEVELS/零 paper 接线（票面 "NO paper activation in this batch" 逐字兑现）；不触发 g1_prime_v2/g2_registration_v2（路由规则 A/B 非成员注册）。启用面另走 T-33 d3 路由 spec + 月界。

## §1 α 机制段（D6 四选一）

**机制=行为偏差（动量期确认滞后下的早入场捕获）**。一句话论证：确认线（MA250/MA200 系慢线）的确认滞后=换防迟到成本的结构根源——GREEN 确认前市场往往已走出一段动量（underreaction→趋势延续），前置快线在确认前把进攻军半档押入，捕获的即这段「确认前动量」；**代价支付者=梯子使用者自己**（鞭打换手：假信号半档押入→确认线永不 GREEN→回撤成本由本方承担）——故「值不值必须实测」（O-2030 §三3 检验纪律逐字）。

**D6 同族披露**：本批零新交易员函数（军种成员=在册 6 员复用 T-33 roster 分配，成员级 corr 门已在册）；快线 C1-C4=路由层叠加门非成员函数，成员级 max|corr| 检查不适用，如实以 **C1-C4 状态重叠率**（逐对激活日重合 %）作层内去冗余披露，无门（层内多线共存合法，采用以 primary 判定）。

## §2 数据与面板（跑前探针事实）

- **双轴复用 T-22 冻结面**：legacy=core48 CSV 面板截断 **evidence_cutoff=2026-09-23**；deep=T-18 面板 manifest PASS（panel 2013-06-17→**2026-09-22**，48 员，19 员 adjusted view 硬门）——逐字复用 `t22_virtual_timepoints._load_axis_prices` 断言链。**binding cutoff=2026-09-22**（deep 面）；结果 JSON 顶层带 `science_gates.cutoff_meta("2026-09-22")`。09-24 新 bar 锁死不入本批（前向锁盒 D2）。
- **数据完备门（不过即 VOID 中止零产数）**：
  - G-CENSUS（漂移门，r105 律）：冻结 cutoff 下重枚举起点集必须逐位等于 T-22 finalize 记录 {legacy: 1,255, deep: 1,506}（源=results/t22_virtual_timepoints.json axes…n_starts 实读，禁手抄）；
  - G-ANCHOR：6 员锚定门全过（T-22 run 门同款）；
  - G-V3：legacy 轴确认线=v3 import-replay（live.paper.v3_state_series），截断 09-23 的窗口状态计数必须逐位等于校准批记录 GREEN=664/YELLOW=772/ORANGE=35/RED=161（源=results/regime_calibration_v3.json state_counts 实读）；
  - G-MANIFEST：t18 manifest verdict==PASS 且 48 员（_load_axis_prices 内建断言）。
- **宇宙**：core48 双轴（与 T-22 同口径）；军种成员=在册 6 员（T-33 roster v1 冻结分配：attack={COMPOSITE-CE-01}、chop={CE-02, DROUGHT, ENGULF, NEEDLE, VOLATILITY}、defense=∅→RED/bear=100% 现金，诚实缺口披露）。

## §3 方法学（冻结）

- **确认线（慢线·对照臂基座）**：legacy 轴=REGIME_GUARD v3 四态（import-replay 无缓存）；deep 轴=v3 仅覆盖 2020+→**诚实降级为 T-22 冻结 3-way proxy**（510300 vs MA200：bear/chop/bull，与 T-22 分段同源 disclosed proxy，非 REGIME_GUARD 第二真值源）。映射（冻结）：GREEN/bull→attack；YELLOW/ORANGE/chop→chop（YELLOW=非确认进攻，路由面保守归震荡军；v3 响应矩阵 x0.5 sizing 属执行面 sizing 非军种路由，本批不涉及）；RED/bear→cash。
- **前置快线（候选登记册，票面 C1-C4 全部预注册，参数冻结零事后搜索）**：
  - **C1（primary）MA20/MA60 金叉梯+持续滤**：510300 收盘 ma20>ma60 且**连续保持 P=5 bar**（t-4..t 全真）→ ladder_active；ma20≤ma60 即刻熄灭（非对称出线=防鞭打设计）。
  - C2 池内宽度：core48 有效成员 close>自身 MA20 占比 >0.60 → breadth_bull（reporting 列）。
  - C3 波动率形态：510300 vol20>vol60（日收益口径）→ vol_expand（reporting 列）。
  - C4 动量冲击：510300 20 日收益 >+5% → thrust（reporting 列）。
  - **采用门只绑 C1**；C2-C4 逐线 A/B 读数如实披露但零判定权——单线翻案须另开预注册（PA1 r55 律）。
- **半档梯（O-2030 §三2 逐字）**：ladder_active 且确认态≠GREEN/bull 时：attack=0.5、确认态军种=0.5（chop 或 cash）；确认 GREEN/bull→attack=1.0（确认线优先，梯子只补位不越权）；**刹车 T0 权威不破**（REGIME_GUARD 红线零触碰，本批只测路由权重不碰执行面）。
- **因果契约**：T 收盘决策→T+1 开盘生效（引擎契约同款）：状态/快线序列按面板行 shift(1) 后赋权，无未来数据；w(首行)=首已知态的保守映射（无前决策→不预置进攻）。
- **包络构造**：军种日收益=成员引擎曲线日收益 EW（成员曲线含引擎全部 T+1/成本）；env_ret(t)=Σ_c w_c(t)·r_c(t) − rebalance_cost(t)；**rebalance_cost=单边费率 × Σ_c|w_c(t)−w_c(t−1)|**，单边费率=science_gates.COST_X2_RATE/2（≈13.04bp，禁手抄，运行时派生披露）；窗内权重变化才计费，起点日初始建仓不计（与成员格/被动基线的成本不对称同向保守：包络带再平衡成本 vs 被动零成本，诚实让分）。passive=T-22 同款（s 日已上市成员 EW buy&hold）。
- **窗口族**：{6m=126, 12m=252, 24m=504}；每起点跑 24m 一段、切 6m/12m 片（P-5 切片法）；partial 窗如实标记，主读=完整窗子集，all-window 面并行披露。
- **null 对照**：本批无 K=50 随机 null——对照=CONF 臂自身+被动基线（A/B 设计固有对照）；pooled beat 率 95% CI=二项 bootstrap B=2000，seed 基=**20260928**（已登记 science_gates.SEED_REGISTRY["t34_early_signal"]，rg 全 repo 扫描空闲，唯一命中=Money0923/tests 日期串非 RNG 巧合已披露）。
- **成本口径**：成员曲线=V1 legacy 引擎面（base，13bp 系）；包络再平衡=上述单边率；×2 面不入本批（曲线重派生用 base；x2 生存面另批）。

## §4 判据（跑前写死，O-2030 §三3+票面 deliverable-3 逐字）

- **J1（primary·J4 提升）**：pooled 12m beat-passive 率提升（LADDER−CONF）**> 0 且双轴同号**（legacy 与 deep 均 >0）。
- **J2（红线）**：LADDER 臂最差起点 12m 回撤 ≥ **−0.35**（双轴；P-5 冻结红线）。
- **J3（如实披露，无门）**：双臂逐窗换防计数（mean/median/max）+ 梯子点火/熄灭 episode 数；LADDER≥CONF 由构造，读数照抄。
- **PASS=J1∧J2** → STYLE_CORPS v1.1 §4.5 接线注（启用候选面：另批走 T-33 d3 路由 spec 冻结+月界，本批零接线）；**FAIL→诚实不用，保持纯确认线**（O-2030 逐字）。
- 附披露（无判定权）：配对不一致格计数（L+R−/L−R−）、提升量 bootstrap CI、C2-C4 逐线 uplift、半档分数敏感性 0.25/0.75、CONF 臂同门读数。

## §5 跑前预测（写死于跑前，跑后 §7 对账）

1. G-CENSUS 双门 1,255/1,506 逐位复现（确定性管线）；
2. CONF 臂 pooled 12m beat ≈ [0.50, 0.65] 双轴（6 员包络；T-22 pooled 6m 0.55-0.70 带的 12m 平滑迁移）；
3. LADDER−CONF 提升点估计 [−0.01, +0.04]：确认前动量捕获为正、鞭打+半档稀释为负，net 方向先验=微正但弱（MA20/60 在指数上 2-6 次/年点火，样本内 GREEN 前置窗有限）；**整体 PASS 概率 30-45%**（J1 双轴同号是最可能失败点）；
4. 梯子点火频率：[2, 8] episodes/年（510300 MA20/60 中频系）；
5. LADDER 最差起点 12m dd ∈ [−0.32, −0.12]（包络分散+RED 现金底浅于单成员；−0.35 红线预计不绑定）；
6. 换防计数：LADDER−CONF 均值增量 [+0.5, +3] 次/12m 窗（半档开关叠加确认线开关）。

## §6 产物

script `scripts/t34_early_signal.py`（run/overlay/finalize/selftest 子命令；Stage A 复用 t22_virtual_timepoints 枚举/装载/锚门原语，禁重写）+ 曲线 checkpoint `results/t34/curves_{axis}.jsonl`（gitignored 数据面）+ `results/t34_early_signal_verdict.json`（顶层 cutoff_meta("2026-09-22")）+ `research/shortline/t34_envelope_results.csv`（聚合小表）+ 本文件 §7/§8 回填 + STYLE_CORPS v1.1 §4.5 接线注。

## §7 跑后实证（跑前必须为空——占位纪律：写数字即造假）

- **跑动**：r115 bm-b 一次定稿（stage A=r114 死轮分离批 7518+9036 格双轴全完 262.6s/575.5s @ workers_plan=10；stage B=finalize 74.3s；run#1 门红→run#2 正典，见 §8 坑注）。
- **门读数**：G-V3 PASS（1632 日窗逐位 GREEN664/YELLOW772/ORANGE35/RED161）；G-CENSUS PASS {legacy 1,255, deep 1,506} 逐位；G-PROBE 12/12+24/24 bit-equal；G-ANCHOR 6/6（stage A 起跑）；audit 段=FLAG:idle_with_work @21:26:17（finalize 内联 I/O 间隙采样瞬时，如实入 verdict）。
- **legacy 轴**（完整 12m 窗 n=1,129）：CONF 485/1,129=**0.4296** CI[0.4021,0.4579]；LADDER 526/1,129=**0.4659** CI[0.4376,0.4942]；**uplift=+0.0363**；配对 L+R−=41 / L−R+=**0**；LADDER 最差起点 dd=**−0.1249**（红线 −0.35 不绑定）；换防均值 48.3→52.74（+4.44）。
- **deep 轴**（n=1,380）：CONF 544/1,380=**0.3942** CI[0.3696,0.4196]；LADDER 594/1,380=**0.4304** CI[0.4058,0.4565]；**uplift=+0.0362**；配对 50/**0**；最差起点 dd=**−0.1041**；换防 17.66→23.63（+5.97）。
- **梯子点火**：legacy 16 次/6.7y≈2.4/年；deep 32 次/13.3y≈2.4/年。
- **敏感性（零判定权报告列）**：C2 uplift legacy +0.0/deep −0.0507（宽度线不迁移）；C3 +0.0319/+0.0159（双轴正）；C4 −0.0044/−0.0217；半档 h25 +0.0204/+0.0123、h75 +0.0505/+0.0623（更高半档读数更优=报告面，采用仍绑 C1@h=0.5 冻结值，禁事后择优）。
- **判定**：J1 ✓（双轴 uplift>0 同号）∧ J2 ✓（双轴最差 dd 远离红线）→ **PASS**。产物=results/t34_early_signal_verdict.json（evidence_cutoff=2026-09-22+prereg_sha256）+research/shortline/t34_envelope_results.csv。
- **账本**：batch_trials=5,522 **未入统一账本**（audit 非 CLEAN→per §0 不计数，verdict trials_ledger total=null 如实；不重跑刷采样——确定性 finalize 重跑唯一差异=audit 采样，属「跑到达标为止」禁律邻域）。链头维持 60,074（xstock_synth 面）。

## §8 批后复盘（s7-T 必填）

- **预测对账（对3/部分1/错2）**：①G-CENSUS 逐位复现=**对**；②CONF 12m ∈[0.50,0.65]=**错**（实测 0.4296/0.3942 双轴低于带——12m 窗含熊段多于 6m 切片，T-22 6m 带迁移假设过乐观）；③uplift ∈[−0.01,+0.04]=**对**（+0.0363/+0.0362 双双带内；PASS 概率 30-45% 的保守方向兑现，预测的最可能失败点「双轴同号」实测未失败）；④点火 [2,8]/年=**对**（双轴均 ~2.4/年）；⑤最差 dd ∈[−0.32,−0.12]=**部分**（legacy −0.1249 带内；deep −0.1041 浅于带沿=保守方向偏离；「红线不绑定」兑现）；⑥换防增量 [+0.5,+3]=**错**（实测 +4.44/+5.97 超上沿——半档开关鞭打代价被低估；但配对 41/50 wins vs **0** regressions 证明增量换手换来纯增益，J3 披露面如实）。
- **坑注（run#1 门红→修实现禁改判据 J18）**：G-V3 首跑红=T-18 Twin 长史（r101 落地）把 v3 重放面扩到 2012 起（3,484 态）vs 校准窗 2020-01-02 起（1,632）——门实现只裁 end 未裁 start；实测窗内段逐位一致（664/772/35/161 精确）证重放无恙，修=窗口过滤补 start 界（判据零触碰）；selftest 13/13 无 G-V3 活线覆盖=假绿盲区（门族自检缺口，HQ-FEEDBACK 候选）。
- **attrition 行**：runner 正典行已在 results/gate_attrition.json（T34_EARLY_SIGNAL · measurement · cells_ledger_delta=0 未入账如实 · ledger_total_after=null · gates={pass=true, uplift 双轴, min_dd 双轴}；r115 手动重复行已删=保 runner 自动行唯一）。
- **定案（O-2030 §三3 逐字）**：半档梯=**ENABLED candidate**——另批走 T-33 d3 路由 spec 冻结+月界接线（本批零接线零激活零注册；目标月界=11-01 per STYLE_CORPS §6）；接线注已落 firm/STYLE_CORPS.md §4.5。
- **回执**：入 r115 轮报告+CODELY.md；票 T-2026-09-24-34 done（result_ref=results/t34_early_signal_verdict.json）。

预测对账（对/部分/错）+ gate_attrition.json 追加行 + 回执入轮报告与 CODELY.md；PASS→接线注+路由 spec 指针；FAIL→保持纯确认线定案（O-2030 逐字）。
