# WILD_ROUTE_S1 预注册（跑前冻结件 · R99 律：本 commit 前 = 仅数据面探针，零策略跑批）

> 模板：research/PREREG_TEMPLATE.md（逐节齐填）；权威：BACKTEST_SCIENCE.md v2＋BACKTEST_PLAN 三铁律＋COMPUTE_AUDIT.md；卡片输入=research/WILD_ROUTE_LAB_S1_CARDS.md（s1 收口件，本批唯一阈值来源面）；探针证据=results/wild_route/wild_route_probe.json；载体=scripts/wild_route_lab.py（selftest 22/22 hermetic）。

## §0 批件身份

- **批名/批号**：WILD_ROUTE_S1（T-2026-09-25-57 s2/s3 · CEO 直令 O-20260925-1132 股域重开新线）
- **格子（N_eff 口径）**：29 pattern 臂 × 3 宇宙 × 9 窗 × 2 成本面 = 1566 ＋ 3 regime 附加格 = **1569 cells ＋ K=50 nulls = N_eff 1619**（确定性 census，enumerate_cells 冻结枚举；扩容即买单）
- **认领**：T-57 票 bm-b r174 认领锁在册；F-04 MSG 于入池 commit 同窗先落（fleet/inbox/，入池条目引用）；部门=研究部（编码）＋策略部（规则/门）＋工程部（载体/池）联合（票面 mandate）
- **算力预算**：引擎一次构建 ~1-2min + 每格 ~0.3-1.5s → 8 分片（每片 ~196 格）估 5-25min/片；workers_plan=每分片 1 进程（O-2130：≤floor(核×0.8)，本批单进程向量内存面为主）；>10min 批已后台化+跨轮 checkpoint（每格 JSON + 分片 jsonl 断点续跑，行自带 key r163 律）
- **批报告必带 audit 段**（COMPUTE_AUDIT 章）。

## §1 α 机制段【D6 · 四选一勾选】

- [x] **行为偏差**：涨停事件=注意力稀缺锚（醒目涨幅进散户决策集）＋追涨/延续偏置（处置效应反面）；跟风盘与打板族为「注意力溢价」付出代价——由次日高位接盘的迟到者付钱。涨停/炸板/连板高度全市场是注意力度量面，野路子战法=对注意力流的显式下注。
- 先验负上下文（CARDS §〇.1）：zoo #75 行为延续族出谱（旧域批 2A 深负+批二 0/19）——**不阻断**（CEO O-1132 股域重开=新域新判），作 prior-negative 注记，s4 判决以股域实测为准。
- **同族相关性披露（D6）**：12 卡全部=涨停事件流族（机制面「涨停事件后的短线行为延续/承接」），族内臂相关**预期高**——本批以族内 PBO（CSCV 8 块、29 臂家族矩阵）承担过拟合惩罚，族内高相关=披露非互斥；**跨在册交易员 max|corr| 检查**：在册 6 员全为 core48 ETF 轮动/组合（不同品种不同机制面），预期低相关；幸存者注册时按 sleeve-tag 先例逐对实算 `max|corr|`（日收益口径），≥0.7 拒收——注册管线既有闸，本批不豁免。

## §2 数据与面板【跑前探针事实 · wild_route_probe.json】

- **宇宙/池**：P-1c Stage-A 缓存（Money02/data/cache/p1c_stock，qfq 已证事件日精确；r105 census 律：generated=2026-09-24 03:42:50 冻结，census gate 在探针与载体双侧内建，漂移即拒跑）。N=5222，T=8792（1990-12-19→2026-09-22），ok 集=bars≥250 复算 **5130=meta 一致**；板型分布 main 3197 / 创业 1407 / 科创 618，**北交所零在场**（天然剔除）。ST 剔除=data/fundamental/eligibility.csv r2_st 当前快照（-201 员）——**点时快照近似**（历史 ST 变更不可得，诚实披露，无 invent 补数）；上市<365d ≈ bars≥250 口径（P-1c MIN_ROWS 同构）。U_full=5130−201≈4929 静态；U_limup60（尾 60 日≥1 封板）/U_leader60（尾 60 日 max runs≥2）=日频动态子池（票面「涨停池/龙头池子集」的冻结实现）。
- **窗口与 evidence_cutoff（D2 前向锁盒）**：**cutoff=2026-09-22**（Stage-A 面板末 bar；结果 JSON 顶层 evidence_cutoff + science_gates.cutoff_meta(cutoff) 双字段，缺=C2 VIOLATION）。窗=W_full（2001-01-01→cutoff，25y 深史主轴）＋8 个 8 年错位窗（1996/1999/…/2017 起，T-22 海量虚拟时点的事件策略同构）。cutoff 后新 bar 锁定不得回流本批。
- **涨停判定数据面（探针实证）**：封板=close==high（浮点恒等）∧ qfq 日环比 ≥ 板型/日期阈值（main 0.0975、创科 0.1975；创业板 20cm 仅自 2020-08-24、科创自 2019-07-22）；悬崖实证：近期域捕获率 main **99.4%**/深史域（1995-2005，f<1 qfq）**95.8%**；日涨停家数近期均值 **70.11**（公开现实带 30-150 内）；炸板率近期 **36.8%**（定义面=触及未封，含近失日，披露为定义依赖读数）；regime 三轴全日频可算（高度中位 5 板/p90 9 板，与情绪周期表带吻合）。
- **数据完备门**：载体 census gate（census 漂移拒跑）＋每格零事件诚实腿（n_entries=0 → cell 记 NULL 非造假）＋封板/一字/停牌三拒面逐格计数（un-captured premium 台账）。
- **已知数据面边界（诚实披露，禁发明）**：①**换手率场死面**（non-nan 0.01%）→ #5/#6/#12 换手阈值腿全部缺席披露，量能门一律 vol/amount 比替代；②qfq 除权日涨停关系结构性不可检测（除权基准价不在面板）→ 除权日真涨停=假阴性、qfq 比值恰入带=假阳性，双向发生率不入档（探针悬崖主质量 99%+ 证明带内主质量为真封板）；③ST 历史变更无面（点时近似）；④一字/近涨停开盘买入=乐观偏差 → 入场拒单记账（#1 9% 论证同族）。

## §3 方法学

- **编码（冻结，CARDS §二 29 臂）**：P01 打板9%（high/prev≥9% ∧ 非一字，hold1）；P02 一进二（runs==2 确认日）；P03a/b 断板低吸/反包（炸板事件；反包腿 vol-ratio∈[0.8,0.9] S-A 硬阈）；P04a/b/c 凤还巢金/银/火（level=high−range×{0.25,0.5,1.0}，买日 a+{5,7,9}，调整缩量+介入放量，>13 天失效由固定窗内含）；P05a/b 首阴高开腿/反包腿（runs≥2 ∧ 段内首阴 ∧ 当日最高连板者 ∧ vol∈[1.5,2.0]×前日；A=次日开盘≥+2%，B=次日收盘>事件日 high；止损=−3% ∨ 破 MA5 次日开盘出，仓位=1/5 桶近似「单笔≤20%」）；P06 烂板 hold{1,2,3,5}×{全/阳线}=8 臂；P07a/b 地天板无条件/条件臂（条件=尾 5 日存跌停日 ∧ vol≥2×最近跌停日）；P08 冰点卡位（regime 退潮→主升反转日 ∧ 封板 ∧ runs==1 首板代理）；P09a/b 高度 4/5 板跟风、P09c 空间打开（heights 创 60 日窗高）；P10 老妖回魂（**自设面披露**：M=尾 120 日 max runs≥3、沉寂≥10d、回调≤10% 硬门 B+、缩量、再涨停——外部零源腿=M/N 自设+命名权本批，CARDS 卡 #10 冻结）；P11a/b 龙字辈/全名对照（龙头=runs==heights≥3 确立日次日跟风涨停 runs==1）；P12a/b/c 涨停基因（16 日窗涨停计数≥{2,3}×当日封板；c 臂=1.8×放量 S-C 参数）。
- **滞后规则（禁未来数据）**：信号全在 T 收盘可得（close/high/low/volume/pct_chg 收盘面）→ T+1 开盘成交；regime/连板/量比全用 ≤T 信息；除 T+1 开盘价外零未来引用。
- **执行口径（票 spec 冻结）**：entry=open_T+1 **仅当可成交**（bar 在场 ∧ 非停牌 ∧ 开盘未达涨停带 floor−0.002——一字/近涨停开盘=拒单入 un-captured premium 台账）；停牌出场顺延至复牌首开盘；exit=open_{T+1+H}（H=hold）。
- **成本口径**：**x1=V1 legacy 13bp/边**（双边乘性 (1−c)²），**x2=26bp/边=×2 压测面**；涨停价成交乐观偏差由拒单腿承担（无 ADV 参与帽——与 #6 复现口径对齐；ADV 帽敏感面=诚实边界注记）。
- **记账（桶式事件组合）**：资金分 H 桶，日 t 信号组=t+1 开盘建仓等权，组合净收益=(1+r)(1−c)²−1 逐桶均值，跨持有日均匀入账（hold-1=出场日单日入账；止损臂按实际出场日、名义 H=5 桶入账——近似披露）；日收益序列→全窗 Sharpe（×√252）。
- **null 对照**：K=50 同掩码随机事件日 null（基=`science_gates.SEED_REGISTRY['wild_route_s1']`=61000+k，**登记在册 2026-09-25 bm-b**；日事件数谱=P06_h1_all 全宇宙信号的日均谱，同日随机抽宇宙成员、同 hold-1 桶记账、同 x1 成本）；被动基线=注册池 `stock_b_layer`（P4_EXT_TILT 落地件 0.4606，registry 读取零手抄）。
- **账本**：`science_gates.append_ledger("WILD_ROUTE_S1", N_eff=1619, file_name=results/wild_route/wild_route_s1.json, evidence_cutoff="2026-09-22")`（finalize 单发守卫 WILD_ROUTE_S1_REFINALIZE）。

## §4 判据【跑前写死 · 共享库零手抄】

- **G1' v2（29 主格）**：`science_gates.g1_prime_v2(sharpe_full, returns=None(序列口径由 finalize 家族矩阵承担), batch_cells=1619, pool="stock_b_layer", n_trades, n_entries, min_trades=30, ci_seed=61000, null_pool=本批 50 nulls)`——skill_line_v2=max(被动+0.10, μ_null+σ_null·√(2·ln 1619)) 数据驱动现算；F6 双口径 entries≥30 为主；批报告逐列披露 skill_line/null 面/交易门全输入。
- **G2 v2**：`science_gates.g2_registration_v2(g1_pass, dsr, pbo)`——DSR≥0.95（`deflated_sharpe_ratio` 原始日收益序列跑）∧ 家族 PBO≤0.25（`screening/pbo.cscv_pbo` CSCV 8 块、29 臂家族矩阵=主格日收益）。
- **描述性条款（批级披露不替代 v2 门）**：年化>0、OOS（窗末 30%）双正、maxDD≥−35%、无≤−30% 崩年、成本×2 面存活披露（x1→x2 Sharpe 衰减逐臂表）。
- **硬界设计三件套（D-20260925-01①·检测/健康面）**：(a) 封板检测分布界已在探针在档（悬崖主质量 median/p99.9 面，非裸 max）；(b) 极端事件密度日（2015-06/07 救市、2016-01 熔断、2024-09/10 暴力反弹：千股涨停/炸板极值日）=**危机日豁免单列**——事件数极值为合法市场结构，豁免路径=逐日单列披露于批报告，禁整批判负；(c) 跑前预测 §5 已给极端日先验（第 5 条）。
- **诚实负行**：预期负臂照报（s4 verdict：dead=dead），funnel 双列（收割 12 vs 过门 N）。

## §5 跑前预测【写死于跑前 · 跑后对账】

1. **#6 校准锚（本批唯一大卡）**：纯主板 hold1 全臂=邢不行 N=61939 复现口径最近臂 → 预期全窗日期望 **+0.4%~+0.9%**、胜率 **52%~53%**；近年段（2020+）日期望预期显著低于全窗（作者自认近年衰减+「alpha 最后一跳」专文=拥挤硬证据）——**衰减张力条**：若 2020+ 段读数 < 全窗读数的 50%，方向验证拥挤衰减；阳线条件臂预期 > 全臂（复现面 42%→54% 年化梯度）。
2. **追高臂判负预期**：#2 一进二/#9 高度 4/5/#10 回魂/#1 打板 → 预期多数臂全窗 Sharpe < skill_line 或为负（S-F「还不如 60 日均线」创业板实证＋S-G 40 日 0% 晋级窗双参照）。
3. **#5 首阴判负预期**：北炒/陈小群显学=高拥挤面 → 预期不过 G1'（zoo #75 首阴族出谱 prior）。
4. **#11 跟风 honest-negative 主向**：跟风腿显著弱于龙头腿为民间共识 → 预期负/零 edge；**龙字辈臂 vs 全名对照臂差值 ≈ 0**（命名梗无额外跟风溢价=CEO「国民梗传播力」命题的本批反证预期）。
5. **极端日先验（三件套 c）**：窗内必遇千股涨停日（2015-06 起）与熔断日（2016-01）——单日事件数可较中位数放大 **10-50×**（近期中位 ~60/日 → 极值日 500-1500/日），bucket cohort 规模极值=合法结构非腐坏；此类日逐日单列豁免披露。
6. **稀事件臂拒收预期**：#7 地天板/#8 冰点卡位/#10 回魂 → entries 可能 <30 → F6 门槛诚实拒收（合法判读非错误）。
7. **随机基线同批跑**：50 nulls 预期 Sharpe 分布中心 ≈0（同掩码等容随机）——skill_line 由 null 面实算，本批 N_eff=1619 下 skill_line 预期高于历史批（N 惩罚 √(2lnN) 项）。

## §6 产物

scripts/wild_route_lab.py（run/run-nulls/finalize/selftest/status）＋ results/wild_route/cells/<cell>.json（1569 件，断点续跑面）＋ wild_route_s1_nulls.json（50 nulls）＋ **wild_route_s1.json（顶层 evidence_cutoff="2026-09-22" + science_gates.cutoff_meta）** ＋ wild_route_s1_primaries.csv（29 主格镜像行）＋ 本文件 §7 回填。

## §7 跑后实证【跑前必须为空——写数字即造假】

（占位纪律：一次定稿；工程修复重跑双跑留痕；确定性引擎产物写 bug 的合法重执行≠结果重跑）

- **交付事实（2026-09-25 r204 bm-b finalize）**：1569/1569 cells 全量落地（SHARD-0..7 三方验证：ckpt 全键 done:true＋磁盘 cell 件逐一在场＋跨片零重叠；0of8=197、其余各 196）＋50 nulls（r198 45s，seed 61000）＝N_eff 1619 与本 prereg 一致；finalize 单发 exit 0，产物三件齐：wild_route_s1.json（顶层 evidence_cutoff="2026-09-22"＋science_gates.cutoff_meta 双键在位）＋wild_route_s1_primaries.csv（25 行）＋nulls 件。
- **29 主格实况**：25 臂有交易（g1_prime_v2 评估域=25）；4 臂全窗零事件诚实 NULL（P05a_shouyin_gaokai／P05b_shouyin_fanbao／P08_bingdian_kawei／P11a_longzibei——首板/冰点/龙子辈事件面在冻结宇宙内无可成交样本）；家族矩阵=25 臂。
- **工程修复重跑留痕（合法重执行≠结果重跑）**：finalize 首发在族 PBO 调用点崩（_family_series 产出 dict 直接喂 cscv_pbo；align_returns 已 import 未上调用点——r162/r188 族条件路径首次激活崩溃），修=cscv_pbo(align_returns(pbo_in), 8)（零判据改动：同 8 块同 29 臂矩阵语义），确定性重跑 exit 0；selftest 32/32 绿（F18 夹具未镜像生产 dict 入参形态——r157/r180 族新例，坑录见 CODELY r204）。
- **判定数字（全量如档 wild_route_s1.json）**：family PBO=0.0（CSCV 8 块、25 臂、verdict=register_eligible 面）；nulls sharpe mean −1.1849／p95 −1.0533；**G1'v2＝0/25 全灭**；G2 域空（仅 G1 过线者评估）。主格最优=P09c_space_open 全窗 sharpe 0.2693／maxDD −0.5214，远低于 nulls p95 带上方存活所需；P01_daban9 主格全窗 −2.08／maxDD −20.6（十二民间模式在成本 x1 下的典型面貌）。
- **批结论=诚实负结果**：12 民间涨停街模式 29 臂在冻结宇宙/窗/成本下无一过 G1'v2；无臂进入注册管线（幸存者注册腿零触发＝零 corr 检查面）；§8 批后复盘（预测对账/门禁损耗/funnel/逐 pattern verdict）另轮执行。

## §8 批后复盘【s4 · s7-T】

- 预测对账（对/部分/错 七条逐一对账）＋门禁链损耗账（`results/gate_attrition.json` 追加行）＋skill_line 当批读数披露；
- funnel 双列宣告（12 卡收割 vs 过门数）＋拥挤注记逐行携带（CARDS §三总表：#6 极高/#5/#9 高…）＋s4 判决 per-pattern honest verdict（dead=dead 照报）；
- 幸存者注册：zoo 溯源 lineage=source-tagged wild-route（准入闸不变：G2 过线＋注册管线 corr 检查＋live/paper SIGNAL_BUILDERS 接线＋evidence_cutoff 元数据）；2017+ 板上衰减类证据面披露（若在）；
- 回执入轮报告＋CODELY.md 行级追加。
