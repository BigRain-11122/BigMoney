# T-101-V4-A13-PREDFACE 预注册（输入特征路线残余·纯预测器 forecast/walk-forward 信息面终测）

> 血统：A12 §8 下游指针兑现（「残余去向=纯预测器（forecast·walk-forward 面）……若未来立项须新 prereg+D6 先行论证」——本批即该指名面首测=终测）+ r445 state next(d)（「pure predictor face (fresh prereg + D6 first) or line exit」）。A2/A9/A10/A11/A12 五子线已证伪=门/因子特征源在五员宇宙的**二值择时/门态连续权重/横截面选择/vol 条件化**四类**仓位映射**用法；本批=**信息面（forecast·walk-forward）**首测——测量「特征值→未来 20d 收益」的**秩相关预测技能本身**，非任何仓位构造：功能形=条件期望建模（Spearman IC·stride-20 非重叠再平衡日历），与已闭五子线功能形不同（A12 §8 冻结表述）。**本批=输入特征路线全谱收线的最后一面**：判负即线退出（superline exit），过线即 s4 供给注记（下游转化仍须过 D6 beta 同源门=预声明）。
> 状态：**FROZEN——冻结于跑前·2026-09-29 21:3x·bm-a r446（起草机同轮一次冻结·A9/A10/A11/A12 臂线批先例：一次冻结即烧）**。本冻结 commit 同窗含 SEED_REGISTRY 两键注册（20318500/20319000 三步律过：126 键全盘零精确撞带·首元素正典 int(default_rng(s).integers(0,2**31))=295045756/989029903 互异且 vs 全部既有基零撞·null 派生带 20318500..20318539 与 unc 派生带 20319000..20319039 净隙 500 零重叠·rg 仓内代码面 20318xxx/20319xxx 零命中）+runner+MSG 声明。

## §0 批件身份【必填·跑前】

- 批名：**T-101-V4-A13-PREDFACE**·批内格数：**40**（特征 4 × 成员 5 × 收益面 2）；null 对照 K=200/格·另计不膨胀格数。本批=**信息面初筛判决批**（入 trials_ledger，batch_trials=40）。
- 认领：F-04 先行=MSG-20260929-2130-bm-a-ALL（fleet/inbox/·开工声明）；任务板引用=臂表 A13 位（A 系列惯例=臂表行即工单·r441-r445 同法·无新票）。
- 部门归属：dept:研究（链条研究线·T-101 v4 输入特征路线残余面 A13 位）。
- 算力预算：est <2 min 单进程（五员特征构造 157 因子×2 面+40 格×(200 位移 null+2000 块自助)+IS/OOS/全期三段）——trivial compute in-round 合法（O-2100·A12 61.0s 同族先例）；worker 数 1；批报告必带 audit 段。
- 车道：**bm-a**（五员面板 data/daily in-repo·probe/fv 机器件本机全在·r441-r445 同车道延续）。
- 语法查重/防重跑：**时序秩相关预测器面=未被消费面**——TRIAL_GRAMMAR_LEDGER 全文 rg「forecast|预测器|spearman|IC 面」零命中；A158_TRUEGAP_IC=个股横截面 IC（P-1c 面板 5,129 股·composite_ic xs_zscore·不同宇宙不同轴）；A11=ETF 横截面 rank top-k 选择（再平衡日粗二值化·非连续值 IC）；gate 族=二值门条件均值（非连续值秩相关）；A12=权重映射（非预测）。A13=ETF 面连续特征值×stride-20 时序 Spearman IC+成员相对（LOO 去均值）面=仓内零重跑面。
- **撞批三查**（r440 律）：job_list 空✓+fleet/tasks 零 open✓+git fetch 近 30min 他人 commit 扫标题（W11=bm-b TRIAL 波车道·零 A13 面冲突）+SEED_REGISTRY 尾 live-read（20318500/20319000 零撞）✓。

**§0-X 预测器形态【冻结·禁搜参·全冻死】**：
- **特征（4·全冻结·零新发明·全部源自已闭子线在册定义·import 单源）**：`f_rsv30`=probe RSV30（A11 逐字）·`f_c2`=17 冻结门掩码均值（fv.GATES17·A11 逐字）·`f_roc20`=probe ROC20（A11 逐字）·`f_std20`=σ20=日收益 20d 滚动 std ddof=1（A12 sig_i 逐字）。**方向零假设**：IC 面测符号本身·无升序/降序选择（A11 RANK_ASCENDING 的方向选择风险在 IC 面不存在）。
- **预测目标**：`fwd20(t)=close[t+20]/close[t]−1`（20 交易日·stride-20 非重叠再平衡日历=族律）。
- **收益面（2·冻结）**：
  - **RAW 面**：成员自身 fwd20（β 主导面·五子线 D6 判例结构主预期如实携带）；
  - **RESID 面**：`r_resid_i(t)=fwd20_i(t)−mean_{j≠i} fwd20_j(t)`（LOO 同侪去均值=成员相对面·**从未被测量过的主张**：A11 测的是再平衡日 top-k 二值选择·非连续值成员相对预测）。
- **格（40）**：RAW=4 特征×5 成员=20（成员自身可判窗·特征各自最大窗）；RESID=4 特征×5 成员=20（U5 master 交集窗·A11 build 同法）。
- **IC 统计**：每格=Spearman 秩相关（特征值,fwd 目标）over 再平衡日对集·三段（full/IS/OOS·SPLIT=2017-01-01 族常量）。常数列→NaN 如实披露（nan-safe r442 律：有效集统计+nan_excluded 计数）。
- **FV 可判格=12**：RAW 面×{510300,510050,510500}（IS 段≥15 对可判）×4 特征。**OBS：RESID 全部 20 格+RAW{512100,588000} 8 格=结构 OOS-only**（512100 上市 2016-11·588000 上市 2020-11→master 交集窗全在 2017 后）→**读数层**（p/z 如实披露·无 FV 资格·任何 p<0.05 OOS 命中→「供给注记」旗供 A1/C1 输入特征面·非策略宣称）。

## §1 α 机制段【必填·D6】

四选一：**[x] 行为偏差**——恐慌过度反应+锚定效应的连续值版：超卖深值（RSV 低）→恐慌抛售者交出筹码→20 日窗均值回归修复；门族条件均值已测得 OOS 正（gate_verify RSV60/30 +1.08%/+0.81%·二值面）——本批测其**连续值秩相关版本**是否独立成立（二值门≠连续单调：门截断只测阈下·IC 测全分布单调）。RESID 面机制=成员相对过度反应（同侪分化修复）。由谁付出代价=预测面无对手盘构造（信息面·不构造交易）——**诚实披露：信息面测量不构造策略收益流·其下游任何转化仍须过 D6 beta 同源门**（五子线判例 0.57-0.97 结构同源）。
- **同族相关性准入检查【D6·跑前预声明】**：信息面无收益流→D6 收益流判线**不适用于本批本体**（预声明）；但**下游转化预声明**=任何 FV-PASS/供给注记格的仓位转化收益流将结构性撞 vs B&H β 同源门（A2/A9/A10/A11/A12 判例族 0.57-0.97·恒满仓/门控持有同类资产定义性同源）→**本批过线≠注册资格**·仅=信息面存在性判决+s4 供给注记资格。特征间互相关披露面：f_rsv30/f_roc20/f_std20/f_c2 逐成员 Spearman 互相关矩阵落 JSON（读数·不 kill）。

## §2 数据与面板【必填·跑前探针事实】

- 宇宙=冻结五员 O-1555={510300, 510050, 510500, 512100, 588000}；数据锚四元组（G-ANCHOR-FACE）=`data/daily/sh<码>.csv`+pd.read_csv raw 直读+**cutoff 2026-09-29 截断+尾行断言**（runner 自有 loader·tpl.load_panel 语义逐字换 cutoff 常量=新批新 cutoff 合法·探针-锚同面断言）。
- **冻结行数锚（@2026-09-29·本批探针实测）**：510300=3,487 / 510050=5,252 / 510500=3,290 / 512100=2,406 / 588000=1,426；尾行一律 2026-09-29（runner 断言·A13_ANCHOR_ROWS）。**注意：fv.ANCHOR_ROWS=09-28 锚·本批禁用**（cutoff 推进+1 行）。
- **evidence_cutoff=2026-09-29**（D2 前向锁·五员尾行实测 09-29·09-29 bar 20:36 早落 r440 实况）；cutoff 后新 bar 不回流；结果 JSON 顶层必带 `science_gates.cutoff_meta(evidence_cutoff)`。
- **可判窗（跑前探针披露·runner 实算如实落 JSON）**：RAW 面各成员最大窗=特征各自预热后（RSV30≥30d·ROC20≥20d·σ20≥21d·f_c2≥因子窗+GATE_MINP=120d）；RESID 面=U5 master 交集（588000 上市 2020-11 起）+f_c2 决定窗≈2021-05 起（A11 U5 同构）。IS 段（<2017-01-01）：510300/510050/510500 历史充分（510050 2005 起 IS 深）；512100/588000 IS 结构近空=OOS-only 如实记。

## §3 方法学【必填】

- **执行机器零重实现（import 单源）**：`a158_tsgate_probe`（probe：alpha158_factors/gate_universe/N_FACTORS）；`t101_v4_a158_fv`（fv：GATES17/g_p1_check/g_accept_check）；`t101_v4_a2_prescreen`（tpl：SPLIT 族常量）；`science_gates`（sg：append_ledger/SEED_REGISTRY/cutoff_meta）；`scipy.stats.spearmanr`（秩相关）。
- **特征构造（A11 逐字范式）**：per member：F=probe.alpha158_factors(panel)（行数=N_FACTORS 断言）；gates={g[0]:(mask,dec)}；c2=17 掩码 concat 均值；c2dec=17 dec 全 AND。f_std20=close.pct_change().rolling(20).std()。**RAW 面窗=成员自身日期轴上特征 decidable 起**（各特征独立窗·最大化 IS 深度）；**RESID 面窗=A11 build_universe_face 同法 master 交集+全成员 AND decidable**。
- **再平衡日历**：stride-20·rebal_idx=arange(0,n,20)（族律）；对集=(特征值@rebal, fwd20@rebal)·尾 rebal 不满 20d 前瞻窗者弃（p+20≤n−1）。
- **位移 null（批自对照·核心）**：K=200/格·**特征再平衡对数组** circular shift 随机偏移（偏移∈[1,n_pairs−1]·保对数组自相关结构+特征边际分布·同 fwd 目标同对集位重算 IC）→位移 null 池；empirical 双侧 p=(1+#{|null|≥|IC|})/(K+1)；z=(IC−mean_null)/std_null（nan-safe r442 律·std=0→z=NaN 披露）。**冻结流声明**：full 段流=rng([**20318500**, cell_idx])·OOS 段派生流=rng([**20318500+100000**, cell_idx])（段流分离防同一 null 池双用·cell_idx=冻结 40 格表序）。
- **块自助 CI（不确定性面）**：circular block bootstrap B=2000·block=10（对再平衡对索引重采样重算 IC）；percentile CI 2.5/97.5（full+OOS 段）；**冻结流**：full=rng([**20319000**, cell_idx])·OOS 派生流=rng([**20319000+100000**, cell_idx])。**声明=实跑同基**（A12 rebind 正法：本批不经 fv.dual_nulls·UNC_BASE 直读直用·无继承基错配面）。
- **账本**：`sg.append_ledger("T-101-V4-A13-PREDFACE", 40, "t101_v4_a13_predface.json", evidence_cutoff="2026-09-29")`（finalize 落·线性·**返回值必落 out["trials_ledger"] 键 r442 律**）。

## §4 判据【必填·跑前写死，禁看结果调线】

**FV-PASS（12 可判格·四条合取）**：
1. **|IC_OOS| ≥ 0.10**（20d 横标指数级量级线·n_OOS≈100-170 对下 t≈2 阈≈0.16-0.18·0.10=筛选面量级守门）；
2. **位移 null p_OOS < 0.05**（双侧 empirical）；
3. **IS/OOS 同号**（n_IS≥15 可判格·gate_verify 反号族处置延续：IS 反号=政体依赖如实记不粉饰）；
4. **full/OOS 同号**（全期一致性）。
- FV-PASS 格→s4 供给注记资格（下游转化另批·D6 门恒在）；FV-FAIL→判负如实入 §7+attrition。**零 FV-PASS=输入特征路线全谱线退出**（A2/A9/A10/A11/A12/A13 六面全负→superline exit 正典判决·T-101 v4 输入特征线关板·残余供给面转 bm-b 车道 A1/C1 情绪门族）。
- 读数层（28 格）：p_OOS<0.05 命中→「供给注记」旗（A1/C1 输入特征面候选披露·非策略宣称·无 IS 确认结构诚实）。
- 多重检验税披露：FV 可判 12 格 E[FP]=0.05×12=**0.60**；读数层 28 格纯披露不入判；N_eff 累计照 TRIAL_LABOR_LAW §4 跨波不重置（活头实读·346,553→+40 预期 346,593）。

## §5 跑前预测【必填·写死于跑前】

1. **RAW 面 f_rsv30 小正 IC 主预期但不过线**：门族二值条件均值 OOS +1.08%（20% 开门率·截断阈下集中）→连续版 IC 稀释主预期 |IC|≈0.03-0.08<0.10；510050 低波大盘稀释更甚（gate_verify 同构预期）。
2. **RESID 面全灭主预期**：A11 成员相对 rank 已证「低于随机」（类内接刀/动量死）→连续版成员相对预测同源死信息主预期；若现 p<0.05 命中=供 A1/C1 输入注记（诚实·非策略面）。
3. **f_std20 RAW 面负 IC 可能**（高波→低 fwd·vol-managed 族先验）量级 <0.10 不过线；f_c2 RAW 面弱正（门开多=超卖修复聚合）不过线。
4. **IS 反号风险**：2017 前低波慢牛超卖不灵族（gate_verify PARTIAL 同族）→510300/510050 IS 段弱/反号可能→判据 3 淘汰面如实记。
5. **总判：0/12 FV_PASS 主预期→输入特征路线 superline exit**；T-101 v4 残余面收口·供给面移交 bm-b 车道（A1 C1 双温度计+A3/A4 情绪族）。

## §6 产物

- 结果：`results/t101_v4_a13_predface.json`（顶层 evidence_cutoff+cutoff_meta+audit 段+40 格全量三段 IC/p/z/CI+null 池统计+特征互相关矩阵+FV 12 格判决+读数层 28 格+供给注记旗）
- 轮报告回执 + `results/gate_attrition.bm-a.json` 追加行 + 臂表 A13 行（research/DECISION_CHAIN_BENCHMARKS.md §五）
