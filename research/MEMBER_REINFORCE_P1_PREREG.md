# MEMBER_REINFORCE_P1_PREREG · 在册成员补强面批 P1（T-107 §4(b) 填弹梯 tranche-1(b) 供给 prereg）

> 状态：**跑前冻结**（2026-09-28 r180 bm-c · 与 F-04 MSG-20260928-2035＋SEED_REGISTRY 登记同 commit）；跑后只许回填 §7 占位节，禁改判据禁重跑。
> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节+G-ANCHOR-FACE 四元组 O-20260928-1712 律）；令源=O-20260928-1614 §一.4 填充阶梯②在册员补强面+O-20260928-1630 D4 供给目录+firm/TRIAL_LABOR_LAW §1 常供律（供给 prereq 债·audit v2.4.1 supply_floor ready=1<3 破线根因）；票=T-2026-09-28-107 §4(b)（bm-c r174 认领线）+Tools/fill_ladder_catalog.json `MEMBER-REINFORCE-P1` 条目（lane_owner=null·enqueue_gates=prereg_frozen+runner_exists）。
> 定位：**稳健性再派生批（robustness re-derivation）非新 α 搜索批**——零新策略发明（T-107 票面「ladder=DISPATCHER over existing law」）；批产物=在册成员证据面的四补强维（T-63 三卡 robustness dims 消费面+晋升门证据面）；robustness 面=注册证据的一致性复核非翻案面——判负成员零翻案通道（新证据=另立新 prereg，RANDOM_LARGE_SAMPLE_LAW §5）。
> 统摄律：research/BACKTEST_SCIENCE.md v2（判据唯一权威）+ firm/RANDOM_LARGE_SAMPLE_LAW v1.0 + BACKTEST_PLAN.md 三铁律 + research/COMPUTE_AUDIT.md 批件纪律。

## §0 批件身份。【跑前。】

- 批名/批号：**MEMBER_REINFORCE_P1**（在册成员补强面批·四面）。batch_trials = 6 成员 × 4 面 = **24 robustness cells** + 种子稳定性面 K=200 null × 3 seeds = **600 null draws** → 合计 **624**（append_ledger 照实计数·RANDOM_LARGE_SAMPLE_LAW 计数律）；robustness cells 非新 α 格（不与排除簿「已判精确核禁重跑」冲突——§3 释法）。
- 认领：F-04 先行已落（`fleet/inbox/MSG-20260928-2035-bmc-all-supply-prereg-freeze.md`）；任务引用=T-2026-09-28-107 §4(b)+fill_ladder_catalog tranche-1(b)。
- 部门归属：dept:策略（成员证据面）+ dept:研究（null/CSCV 派生面）joint。
- 算力预算：6 成员全史重放 ×4 面 = 分钟级池批（引擎确定性回放 W4 G-ANCHOR 同 Machinery 量级：6 员全史重放 ~秒级/员 ×3 成本面 + nulls 向量化）；>5min 入池（results/runnable_pool.json·O-2100 执行面分离）·checkpoint 幂等。

## §1 α 机制段。【四选一+论证·D6 门槛。】

- 本批零新 α 主张（robustness 再派生批定性）；各成员注册机制承继逐员注记：COMPOSITE-CE-01/02=**风险溢价**（低波+低振幅动量复合源价·注册件 §1 承继）、VOLATILITY-CE-01=**风险溢价**（低波源价）、ENGULF-CE-01/NEEDLE-DE-01/DROUGHT-CE-01=**行为偏差**（确认性行为反转·恐慌过度反应收割）。批级主张=**「在册成员注册证据在四补强面下稳健」**——被复核面=注册判据本身非新机制。
- **同族相关性准入（D6）**：本批零新函数零新格——批内两两 corr 矩阵照 derive（6 员日收益两两 max|corr| 描述性再披露·注册时点已过 0.7 门），robustness 面不设新准入门（无新入册主张）；数值与对照清单逐对列 §7 回填。

## §2 数据与面板。【跑前探针事实·冻结引用件 `results/_r180bmc_supply_prereg_probe_facts.json`（r180 实读）。】

- **成员名册（冻结时点 roster·prereg 定谳面）**：**6 员**——COMPOSITE-CE-01（entry=`top_n_rotation(composite, n=5, rebal_days=20)`·IS 0.4696/OOS 1.7479）/COMPOSITE-CE-02（`top_n_rotation(composite, n=8, rebal_days=20)`·0.5346/1.6392）/DROUGHT-CE-01（`vol_drought_reversal(vol_floor=0.55, drop_th=-0.05)`·0.5538/1.213）/ENGULF-CE-01（`engulf_reversal(drop_th=-0.05)`·0.6121/0.3835）/NEEDLE-DE-01（`needle_probe(drop_th=-0.05, shadow_pct=0.02)`·0.7781/0.4089）/VOLATILITY-CE-01（`low_vol_long(n=60, top_k=5, daily)`·1.0275/2.0568）——全 level=INTERN·evidence_cutoff=2026-09-22·锚常数=live.paper 锚定门常数逐位一致（smoke 25/25 同源）。**排除披露**：`firm/traders/_template.json`（占位模板件 id=TREND-001·entry=None·非注册员·构造性排除）；PROS-\* 22 员=PROSPECT 观察仓（O-2045 观察仓 0·构造性排除）。
- **名册面四元组**：`firm/traders/*.json` ＋ raw `json.load` 直读 ＋ 全史（各员注册时点起算）＋ 成员信号参数无预热窗（引擎入场序列按各员注册配置冻结）。**探针-锚同面断言**：runner 名册加载路径与本声明逐位比对（一面不等=配置错配 VOID·fail-closed 报「面错配」）。
- **行情面板四元组**：`data/daily/sh510300.csv` 等 core48 ＋ 引擎 T-22/T-34 血统 import-face（`load_core` 池面·与注册判据同 loader）＋ 2012-05-28 全史起算 ＋ 成员指标预热窗=各员注册配置（vol20 min_periods=20/med500 min_periods=500→首有效第 519 bar·W4 G-VOL 同面）。**锚面断言**：runner 重放各员注册配置经引擎默认路线，IS/OOS Sharpe==本节锚常数（G-ANCHOR 复现律·W4 同例；不等=配置错配 VOID 非数据腐坏）。
- **evidence_cutoff=2026-09-22**（P-5C 冻结口径 binding·与注册件/live.paper 锚定门常数同锚）；cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta("2026-09-22")`（缺字段=science_audit C2 VIOLATION）。
- 数据完备门（fail-closed·不过即 VOID 零产出）：G-PANEL core48 48/48 员截断后末行==2026-09-22；G-ROSTER 名册 re-derive==6 员且锚常数逐位一致；G-ANCHOR 各员 x1 重放 IS/OOS Sharpe==锚常数（±1e-9）。
- **beat-rate 虚拟起点面**：P-5C FROZEN_CENSUS（leg-L 6m=1,253/12m/24m 同册值·import `scripts/p5c_virtual_timepoint.py` 冻结口径禁重实现——与注册 beat_rate 同 census=可比性律·K≥1000 满足 RANDOM_LARGE_SAMPLE_LAW §1）。

## §3 方法学。【必填。】

- **面 F1 成本压测再派生**：6 员注册配置 × 成本面 {x1=13.041bp 单边（注册基线·锚复现面）, x2=26bp, x3=39bp} 全史重放——V1 legacy 成本族（注册判据同源；×2/×3 逐年稳定描述条款）。
- **面 F2 种子稳定性**：null 基线三种子重 derive——`default_rng([seed, k])` K=200 同掩码随机 null ×3 seeds（`member_reinforce_p1_null`=20294500/`_seedstab2`=20294600/`_seedstab3`=20294700·SEED_REGISTRY 已登记）；skill_line_v2 null 项逐种子 derive → G1' 判定逐种子复核。
- **面 F3 CSCV 补折**：PBO（`screening/pbo.py`）8 块（g2_registration_v2 家族标准面）＋**16 块补折面**（extra folds·稳定性对照）——两面 PBO 并列披露。
- **面 F4 政体段细分**：import `scripts/market_regime.py` 原子函数（同源断言零重实现·national_team_s3_review 同例）——v3 状态序列逐员逐段 beat_rate/Sharpe 派生（段聚合映射 GREEN→bull/YELLOW·CHOP→chop/ORANGE·RED→bear·映射冻结于此）。
- **滞后规则**：信号日 d 收盘信息集→d+1 开盘执行（T+1 因果律·注册面同律·全批禁未来数据）；robustness 面零参数调优零选优（面定义即冻结·批内零网格搜索）。
- **排除簿释法（已判精确核不冲突律）**：本批 x1 基线重放=**锚复现面**（G-ANCHOR 复现律·产出=断言不产出新判格）；x2/x3/种子/CSCV/政体段五面=**注册判据未覆盖的新 robustness 面**（注册件仅录 cost_x2 单面·W4 语法轴不含在册成员逐员四面证据）——四面+锚复现=合法再派生非重跑翻案。
- 账本：`science_gates.append_ledger("MEMBER_REINFORCE_P1", 624, "results/member_reinforce/MEMBER-REINFORCE-P1.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev）。

## §4 判据。【跑前写死，禁看结果调线。】

- **G1' v2（逐成本面）**：`science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=6, n_trades, n_entries)` 逐员逐成本面 {x1, x2} 判定（x3=披露面不计判定·逐年稳定描述条款）；skill_line_v2 输入逐列披露（passive_term/null_term/μ_null/σ_null 逐种子）。
- **F2 稳定性判读（冻结）**：3 种子 G1' 判定 **3/3 一致=seed-stable**；任一种子翻转=seed-unstable 旗（如实披露·不翻注册案）。
- **F3 稳定性判读（冻结）**：|PBO(8) − PBO(16)| ≤ 0.15 = fold-stable；超线=fold-unstable 旗。
- **F1 成本判读（冻结）**：x2 Sharpe_full ≥ 0 = x2-robust；x2 < 0 = x2-fragile 旗（描述性·注册案不动）；x3 面纯披露。
- **F4 政体段判读（冻结）**：逐员逐段 beat_rate vs 该员全史 beat_rate 差值披露（|Δ|>0.10=segment-tilt 旗·描述性）；无段 Sharpe<-0.5 段级红旗。
- **G2 注册资格 v2**：本批零注册主张（robustness 批）——G2 门不适用面如实声明（g2_registration_v2 调用=零·无新注册）；消费面=scorecard robustness dims+晋升门证据面（T-63）。
- 硬界设计三件套：本批无腐坏/健康检测类判线（robustness 复核面）；极端日先验=§5 承载（成员日收益面·2015-07/2016-01/2024-02-28/2025-04-07 七极端日家族面·W5-YANG 同锚）。

## §5 跑前预测。【写死于跑前·≥3 条。】

1. F1：6 员 x2 Sharpe_full ≥ 0 预测 **6/6**（注册面 cost_x2 先例：COMPOSITE-CE-01 x2 survive=true·0.5242/1.363 在册；低波/复合族成本敏感度低）——若 x2 面任员翻负=预测错（预期最弱面=ENGULF-CE-01 OOS 0.3835 薄边际员）。
2. F2：x1 边际薄员（ENGULF-CE-01 OOS 0.3835/NEEDLE-DE-01 0.4089）skill_line 距离窄→预测 **至少 1 员 3 种子判定出现不稳定读数**的风险在册；厚边际员（VOLATILITY-CE-01 IS 1.0275/OOS 2.0568）预测 3/3 stable。
3. F3：6 员族 PBO(8) 预测 ≤0.25（注册面 G2 已过线先例）·16 块补折预测 |ΔPBO|≤0.15。
4. F4：反转族三员（ENGULF/NEEDLE/DROUGHT）bear 段 beat_rate 预测高于其 bull 段（T-22 学派证据侧写+CEO O-2330 超跌反弹当前 regime 王定谳同向）；复合/低波两族 bull 段占优预期。
5. 极端日先验：七极端日家族日（2015-07-27/2016-01-04/2024-02-28/2025-04-07 崩盘日）成员日收益 |r| 可破 ±5%——段级披露非整批判负（硬界三件套 (b) 豁免单列承载）。

## §6 产物。

- runner `scripts/member_reinforce_p1.py`（**下轮建·selftest 先行**·梯 runner_exists 门届时自开）→ `results/member_reinforce/MEMBER-REINFORCE-P1.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+逐员四面+nulls 记录）+ scorecard robustness dims 消费面接线（strategy_scorecard.py 消费面=另行 slice·本批只产证据件）。
- 本冻结 commit 面：本件+SEED_REGISTRY 三新行+F-04 MSG+探针事实件。

## §7 跑后实证。【跑前必须为空——占位纪律：写数字即造假。】

（一次定稿；工程修复重跑须双跑留痕如实记账；确定性引擎产物写 bug 的合法重执行口径≠结果重跑。）

- **烧录回执**（r182 bm-c 收口·2026-09-28 21:06:58 runner 完成·回执 `results/member_reinforce/MEMBER-REINFORCE-P1.json`·账本 +624→320487·损耗账行 `results/gate_attrition.json` runner 自写 ts 21:04:28）：6 员×四面全烧（cutoff 2026-09-22·skill_line 0.4792 恒定）。
- **F1 x1**：3/6 g1-pass——COMPOSITE-CE-01 s=0.8416✓／COMPOSITE-CE-02 s=0.7854✓／VOLATILITY-CE-01 s=1.2578✓；三败员 DROUGHT 0.724／ENGULF 0.5539／NEEDLE 0.6624 点估计超线但 **CI95 下界负**（-0.0801／-0.2363／-0.1230）=不可证面（trades 73-150 全过 min 30）。
- **F1 x2**：0/6 g1-pass（0.4147~0.5902 vs line 0.4792·CI 门全败）——**双倍成本下全员 cost-fragile**＝x2 面最重诚实读数；符号面 6/6 Sharpe≥0（预测1 的字面判据成立）。
- **F2 种子稳定**：6/6 员 3 种子判定全一致（seed_stable=true 全表）。
- **F3 CSCV**：PBO(8)=0.3714（observe）+PBO(16)=0.5269（fail）·|ΔPBO|=0.1555>0.15＝**fold-unstable 旗如实**（6 员族对折块选择脆弱）。
- **F4 分段**：反转族三员 **bull>bear**（ENGULF 0.5842>0.5724／NEEDLE 0.5901>0.4690／DROUGHT 0.6198>0.5310）＝与预测反向；COMPOSITE-CE-01 bear 段 beat_rate 0.3724 segment_red_flag=true（本批唯一红旗·与 O-2330 regime 面一致）。
- **§5 预测对账**：预测1 x2 符号 6/6≥0——**对**（但 g1 门 0/6 为预测未覆盖的更强读数）；预测2 ≥1 员种子不稳定——**错**（全稳定）；预测3 PBO≤0.25+|Δ|≤0.15——**错**（0.3714/0.5269/0.1555 全破线）；预测4 反转族 bear>bull——**错**（反向）；预测5 极端日=回执单列承载如实。
- **消费面注记**：零注册主张（s4 冻结）；robustness dims → scorecard 消费接线=另行 slice（s6 冻结条款）；在册资格不受本批影响（本批=robustness 证据面非 admission 面）。

## §8 批后复盘。【必填·s7-T。】

- 预测对账（对/部分/错）＋门禁链损耗账（`results/gate_attrition.json` 追加一行）＋判线 v2 当批读数（skill_line_v2 数字逐种子）；回执入轮报告＋CODELY.md 行级追加。
