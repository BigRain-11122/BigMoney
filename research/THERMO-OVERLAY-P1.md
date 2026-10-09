# THERMO-OVERLAY-P1 · 游资情绪温度计风险开关 overlay 判决批预注册

> 模板：research/PREREG_TEMPLATE.md（2026-09-23 入库版）· 令源 O-20261009-2340 §二.4 + T-2026-10-10-181（GM 署名票·bm-a r938 认领）· 消费面指名：C1 政体门情绪臂互证 / 打板溢价供给线参照（§2b）。
> 状态：**FROZEN**（bm-a r938 跑前 commit 冻结；跑后只许回填 §7/§8，禁改判据禁重跑）。

## §0 批件身份【跑前】

- **批名**：THERMO-OVERLAY-P1；**批内格数 = 6 实格 + 6×200 null = 1,206**（每格计入 N_eff，扩容即买单）。
- **认领**：F-04 先行——本件与 fleet/inbox/MSG-2026-10-10-0335-bma 同 commit 声明；任务板引用：T-2026-10-10-181-P1（status=claimed, claimed_by=bm-a r938, commit dae0a53e9 票锁在先）。
- **部门归属**：dept:研究（研究部·情绪/政体供给线）。
- **算力预算**：runner 单机烧批预估 ~10-25 分钟（bars 面板一遍式 EW 收益构建 + 6 格 overlay 重放 + 1,200 null 位移重放·纯向量化）；>10min 批入池后台化，lane_owner=**bm-a**（Money02 bars 面板 bm-a 宿主·数据本地性律·R31 车道判例：他机无面板=探针 fail-closed 拒烧）；批报告必带 audit 段。

## §0.5 禁开方向硬闸【跑前·D-20260930-41 §1.2】

- 闸实测：`python Tools/banned_direction_gate.py --prereg research/THERMO-OVERLAY-P1.md`（同 commit 收据入 §6）。
- **命中编号：BAN-05**（Market-temperature / breadth timing as a precondition）。
- **例外类型：`new_mechanism`（主）+ `new_data`（辅）**。
- **原否证不可能看见的东西**：BAN-05 原否证面=「低量反转基策略上的**入场确认前置**」（breadth>0.5/0.3、EW>MA200 三滤·ETF 世代截面数据·全部比无前置更差·机制=确认滤除反转信号的最佳入场）；本批测的是**反方向机制**——默认满仓、**仅在恐慌/过热极端日离场**的 de-risking 风险开关（BAN-05 三滤全部是「市场够暖才许进」的入场门，从未测过「极端时离场」方向）；且原否证用 breadth/MA200 数据，**看不见**本批 Money02 全宇宙 5,222 只涨跌停微观结构面板（1996-12-16→2026-09-22 三十年全窗·含全部 20 个实测千股跌停日：2015 股灾/2016 熔断/2018 贸易战尾/2020 疫情/2024-02 微盘/2025-04 关税）——涨跌停磁吸/流动性挤压机制在原否证的数据面（ETF 截面 MA 类 breadth）上**不存在观测量**。科学效力归 science_gates 判据链+本批判决，本节例外=入场券非结论。

## §1 α 机制段【D6】

- [x] **结构性**：涨跌停制度磁吸效应+流动性挤压——恐慌日（跌停潮）卖方因跌停**无法成交**形成未执行卖压悬挂，价格发现被制度性延迟 → 次日延续下跌是制度产物（非行为噪声）；过热日（连板高度极端）则反向为追买拥挤+监管降温风险。**由谁付出代价**：恐慌日被强制卖出的参与者（融资平仓/赎回强制/质押盘）——他们卖不出去、次日继续承担延续损失；overlay 持币避开该流动性挤压段。
- **散户凭什么赢【§1.2】**：**制度**——该信号纯收盘公开数据零速度零数据门槛；散户赢面=「无强制卖出约束」（机构在恐慌日面临赎回/强平**必须**在跌停板上排队，散户可 t+1 自主离场）+涨跌停制度对所有人的磁吸是同一制度租金，谁先离场谁免交。
- **同族相关性准入检查【D6】**：新 family_key=thermo_overlay_p1（在册零成员·intake 时 engine 面重算 max|corr| vs 在册交易员全部成员+在队函数，日收益口径 cutoff-truncated-first）；**数值与对照清单**：intake 步实算逐对披露；`max|corr| ≥ 0.7` → 拒收。预披露风险面：恐慌段与 REGIME 类 sleeve 在崩盘窗重叠度非零——以实算为准，诚实披露。

## §2 数据与面板【跑前探针事实·非结果】

- **宇宙**：Money02/data/bars 5,222 只 parquet（沪深主板+创业板+科创板·**无北交所·panel as-is**）；**幸存者面诚实披露**：面板零退市股（retail-quant-conclusions #3）→ EW 宇宙绝对收益水平被幸存者偏差抬高，**本批判决面=同宇宙 overlay vs passive 差分**（两者同受偏差·差分保留），绝对水平不作主张。
- **数据锚面四元组**：
  - 面 1（状态轴）：`results/regime_thermo/thermo_daily.csv` / `pd.read_csv`（raw 直读） / 1996-12-16 起算 / 零预热（计数面）——探针实锚：**7,216 行、首 1996-12-16、末 2026-09-22、13 列**（REGIME_THERMO_V1 白皮书所记 7,257 为写作近似·以 CSV 实测为准）。
  - 面 2（收益面）：`Money02/data/bars/*.parquet`（5,222 件·探针实锚）/ `pd.read_parquet(fp, columns=["date","close","high","preclose"])` / 1996-12-16 起算（VALID_FROM）/ 预热=上市首日 preclose NaN 自动出局（零额外窗）。
  - **探针-锚同面断言**：runner 探针实载路径与上述声明路径逐位比对，一面不等=面错配 VOID fail-closed 拒烧。
- **窗口与 evidence_cutoff**：一律截断 **2026-09-22（P-5C 冻结面·与机队全线一致）**；cutoff 后新 bar 锁定不得回流；结果 JSON 顶层必须带 `science_gates.cutoff_meta` 字段。
- **数据完备门（不过禁跑）**：面 1 行数==7,216 且首末日期逐位相等；面 2 parquet 件数==5222；两面板日期轴恒等断言（thermo_daily 由 bars 面板 derive·逐日对齐）。
- **冻结判决格掩码边际探针事实（跑前实锚·非结果）**（n_sealed_down=恐慌轴/max_height=连板高度轴·格点=cell lattice 非任何交易形态）：

| 格 | 规则（off(t) 定义） | off 天数 | 占比 | off 段数（=entries） |
|---|---|---|---|---|
| P100 | n_sealed_down(t) ≥ 100 | 145 | 2.0% | 109 |
| P500 | n_sealed_down(t) ≥ 500 | 46 | 0.64% | 36 |
| P1000 | n_sealed_down(t) ≥ 1000 | 20 | 0.28% | 17 |
| H12 | max_height(t) ≥ 12 | 1,019 | 14.1% | 166 |
| H16 | max_height(t) ≥ 16 | 443 | 6.1% | 91 |
| PH | [n_sealed_down(t) ≥ 500] OR [max_height(t) ≥ 12] | 1,050 | 14.6% | 183 |

- **种子选位律合规**：null 基点 **94,500**（94_001..94_999 净袋内·禁爬 95_000+ 律合规·与在位 94100/94200/94300 disjoint·extent-aware 带隙法 _seed_band_check 验证）。

## §2b 打板溢价供给线年代分层参照面【描述·零判据·外源目录 #2 消费】

- 冻结锚（REGIME_THERMO_V1 白皮书+results/regime_thermo/thermo_summary.json）：年均封住率 **2005≈21.4% → 2026≈14.6%**（三十单调下行带波动）；连板高度中枢 2015 前后 ≈11 → 2023-2026 ≈5-7。
- **供给线消费含义（描述面）**：打板溢价类任何后续预注册的历史参照收益段**必须按年代分层**——2015 世代参照不可外推至 2020+ 世代（封住率-7pp+高度中枢-4~6 的结构迁移=外推即数据窥探）；本节为登记参照非判据。

## §3 方法学【冻结】

- **底层收益面**：r_u(t) = 全宇宙等权日收益 = mean over valid rows of (close/preclose − 1)，valid=preclose 非 NaN **且 preclose ≥ 1.0**（仙股行剔除·与温度计构建器同守卫）；as-is 面无最低成分数门（1996-1997 早年成分少·如实披露）。
- **overlay 执行（T+1 滞后·禁未来数据）**：state 由 t 日收盘数据算出 → **pos(t+1) = 0 若 off(t) 否则 1**；收益归属 r_ov(t+1) = pos(t+1)·r_u(t+1) − c·1[pos(t+1)≠pos(t)]；t0 起始满仓无入场成本；c=13bp（0.0013/边·V1 legacy 压测口径）。
- **成本口径【CN-C7 申报】**：单一可比数字=**13 bp/边 ×2 = 26 bp/往返**（与面 A ETF 26.082 bp/往返同量级·V1 legacy）；**×2 成本压测腿**（26 bp/边·52 bp/往返）逐年稳定性披露；股票面逐名实施时按 `knowledge/rules.py fee_schedule_for` 前缀路由（印花税仅卖边 5bp+过户费双边 0.1bp·¥5 最低佣金临界=名义 ¥20,000·engine 派生披露非手抄）。
- **null 对照（K=200 同构 null）**：每格 **circular random shift** 掩码 null——null_i(t) = off((t + s_i) mod T)，s_i ~ Uniform{1..T−1}（保序保边际：off 占比/off 段长分布/自相关全保留·仅随机化相位=「温度计时点是否携带信息」的正法 null）；K=200，seed=**94,500+i**（i=0..199·thermo_overlay_p1_nulls 基点 94500 同 commit 登记 SEED_REGISTRY）；被动基线=无 overlay 宇宙持有（pos≡1）。
- **出场轴显式门【TRIAL_LABOR_LAW §4 三选一】**：**②持有到底声明**——overlay 即唯一风险出场机制；runner **显式禁用引擎缺省出场栈**（无止损/无超时/无其他出场叠加）·代码层硬断言。
- **账本**：`science_gates.append_ledger(batch_name='THERMO-OVERLAY-P1', batch_trials=1206, file_name='thermo_overlay_p1/thermo_overlay_p1_results.json', evidence_cutoff='2026-09-22')`（dict schema·runner 嵌入 payload['trials_ledger']·禁手抄 prev）。
- **闭合族对号【M3】**：family_key=**thermo_overlay_p1**——`science_gates.CLOSED_FAMILIES` 不在册=open 照跑（closed_family_check 实跑收据入 §6）。

## §4 判据【跑前写死·禁看结果调线】

- **G1' v2**（逐格）：`science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=6, n_trades=2×off段数, n_entries=off段数, null_pool=本格 200-null Sharpe 族, passive_override=宇宙被动 Sharpe, min_trades=30)`——全期 Sharpe > skill_line_v2（max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))·**本批自校准 null 族**）且平稳 bootstrap CI 下界>0 且 entries≥30（F6 双口径·P1000 格 17 段<30 预测性披露于 §5·如实判）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2**：`science_gates.g2_registration_v2(g1_pass, dsr, pbo)`——G1' 过线 **且** DSR≥0.95（deflated_sharpe_ratio 原始收益跑·禁 dsr_from_stats 充数）**且** 家族 PBO≤0.25（screening/pbo.py CSCV 8 块·同族格点=6 格）。
- **新因子 t 面【M1】**：策略面无直接 t → `science_gates.t_from_sharpe(SR_ann, T=n_days)` 派生 → `science_gates.m1_t_value_gate(t, hurdle=3.0, claim_class='new_factor')`；缺面=missing_input 拒收非放行。
- **描述性条款（批级披露不替代门）**：年化>0、OOS 双正、回撤≥-35%、无崩年、26bp/52bp 成本压测逐年稳定。
- 本批判线为收益判决面（非数据腐坏检测面）——硬界三件套适用性=不适用主判（无 max 硬界判线）；极端日先验入 §5(c)。
- **全起点分布【§1.3 D-41】**：月度虚拟起点族（1997-01 起每月首个交易日至 2026-06·~354 起点）逐格计算起点起 Sharpe——§8 报最好/最坏/p25/中位/p75+滚动 3/5/10 年最差；只报单一起点=结论无效。

## §5 跑前预测【写死于跑前·跑后对账】

1. **P 轴主向预测（方向=部分确信）**：恐慌日次日宇宙 EW 收益显著负偏（磁吸延续机制）——P100/P500 格 overlay Sharpe 高于被动、回撤显著收窄；**但恐慌日同时含 V 型底反弹**（2015-07-09 类），Sharpe 改善量级预测为**中等**（非碾压），回撤/尾部改善>Sharpe 改善。
2. **H 轴预测（方向=不确定·诚实双向）**：H12 格离场 14.1% 天数含全部情绪高潮段——若题材延续主导则错失趋势（Sharpe 降）；若高度极端后监管降温/拥挤崩塌主导则改善；**预测=H16（6.1% 离场·更接近极端顶定义）优于 H12**，但两格判负可能性如实申报非零。
3. **P1000 格预测=entries 17<30 → F6 判不 eligible**（千股跌停 20 日太少·预测性披露非跑后得知）；PH 格≈H12 主导（H12 覆盖 P500 超集大部）→与 H12 高相关，家族 PBO 风格面如实披露。
4. **门槛读数预测**：skill_line_v2（自校准 null）预测 ≈ max(被动+0.10, μ_null+σ_null·√(2 ln 1206))——null 族保结构保边际、仅随机相位 → μ_null≈被动量级、σ_null 由恐慌窗位移方差驱动；预测 6 格中 **0-2 格**过 G1'（多格判负为诚实预期·本批=机制判决批非注册冲刺批）。
5. **极端日先验【(c)】**：2015-08-24（2,015 家跌停·EW 预测 ≈ −9% 量级单日）/2016-01-04（熔断·≈−7%）/2020-02-03（2,938 家·≈−8%）/2025-04-07（2,770 家·≈−8%）——P 轴掩码的收益端极值；EW 面单日 |r| 大于任何 ETF 面（全宇宙跌停日磁吸）=预期内形态非数据腐坏。

## §6 产物【跑前占位】

- runner：`scripts/thermo_overlay_p1.py`（subcommands: run/probe/selftest——**下一切片交付**；selftest=离线自检；lane 车道护栏=bm-a 宿主·他机探针 fail-closed）。
- 结果：`results/thermo_overlay_p1/thermo_overlay_p1_results.json`（顶层 evidence_cutoff 必带）+ `cells_*.csv` + nulls 明细；批报告必带 audit 段。
- 跑前收据（同 freeze commit）：banned_direction_gate 判决 JSON + closed_family_check 收据 + 掩码边际探针实锚（§2 表）+ SEED_REGISTRY 登记（thermo_overlay_p1_nulls=94500）。

## §7 跑后实证【跑前必须为空——写数字即造假】

机器回填 bm-a 2026-10-10 05:2x·一次定稿（跑前本节为空·冻结 commit 5c332d987 先于烧录）

- **烧录事实**：results/thermo_overlay_p1/（8 件·burn 完成 2026-10-10 05:02:41·runtime 262.86s·6 workers house ProcessPool r941 改造·audit.engine_used=false·审计 fresh_ledger_append=true）；evidence_cutoff 2026-09-22；面板面=冻结面逐项恒等（face1 7,216 行 1996-12-16..2026-09-22 · face2 5,222 parquet 16,112,689 有效行 · 掩码边际逐格恒等 145/46/20 · 1019/443/1050）。
- **被动基线**（宇宙 EW 持有·零成本）：Sharpe 0.6035 · 年化 17.93% · maxdd -1.1656。
- **判决面**（x1=13.041bp/边·x2=26.082bp/边应力·x2 全格 Sharpe 仅微降）：

| 格 | 离场日/段 | entries | Sharpe(x1) | skill_line | μ_null(σ_null) | G1' line_ok | M1 t(≥3.0) | D6 | DSR |
|---|---|---|---|---|---|---|---|---|---|
| P100 | 145/109 | 109 | 0.5949 | 0.7138 | 0.5649(0.0285) | ✗ | 3.18 ✓ | 0.3086 | 0.046 |
| P500 | 46/36 | 36 | 0.6377 | 0.7035 | 0.5895(0.0157) | ✗ | 3.41 ✓ | 0.3105 | 0.072 |
| P1000 | 20/17 | 17 | 0.6509 | 0.7035 | 0.5956(0.0092) | ✗ | 3.48 ✓ | 0.3133 | 0.082 |
| H12 | 1019/166 | 166 | 0.5309 | 0.9230 | 0.4933(0.0822) | ✗ | 2.84 ✗ | 0.3135 | 0.022 |
| H16 | 443/91 | 91 | 0.5809 | 0.8094 | 0.5530(0.0490) | ✗ | 3.11 ✓ | 0.3168 | 0.039 |
| PH | 1050/183 | 183 | 0.5448 | 0.9051 | 0.4854(0.0803) | ✗ | 2.92 ✗ | 0.2917 | 0.026 |

- **全链判决：0/6 格过全链**——G1' line_ok 六格全 False（P 轴格 skill_line==passive_term 0.7035=对被动零增量；H 轴格 line 高于被动但低于 μ_null+σ_null·√(2 ln 862,151) 技能线）；G2 eligible_v2 全 False；P1000 另有 F6 双交易门判负（entries 17<30）；D6 零拒收（max|corr|≤0.3168 全部 <0.70 拒收线）；PBO=0.4（observe 档）；best=P1000（Sharpe 0.6509·+0.047 vs 被动·maxdd 与被动恒等 -1.1656=回撤零改善·P100 回撤反更深 -1.3042）。
- **描述面**：6 格全期年化正·两半子面均正（IS 面·2025-01-01+ 段=烧录 IS2·无 OOS 宣称）；maxdd_ok 六格全 False；crash_year 全 True（年亏损面存在·掩码不消灭深回撤年）。
- **虚拟起点分布**（354 起点 1997-01-02..2026-06-01·逐格 best/p25/median/p75/worst）：P100 1.116/0.432/0.602/0.696/-0.776 · P500 1.339/0.566/0.657/0.750/-0.498 · P1000 1.347/0.605/0.675/0.777/-0.498 · H12 1.369/0.527/0.580/0.652/-0.498 · H16 1.373/0.546/0.608/0.686/-0.498 · PH 1.354/0.512/0.570/0.671/-0.498；滚动最差 3y 六格同量级 -1.20（离场掩码不救深回撤窗）。
- **极值日实锚**（cells_*.csv r_u 复查）：P1000 离场 20 日含 2025-04-07 -11.83% / 2015-08-24 -9.75% / 2015-08-25 -9.35% / 2015-06-26 -9.24% / 2016-01-07 -9.21%。

## §8 批后复盘【跑后回填】

机器回填 bm-a 2026-10-10 05:2x

- **预测对账（§5 冻结面 vs 实跑·负结果照报）**：① §5.4「0-2 格过 G1'·多格判负=诚实预期」→ 实跑 **0/6 过 G1'** ✓ 预测命中区间（机制判决批结论=温度计离场掩码在宇宙 EW 面不产生超保结构零假设的技能线增量）；② §5.1 P 轴「Sharpe 改善中等·回撤改善>Sharpe 改善」→ 实跑 Sharpe 最佳仅 +0.047、回撤零改善（P1000 与被动恒等·P100 反更深）——**改善侧双判负·预测乐观侧被否证**；③ §5.2「H16 优于 H12」→ M1 t 3.11 vs 2.84 + Sharpe 0.581 vs 0.531 方向确认 ✓·但两格均 G1' 判负；④ §5.3「P1000 entries 17<30 → F6 判不 eligible」→ **逐字命中**（17 entries）✓；⑤ §5.5 极端日 EW 面 → 2015-08-24 实测 -9.75%（预测 ≈-9% ✓）·2016-01-04 -8.95%（预测 ≈-7%·实际更深）·2025-04-07 -11.83%（预测 ≈-8%·实际更深）✓·离场日集与冻结掩码边际恒等。
- **门禁链损耗账**：`results/gate_attrition.json` 已由 runner 终态追加 THERMO-OVERLAY-P1 judgment 行（ts 2026-10-10 05:02:41 · cells_ledger_delta 1,206 · ledger_total_after 862,151 · g1_pass_cells=[] · m1_pass_cells=[P100,P500,P1000,H16] · full_chain_cells=[]）；attrition_ledger_guard 4 台账扫描 CLEAN。
- **试验量归因**：本批新增 **1,206 试验**（6 判决格 + 6×K200 保结构循环位移零假设·种子 94500+i 单步注册 R250）·单批>100 归因一句话=「温度计消费面 P6 令的唯一判决步·6 格机制判决格全量判决非挑格注册」；ledger 860,945 → 862,151（LOWAMP-P1/P2 双 void 4,016 已扣口径·与 W203 finalize 同一 ledger_head）。
- **判后去向**：温度计 overlay 作为**收益增强机制**在宇宙 EW 面判负（家族面 `thermo_overlay_p1` 保持 open·机制判决批无注册面动作）；温度计本体 REGIME_THERMO_V1 描述面不受本判影响——其消费面（regime_gate_dualarm 情绪臂交叉验证 + 年代分层供给参照·T-2026-10-10-180 线）照常；C1 政体门消费本批结论=情绪臂维持描述性参照·不升级为判据（判据面任何升级须另过预注册正门）。

—— 认领：bm-a OS 循环 r938 · 2026-10-10 03:3x · 票 T-2026-10-10-181（GM 署名 P1）
