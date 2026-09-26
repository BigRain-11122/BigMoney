# CN_SECTOR_LEADER_P1 · A股「板块龙头非涨停面」judged 判决批（T-87 s2 队列 #4·行 3 龙头战法新面）

- 令链：CEO 流派学令 O-20260926-0926 → O-20260926-2320/2325 淬炼+全域解锁令（RANDOM_LARGE_SAMPLE_LAW v1.0 全律绑定）→ `research/SCHOOL_SUPPLY_S1.md` §二 队列 #4（R298 收线令指定：WILD-S1 涨停龙头面 judged DEAD 后**板块垄断溢价≠涨停事件流**新面候选）→ O-1721 借力律：板块谱系源=**SW 官方 2021 分类簿**（swsresearch.com 直下·legulegu cons 源反爬不可达、EM 本机死 r280 判例、THS cons API 本版 akshare 无——三源死活如实入探针件）。
- 批性质：**judged 判决批**（非淬炼勘探面）——变体轴系=4 出场 cells（持有窗/板块退潮出场/硬止损），入场编码=**EF 工程冻结**（龙头战法数字腿付费墙缺席·WILD_ROUTE_LAB_S1_CARDS L92 如实披露→编码禁称 folklore 出品，边界披露 a 同 K 线批范式），冻结于此，批内零选优。
- 判负族边界披露（判负不重开律）：WILD-S1 涨停族=T+1 事件面同域但**涨停封板事件≠板块内相对强弱身份**（机制面不同·D6 披露列·且本批触发端显式剔除收盘涨停/近涨停面=面纯净性双保险）；CN-TREND（ETF 趋势）/CN-SOE/CN-KLINE/REV_OSC/GRID-SLEEVE/CN-REV-TILT/CN-DIV-LOWVOL-ROT=judged-negative 家族 advisory 披露列（已闭族不作准入面）；微盘（2024 崩塌判负）/期货 CTA ×3/T0=零涉；跟庄=合规禁零涉。
- 反重复注记：仓内板块龙头/sector-leader runner/prereg 全档零命中（rg 2026-09-27 06:4x·`sector.leader|板块龙头|LDR-` 唯命中=本批族件+本轮 MSG）；PRODUCT_MATRIX 资产轴=股票在册轴内、时间轴=短线波段段，无新维度开线。

## §0 批件身份【跑前】

- 批名：`CN_SECTOR_LEADER_P1` · N_eff=**2004**（4 judged cells ×1 判面 + 2000 null draws；x1 成本=披露列不计 N，CN 家族先例 CN_KLINE_PATTERN_P1）
- 认领：任务板 T-2026-09-26-87（claimed_by bm-a·s2 队列 #4 续作切片）；F-04 MSG 先行（`fleet/inbox/MSG-20260927-0645-bm-a.md`·bm-a R299）；部门 dept:研究+策略
- 算力预算：est 30-120min wall（17,823 触发 cohort-events × 2000 null draws 向量化 + 全史虚拟起点 census + Sobol 500 描述腿 + 随机分窗；workers=4 BelowNormal）；**按 O-1137 真实载体供给律池提交**（池 ready=0=饿池载体）；per-cell+per-null-shard checkpoint 幂等（>10min 批池化跨轮）。

## §1 α 机制段【D6·四选一】

- [x] **行为偏差**：板块龙头垄断溢价=注意力/羊群面——热板块吸引资金羊群（板块效应），龙头=板块内注意力磁极（身份垄断），后段 drift 由**晚到追涨盘**付出代价（attention premium 归早持有人）；A 股散户羊群+板块轮动实证（T-73 s2 行为规律 digest：T+1 约束/羊群/风格轮动史 2017 核心资产→2021 成长→2023 微盘→2024 红利）=仓内证据侧写。**与 WILD-S1 机制区分**：涨停溢价=封板事件稀缺性博弈（事件门槛）；本面=板块内相对强弱身份溢价（零事件门槛·触发端反剔除涨停面）。
- **同族相关性准入（in-runner D6 面）**：逐 judged cell 对在册 6 CE 成员（ew6 canon member_run 日收益）max|corr| + 批内两两 |corr|；**≥0.7 vs 在册成员=拒收**。个股板块龙头袖 vs ETF/组合 CE 成员预期 <0.4（跨工具域+≤3 员/日稀释），数值批报告 D6 表逐对列；judged-negative 家族（上列）=advisory 披露列；T-47 截面动量=机制披露列（ETF 工具域+全池截面 rank ≠ 个股板块内身份+唯一性帽，披露不设门）。

## §2 数据与面板【跑前探针事实·冻结引用件 `results/cn_sector_leader_probe.json`】

- 面板：`Money02/data/bars/*.parquet` 5222 只 A股个股日线（只读·WILD-S1/KLINE 先例同源同面）+ `Money02/data/cache/p1c_stock/*.npy` 对齐面板（T=8792×N=5222·float32·**cache↔bars 交叉验证件 `results/_r299bma_cache_crosscheck.json`**：4 样本股有限掩码 0 失配·值偏差 ≤1.1e-4=float32 精度面·末端 2026-09-22）；**cutoff=2026-09-22（D2 前向锁盒·与 WILD-S1/KLINE 同 cutoff）**；cutoff 后新 bar 不回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta('2026-09-22')`（缺字段=science_audit C2 VIOLATION）。
- **板块谱系（冻结资产）**：`data/basic/sw_stock_classify_2021.xls`＝SW 官方 2021 全史分类簿（sha256 `1111bceb420c510c90f0f794fd8ae0c39015c99768162374f90b782ce5d3a3c8`·fetched 2026-09-27 06:35:32·1,166,336 bytes·12,925 行/5,930 股/553 行业码·**覆盖 bars 5222 = 100%**）；粒度=**L2（industry_code[:4]·131 板块·中位 25 员·124 板块≥5 员）**；**point-in-time**：逐股逐段 start_date 生效日历史（1990-01-01→2026-09-24·3,914 股多次改类·2021 标准切换峰 3,393 行如实）。诚实披露三条：①**2021 标准回溯适配**（2021 分组设计应用于 2021 前历史段=分类学修订回溯代理面·官方公布史=可得上界最优面）；②标准内改类按生效日 point-in-time 履行；③首次分类前 (股,日) 对=unmapped 剔除不计板块成员。TLS 采集披露：swsresearch.com 服务端链不全 → verify=False 一次性直下（公开静态研究文件·`results/_r299bma_sw_clf_meta.json` 留痕）。
- **宇宙（冻结过滤器·机械再derive 禁手抄名单）**：bars ok_static ∧ rows≥500 ∧ last==2026-09-22 ∧ med(amount, 自身末20行)≥¥30M（**KLINE 同式逐文件法**）→ **universe_n=3106**（探针实证 skip not_ok 1705/rows 163/last 5/liq 243 与 KLINE 探针零漂移）。诚实披露同 KLINE 三面：ok_static=当前时点掩码近似；末20bar 流动性=当前面；bars=当前在册面板=退市股缺席幸存者面。
- **触发事件普查（冻结引用件 census 面·编码=本节冻结·探针 26.0s 实证）**：hot 门（L2 EW 20d-ret top K=3 ∧ >0 ∧ 板块内有效成员≥5）逐日触发 → 板块内 argmax 20d-ret 龙头（并列取 trailing amount20 高者）∧ 龙头收盘非涨停/近涨停（r1 < 板型阈−0.002）→ **trigger_events_n=17,823**（1994-01-17→2026-09-22·7,026 触发日·峰 3 事件/日=K_TOP 帽构造性上界·逐年 380-630 均匀健康·distinct leaders 1,545·涨停面剔除 2,562 如实计）。
- **数据完备门（不过即拒批 exit 2 零产物）**：universe re-derive==3106 ∧ bars 文件数==5222 ∧ cache 交叉验证件在位且 0 失配 ∧ 分类簿 sha256==冻结值 ∧ 板块覆盖==100% ∧ trigger census re-derive==17823（census-drift face 同 KLINE L363 律）。
- 工程冻结参数表（EF·非 folklore·边界披露 a）：W=20td（板块/龙头回看）；K_TOP=3（热板块帽）；MIN_SECT=5（板块最小有效成员）；LIMIT_EXCL_TOL=0.002（触发端收盘涨停/近涨停剔除·WILD-S1 LIMIT_OPEN_TOL 同式）；板型阈 main 0.0975/创科 0.1975（创 20cm 自 2020-08-24·科自 2019-07-22·WILD-S1 冻结面）。全部数值源于叙事忠实的**本批工程冻结**，禁回溯归因 folklore（数字腿付费墙缺席·L92 披露）。

## §3 方法学【冻结】

- **信号编码（全 close 面·探针引用件=唯一编码权威）**：日 t：r20[j]=c[t]/c[t-20]−1（双 finite）；板块 S 的 EW20=成员 r20 均值（成员=U_static ∧ 板块 active(t) ∧ c finite ∧ r20 finite∧r1 finite）；hot_rank(t)=EW20 降序 top-3 ∧ EW20>0 ∧ 成员数≥5；leader(S,t)=argmax r20（并列 amount20 高者）；**trigger**=(S,t,leader) 当 leader r1[c]<板型阈−0.002。t 收盘发令。
- **执行（T+1 禁未来数据·WILD-S1/KLINE 同式）**：信号 d 收盘 → 入场 d+1 开盘；一字/近涨停开盘=不可成交拒单（open/prev_close−1 ≥ 板型阈−0.002）**计数不弃账**；停牌→滚动至首个可成交开盘；出场同 T+1 开盘式。
- **组合记账（WILD-S1/KLINE bucket 语义冻结复用）**：资本入 H 桶；触发日 t 的 cohort（=当日全部触发龙头·≤3 员·等权内构）于 t+1 开盘部署；cohort 净收益均摊记入其 H 持有日；止损/退潮臂=触发日实际出场记账（残余桶回收）；cell 日收益序列=活跃 cohort 日收益均值。
- **出场臂（④工程冻结·folklore 无共识面）**：
  - LDR-FIX10：H=10td；
  - LDR-FIX20：H=20td；
  - LDR-SECT10：H=10td ∨ 板块退潮出场（持有日 t′ 板块 ∉ hot_rank(t′) → 次开出·folklore 方向注记「卖点=情绪退潮」卡#7 工程代理）；
  - LDR-STOP10：H=10td ∨ close≤入场价×(1−8%) → 次开出（engine canonical 硬止损 −8% 面）。
- **成本口径**：V2 单源（`alloc_backtest.side_cost_v2(gross, adv20)`·ADV20=amount 滚动 20 均值·股票面直算）；**judged face=x2 恒开**（`side_cost_x2`·V2 各分量加倍·CN 家族先例）；x1=披露列。成本作用于每笔名义（入场/出场双边）。
- **null 对照（RANDOM_LARGE_SAMPLE_LAW §3）**：K=2000 draws；每 draw=逐 cell 同掩码随机事件面——(U_static×有效日) 均匀随机抽 N=该 cell 实测触发数的 (龙头,日) 对→同 H 同执行同成本同 bucket 记账→null cell Sharpe；逐 cell own-null 池 2000 值（CN 家族「逐腿 own-null」先例）；seed=`SEED_REGISTRY['cn_sector_leader_p1']`=**20277200**+k（k<2000·跑前登记·band 20277200..20279200 构造性零碰撞：cn_kline_pattern_p1 带顶 20277100 之上·rg 全档扫描零命中 2026-09-27 06:3x 留痕）；skill_line=own-null 池分位；双法并列：block bootstrap 2000 draws（块长 10）+ sign-flip 2000 draws，p 值双报。
- **账本**：`science_gates.append_ledger('CN_SECTOR_LEADER_P1', 2004, 'cn_sector_leader_p1', evidence_cutoff='2026-09-22')` dict schema 唯一禁手抄 prev。
- **虚拟起点面（RANDOM_LARGE_SAMPLE_LAW §2.1）**：cell 组合日序列全史枚举 census——起点日序号∈[200, T−126]，每起点 126 交易日窗（收益/胜率/beat vs 宇宙 EW 代理）；分段 4 类（bull/bear/deep-bear/chop·sse 态打标同 REV_OSC/KLINE §2.1 冻结面）逐列；任一分段起点数<500=insufficient-sample 如实注记。**随机分窗（§2.3）**：train/validation 随机划分 ≥100 次 + walk-forward 5 顺序折叠双证。
- **随机参数 sensitivity 描述腿（§2.2 空间填充·描述面零判定宣称）**：Sobol N=500 draws over（W∈[10,60]·K∈[1,5]·H∈[5,20] 整数格·同一编码同执行同成本 x1 面）；scramble seed-sequence `np.random.default_rng([20277200, 2000])`（census_fusion_s2_unc seed-sequence 派生先例·无带占用）；产物=Sharpe/均值/maxDD 分布描述列，**不计 N_eff、不设门、禁幸存者宣称**——本批 judged cells=folklore 叙事+工程冻结轴，零参数搜寻宣称（KLINE 同式判读先例），sensitivity 腿=§2.2 诚实履约面。

### §3.1 judged 格表（4 cells，判面 x2，全冻结）

| cell | 入场 | 出场（先到先计） |
|---|---|---|
| LDR-FIX10 | trigger cohort | H=10td（④工程冻结） |
| LDR-FIX20 | trigger cohort | H=20td（④工程冻结） |
| LDR-SECT10 | trigger cohort | H=10td ∨ 板块∉hot_rank(t′) 次开（④卡#7 方向代理） |
| LDR-STOP10 | trigger cohort | H=10td ∨ close≤入场价×0.92 次开（engine −8% 面） |

## §4 判据【跑前写死·共享库调用禁手抄判线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=2004, pool='stock_b_layer', n_trades, n_entries, null_pool=<本批 2000-null own 池>)`**（pool 口径=WILD-S1/KLINE 股票域先例）：全期 Sharpe > skill_line_v2 ∧ 平稳 bootstrap CI 下界>0 ∧ entries≥30（F6 双口径）；逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：DSR≥0.95（deflated_sharpe_ratio 原始日序列·禁 dsr_from_stats 充数）∧ PBO≤0.25（screening/pbo.py CSCV 8 块·4 臂家族矩阵）。
- 批面要求（披露列）：annualized>0 ∧ OOS（≥2025-01-01·composite_ic.IS_END 共享分割）双正 ∧ maxDD≥−35%。

## §5 跑前预测【写死于跑前，跑后对账】

1. **随机本底高企判负照报概率高**：KLINE 实证 A 股个股 35 年随机时点同持有面 null mu≈0.42-2.1 Sharpe → 本批 own-null 线预期 1.5-3.0 带；热板块龙头 20d 强势=T+1 追高均值回归压力面（s2 slice-A 个股短期反转>动量实证）→ 毛面预期 Sharpe −0.5..+0.5 薄带、大概率 <线（claim≠verify；涨停生态 2017+ 衰减同族证据面 WILD-S1 §8）。
2. SECT10 退潮出场 vs FIX10=maxDD 改善 10-30% 方向（早出避板块退潮尾部）、Sharpe ±20% 带内 whipsaw 对冲；STOP10 −8% 硬止损=同面修饰。
3. entries 面：17,823 触发全史均匀（380-630/年）→ trade gate 全过、CI 紧；2017+ 段若衰减与 WILD-S1 同向（板块轮动加速+龙头溢价被量化收割面）→ W2017 子窗 Sharpe 低于全窗 30%+ 概率高。
4. **极端日先验（硬界三件套 c·KLINE 同窗实证锚）**：2015-06/07 崩盘窗=hot 板块极端轮动+cohort 涌入日；2024-09-30 政策脉冲（KLINE TWS 截面峰同日 256 员）=板块普涨面，本面 K_TOP=3 截断→单日触发≤3 构造性 cap 如实；2024-02-28 微盘崩；2016-01 熔断窗=maxDD 集中面。
5. x1 面净 Sharpe ≥ x2 面（中频 churn：V2 双边成本侵蚀毛收益 10-30%）。
6. D6 预判：vs ew6 canon max|corr|<0.4（跨工具域+事件稀释）；批内两两（4 cells 同入场不同出场）预期 0.5-0.9 高相关带如实报。

## §6 产物

- `results/cn_sector_leader/p1_results.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+D6 表+judged 判读+N 计数+涨停面剔除/不可成交拒单披露+Sobol 描述腿+census+分窗产物）；`results/cn_sector_leader/cells/*.json|npy` per-cell/per-null-shard checkpoint；`results/gate_attrition.json` 追加一行（**entries 列表面·r248 律**）。
- runner=scripts/cn_sector_leader_p1.py（冻结 commit 后建·R99 序：prereg 冻结先于 runner build 先于任何 run；selftest 子命令=离线自检 hermetic fixtures·**B7b 契约腿必带**（下游下标键集 ⊆ stats 构造键集断言·R297 坑律））。

## §7 跑后实证【跑前为空——占位纪律：写数字即造假】

（一次定稿 2026-09-27 R302 bm-a autofill burn pid 64840·07:20:16 开烧→`results/cn_sector_leader/p1_results.json` 07:28:39·elapsed ~503s·池 done-flip+result_ref 同轮：**4/4 cells 判负照报**——x2 判面全期 Sharpe LDR-FIX10 −0.5378/LDR-FIX20 +0.2288/LDR-SECT10 −1.3880/LDR-STOP10 −1.0618；skill line（own-null 校准）2.041（H10 系·mu_null 0.8413）/3.5375（H20 系·mu_null 2.0495）全数 line_ok=False ∧ bootstrap CI 下界 −0.9239/−0.1691/−1.7376/−1.4375 全 ≤0；DSR 0.0/0.0007/0.0/0.0 全 <<0.95；family PBO 0.0（FIX20 IS-best 70/70 组合·OOS rank 1——但 G1 挂→G2 eligible_v2=False 4/4）；批面 cells_ok 4/4 False（ann −0.71~−0.83<0 ∧ maxDD −1.0<−35% 双挂；OOS 2025+ oos_sharpe 1.45-4.01 正号如实=oos_ann 列正但批面 AND 规则全挂·单窗正号不救判据）；entries 面 17,823 事件→17,771 filled/cell（trade gate 过·全史均匀 380-630/年健康）；rejects=limit_reject 50+susp_end 2（不可成交计数不弃账）·触发端涨停面剔除 2,562（census 冻结面）；D6 max|corr| vs ew6 canon ≤0.0375 无拒收（§1 预判 <0.4 ✓·事件稀释+跨工具域）；批内两两 0.5082-0.8733（§1 预判 0.5-0.9 ✓）；robust 双法=sign-flip p 0.002/0.171/0.0/0.0 + block bootstrap p≤0 0.8625/0.325/0.9995/0.993；虚拟起点 census 8,466 起点四段全 sufficient（bull 2415/bear 3170/deep_bear 717/chop 2164）·beat_rate_6m 0.3161/0.3943/0.2004/0.2594 全 <0.5·oos_halves 后半 −1.40/−1.54/−1.24/−1.63 全负（衰减方向面）·walk-forward 5 折正负交替偏负·split_sign_agreement 100% 4/4；null 池 mu 0.8413（H10）/2.0495（H20）——**A 股个股随机同持有漂移本底再证（KLINE 0.42-2.1 带内上段），龙头追高面判负=负期望+跑不赢随机本底双挂**；x1 面披露列 −0.1766/+0.4956/−0.9511/−0.6972（x1≥x2 4/4 ✓）；Sobol 500 描述腿 Sharpe −0.37..+0.38 带·maxDD −1.0 全（§2.2 诚实履约·零幸存者宣称·judged=冻结轴零参数搜寻宣称）。ledger 204,445=202,441+2,004 单计 ✓；attrition 行 entries 列表面 ✓（ts 07:28:39·r248 律）。）

## §8 批后复盘【必填·s7-T】

（2026-09-27 R302 定稿。**§5 六预测对账**：①「随机本底高企判负照报」→ **命中**（own-null 线 2.041/3.5375；毛面 x1 −0.95..+0.50 落 −0.5..+0.5 薄带内；judged-negative 4/4——但 H20 线 3.5375 超预测带上沿 3.0：持有窗越长随机底越高=预测带未按 H 分层，粒度不足如实记）；②「SECT10 vs FIX10=maxDD 改善 10-30%、Sharpe ±20% 带内」→ **MISS**（maxDD 同 −1.0 无差异化——35 年负漂移复利下 DD 面由 ann 决定非出场修饰=KLINE ③ 同律再证；Sharpe −0.538→−1.388 恶化 158% 远超 ±20% 带=退潮出场 whipsaw 成本主导；STOP10 −1.0618 同向=硬止损不救复利面）；③「trade gate 全过；2017+ 衰减同向」→ **命中**（17,771≥30 全过；oos_halves 后半全负+wf 后折负=衰减方向 ✓；未单列 W2017 子窗=预测粒度不足如实）；④「极端日先验」→ maxDD −1.0 全 cell=ann −56%~−83% 复利归零面（2015 崩盘窗集中归因不可分离=未验证面 honest note）；⑤「x1≥x2」→ **4/4 全中**（成本侵蚀 0.18-0.46 Sharpe/腿）；⑥「D6 <0.4 ∧ 批内 0.5-0.9」→ **全中**（0.0375 上限；0.508-0.873 实测带）。**判线读数**：判负语义=「板块垄断溢价追高不如随机时点+跑不赢高随机本底双挂」——与 WILD-S1（涨停事件面 judged DEAD）合并=**行 3 龙头战法流派全 judged-closed**；判负不重开律生效：板块龙头面（本编码·本执行域·SW L2 谱系）**判负关槽**，新证据=新预注册（板块粒度/龙头定义/出场域变体须另立 prereg 禁本批翻案）。**gate_attrition**：own 行在册（entries 列表面·r248 律）。**回执面**：T-87 s2 队列 #4 闭环（freeze b3d72924→runner R300→池提交 R300→claim 07:20:16 latency 18.8min 超标如实=R301 饿批窗已报→burn 503s→judged 定稿全链 R99 序合规）；后续=①post_review criteria 注册（CN_SECTOR_LEADER_P1 判据锚 §7/§8 稳定产物件·本轮随做）②SCHOOL 下一候选=#5 行 16 市场中性（工程量最重：期货保证金/移仓成本+CTA 禁翻案边界机制披露）。）
