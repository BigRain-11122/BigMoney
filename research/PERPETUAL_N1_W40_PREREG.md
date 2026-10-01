<<<<<<< HEAD
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
=======
# PERPETUAL-N1-W40 预注册 · N1 nulls-deepening 波 40（never-dry 供给律常设步·第二十九枚引擎波·bm-a 第九枚自有引擎波）

> 令源：CEO 直令 **O-20261001-1410**（机队算力根因梳理与彻底解决令·SATURATION_ENGINE_LAW v1.0 随令立档）→ 建造票 **T-2026-10-01-141** s1（引擎核心·本机 bm-a 实例=tick 架构〔r535 实证：无常驻进程·每分钟新 python 进程重读活树=新波行天然可见·零重启自燃先例·免杀重启循环〕）→ **never-dry 供给律常设步**＋**O-20261001-2355 CEO 去节流令 §二执行**（「排好单子！开工！」·座位序列=违律 §1「恒不干」——每机自持连续系列·本机上一波收口→秒级物化下一波·禁等待·引擎活而核闲 >5min=红旗〔r549 实况=引擎活〔status exit 0·heartbeat 62s〕·本机上一波 **W35 已全生命周期收口**〔r545 冻结→12/12 烧录→r546 finalize 落账·K=74,920·账本 439,540 链性〕；**W39（bm-c r342）烧毕/烧录态在飞=注册在用面**——finalize 链序 W39 先于本波（r543 纪律消费面·序贯约束保序不保闲）·禁空转禁等 CEO 提醒〕）→ 面级法典=research/PERPETUAL_FACES.md v1.0 §4 台账 W40 展行（R250 one-step 律=冻结后禁再挑；本件零新挑——**W40 带从未指派**：A=123_004..125_003、B exit=43_201..43_400，两侧零跳位算术顺延 ADMIT 回执=results/_r548bma_w40_band_gate.py）。**本波=第二十九枚引擎波·bm-a 第九枚自有波（W12/W18/W21/W24/W27/W30/W33/W35 后第九枚）·波号=W39 公示认领后首个自由号**〔bm-c r342 W39 行落地=号位占用；去节流令=first-free-number 法·座位制同令废止——本波起草窗冻结前已 fetch 实核表尾无 W40 行=号位净空（r511 表尾锁律）〕（W10/W11/W13/W16/W19/W22/W25/W28/W31/W34/W36/W38=bm-b·W12/W18/W21/W24/W27/W30/W33/W35/W40=bm-a·W14/W17/W20/W23/W26/W29/W32/W37/W39=bm-c 先例合同同款）：engine_owner=bm-a（SATURATION_ENGINE_LAW §1 本地永续队列烧录·**不入池**·§2 免预认领；池面 supply 生成器对 engine_owner 波诚实拒绝物化=零跨机双烧面〔cmd_supply owner 跳过门·代码在场〕）。**收编注记（r314 收编律·如实披露）**：本波冻结窗由 r548 bm-a 起草（N1_BANDS/WAVE_CONFIGS 行+带闸工具已落工作树·01:3x 会话猝死·未 commit·state 轮号未加·两 ride commit 已先达 origin）→ r549 bm-a 收编窗完成冻结（本 prereg+法典 §4 行+selftest W40 腿+带闸实跑）=**同一冻结窗两段执行**，判据面零改动、带位零改动（收编面=工程续作非科学变更）。
> **续带注记（法典 §4 波40 行·两侧零跳位如实披露）**：①**A 面算术顺延零跳位**——A=123_004..125_003〔==W39 A 尾 123_003+1·步长逐字〕＝W39 行 W40+ 警示公示窗 CLEAN 逐位吻合（leg1 registry-derive 机证）；②**B 面算术顺延零跳位**——B=43_201..43_400〔==W39 B 尾 43_200+1·步长逐字〕＝W39 行 W40+ 警示公示窗 CLEAN 逐位吻合（同上·两侧独立裁定·零跳位面无 refusal facts=如实注记）。扫描面=pre-W40 三十七行 N1 带表（含 W36 行 115_004..117_003/42_201..42_400〔r528 bm-b·finalize 已落账 K=77,120〕·W37 行 117_004..119_003/42_401..42_600〔r341 bm-c·finalize 已落账 K=79,320〕·W38 行 119_004..121_003/42_601..42_800〔r529 bm-b·finalize 已落账 K=81,520·净链头 446,140〕·W39 行 121_004..123_003/43_001..43_200〔r342 bm-c·烧录在飞=注册在用面·带域不相交=异带共存 r531 律〕）＋W1 ext＋v1 在用带＋SEED_REGISTRY 全值〔含 bm-a r547 lowamp_p3 三新行〕＋**N3 已用种子带腿（N3-R1=70_000..70_005 全 6 值·MSG-183x r529 裁定行②强制腿）**＋**runner 设计探针种子簇 95_000..95_003（r335 发现腿·W26 起一切带闸回执强制携带）**＋N2/N4 设计探针保留点 40_000/40_001＋N2-W15 草案探针点 31_000/31_500/32_000＋lfc 实际流 30_000..30_099＋options_wave2 实际流 63_000..63_049〔leg-3e 实际流避让腿〕；**ADMIT 回执=results/_r548bma_w40_band_gate.py**〔r548 bm-a 起草·r549 收编窗实跑·leg0 三十七行+候选注册面校验+leg0b W39 行 W40+ 警示 prose 在场校验+leg1 registry-derive 算术窗==公示投影==候选+leg2 首净窗==候选双带〔顺延净空机证·零跳位面〕+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验〕。
> 性质=**测量加深面**（法典 §2：N1 对既有零假设基线按新种子带重 bootstrap 加深，产物=更深置信面〔p95/p99/mu/sigma/se_mu〕非新注册件，不入候选漏斗，不占语法消耗登记簿行；D6 同族相关性与闭合族对号约束=N2 专属，本面豁免如实注记）。
> 复用基=verbatim import 禁重写：`scripts/p2_null_calibration.py`（frozen v1 设计·run_one 引擎同源）＋ `scripts/p2_null_calibration_ext.py`（波扩展范式：_assemble/_entry_matrix/p_for/分片连续切片律/确定性重跑字节恒等）＋ `scripts/perpetual_faces_n1.py`（W2..W39 落地 runner 的 wave 参数化复用——同引擎同驱动同切片律，仅法典 §4 新带；引擎侧 `scripts/saturation_engine.py`〔本机 bm-a 实例·tick 架构 r535〕只做队列/点火/台账批处理面，runner 零改写）。

## §0 批件身份【必填·跑前】

- 批名=**PERPETUAL-N1-W40**。N=**2,200**（A 族 2,000＋B 族 200）；账本 **+2,200**（null trials 计数律=K2200 先例；prev=**届时活链头 derive 禁手抄**——起草窗实况：**W1..W38 finalize 已全部落账**〔净账本链头 **446,140**·W38=bm-b r530 收口 K=81,520；毛面=净面+LOWAMP-P1+P2 voids 已在链性 voids_applied 面〕）；**W39（bm-c）烧录态在飞=上游面**——本波 finalize 链序=W39→W40（finalize runtime FAIL-CLOSED compose registry 全键<40·W39 产品件到位前诚实等待·r543/r541 先例同款注记）；累计 null 池=**canon 120＋W1 ext 2,200＋W2..W14 2,200×13＋W16..W38 2,200×23（=落地基 81,520·W38 finalize 产品 n_values 实测机证）＋W39 在飞 2,200＋本波 2,200=86,120 投影**（法典 §5 跨波累计 N_eff 恒不重置；derive 禁手抄；W39 在飞披露=r545/r528/r539 prereg 同式先例）。
- 认领：never-dry 供给律常设步（TRIAL_LABOR_LAW §4·板空/池饿/无在飞判决批=默认续跑下一波）＋**O-20261001-2355 CEO 去节流令 §二执行**（每机自持连续系列·禁等待）；T-2026-10-01-141 s1 引擎线第二十九波·bm-a 第九枚自有波·波号=W39 认领后首个自由号（first-free-number 法·座位制已废）·lane-free；部门=dept:研究。
- 算力预算=**引擎本地队列烧录**（SATURATION_ENGINE_LAW §1/§2·**不入池**·免预认领）：12 分片（每片=A 族 2,000/12＋B 族 200/12 连续切片）；每片 workers=8（O-20261001-1332 多核律=逐片 8 workers·serial-vs-pool 字节恒等已证〔W2 parity r485/r488·W3..W39 多波 12/12 实烧重证〕）；本机并发帽=26//8=3 片（CEO 前台余量律·bm-a 核帽 26/32）；点火前置自检=引擎 PreIgnitionChecks（r316 律升格：本机数据前置件复验·缺件=跳过+上报·禁僵尸点火）；checkpoint=分片件本体（presence=done 证据；确定性重跑字节恒等=断点续跑语义）；台账=jsonl+引擎异步批量 git 交付（appender 批量 commit·本机 bm-a scripts 实例架构·烧录遥测在 results/saturation_engine/state_bm-a.json）。
- 物化条款（法典冻结签名行「runner 落地一批物化一批」）：本波=**引擎生成器物化**（N1 generator port：N1_BANDS 单源 derive·engine_owner==bm-a 波的未烧分片=本地队列项·per-wave prereg 在场=物化前置条件〔缺失=诚实拒绝物化，禁假供给〕）；池面 supply 生成器对 engine_owner 波拒绝物化（cmd_supply owner 跳过门·零双烧面）；**引擎实况注记（本机 bm-a 实例=tick 架构〔r535 律：无常驻进程·tick 每分钟新进程重读活树=冻结 commit 后新波行即点即见·免杀重启循环〕·点火验证唯一证据面=产物增长（results/p2cal_ext/n1_w40/ 分片计数增长·2 tick 窗·r325 律），state queue 面不信〕。
- CPU 余量律（CEO 令 09-28＋O-2026-0930-1858 假期修正案）：假期窗（至 2026-10-08·A股休市历）本机烧批解除 ~10% 余量默认——常权优先+满核·逐片 8 workers（核帽 26/32 保 CEO 前台）；引擎分离子进程烧完即退。

## §0.5 禁开方向硬闸【必填·跑前】

- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W40_PREREG.md` → exit 0=放行（回执入轮报告；fail-closed）。
- 人工预读结论：**零命中**——本波=对既有 core48 零假设基线（p2_calibration v1/v2 canon＋W1 ext＋W2..W39 落地）的种子带扩展重测，纯测量基础设施加深，零新机制宣称、零新候选面、零新信号定义、零前置条件类规则；禁向词面不在本件复述（机器闸为准·防否证模式词面自撞，W2..W39 同法先例）。

## §1 机制段

- 本面非候选漏斗面：模板 §1 机制四选一不适用（法典 §2 测量面豁免如实注记）。被加深对象=既有 G1' 技能线 null 基线（skill_line_v2 消费面）；本波不产生任何注册宣称，三态判定面=N/A。

## §2 数据与锚面

- 宇宙=core48 bare codes（48 员）；装载=`p2_null_calibration_ext.load_core_at_cutoff`（v1 `load_core` ＋ **2026-09-22 硬截断**=同窗律逐字）；引擎=`p2_null_calibration.run_one`（frozen v1 同源 import·禁旁路）；成本=FeeSchedule 单源（run_one 引擎内正典面）；断言=**48 员**（宇宙漂移=FAIL-CLOSED 拒烧·引擎 PreIgnitionChecks 前置复验）＋面板末行==2026-09-22（实跑双载断言）。
- evidence_cutoff=**2026-09-22**（同窗律；结果 JSON 顶层字段＋`science_gates.cutoff_meta("2026-09-22")` 双写，缺字段=science_audit C2 VIOLATION）。
- DATA_GAP 对号：不涉（core48 legacy 面板在仓覆盖全窗）。

## §3 方法学【冻结】

- **A 族**（j=0..1,999）：entry rng seed=**123_004+j**（法典 §4 W40 行 A=123_004..125_003·零跳位算术顺延·ADMIT 回执在场）；p=`BASELINE_P[(j//50)%2]`（v1 50-seed 块交替延续律逐字）；随机入场矩阵＋**引擎退出**（v1 设计逐字）。
- **B 族**（j=0..199）：entry rng=**123_004+j**（与 A[j] 同阵配对语义逐字）；exit rng=**43_201+j**（法典 §4 W40 行 B=43_201..43_400·零跳位算术顺延：==W39 B 尾 43_200+1·步长逐字·无带内点避让·两侧独立裁定如实注记）；p_exit=`P_EXIT=0.05`。
- **出场轴显式声明（O-20261001-1108 反瞎搞三道门·TRIAL_LABOR_LAW §4）**：本波出场轴=**template_default 按设计测**③——null 基线的被测对象即 v1 冻结设计的引擎缺省出场栈（run_one 引擎内正典面），与 skill_line_v2 被基线面同引擎同出场栈=测量恒等律（对拍面必须同栈才构成 null）；r301「非股票族禁裸缺省栈」教训对本面不适用=本面非判决面非策略面（三腿对账面=N/A·measurement-only 如实注记）。
- 探针=不另设（W2 探针 95_002/95_003 已证设计端到端；本波设计=W2..W39 逐字复用，runner probe 面=诚实 no-op；账本 +0）。
- 确定性律：同 seed 重跑字节恒等（分片件 append-only，重跑同片=字节恒等覆写幂等）；分片=连续切片零重叠零间隙（nshards∈{1,2,4,12} 切片数学自检腿）；spawn 面波配置随 executor initializer 携带（Windows spawn 重导入回默认波=物化前已防护，selftest 腿强制）。
- 种子带 disjoint 全律（selftest 强制）：W40 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W39 在用带（…W36 115_004..117_003/42_201..42_400〔波36·r528 bm-b·finalize 已落账 K=77,120=注册在用面〕·W37 117_004..119_003/42_401..42_600〔波37·r341 bm-c·finalize 已落账 K=79,320=注册在用面〕·W38 119_004..121_003/42_601..42_800〔波38·r529 bm-b·finalize 已落账 K=81,520=注册在用面〕·W39 121_004..123_003/43_001..43_200〔波39·r342 bm-c·烧录在飞=注册在用面〕逐字全套见 selftest leg 2 全表）、runner 设计探针种子簇（95_000..95_003·r335 发现腿·W26 起强制）、N3-R1 已用种子带（70_000..70_005·MSG-183x r529 强制腿）、SEED_REGISTRY 全值零交集（lfc_p1_screen 实际流 30_000..30_099 与 options_wave2 实际流 63_000..63_049 避让=leg 3e 实际流面·N2/N4 设计探针保留点 40_000/40_001 与 N2-W15 草案探针点 31_000/31_500/32_000 避让；本波机验 ADMIT 回执在场=r548 bm-a 起草·r549 收编窗实跑；selftest leg 2 全表 disjoint+leg N3-R1 腿+leg 探针簇腿+W38/W39 在用带腿）。

## §4 判据/读出面（测量面=数字读出，零注册门）

- 合并池=`canon 120 ＋ 已落账波值（W1..W38 已落 81,520 实锚·W38=bm-b r530 收口·derive 禁手抄）＋W39 在飞值＋ 本波 2,200`；`skill_line_v2` **同 n_eff K-lift**（旧线=届时空窗前态 derive·v2 归因律逐字·禁手抄 prev）；mu/sigma/p95/p99 新旧对照与 se_mu 收窄面逐列披露。
- 账本：finalize 步 `science_gates.append_ledger(batch_name="PERPETUAL-N1-W40", batch_trials=2200, file_name="results/perpetual_faces/n1_w40_results.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev；**guard 前持久化块入 family summary**=r509 append_ledger 幻影记账律·selftest 拒双 append 腿在场；**首 finalize 后禁盲重跑**=r538 重跑双计坑律·确需重跑先删未 commit 自产波件）。
- 无 pass/fail 门（测量面三态=N/A 如实）；本波数字为治理提案面素材（canon flip 不在本波——K2200 同律）。

## §5 跑前预测【必填·写死于跑前】

（起草窗实况注记：**W1..W38 finalize 已全部落账**〔净账本链头 446,140·W38=bm-b r530 收口 K=81,520〕——本波 §5 预测锚=**W38 finalize 实测值**〔results/perpetual_faces/n1_w38_results.json·origin 最新可得锚·单波跨度〕。锚滚动律披露：W39（bm-c）烧录在飞——若本波 finalize 窗前 W39 finalize 落账，本波 §5 判定锚按届时最新 finalize 实测值滚动执行并披露；W39 在飞未落=锚保持 W38 实测。）

1. W40-only mu 与累计池 merged mu（W38 finalize 实测锚 **−0.0916**）漂移 **|Δ|<0.02**（W2..W38 三十七面实测 mu 稳定先例；单波跨度）。
2. sigma 相对变化 **<±10%**（同设计同窗，纯抽样波动；锚 **0.2449**=W38 merged 实测）。
3. A 族 p95 与 W38 A 族 p95（**0.3119** 实测锚）差 **<0.05**（门校准注记沿 W5..W38 先例：结果知情校准面，仅作机器断裂侦测用，测量面零注册利害）。
4. K-lift 线移动幅度 **≤0.02**（累计池加深收窄 se_mu，线动=mu/sigma 微调面非质变——加深不必然抬线，W3..W38 先例（含 W35 +0.0005/W36 +0.0011/W37 +0.0003 三波连正·W38 −0.0001 首负如实报）如实报正负；锚=W38 实测 K-lift **−0.0001**〔1.1575→1.1574·@n_eff 443,940〕）。

## §6 产物

- runner=`scripts/perpetual_faces_n1.py`（selftest/status/run --shard k --of 12 --wave 40/finalize --wave 40；probe/parity=W2 设计验证面·本波诚实 no-op）；点火面=`scripts/saturation_engine.py`（本机 bm-a 实例·tick 架构 r535·本地队列→PreIgnitionChecks→分离点火→完成探测→台账批量·runner_args --lane engine 车道合同〔r523 律〕·**点火验证=2 tick 内产物增长（n1_w40/ 分片计数）=唯一点火证据〔r325 律·state queue 面不信·tick 架构免杀重启循环=r535 先例〕**）。
- 件：`results/p2cal_ext/n1_w40/shard-<k>-of-12.json`（append-only·确定性）＋ `results/perpetual_faces/n1_w40_results.json`（finalize 合并件·顶层 evidence_cutoff＋cutoff_meta＋audit 段＋K-lift 对照；**finalize 链序=W39 先行**〔pre-values 消费 registry 全键<40·W39 产品件到位前 FAIL-CLOSED 诚实等待·r543/r541 先例同款〕）。
- 引擎台账：jsonl+git appender 批量 commit（本机 bm-a scripts 实例架构·烧录遥测=results/saturation_engine/state_bm-a.json）；attrition 账本完整性 tripwire 覆盖本波产物件（r448 律）。
>>>>>>> 9f6ea8b2d (round 549: W40 FREEZE (29th engine wave, bm-a 9th own wave, own-series de-throttle law; bands A 123_004..125_003 / B 43_201..43_400 both zero-skip arithmetic; band gate ADMIT + banned gate ADMIT + compile green; r548 crash-salvage completion: prereg + canon row + selftest W40 leg; W38 anchor chain 446,140) + LOWAMP-P3 LA-EDGE legacy_base cell products delivery (r310) + engine lane files ride (r523) [bm-a])
- 下游=skill_line_v2/g1_prime_v2 的 null 基线消费面（自动·判线共享库零手抄）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（占位·finalize 窗机械回填。）

## §8 批后复盘【必填·s7-T】

（占位·finalize 窗机械回填。）
