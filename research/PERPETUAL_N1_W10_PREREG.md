# PERPETUAL-N1-W10 预注册 · N1 nulls-deepening 波 10（T-2026-10-01-141 s1 首枚引擎波）

> 令源：CEO 直令 **O-20261001-1410**（机队算力根因梳理与彻底解决令·SATURATION_ENGINE_LAW v1.0 随令立档）→ 建造票 **T-2026-10-01-141** s1（引擎核心·bm-b 实例）→ 面级法典=research/PERPETUAL_FACES.md v1.0 §4 台账 W10 展行（R250 one-step 律=冻结后禁再挑；本件零新挑——W10 带首次指派即本行：A=34_100..36_099、B exit=28_700..28_899）。**本波=首枚引擎波**：engine_owner=bm-b（SATURATION_ENGINE_LAW §1 本地永续队列烧录·**不入池**·§2 免预认领·台账异步批量；池面 supply 生成器对 engine_owner 波诚实拒绝物化=零跨机双烧面）。
> **算术续带注记（法典 §4 W10 行·W9 行预告兑现）**：A +2_000 顺延算术位（34_100..36_099=W9 A 尾+1）与 B +200 顺延算术位（28_700..28_899=W9 B 尾+1）按 W9 行净空预告**双双照常机验**（预告非免验理由·尾律）——全 N1 带表+W1 ext+v1 在用带+SEED_REGISTRY 全值+lfc_p1_screen 实际流（30_000..30_099）机验 **ADMIT 回执=results/_r508bmb_w10_band_gate.py**（r508 bm-b 起草窗实跑）：本波无跳位事实（算术续带免跳）；非重挑（W10 带从未指派·测量面零结果可钓·R250）。
> 性质=**测量加深面**（法典 §2：N1 对既有零假设基线按新种子带重 bootstrap 加深，产物=更深置信面〔p95/p99/mu/sigma/se_mu〕非新注册件，不入候选漏斗，不占语法消耗登记簿行；D6 同族相关性与闭合族对号约束=N2 专属，本面豁免如实注记）。
> 复用基=verbatim import 禁重写：`scripts/p2_null_calibration.py`（frozen v1 设计·run_one 引擎同源）＋ `scripts/p2_null_calibration_ext.py`（波扩展范式：_assemble/_entry_matrix/p_for/分片连续切片律/确定性重跑字节恒等）＋ `scripts/perpetual_faces_n1.py`（W2..W9 落地 runner 的 wave 参数化复用——同引擎同驱动同切片律，仅法典 §4 新带；引擎侧 `scripts/saturation_engine.py` 只做队列/点火/台账批处理面，runner 零改写）。

## §0 批件身份【必填·跑前】

- 批名=**PERPETUAL-N1-W10**。N=**2,200**（A 族 2,000＋B 族 200）；账本 **+2,200**（null trials 计数律=K2200 先例；prev=前波 finalize 落账值 derive·W9 finalize 时点值·禁手抄）；累计 null 池=canon 120＋W1 ext 2,200＋W2..W9 2,200×8＋本波 2,200=**22,120**（法典 §5 跨波累计 N_eff 恒不重置；W9 finalize 起草窗未落=在飞如实注记，finalize 合并面 FAIL-CLOSED 兜底）。
- 认领：T-2026-10-01-141 s1（T-141 建造票切片律·lane-free·本波=bm-b 引擎实例首枚本地队列波）；部门=dept:研究。
- 算力预算=**引擎本地队列烧录**（SATURATION_ENGINE_LAW §1/§2·**不入池**·免预认领）：12 分片（每片=A 族 2,000/12＋B 族 200/12 连续切片）；每片 workers=8（O-20260930-2355 多核律=逐片 8 workers·serial-vs-pool 字节恒等已证〔W2 parity r485/r488·W3..W9 多波 12/12 实烧重证〕·O-20261001-1410 s1 满核档=bm-b full）；点火前置自检=引擎 PreIgnitionChecks（r316 律升格：本机数据前置件复验·缺件=跳过+上报·禁僵尸点火）；checkpoint=分片件本体（presence=done 证据；确定性重跑字节恒等=断点续跑语义）；烧录宿主门=core48 in-repo 数据（worker_class=self-contained）；台账=引擎异步批量落 `results/saturation_engine/ledger_bm-b.jsonl`（§2 10-20min 或 N 片批）；跑批宿主门=core48 in-repo 数据（worker_class=self-contained·R31/R65 合法）。
- 物化条款（法典冻结签名行「runner 落地一批物化一批」）：本波=**引擎生成器物化**（N1 generator port：WAVE_CONFIGS 单源 derive·engine_owner==bm-b 波的未烧分片=本地队列项·per-wave prereg 在场=物化前置条件〔缺失=诚实拒绝物化，禁假供给〕）；池面 supply 生成器对 engine_owner 波拒绝物化（cmd_supply 跳过门·零双烧面）。

## §0.5 禁开方向硬闸【必填·跑前】

- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W10_PREREG.md` → exit 0=放行（回执入轮报告；fail-closed）。
- 人工预读结论：**零命中**——本波=对既有 core48 零假设基线（p2_calibration v1/v2 canon＋W1 ext＋W2..W9）的种子带扩展重测，纯测量基础设施加深，零新机制宣称、零新候选面、零新信号定义、零前置条件类规则；禁向词面不在本件复述（机器闸为准·防否证模式词面自撞，W2..W9 同法先例）。

## §1 机制段

- 本面非候选漏斗面：模板 §1 机制四选一不适用（法典 §2 测量面豁免如实注记）。被加深对象=既有 G1' 技能线 null 基线（skill_line_v2 消费面）；本波不产生任何注册宣称，三态判定面=N/A。

## §2 数据与锚面

- 宇宙=core48 bare codes（48 员）；装载=`p2_null_calibration_ext.load_core_at_cutoff`（v1 `load_core` ＋ **2026-09-22 硬截断**=同窗律逐字）；引擎=`p2_null_calibration.run_one`（frozen v1 同源 import·禁旁路）；成本=FeeSchedule 单源（run_one 引擎内正典面）；断言=**48 员**（宇宙漂移=FAIL-CLOSED 拒烧·引擎 PreIgnitionChecks 前置复验）＋面板末行==2026-09-22（实跑双载断言）。
- evidence_cutoff=**2026-09-22**（同窗律；结果 JSON 顶层字段＋`science_gates.cutoff_meta("2026-09-22")` 双写，缺字段=science_audit C2 VIOLATION）。
- DATA_GAP 对号：不涉（core48 legacy 面板在仓覆盖全窗）。

## §3 方法学【冻结】

- **A 族**（j=0..1,999）：entry rng seed=**34_100+j**（法典 §4 W10 行 A=34_100..36_099·算术续带免跳注记见篇首）；p=`BASELINE_P[(j//50)%2]`（v1 50-seed 块交替延续律逐字）；随机入场矩阵＋**引擎退出**（v1 设计逐字）。
- **B 族**（j=0..199）：entry rng=**34_100+j**（与 A[j] 同阵配对语义逐字）；exit rng=**28_700+j**（法典 §4 W10 行 B=28_700..28_899·算术续带免跳注记见篇首）；p_exit=`P_EXIT=0.05`。
- 探针=不另设（W2 探针 95_002/95_003 已证设计端到端；本波设计=W2..W9 逐字复用，runner probe 面=诚实 no-op；账本 +0）。
- 确定性律：同 seed 重跑字节恒等（分片件 append-only，重跑同片=字节恒等覆写幂等）；分片=连续切片零重叠零间隙（nshards∈{1,2,4,12} 切片数学自检腿）；spawn 面波配置随 executor initializer 携带（Windows spawn 重导入回默认波=物化前已防护，selftest 腿强制）。
- 种子带 disjoint 全律（selftest 强制）：W10 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2 在用带（12_100..14_099/21_100..21_299）、W3 在用带（14_100..16_099/21_300..21_499）、W4 在用带（16_100..18_099/21_500..21_699）、W5 在用带（21_900..23_899/21_700..21_899）、W6 在用带（23_900..25_899/25_900..26_099）、W7 在用带（26_100..28_099/28_100..28_299）、W8 在用带（30_100..32_099/28_300..28_499）、W9 在用带（32_100..34_099/28_500..28_699）、SEED_REGISTRY 全值零交集（**含 lfc_p1_screen 点 30_000 与其实际流 30_000..30_099 的避让=leg 3e 实际流面·本波机验 ADMIT 回执在场=r508 bm-b 起草窗**；selftest leg 2 全表 disjoint+leg 3f 续带不变式）。

## §4 判据/读出面（测量面=数字读出，零注册门）

- 合并池=`canon 120 ＋ W1..W9 ext 各 2,200 ＋ 本波 2,200`＝**22,120** 值；`skill_line_v2` **同 n_eff K-lift**（旧线=前波 finalize 落账后账本前态 derive·v2 归因律逐字·禁手抄 prev）；mu/sigma/p95/p99 新旧对照与 se_mu 收窄面逐列披露。
- 账本：finalize 步 `science_gates.append_ledger(batch_name="PERPETUAL-N1-W10", batch_trials=2200, file_name="results/perpetual_faces/n1_w10_results.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev）。
- 无 pass/fail 门（测量面三态=N/A 如实）；本波数字为治理提案面素材（canon flip 不在本波——K2200 同律）。

## §5 跑前预测【必填·写死于跑前】

（起草窗实况注记：W9 finalize 在飞未落——锚面=最近已落账 W8 finalize 实测值，W9 finalize 落账后如有更新由 §7 回填面对账披露。）

1. W10-only mu 与累计池 merged mu（W8 finalize 实测锚 **−0.0921**）漂移 **|Δ|<0.02**（W1..W8 八波实测 mu 稳定先例）。
2. sigma 相对变化 **<±10%**（同设计同窗，纯抽样波动；锚 **0.2457**=W8 merged 实测）。
3. A 族 p95 与 W8 A 族 p95（**0.3179** 实测锚）差 **<0.05**（门校准注记沿 W5..W9 先例：结果知情校准面，仅作机器断裂侦测用，测量面零注册利害）。
4. K-lift 线移动幅度 **≤0.02**（17,720→22,120 加深收窄 se_mu，线动=mu/sigma 微调面非质变——加深不必然抬线，W3..W8 六向先例（+0.0082/−0.0143/−0.0018/+0.0003/+0.0017/+0.0013）如实报正负）。

## §6 产物

- runner=`scripts/perpetual_faces_n1.py`（selftest/status/run --shard k --of 12 --wave 10/finalize --wave 10；probe/parity=W2 设计验证面·本波诚实 no-op）；点火面=`scripts/saturation_engine.py tick`（本地队列→PreIgnitionChecks→分离点火→完成探测→台账批量）。
- 件：`results/p2cal_ext/n1_w10/shard-<k>-of-12.json`（append-only·确定性）＋ `results/perpetual_faces/n1_w10_results.json`（finalize 合并件·顶层 evidence_cutoff＋cutoff_meta＋audit 段＋K-lift 对照）。
- 引擎台账：`results/saturation_engine/ledger_bm-b.jsonl`（§2 异步批量·逐分片行：batch/shard/started_at/done_at/elapsed_sec/pid）；attrition 账本完整性 tripwire 覆盖本波产物件（r448 律）。
- 下游=skill_line_v2/g1_prime_v2 的 null 基线消费面（自动·判线共享库零手抄）。

## §7 跑后实证【待回填·finalize 后同窗回填=r307 两态守卫律】

- 占位（12/12 分片合并·W10-only K/mu/sigma·merged K=22,120 面·se_mu·K-lift·账本行回执 prev=W9 finalize 落账值+2,200 derive）。

## §8 批后复盘【s7-T·待回填】

- 占位（预测对账 4/4 面·累计池 22,120 态·波间协作如实记·W11+ 尾律警示窗照法典 §4 W10 行·引擎面首波运行实况〔点火延迟/自愈/台账批节奏〕如实记）。
