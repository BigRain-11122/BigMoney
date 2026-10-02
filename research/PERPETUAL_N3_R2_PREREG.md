# PERPETUAL-N3-R2 预注册 · N3 neighborhood robustness grid 波 2（时间区间起点稳健性网格）· **FROZEN v1.0**

> 令源：O-20261002-2155 P0 引擎发生器补全（三面单执行体闭合：bm-a=N4-B1 · bm-b=N2-W15 slice-2 · **bm-c=N3-R2**〔MSG-2026-10-03-0115 认领〕）；面级法典=research/PERPETUAL_FACES.md v1.0 §2 N3 行；本件=N3 面**波级 prereg 草案**（R99 纪律·从 PREREG_TEMPLATE.md 起草）。
> 性质=**测量加深面**（法典 §2 同 R1：对在册成员重测、产物=更深置信面非新注册件、不入候选漏斗、不占语法消耗登记簿行、零除名效应——本波判读不触发成员状态变化；D6 同族相关性约束=N2 专属，本面豁免如实注记）。
> 复用基=verbatim import 禁重写：`scripts/perpetual_faces_n3.py`（R1 runner：_panel/load_members/FAMILIES/_run_cell/池握手全套——R2=同 runner 的 R2 波模式扩展）；`science_gates`（recorded_lines/append_ledger——判线机器链接零手抄）；`live/paper` 注册面正典 run 约定（R1 §2 同源逐字）。
> **状态=FROZEN（2026-10-03 03:0x bm-c r394）**：五条件冻结门全过=①runner R2 模式落地（`run/finalize/probe/status --wave r2`·selftest S1-S9 ALL PASS·02:5x）②probe 复验 PASS（常设化 `probe --wave r2`·4 腿 P/S/R/W 全绿·worst 0.912@2025Q4 与 §0 冻结前披露逐位复现·回执 results/_n3r2_probe_latest.json）③banned_direction_gate ADMIT rc0（BAN-04 字面命中+§0.5 例外三件套完整·02:5x）④S6 链自检 rc0 全绿（本窗 36 腿·reconcile ZERO-DRIFT streak 1/3·详见 r394 轮报告）⑤冻结 commit（签名节回填）。冻结前零烧录零池物化已守（法典 §1）；冻结后按 §0 算力预算入池。

## §0 批件身份【必填·跑前】

- 批名=**PERPETUAL-N3-R2**。宇宙=**在册 6 员**（同 R1：COMPOSITE-CE-01/02、DROUGHT-CE-01、ENGULF-CE-01、NEEDLE-DE-01、VOLATILITY-CE-01；evidence_cutoff=2026-09-22 逐员断言）。
- **面定义（R2=时间区间维应力网格）**：R1 应力维=冻结参数邻域（OAT ±1 步·参数轴）；R2 应力维=**时间区间起点**（投资者从不同季度开始跟单的全起点体验分布）——与 R1 正交=「全新邻域面非重烧」（MSG-0115 认领原文）；模板 §8 §1.3 全起点分布条款的批级前置化。
- **设计取舍披露**（认领文三候选方向）：①实用 SW 分区=本波采（「新区」字面正解+CEO 可呈报语义「从 X 年 X 季开始跟单体验如何」）；②hold 族扩展=弃（扰动成员自有出场栈=违 R1 注册面正典 verbatim 约定·出场轴显式门①策略自有出场）；③参轴增广=弃（参数维加密=R1 邻域面扩展非新维·留 R3 候选如实注记）。
- 引擎格=**6 center 复演 + 144 窗读出格**（24 起点/员 × 6 员；窗读出=eq 曲线切片统计纯数学面·零额外引擎跑）；**账本 +144**（保守侧：窗读出面=R1 未测的新证据读出格全计·派生面性质如实注记——R1 分类纪律「未验证复演一律从新证」同源）。
- 认领：T-2026-10-03-151 分工面响应（bm-c MSG-0115）；部门=dept:研究。
- 算力预算=**长活入池**（O-20260924-2100 禁轮内内联代跑）：6 分片（每片=1 员 center 复演 ~5-10s + 24 切片统计 <1s = 轻批·R1 同量级）；workers_plan={"workers": 1, "priority": "BelowNormal"}（R1 同款·轻批不套多核壳）；lane_owner=ANY（R31/R65 合法）；确定性重跑字节恒等（checkpoint JSONL append-only·幂等）。
- 冻结前冒烟披露（R1 §0 先例同款·判据零改动）：probe=results/_r392bmc_n3r2_probe.py（4 腿全 PASS·2026-10-03 r392 bm-c）——leg P 面板四元组断言（core48 48 员·cutoff 2026-09-22·1631 bar·首 bar 2020-01-02）；leg S 起点表 derive=24 季度首 bar；leg R center 引擎复演（VOLATILITY-CE-01）与 R1 checkpoint **逐位恒等**（full_s 1.2534/in 1.103/oos 1.7166/trades 470/339/131——确定性律实证）；leg W 24 窗切片读出+rebase 交叉路径恒等（allclose<1e-12）。

## §0.5 禁开方向硬闸【必填·跑前】

- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N3_R2_PREREG.md` → exit 0=放行（回执入轮报告·fail-closed）——冻结门条件③。
- 人工预读结论：**零命中**——本波=对在册成员净值曲线的时间区间起点应力重测（纯测量基础设施加深），零新机制宣称、零新候选面、零新信号定义、零前置条件类规则。
- 例外三件套（正文「网格」词面=BAN-04 字面命中假阳性披露，R1 合同同款）：
  1. 逐 matched id 引证：**BAN-04**（本件正文「网格」=起点采样格点语义，非网格交易族）。
  2. 例外类型 token：**new_data**。
  3. 不可能看见：原证伪判面（GRID-SLEEVE 网格触发交易族·T-54 八分片判负收口）构造上只覆盖「以网格触发为入场机制的交易策略候选」；本批 144 胞全部=在册成员（low_vol/composite/drought/engulf/needle 五族）冻结构造净值曲线的起点切片读出，零网格触发入场构造，原判面对本批新面在构造上不可见。

## §1 机制段

- 本面非候选漏斗面：模板 §1 机制四选一不适用（法典 §2 测量面豁免·R1 同款注记）。被加深对象=在册成员的**时间区间稳健性证据面**（全起点分布：从任意季度开始跟单的已实现体验分布）；本波不产生任何注册宣称，三态判定面=N/A。

## §2 数据与锚面【必填·跑前】

- 宇宙=core48 bare codes（48 员）；装载=`live.paper.load_core`＋**2026-09-22 硬截断**（R1 同窗律逐字）；面板断言=48 员＋末行==2026-09-22（漂移=FAIL-CLOSED 拒烧·`_panel()` 同函数复用=probe-锚同面断言律天然满足）。
- **数据锚面定义四元组**（G-ANCHOR-FACE 律）：①数据面路径=`data/daily/sh*.csv`（core48 bare codes）②加载函数=`live.paper.load_core -> build_panels`（probe 复用 `perpetual_faces_n3._panel()` 同一函数）③起算窗=**2020-01-02**（面板首 bar·probe leg P 实证 1631 bar——注：非 2012 全史 CSV 起点，load_core 载入的 core48 面板自身始于 2020-01-02）④预热窗=vol20/med500 min_periods 20/500（面板内预热·信号首有效 bar 后的一切起点合法）。
- run 约定=**注册面正典**（R1 §2 逐字）：`run_backtest(prices, {params 去 entry}, entry_signal=SIGNAL_BUILDERS 变体, exit_signal=(state<=0), dd_control=成员件)`＋`ExitPatch(成员件 exit_overrides)`——**出场轴显式门声明（O-20261001-1108）=①策略自有出场**（center 构造 verbatim·成员件出场栈逐字零扰动）。
- **起点表冻结公式**：起点族=**每季首交易 bar**（Q1=01-01/Q2=04-01/Q3=07-01/Q4=10-01 首个面板 bar），年度域=面板首年（2020）至 cutoff 前一年（2025）→ derive 起点=**2020Q1..2025Q4=24 起点**（probe leg S 实证 24/24·面板头重叠去重后）；起点域=面板内（面板外年份起点坍缩=构造排除）。
- **跟单进场语义钉死**：起点 s 的跟单窗=**s 收盘进场、持有至 cutoff**——窗日收益序列=全史日收益的**严格尾段切片（index > s）**；`>=` 切片会把 s-1→s 的损益（属前一日的投资者）误记给 s 进场者=语义错误（probe 开发窗当场抓出并修正——判据面冻结前设计修正·非结果驱动·r251/r280 先例族）；rebase 交叉验证腿（切片路径 vs 重基路径 allclose<1e-12）=runner 常设断言。
- evidence_cutoff=**2026-09-22**（结果 JSON 顶层字段＋`science_gates.cutoff_meta` 双写）。

## §3 方法学【冻结】

- **起点应力网格**（冻结公式禁跑后再挑）：每员 center 构造（冻结参数 verbatim·零成本补丁）全史引擎跑 1 次 → eq 逐日净值曲线 → 24 起点窗切片读出：`window_sharpe`（窗日收益 mean/std×√252）、`annual_return`（窗终复利年化）、`max_dd`（窗内 cummax 回撤）、`n_days`。
- **中心复演锚门**（冻结判读）：每员 center 复演读数与 R1 checkpoint 胞**逐位恒等**（full/in/oos sharpe 双段+trades 双段+maxdd+annual——确定性律下面=复现事实）；锚断员=该员 24 窗全拒（R1 t24 锚门约定同型）。
- 判读线（机器链接零手抄）：窗红点线=recorded_lines()：CE 员=`ce_null_p4_batch1`（0.4474）、DE 员（NEEDLE-DE-01）=`i_line`（0.3521）——逐员判线与 R1 §3 同源。
- **种子面=零新随机面声明**：窗切割=日历确定性 derive；切片统计=纯数学零随机；center 复演=确定性引擎零种子；窗级不跑 bootstrap CI（短窗 CI 无意义面宽·全史 CI R1 已测）→ **R2 零新种子带**（SEED_REGISTRY 零新增键）——对 MSG-2026-10-03-0135（bm-a N4-B1 DRAFT 带位 68_501..69_999 防撞提示）的回执：R2 无新种子带=零撞面，提示条件性消解（若下轮设计变更引入随机面须重过带闸扫描含 N4 DRAFT 带）。
- 确定性律：同输入重跑字节恒等（JSONL append-only·胞 id=员+start 幂等）；分片=逐员独立（一员一 JSONL，锚断员零外溢）。

## §4 判据/读出面（测量面=数字读出，零注册门）

- **起点红点条款**（R1 邻域条款同型）：red=window_sharpe ≤ 员判读线；pass=**red×2 ≤ 24**（多数起点存活）。
- **全起点分布**（模板 §8 §1.3 逐字）：每员 24 起点的 best/worst/p25/median/p75（pandas 线性插值分位）＋worst-start 季度披露。
- **worst-start 应力披露**：每员最差窗 {window_sharpe, start, n_days, max_dd}（CEO 呈报白话面：最坏进场时点的体验）。
- 无 pass/fail 注册门（测量面三态=N/A 如实）；锚断/红点=应力披露非除名；窗读出**不构成**任何成员状态变化（月界注册管线独占）。
- 账本：finalize 步 `science_gates.append_ledger(batch_name="PERPETUAL-N3-R2", batch_trials=144, file_name="results/perpetual_faces/n3_r2_results.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev）。

## §5 跑前预测【必填·写死于跑前】

1. **中心复演锚门 6/6 PASS**（确定性律下=复现 R1 checkpoint 事实；VOLATILITY 腿 probe 已实证逐位恒等）。
2. **VOLATILITY-CE-01 全起点分布**（probe 实测冻结前披露）：best 1.9888 / worst 0.912 @2025Q4 / p25 1.2196 / median 1.4391 / p75 1.7174；24 窗红点 0/24（全窗过 CE 判线 0.4474）——复现 probe 事实。
3. **红点条款**：低换手族（VOLATILITY/COMPOSITE-01/02/NEEDLE/DROUGHT）预期多数起点过线（R1 邻域稳健 6/6 先验迁移：参数 ±1 步都稳的成员对进场时点应同样稳）；**ENGULF-CE-01 风险最高**（R1 邻域 1/2 红·小样本面）——预期起点红点率显著高于他员。
4. **worst-start 形态预期**：最差起点聚集于两类——近段短窗（2025Q4 类·窗仅 ~1 季度·样本噪声主导）与熊市段起点（2021Q1/2022Q1 类·进场即遇回撤段）。
5. **极端日先验**（硬界设计三件套 (c)）：2020Q1 起点窗含 2020-03 疫情熔断段（面板最深应力段·预期该起点 maxdd 为各员最差窗前列）；2024Q4 起点窗含 2025-01-19 极端溢价日（D-C 批实证 12 极端微观结构日族之一）——maxdd 读出面按分布界披露非裸 max 判门。

## §6 产物

- runner=`scripts/perpetual_faces_n3.py` R2 波模式扩展（run --member <ID> --wave r2＋finalize --wave r2＋probe（R2 探针=本 probe 收编常设化）＋selftest 增 R2 腿）——下轮工程续作（冻结门条件①）。
- 件：`results/perpetual_faces/n3_r2/cells-<ID>.jsonl`（逐员 append-only 胞件）＋`results/perpetual_faces/n3_r2_results.json`（finalize 合并件：顶层 evidence_cutoff＋cutoff_meta＋audit 段＋144 窗读出＋6 员 pack）＋逐员 pack `results/perpetual_faces/n3_r2/<ID>.json`（全起点分布/红点条款/worst-start/中心复演锚验五面）。
- 波账=`results/perpetual_faces_state.json` waves[] append（生成器 §3 契约）；attrition 账本完整性 tripwire 覆盖本波产物件（r448 律）。
- 池握手=worker 侧 pool_claims 三调用点（r497 律：burn 完成/幂等 no-op/selftest 守卫 write=False）。

## §7 跑后实证【跑前必须为空——写数字即造假】

（占位——冻结后烧录+finalize 回填；一次定稿）

## §8 批后复盘【必填·s7-T·跑后回填】

（占位——预测对账 5 条+全起点分布读数+回执入轮报告+CODELY.md 行级追加）

## 冻结签名（FROZEN——五条件达成回填）

- 冻结时刻：2026-10-03 03:0x bm-c r394 会话（条件①-⑤全过；冻结 commit=本件所在 commit·哈希见 git log --grep "freeze PERPETUAL-N3-R2"）
- 条件①：runner R2 波模式落地+`selftest` S1-S9 ALL PASS（S9=R2 机件腿七件：起点族 24+标签序+面板头季中旬去重/严格尾切片语义（进场日移动不归跟单者）/窗读出算术/红点条款边界/零新种子钉（SEED_REGISTRY 无 perpetual_n3_r2 键）/波面池 id 双态/R2 JSONL 幂等 fixture/锚门逐位算术·2026-10-03 02:5x）
- 条件②：`probe --wave r2` 4 腿 PASS（P 面板四元组 48 员·1631 bar·尾 2026-09-22 / S 起点表 24 / R center 复演与 R1 checkpoint 逐位恒等 / W 24 窗读出+rebase 交叉路径恒等·red_rate 0.0·worst 0.912@2025Q4 与 §0 冻结前披露逐位一致）·回执 results/_n3r2_probe_latest.json
- 条件③：banned_direction_gate ADMIT rc0（BAN-04 网格字面命中·§0.5 例外三件套完整·new_data·2026-10-03 02:5x）
- 条件④：S6 链自检 rc0 全绿（本窗 36 腿·reconcile ZERO-DRIFT·compute_audit supply_gap 旗如实照录=r393 p1c_stock 数据根因封锁的机队面观察非本机违令·py_watermark py_low_with_work_cands 的点名整改=本冻结+同窗入池物化即供给）
- 条件⑤：本 commit（冻结与 runner/探针回执同窗落账；池物化随后续 commit）
- 冻结前 probe：results/_r392bmc_n3r2_probe.py + results/_r392bmc_n3r2_probe.json（4 腿 PASS·2026-10-03 r392 bm-c·VOLATILITY 单员冒烟·判据零改动）
- 起草：2026-10-03 ~02:2x bm-c r392 会话（MSG-0115 认领兑现·主产品线首件）；冻结：2026-10-03 03:0x bm-c r394 会话
