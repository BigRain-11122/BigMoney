# PERPETUAL-N1-W5 预注册 · N1 nulls-deepening 波 5（T-2026-09-30-133 s2 波级冻结件）

> 令源：CEO 直令 O-2026-09-30-2340（机队满负荷·常供面）→ 面级法典=research/PERPETUAL_FACES.md v1.0（bm-b r484 面级冻结）；本件=N1 面**波级 prereg**（R99 纪律）。种子带=法典 §4 台账 W5 展行（R250 one-step 律=冻结后禁再挑；本件零新挑——W5 带首次指派即本行：A=21_900..23_899、B exit=21_700..21_899）。
> **A 带跳位注记（法典 §4 W5 行原文）**：+2_000 顺延算术位（18_100..20_099）撞 v1 B 在用带 20_000..20_019 与 SEED_REGISTRY 值 20000 及 ext W1 B 带 20_100..20_299——disjoint 硬律（selftest 机闸）优先于步长惯例，A 跳位至全部已预留带后首个连续 2,000 窗（21_900=本波 B 尾+1）；非重挑（W5 带从未指派、测量面零结果可钓、跳位发生在任何烧录之前=prereg 时点即法典指定的展行时点）。
> 性质=**测量加深面**（法典 §2：N1 对既有零假设基线按新种子带重 bootstrap 加深，产物=更深置信面〔p95/p99/mu/sigma/se_mu〕非新注册件，不入候选漏斗，不占语法消耗登记簿行；D6 同族相关性与闭合族对号约束=N2 专属，本面豁免如实注记）。
> 复用基=verbatim import 禁重写：`scripts/p2_null_calibration.py`（frozen v1 设计·run_one 引擎同源）＋ `scripts/p2_null_calibration_ext.py`（波扩展范式：_assemble/_entry_matrix/p_for/分片连续切片律/确定性重跑字节恒等）＋ `scripts/perpetual_faces_n1.py`（W2/W3/W4 落地 runner 的 wave 参数化复用——同引擎同驱动同切片律，仅法典 §4 新带）。

## §0 批件身份【必填·跑前】

- 批名=**PERPETUAL-N1-W5**。N=**2,200**（A 族 2,000＋B 族 200）；账本 **+2,200**（null trials 计数律=K2200 先例）；累计 null 池=canon 120＋W1 ext 2,200＋W2 2,200＋W3 2,200＋W4 2,200＋本波 2,200=**11,120**（法典 §5 跨波累计 N_eff 恒不重置；W4 finalize 已落 bm-a r508：merged K=8,920 mu=-0.0903 sigma=0.2451，K-lift -0.0143 负向如实）。
- 认领：T-2026-09-30-133 s2（法典注记=faces lane 任意健康机合法；本波由 bm-c 于池饿触发窗起草——supply_floor 红牌 r307）；部门=dept:研究。
- 算力预算=**长活入池**（O-20260924-2100 s2·禁轮内内联代跑）：12 分片（每片=A 族 2000/12＋B 族 200/12 连续切片；池条目=逐片一 entry）× workers_plan={"workers": 8, "priority": "BelowNormal"}（O-20260930-2355 多核律=逐片 8 workers·serial-vs-pool 字节恒等已证〔W2 parity r485/r488·W3/W4 12/12 实烧重证〕）；多片并行面=autofill claim-to-saturation〔T-134 s1 已落地〕；checkpoint=分片件本体（presence=done 证据；确定性重跑字节恒等=断点续跑语义）；跑批宿主门=core48 in-repo 数据（worker_class=self-contained·lane_owner=ANY·R31/R65 合法）。
- 物化条款（法典冻结签名行「runner 落地一批物化一批」）：本波=**生成器 supply 供给面物化**（per-shard materializer 已落地：法典 §1 三腿触发〔池饿 AND py<70 AND 无同面在飞波〕→ 生成器自动展开 12 逐片 entry 入池）；per-wave prereg 在场=物化前置条件（缺失=诚实拒绝物化，禁假供给；W2 首批 autofill-submit 特例不复用·不构成先例）。

## §0.5 禁开方向硬闸【必填·跑前】

- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W5_PREREG.md` → exit 0=放行（回执入轮报告；fail-closed）。
- 人工预读结论：**零命中**——本波=对既有 core48 零假设基线（p2_calibration v1/v2 canon＋W1 ext＋W2＋W3＋W4）的种子带扩展重测，纯测量基础设施加深，零新机制宣称、零新候选面、零新信号定义、零前置条件类规则；禁向词面不在本件复述（机器闸为准·防否证模式词面自撞，W2/W3/W4 同法先例）。

## §1 机制段

- 本面非候选漏斗面：模板 §1 机制四选一不适用（法典 §2 测量面豁免如实注记）。被加深对象=既有 G1' 技能线 null 基线（skill_line_v2 消费面）；本波不产生任何注册宣称，三态判定面=N/A。

## §2 数据与锚面

- 宇宙=core48 bare codes（48 员）；装载=`p2_null_calibration_ext.load_core_at_cutoff`（v1 `load_core` ＋ **2026-09-22 硬截断**=同窗律逐字）；引擎=`p2_null_calibration.run_one`（frozen v1 同源 import·禁旁路）；成本=FeeSchedule 单源（run_one 引擎内正典面）；断言=**48 员**（宇宙漂移=FAIL-CLOSED 拒烧）＋面板末行==2026-09-22（实跑双载断言）。
- evidence_cutoff=**2026-09-22**（同窗律；结果 JSON 顶层字段＋`science_gates.cutoff_meta("2026-09-22")` 双写，缺字段=science_audit C2 VIOLATION）。
- DATA_GAP 对号：不涉（core48 legacy 面板在仓覆盖全窗）。

## §3 方法学【冻结】

- **A 族**（j=0..1,999）：entry rng seed=**21_900+j**（法典 §4 W5 行 A=21_900..23_899·跳位注记见篇首）；p=`BASELINE_P[(j//50)%2]`（v1 50-seed 块交替延续律逐字）；随机入场矩阵＋**引擎退出**（v1 设计逐字）。
- **B 族**（j=0..199）：entry rng=**21_900+j**（与 A[j] 同阵配对语义逐字）；exit rng=**21_700+j**（法典 §4 W5 行 B=21_700..21_899·+200 律原样）；p_exit=`P_EXIT=0.05`。
- 探针=不另设（W2 探针 95_002/95_003 已证设计端到端；本波设计=W2/W3/W4 逐字复用，runner probe 面=诚实 no-op；账本 +0）。
- 确定性律：同 seed 重跑字节恒等（分片件 append-only，重跑同片=字节恒等覆写幂等）；分片=连续切片零重叠零间隙（nshards∈{1,2,4,12} 切片数学自检腿）；spawn 面波配置随 executor initializer 携带（Windows spawn 重导入回默认波=物化前已防护，selftest 腿强制）。
- 种子带 disjoint 全律（selftest 强制）：W5 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2 在用带（12_100..14_099/21_100..21_299）、W3 在用带（14_100..16_099/21_300..21_499）、W4 在用带（16_100..18_099/21_500..21_699）、SEED_REGISTRY 全值零交集（r307 bm-c 起草窗机验 PASS·152 数值全核）。

## §4 判据/读出面（测量面=数字读出，零注册门）

- 合并池=`canon 120 ＋ W1 ext 2,200 ＋ W2 2,200 ＋ W3 2,200 ＋ W4 2,200 ＋ 本波 2,200`＝**11,120** 值；`skill_line_v2` **同 n_eff K-lift**（旧线@373,219 前态 vs 新线@375,419·v2 归因律逐字）；mu/sigma/p95/p99 新旧对照与 se_mu 收窄面逐列披露。
- 账本：finalize 步 `science_gates.append_ledger(batch_name="PERPETUAL-N1-W5", batch_trials=2200, file_name="results/perpetual_faces/n1_w5_results.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev）。
- 无 pass/fail 门（测量面三态=N/A 如实）；本波数字为治理提案面素材（canon flip 不在本波——K2200 同律）。

## §5 跑前预测【必填·写死于跑前】

1. W5-only mu 与累计池 merged mu（-0.0903 实测锚·W4 finalize r508）漂移 **|Δ|<0.02**（W1/W2/W3/W4 四波实测 mu 稳定先验）。
2. sigma 相对变化 **<±10%**（同设计同窗，纯抽样波动）。
3. A 族 p95 与 W4 A 族 p95（0.3055 实测锚）差 **<0.05**（门校准注记：0.03 门在 W3/W4 连续两波越界〔0.0403/0.0323〕，邻波 2,000 样本尾部抽样噪声带实宽>0.03——本门为**结果知情校准**如实注记：预测门仅作机器断裂侦测用，测量面零注册利害；W4 §8 治理提案面已记同一结论）。
4. K-lift 线移动幅度 **≤0.02**（8,920→11,120 加深收窄 se_mu，线动=mu/sigma 微调面非质变——加深不必然抬线，W3 +0.0082/W4 -0.0143 双向先例，如实报正负）。

## §6 产物

- runner=`scripts/perpetual_faces_n1.py`（selftest/status/run --shard k --of 12 --wave 5/finalize --wave 5；probe/parity=W2 设计验证面·本波诚实 no-op）。
- 件：`results/p2cal_ext/n1_w5/shard-<k>-of-12.json`（append-only·确定性）＋ `results/perpetual_faces/n1_w5_results.json`（finalize 合并件·顶层 evidence_cutoff＋cutoff_meta＋audit 段＋K-lift 对照）。
- 波账=`results/perpetual_faces_state.json` waves[] append（生成器 §3 契约）；attrition 账本完整性 tripwire 覆盖本波产物件（r448 律）。
- 下游=skill_line_v2/g1_prime_v2 的 null 基线消费面（自动·判线共享库零手抄）。

## §7 跑后实证【2026-10-01 09:4x finalize 回填·source=results/perpetual_faces/n1_w5_results.json】

- 12/12 分片合并（shards_consumed 12 件全在场·fail-closed 过）；W5-only **K=2,200 mu=−0.0974 sigma=0.2446**（mu_delta_w5_vs_w4ext=−0.0072）。
- merged 累计池 **K=11,120 mu=−0.0917 sigma=0.2450**，se_mu@K11120=**0.002323**（五波加深收窄链持续：canon120→W1→W2→W3→W4→W5）。
- skill_line_v2 @n_eff=373,219：line_pre_w5 **1.151 → merged 1.1492**（K-lift delta=**−0.0018**）。
- A 队（n=2,000）：mu=−0.0914，**p95=0.3138**，p99=0.4661；B 队 200 run 逐件明细面在合并件。
- 账本行回执：prev_total 373,219 ＋ batch 2,200 ＝ **total 375,419**（batch=PERPETUAL-N1-W5·file=n1_w5_results.json·evidence_cutoff 2026-09-22）；波账 waves[] append wave 5 自动落（perpetual_faces_state.json）。

## §8 批后复盘【s7-T·2026-10-01 09:4x 回填】

- 预测对账 **4/4 全对**：①|Δmu| W5-only vs −0.0903 锚=0.0071＜0.02 ✓（merged 侧 0.0014 亦过）②sigma 相对变化 −0.2%＜±10% ✓ ③A 队 p95 Δ=0.0083（0.3138−0.3055）＜0.05 ✓（且本波 Δ 亦＜原 0.03 门=三波首回原门内：W3 0.0403/W4 0.0323/W5 0.0083）④K-lift −0.0018≤0.02 ✓（W3 +0.0082/W4 −0.0143/W5 −0.0018 三波全带内·线稳 1.1492）。
- 累计 null 池 11,120 态：mu −0.0917/sigma 0.2450/se_mu 0.002323——五波 22,000 值同设计同窗加深，mu/sigma 稳定先验再证；skill 线零质变（加深不抬线的 W4 结论第三次复证）。
- 回执入轮报告（r308 bm-c）；CODELY.md 流水面按记忆门①不追加（W4 finalize 同先例·git/prereg/轮报告=永久回执）。
- 供给线展望：W5 闭合后池供给面回落——W6 prereg 时 **B 带 +200 算术位（21_900..22_099）落入 W5 A 带，须同法跳位**（法典 §4 警示行已钉·r307 跳位先例复用）。
