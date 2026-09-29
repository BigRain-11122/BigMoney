# T-101-V4-A11-XSELECT 预注册 —— 五员输入特征「横截面选择组合器」首测（v4 政体门臂·输入特征消费面子线·非择时面）

> 血统：A10 §8 下游指针兑现（「C1 输入特征面=588000 门族供 T-101 v4 后续『输入特征组合器』（非择时面）消费；择时臂面勿再立项〔三子线合流判决 r442〕」）。A2/A9/A10 三子线已证伪=单门与等权门组合的**时间序列择时用法**；本批=同特征源在**横截面相对选择用法**的首测——结构性新面：组合器始终满仓（无市场进出场=零择时成分）、特征差分只决定**持有哪 k 员**；共同市场 beta 在横截面内抵消，与择时线的 beta 镜像机制（d6_sg 0.83-0.90 判例）结构性不同。
> 状态：**FROZEN——冻结于跑前·2026-09-29 19:2x·bm-a r443（起草机同轮一次冻结·A9/A10 臂线批先例：一次冻结即烧·非 TRIAL_LABOR 波线协议面）**。本冻结 commit 同窗含 SEED_REGISTRY 两键注册（R250 一步律·20315000/20315500 三步律过：120 int 基零撞·band 20315xxx rg 空〔命中=Money0923 volume 数值巧合 t34/69 批先例面+本批 MSG 自身〕·首元素 0.1057/0.4203 互异）+runner+MSG-1924 声明。

## §0 批件身份【必填·跑前】

- 批名：**T-101-V4-A11-XSELECT**·批内格数：**24**（宇宙 2 × 特征 3 × top-k 2 × 成本 2）；null 对照 K=200/格·另计不膨胀策略数。本批=**试验判决批**（入 trials_ledger，batch_trials=24）。
- 部门归属：dept:研究（链条研究线·T-101 v4 政体门臂 A11 位）。
- 算力预算：est <2 min 单进程（2 宇宙横截面回测 + 4,800 随机选择 null + 双 nulls B=2000/P=2000 + PBO CSCV 2×12 配置）—trivial compute in-round 合法（O-2100·A10 101.2s 同族先例）；worker 数 1；批报告必带 audit 段。
- 车道：**bm-a**（五员面板 data/daily in-repo·lane-free·本机直跑·r441/r442 同车道延续）。
- 语法查重/防重跑：横截面 top-k 选择用法=**未被消费面**——A2/A9=单门 0/1 全仓择时（已关）；A10=门态等权连续权重择时（已关）；MF_ROT_S1=**个股**资金流 Top3 轮动（r178 冻结·不同宇宙不同特征源=非同语法·先例披露）；W10 MOM 轴=个股语法门（bm-b 在飞·非 ETF 五员横截面）；本批=五员 ETF 宇宙门/因子特征差分横截面用法首测（非同语法重跑）；同语法重跑须新 prereg（本冻结 commit=防重跑锚）。

**§0-X 横截面选择组合器形态【冻结·禁搜参·全冻死】**：
- **宇宙**：U5=冻结五员 O-1555={510300, 510050, 510500, 512100, 588000}（主面）；U4={510300, 510050, 510500, 512100}（深度腿——588000 上市 2020-11 使 U5 共同可判窗仅 ~5 年·U4 腿把横截面可判史拉深至 ~9.5 年·两腿分格独立判）。
- **特征（三面·冻结定义·probe 157 因子表单源）**：f_rsv30=RSV30 原值**升序**（最超卖员 rank 1·横截面回归面）；f_c2=17 门库（GATES17 逐字）开态算术均值**降序**（门族聚合态最开员 rank 1·A10 C2 同源特征横截面化）；f_roc20=ROC20 原值**降序**（动量最强员 rank 1·反向对照面——方向未知先验下双面披露·非独立机制宣称）。
- **选择规则**：每 20 交易日（stride-20·gate_verify 同律）再平衡日 t 依特征序取 top-k 员等权（k∈{1,2}）；非再平衡日权重恒定；**始终满仓**（Σw=1 恒成立·现金腿 0% 如实）。
- **禁搜参声明**：特征三面/stride-20/top-k 二值/等权=全冻结；无任何阈值、排序加权、再平衡节奏搜索；U4 腿=深度披露面非参数扫描。

## §1 α 机制段【必填·D6】

四选一：**[x] 行为偏差环**——五个高相关宽基/科创 ETF 间的相对超买超卖差分触发横截面过度反应-修正（reversal premium 由追逐同族动量者支付）；本批子假设=**横截面条件信息差分**：成员间门/因子状态差携带下一期**相对**表现信息（时间序列择向=A2/A9/A10 三子线已证伪；横截面差分面从未测过）；若选择组合器的全量风险调整表现不过批自**随机选择** null 池 → 横截面选择子线判负，输入特征路线残余去向=预测器/条件面（非选择面）。f_roc20 面=反向对照（延续方向）·判读时与回归面同批判。

**同族相关性准入检查【D6·跑前预声明】**：
- **vs 宇宙成员 B&H**：top-1 恒持单员格与被持员 B&H corr≥0.7 **结构高发主预期**（五员同类资产 chronic rho 0.71+〔A6 实测〕+恒满仓单持=成员 beta 直通）——预声明相关性来源论证：选择组合器与成员 B&H 的高相关=**类 beta 结构性同源**（恒满仓持有该类资产的定义性结果），其独立信息含量=**选择差分**，由批自随机选择 null 池隔离测量；max|corr|≥0.7 仍按 D6 律 REJECT（注册资格面·不阻断科学判决线）。
- **vs A10 16 格**（同门态源连续权重线·f_c2 特征同源面）：runner 经 a10 模块 import 复算 A10 格日收益做 pairwise max|corr|≥0.7 → REJECT（beta 重复）。
- **vs A9 单门 9 格**（r441 冻结表·fv 机器件复算）：同上 REJECT 律。
- 批内 24 格 |corr| 矩阵逐格落 JSON（披露不 kill·r231 先例）；vs 在册六员 D6 绑定门=s4 intake 切片 defer 注记（paper_export 无日序列·r434 实证·A10 同法）。

## §2 数据与面板【必填·跑前探针事实】

- 宇宙成员同 §0-X；数据锚四元组（G-ANCHOR-FACE）=`data/daily/sh<码>.csv` + `tpl.load_panel` 单源（cutoff 截断+尾行断言内建）。
- **冻结行数锚（@2026-09-28·r231 同表·A10 同锚）**：510300=3486 / 510050=5251 / 510500=3289 / 512100=2405 / 588000=1425；尾行一律 2026-09-28（runner 断言·fv.ANCHOR_ROWS 逐字）。
- **共同可判窗（横截面构造的代价·如实披露）**：U5 全员共同+特征可判（RSV30∧ROC20 notna ∧ 17 门 rolling(252,min_periods=120) decidable）首日 ≈2021-05（588000 行 120+）→样本 ≈1,3xx td；U4 ≈2017-05（512100 行 120+）→样本 ≈2,2xx td；**两腿 IS 面（≤2016-12-31）=结构空窗**（共同可判窗后于 SPLIT）——G1' 判据面不受影响（全期 Sharpe+skill line+trade gate），OOS 超额面=全窗即 OOS 如实记。
- **evidence_cutoff=2026-09-28**（D2 前向锁·A10 同面）；cutoff 后新 bar 不回流；结果 JSON 顶层必带 `science_gates.cutoff_meta`。

## §3 方法学【必填】

- **执行机器零重实现（import 单源）**：`t101_v4_a2_prescreen`（tpl：load_panel/regime_segment/sharpe/ann_ret/max_drawdown）；`a158_tsgate_probe`（probe：alpha158_factors/gate_universe·157 因子冻结表）；`t101_v4_a158_fv`（fv：dual_nulls/window_grid/WINDOWS/GATES17/ANCHOR_ROWS）；`t101_v4_a10_regimecombo`（a10：combo_position/combo_returns 语义镜像+C1_FAMILY——A10 格 D6 复算源）；`science_gates`（sg：g1_prime_v2/g2_registration_v2/deflated_sharpe_ratio/append_ledger/SEED_REGISTRY）；`screening.pbo.cscv_pbo`（CSCV 8 块冻结）。
- **横截面连续权重回测语义（本批新面·冻结定义·A10 连续权重口径逐字扩展）**：再平衡日 t 特征排序→w_raw,t（top-k 员各 1/k）；生效权重 w_eff,t = w_raw,{t-1}（T+1 开盘代理·同 tpl.shift 语义）；日收益 r_strat,t = Σᵢ w_eff,i,t × r_i,t（r_i=成员 close-to-close）− Σᵢ|w_eff,i,t − w_eff,i,{t-1}| × cost_rate（初始建仓 |Δw| 计成本）。
- **成本口径（A10 保守冻结逐字）**：cost_rate=0.001/单位 |Δw|（0.1% 往返/满换手=0/1 门控口径 2 倍保守面）；×2 压测腿=0.002。SPLIT=2017-01-01（IS 结构空窗披露见 §2）。
- **trade/entries 口径（G1 双口径·冻结）**：trade event=Σᵢ|Δw_eff,i,t|≥0.10 的交易日数（A10 TRADE_EVENT_DW 同值·top-1 换员=2.0·top-2 换一员=1.0 均入事件）；n_entries=OOS（≥SPLIT）trade events；entries_ok=≥15（tpl.MIN_OOS_ENTRIES 同值）。
- **随机选择 null（批自 null 族池·本批核心对照）**：K=200/格·每 null=同再平衡日历上从宇宙均匀随机抽 k 员等权→同构造同成本回测（择时成分=0 同构·唯一差=特征序 vs 随机序）；seed 基=`SEED_REGISTRY["t101_v4_a11_xsel_scrnull"]`=**20315000**（rng([20315000, cell_idx])·本批注册）；4,800 null Sharpe 全收=批自 null 族池（P4_EXT_TILT 语义；**nan-safe 统计 r442 律**：有效集统计+nan_excluded 计数披露——随机选择族不产全零序列但同律防御）。
- **双 nulls（W1 `_dual_nulls` 语义逐字）**：块自助 B=2000·block=20 circular（均值 CI）；符号翻转 P=2000（双侧 p）；seed=[`SEED_REGISTRY["t101_v4_a11_xsel_unc"]`=**20315500**, cell_idx]·cell_idx=冻结 24 格表序。
- **虚拟起点窗网格（三窗·描述面恒带）**：{6m=126, 12m=252, 24m=504}；起点=每交易日 p∈[窗首+1, n−w]（W1 同径日频起点·重叠窗如实披露）；每窗策略收益 vs **同宇宙 EW-B&H 同窗收益**（逐格批自被动=REPO_CALENDAR_P2 语义·EW 合成指数=(1+r_ew).cumprod() 披露构造）；段=起点日 510300 MA200 政体（bear/bull/chop·tpl.regime_segment 逐字）。
- **G1' v2（共享库禁手抄）**：`sg.g1_prime_v2(sharpe_full, returns_full, batch_cells=24, n_trades, n_entries, null_pool=批自 null 族池, passive_override=同宇宙 EW-B&H 同窗 Sharpe)`——skill line N_eff=ledger 活头+24 数目驱动。
- **DSR**：`sg.deflated_sharpe_ratio(returns_full, n_trials=本批 append 后活头)`（跨波不重置·禁 dsr_from_stats 充数）。
- **G2 注册资格 v2（共享库）**：`sg.g2_registration_v2(g1_pass, dsr, pbo)`。**PBO 族面（跑前冻结）**：族=每宇宙「本批已试配置全网格」=3 特征×2 topk×2 成本=12 配置（≥8 可判）→ 判格承本宇宙族 PBO；两宇宙分族判。
- 分段恒带：bear/bull/chop OOS 逐段年化（≥30 日段才计）。
- 账本：`sg.append_ledger("T-101-V4-A11-XSELECT", 24, "t101_v4_a11_xselect.json", evidence_cutoff="2026-09-28")`（finalize 时落·线性·**返回值必落 out["trials_ledger"] 键 r442 律**）。

## §4 判据【必填·跑前写死，禁看结果调线】

**FV-PASS（注册候选资格）= 五条合取（全量判决面）**：
1. **G1' v2 pass**（skill line+bootstrap CI 下界>0+trade 门 entries_ok——共享库逐条）；
2. **DSR ≥ 0.95**（原始收益 deflated_sharpe_ratio·n_trials=append 后活头）；
3. **成本 ×2 压测**：OOS 超额（vs 同宇宙 EW-B&H·0.2% 往返口径）> 0；
4. **G2 eligible_v2**（G1∧DSR∧PBO≤0.25·共享库）；
5. **D6-ACCEPT**（§1 三面 max|corr|<0.7·预声明结构同源论证不豁免判线）。
- FV-PASS 格→s4 intake 切片（D6 绑定门对在册六员→STRATEGY_LIBRARY+纸盘按 W10 §s4 律）；FV-FAIL 格→横截面选择子线关面如实入 §7+attrition（禁换参重跑）；零 FV-PASS=「五员门/因子特征差分横截面选择用法判负」合法判决照报不粉饰。
- 多重检验税披露：n_wave=24 判格·E[FP]=0.05×24=**1.20**；N_eff 累计照 TRIAL_LABOR_LAW §4 跨波不重置（活头实读）。
- 描述条款恒带（非判线）：全期 maxdd≥−35% 地板·政体依赖性·entries 数·U5/U4 窗深与 IS 空窗。

## §5 跑前预测【必填·写死于跑前】

1. **f_c2 面大概率最弱**：17 门态为市场共同态代理（同族成员门态高度同开同关）→横截面离散度低→选择≈随机→G1 全灭主预期；其格 Sharpe 预期≈EW 底±噪声−成本。
2. **f_rsv30 回归面=批内最强候选但难过线**：五员内高波员（588000/512100）更常居超卖端→选择≈系统性偏持高波员=类内高波 tilt（非纯差分信息）；主预期 OOS 超额 0 附近、×2 翻负高发；若 Sharpe 抬升也大概率被 vs 被持员 B&H 的 d6≥0.7 REJECT 兜底（结构同源预声明）。
3. **f_roc20 动量对照面**：2017+ chop 为主窗→宽基间动量轮动弱+5.8/9.5 年窗浅→G1 全灭主预期；其价值=与 f_rsv30 反向读数构成方向信息的一致性披露。
4. **U5 腿统计力薄**（~1,3xx td·~65 再平衡·全 OOS）→ bootstrap CI 与 DSR 双重折减下 0/12 主预期；U4 腿深度较好但 512100 上市使窗内含 2018 bear/2019-2021 结构断点→段依赖性如实入面。
5. **trade gate 高发失败面**：top-2 stride-20 换员频率低（特征序黏性）→OOS trade events<15 的格高发→entries_ok 拦截非 Sharpe 拦截为主预期之一。
6. **总判**：0/24 FV_PASS 主预期→输入特征路线「横截面选择」子线判负；残余去向=预测器/条件面（vol/风险条件化）非选择面——判决照报不粉饰。

## §6 产物

- 结果：`results/t101_v4_a11_xselect.json`（顶层 evidence_cutoff+cutoff_meta+audit 段+24 判格全量+null 池统计+D6 三面+PBO 族面+三窗/分段描述面+批内 24×24 矩阵）
- 轮报告回执 + `results/gate_attrition.bm-a.json` 追加行（**entries 列表消费面 r248 律**）+ 臂表 A11 行（research/DECISION_CHAIN_BENCHMARKS.md §5）
- 判负处置预案（O-1820 三验③）：FV-FAIL/REJECT 格=特征差分选择面注记关闭；零 FV-PASS=输入特征「横截面选择」子线判负（与择时三子线合流后输入特征路线残余面=预测器/条件化·供下游另批消费）；正结果格→s4 intake。

## §7 跑后实证【占位·跑前必空】

## §8 批后复盘【占位·跑前必空】
