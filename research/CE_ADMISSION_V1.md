# CE_ADMISSION v1.0 — CE 正典层稳定优先准入规则（冻结件）

> 票：T-2026-09-25-54-P1 slice-1（策略部）。令链：O-20260925-1105（R3）← firm/STABLE_PROFIT_MODEL.md §3.1（「相关性帽具体数值归策略部 prereg 冻结」的受权落法）+ O-20260925-0857（两约束面）。
> 性质：**规则冻结件（governance prereg）**——非回测批、零 N_eff 入账、零引擎跑。冻结=本文件首 commit；**冻结先于一切按本规则进行的准入批**（票内 sequencing 条款）。适用对象=冻结 commit 起的一切**新**成员 CE 正典层准入；存量成员不追溯（§5.3）。
> 地位：**叠加条款，不替代不绕行**——候选先走完整既有门链（判定律预检→G1' v2→G2 注册资格→注册管线），全过后本规则两条款为准入门的增量面。任何条款与既有冻结判据冲突时，**从严者优先**。

## §1 既有门链底线（不可豁免清单·指针不复制）

1. 每候选每批一律走 `research/PREREG_TEMPLATE.md` 全节（§1 α 机制段四选一+同族 D6 检查**照旧必填**，本规则不免除）；
2. G1' v2 / G2 注册资格 v2 判据一律调 `science_gates` 共享库（禁手抄判线，T-02 6/7 纪律）；
3. 判负线禁翻案：期货 CTA×3 / P-A1 ETF 折溢价 / T-48 factor blend 等已判负线保持关闭，复活唯新预注册（house law）；
4. 反重复：与 T-33 三军架构车道（进攻/防空/震荡·替补席制）协同不重建，供给线消费 T-47 wave-6 / T-53 稳定范式族。

## §2 MW 条款——多窗口稳定性证据（冻结）

**证据面（必须全部在场，缺一=不可评审）**：候选须持有**全脸网格注册证据**——T-22/T54 站立口径 verbatim（`enumerate_starts`：warmup 252 / ≥24 员上市 / ≥126 bars 前瞻；单次 24m 跑切三窗 {6m=126, 12m=252, 24m=504}；被动=同窗上市成员 EW buy&hold；真实 T+1/成本/退出规则；census 门=枚举数对批内冻结 census，漂移=abort；anchor gate 逐成员复现，FAIL=剔除+披露）。覆盖面=**双轴（legacy core48 + deep 2013 growing-membership）×双面（base + x2=CostPatch(2.0) r82 口径）×三窗**，全普查零摘樱桃（T54 prereg §2/§3/§4/§5 逐字引用为测量正典）。

**门线（冻结·只读 legacy 轴 base 面；deep/x2 面=强制披露不设门）**：

| 窗 | 线 | 锚 |
|---|---|---|
| 6m | beat_rate ≥ **0.70** | P-5/P-5B 冻结口径**逐字**（O-20260924-1532；hr.py PROSPECT_PROMOTION_GATE；base 面作门 x2 披露=t24 promotion 既有约定，本规则照抄不扩） |
| 12m | beat_rate ≥ **0.50** | 新线：中位虚拟起点跑赢被动=「稳定」的定义地板（<0.50=中位起点输被动=无准入主张）；不沿用 0.70 因 12m/24m 无冻结先例、J4 0.70 线=装配层面非成员层面（混层=判线发明） |
| 24m | beat_rate ≥ **0.50** | 同上 |

三窗**同时**达标方过 MW 条款；任一窗破线=MW FAIL（照交不翻案）。deep 轴与 x2 面读数逐格披露于准入批报告（零门线，robustness 披露面）。

## §3 CORR 条款——相关性帽（冻结）

**帽值 = 0.50**（真两两 max \|corr\|，双面取 max，详下）。

**测量协议（零新机件·corr-watch §2 逐字引用）**：
- 序列=成员 **x1 sleeve 日收益**（注册配置逐字复现：`live.paper` SIGNAL_BUILDERS + ExitPatch/CostPatch，EW6 harness `E.member_run` import 禁重写——sleeve-tag 先例）；
- 对象=候选 vs **CE 正典层在册全员**（冻结时点名册：COMPOSITE-CE-01 / COMPOSITE-CE-02 / DROUGHT-CE-01 / ENGULF-CE-01 / NEEDLE-DE-01 / VOLATILITY-CE-01，`firm/traders/*.json` 非下划线非 PROS-* 员；冻结后新准入员自动入点名册）**＋同批全部候选**（批内两两）；
- 面=**full-RW**（两序列各截断至自身注册 evidence_cutoff 后的公共重叠窗）**＋ IS2**（≥2025-01-01，IV6 §3 冻结段面）——**两面各自成对取 max \|corr\|，再总取 max**；
- 每面腿须 ≥ **MIN_PERIODS=60** 根公共 bar（corr-watch FL 先例）；任一面腿 <60 bar ⇒ 该候选**准入 DEFERRED**（诚实等待数据，非拒收非准入），披露所缺面；
- 判定：总 max \|corr\| **< 0.50** ⇒ CORR PASS；≥ 0.50 ⇒ **CORR 拒收**（数值+逐对清单全披露，D6 拒收语义同款）；
- 批内两两 ≥0.50 ⇒ 确定性去重：胜者=legacy base pooled beat_rate_6m 高者，平手=成员 id 字典序小者；败者=CORR 拒收（复活唯新预注册）。

**帽值锚链（四锚·全为在档事实非本批结果）**：
1. **<0.30** = S 级「独立分散价值」满分目标（firm/STRATEGY_EVALUATION.md §2 维5）——帽值留改善空间、准入线不占满目标线；
2. **0.50** = 本帽：低于 corr-watch §7 已档「尾段 0.5+ =独立引擎数下降先兆（P3『1.5 个真独立引擎』担忧新候选证据链）」预警带下沿 ⇒ **被准入员结构性不入侵蚀带**；
3. **≥0.70** = D6 机制硬拒收（PREREG_TEMPLATE §1）+ corr-watch W1 RED——本帽严于 D6：池级正典准入须严于供给级反重复门（产品层>供应链层次序）；
4. **0.87** = P3 反面典型（research/portfolio_report.md：composite 双员 OOS 相关 0.87，三员公司真独立风险引擎仅 1.5 个；CEO 令原文点名）——帽值距反例 0.37 决定性余量。

## §4 漏斗与披露（冻结）

1. **漏斗双列**：每准入批报告双列漏斗（进入口径 | 过闸口径）逐级点名——considered → 判定律预检 → G1'v2 → G2 → MW → CORR → admitted（票内「breadth expansion != admission inflation」条款的机械化）；
2. **N_eff 披露**：批后披露正典池全 pairwise 矩阵（full-RW+IS2 双面）、平均 pairwise、等波动 N_eff 估算 `M/(1+(M-1)·ρ̄_avg)`——**描述性零门线**；「真独立引擎 ≥4」= 2026-12 季度深审呈报读数（总纲 §七.4），非本规则门；
3. **PROSPECT 层两两**：对 PROS 预备层的 pairwise 作描述性披露（W-GRID 全池消费面相关），其准入治理归 T-24 promotion 管线，非本规则。

## §5 诚实边界（冻结）

1. **不追溯**：本规则约束冻结 commit 起的新准入；存量 6 员保持注册态不重判；
2. **存量反例披露**：COMPOSITE-CE-01|02 IS2 pairwise 0.8687（corr-watch 首跑 W2 ORANGE 在档）=本规则所要防的反面典型**已在池内**——留驻 corr-watch W1/W2 月更监控盯防；退役/权重帽=独立面（CEO/复审呈报域），本规则不开退役门；
3. **帽值不可经批移动**：0.50/0.70/0.50 与 0.50 帽冻结后，改线唯「外部证据+新预注册+CEO 批」路径（总纲 §六.1 同款纪律）；若连续多批出现「唯 CORR 腿拒收」的供给 starvation 证据，如实呈 CEO 裁定，禁自行放宽；
4. MW 证据面**测量批**（如 T54 类网格批）零判据零准入——测量与判定恒分批（T54 prereg 判例）。

## §6 准入批协议（冻结）

每个按本规则运行的准入批：F-04 先行（fleet/inbox/ MSG 认领声明防双机撞车）→ PREREG_TEMPLATE 全节 prereg 跑前冻结（§1 机制段照填；§2 面板/cutoff；§4 判据调共享库+本规则 §2/§3 两条款写死入 prereg；§5 跑前预测含「极端日先验」）→ 网格测量批/证据包按需另冻（测量与判定分批）→ 判定跑 → 漏斗双列+逐对清单+N_eff 披露落盘 → 账本实际计数 → 负判定照交禁翻案。注册新员=注册管线既有面（evidence_cutoff+接线+smoke 锚定门），本规则零新增接线。

## §7 跑前预测（冻结时写死·批后对账）

1. **近期漏斗以损耗为主**：J-1 先例 legacy 6m 面 0/22 ≥0.70 ⇒ 首批按本规则跑出的常态读数=多数候选 MW FAIL，诚实负为预期首读而非规则失效信号；
2. **CORR 腿双面不对称**：IS2 腿（2025+ 政体趋同窗）预期拒收多于 full-RW 腿——政体收敛候选（同因子族/同政体暴露）预期 full-RW 过而 IS2 破 0.50（P3 全期 0.36→OOS 0.58 抬升形态的准入面重演）；composite 族加权变体预期 0.71-0.87 面直接拒收（FACTOR_BLEND v1 教训）；
3. **N_eff 首读 <4**：当前真独立引擎 ~1.5（P3）+ 存量 0.87 对拖累 ⇒ ≥4 目标需多次净准入累积，单批不可期；2026-12 深审若 N_eff 仍 <4，如实呈升/平/降+归因（总纲 §七.4「升≠达标」）；
4. **极端先验**：共享主政体暴露的供给族（如全部牛市动量族同窗入场）即使机制叙述互异，IS2 两两仍可能齐破 0.50——双面 max 设计即为此类「结构性趋同」预设绊线；此为规则预期行为非误报。

## §8 占位纪律（冻结时为空·批后回填）

- **CE-ADMISSION-B1（2026-09-25 15:06·T-54 s3·bm-b·判定批零新引擎）**：候选=PROSPECT 池 22 员（唯一持有 §2 全脸网格证据面·T54 测量件复读）。漏斗双列 considered 22→precheck 22→G1'v2 3（DUCK-01/DUCK-CE-01/VOB-CE-01）→G2 0（cost_x3 0/22 在档）→MW 0/0→CORR 0/0→**admitted 0**。MW 描述读：max legacy base 6m=0.5876 ⇒ 0/22 过线（§7.1 预测态）；CORR 腿未触发；N_eff 描述面=2.6225（ρ̄_avg 0.2576·M=6）。账本+0（判定批零新试验）；gate_attrition +1 行。prereg=`research/CE_ADMISSION_INTAKE_B1_PREREG.md`（113f9400 跑前冻结）+结果=`results/ce_admission/CE_ADMISSION_B1.json`+脚本=`scripts/ce_admission_intake.py`（selftest 6/6）。预测对账 4/4 对；零翻案零改线。

## §9 复盘钩子

- 每准入批 §8 追加+轮报告回执；预测对账（§7 vs 实跑）入批后复盘；本规则自身修订=立法废法路径（RULES §7 七天否决窗）+改线纪律（§5.3）。
