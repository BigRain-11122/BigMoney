# E16_ALPHAGEN_RG_CENSUS_P1 —— alphagen slice-2 随机语法廉价普查批（预注册）

> 【状态：FROZEN——跑前 commit 冻结】E16 队列行 leg-2（supply-floor chain leg-4·外源目录 #17 通道件承接·N2 U3 ①全新语法重开候选）；bm-b r877 登记+认领同轮（T-18 CLEAR+T-19 seed gate hits=[] 双闸 rc0），leg-1 roster 探针已交付（scripts/alphagen_rg_roster.py selftest 15/15 + results/alphagen_rg/e16_roster.json sha16=1d06d218b2cbf870）。跑后只许回填 §7/§8，禁改判据禁重跑（工程修复重跑须双跑留痕）。
> 【批型】**测量普查批（measurement census）**——K=200 随机语法公式在股票面板上的逐公式 rank-IC 分布 + 同机械置换零校准；**零判据宣称、零注册效力、零出场机械、零引擎运行**。判读=licensing or killing RL build before training spend（T23 r840 slice-1 POSITIVE-with-riders 承接面 verbatim：holds→N2 U3 channel-1 drafting window 合法开窗；negative→RL 承诺停止，G2 fallback，学术引用面）。
> 【血统负先验披露律】A158 lineage negative prior verbatim：157/158 因子 |ICIR|<0.09 于 ETF/基金截面判负（results/_r840bmb_t23_alphagen_census.json）；GTJA 0/183 core48；WQ 0/82 strict；A9 0/9 单门；A10 0/16 组合。本批与先验差异面=搜索引擎（随机采样 vs 固定清单）、语料（股票宽截面 vs 48 ETF/基金）、目标（分布面 vs 注册）——三差异如实披露，先验不阻烧亦不借判。

## §0 批件身份【必填·跑前】

- 批名/批号：**E16-ALPHAGEN-RG-CENSUS-P1**（K_total=200=K_depth1 120+K_depth2 80；批内格数=每公式计入 N_eff 面见 §3 试验量）。
- 认领：explore 队列 E16 行（bm-b r877 登记+认领·T-18 CLEAR·T-19 hits=[]）；leg-2=同行延续非新认领。种子双键登记：`e16_alphagen_rg_gen`=20_620_000 + `e16_alphagen_rg_null`=20_620_100（seed_admit_gate rc0 双回执：20261011/20261111 roster 提案撞 2026xxxx 注册带〔t73_style_rot_s1=20261030/cn_core_sat_p1=20261080/cn_core_ddctl_p1=20261130/rev_osc_stock_p1=20261230〕被拒→净袋重选 20620000 带〔t23 20615000 族 +100 偏移范式〕·gate 是唯一权威）；F-04 声明=freeze commit 同窗 fleet/inbox/ MSG（防双机撞烧）。
- 部门归属：dept:研究（alphagen 范式评估线·T23 承接）。
- 算力预算：12 shards × workers=min(worker_cap(),8)（R31 车道律全分片 bm-b 烧）；单分片 est 5-15min（面板解析 ~2-4min 首次+缓存复用+16-17 公式×(eval+IC+200 nulls)）；RAM 峰 ~3GB（panel cache npz ~520MB mmap + 每 worker 触页 200-400MB）；BelowNormal（autofill 设置）；>5min 批律→池面烧录禁轮内代跑，per-formula checkpoint 跨击杀续跑。
- evidence_cutoff（前向锁盒 D2）=**2026-10-09**（面板完备末 bar 日·r877 盘实测）；cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层必带 `evidence_cutoff` + `science_gates.cutoff_meta` 字段。
- 池 entry：12 件 `E16-ALPHAGEN-RG-SHARD-{k}OF12`（k=0..11·status=ready·lane_owner=bm-b·workers_plan 8 BelowNormal）+ finalize=观测轮在 12/12 分片齐后执行（refuse-if-exists 幂等）。

## §0.5 禁开方向硬闸【必填·跑前·D-20260930-41 §1.2】

- 跑前实跑：`python Tools/banned_direction_gate.py --prereg research/E16_ALPHAGEN_RG_CENSUS_P1.md` → 回执记入冻结 commit message。
- 本批=随机语法测量普查（引擎面零承诺）；命中 BAN-__：无（跑前实跑回执为准）。

## §1 α 机制段【必填·D6——无机制段=批不受理】

- 四选一：**[x] 行为偏差**（主）——A158 算子族主体=动量/反转/量能/波动族，其交叉截面对应可命名行为面：追涨杀跌（ROC/MA/RSV 族）、处置效应与超卖反弹（QTLD/SUMP/RSV 族）、注意力与放量行为（CORR/CORD/VSUM*/WVMA 族）；代价支付者=截面上过度反应/反应不足的散户与追涨资金。**诚实披露**：随机语法普查不承诺单一机制——勾选框=该语法空间主导族先验，非本批宣称；本批唯一宣称=分布面 vs 同机械零校准的读数。
- **散户凭什么赢【§1.2】**：**行为**——日线级宽截面无速度/容量/制度优势可主张；散户优势面=纪律化系统捕获他人行为偏差（A158-TSGATE-P1 §1 同律延续），本批为测量面不新增主张。
- **同族相关性准入检查【D6】**：本批无注册轴——census 输出=分布面 only；`max|corr|≥0.7` 拒收在任何幸存者**注册**时执法（roster d6_law verbatim），非本批面。幸存者消费路线=时间序列门/输入特征 on core48（A158-TSGATE-P1+A10 先例·long-only T+1 成本）——judged 面 后续若开须另过 PREREG_TEMPLATE 正门+D6+出场轴显式门。

## §2 数据与面板【必填·跑前探针事实，非结果——r877 roster+r878 锚探针实测落稿】

- **roster 冻结源**：`results/alphagen_rg/e16_roster.json` sha16=**1d06d218b2cbf870**（substrate gate 158/158·grammar_space d1=1160·K/nulls/窗/种子提案·panel disk truth 5,219 件全 cutoff 2026-10-09·mini_timing 56.6min 单线程估=池烧量级）。
- **语法底座（vendored verbatim）**：`research/shortline/external/qlib_alpha158_loader.py` sha16=**814b7f7ab3d418ae**（qlib MIT·vendored commit a7d5a9b500de）——`scripts/alpha158_compare.py build_inventory()` parse 门 verbatim import（9 kbar+4 price0+29 rolling×5 窗=158 断言）。
- **普查机械（同机械律）**：`scripts/t23_random_grammar_census.py` sha16=**f5d146d1ad1f4eac**——rank-IC/置换零/family-max 判读/pa_lhb_ic rank_rows+ic_from_ranks+fwd_ret/composite_ic stats_block 逐字 import 禁重写；同机械差异面仅：语法（A158 29 算子 verbatim vs t23 缩减树）、窗（2018-01-01 起全窗 vs 尾窗 500 日）、K/B（200/200 vs 64/64）、账本口径（§3）。
- **数据锚面定义四元组【G-ANCHOR-FACE 律】**：
  - 日历轴=（①data/daily/sh510300.csv ②pd.read_csv usecols=[date] ③全史起算 ④截 ≤2026-10-09 后取 [首个 ≥2018-01-01 行−130, 末] 窗）——r878 探针实测：截后 3,490 行·首个 ≥2018-01-01 idx=1365·窗 2,255 行（warmup 实取 130·首 2017-06-26·末 2026-10-09）·census 行=2,125 日（2018-01-02..2026-10-09）。
  - 股票面板=（①data/astock_daily/per/<code>.csv（gitignored bm-b 车道件·R31）②pd.read_csv 直读 ③每员全史 ④窗内映射+130 行预热）——r878 探针实测：5,219 件·000001.csv 首 1991-04-03/末 2026-10-09·9 列 schema（date,open,high,low,close,volume,amount,outstanding_share,turnover）。
  - 宇宙=（①scripts/stock_face_furnace._universe() 单源 ②eligibility.csv 码表(6 位 0/3/6 前缀)∩b_layer_mask ok_static∩盘上文件 ③r878 探针 n=**3,514** ④P4_BATCH2 动态逐日资格条款 verbatim〔rev_osc_stock_p1 常量：close≥PRICE_MIN·amt20≥AMT20_MIN·listed≥LISTED_MIN·fresh≤FRESH_MAX·board≠other〕t23 load_panel 同律）。**eligibility <24h 快照旗漂移面如实披露**：roster leg-1 时点 eligible 旗∩ok_static=3,517；r878 复探同 join=2,531=快照日刷新致旗面缩（roster pit_disclosure 预言之坑）——**烧录宇宙钉死 sff._universe() 稳定码表面（不用 eligible 旗）**+panel cache 冻结（分片间同面保证）；burn 宇宙计数随件披露。
  - 前瞻收益=fwd_ret(close,1)（pa_lhb_ic 逐字·1d close-to-close·roster FWD pin）——信号日收盘信息集·T+1 无未来数据。
- **窗口与 evidence_cutoff**：census_window_start=**2018-01-01**（roster pin·窗内 2,125 交易日·est 9.11M 面板行 r877 实测）；面板一律截断到 2026-10-09。
- **数据完备门（fail-closed exit 2，不过即 VOID 拒烧）**：G-PANEL（t23 gate_face 逐字 import：status complete+盘真 5,219 对账+stale fresh）+G-CUTOFF（面板 cutoff==2026-10-09·日历末行==2026-10-09）+G-CAL（窗 2,255 行·warmup 130·census 2,125·首 2017-06-26·末 2026-10-09 逐位）+G-UNIVERSE（|uni|∈[3,400,3,600]·r878 探针 3,514 披露）+G-ROSTER（roster sha16 恒等）+G-SEEDS（SEED_REGISTRY 双键==20620000/20620100）——runner 探针与锚**强制同面断言**（探针加载路径与锚声明路径逐位比对，一面不相等=配置错配 VOID 拒烧）。
- **零网络**：全在库零采集；eligibility/b_layer_mask 只读消费。

## §3 方法学【必填·冻结】

- **语法（冻结）**：29 算子 × 8 底座输入 {open,high,low,close,volume,amount,vwap(=amount/volume),turnover} × 5 窗 {5,10,20,30,60}；depth-1=op(X,w) 空间 1,160；depth-2=op2(op1(X,w1),w2)（roster grammar_space verbatim·采样非枚举）。
- **泛化规则（唯一机械律·跑前钉死）**：vendored 模板的**全部价格类字段槽（$open/$high/$low/$close/$vwap 等）一律替换为采样输入 X；$volume 槽保持原 volume 序列 verbatim**（量能结构性辅助）。推论：单字段模板 X=close 时逐字复现 A158 原特征（ROC/MA/STD/BETA/RSQR/RESI/QTLU/QTLD/RANK/CNTP/CNTN/CNTD/SUMP/SUMN/SUMD 族）；双价格字段模板（MAX/LOW/RSV/IMAX/IMIN/IMXD/CORR/CORD/WVMA）产出泛化形（如 RSV(X,d)=(X−Min(X,d))/(Max(X,d)−Min(X,d)+1e-12)）——非 verbatim-A158 特征如实披露；depth-2 中 $volume 槽仍指原始 volume 叶非中间序列。
- **采样（确定性）**：公式 i∈[0,200)：rng=np.random.default_rng([20620000, i])；i<120→depth-1，else depth-2；input/op/w（+d2: op2/w2）取自 rng 流；**去重**=同流拒绝重抽直至公式串唯一（上限 10k 抽·不达则诚实保留重复并披露）；公式串逐字随件（n_unique_formulas 披露·t23 同律）。
- **NaN 政策（钉死）**：一切滚动算子**全窗规则**（窗内 d 个有限值才出值·t23 primitives 律：_roll_mean/_roll_std/_roll_sum/_roll_maxmin/_roll_corr n==d+方差>0 卫；比较算子任侧 NaN→NaN 禁 False 归桶）；因子/前瞻 NaN→当日截面剔除（eff=elig∧isfinite(F)∧isfinite(fwd)）；**MIN_CROSS=100**（逐日截面下限·t23 律）；**MIN_PERIODS=30**（stats_block 下限·t23 律）；公式 h1 有效期数<30=skip 诚实行。t23 全窗律与 a158_tsgate min_periods=1 律为**两冻结面各持其法**（跨面不互借·差异披露）。
- **IC 面（t23/pa_lhb_ic 逐字）**：逐日截面 Spearman rank-IC（rank_rows 掩码优先平均并列→ic_from_ranks n≥5 零方差→NaN）vs 1d close-to-close 前瞻；h=1 唯一口径（roster FWD pin·无 h5 副面）。
- **零校准（同机械零）**：B=**200**/公式（roster K_nulls pin）——per-date 同掩码因子秩置换（t23 `_permute_ranks_within_mask` 逐字·因子矩阵复用同机械面），rng=[20620100, idx, bj]；null_family_max_b=max_k |ICIR_{k,b}|（逐 draw b 跨公式配对·family-max 多重检验校正面）→ null_p95=B draws 的 95 分位（≥10 draws 才报·t23 律）。
- **判读线（跑前写死）**：`census_holds = observed_family_max_abs_icir > null_family_p95`——holds→RL build licensed（N2 U3 channel-1 drafting window 经 PREREG_TEMPLATE 正门合法开窗）；else→RL build killed（G2 fallback·学术引用面）。MAX_SKIP_FRAC=0.10（>10% 公式 skip=机制嫌疑 exit 2 诚实拒判）。
- **试验量与账本（roster pin 冻结）**：`science_gates.append_ledger("E16_ALPHAGEN_RG_CENSUS_P1", 200, file_name=…, evidence_cutoff="2026-10-09")`——trials=**K_total=200**（批账面·BACKTEST_PLAN ≤500/30d 预算内）；**nulls=校准非试验不计**（roster trial_budget_law verbatim；与 t23 先例 K+K·B=4,160 口径分歧如实披露——roster pin 为本批冻结权威）。E[FP] 名义=0.05×200=10。
- **出场轴显式门（O-20261001-1108）**：**测量普查面声明**——本批零持仓零出场机械（roster exit_axis verbatim："measurement census -- no position/exit machinery"）；三选一强制门绑定**后续幸存者 judged prereg**（出场轴三选一必填）；本批消费路线=core48 时间序列门/输入特征（A158-TSGATE-P1+A10 先例·long-only T+1 成本）。
- **闭合族对号声明【M3】**：family_key=**alphagen_random_grammar**——`science_gates.CLOSED_FAMILIES` 无此键（在册=open 照跑）；同族近邻披露：T23 slice-2 同机械 ETF 缩减语法面（t23_random_grammar_census·2018-10 尾窗 500 日·未烧=gated on 面板重建·现完备）与本批=不同语料不同窗独立假设；A158 ETF 截面判负族=先验披露非本批否证面。
- **幂等与确定性**：shard 产物在位=该公式 done-set 跳过（per-formula checkpoint jsonl 续跑）；finalize refuse-if-exists（finalize_already_landed 守卫·重跑零账本双记）；全批确定性零网络（唯一运行时元数据=generated/elapsed 独立段）。

## §4 判据【必填·跑前写死，禁看结果调线】

- 本批判据=§3 census_holds 单线（observed_family_max_abs_icir vs null_family_p95·family-max 校正）——**G1'v2/G2v2 不适用声明**：本批无策略收益序列/无 trade 流（测量普查批型·A158-TSGATE-P1 §4 同律），机械套用=类别错配。
- 硬披露门（非淘汰线·逐公式必带）：ic_mean/ic_std/ic_ir/ic_pos_pct/n_periods/null_abs_ir_p50/null_abs_ir_p95/skip 原因/n_dates；批级=observed_family_max、null_family_max_list、null_p95、n_ok/n_skip、n_unique_formulas、宇宙计数、elig 中位/极值逐日分布。
- 硬界设计三件套 (a)(b)：IC 面天然有界 [−1,1]（Spearman 构造界）→分布界即硬界，无裸 max 风险面；(c) 极端日先验见 §5。
- 全员判负=合法产出（普查面如实档案化·O-1820 三验③）。

## §5 跑前预测【必填·写死于跑前，跑后对账】

- P1：observed_family_max_abs_icir ∈ **[0.02, 0.15]**（A158 ETF 负底 157/158 |ICIR|<0.09 延伸到随机语法宽截面；股票截面噪声更宽→family max 上带放宽到 0.15）。
- P2：**census_holds=False 概率 >60%**（血统负先验+K=200 family-max 零校正 harsh 面；holds=意外惊喜面）。
- P3：skip 率 <10%（机制健全门 MAX_SKIP_FRAC 同值·超限=机制嫌疑拒判）；n_unique_formulas==200（去重后）。
- P4：≥90% 公式 |ICIR|<0.05（负底先验的面密度延伸）。
- P5：depth-2 平均 |ICIR| 不显著高于 depth-1（无复合增益先验；若显著=语法复合效应线索·descriptive 不判读）。
- P6（极端日先验·三件套 (c)）：窗内已知极端微观结构日=2024-09-24/09-30 政策脉冲、2025-04-07 外生缺口、2026-01-19 极端量日——全市场同向日截面区分度塌缩→单日 IC 趋 0/NaN，ICIR 影响有限；IC 有界无 max 硬界设计（§4 (a)）。

## §6 产物

- runner：`scripts/alphagen_rg_census.py`（subcommands：run --shard k --shards 12 [--workers N] / finalize / status / selftest；`__main__` 守卫=Windows mp 坑律；selftest=hermetic 离线腿：语法确定性/算子手值/NaN 政策/去重/置换确定性与同掩码不变性（t23 s5 律）/IC 机械/分片切分算术/门腿/账本块形状）。
- 池 entry：12 件 `results/runnable_pool.json` E16-ALPHAGEN-RG-SHARD-{k}OF12（ready·lane_owner=bm-b·workers_plan 8 BelowNormal·host_gates dir_nonempty data/astock_daily/per·data_gates=§2 完备门）。
- 产物：per-shard `results/alphagen_rg/shard_<k>of12.json`（逐公式统计+200 零 |ICIR| 向量·committed）+ finalize `results/alphagen_rg/CENSUS-2026-10-09.json`+`latest.json`（顶层 evidence_cutoff+cutoff_meta+判读面+audit 段）；机器本地件（gitignored）=per-formula checkpoint `results/alphagen_rg/ckpt/`+面板缓存 `results/alphagen_rg/panel_cache_2026-10-09.npz`（~520MB 叶矩阵·断点复用·deterministic rebuild）。
- F-04 MSG：freeze commit 同窗 fleet/inbox/ 声明（烧录车道 bm-b·防双机撞建 runner）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（一次定稿；工程修复重跑须双跑留痕如实记账；确定性引擎产物写 bug 的合法重执行口径≠结果重跑）

## §8 批后复盘【必填·s7-T】

- 预测对账（P1-P6 对/部分/错）＋门禁链损耗账（`results/gate_attrition.json` 追加一行·若适用）＋判线当批读数（observed_family_max 与 null_p95 数字）；
- 回执入轮报告＋CODELY.md 行级追加；幸存者面：holds→N2 U3 channel-1 drafting window 开窗指针（PREREG_TEMPLATE 正门）；killed→RL 承诺停止+学术引用收口。
- **全起点分布【§1.3】**：不适用声明——测量普查批无策略起点面（无回测曲线；全窗单点 IC 分布即本批「起点」面·census 窗 2018-01-01 起全窗钉死）。
- **试验量归因【§1.4】**：本批新增试验数=**200**（计入 ≤500/30d 预算·与 E15 重估面 0 增量同窗）；一句话归因：RL build 训练承诺前的最后一道廉价普查闸（K=200 采样≈语法空间 1,160 深度1 空间的 17%+深度2 采样面），烧 200 格省 RL 训练量级算力=典型廉价初筛先行律（TRIAL_LABOR_LAW）。
