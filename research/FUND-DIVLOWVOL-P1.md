# FUND-DIVLOWVOL-P1 预注册 · 基本面红利低波族（高 TTM 股息率 × 低波动筛选）股票横截面月频再平衡**新家族**主考格判决批

> **FROZEN v1.0（2026-10-03 bm-b r610 冻结窗·五条件门全绿证链）**：①T-154 TRANSFER 落位——div_events_faces.parquet 54,494 行/5,124 符号/357,002 B/sha256 `66c67d9fd012c504327271a4e1a96bbecb542c9e9cfe47fbd403651723757b40`（bm-c r403 commit 2d8d53ee7·10/10 fail-closed gates PASS·manifest T-2026-10-03-154-sender.json·本机字节+sha256 复验恒等）②probe 全绿 legs1-5——results/_fund_divlowvol_p1_transfer_probe.json（r610 08:5x：T-154 spec 逐字门 + sidecar 全覆盖 5,124/5,124 + **raw-price 恢复公式已知答案 36,399 事件 median rel dev 2.9e-10/72.8% 精确 <1e-6**〔p90 0.23=同日现金+送转混合件漏滤面如实披露·median 为机器答案〕+ yield 月度普查 G-CENSUS 401 + 种子带 disjoint 三门全过）③D6 同族 probe——**ADMIT max|corr|=0.2555**（ENGULF-CE-01·六员全对清单 results/fund_divlowvol_p1/d6.json·probe 级轻量 sleeve 模拟披露面）④种子带注册——`science_gates.SEED_REGISTRY` 落 fund_divlowvol_p1_nulls=20520000·fund_divlowvol_p1_sens=20520500（R250 一步律·本冻结 commit 落键）⑤banned_direction_gate 对冻结终稿 ADMIT rc0（回执见冻结 commit）。**t0 pin=2006-02-06**（probe first_signal_date_t0·A 股现金分红文化 2006 起稳态+¥10M 流动性闸实证；t0 前 148 个月=below-floor 无信号月=诚实跳过禁插补）；**yield 单位口径核验=百分比形态实证**（普查 yield_median_of_medians 0.97%· sane A 股 TTM 股息率量级）。冻结后禁改 §0-§6 判据面；跑后只回填 §7/§8。
> **姊妹族收益流相关性前置披露（disclosure-only·非本批点火门）**：与 FUND-VALUE-P1 headline 日收益 corr=**0.8039**（5017 重叠日）·与 FUND-QUALITY-P1 corr=0.5796——机制同源面如实注记（高股息≈低估值=红利与价值在 A 股历史面高度同源）；D6 拒收线 0.7 只对**在册**成员生效（价值族 NULLS 在烧未判决未入册），**若价值族先注册入六员集，本族注册时点 D6 将面对 0.8039 ≥ 0.7=注册面拒收风险前置披露**；判据面不预设、以本族 burn 读数独立检验（M04/M05 NON-GOALS verbatim）。
>
> 令链血统：**CEO 直令 O-20261002-2115 §一.1③**（新策略/新方向开发提速窗）→ T-2026-10-02-145 leg(c)「首批基本面族 prereg：价值/质量/红利低波」——本批=三族第三件（价值族在烧·质量族在烧）。数据基座=T-131（done·fund_history 5224/5129 完备）＋**T-2026-10-03-154 div_events 转移票（bm-c→fleet·git 方案 A·DELIVERED）**；lane=烧批池宿主=全机（pool autofill 域·akshare/5228 面板数据面 bm-b 在位=R31 判例）。部门=dept:策略（族规格）+研究（judgment 面）。模板=research/PREREG_TEMPLATE.md＋FUND-QUALITY-P1.md（族第二件·结构逐节镜像）；判据节调 science_gates 共享库禁手抄判线；跑前 commit 冻结；跑后只回填 §7/§8；CEO 研究导向律（2026-09-28）合规声明：红利低波=国内基本面打法主流风格（红利/红利低波 ETF 族+A 股经典防御面），本批=A 股原生打法形式化，非国外框架筛国内打法。

## §0 批件身份【必填·跑前】

- 批名/批号：**FUND-DIVLOWVOL-P1**。**N_eff=2,002**＝judged cells 2（1 构造规则 × 2 成本面 x1/x2）＋same-mask 随机 null 2,000；sensitivity Sobol 腿=描述面**不计 N_eff**（§3）。扩容即买单。
- 认领（F-04 先行）：本票 **T-2026-10-03-155**（bm-b 开票+同轮认领+同轮冻结·O-1730 即时律）＋TRANSFER 票 **T-2026-10-03-154**（bm-c 数据车道件·DELIVERED）＋T-2026-10-02-145 leg(c) 引用；开工声明=轮报告 r610 回执。
- 算力预算：**长活入池**（>5min 一律 runnable_pool·O-20260924-2100 s2）——池单元=2 cell-face（DIVLOWVOL-YIELDVOL-x1/x2·每单元=401 起点全窗·t0 前 below-floor 月=诚实跳过计入）＋NULLS（2,000 draws·checkpoint）＋SENS（500 draws）共 **4 池条目**；workers_plan={"workers": 32, "priority": "BelowNormal"}（O-20261002-2158 宽度律同族先例=VALUE/QUALITY 32 workers 对齐）；checkpoint 逐单元 JSONL done-key skip；**点火前置门（fail-closed 全链）**：①div_events TRANSFER 落位（§2·已绿）②probe 全绿（legs1-5·已绿）③D6 同族相关性 probe（已 ADMIT）——三门全绿才入池点火；批报告必带 audit 段。
- 账本面：finalize 步 `science_gates.append_ledger(batch_name="FUND-DIVLOWVOL-P1", batch_trials=2002, file_name="results/fund_divlowvol_p1/fund_divlowvol_p1_results.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev·r509 序律：块持久化进产物件后才写 guard）。

## §0.5 禁开方向硬闸【必填·跑前·D-20260930-41 §1.2】

- 跑前过闸（冻结窗已过）：`python Tools/banned_direction_gate.py --prereg research/FUND-DIVLOWVOL-P1.md` → 退出 0=放行（fail-closed）·冻结 commit 内回执。
- 人工预读结论：**零命中预期**——红利低波=基本面股息率×低波面选股，禁向九方向（横截面动量/反转·单名择时·网格·水温前置·个股确认前置·市值/价格因子·缓冲带·风格延续）无一涉及；**低波筛=风险面横截面排序非价格动量/反转机制**（σ_252=已实现波动率度量·与动量/反转构造零接触·BAN-07 市值面不涉及）；本批无常开择时前置、无缓冲带；本节不复述禁向词面（机器闸为准·r483 清洗律）。

## §0.6 出场轴显式声明【O-20261001-1108 立法·TRIAL_LABOR_LAW §4·M02 双件门】

- **出场轴=②持有到底（ALWAYS-ON hold-through）**（族定义与价值/质量族逐字同面）：成员**只因月频横截面排序轮换离场**（再平衡日落出 Top-N 入选集=entry≤0 信号出场·t22 惯例），**无价格类出场**（无止盈/无止损/无衰减踢出/无亏损时限/无持有上限）。
- **引擎缺省出场栈显式禁用【双通道逐键申报·r522 根因修正面·与价值/质量族逐字同面】**：
  - params 通道（桥内 4 键）：`take_profit_levels=()`·`trailing_stop_activate=1e12`·`initial_stop=-1.0`·`time_decay_period=10**9`；
  - ExitPatch 通道（桥外 2 键·live/paper.py ExitConfig 工厂补丁）：`loss_time_days=10**9`·`global_hard_limit=10**9`；
  - 两通道键集**互斥断言**入 runner selftest（F11 死信回归守卫）；`exit_signal`=entry≤0 全矩阵；**engine/ 零触碰**；T+1 执行与成本模型=引擎正典不变。
- **第二件门=律 A 烧后出场原因普查**（LOWAMP-P2 §9 立法）：finalize 步对 headline 以同一冻结机件重跑逐符号捕获每笔出场 reason——hold-through 面上**唯一合法 reason=signal_reversal**；**缺省栈出场占比 >20%（CENSUS_BLOCK_SHARE=0.20 跑前写死）→ verdict=consumption-blocked**。普查块入结果 JSON gates.exit_census。

## §1 α 机制段【必填·D6】

- 机制勾选：**风险溢价**（主：红利溢价=持有高股息低波组合=承担现金流久期与利率政体风险的补偿——红利股现金流确定性溢价+低波面=防御族尾部风险补偿的反面）＋**行为偏差**（辅：彩票偏好/成长叙事追逐——投资者系统性超配叙事性成长股、低配「无聊」的高股息现金牛，代价支付者=追逐题材弹性的行为对手盘；低波筛=对彩票偏好面〔高波动=彩票型〕的系统性反向）——**结构性**面注记：A 股散户主导市场彩票偏好更重（题材股历史实证；本批资格闸 amt20≥¥10M 反向排除微盘=与 BAN-07 方向零接触，机制叙述纯市场结构上下文非因子输入），机制主张以 burn 读数检验不以此段宣称为准。
- **散户凭什么赢【§1.2】**：**制度/容量**——¥1,000,000 账户在 5100+ 股票池 Top-20 等权持有=容量无限、零杠杆需求、月频再平衡执行压力近零；不重跑任何机构结论（红利溢价=公开文献常识面引用，股息贴现/防御族文献）；例外三问=本账户独有约束（场内股票直接持有·真实成本·本市场 1992-2026 全史窗）成立。
- **同族相关性准入检查【必填·D6】**：入池前 probe 步计算 headline（DIVLOWVOL-YIELDVOL）日收益序列 vs **在册六员全部成员**日收益序列逐对 max|corr|；**max|corr| ≥ 0.7 → 拒收 fail-closed 禁烧**（数值与逐对清单 d6.json 落盘后方可点火；**已跑=ADMIT 0.2555**〔ENGULF-CE-01·probe 级轻量 sleeve 模拟=相关性门输入面·levels 非判据面如实披露〕）；**与 FUND-VALUE-P1/FUND-QUALITY-P1 headline 相关性另列披露**（0.8039/0.5796·disclosure-only——价值族在册后进六员集则照测·0.8039≥0.7=本族注册面拒收风险前置披露非点火门·高股息≈低估值同源面如实注记）。
- M1 t 面【必填申报】：`science_gates.t_from_sharpe(sharpe_full, n_periods)` 派生面（headline cell）；判据=`science_gates.m1_t_value_gate`（Harvey/Liu/Zhu 门槛 **t≥3.0**）。
- M3 闭合族对号【必填】：family_key=**fund_divlowvol_stock_xs**（新键·`science_gates.CLOSED_FAMILIES` 在册键零命中=open 照跑；cn_div_lowvol_rot=ETF 轮动对族〔两器械构造法则差异问题〕与本批=股票横截面族问题正交——机制/宇宙/执行面全异，互不沿用判决·M04/M05 verbatim；fund_value/fund_quality=同面板姊妹族，排序输入〔pe_ttm/pb、roe_q vs TTM 股息率×低波〕与判据面各自独立全路径回测）。

## §2 数据与面板【必填·跑前探针事实，非结果】

- **价格面板**：p1c_stock 冻结缓存（T-139 炉面板·与价值/质量族同面板）——**锚面四元组**：`Money02/data/cache/p1c_stock/*.npy`＋`numpy.load` memmap 直读截断＋1990-12-19 全史起算＋252td 预热。探针事实（probe leg1·bm-b 2026-10-03 已跑绿）：8792 bars·≥5100 列·末 bar **2026-09-22**（qfq）。
- **股息事件面（数据车道件·DELIVERED）**：`data/fund_history/<code>/div_events.json`（T-131 采集·raw sina ak.stock_history_dividend_detail）→ **TRANSFER T-2026-10-03-154**（bm-c→fleet·git 方案 A·value/quality faces 先例）：合并件 `data/fund_history_export/div_events_faces.parquet`（**列：code·ex_date·cash_div_per_10·record_date**；code=large_string·ex_date/record_date=date32[day]·cash_div_per_10=double），行滤（fail-closed·manifest 注记计数）：仅 进度=实施 行·null/unparseable ex_date 19,498 排除·null cash 0·exact-dup 0·5 隔离符号缺席如实披露；**导出门（T-154 spec 逐字·probe leg2 复验绿）**：n_symbols_nonempty 5,124≥5,100 ∧ 逐员事件数中位 9≥3 ∧ ex_date span 1991-04-03..2026-10-23（d1≥2026-01-01）∧ 零 null cash ∧ 零 unsorted ∧ dtype 契约 ∧ sha256==manifest；**同日多组件保全律**（600519 2006-05-19 两行 cash-sum 3.0 已知答案·精确 dup 键不塌缩）。
- **接合法（冻结·PIT 律·本批核心增量一）**：**股息入 TTM 窗以 ex_date 为锚**（除权除息日=分红确定时点·公告/实施日早于 ex_date 的分红可被取消=ex-date 锚构造性消除该风险；T-154 spec 立法面）；**法定日锚定门（T-145 leg(a) 立法）本批 N/A 如实声明**——div_events=公司行动事件面非财报申报面（对照：质量族 MANDATORY/价值族 N/A 声明）；record_date 随件携带但本批不消费（股权登记日=股东资格面与 yield derive 无关·如实披露）。
- **TTM yield derive（本批核心增量二·冻结公式）**：信号日 t 的 **yield_ttm(t) = [Σ_{ex_date ∈ (t−365 历法日, t]} cash_div_per_10/10] / P_raw_close(t)**——分子=trailing 12M 已实施现金分红（每 10 股派息 → 每股 /10·同日多组件行求和）；分母=**恢复到 raw 口径的收盘价**（见下）；TTM 窗=历法 365 日开闭区间 (t−365d, t]（边界排除 ws 日本身·含 t 日本身·probe S1 已知答案腿钉死）。
- **raw-price 恢复（本批核心增量三·冻结公式·probe leg3 实证）**：**P_raw_close(t) = close_qfq(t) × f(t)**，f(t)=`Money02/data/bars/<sym>.factor.json` sidecar 阶梯因子（d/f 双列·f(latest)=1.0·t 取最新 d≤t 档）；sidecar 覆盖 5,124/5,124 div 符号零缺失（probe leg3 普查）；**已知答案实证**：36,399 纯现金事件（2015+·±100 历法日窗内单一 sidecar 事件滤面）implied 跌幅比 f(s)/f(s−1) vs 交易所除权公式 (P_prev−d)/P_prev 的 **median rel dev=2.9e-10**（72.8% 事件 <1e-6 精确·p90 0.23=同日现金+送转混合件漏滤面如实披露·median 为机器答案）；wrong-direction（÷f）判别面披露 0.0024；**禁用 qfq 直作分母**（横截面序被 1/f_i(t) 逐员扭曲·probe 设计段论证）。
- 窗口与 **evidence_cutoff=2026-09-22**（面板末 bar·P 族系 D2 前向锁盒同界；cutoff 后新 bar 锁定不得回流）；结果 JSON 顶层 `evidence_cutoff` + `science_gates.cutoff_meta("2026-09-22")`（缺字段=C2 VIOLATION）。
- 起点集：**T-22 冻结枚举律·月频适配**（与价值/质量族逐字同面）——信号日=每月首个交易日；`enumerate_starts` 月频版（pos≥252td ∧ ≥126td 前瞻 ∧ 当日上市成员数≥24）确定性全枚举；**G-CENSUS 门：起点数逐位==401**（首 1992-09-01·末 2026-03-02·probe leg4 冻结读数同数）。
- **宇宙下限门（本族特有·冻结）**：**UNIVERSE_FLOOR=60（3N·pre-screen）**——信号日 yield>0 ∩ 基础资格 ∩ 可筛波 成员数 <60=该月 below-floor **诚实跳过（禁插补·sleeve 维持原态=t0 前恒空仓）**；probe leg4 普查：**t0=2006-02-06**（首个 clean-tail 月·t0 起 401−148=253 月全过 floor；rank universe post-screen min 51≥30 门/median 779.5）；t0 前 148 个月=below-floor 无信号月（A 股现金分红文化 2006 前稀薄+¥10M 流动性闸历史实证·诚实披露非数据缺陷）。
- 数据完备门（不过门禁跑·probe fail-closed·legs1-5 全绿已过）：①p1c_stock meta 在位 ∧ ≥5100 员 ∧ 末 bar==2026-09-22；②div_events TRANSFER 落位 ∧ 导出门绿（含 sha256 manifest 恒等）；③sidecar 覆盖 div 符号零缺失+恢复公式已知答案 median <2%；④G-CENSUS 401+t0 clean-tail；⑤种子带 disjoint（leg5·已跑绿）。
- **资格掩码（冻结）**：close notna ∧ volume>0 ∧ amount>0 ∧ **amt20_median ≥ ¥10,000,000**（月频信号日回看 20 成交日中位成交额·与价值/质量族逐字同面）∧ 上市≥252td ∧ 动态资格=As-of-date ST/退市排除（P4_BATCH2 sec.2 verbatim·runner import 既有 helper 禁重写）∧ **股息资格：yield_ttm(t) > 0**（trailing 12M 已实施现金分红>0=「分红股」定义门·零股息员不入红利序）；**无 yield 上限帽**（高 yield 陷阱面由低波筛+流动性闸承压·设计从简如实披露）。
- **低波筛（冻结·本族核心构造件）**：σ_252=信号日回看 252 交易日 qfq 日收益（pct_chg）样本标准差（**ddof=1**·min 126 有效 bar 否则不可筛=诚实排除）；**yield>0 资格宇宙内横截面中位数劈半**（σ≤median 低波半区保留）；**Top-N=20 按 yield_ttm 降序**于低波半区内取入选集。

## §3 方法学【必填·冻结】

- **信号定义（冻结）**：信号日=每月首个交易日 t；**两段式经典构造**：①yield_ttm(t) derive（§2 冻结公式·ex-date 锚+raw 恢复分母）→ 股息资格 yield>0；②基础资格掩码内低波筛（σ_252≤宇宙中位）→ ③Top-N=20 by yield_ttm 降序=**cell A=DIVLOWVOL-YIELDVOL（headline·唯一构造规则）**；权重 **eq**（1/N）；**常开**（零前置条件·无择时闸）；**月频再平衡**（信号日 T 收盘算、引擎正典 T+1 开盘执行·O-1132 保守代理）。
- **judged cells 2（跑前写死）**：①DIVLOWVOL-YIELDVOL（HEADLINE）②=①×x2 成本压测面；N_eff=2+nulls 2,000=2,002。
- **执行语义【§0.6 逐字】**：entry_signal=当日入选 ∧ exit_signal=entry≤0（排序轮换出场·全矩阵注入）→ `engine.run_backtest`（T+1·成本模型·双通道缺省栈显式禁用）→ 持有到底；below-floor 月=无信号=持有维持（t0 前恒空仓）；x2 面=成本乘数 2.0；每起点 fresh-entry 洁净切片（t22 先例）；逐符号子账户分解+eq 权重映射。
- **窗族 {6m=126·12m=252·24m=504}**：最长窗一次跑+同曲线切片（P-5 律）；**主判窗=12m 完整窗**·partial 窗如实标记；被动基线=起点日资格掩码内全体成员等权 B&H 同窗（月频族无再平衡）·beat_k=ret_k>p_ret_k。
- **null 对照（≥2,000 三族全律·RANDOM_LARGE_SAMPLE_LAW §3 逐字）**：①**null_pool（G1' skill line 源）**：K=2,000 **same-mask 随机选择 null**——每月同一资格掩码宇宙（**headline DIVLOWVOL-YIELDVOL 完整掩码宇宙**〔yield>0+低波筛+全套资格·与真实 cell 日宇宙逐位恒等·G-MASK 断言〕·同 N=20·同执行·eq 权·`rng([20520000, k])` 子流律·**新种子带 20520000/20520500 disjoint 机证（probe leg5 2026-10-03 已跑绿：全 registry 167 基点 exact+stock_face_furnace 占用带 [20333000, 20445400) 开区间+邻近 ≥2000 三门全过·与价值族块 20500000 净距 ≥20000·质量族块 20510000 净距 ≥8000）**）内均匀随机选 20 员，全面板模拟取 Sharpe 分布（μ_null/σ_null 入 skill_line_v2）。②**block bootstrap B=2,000**（headline 日收益·块长 21td）＋③**sign-flip permutation P=2,000**（双法并列）。**种子带先登记 `science_gates.SEED_REGISTRY` 再跑**（本批键=fund_divlowvol_p1_nulls=20520000·fund_divlowvol_p1_sens=20520500·冻结窗 R250 一步律落键·与本冻结 commit 同批）。
- **sensitivity 腿（描述面零判定宣称）**：N=500 空间填充均匀抽取 over（N∈{10,15,20}·vol_screen_frac∈{0.5,1.0}〔1.0=无低波筛消融面·测量低波筛增量描述〕·yield>0 门固定·再平衡=月频固定·出场轴=§0.6 同面），产物=Sharpe/均值/maxDD 分布描述列，**不计 N_eff、不设门、禁幸存者宣称**；`rng([20520500, k])`。
- **政体分段**：每起点 regime 标签（510300 列 t22 3-way proxy）→ 分段统计；**G-SEG 覆盖门：bear/bull/chop 各 ≥50 起点（12m 完整窗）**——不过=verdict=insufficient-sample（t0=2006-02 后 2006-2026 窗含 2008 熊/2009-15 牛熊轮/2016-18 结构市/2019-21 牛/2022-24 熊/2024-09 反弹=各政体段覆盖以 burn 实读为准）。
- **成本口径声明【CN-C7】**：**股票面 V1=13.041bp/边**（`rev_osc_stock_p1.COST_X1` **单源 import 禁手抄**·runner 断言恒等；¥1,000,000 账户口径申报）；往返=26.082bp；x2 面=52.164bp；单笔名义档位披露同价值/质量族（eq Top-20 单仓 ¥50,000 > ¥20,000 最低佣金临界）。
- **反重复披露（票面 anti-dup）**：①FUND-VALUE-P1/FUND-QUALITY-P1=同面板姊妹族（估值面/盈利面），本批=股息率×低波面首烧——排序输入正交（pe_ttm/pb、roe_q vs yield_ttm×σ_252）、judgment 全路径各自独立，headline 相关性由 D6 另列披露不预设（0.8039/0.5796·§1 前置披露）；②cn_div_lowvol_rot=ETF 轮动对族零重跑（问题正交·M3 对号声明）；③T-139 炉三族=价格面族零重跑；④p1c 面板在用判决存量+2 族零重跑；⑤同族参数面（N×vol_frac 维度集）首烧即本批，确定性重现断言=族首烧无前工件（首个 judged 记录即基线）。

## §4 判据【必填·跑前写死，禁看结果调线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, n_trades, n_entries)`**：全期 Sharpe > skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))）**且** 平稳 bootstrap CI 下界 > 0 **且** entries≥30（F6 双口径）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线 **且** DSR≥0.95（`deflated_sharpe_ratio` 原始收益跑，禁用 dsr_from_stats 充数）**且** 家族 PBO≤0.25（`screening/pbo.py` CSCV 8 块·同族判面集=本批 2 cell）；缺输入=诚实拒收。
- 保留历史描述性条款（批级披露）：年化>0、OOS 双正、回撤≥−35%、无崩年、成本压测（x2 面逐年稳定）——描述条款不替代 v2 门。
- **硬界设计三件套【D-20260925-01①】**：本批无数据腐坏检测类判线（纯策略批），max 硬界 N/A；极端日先验入 §5(c)。
- **新因子 t 面申报【M1】**：headline cell `t_from_sharpe` 派生面跑前申报槽位（SR_ann=§7 回填·T=面板期数·t=§7 回填）；判据=`m1_t_value_gate`（t≥3.0）；缺 t 面=missing_input 拒收非放行。

## §5 跑前预测【必填·写死于跑前，跑后对账】

- (a) **方向**：headline DIVLOWVOL-YIELDVOL 12m 完整窗全期 Sharpe 预期为正但**低于在册 ETF 六员水平带**（与价值/质量族同面预测：股票单名尾部风险>ETF 组合；预测带 Sharpe 0.3-0.8 区间·超带=数据问题先查 ex-date 接合法与 raw 恢复）；beat 被动基线=**不确定方向**——红利低波 A 股历史含长失效段（2013-2015 题材牛市=防御族大幅跑输·2019-2021 成长牛=红利钝化），多数起点不成立=诚实判负预期**真实存在**；**与价值族 sleeve 收益流 corr 0.8039（§1 披露）=本族 OOS 行为预期与价值族高度联动**（价值族判负面本族大概率同向·两族判据面仍各自独立检验）。
- (b) **换手**：月频再平衡换手与价值/质量族同阶（远低于日频族）；x2 成本面年化拖累预测 <2pp/年。
- (c) **极端日先验（硬界三件套 (c)）**：面板窗内极端段=2015-06/07 千股跌停救市段（红利权重金融同跌停·低波面历史跌幅相对较小〔低波=已实现风险度量·非价格带/zone 机制〕）、2016-01 熔断段、2018 全年熊（防御族相对抗跌面=本族机制主张段）、2024-02 微盘崩段（本族 amt20≥¥10M 闸+高股息序天然偏大盘价值=微盘暴露低）、2024-09-24→10-08 暴力反弹窗（红利低波=whipsaw 面·cn_div_lowvol_rot §5 先例承袭）、2021Q1-2024 白马估值消化段；以上极端段**不设豁免**（描述性披露非判据）。
- (d) **nulls 面**：same-mask 随机 null μ 预期≈掩码内等权被动（无信息选择）——headline 超被动+0.10 才可能过 skill line，预测**过线概率中等偏低**（红利溢价在 A 股月频股票面强度未知=本批要测的问题本身）。

## §6 产物

- runner=`scripts/fund_divlowvol_p1.py`（待建·引擎 import 禁重写·FUND-QUALITY-P1 runner 结构镜像·selftest 子命令含 F11 双通道互斥断言+G-MASK+G-CENSUS+t0 钉定腿·probe 内核〔ttm_cash_sum/sidecar_f_at 单源〕import 本 probe 模块禁重实现）；
- probe=`scripts/fund_divlowvol_p1_probe.py`（已建·selftest 13/13·legs1-5 GREEN+d6 ADMIT 已跑）；
- results：`results/fund_divlowvol_p1/fund_divlowvol_p1_results.json`（顶层 evidence_cutoff + gates 块含 exit_census）＋nulls/bootstrap/signflip/SENS 分件＋d6.json（已在位）＋CSV；
- 本文件 §7/§8 回填；轮报告回执。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（一次定稿；工程修复重跑须双跑留痕如实记账）

**r806 finalize 实证（2026-10-08 23:30-23:33 落判·bm-b·driver 日志 rc0·单读 r638 律）**：

- **判决=insufficient-sample**（G-SEG 分段覆盖 bear 70 / bull 65 / **chop 14<50** / na 246——510300 MA200 代理标签期 chop 完整 12m 起点窗天然稀薄+pre-2006 无标签 246 窗；判据面顺序先决拒收，禁重跑）。
- headline x1（t0 2006-02-06·n_days 5018）：Sharpe **0.8941**·ret_full 4.4418·maxDD −0.3042·1,401 trades（70.36/yr）·entries 1,421；x2 生存面 Sharpe 0.8683>0 PASS。
- G1' v2 读数：**line_ok=false**（obs 0.8941 未过硬技能线——同掩码 null μ 0.7178 强基准+多重度校正；skill_line 全输入见 results gates.g1_prime.skill_line·finalize 时点 N_eff=陈旧树面 ledger head 790,905+2）；bootstrap CI95 [0.4635, 1.3285] 下界>0 ✓；trade_gate ✓。
- M1 t=3.9893 PASS；DSR 0.6751（<0.95 fail）；PBO 0.0（register_eligible）；exit_census PASS（block_share 0.2·signal_reversal 合法挡位）。
- nulls（same-mask k=2,000）：μ 0.7178·σ 0.0546·p05/p50/p95=0.6286/0.7183/0.8069；block bootstrap p_ge_obs=0.489；signflip p_two_sided=0.0。
- 全起点 12m 分布（n=395）：best +2.0436 / p75 +0.1603 / median 0.0 / p25 0.0 / worst −0.7747 / positive_share 48.1%；滚动最差 3y −3.77% / 5y −0.20% / 10y **+12.57%**。
- 敏感性（k=500）：Sharpe p05/p50/p95=0.8429/0.8726/0.9024·maxdd_worst −0.3337。
- 台账：本批 +2,002（prev 790,905=**bm-b 网络封锁窗陈旧树基座**，分面 total 792,907 为被取代分支记录；r807 追加式分叉补账 FUND-TRIO-REANCHOR-R807 将三族 6,008 试验单次重锚至活链头 825,328→**831,336**，零双计零丢失）。

## §8 批后复盘【必填·s7-T】

- 预测对账（对/部分/错）＋门禁链损耗账（`results/gate_attrition.json` 追加一行）＋判线 v2 当批读数（skill_line_v2 数字）；
- 回执入轮报告＋CODELY.md 行级追加；若注册新员：注册件带 evidence_cutoff＋live/paper SIGNAL_BUILDERS 接线＋smoke 锚定门复跑。
- **全起点分布【§1.3·D-20260930-41】**：最好/最坏/p25/中位/p75＋滚动 3/5/10 年窗口最差——只报单一起点=结论无效；撤回判定=多数起点不成立即撤回。
- **试验量归因【§1.4】**：本批新增试验数 2,002（RETAIL_QUANT_TRACK §四闸 30 天 ≤500 预算**超限申报**：基本面三族假期开发窗=O-20261002-2115 CEO 直令提速授权——与 FUND-VALUE-P1/FUND-QUALITY-P1 同窗同归因链；judged 仅 2 格，nulls 2,000=判据校准面非探索面·RANDOM_LARGE_SAMPLE_LAW 立法内必需；一句话归因=CEO 直令新家族第三件，判据面 N_eff 由立法最小值撑起非探索面膨胀）。

**r807 批后复盘（absorb 窗回填）**：

- **预测对账=部分对**：①方向带=**错（超带）**——headline Sharpe 0.8941 高于 §5(a) 预测带 0.3-0.8 上沿；按 §5(a) 预案「超带=数据问题先查 ex-date 接合法与 raw 恢复」→ 已立为下窗工程排查项（ex-date 接法探针待跑，不改本窗判决——判决由 G-SEG 先决与判据面独立成立）；经济面备择解释=红利低波筛天然偏大盘稳定白马·同掩码 null μ 0.7178 亦在带上方（掩码本身即高 Sharpe 面，headline 超掩码仅 +0.176）。②「多数起点不成立预期」=**对**（positive_share 48.1%·median 0.0·worst −0.7747）。③「与价值族联动」=**同面实证**（两族同窗同判 insufficient-sample·headline corr 面 D6 已前置披露 0.8039）。④nulls μ≈等权被动预期=**部分对**（μ 0.7178 高于被动常规量级=掩码面强 beta 段贡献）。
- **判线 v2 当批读数**：line_ok=false（obs 0.8941 < 数据驱动 skill line；N_eff 面为陈旧树 790,907 时点读数——补账后真链头 831,336 面只会在未来批抬高线，本批读数如实留档）。
- **门禁链损耗账**：`results/gate_attrition.json` 追加一行（FUND-DIVLOWVOL-P1·r807）。
- **判决链结论**：G-SEG 先决 insufficient-sample（单读 r638 律）→ 无注册新员·无 live/paper 接线·无 smoke 锚定门复跑义务；G1' 明细（line_ok false/CI 下界正/M1 pass/DSR fail/PBO eligible）留档备族炉重访。**族重访前置=G-SEG chop 覆盖结构性问题裁决**（chop 14/50 系代理标签面供给不足，非本批可控变量）+ ex-date 接法探针两项。
- **全起点分布**：见 §7 六数面（best/最坏/p25/中位/p75+滚动 3/5/10y 最差全披露）；撤回判定=不适用（判决非 judged-negative；样本不足面不触发撤回轴）。
- 回执：r807 轮报告+CODELY.md 行级追加。

**r811 ex-date 接法探针定谳（due ≤10-10 12:00·bm-b·探针=scripts/fund_trio_p1_diagnostics.py divlowvol-exdate 腿·内核单源 import 冻结 probe/runner·selftest 7/7）**：

- **§5(a) 超带预案裁决=数据面无罪**：①join PIT 零违例——12 采样 firing 月（2006-02..2026-03 均匀）/19,387 候选员，冻结内核 ttm_cash_sum vs 独立窗口滤重算全等（1e-9 容差·0 失配·0 未排序包·构造性无未来事件）；②raw 恢复零违例——sidecar f≥1 方向/单位全对（f(latest)=1.0·P_raw 恒正·0 越界·1 例 j<0 前首事件边沿 689009 信息性注记）；③选股完整性 12/12（低波半区+Top-20 yield 降序+code 平序全过）；④收益面 qfq 干净——Sharpe 复现恒等（0.8940923==stored·ddof1 面钉死）·max |日收益| 7.1% 零 >10% 日·成员除权日 sleeve 均动 −0.00014 vs 全日 +0.00036（无除权日系统性负偏）。
- **超带归因=掩码防御 beta+段结构，非数据问题**：same-mask null μ 0.7178 已处预测带上沿（预测带 0.3-0.8 锚在册 ETF 六员面、低估了掩码宇宙自身 beta）；headline 超 null 仅 +0.176；段分解 2013-2015 Sharpe 1.40（§5(a)「题材牛跑输」经济预测该段=**错**，如实对账）·2016 后 0.43。
- **处置=不重烧**（判决 insufficient-sample 由 G-SEG 结构先决独立成立）；族重访前置维持 G-SEG chop 覆盖单一项（ex-date 项已闭合）。证据：results/fund_divlowvol_p1/ex_date_probe_r811.json。回执：r811 轮报告。
