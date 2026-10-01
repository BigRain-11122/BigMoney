# PERPETUAL-N1-W40 预注册 · N1 nulls-deepening · 第40波（never-dry 常设供给步·第三十枚引擎波·bm-b 第十三自有波）

> 来源：CEO 直令 **O-20261001-1410**（波级常设供给·饱和引擎落地·SATURATION_ENGINE_LAW v1.0 冻结法·池化禁令）+ 票 **T-2026-10-01-141** s1 lineage。本机 bm-b 实况架构=scripts 单源 tick 架构（schtasks 1-min 起进程·per-tick module re-read D-20261002-03 fix1·点火验证唯一证据=产物增长 r330-③）。
> **带位注记（法典 §4 W40 行·A 算术顺延位+B 算术顺延位·双侧零跳位实况）**：A=123_004..125_003（==W39 A 尾 123_003+1·步长逐字·与 W39 行 W40+ 警示投影 CLEAN 带位吻合·leg1-A registry-derive 机证=候选·非重挑 R250）；B=43_201..43_400（==W39 B 尾 43_200+1·算术位零跳位·与 W39 行 W40+ 警示投影 CLEAN 吻合·leg2-B 首净窗机证=候选）。
> 设计=**冻结设计 verbatim**（§2 N1 自家基线：入场矩阵从上已注册 bootstrap 面扩带·结果=引擎出口分布·p95/p99/mu/sigma/se_mu·预注册纪律零选漏；带位与法典登记簿同律；D6 同族单字门不适用·本注=非注册新主张）。
> 蓝本=verbatim import 自 `scripts/p2_null_calibration.py`（frozen v1 设计）·`run_one` 同源引擎·扩展面 `scripts/p2_null_calibration_ext.py`（扩展入场·_assemble/_entry_mat 族）。

## §0 波级参数冻结【存证·跑前】

- 批名=**PERPETUAL-N1-W40**·N=**2,200**（A 带 2,000·B 带 200）·净本波 **+2,200**·null trials 台账口径=K2200 同律·prev=**活链头 derive（冻结声明）**·数据从实锚定**W1..W38 finalize 落全**（W38=bm-b r530 同窗收官·链头 446,140·W39 finalize 待落〔bm-c 车道〕·W40 finalize 链序候 W39 落地后·链头运行时 derive 非预写）。
- 供给律：never-dry 常设供给步·TRIAL_LABOR_LAW §4（板空/池饿/无在飞判决批=默认续下一波候选）**O-20261001-2355 CEO 去节流令 §二常设生效**·每机自持连续系列·本波=引擎**第三十枚**·bm-b **第十三自有波**（W10/W11/W13/W16/W19/W22/W25/W28/W31/W34/W36/W38 后）。
- 引擎预跑=**本地版本冻结纪律**（SATURATION_ENGINE_LAW §1/§2·**非池化**预注册律）·12 分片（每片=A 带 2,000/12·B 带 200/12 逐片）·每片 workers=8（O-20261001-1332 CPU 纪律=片 8 workers·serial 等价语义）。
- 参数化合同（引擎冻结签）：runner 波参数一次性冻结（N1 generator port·N1_BANDS 单源 derive·engine_owner==bm-b 拒未发分片=去节流合同·per-wave prereg 冻结=引擎零缺发·冻结 commit 后引擎 per-tick 重读自燃·禁手工代烧）。
- CPU 纪律：CEO 令 09-28（O-2026-0930-1858 数值纪律窗内至 2026-10-08）·本批片 8 workers·26/32 核以内·后台优先级·离前台令即熄。

## §0.5 冻结前硬闸【存证·跑前】

- 冻结前闸：`python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W40_PREREG.md` 先执行·exit 0=放行后才冻结落行；fail-closed。
- 带位闸：`python results/_r531bmb_w40_band_gate.py`（本波 ADMIT 回执·预留面穷尽扫描机闸·r335 探针种子簇腿+r529 N3-R1 实际种子带腿+origin 号位空缺机验）exit 0=ADMIT。
- 人工预注册声明：**冻结设计**（设计=自家 core48 基线扩展·p2_calibration v1/v2 canon·W1 ext·W2..W39 已烧·从上扩带重复测量·零新主张·零新判线·零新定义·零新选漏·零未来数据·结果面不因本批改判据；如违·以硬闸为准）。

## §1 机制主张

- 零候选漏面：模板 §1 已选一（适用）——本批=§2 基线扩展测量（N1 null 基线·skill_line_v2 判线冻结消费面）·非注册新信号主张（裁决门=N/A）。

## §2 数据锚

- 基线=core48 bare codes·48 员装配=`p2_null_calibration_ext.load_core_at_cutoff`·v1 `load_core` 在 **2026-09-22 硬切换**=同律入档·单源=`p2_null_calibration.run_o
- evidence_cutoff=**2026-09-22**·同源生成·新批 JSON 顶层字段：`science_gates.cutoff_meta("2026-09-22")` 双写·缺字段=science_audit C2 VIOLATION口径。
- DATA_GAP 如实（core48 legacy 面不据指谎全）。

## §3 波段学设计

- **A 带**：j=0..1,999·entry rng seed=**123_004+j**（法典 §4 W40 A=123_004..125_003·算术顺延零跳位·ADMIT 回执在场）·基线 p=`BASELINE_P[(j//50)%2]`·v1 50-seed 交替纪律（分位纪律不变）。
- **B 带**：j=0..199·entry rng=**123_004+j**（与 A[j] 同源·入场分位纪律）·exit rng=**43_201+j**（法典 §4 W40 B=43_201..43_400·算术顺延零跳位·ADMIT 回执在场）。
- **出场轴显式声明（O-20261001-1108 反瞎搞令·TRIAL_LABOR_LAW §4）**：本批出场轴=**template_default（按设计测）**（本 null 基线的出场=自家 v1 引擎冻结的缺省出场栈（run_one 冻结内建），非 skill_line_v2 判线注册利害面）。
- 探针=烧前腿（W2 探针 95_002/95_003 验证推演已录）·本波=复用面·runner probe 腿=诚实 no-op·台账 +0·种子 +0。
- 确定性律：同 seed 烧录字节恒等（分片幂等·同片重烧=字节恒等覆写·跨片=分片边界确定性）·分片 nshards∈{1,2,4,12} 数科学恒等·spawn 面（进程 executor initializer 携面板·Windows spawn 重导入默认）。
- 种子带 disjoint 全门（selftest 强制）：W40 带 vs v1 在用带（10_000..10_099/20_000..20_019）·W1 ext（10_100..12_099/20_100..20_299）·W2..W39 已烧带（含 W35 113_004..115_003/W36 115_004..117_003/W37 117_004..119_003/W38 119_004..121_003/W39 121_004..123_003 与 42_401..42_600/42_601..42_800/43_001..43_200 B 带族）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际抽带 30_000..30_099·options_wave2 实际抽带 63_000..63_049·leg-3e 实际流避让。

## §4 研究/冻结面（结果从=字段段·非注记簿）

- 合并账=`canon 120 + 活链头 derive`（W1..W38 finalize 落全 81,520 实锚·W39 finalize 待落·本波 finalize 时活链头运行时组合=FAIL-CLOSED 诚实候 W39 件）·`skill_line_v2` **同 n_eff K-lift**·台账=活链头 derive（v2 台账·append_ledger 返回块持久化进 family summary 件=r509 幻影记账律）。
- 本波台账 finalize 走 `science_gates.append_ledger(batch_name="PERPETUAL-N1-W40", batch_trials=2200, file_name="results/perpetual_faces/n1_w40_results.json", ...)` 同律。
- 过/败门：单波判读态=N/A（本批=基线测量·无注册裁决面）·canon flip 面（治理提案面·K2200 同律·本波不做）。

## §5 跑前预测【锚定·写定跑前】

数据从实锚定·**W1..W38 finalize 落全**（累计池 81,520·W38=bm-b r530 同窗收官）·本波 §5 预测锚=**W38 finalize 实测值**（results/perpetual_faces/n1_w38_results.json 新近可得）：

1. W40-only mu 与累计池 merged mu（W38 finalize 实测锚 **−0.091622**）漂移 **|Δ|<0.02**（W2..W38 三十七面实测 mu 稳定先例；单波跨度）。
2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；锚 **0.244915**=W38 merged 实测）。
3. A 族 p95 与 W38 A 族 p95（**0.3119** 实测锚）差 **<0.05**（门校准注记沿 W5..W38 先例：结果知情校准面·仅作机器断裂侦测用·测量面零注册利害）。
4. K-lift 线移动幅度 **≤0.02**（累计池加深收窄 se_mu·线动=mu/sigma 微调面非质变——加深不必然抬线·W3..W38 先例（含 W35 +0.0005/W36 +0.0011/W37 +0.0003 三波连正·W38 −0.0001 如实报负）如实报正负；锚=W38 实测 K-lift −0.0001〔1.1575→1.1574·@n_eff 443,940〕）。

## §6 产物

- runner=`scripts/perpetual_faces_n1.py`（selftest/status/run --shard k --of 12 --wave 40/finalize --wave 40；probe/parity=W2 设计验证面·本波诚实 no-op）；点火面=`Tools/saturation_engine.py` tick（本机 bm-b 车道·schtasks 1-min·产物增长=唯一点火证据面）。
- 件：`results/p2cal_ext/n1_w40/shard-<k>-of-12.json`（append-only·确定性）＋ `results/perpetual_faces/n1_w40_results.json`（finalize 合并件·顶层 evidence_cutoff＋cutoff_meta＋audit 段＋K-lift 段·finalize 窗机械回填 §7/§8）。
- 引擎台账：git appender 批量 commit（本机 bm-b scripts 架构·烧录遥测=results/saturation_engine/{ledger,history,state}_bm-b.jsonl/json·孤儿对账腿 r522 同律）。
- 下游=skill_line_v2/g1_prime_v2 的 null 基线消费面（自动·判线共享库零手抄）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（占位·finalize 窗机械回填。）

## §8 批后复盘【必填·s7-T】

（占位·finalize 窗机械回填。）
