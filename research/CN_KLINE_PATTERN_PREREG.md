# CN_KLINE_PATTERN_PREREG · A股 K 线形态面 judged 判决批（T-87 s2 队列 #3·行 13 形态识别面）

- 令链：CEO 流派学令 O-20260926-0926 → O-20260926-2320/2325 淬炼+全域解锁令（RANDOM_LARGE_SAMPLE_LAW v1.0 全律绑定）→ O-1721 借力律 folklore 门 **PASS（R289·`research/digests/DIGEST-20260927-kline-folklore.md`）**：正典 4 形态族 ①定义强（同花顺/分析家终端公式级趋同）②入场中 ③止损中可编码；④出场/⑤仓位无社区共识=**工程冻结参数显式披露、禁称 folklore 出品**（边界披露 a）；负面形态（乌云盖顶/三只乌鸦）在 A股 T+1 多头工具域=**出场/回避信号面禁做空宣称**（边界披露 b·O-1132 日线可表达律）；终端内置形态=高拥挤知识面=**幸存者必须过 RANDOM_LARGE_SAMPLE_LAW 大样本门+宣称≠验证**（边界披露 c）→ `research/SCHOOL_SUPPLY_S1.md` §二 队列 #3（既立队列零发明）。
- 批性质：**judged 判决批**（非淬炼勘探面）——变体轴系=canonical 4 形态族 folklore 冻结面（早晨之星/红三兵=多头入场面；乌云盖顶/三只乌鸦=负面出场信号面），编码忠实核=终端公式逐条映射，冻结于此，批内零选优。
- 判负族边界披露（判负不重开律）：网格腿=GRID-SLEEVE-P1 判负≠本批（本批非网格非振荡收割，形态事件制）；WILD-S1 打板族=T+1 事件面同域但**涨停封板事件≠K线形态反转事件**（机制面不同·D6 披露列）；微盘（2024 崩塌判负）/期货 CTA ×3/T0=零涉；老鸭头族=源面未达不判不编（DIGEST §三）。
- 反重复注记：仓内 K 线形态 runner/prereg 全档零命中（rg 2026-09-27 03:5x·`早晨之星|morning.?star|红三兵|three.?white|乌云盖顶|dark.?cloud|三只乌鸦|three.?black.?crow` 唯命中=本批族件）；PRODUCT_MATRIX 资产轴=股票在册轴内、时间轴=短线波段段，无新维度开线。

## §0 批件身份【跑前】

- 批名：`CN_KLINE_PATTERN_P1` · N_eff=**2007**（7 judged cells ×1 判面 + 2000 null draws；x1 成本=披露列不计 N，CN 家族先例 CN_TREND_ETF_P1）
- 认领：任务板 T-2026-09-26-87（claimed_by bm-a·s2 队列 #3 续作切片）；F-04 MSG 先行（`fleet/inbox/MSG-20260927-0355-bm-a.md`·bm-a R292）；部门 dept:研究+策略
- 算力预算：est 60-180min wall（事件合计 ~92k cohort-holds × 2000 null draws 向量化 + 虚拟起点 census；workers=4 BelowNormal）；**按 O-1137 真实载体供给律池提交**（池 ready=0=饿池载体·O-20260926-2320 24h 淬炼窗内）；per-cell+per-null-shard checkpoint 幂等（>10min 批池化跨轮）。

## §1 α 机制段【D6·四选一】

- [x] **行为偏差**：①早晨之星/红三兵=恐慌 capitulation 后的反转确认面——付出代价方=底部恐慌割肉的过度反应散户（早晨之星·13日新低双价+跳空十字= capitulation 结构）与确认前不敢进场的反应不足者（红三兵·三阳确认后追涨盘提供后段 drift）；A股散户羊群+短期反转>动量实证（s2 slice-A 在册）=该行为面的仓内证据侧写。②负面形态出场面=处置效应收割（乌云盖顶/三只乌鸦=顶部结构确认，纪律性出场规避「不卖亏钱股」处置效应持仓者的后续损失）。T+1 多头约束下形态溢价归于形态日收盘后 T+1 开盘入场的耐心确认方；**禁做空宣称=边界披露 b**。
- **同族相关性准入（in-runner D6 面）**：逐 judged cell 对在册 6 CE 成员（ew6 canon member_run 日收益）max|corr| + 批内两两 |corr|；**≥0.7 vs 在册成员=拒收**。个股形态事件袖 vs ETF/组合 CE 成员预期 <0.4（跨工具域+事件稀释），数值批报告 D6 表逐对列；judged-negative 家族（WILD-S1 打板 25 臂/CN-TREND/CN-SOE）=advisory 披露列（已闭族不作准入面）；T-47 截面动量=机制面不同（截面相对强弱 rank≠形态 shape 事件），披露不设门。

## §2 数据与面板【跑前探针事实·冻结引用件 `results/cn_kline_probe.json`】

- 面板：`Money02/data/bars/*.parquet` 5222 只 A股个股日线（OHLCV+amount·只读消费·**WILD-S1 先例同源同面**）；**cutoff=2026-09-22（D2 前向锁盒·Stage-A 末 bar·与 WILD-S1 同 cutoff）**；cutoff 后新 bar 不回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta('2026-09-22')`（缺字段=science_audit C2 VIOLATION）。
- **宇宙（冻结过滤器·机械再derive 禁手抄名单）**：b_layer ok_static==True ∧ rows≥500 ∧ last==2026-09-22 ∧ med(amount, 末20bar)≥¥30M → **universe_n=3106**（探针实证 2026-09-27 03:5x·skip 台账 not_ok 1705/rows 163/last 5/liq 243；board 分布在引用件）。诚实披露：①ok_static=**当前时点掩码**近似历史 ST/亏损面（WILD-S1 同面先例）；②末20bar 流动性=**当前流动性面**（historically-illiquid-then-liquid 名员含入=幸存者相邻面如实注记）；③bars=**当前在册上市公司面板=退市股缺席=幸存者偏差面**（WILD-S1 同面冻结披露，判读按此口径）。
- **数据完备门（不过即拒批 exit 2 零产物）**：universe re-derive==3106 ∧ 逐件（D2 截断至 cutoff 后）末 bar==2026-09-22 ∧ 引用件在位 ∧ bars 文件数==5222。
- **形态事件普查（冻结引用件 census 面·编码=本节冻结）**：
  - 早晨之星 MS=1,342 事件/963 名员/673 事件日，活跃 1994-04-08→2026-09-21，截面峰 21 员/日（2016-05-20），p99=1 员/日；
  - 红三兵 TWS=21,518/2,943/3,682 日，1992→cutoff 当日，截面峰 **256 员/日（2024-09-30 政策脉冲）**；
  - 乌云盖顶 DCC=35,270/3,066/5,023 日，截面峰 **754 员/日（2024-02-28 微盘崩）**；
  - 三只乌鸦 TBC=**14 事件/35 年=严忠实编码下统计性面死**（诚实披露：AA=REF(HIGH,2)==HHV(30) 双价严合流+三阴逐级收低+开盘入实体+收近最低的联合=超稀有；页内 A2 公式排版截断如实不编（DIGEST §一））→ 出场联合面 DCC∪TBC 中 **DCC=主操作面**、TBC=advisory 联合员（≤14 员增量零机制影响），TBC 单独 face 判读行=insufficient-sample 如实旗。
- 工程冻结参数表（EF·非 folklore·边界披露 a）：光头收市 close∈区间顶 30%（HEAD_TOP=0.3）；实体等长 max/min body≤2.0；升势后文境 c[d-1]≥1.05×c[d-6]；收近最低 close∈区间底 30%（CROW_TOP=0.3）；长阳 body≥50%×range（YANG_BODY_FRAC=0.5）；持有窗 H=10td（FIX cells）/H=20td cap（BEAR cells）。全部数值源于叙事忠实的**本批工程冻结**，禁回溯归因 folklore。

## §3 方法学【冻结】

- **信号编码（全部 close 面·探针引用件=唯一编码权威·逐条终端公式映射）**：
  - MS（信号日 d=修复长阳日·doji 日 e=d-1）：e-1 长阴（c<o）∧ a1[e]（|c-o|/o<0.005 ∧ (h-l)/|c-o|>2·同花顺内置式）∧ a2（近2日恰一次 a1）∧ a3（l[e-1]==LLV(l,13 ending e) ∧ c[e-1]==LLV(c,13 ending e)·同花顺双价新低式）∧ 跳空低开 o[e]<c[e-1] ∧ d 长阳（c[d]>o[d] ∧ body≥50%range ∧ c[d]>c[e-1] 收复）；d 收盘发令。
  - TWS（信号日 d=第三兵）：三阳（逐员 c>o）∧ 开盘/收盘逐升 ∧ 三员光头（EF 0.3）∧ 实体等长（EF ≤2.0）∧ 底部邻接=前员阴线（c[d-3]<o[d-3]·EF）；d 收盘发令。
  - DCC（信号日 d）：前员阳 ∧ o[d]>h[d-1] 高开 ∧ c[d]<o[d] 阴 ∧ c[d]<(o[d-1]+c[d-1])/2 入阳体中点下 ∧ 升势文境（EF 5%/5d）；成交量放大=folklore 强化注记非定义（不编码·披露）。
  - TBC（信号日 d=第三鸦）：三阴 ∧ AA（h[d-2]==HHV(h,30 ending d)·分析家式）∧ 逐级收低于前低（c[i]<l[i-1]）∧ 开盘入前实体 ∧ 收近最低（EF 0.3）；A2 截断不编（§二披露）。
- **执行（T+1 禁未来数据）**：信号 d 收盘 → 入场 d+1 开盘；一字/近涨停开盘=不可成交拒单（open/prev_close−1 ≥ 板型阈−0.002·WILD-S1 LIMIT_OPEN_TOL 同式）**计数不弃账**；停牌→滚动至首个可成交开盘（WILD-S1 先例）；出场同 T+1 开盘式。板型阈值 main 0.0975/创科 0.1975（创 20cm 自 2020-08-24·科自 2019-07-22·WILD-S1 冻结面）。
- **组合记账（WILD-S1 bucket 语义冻结复用）**：资本入 H 桶；事件日 t 的 cohort（=当日全部发令名员·等权内构·无成员帽=flood 面如实）于 t+1 开盘部署；cohort 净收益均摊记入其 H 持有日；止损臂=触发日实际出场记账（残余桶回收）；cell 日收益序列=活跃 cohort 日收益均值（等权构造）。
- **止损（folklore ③忠实核·形态极值惯例）**：MS 止损=doji 日低点 l[e]（形态另一侧极值）；TWS 止损=首兵日低点 l[d-2]；触发=持有期内 close<止损位 → 次开出场。
- **负面形态出场（边界披露 b·long-only 域）**：持有名员上 DCC∪TBC 发令 → 次开出局（仅平仓·零做空零反向腿）；BEAR cells H=20td cap。
- **成本口径**：V2 单源（`alloc_backtest.side_cost_v2(gross, adv20)`·ADV20=amount 滚动 20 均值·股票面直算·佣金含最低费用面）；**judged face=x2 恒开**（`side_cost_x2`·V2 各分量加倍·CN 家族先例）；x1=披露列。成本作用于每笔名义（入场/出场双边）。
- **null 对照（RANDOM_LARGE_SAMPLE_LAW §3）**：K=2000 draws；每 draw=逐 cell 同掩码随机事件面——(universe×有效日) 均匀随机抽 N=该 cell 实测事件数的 (名员,日) 对→同 H 同执行同成本同 bucket 记账→null cell Sharpe；逐 cell own-null 池 2000 值（CN 家族「逐腿 own-null」先例）；seed=`SEED_REGISTRY['cn_kline_pattern_p1']`=20275100+k（k<2000·跑前登记·band 20275100..20277100 构造性零碰撞：census_fusion_s2 带顶 20274900 与 census_fusion_s2_unc 20275000 seed-sequence 基之上·rg 全档扫描留痕）；skill_line=own-null 池分位；双法并列：block bootstrap 2000 draws（块长 10）+ sign-flip 2000 draws，p 值双报。
- **账本**：`science_gates.append_ledger('CN_KLINE_PATTERN_P1', 2007, 'cn_kline_pattern_p1', evidence_cutoff='2026-09-22')` dict schema 唯一禁手抄 prev。
- **虚拟起点面（RANDOM_LARGE_SAMPLE_LAW §2.1）**：cell 组合日序列全史枚举 census——起点日序号∈[200, T−126]，每起点 126 交易日窗（收益/胜率/beat vs 宇宙 EW 代理）；分段 4 类（bull/bear/deep-bear/chop·sse 态打标同 REV_OSC §2.1 冻结面）逐列；任一分段起点数<500=insufficient-sample 如实注记。**随机分窗（§2.3）**：train/validation 随机划分 ≥100 次 + walk-forward 5 顺序折叠双证。

### §3.1 judged 格表（7 cells，判面 x2，全冻结）

| cell | 入场 | 出场（先到先计） |
|---|---|---|
| MS-FIX10 | MS | H=10td（④工程冻结） |
| MS-STOP10 | MS | H=10td ∨ close<l[e] 止损（③folklore 形态极值） |
| TWS-FIX10 | TWS | H=10td |
| TWS-STOP10 | TWS | H=10td ∨ close<l[d-2] 止损 |
| MS-BEAR | MS | 持有名 DCC∪TBC 次开 ∨ H=20td cap |
| TWS-BEAR | TWS | 持有名 DCC∪TBC 次开 ∨ H=20td cap |
| COMBO | MS∪TWS（同日并集 cohort） | 持有名 DCC∪TBC 次开 ∨ H=20td cap |

## §4 判据【跑前写死·共享库调用禁手抄判线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=2007, pool='stock_b_layer', n_trades, n_entries, null_pool=<本批 2000-null own 池>)`**（pool 口径=WILD-S1 股票域先例）：全期 Sharpe > skill_line_v2 ∧ 平稳 bootstrap CI 下界>0 ∧ entries≥30（F6 双口径）；逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：DSR≥0.95（deflated_sharpe_ratio 原始日序列·禁 dsr_from_stats 充数）∧ PBO≤0.25（screening/pbo.py CSCV 8 块·7臂家族矩阵）。
- 批面要求（披露列）：annualized>0 ∧ OOS（≥2025-01-01·composite_ic.IS_END 共享分割）双正 ∧ maxDD≥−35%。

## §5 跑前预测【写死于跑前，跑后对账】

1. **反转>动量的 A股实证外推**：MS 系（capitulation 反转）毛面优于 TWS 系（确认延续），但成本后皆落 Sharpe 0.0-0.5 薄带、<0.70 注册线——**判负照报概率高**（形态面=高拥挤全民知识·边界披露 c；claim≠verify）。
2. TWS 系事件数（21.5k）≫MS 系（1.3k）→ TWS cells 的 CI 更紧、trade gate 全过；MS cells entries≥30 过门但 n 小（1,342）统计力弱如实。
3. 止损/负面出场修饰面：STOP10 与 BEAR 相对 FIX10=maxDD 改善 10-30%（顶部结构早出），Sharpe 变化 ±20% 带内（whipsaw 对冲）——不改变过线/不过线的大类判读。
4. **极端日先验（flood 面实证已锚）**：TWS 截面峰 2024-09-30（256 员·政策脉冲日 T+1 追高=脉冲回落风险）、DCC 峰 2024-02-28（微盘崩）；2015-06/07、2016-01 熔断窗=MS 系 cohort 涌入日；census deep-bear 分段预期 insufficient-sample 旗（CN-TREND 同型 327 先例）。
5. x1 面净 Sharpe ≥ x2 面（事件制中频 churn：V2 双边成本侵蚀毛收益 10-30%）。

## §6 产物

- `results/cn_kline_pattern/p1_results.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+D6 表+judged 判读+N 计数+TBC insufficient-sample 旗）；`results/cn_kline_pattern/cells/*.json|npy` per-cell/per-null-shard checkpoint；census+§2.3 分窗产物；`results/gate_attrition.json` 追加一行（**entries 列表面·r248 律**）。
- runner=scripts/cn_kline_pattern_p1.py（冻结 commit 后建·R99 序：prereg 冻结先于 runner build 先于任何 run；selftest 子命令=离线自检 hermetic fixtures）。

## §7 跑后实证【跑前为空——占位纪律】

（一次定稿 2026-09-27 R293 bm-a autofill burn pid 56364·elapsed 353s·`results/cn_kline_pattern/p1_results.json`：**7/7 cells 判负照报**——x2 判面全期 Sharpe MS-FIX −0.7145/MS-STOP −0.6385/TWS-FIX −0.3811/TWS-STOP −0.4363/MS-BEAR +0.1218/TWS-BEAR +0.4000/COMBO +0.2768；skill line（own-null 校准）1.9486（TWS 系）/2.6603（MS 系）/3.5701-4.0655（BEAR 系）全数 line_ok=False ∧ bootstrap CI 下界≤0；DSR 全 ≤0.015；family PBO 0.4429>0.25；批面 cells_ok 7/7 False（ann>0∧OOS>0∧maxDD≥−35% 三重挂：maxDD −97%~−100%）；entries 面 MS 系 ~1.3k/TWS 系 21,192/COMBO 22,532 filled（trade gate 过·事件面健康）；D6 max|corr| vs ew6 canon 全 ≤0.1295 无拒收（事件稀释+跨工具域如 §1 预判）；null 池 mu 0.4229（MS-H10）/0.8645（TWS-H10）/1.3527-2.0986（H20 系）——**A 股个股 35 年随机时点同持有面的漂移本底即 ~0.4-2.1 Sharpe，形态面判负=负期望+跑不赢随机本底双挂**。ledger 200,396=198,389+2,007 单计 ✓；attrition 行 entries 列表面 ✓。）

## §8 批后复盘【必填·s7-T】

（2026-09-27 R293 定稿。**§5 五预测对账**：①「MS 毛面优于 TWS+双落薄带+判负照报概率高」→ **命中**（MS 系 Sharpe −0.71/−0.64 优于 TWS 系 −0.38/−0.44 但全负；claim≠verify 实证：正典 4 形态在 T+1 开盘保守代理+x2 成本下零 α）；②「TWS 系 CI 更紧、trade gate 全过；MS n 小如实」→ **命中**（entries 门全过；MS 事件面 1,342 统计力弱如实注记）；③「STOP/BEAR 相对 FIX=maxDD 改善 10-30%、Sharpe ±20% 带内」→ **半中**（STOP 臂 Sharpe 变化 +10%/−15% 带内 ✓；但 maxDD 无改善（−97%~−100% 全线·负漂移 35 年复利下 DD 面由 ann 决定非出场修饰）、BEAR 臂 Sharpe 变化远超 ±20% 带（MS −0.71→+0.12、TWS −0.38→+0.40 符号翻转）=负面形态出场是本批最大修饰面、超出预测幅度如实记）；④「极端日/deep-bear insufficient-sample」→ deep_bear 分段 beat 0.2552 在册（census 分段起点数未触 <500 旗的主面·na 段如实）；⑤「x1≥x2」→ x1 面见 cells_summary.csv（成本减半不改变判读·judged=x2 冻结面）。**判线读数**：own-null 校准线 1.9-4.1 高企=随机本底含长持有漂移面，G1' 判负的语义=「形态时点择股不如随机时点」——判负不重开律生效：K 线形态面（canon 4 族·本编码·本执行域）**判负关槽**，新证据=新预注册（O-1132 域内变体/编码变体须另立 prereg 禁本批翻案）。**gate_attrition**：own 行在册（entries 列表面·r248 律）。**回执面**：T-87 s2 队列 #3 闭环（freeze cbf6c93c→runner f7efdec3→burn 353s→判负定稿全链 R99 序合规）；后续=①post_review criteria 注册（CN_KLINE_PATTERN_P1 判据锚 §7/§8 稳定产物件·下轮 P0 候选）②SCHOOL_SUPPLY_S1 队列下一候选按 R99 节律。）
