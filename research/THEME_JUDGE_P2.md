# THEME_JUDGE-P2 预注册 · 题材波骑机械翻译**改道判决批**（深破线 bl=0.75 族 · 算法点火普查全集 × E28 集群分层）

> **FROZEN v1.0（2026-10-04 bm-a r676 冻结窗）**：本件 commit 冻结先于任何 judged run（R99 律）。冻结证链=①票 **T-2026-10-04-169-P1**（r676 开票+同轮认领·O-1730 即时律）+开工声明 `fleet/inbox/MSG-2026-10-04-1245-bma-all.md`（零反对窗）；②消费面冻结产物在盘=v0.3 算法点火普查 `results/theme_ring/theme_events_v03_algorithmic.json`（**sha16=51b1b8226afc74b1**·1919 行·去重后 1822 rides/796 ETF·P1 冻结件字节恒等复用）；③种子带 `theme_judge_p2_nulls=20589000` 随本冻结窗注册（science_gates.SEED_REGISTRY·带 [20589000,20591000)·与 theme_judge_p1 带端 20587000 净距 2000≥2000·全 registry 178 条撞带扫描零命中·回执 `results/theme_judge_p2_seed_band_receipt.json`）；④D6 同族准入 probe **ADMIT max|corr|=0.3682**（P2 名下实跑重算·B&H 探针 sleeve 出场常数不变性 by construction·回执 `results/theme_judge_p2_d6_probe.json`·REG6 逐对数值=P1 同值 0.3682 复现）；⑤banned_direction_gate 对冻结终稿 ADMIT（回执见冻结 commit）；⑥closed_family_check：`science_gates.CLOSED_FAMILIES` 键 `theme_wave_ride_mechanical` **零命中**（P1 判负未入闭合册——P1 关线范围=bl 0.80 headline 面·0.75 族由令链预留）=open 照跑。冻结后禁改 §0-§6 判据面；跑后只回填 §7/§8。
>
> 令链血统：**O-20261001-2103（题材战法 T1 立项·R4 exploration 判负线明确预留「0.75 深破线族待独立冻结再判」——本批授权面）**＋O-20261001-2106（实测律）＋O-20260928-1522（A 股原生打法优先纲）＋THEME_JUDGE_P1 §4/§5(g) E24-ii 条款（「主面判负但某变体读数高=照实披露+须另立预注册才可升格·禁本批内改常数翻案」）。**与 THEME_JUDGE-P1 判负的关系（三诚实申报）**：①**非 post-hoc 翻案**——0.75 族的预留（10-01 R4 判负线）先于 P1 烧批（10-04）；②**非同族重开**——P1 判负关线范围按其 §4 判读结构原文=「算法点火全集上破线出场+复活再入场系统（bl 0.80 正典常数）无法过 null 校准门」·0.75 深破线族在其判负前即被令链 carve-out 为「待独立冻结再判」面；③**选择偏差如实披露**——本批 headline 常数选择=bl 0.75（令链预留·非 sens-argmax）+rb 1.25（v0.2/v0.3 正典·**刻意不取 sens-max rb 1.3**）；P1 敏感腿 16 行读数=动机披露面非判据面；DSR 折减消费 ledger N_eff 全量（§4）·跑前预测带以 sens 读数为先验锚如实宽设（§5）。部门 dept:策略（系统判决面）+研究（题材环 R3-R6 消费面）。
>
> **CEO 研究导向律合规**：题材波骑=A 股原生「抓机遇」民俗打法的机械翻译续判；改道候选=E24-ii 语法内变体升格正路（非新框架）。P1 敏感腿披露（TJ-SOLO bl0.75 pooled Sharpe 0.52/1.02/1.30 @rb1.2/1.25/1.3 vs headline bl0.80 0.2735）=本批动机面——本批判的是**该读数在新 null 校准门下是否仍立**（P1 null μ 0.3734→P2 null 族随 bl0.75 出场同移·判线同步重算·非拿 P1 判线复用）。

## §0 批件身份【必填·跑前】

- 批名/批号：**THEME-JUDGE-P2**。**N_rows=8,004**＝judged cells 4（{FULL, SOLO} 分层 × {x1, x2} 成本面）＋same-mask 随机点火 null 4 族 × 2,000 draws；邻域敏感腿 8（§3·描述面**不计 N_eff**）。扩容即买单。
- 认领（F-04 先行）：本票 **T-2026-10-04-169-P1**（r676 开票+认领同轮）＋开工声明=MSG `fleet/inbox/MSG-2026-10-04-1245-bma-all.md`（零反对窗）。
- 部门归属：dept:策略（judged 面）＋研究（题材环消费面）。
- 算力预算：**长活入池**（>300s=O-1900 ①帽外·O-20260924-2100 s2）——池单元=1 烧判 shard `theme-judge-p2-burn-0of1`（real cells 4＋nulls 4×2000＋邻域敏感腿 8＋D6 real 面复验＋出场普查全链）；workers_plan={"workers": 26, "priority": "BelowNormal"}（O-2355 多核强制 ProcessPool＋CEO 10% CPU 余量律 26/32 帽）；算力同型 P1 实测 87s/26 workers＋面板装载 ~20s·预算帽 600s 诚实停；checkpoint=逐 rep-chunk（100 reps/块·80 块/族）JSONL done-key skip＋**非空 payload 守卫**（r670 律：done 判定=文件名实配+ks 非空双条件）；批报告必带 audit 段。
- 账本面：finalize 步 `science_gates.append_ledger(batch_name="THEME-JUDGE-P2", batch_trials=8004, file_name="results/theme_judge_p2/theme_judge_p2_results.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev）。
- **池面 data_deps 字段（D-20261004-02① 池认领数据本地性门）**：池 entry 增 `data_deps=["results/theme_ring/theme_events_v03_algorithmic.json", "data/daily/"]`——tick 认领前本地在场断言（文件/目录级·秒级零成本）·不在场=跳过+last_tick 记 `data_not_local`。

## §0.5 禁开方向硬闸【必填·跑前·D-20260930-41 §1.2】

- 跑前过闸（冻结窗实跑）：`python Tools/banned_direction_gate.py --prereg research/THEME_JUDGE_P2.md` → **退出 0=ADMIT**（fail-closed·冻结 commit 内回执）。
- 人工预读结论：**零命中预期**——本批机具与 P1 同构（事件锚定入场〔+20%/20td 量能 3× 滞后确认〕＋破线出场〔回撤破线非反转·仅常数 0.80→0.75〕＋复活再入场〔谷底尺度反弹非短线窗口〕）：非 BAN-01（零横截面排序）、非 BAN-03（出场=回撤破线非反转）、非 BAN-05（E28 分层=判决面分层非交易前置闸）、非 BAN-08（250td=复活等待窗）；**非 BAN-04**（常数改动=出场深度参数·非任何网格交易构造——P1 §3 同词面回避注记续用）。若机器闸命中=按例外类型 `new_mechanism` 声明（深破线出场=处置效应对手盘结构的常数面·P1 判负未覆盖）。
- **对 THEME-JUDGE-P1 判负的关系**：非同族重开（P1 未入闭合册·0.75 族令链 carve-out）；同语法重试合法性=本文件头三诚实申报＋令链预留（§1 语法面）。
- 消费在册判负线：`science_gates.CLOSED_FAMILIES` 键 `theme_wave_ride_mechanical` 零命中=open 照跑（冻结窗 closed_family_check 回执随 commit）；**若本批主面判负=族级关线连同 0.75 预留面一并诚实收口（theme 线机械翻译改道候选耗尽·下一供给面走新判据面另立预注册）**。

## §0.6 出场轴显式声明【O-20261001-1108 立法·TRIAL_LABOR_LAW §4·M02 双件门】

- **出场轴=①策略自有出场**：破线门（收盘≤持有期峰收盘×**0.75**·`theme_persist_p1.simulate(break_line=0.75)` 参数面单源·MINUS20_LINE=0.8 正典值在本批**不消费**）=系统唯一价格出场；复活再入场（出场后 250td 内收盘≥谷×1.25=正典 verbatim）=系统唯一再入场；**无止盈/无时间衰减/无持有上限**。窗=点火 bar 起 min(ignition+750td, 截断面板末)——窗末存活仓按窗末收盘估值（不强制平仓·B&H 同待遇）。
- **引擎缺省出场栈双通道禁用断言**：本批=纯 L1 逐日模拟器（`theme_persist_p1.simulate` **单源复用禁重写**·engine/ 零 import）；runner selftest 断言=①`engine` 与 `engine.exit_rules` 不在本 runner import 图②`simulate` 为唯一出场实现③缺省栈（take_profit/initial_stop/trailing/time_decay/loss_time/global_hard_limit）零涉入=双通道键集不适用如实声明（无桥=无键）。
- **第二件门=烧后出场原因普查（CENSUS_BLOCK_SHARE=0.20 跑前写死）**：finalize 步逐 ride 普查每笔出场/入场 reason——**唯一合法集={first_entry, break_line_sell, rebirth_buy}**；窗末存活=censored 旗（非出场）；非法 reason 占比 >0 即 verdict=consumption-blocked（本批 CENSUS 门取 0 非帽值：L1 路径无缺省栈=任何非空集即实现 bug）。
- **右删失处理**：censored ride=持有至窗末按末 bar 收盘估值并入 pooled 曲线（B&H 同待遇）；per-ride 行带 `censored=true` 旗；截断致删失翻转面=break_date>2026-09-22 的 wave（P1 实测 1 例·159901 seq-2——本批出场线下翻转集**必不同**：bl0.75 更少出场=翻转面只减不增·实测数 §7 对账）。

## §1 α 机制段【必填·D6·四选一】

- 机制勾选：**[x] 行为偏差（主）**——题材点火=注意力稀缺驱动的叙事聚集资金流（+20%/20td×量能 3×=注意力确认器）；**深破线的独立行为主张（本批新面）**：P1 bl0.80 出场在−20% 处=噪声区间内（题材波正常回撤常破−20% 再续升）·机械早出=把「回撤后余下升段」让给不执行纪律者；bl0.75=把出场线下移到处置效应痛感区之下=**持有者对浮盈回吐的处置效应对手盘结构变化**（谁付出代价：在−20%~-25% 区间恐慌卖出的处置效应交易者——本批多赚/多亏的都是他们让渡的段）；长命波行为面与 E28 分层判罚同 P1。**+[x] 结构性（辅）**——ETF T+1 与点火滞后确认=入场执行保守代理结构来源。
- **散户凭什么赢【§1.2·必填】**：**纪律/行为**——测「更深破线能否在无成名选择偏差的算法全集上把波尾段持住」；零速度/零独有数据/容量=ETF 面无限；不重跑任何机构已验证结论（处置效应=folk 常识面）。
- **同族相关性准入检查【必填·D6】**：冻结窗 probe 已跑（P2 名下）——pooled 同窗 B&H 探针 sleeve（出场常数不变性 by construction·fund-family probe 先例·levels 非判据面）vs 在册六员（REG6·`ew6_portfolio.member_run` 同码路径）逐对 |corr|：COMPOSITE-CE-01 0.2608/COMPOSITE-CE-02 0.2329/DROUGHT-CE-01 0.2707/ENGULF-CE-01 0.3682/NEEDLE-DE-01 0.2989/VOLATILITY-CE-01 0.2217（n_common=1630·事实件 `results/theme_judge_p2_d6_probe.json`）——**max|corr|=0.3682 < 0.7 → ADMIT**；烧后另以 real pooled 系统面（bl0.75 出场）复算并入批报告（judged 面复验非再门）。
- **语法去重门【T-84s3】**：TRIAL_GRAMMAR_LEDGER 已含 P1 消费行「事件锚入场+破线出场+复活再入场」三元组——本批**同语法=已消费行申报例外**（例外合法性=令链预留 0.75 carve-out+E24-ii 变体升格条款·非语法面 novelty 重试）；runner selftest 断言=ledger 消费行存在性+本批例外申报在场（防第三批同语法无申报撞入）。
- **M1 t 面【必填申报】**：headline cell `science_gates.t_from_sharpe(sharpe_full, n_periods)` 派生面；判据=`science_gates.m1_t_value_gate`（t≥3.0·Harvey/Liu/Zhu）；缺 t 面=missing_input 拒收。
- **M3 闭合族对号【必填】**：family_key=**theme_wave_ride_mechanical**——CLOSED_FAMILIES 零命中（冻结窗回执）=open 照跑；**本批负判决=M3 收口申报**（§0.5 尾行）。
- **试验量归因【§1.4·RETAIL_QUANT_TRACK 四闸 30 天 ≤500 预算超限申报】**：本批新增 **8,004**（judged 4+nulls 8,000——RANDOM_LARGE_SAMPLE_LAW §3 ≥2000×4 格一一对应·立法内必需）；归因=CEO 直令题材 T1 线 R4 判负线 0.75 预留面的独立判决（O-20261001-2103）+E24-ii 变体升格条款直接执法——**判决语义先写死**：主面过线=0.75 族升格候选成立（注册走注册件另议）；主面不过线=theme 线机械翻译族**连预留面一并诚实关线**（改道候选耗尽·无第三常数面可翻）。

## §2 数据与面板【必填·跑前探针事实，非结果】

- **宇宙/事件面**：v0.3 算法点火普查全集（P1 冻结件）——**字节恒等消费**（sha16=51b1b8226afc74b1·runner selftest 断言）；去重正典 verbatim（identity=(norm6, ignition_date)·碰撞确定性序 keep-first bare 胜出·1919→1822 去除 97 双计·796 唯一 ETF·48 双胞胎重叠段价格逐日恒等 P1 探针腿 5 已证——**本批复用 P1 冻结件零重拉**）。
- **代码→文件正典（verbatim）**：`code_to_file`：剥前缀→1 开头映 `sz{6位}.csv`/5 开头映 `sh{6位}.csv`（837/837 覆盖·0 unknown）。
- **evidence_cutoff=2026-09-22（前向锁盒 D2·两口径披露·P1 冻结口径 verbatim）**：episode 面文件尾=836 尾 09-22＋1 尾 09-04（sh512390 停更件）——统一截断到 2026-09-22；census window_end 标签 09-30=生成器全局 max 尾工件不消费；48 bare 件与核心五员 09-23..09-30 bars=锁盒外锁定不得回流本批；cutoff 后新 bar 锁定；结果 JSON 顶层必带 `evidence_cutoff`＋`science_gates.cutoff_meta("2026-09-22")`（缺字段=C2 VIOLATION）。
- **数据锚面定义四元组【G-ANCHOR-FACE·逐位同 P1】**：事件面=`results/theme_ring/theme_events_v03_algorithmic.json` json.load 直读＋无预热；日线面=`data/daily/<code_to_file>.csv` pd.read_csv(usecols=["date","close"]) raw 直读截断≤2026-09-22＋各员全史起算＋无预热；在册六员面=`ew6_portfolio.member_run`＋`live.paper.load_core`＋cutoff 截断；政体标签面=`t22_virtual_timepoints.regime_proxy` 同面 import。**探针-锚同面断言**：runner 实载路径与锚声明路径逐位比对——一面不相等=面错配 VOID。
- **E28 同日集群分层（判决面分层·verbatim）**：CLUSTER 面=cluster_size≥10 的日（34 日·1,171 rides）；SOLO 面=<10 的日（651 rides）——两分层各判各的。
- **drop gates（fail-closed·P1 实测全零）**：ignition_date 不在截断序列（0）／窗长<2 bar 不可入场（0）——1822/1822 rides 全入场。
- 数据完备门（不过门禁跑）：①census sha16 恒等②去重计数逐位==1822③1822 rides 零 drop④种子带 disjoint（§3）⑤COST_X1 单源 import 恒等 0.0013041⑥48 双胞胎价格恒等（P1 冻结件消费=①②⑥由恒等断言承载）。
- **面板新鲜度**：日线面=P1 同窗字节（cutoff 2026-09-22 锁盒内·黄金周无新 bar 无漂移面）；**cutoff 后 bar 一律不入本批**（D2）。

## §3 方法学【必填·冻结】

- **系统（单源复用禁重写）**：每 episode 独立窗=ignition bar 起 min(+750td, 截断面末)；`theme_persist_p1.simulate(closes, break_line=0.75, rebirth=1.25, rebirth_win=250, cost)` verbatim（**唯一改动=break_line 0.80→0.75·令链预留面**；rb/rebirth_win=正典 verbatim）——T+1 收盘入场→破线出场（收盘≤峰×0.75 次日收盘执行·计成本）→复活再入场（250td 内收盘≥谷×1.25 次日收盘·计成本）→窗末估值（B&H 同待遇）。
- **汇聚**：pooled 等权日收益（`theme_persist_p1._daily_rets`＋`_pool` 单源 import）——每 ride 资本线自入场日归一·同日多 ride 等权平均；judged 序列=分层×成本面 pooled 日收益（FULL=1,171 rides·SOLO=651 rides）。
- **被动基线（逐格）**：同窗同入场 B&H（`theme_persist_p1.bh_series` 单源·入场付同成本·窗末估值零出场成本）pooled Sharpe=skill line passive_override 逐格注入（P1 先例）。
- **judged cells 4（跑前写死）**：①TJ2-FULL-x1（实用面）②TJ2-FULL-x2③TJ2-SOLO-x1（**E28 alpha 面=主面**）④TJ2-SOLO-x2；x2=成本乘数 2.0（26.082bp/边压测面）；注册资格=主面 TJ2-SOLO-x1 过 G1'+G2 且 TJ2-SOLO-x2 成本压测面稳定（描述条款）；TJ2-FULL 过线=实用披露面不构成 alpha 宣称（E28）。
- **null 对照（RANDOM_LARGE_SAMPLE_LAW §3 ≥2000·子流律）**：**4 族 same-mask 随机点火 null**（分层×成本一一对应）——rep k：`np.random.default_rng([20589000, k])`（**新种子带随冻结窗注册**·带 [20589000,20591000) disjoint·净距 2000·全 registry 撞带扫描零命中·回执随 commit）→该分层每 episode 同码截断序列内均匀抽随机起点 s∈[0, len−wlen]→**同系统同成本 simulate（bl0.75 出场）**→pooled Sharpe；**K=2,000/族**；μ_null/σ_null 入 skill line·null_pool coverage n_values=2000/族。**null 族与 P1 null 族的独立性**：不同种子带+同出场常数=判线对 bl0.75 系统自校准（非 P1 判线复用——μ_null 随出场线上移的实证读数=§5(c) 预测面）。
- **账本（冻结）**：见 §0（batch_trials=8004=4 cells+4×2000 null draws）。
- **描述面（零判定宣称·不计 N_eff）**：①**邻域敏感腿 8**（bl0.75 headline 的常数邻域：{bl0.70-rb1.25, bl0.80-rb1.25, bl0.75-rb1.20, bl0.75-rb1.30} × 2 分层 pooled x1——E24-② 结构常数敏感性律：**P2 headline 必须过邻域稳定披露**；判线不因变体读数重设·若邻域某变体过线=照实披露+须另立预注册〔同 E24-ii 递归条款·禁本批内改常数翻案〕；P1 敏感腿 16 变体全体已披露留册=外层稳定面·本腿=内层局部邻域）；②LOO 留一 ETF 稳定性（796 折·sys−bh 符号一致率·≥0.80 稳定注记非门）；③点火日三分位（早/中/晚 pooled sys vs bh）；④政体分段（510300 t22 3-way proxy 标签·P1 分段腿 AttributeError 教训=**str/TS 类型先探后用**·补腿如实）；⑤famous16 成员归属重derive（披露面）。
- **成本口径声明【CN-C7】**：ETF 面 **V1=13.041bp/边**（`theme_persist_p1.COST_X1` 单源 import 禁手抄·runner 断言恒等 0.0013041）；往返=26.082bp；x2 面=26.082bp/边（往返 52.164bp）。
- **闭合族对号声明【M3】**：family_key=`theme_wave_ride_mechanical`——CLOSED_FAMILIES 零命中=open 照跑；负判决=M3 收口申报（§0.5/§1.4 判决语义先写死）。

## §4 判据【必填·跑前写死·禁看结果调线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=4, pool="core48", null_pool=<该格对应族>, n_trades, n_entries, passive_override=<该格同窗被动>)`**：全期 pooled Sharpe > skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))·**N_eff=ledger head＋本批 4**——append_ledger 先于判据·全量折减含 P1 8,004 与 sens 读数选择面）**且**平稳 bootstrap CI 下界 >0 **且** entries≥30（F6 双口径·FULL 1,171/SOLO 651 双过）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入；缺输入=诚实拒收。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线**且** DSR≥0.95（`deflated_sharpe_ratio` 原始收益跑·n_trials=N_eff·var_null_sr=该格族 σ_null²）**且** 家族 PBO≤0.25（`screening/pbo.py` CSCV 8 块·同族判面集=本批 4 cells aligned pooled returns）。
- 保留历史描述性条款（批级披露）：年化>0、OOS 双正（三分位符号稳定·描述口径）、回撤≥−35%、无崩年、成本压测 x2 面逐年稳定——描述条款不替代 v2 门。
- **判读结构（E28 执法·冻结）**：主面=TJ2-SOLO-x1——过线=深破线族升格候选成立（**0.75 族过 v2 门=theme 线机械翻译首个可注册候选**·注册资格走注册件另议·本批不注册只判）；TJ2-SOLO-x1 不过线=**theme 线机械翻译族连预留面诚实关线**（0.75 预留面耗尽·禁常数面第三批翻案——邻域变体过线照实披露仍须另立预注册·与本批判决独立）；TJ2-FULL 面无论过线与否=实用披露面（过线≠alpha 宣称）。
- **硬界设计三件套【D-20260925-01①】**：本批无数据腐坏检测类判线（消费冻结产物+库内面板·完备门=§2 六条）；max 硬界 N/A；极端日先验入 §5(d)。
- **新因子 t 面申报【M1】**：主面 TJ2-SOLO-x1 `t_from_sharpe` 派生槽位（SR_ann=§7 回填·T=pooled 期数·t=§7 回填）；判据=`m1_t_value_gate`（t≥3.0）；缺 t 面=missing_input 拒收。

## §5 跑前预测【必填·写死于跑前·跑后对账】

- (a) **SOLO-x1 方向（主面·本批真问题）**：pooled Sharpe 预测带 **0.5-1.5**（sens 读数 1.0203=带内锚——**该锚是同窗 in-sample 读数非独立证据**·判线将随新 null 族上移）；过线概率**低中 0.15-0.35**——先验张力=正面（sens 读数三常数一致高于 headline）vs 负面（μ_null 同出场线下移效应=深线 null 同样多吃 drift 段·判线水涨船高；sens 读数本身=16 变体披露面中的被选者=选择偏差朝上）；最可能结局=**Sharpe 显著高于 P1 headline 但仍不过重算后判线**（若 μ_null 上移幅度大于系统面增益即如此）。
- (b) **FULL-x1 方向**：集群面 1,171 rides 集中 34 日（2024-09-30 单日 413）——预测低于 SOLO 面（同日等权≈单日 beta 杠仓·whipsaw 大）且同窗被动同高（beta 双升）——过线概率低；两面差值=E28 分层价值二读数。
- (c) **null 带**：μ_null 预测 **0.35-0.65**（深线出场持有更久=随机窗同样多吃 drift→**较 P1 的 0.3734 上移**·上移幅度=本批判读的关键新读数）；σ_null 预测 **0.12-0.30**（更少出场=更平滑曲线→较 P1 的 0.1827 收窄带）；若 μ_null≥0.9 或 σ_null≥1.0=null 构造异常先查抽样面。
- (d) **极端日先验（三件套 (c)）**：同 P1 段（2015 救市/2016 熔断/2024-09-30 簇/2020-02-03）；**深线特有加注**：bl0.75 比 bl0.80 多扛 −20%~-25% 区间=崩盘段骑乘暴露**更高**（2015 连续一字跌停段按收盘成交的乐观偏差·x2 面部分缓解非根治——P1 §5(d) 同披露加深度注记）。
- (e) **出场普查**：censored 占比预测 **33-45%**（P1 实测 31.34% 基线+深线更少出场=**上移**）；break_line sells=100% of sells·rebirth buys=100% of non-initial buys·**非法 reason 0 容忍**（§0.6 门）。
- (f) **换手**：每 ride 成交次数预测 **1.5-4**（P1 实测 ~4/ride·深线更少出场再入=**下移**）；x2 成本拖累 pooled <2pp。
- (g) **邻域敏感腿**：4 变体×2 分层读数预测——bl0.80 邻腿≈P1 headline 族读数带（0.1-0.4·回接 P1 冻结面）；bl0.70 邻腿=未测新面（预测接近或低于 bl0.75·更深扛崩盘尾部）；rb 邻腿（1.20/1.30）预测沿 P1 sens 方向（rb1.30>rb1.20）；**判线不因变体读数重设**（E24-②）；若主面判负但邻域某变体过线=照实披露+另立预注册（递归条款·禁本批内翻案）。

## §6 产物

- runner=`scripts/theme_judge_p2.py`（**冻结后建**·subcommands selftest/run/finalize；结构=P1 runner 同型——`theme_judge_p1` 内核 import 禁重实现（dedup/strata/panels/null-chunk 模式/出场普查）+`theme_persist_p1` simulate/bh_series/_daily_rets/_pool/COST_X1 单源+science_gates g1_prime_v2/g2_registration_v2/t_from_sharpe/m1_t_value_gate/deflated_sharpe_ratio/append_ledger/cutoff_meta+screening.pbo.cscv_pbo；ProcessPool O-2355+BelowNormal+26 帽+预算帽 600s 诚实停；selftest=hermetic 合成断言〔**ks 铺瓦守卫腿**（r670 律）+checkpoint 扫描器实名配对+done 非空判定+种子带 extent-aware disjoint（r675 律：extent 从 registry derive 勿钝全量距离）+引擎零 import 图+CENSUS reason 集+sha16 恒等+确定性双跑〕）；
- probe=`results/_r676bma_theme_judge_p2_d6_probe.py`（已建·P1 探针内核 import·D6 ADMIT 0.3682 回执在盘）+`results/_r676bma_p2_seed_band.py`（种子带 disjoint 扫描回执）；
- results：`results/theme_judge_p2/theme_judge_p2_results.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+gates 块〔skill_line/bootstrap_ci/trade_gate/dsr/pbo 全输入〕+exit_census+邻域敏感/LOO/三分位/政体全表）＋`nulls_{face}.jsonl`（逐 chunk checkpoint）＋`d6_real.json`＋episodes CSV；
- 池面：`results/runnable_pool.json` entry THEME-JUDGE-P2（data_deps 字段 D-20261004-02①）；
- 本文件 §7/§8 回填；轮报告回执＋T-169 progress 行。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

## §8 批后复盘【必填·s7-T】
