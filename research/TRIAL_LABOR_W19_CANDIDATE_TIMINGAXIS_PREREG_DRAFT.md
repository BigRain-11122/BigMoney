# TRIAL_LABOR_W19 候选稿（CANDIDATE DRAFT·未冻结）——时机 timing 轴族首烧（配对块隔离设计·两 face 全叉·X/S 双消费定谳收官批）

> 状态：**DRAFT-BERTH**（funnel leg 1/5：draft → probe → freeze → runner → pool；本件非冻结预注册，冻结时另立 `research/TRIAL_LABOR_W19_PREREG.md` 全模板填齐）。
> 起草：bm-b r924（2026-10-14 06:2x）·dept:研究 ·法源=TRIAL_LABOR_LAW §1 常供律（供给三面：板空〔job_list 零 open+fleet 票零 unclaimed open〕+池饿〔runnable_pool ready=0<floor 3·结构性补充到期〕+W 线判决批零在飞〔W17-JUDGE 344 格 10-11 收官·W18-JUDGE 188 格 10-12 收官·两波全负 lawful-zero〕；N2U3-ALPHAGEN-RL-P1 judged 在飞=E17 通道①非本线判决批——如实注记非本线触发面·算力面错峰照旧）。
> 供给血统：TRIAL_LABOR_LAW §3 多维律声明轴系「入场过滤×出场规则×仓位法×**时机**×域」——W1-W16 十六波全烧入场过滤轴；W17=出场规则轴（judged 344 全负·七 face 配对中位差 0.966-1.0 零迁移=X 消费定谳）；W18=仓位法轴（judged 188 lawful-zero·四 face 中位差全≈0=S as-burned 保持定谳）。**时机轴=声明在册但 W 血统零隔离烧的未探索轴（W17/W18 范式镜像位·执行侧第三轴收官）**。
> probe 事实腿（funnel 2/5·本窗同落）：`results/_r924bmb_w19_probe_facts.json`（W17 r786 候选稿+probe 同窗先例）。

## §0 批件身份（草案位）

- 批名：**TRIAL_LABOR_W19**（时机 timing 轴族首烧·完整配对块隔离·**两 face 全叉**=tl1.AXIS_TIMING 仅 2 face）；批号=冻结时开票 T-<date>-<seq>-P1（开票即认领同轮·O-1730 即时律·W17=T-178/W18=T-185 血统延续）。
- 触发律实况（诚实披露）：本批起草=TRIAL_LABOR_LAW §1 常供律例行供给步（W 线两波判决批均已排水收官·池饿坐实）；**冻结窗不受 N2U3 judged 排水约束（不同通道）**，但点火窗算力面与在飞批错峰（功率红线律·CPU 批并行照旧）。
- 格点规模（草案算术）：SCREEN=**173 入场 cell × 2 timing face = 346 配对格 + K=200 同构 null = 546 试验**（廉价 6m 面）；JUDGE=**2×n_blocks 完整配对块**（块完整律：任一臂过初筛的入场 cell→该 cell 全 2 臂入判决；块数上限 90 冻结窗定·按 screen beat6m 均值降序确定性选择规则非看判决结果挑选）；两批 evidence_cutoff 均 **2026-09-22**（P-5C 冻结口径 binding·W4-W18 同锚）。
- 算力预算：GENERATE=分钟级（W16 候选件 verbatim 载入+2-face 全叉展开+排除簿对号·确定性零随机）；SCREEN 546 格 6m 廉价腿（>5min 入 results/runnable_pool.json·O-2100 执行面分离·W15/W17/W18 分片先例）；JUDGE=2×n_blocks 深面板物理腿（预测 ≤180 格·>5min 入池分片）；**烧批一律 CPU 余量律**（BelowNormal+线程帽 ~26/32）。
- **供结契约**：本批零生成供给（入场=W16 冻结 cell 复用=A6/B167 自然比；X=template_default 消费 W17 定谳；S=as-burned 保持 W18 定谳）；**双消费定谳=W19 为执行侧三轴（X/S/T）隔离收官批**——若 T 轴照负，未来 GENERATE 可三轴全固定省三维度（语法效率链可执行结论）。**48h CEO 呈报钟**：随判决面落地起计（票面持有）。

## §0.5 禁开方向硬闸。【必填·跑前——本窗实跑两连：run1 无例外块=REJECT（BAN-04 词面）→补齐例外块→run2=**ADMIT**（registry v1.0·r924 实跑回执）；冻结窗复跑 rc0 ADMIT 为冻结门必要条件。】

- 命中编号：**BAN-04**（Grid trading·词面命中=line 18「weekly_grid=ISO 周首日网格门」——frozen tl1 face 名 verbatim 所致〔tl1.AXIS_TIMING 注册面在册〕·机制非同体）。
- 例外类型：`new_mechanism`
- **原否证不可能看见的东西**：BAN-04 否证的是「价格网格交易」——按价格档位分层挂单补仓/止盈的执行机制（grid ladder at price levels）。本批 weekly_grid=**时机粒度门**（入场仅限 ISO 周首个交易日的日历门控·`tl1.apply_timing` L596-604 机械逐行=纯日历条件分支 `isoweek!=shift(1) ∨ isoyear!=shift(1)`·**零价格档位逻辑零挂单阶梯**）——作用维度=入场时点选择，与价格网格正交；原否证不可能看见本批的日历粒度配对读数。词面撞=引擎注册面 verbatim 纪律所致（禁改 tl1 face 名），非机制复刻零形态复刻。

## §1 意义门三问（TRIAL_LABOR_LAW §4·过门声明）

1. **本批回答什么研究问题**：在受控入场语法（W16 冻结 173 cell verbatim·零新生成）+受控出场面（X=template_default·W17 证据消费）+受控仓位面（S=cell 原生 as-burned·W18 证据保持）上，**入场时机粒度族（daily_signal=日频信号原生 mask vs weekly_grid=ISO 周首日网格门）的边际贡献是否显著**——timing 是唯一被测维度（执行粒度 vs 信号衰减 tradeoff 的首份受控配对读数；入场/出场/仓位/过滤面全格恒同 per-cell 配对对照）。
2. **消费方是谁**：①timing 轴在 W 血统的**首份受控配对读数表**（历史读数=T 始终为 per-cell 冻结随机抽样混杂维·从未以唯一变量+逐入场配对形态烧过——W17 A7 普查范式同构命题）；②**语法效率链收官**：若负读数照报→T 轴降权正典依据=未来波 GENERATE 可固定 T=daily_signal 省第三轴维度（W17 §0 consumer ③/W18 §0 consumer ② 同律兑现链·X+S+T 三轴全定谳后未来生成只需入场×过滤面）；③试用期题库 s4 intake（D6 绑定门→STRATEGY_LIBRARY 注册行+纸盘上岗）；④engine apply_timing 机制稳健性证据；⑤scorecard/CEO 一页纸消费。
3. **语法登记簿查重**：TRIAL_GRAMMAR_LEDGER 实读（r924 2026-10-14 06:2x）——W1..W16 全部行=入场语法 face 族（T 为 per-cell 冻结随机抽样混杂维）；W17 行=出场轴（T 逐字携带非变量轴）；W18 行=仓位轴（T 逐字携带非变量轴）；N2-W15/W18/W20=组合采样族。**timing 规则族在 W 血统=零隔离烧**。冻结窗 probe 腿强制复扫登记簿+A7 式全产物普查断言零 timing 隔离行（fail-closed·W17 烧史修正横幅教训=L1 文本扫描盲区·须全产物普查面）。

## §2 α 机制段（D6·冻结时全填·草案方向位）

- α=**结构**：执行粒度纪律——周频网格门=对信号噪声与过度交易的结构化过滤（入场机会集中于每周首个交易日=对散户追涨杀跌频率偏好的机械化抑制；少交易=少成本损耗+少假信号暴露），日频=信号即时性（衰减风险 vs 粒度收益的 tradeoff 为本批被测命题本体）。冻结时按 face 逐个展开论证一句话。
- **散户凭什么赢（§1.2）**：结构（粒度纪律 vs 情绪化交易频率——散户在 timing 维度的对手盘是自己的过度交易冲动；机械化网格门=结构化反收割）＋制度（T+1/成本口径恒开·三铁律不变）。
- 同族相关性准入检查：冻结时逐对算 max|corr|（在册+同批·日收益口径·≥0.7 拒收）；本批**零新策略函数**（入场=W16 冻结 cell·timing=tl1.apply_timing 既有函数 verbatim import）——配对臂间高相关=设计本体（同入场 2 臂·weekly 臂 mask=daily 臂 mask∩周首门为掩码子集=臂间差异为设计面），N_eff 折减由 g1_prime_v2 数据驱动线（batch_cells=546 计入）与批内 BH FDR 承担（W17/W18 §1 同律披露）。

## §3 timing face 集+X/S 双消费定谳（草案位·冻结窗定稿）

- **timing face 表（tl1.AXIS_TIMING verbatim·零新代码零引擎改动）**：
  | face | 时机规则 | 机制语义（tl1.apply_timing L596-604 verbatim） |
  |---|---|---|
  | daily_signal | 日频信号（基准） | mask 原生 verbatim（零门控） |
  | weekly_grid | 周频网格门 | mask ∧ ISO 周首日门（新入场仅每周首个交易日·`isoweek!=shift(1) ∨ isoyear!=shift(1)`） |
  control 臂=**cell 原生冻结 T verbatim**（as-burned 基线·实测分布 daily_signal 128/weekly_grid 45）；treatment 臂=**另一 face（per cell 恰一·两 face 全叉=每 cell 两臂完备配对块）**。
- **X 轴消费定谳（W17 证据兑现）**：X=③ template_default 按设计测（W17-JUDGE 344 格全负+七出场 face 配对中位差 0.966-1.0 零迁移=出场轴降权正典·W17 §0 consumer ③ 语法效率结论兑现首例）。
- **S 轴消费定谳（W18 证据兑现）**：S=cell 原生 as-burned 保持（W18-JUDGE 188 格 lawful-zero+四 sizing face 中位差全≈0=S 轴非判别面·W18 §0 consumer ② 降权结论兑现；配对面保持原生冻结=决定论交叉门三波链可续）。
- **出场轴显式门（O-20261001-1108 三选一）**：X=③ template_default 按设计测（引擎缺省出场栈=被测基线非隐用·三选一显式声明零缺位）——与 X 消费定谳同面互证。
- 禁开方向硬闸（§0.5）：timing 轴族非新入场方向（粒度门控作用于既有入场掩码·九禁向预期零命中）；冻结时 `banned_direction_gate.py --prereg` rc0 放行为冻结门必要条件。

## §4 数据与面板（冻结时全填·草案锚位·本窗 probe 已实测）

- 宇宙=core48 冻结锁盒（RW-4）；evidence_cutoff=P-5C 冻结绑定 **2026-09-22**（W14/W16/W17/W18 同族绑定先例）；面板锚 `data/daily/sh510300.csv` rows≤cutoff=**3,483** 实测（首 2012-05-28·W17/W18 同锚复现）。
- 入场源锚=`results/trial_labor_w16/w16_candidates.json`（冻结产物零再推导·n=173·A=6/B=167·20 元组·axis[3]=T 槽实测 daily_signal 128/weekly_grid 45）；**sha256_16=22179881b7537193=CRLF-canonical face**（r890 bm-b 坑修配方：LF 检出须 `replace(CRLF→LF→CRLF)` 归一后哈希·W18 runner `_entry_load` L421-429 verbatim 克隆为本批 runner 必列；当前本机 LF worktree 原始面 sha256_16=9974725830e76f31·blob 33f7ea3f 自 10-07 未动=同 blob 双面如实披露——**禁按原始面直接断言**）；runner 探针与锚强制同面断言（载入件 CRLF-canonical sha 恒等·面错配=VOID fail-closed）。
- null 对照=K=**200** 同构随机信号 null（随机入场掩码+timing face 从 2 face 均匀抽——同格点空间同参数空间 draw·BACKTEST_PLAN 三铁律）；判官双 null（B=2000 block bootstrap+P=2000 sign-flip）。
- **种子带候选=20640000 族带**（W17 20610000/W18 20630000 结构镜像·角色间隔 500/1000 保形）：trial_labor_w19_gen=**20640000**（本批零消费持有——零新生成·族带连续性+未来 W19 派生生成面预留）/ trial_labor_w19_scrnull=**20640500**（rng([20640500,i])·i<200）/ trial_labor_w19_unc=**20641000**（rng([20641000,cell_idx])·cell_idx<346）；**本窗 seed_admit_gate 实跑 base=20640000 span=1 rc0 verdict=FREE**；冻结窗 span=1001 全带复跑+registry live（218 键）disjoint 断言+全仓文本外来零命中扫（W17 教训=自然候选可被占拒·theme_deepen 实锚）；R250 同 commit 一步律。
- DSR 活链头（草案时点 live 读参考）：**940,789**（head file=n1_w235_results.json·SatEngine 永续波推进中——**冻结窗 live 读为准·禁手抄本数**）。

## §5 判据（冻结时按 PREREG_TEMPLATE §4 全填·共享库引用零手抄）

- SCREEN 判线（L2 技能线）：存活 iff leg-L 6m beat6m > null 族 p95（程序冻结·K=200 同构 null·p95 跑前写死）；null p95 参照带 **[0.50,0.53]**（W1-W13 带延续·W17 实读 0.5116/W18 实读 0.511572 均带内）。
- JUDGE 判线（双口径分离披露·W17/W18 §4 同律）：(a) 注册改革口径（正典·O-1058 五步链）=L3 批内 BH FDR（q≤10%）∧四维合成分完整双门（`science_gates.g2_reform_fdr4d`·缺维拒收零静默填充）+L4 top-N=3/波 by composite（REFORM 常数 import 禁手抄）；(b) G1'v2+G2-v2 口径=`science_gates.g1_prime_v2`+`science_gates.g2_registration_v2`；**W16 §8 缺口教训=runner 规约必列改革面块**（member_metrics 四维提取+dual-nulls+g2_reform_fdr4d+top-3+天花板基线·同名点验·缺块=runner 不许 landed）；E[FP]=0.05×N_judged 如实披露；负波照报。
- M1 t 面（必填）：judged cell 逐格 t 面=leg-L Sharpe `science_gates.t_from_sharpe` 派生过 `science_gates.m1_t_value_gate`（t≥3.0）；缺 t 面=missing_input 拒收非放行。
- **配对读数面（本批设计独有·冻结统计口径·W17/W18 §4 同律）**：逐 face 配对差分序列 delta_f(cell)=reading(cell@f)−reading(cell@as-burned)→逐 face Wilcoxon 符号秩检验（B=2000·rng=unc 族带）+逐 face 中位差与 IQR 全列披露+**按 as-burned T 子群二级读数**（daily_asburned 子群 n=128〔treatment=weekly〕/ weekly_asburned 子群 n=45〔treatment=daily〕——粒度迁移的方向不对称面=本批独有交付件 w19_paired_deltas.json）；描述性对照条款批级披露不替代判线。
- 样本充足律：n_eff≥100 起点×三段各≥100（na 桶诚实）——不越→verdict=insufficient-sample 禁判 pass。

## §6 跑前预测（冻结窗写死位·草案方向先验）

- **§5.1 决定论交叉门预测（三波链）**：as-burned T 臂 screen 存活=**恰好 43/173**（W17 control 臂=W18 as-burned 臂同 cell 读数逐位恒等复现·确定性引擎零漂移前提·三波链第三环）；任何偏差=面错配 VOID 红旗非科学读数。
- **§5.2 treatment 存活率带（vs as-burned 43/173=24.9% 基线）**：weekly 臂（daily_asburned 子群 treatment·入场机会 thinning ≈5/22 ≈-77%）**[0.4x,1.1x]**（n_entries≥30 门槛风险+少亏双面）；daily 臂（weekly_asburned 子群 treatment·thickening+77%）**[0.8x,1.5x]**（负 alpha 暴露更多 vs 更多样本两面）。
- **§5.3 null p95 参照带**：[0.50,0.53]（2-face 混合 null·W18 实读延续）。
- **§5.4 JUDGE 面**：eligible_reform 预测 **[0,3]**（血统先验=W17/W18 连续 lawful-zero+入场源同 cell 已两次判负——执行侧第三轴照负为主预期·负读数的语法效率结论照 §0 consumer ② 兑现=可执行产出）；n_blocks 预测 **[20,60]**（as-burned 43 块底+treatment 正相关上浮·上限=冻结帽 90）。
- **§5.5 配对差分方向预测**：weekly→daily 臂 delta≤0（负 alpha 池上加密交易=更负·宽幅如实）；daily→weekly 臂 delta≥0（thinning 少亏）或 trade gate 拒（n_entries 不足）——两子群方向不对称=本批独有读数面。
- **§5.6 极端日先验（硬界设计三件套 (c)）**：窗内七极端日（2015-07-27/2016-01-04/2024-02-28/2024-09-24/2024-09-30/2025-04-07/2026-01-19）——周首日门使 weekly 臂在长假后首周集中暴露缺口日开盘（2015/2016 崩盘段 daily 臂逐日骑跌停链 vs weekly 臂少骑若干缺口日=daily 臂 dd 更深先验；2024-09-24/09-30 暴力反弹段 weekly 臂错过周中反弹日=截断利润先验）——方向披露非判线。

## §7 产物（冻结时定稿位）

results/trial_labor_w19/{w19_grammar.json,w19_cells.json,w19_screen.json,w19_screen_cells.csv,judge_state.json,w19_judge.json,w19_reform_face.json,w19_intake.json,w19_paired_deltas.json}（W17/W18 目录范式同构+改革面件必列+配对差分件含按 as-burned T 子群二级读数）+SEED_REGISTRY 三键（20640000/20640500/20641000·冻结步同 commit）+波级票（T-<date>-<seq>-P1·O-1730 即时律）+F-04 MSG 声明同轮+attrition 两行（SCREEN 546+JUDGE 2×n_blocks）+TRIAL_GRAMMAR_LEDGER wave-19 行（GENERATE 消费时落·W11/W17 实践先例）。

## §8 精确续作点（append-only）

- **r924 bm-b（本窗）**：候选稿落件（本件·funnel 1/5）+probe 事实件落地（funnel 2/5·W17 r786 同窗先例）：w16 T 槽分布 128/45 实测+tl1.AXIS_TIMING/apply_timing 语义锚+seeds 带占查（20640000 span1 rc0 FREE）+入场源 sha 双面锚（CRLF-canonical 22179881b7537193/raw-LF 9974725830e76f31/blob 33f7ea3f）+W17/W18 verdict 落地读数+DSR 活链头 940,789+撞头探针 CLEAR。
- **下步=冻结窗（funnel 3/5·任一健康机可承·commit 即锁）**：A 系十腿 probe（W17 r788 范式）=登记簿复扫+A7 全产物 timing 隔离普查（W1-W18 candidates/cells 逐波实读断言零 timing 隔离行）+apply_timing 语义逐行锚+入场源 sha 三面实读+W18 verdict 消费定谳复核+seeds 带占 span=1001 全带复跑+撞批四查（job_list/fleet 票/git fetch/inbox）；冻结四件齐=commit 冻结+SEED_REGISTRY 三键同 commit+波级票同轮开票认领+F-04 MSG 声明同轮。
- **runner 构建（funnel 4/5·r446 手术坑律面）**：clone trial_labor_w18.py 基座（**`_entry_load` CRLF-canonical 配方 verbatim 携带=r890 坑修不回退**）+timing face 层（`tl1.apply_timing` import 零重实现·face 表 §3 verbatim）+改革面块必列（W16 §8 缺口教训）+G-face 断言电池（**三波决定论交叉门**=as-burned 臂 vs W17 control/W18 as-burned 同 cell 三列恒等+tl1.AXIS_TIMING 恒等+入场源 CRLF-canonical sha 恒等）+GBK reconfigure 入口律（r236）+selftest hermetic 全绿→prep/finalize/judge-prep 真数据 identity-face 三命令首跑→宣布 runner landed。
- **GENERATE→SCREEN→JUDGE→intake（funnel 5/5）**：>5min 入池·O-2100 执行面分离·CPU 余量律；judged 落地→§7/§8 回填+48h CEO 呈报钟起计+attrition 两行尾追；判负→T 轴降权正典性依据=执行侧三轴（X/S/T）全定谳收官（未来 GENERATE 语法效率可执行结论）。
