# CN_MKTNEUTRAL_P1 · A股市场中性批（T-87 s2 队列 #5·行 16 市场中性）

- 令链：CEO 流派学令 O-20260926-0926 → O-20260926-2320/2325 淬炼+全域解锁令（RANDOM_LARGE_SAMPLE_LAW v1.0 全律绑定）→ `research/SCHOOL_SUPPLY_S1.md` §二 队列 #5（R302 收线令指定：#1-#4 全 judged-closed 后**下一供给=#5 行 16 市场中性**·工程量最重=期货保证金/移仓成本模型+CTA 禁翻案边界机制披露）→ 外源证据面=T-73 s1/s2 调研正典（survey 行 16：股指期货 IC/IF/IH 在库+对冲腿数据面成立·「融券面依赖如实低」注记=本批空腿=股指期货非融券；s2 sliceA：A 股个股**短期反转>动量**实证·REV60/h10 OOS ic +8.9bp 最强面）。
- 批性质：**judged 判决批**（非淬炼勘探面）——机制面=个股截面选择 α + 股指期货 β 对冲（公募中性产品行业标准结构）；变体轴系=2×2 cells（{REV20,REV60} 反转因子 × {β̂60 自适应, ≡1.0 冻结} 对冲政策），全部冻结于此，批内零选优。
- **判负族边界披露（判负不重开律）**：
  - **期货 CTA ×3 judged-negative ≠本批**：CTA_P1/CTA_P2_NOAU=期货**时间序列趋势择向**（杠杆满额+趋势机制），本批=期货**恒空 β 对冲腿**（非择向非杠杆满额·对冲腿零信号零方向主张）——机制面不同，新预注册+新证据面=合法再入；G2 注册前置数据债条款**全继承**（CTA_P1 §2：主力连续拼接 roll 跳空=V0 直用同面板对称注入·任何幸存者注册前必须分合约 roll 平移复权复跑）。
  - **CN-REV-TILT judged-negative（短期反转 20 名裸篮·差线 23%）=同 α 源前判**：本批诚实披露=**同因子新载体新证据面**——REV-TILT=未对冲 20 名倾斜篮（判词原文「技巧增量为正但量级不足」·REV60_bare CI 下界 +0.3529 为正）；本批=**β 对冲五分位篮**（~620 名 vs 20 名=特质噪声稀释 + β 剥离使判线 null 项摆脱股票域漂移本底 0.6147 主导——对冲后 own-null μ 预期 ≈0，判据问题从「跑赢带漂移随机」改为「对冲基础上跑赢随机选择」=机制级新问题非参数变体）。REV-TILT 判负照册不翻案，本批若判负则行 16 中性面全闭。
  - CN-TREND（ETF 趋势）/CN-SOE/CN-KLINE/REV_OSC/GRID-SLEEVE/CN-DIV-LOWVOL-ROT/CN-SECTOR-LEADER=judged-negative 家族 advisory 披露列（已闭族不作准入面）；微盘（2024 崩塌判负）/T0=零涉；跟庄=合规禁零涉。
- 反重复注记：仓内 market-neutral/中性 runner/prereg 全档零命中（rg `mkneutral|市场中性|中性批|MN-` 2026-09-27 07:5x·唯一命中=本批族件+queue 行）；PRODUCT_MATRIX 资产轴=股票+股指期货在册轴内（C 层 O-1158 授权面）、收益来源轴=截面选择 α=矩阵「择时α/配置β」外的新面（survey 行 16 入册=缺口清单机制已履约），无未入册新维度开线。

## §0 批件身份【跑前】

- 批名：`CN_MKTNEUTRAL_P1` · N_eff=**2004**（4 judged cells ×1 判面 + 2000 null draws；x1/x3 成本=披露列不计 N，CN 家族先例 CN_SECTOR_LEADER_P1/CN_KLINE_PATTERN_P1）
- 认领：任务板 T-2026-09-26-87（claimed_by bm-a·s2 队列 #5 续作切片）；F-04 MSG 先行（`fleet/inbox/MSG-20260927-0750-bm-a.json`·bm-a R303）；部门 dept:研究+策略
- 算力预算：est 30-120min wall（3106 名宇宙 × 2017-01-17→2026-09-22 联合窗 × {4 cells + 2000 null draws + 虚拟起点 census + Sobol 500 + 随机分窗} 向量化 + IC 对冲腿逐日记账；workers=4 BelowNormal）；**按 O-1137 真实载体供给律池提交**（池 ready=0=饿池载体·本批=池饿后首个供给）；per-cell/per-null-shard checkpoint 幂等（>10min 批池化跨轮）；批报告必带 audit 段。

## §1 α 机制段【D6·四选一】

- [x] **行为偏差**：散户短期过度反应→反转溢价——A 股散户主导+T+1/涨跌停约束放大追涨杀跌（T-73 s2 行为规律 digest：羊群实证+短期反转>动量实证·REV60 OOS ic +8.9bp 仓内最强面）；loser 篮后段 drift 由**止损割肉盘与追涨迟到盘**付出代价；市场中性结构=把该截面 α 从 β 漂移中剥离（对冲腿只移除市场风险项、零方向主张）。**与 CTA 机制区分**：CTA=价格趋势延续假设（时间序列）；本批=截面相对排序假设（时间序列零涉·对冲腿恒空结构腿非信号腿）。
- **同族相关性准入（in-runner D6 面）**：逐 judged cell 对在册 6 CE 成员（ew6 canon member_run 日收益）max|corr| + 批内两两 |corr|；**≥0.7 vs 在册成员=拒收**。对冲后近零 β 组合 vs 多头 ETF CE 成员预期 |corr|<0.4（结构面：市场项被对冲腿抵消）；数值批报告 D6 表逐对列；judged-negative 家族（上列）=advisory 披露列；T-47 截面动量=机制披露列（ETF 工具域全池动量 ≠ 个股截面反转+对冲，披露不设门）。

## §2 数据与面板【跑前探针事实·runner selftest 复验门】

- **股票腿面板**：`Money02/data/bars/*.parquet` 5222 只 A股个股日线（只读·WILD-S1/KLINE/SECTOR 同源同面）+ `Money02/data/cache/p1c_stock/*.npy` 对齐面板（T=8792×N=5222·float32·交叉验证件 `results/_r299bma_cache_crosscheck.json` 在位 0 失配）；**cutoff=2026-09-22（D2 前向锁盒·族内一致）**；cutoff 后新 bar 不回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta('2026-09-22')`（缺字段=science_audit C2 VIOLATION）。
- **对冲腿面板**：`data/futures_daily/IC.csv` 中证500 股指期货主力连续（R48 采集器·sina 同源·append-only·overlap 逐行校验·8 列 OHLCV+oi+settle·2353 行 2017-01-17→2026-09-24）；**截断到 cutoff 2026-09-22**（股票面绑定=联合窗合法·期货多出 2 bar 弃用如实披露）；**信号输入裁定=OHLC 四列 only**（oi/settle 覆盖参差 CTA_P1 §2 判例禁入信号）。
- **对冲腿裁定（三披露）**：①**IC 择定**=loser 篮风格贴中证500（中盘）+ 2017-01-17 起全窗在场；IF=大盘错配（反转 α 集中中小盘）、IM=2022-07-22 上市结构性短窗→均不入对冲腿（advisory 列）；②**roll-gap V0 直用**（CTA_P1 裁定全继承）：主力连续换月跳空=拼接序列伪收益源，候选/null/被动全同面板对称注入=相对判据内部有效，绝对水平受跳空污染如实披露；**G2 注册前置数据债=幸存者必须分合约 roll 平移复权 IC 复跑**（零豁免）；③**基差面**=对冲腿按期货价直接记账（期货≠现货指数·期现基差为真实执行面如实内嵌）。
- **宇宙（冻结过滤器·机械再 derive 禁手抄名单）**：bars ok_static ∧ rows≥500 ∧ last==2026-09-22 ∧ med(amount, 自身末 20 行)≥¥30M（**KLINE/SECTOR 同式逐文件法**）→ **universe_n=3106**（SECTOR re-derive 零漂移面·runner selftest 复验==3106）。诚实披露三面：ok_static=当前时点掩码近似；末 20bar 流动性=当前面；bars=当前在册面板=退市股缺席幸存者面。
- **联合窗（冻结）**：面板起点=max(IC 首 bar 2017-01-17, 宇宙成员 warmup 完备日)→**2017-01-17**；终点=2026-09-22；联合交易日历=股票面板日历主源（IC 缺行日=carry 盯市如实披露）；无对冲腿数据的日期=**组合不可成立日**（2017 前）不入窗。
- 数据完备门（不过即拒批 exit 2 零产物）：universe re-derive==3106 ∧ bars 文件数==5222 ∧ cache 交叉验证件在位 0 失配 ∧ IC.csv 行数==2353 ∧ IC 首末 bar=={2017-01-17, 2026-09-24} ∧ 截断后联合窗两端 bar 在场。

## §3 方法学【冻结】

- **信号编码（全 close 面·T+1 禁未来数据）**：REV20(t)=−(C_t/C_{t−20}−1)、REV60(t)=−(C_t/C_{t−60}−1)（**REV-TILT 冻结定义同式**；跌最深=信号最强）；截面降序取**底部五分位**（loser quintile·~620 名 EW·KLINE/SECTOR 池 3106 的 20%）为多头篮；t 收盘算信号 → t+1 开盘调仓（T+1）。
- **对冲机械（工程冻结·全部参数本节冻结禁调）**：
  - 再平衡节律=**20td**（全体 cells 同节律）；调仓日=信号日次一开盘。
  - 对冲名义=β̂ × 篮市值；**β̂ cell 政策二档**：MN-*-BETA=滚动 60d OLS（篮日收益对 IC 日收益·信号日收盘可知）截断 **[0.5, 1.5]**（EF 工程冻结·非 folklore）；MN-*-H1=**≡1.0** 冻结。
  - 手数=round(对冲名义 ÷ (IC 开盘价 × mult 200))·带符号整数（futures_runner 语义）；**保证金占用=|手数|×mult×价×margin_rate 0.14**（FUT_UNIVERSE 冻结表 IC 行·fee_lot 34.6/tick 0.2/limit 0.12 同表）；保证金预算门=Σ 占用 ≤ 权益（超限逐手缩减·futures_runner 同律）。
  - 资本布局=**股票腿 80% NAV + 现金 20%**（保证金+尾部缓冲·EF 冻结）；闲置现金 **V0=计 0 利**（保守·CTA_P1 先例；GC001 逆回购腿=G2 深化项不入 P1）。
  - 期货腿恒空·零信号零方向主张；涨跌停近似（CTA_P1 V1 简化）=开盘触昨收 ±12% → 当日不开新仓（平仓始终允许）。
- **组合记账（逐日 NAV）**：日收益 = 0.8×篮日收益 − 对冲名义占比×IC 日收益(空腿·含 roll 跳空 V0) − 当日成本流；篮日收益=成员 close-close 简单收益 EW（成员停牌/未上市=该日缺席重归一）；β̂/篮构成/手数只在再平衡日变。
- **成本口径**：股票腿 **V2 单源**（`alloc_backtest.side_cost_v2(gross, adv20)`·ADV20=amount 滚动 20 均值·SECTOR 股票面直算先例）**judged face=x2 恒开**（`side_cost_x2`·各分量加倍）+x1/x3 披露列；期货腿=per-lot（fee_lot 34.6+1 tick 滑点/边）×成本乘子 1（judged x2 时**两腿同乘**如实披露：股票腿 V2 加倍+期货腿 fee/滑点加倍）。
- **null 对照（RANDOM_LARGE_SAMPLE_LAW §3·逐腿 own-null CN 家族先例）**：K=2000 draws；每 draw=**同掩码随机五分位篮**（从 3106 有效成员均匀随机抽 20%·与真实篮同再平衡节律同执行同成本同对冲机械）→ 逐 cell own-null 池 2000 值（null 池=随机选择+对冲=**β 漂移被同机械剥离**=判线新面的机制载体）；seed=`SEED_REGISTRY['cn_mkneutral_p1']`=**20279300**+k（k<2000·跑前登记·band 20279300..20281300 构造性零碰撞：cn_sector_leader_p1 带顶 20279200 之上·rg 全仓扫描零命中 2026-09-27 07:5x 留痕·数据文件数字巧合按 t34/wild_route 先例排除）；skill_line=own-null 池分位；双法并列：block bootstrap 2000 draws（块长 10）+ sign-flip 2000 draws，p 值双报。
- **被动基线 2（披露列）**：`unhedged_ew_universe`（同宇宙全成员未对冲 EW 多头=资本机会成本 β 面·非同风险类如实注记）+ `ic_replication`（纯 IC 多头腿=对冲腿镜像漂移面）；二者**不入 skill_line**（对冲后组合无同风险类被动·CTA_P1「域自有 null」律=own-null 池为唯一判线源）。
- **账本**：`science_gates.append_ledger('CN_MKTNEUTRAL_P1', 2004, 'cn_mkneutral_p1', evidence_cutoff='2026-09-22')`（dict schema 唯一禁手抄 prev；链头 204,445→预期 206,449）。
- **虚拟起点面（RANDOM_LARGE_SAMPLE_LAW §2.1）**：cell 组合日序列全史枚举 census——起点日序号∈[200, T−126]，每起点 126 交易日窗（收益/胜率/beat vs unhedged_ew 代理）；分段 4 类（bull/bear/deep-bear/chop·sse 态打标同 REV_OSC/KLINE §2.1 冻结面）逐列；任一分段起点数<500=insufficient-sample 如实注记。**随机分窗（§2.3）**：train/validation 随机划分 ≥100 次 + walk-forward 5 顺序折叠双证。
- **随机参数 sensitivity 描述腿（§2.2 空间填充·描述面零判定宣称）**：Sobol N=500 draws over（REV 回看 W∈{10,20,40,60,120} 离散格 × β̂ 窗 ∈{40,60,120} × 上限 cap ∈{1.25,1.5,2.0}·同一编码同执行同成本 x1 面）；scramble seed-sequence `np.random.default_rng([20279300, 2000])`（SECTOR 派生先例·无带占用）；产物=Sharpe/均值/maxDD 分布描述列，**不计 N_eff、不设门、禁幸存者宣称**。

### §3.1 judged 格表（4 cells，判面 x2，全冻结）

| cell | 多头篮 | 对冲政策 |
|---|---|---|
| MN-REV20-BETA | REV20 底部五分位 EW·20td | β̂60 截断 [0.5,1.5] |
| MN-REV60-BETA | REV60 底部五分位 EW·20td | β̂60 截断 [0.5,1.5] |
| MN-REV20-H1 | REV20 底部五分位 EW·20td | ≡1.0 冻结 |
| MN-REV60-H1 | REV60 底部五分位 EW·20td | ≡1.0 冻结 |

## §4 判据【跑前写死·共享库调用禁手抄判线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=2004, pool='stock_b_layer', n_trades, n_entries, null_pool=<本批 2000-null own 池>)`**（WILD-S1/KLINE/SECTOR 股票域先例）：全期 Sharpe > skill_line_v2 ∧ 平稳 bootstrap CI 下界>0 ∧ entries≥30（F6 双口径·entries=调仓笔数与成员变更事件双口径披露）；逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：DSR≥0.95（deflated_sharpe_ratio 原始日序列·禁 dsr_from_stats 充数）∧ PBO≤0.25（screening/pbo.py CSCV 8 块·4 cell 家族矩阵）；**幸存者注册前置数据债=分合约 roll 平移复权 IC 复跑+股票腿 V2 成本再验**（CTA_P1 条款零豁免）。
- 批面要求（披露列）：annualized>0 ∧ OOS（≥2025-01-01·composite_ic.IS_END 共享分割）双正 ∧ maxDD≥−35%（对冲结构应显著优于该线·贴近=对冲失效旗如实报）∧ 无崩年。

## §5 跑前预测【写死于跑前，跑后对账】

1. **own-null 线下移**：对冲机械剥离 β 漂移→null 池 μ 预期 ≈0±0.1、σ≈0.05-0.15 → 判线预期 **0.2-0.6** 带（vs 未对冲股票域 0.6147/SECTOR 2.04-3.54=面级差异）——**若 null μ 仍 >0.3=对冲机械失效工程旗**（先查 β̂/记账非先查机制）。
2. 反转 α 面：REV60 强于 REV20（REV-TILT s2 sliceA 最强面 8.9bp 地基）；净 x2 Sharpe 预期 REV60 ∈ [0.3, 1.0]、REV20 ∈ [0.0, 0.6]；五分位 620 名 20td 换手 breadth 重 → V2 x2 侵蚀毛收益 30-60%。
3. 对冲政策：BETA≈H1（分散五分位篮 β̂60 典型 0.9-1.1）；BETA 在高波段窗（2018-10/2024-02）略优；|BETA−H1| Sharpe 差 >0.3 = β̂ 帽 [0.5,1.5] 绑定面过窄旗如实报。
4. maxDD：对冲后预期 ≥−15%（vs 未对冲 −35% 面）；DD 逼近 −30% =对冲失效旗（IC 中盘 vs loser 篮小微盘风格错配=基差崩窗嫌疑）。
5. **极端日先验（硬界三件套 c）**：①2024-02 微盘崩（loser 篮小微盘集中→IC 500 对冲风格缺口崩·基差极端窗）；②2024-09-30/10-08 政策脉冲（涨停潮：股票腿 10/20cm 封板估值失真+IC 期货 12% 涨跌停与期现基差脱锚·roll 跳空日单日 |r| 可破 3×滚动 std·KLINE 同窗实证锚）；③2018-10 深熊急跌窗（β̂ 估计失稳+两腿同向缺口）；④2015-2016 熔断/救市窗=**窗外**（2017 起窗结构豁免如实注记）。
6. D6 预判：vs ew6 canon max|corr|<0.4（对冲近零 β）；批内两两 0.7-0.95 高相关带如实报（同 DNA 不同政策·无门）。
7. 幸存者数预测 **0-1**（N_eff 2004+REV-TILT 差线 23% 前科+成本 breadth 重=判负基准情形；对冲结构若真把 REV-TILT 的「技巧增量正」翻译成「量级跨线」=本批唯一翻正路径，claim≠verify）。

## §6 产物

- `results/cn_mkneutral/p1_results.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+D6 表+judged 判读+N 计数+对冲机械审计段[β̂ 分布/手数/保证金占用峰值/roll 日清单]+不可成交拒单披露+null 池+被动 2 基线+Sobol 描述腿+census+分窗产物）；`results/cn_mkneutral/cells/*.json|npy` per-cell/per-null-shard checkpoint；`results/gate_attrition.json` 追加一行（**entries 列表面·r248 律**）。
- runner=scripts/cn_mkneutral_p1.py（**冻结 commit 后建**·R99 序：prereg 冻结先于 runner build 先于任何 run；selftest 子命令=离线自检 hermetic fixtures·**B7b 契约腿必带**（下游下标键集 ⊆ stats 构造键集断言·R297 坑律）+对冲机械合成断言（β̂ cap/手数取整/保证金预算门/roll 日记账））。
- 股票引擎零改动（O-2250 加性铁律）；期货腿复用 `engine/futures_runner.py` FUT_UNIVERSE 冻结表（零改动直读）。

## §7 跑后实证【跑前为空——占位纪律：写数字即造假】

（一次定稿 2026-09-27 R306 bm-a autofill burn pid 19684 08:40:08→~08:47 完结（实际 ~7min vs est 30-120min=向量宽+月度调仓实算远轻于估·估时面如实注记不回溯改估）；done-flip R306 先于本分析（r302 律）+result_ref 落池同轮；**4/4 cells 判负照报**——x2 判面全期 Sharpe MN-REV20-BETA 0.4975/MN-REV60-BETA 0.5577/MN-REV20-H1 0.4680/MN-REV60-H1 0.4802；skill line（own-null 校准·共享库算）BETA 系 0.6834（null_term 绑定·mu_null 0.3752·σ 0.0623）/0.6862 与 H1 系 0.5606（passive_term 绑定·mu_null 0.2244·σ 0.0595·null_term 0.5188）全数 line_ok=False 4/4 ∧ bootstrap CI 下界 −0.1284/−0.1071/−0.1731/−0.1824 全 ≤0；DSR 0.0012/0.0021/0.0009/0.0010 全 <<0.95；family PBO **0.9286**（>>0.25·CSCV 8 块 70 组合·IS-best 几乎不保 OOS）；G2 eligible_v2=False 4/4；**批面 cells_ok 4/4 TRUE**（ann +4.74%~+5.86% 全正 ∧ OOS 2025+ ann +2.5%~+9.3% 双正 ∧ maxDD −21.5%~−25.4% ≥−35% 过 ∧ 无崩年（逐年最差=2017 −8.3%~−13.8%·2018 对冲下转正 +3.3%~·2024 +14.9%）——绝对收益为正但不跨自身本底线=判负语义「跑不赢 own-null 校准线」非「亏钱面」，批面全过与判据全挂并列如实）；entries 面 118 调仓/98,529（REV20 系）/60,812（REV60 系）双口径 trade gate dual_ok 4/4（≥30 过）；D6 max|corr| vs ew6 canon ≤0.1196 无拒收（§5 预判 <0.4 ✓·对冲近零 β 面证）·批内两两 0.7526-0.9418（§5 预判 0.7-0.95 ✓）；robust 双法=sign-flip p 0.098/0.136/0.157/0.143 全 >0.05 不显著 + block bootstrap p≤0 0.054-0.075 边缘不带显著性宣称；虚拟起点 census 2,026 起点（bull 416/deep_bear 6 两段 <500=insufficient 如实注记·bear 837/chop 767 sufficient）·beat_rate_6m 0.4097/0.4151/0.4363/0.4240 全 <0.5（vs 未对冲宇宙 EW 代理·passive 2 披露列）·oos_halves 前后两半均正且后半>前半（如 0.0137→0.0572·无衰减方向面）·walk-forward 5 折首折负后四折偏正（−0.479..+1.067）；null 池 BETA mu 0.3752（**>0.3=§5.1 对冲机械失效工程旗触发**·旗后按令先查 β̂/记账非先查机制：β̂ med 0.935-0.947·cap [0.5,1.5] 双侧绑定（REV60 max 1.498 触上帽·两 BETA 系 min 0.5 触下帽）·fallback 仅 2 次全在 2017 窗首数据不足·手数全短向取整·margin peak 14.7%-16.8%（H1 11.3%）保证金预算门内·NAV identity selftest 42/42=记账面零缺陷→漂移归属=机制面（β̂ 帽在窗内的不对称短敞口+loser 篮结构漂移·非记账缺陷如实分列；判负不依赖此归属：策略 0.468-0.558 < 线 0.561-0.686 双向不跨）；x1 面披露列 0.6967/0.6740/0.6630/0.5963（x1>x2 4/4 ✓·侵蚀 17%-29%）；Sobol 512 抽 500 用（qmc.Sobol 幂平衡如实·seedseq [20279300,2000]）x1 描述腿 Sharpe 带 ~0.60-0.83·零幸存者宣称（judged=冻结 2×2 轴零参数搜寻）；被动 2 基线披露列：未对冲宇宙 EW Sharpe 0.5821/ann 11.3%/maxDD −39.4%（vs 本批对冲面 −21.5~−25.4%=对冲压 DD ~14-18pp 实证）+IC 复制面 Sharpe 0.2249；trials ledger 204,445+2,004=**206,449** 单计 ✓（与冻结预期逐位相等）；gate_attrition 行 runner 自落 ts 08:42:59（entries 列表面 r248 律 ✓）；cutoff_meta evidence_cutoff 2026-09-22 顶层在位 ✓ C2 合法键。）

## §8 批后复盘【必填·s7-T】

（2026-09-27 R306 定稿。**§5 七预测对账**：①「own-null 线下移 μ≈0±0.1·线 0.2-0.6 带；null μ>0.3=工程旗」→ **半中半旗**（H1 mu 0.2244 近带内上沿；BETA mu 0.3752 **>0.3 旗触发**→旗后按令先查 β̂/记账=审计面零缺陷→漂移归属机制面如实记；BETA 线 0.6834/0.6862 出预测带上沿=同一根因非独立意外）；②「REV60 强于 REV20·净 x2 REV60∈[0.3,1.0]/REV20∈[0.0,0.6]」→ **全中**（REV60>REV20 4/4 方向 ✓·两系落带内）；成本侵蚀预测 30-60%→实测 17-29%=**幅度带 MISS**（月度调仓 breadth 侵蚀轻于估·预测过悲观如实记）；③「BETA≈H1·差>0.3=帽窄旗」→ **全中**（|差| 0.030/0.078 远<0.3 旗不触发·BETA 微优方向 ✓）；④「maxDD≥−15%·逼近 −30%=对冲失效旗」→ **MISS 但旗未触发**（实测 −21.5~−25.4% 劣于 −15% 预测·未及 −30% 失效线；vs 未对冲 EW −39.4% 实证压 DD）；⑤「极端日三窗先验」→ 部分验证（年面无崩年·2018 对冲转正·2024 +14.9% ✓；逐窗逐日 DD 归因面 runner 未落=判读粒度不足如实记·2015-16 窗外豁免 ✓）；⑥「D6<0.4 ∧ 批内 0.7-0.95」→ **全中**（0.1196 上限·0.7526-0.9418 实测带）；⑦「幸存者 0-1」→ **中**（0 员·判负基准情形命中·「量级跨线」唯一翻正路径未发生）。**判线读数**：判负语义=「对冲结构绝对收益为正（批面 4/4 全过）但不跨 own-null 校准 skill line ∧ CI 下界全负 ∧ DSR≈0.001 判据亏耗后无物 ∧ PBO 0.93 家族 IS-best 不保 OOS」——与 REV-TILT（未对冲 20 名倾斜面 judged-negative）合并=**行 16 市场中性流派面 judged-closed**：同 α 底层（反转底部五分位）在对冲载具下依然不跨线=「技巧增量正≠量级跨线」实证（REV-TILT negative stands 不翻案·边界披露 b 兑现）；判负不重开律生效：本编码·本执行域（IC 恒短 β 对冲·2017-2026 窗·月度调仓·V2 x2）**判负关槽**，新证据=新预注册（β 对冲工具域/五分位定义/调仓域变体须另立 prereg 禁本批翻案）；CTA-x3 禁翻案边界维持（趋势方向性≠恒短结构腿·机制披露面成立）；G2 数据债（分合约 roll 平移复跑）随 G1 挂而不触发如实注记。**gate_attrition**：runner 自落行在册（ts 08:42:59·entries 列表面·r248 律）。**回执面**：T-87 s2 队列 #5 闭环（freeze 3c71ddb4 R303→runner 42/42+实数据门 R304→池提交 R304→claim 08:40:08 latency 18.9min 超标如实（R305 注册缺陷窗已报·root cause=workers_plan 手写漏=本轮 autofill submit 门机制化闭合）→burn ~7min→done-flip R306 先于分析→judged 定稿全链 R99 序合规）；**SCHOOL s2 队列 #1-#5 五批全部走完 freeze→runner→pool→burn→judged 全链，5/5 judged-negative·0 员幸存**（#1 CN-TREND-ETF G1 5/7 过线但 G2 0/7 DSR/PBO 双杀·#2 CN-SOE-ETF G1 0/5·#3 CN-KLINE-PATTERN 全负·#4 CN-SECTOR-LEADER 4/4·#5 本批 4/4）→ s3 关槽注记逐批在册；s4 供给报告=**零幸存者诚实面**（T-85 融合候选池零新增·cross-ref 本行）；下一供给候选=外源 digest 线（O-1721 借力律常态双频）非仓内队列（#6-#10 文本面缺判据已列不建模）。）
