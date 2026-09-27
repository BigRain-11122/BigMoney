# 【已被取代存档 · owner bm-c r118 采纳裁决 2026-09-28 00:2x】本件=bm-c s1 自拟稿；正典 v2 预注册=**research/DECISION_CHAIN_V2_PREREG.md**（bm-a R365 侧支被采纳为底本+§9 三零跑修正 a1/a2/a3）。本件差异面（O-2340 路由表袖份额 vs RED 满帽袖·工件依赖设计）均已由正典件+§9 裁决覆盖。归档不删（append-only 纪律）。

# DECISION_CHAIN_V2_P1 预注册（T-2026-09-27-95 · CEO 直令 O-2026-09-27-2255「好好设置一下机制，尽快筛选出来合适的组合策略和决策链条」线 A · 决策链 v2 简化链批）

> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节）；跑前 commit 冻结；跑后只回填 §7/§8，禁改判据禁重跑。
> **版本=v2（简化链版·版本台账 v2 行 append-only）**。血统=DECISION_CHAIN.md v1.1 §四版本迭代律 + v1.1 断环定位（r318 finalize·results/decision_chain_e2e.json）+ r318 四环读数：环①温度计日分歧 0.7304（分歧起点 −0.0203 vs 一致 −0.0164=版本选择无救援）+环②成员路由全政体负（bear −0.0613/bull −0.0528/chop −0.0795·×2 全≈−0.12）+环③摩擦 −0.0665pp/−0.1266pp（零费反事实仍负）+环④进攻军 0 席（GREEN 起点 −0.0847）。
> **v2=环级一次改动集（预跑冻结·零调参）**：删日级成员路由（环②负贡献全政体实证→成员恒为六员等权核心）；政体信息只进「仓位梯帽+袖份额」两处；5 日确认滞回绕开环①日级失准；REV-OSC 熊袖首填环④熊席；repo 现金腿承接 RED 段现金收益。

## §0 批件身份【跑前】

- 批名 / 批号：DECISION_CHAIN_V2_P1（决策链 v2 简化链四臂批）。**批内新包络格（N_eff）=5,522** ＝ A′×{base,x2}×2,761 起点（legacy 1,255 + deep 1,506）——B/D 臂=v1.1 已计已测面逐字复算（G-REPRO-V2 完整性门面·非重判·零重计，反重复计数纪律 T-34 §0 先例）；C=被动基线非包络臂；A1/A2=v1 已消费网格零复算（G-REPRO-V2 锚探针面除外·probe 先例）；成员曲线=基础设施重派生零重计（T-22 血统·v1.1 §0 同律）。扩容即买单：臂/起点集/窗口族任何扩容按新格数入账。
- 认领：T-2026-09-27-95 claimed bm-c r118（CEO 即时律认领即开动·fetch-claim-push 原子窗 r239/r113 律）；F-04 先行=MSG-20260928-0005-bmc-decision-chain-v2（fleet/inbox/ 在制窗口声明+袖面/热度面工件派生请求——bm-b Money02 物理依赖面，本轮窗内补发如实注记）。
- 部门归属：dept:策略（链机制 spec·票面 owner）+研究（判读面）。
- 算力预算：**Stage A 成员曲线=本机（bm-c）无 checkpoint 面全量重派生 33,132 cells**（6 员×2,761 起点×{base,x2} 双面·t34._run_cell_curve 原语逐字·base=裸跑/x2=CostPatch(2.0)）≈ 3-6h @ min(cores−2, ram_guard) workers 分离池批（BelowNormal·O-1136 低优先·入 results/runnable_pool.json 轮不内联代跑）；Stage B 包络判读=纯向量化 <10min/face；审计段必带（无 audit 段不入账本·v1.1 §0 同律）。bm-b/bm-a 有既有 checkpoint 的机器运行同批时 Stage A 复用其本地曲线档（位级校验过→零重跑·v1.1 §0 同条款）。

## §1 α 机制段【D6——无机制段=批不受理】

- [x] **结构性行为机制（政体持续性下的条件部署——v1 血统继承+v2 收窄主张）**：市场政体呈持续性分段（bear/chop/bull 自相关），v1 实证「日级成员路由」不捕获该红利（环②全政体负）——v2 主张政体条件化的收益面在**仓位暴露度**（熊降杠杆避跌段+牛升杠杆吃持续段）与**袖配置**（熊态超跌反弹行为席），不在成员选择；**代价支付者**=梯切换摩擦（cap 变动日权重转移×单边费率）+5 日确认滞回的滞后成本（确认期内沿用旧 cap=翻转初期让分）——「简化是否更值」必须实测（CEO「尽快筛选」逐字）。
- D6 同族披露：本批零新交易员函数（成员=在册 6 员纯重放·T-78 出场叠加已内嵌于成员曲线血统）；A′-B/A′-D 臂间相关性=构造性（同书受控比较·v1.1 §1 同律）；袖面-核心/袖面-B 日收益 corr=运行时披露列非门（v1 臂间 corr 范式）。REV-OSC 袖=judged 批已过门面（O-2335 REFINE-BENCH 首炉最优格+T-87 judged 镜像）零重判。

## §2 数据与面板【跑前探针事实】

- 宇宙/池：双轴逐字复用 v1.1 §2 冻结面——legacy=core48 面板（evidence_cutoff=2026-09-24·跑前探针=面板末日 48 员一致）；deep=T-18 增长成员面板（2013-06-17 起·manifest PASS·cutoff=2026-09-22）；**binding cutoff=2026-09-22**（deep 面）；cutoff 后新 bar 锁定不回流本批；结果 JSON 顶层带 science_gates.cutoff_meta("2026-09-22")（缺字段=VIOLATION）。
- **新增数据面三件（v2 特有·全部按轴面板索引对齐采样=截断执法·窗口有界性=cutoff 锁）**：
  - **袖面序列工件**（bm-b 派生·Money02 stock panel 物理依赖）：results/rev_osc_e2e_sleeve/SERIES_FY_BG_TP8_{x1,x2}.json——rev_osc_stock_p1.load_panel()（lockbox 断言族全跑）+sim_cell(P, FY_BG_TP8 冻结格, face∈{x1,x2}) 全面板日净贡献序列（两桶平均=judged 口径逐字）+meta（cell 定义、COST_X1=13.041bp 股票口径、panel lockbox 期望值回显、生成 commit、inputs sha256）；序列日=stock 面板交易日 1990-12-19 起；对齐规则=按轴面板日历取值（缺失日=0.0 平坦如实披露）；窗口采样受轴面板末日有界（cutoff 后日期零采样）。
  - **repo 现金腿**：data/repo_daily/GC001.csv（T-88 s3 供面·newfqkline 主面）——日收益 r_repo(t)=close(t)/100/252（年化%→交易日惯例·alloc_backtest CASH_LEG canon 惯例逐字）；轴面板对齐 ffill；面板内缺失=前值；pre-2012-05-17=0.0 如实（本批窗口 2013+ 全覆盖）。
  - **热度历史工件**（bm-b 派生·Money02/data/lhb/lhb_detail.parquet 物理依赖）：results/rev_osc_e2e_sleeve/HEAT_HISTORY.json——market_clock_call._heat_face 规则逐字历史化（HOT(t)=当日 LHB 行数≥rolling-250d p80 且净买额>0；历史首日前=UNDETERMINED）；**UNDETERMINED/缺失→非 HOT fail-conservative（cap 不加成）**。
- 数据完备门（不过即 VOID 中止零产数）：
  - **G-CENSUS**（r105 律）：冻结 cutoff 下重枚举起点集逐位等于 T-22 finalize 记录 {legacy: 1,255, deep: 1,506}（源=results/t22_virtual_timepoints.json 实读，禁手抄）；
  - **G-ANCHOR**：6 员锚定门全过（T-22 run 门同款）；
  - **G-V3**（两腿·v1.1 s9.3 修正语义逐字）：leg-1 校准窗状态计数位级==校准批记录（GREEN=664/YELLOW=772/ORANGE=35/RED=161·源实读）；leg-2=新鲜度+字母表+双读数披露（v1 在役 vs v3 校准层永不断言相等）；
  - **G-MANIFEST**：t18 manifest verdict==PASS 且 48 员；
  - **G-SLEEVE**（本批新增）：袖面双面工件在位+JSON 可解析+meta 字段齐（cell name/COST/lockbox 回显/sha256）+序列覆盖轴面板全日历（缺失率=0 允许且如实计数披露——序列按构造为全面板长度，采样日缺失=股票面板与轴面板交易日差异·计数入产物）；
  - **G-REPO**：GC001.csv 可读+末日≥2026-09-22（覆盖 binding cutoff）；
  - **G-HEAT**：热度工件在位+字母表校验（值域⊆{HOT,COLD,UNDETERMINED}）+覆盖轴面板末日；
  - **G-REPRO-V2**（本批核心完整性门·双锚）：①B/D 臂 base 面 12m 聚合读数（beat_rate/min_dd）**位级等于** results/decision_chain_e2e.json（v1.1 committed）对应读数——曲线重派生+包络公式双验；②A1/A2 探针 base 面（G-REPRO v1 同款）**位级等于** results/t34_early_signal_verdict.json 冻结读数（legacy 0.4296/0.4659·deep 0.3942/0.4304·dd −0.1249/−0.1041）——任一不等=管线漂移 VOID。

## §3 方法学【冻结】

- **四臂定义（与 v1 同构可比·全部冻结零新搜索）**：
  - **A′=v2 简化链臂**（本批唯一新臂）：
    - 原始态序列：legacy=v3 四态重放（GREEN/YELLOW/ORANGE/RED·live.paper.v3_state_series import-replay·v1 deploy_series 源逐字）；deep=T-22 冻结 3-way proxy（bull/chop/bear·na→chop·disclosed proxy 非第二真值源·主判读=legacy 轴）；
    - **5 日确认滞回**（环①绕开机制·N=5 票面冻结）：confirmed(t)=raw(t) 若 raw(t−4..t) 五连一致；否则 confirmed(t)=confirmed(t−1)；初值 confirmed(0)=raw(0)（确定性·零调参）；
    - 执行滞后：exec_shift(1)（T 收盘决策→T+1 生效·shift(1) 首行留自身态=无预positioning·v1 逐字）；
    - **仓位梯帽 cap**（clock L5 法常量 import 逐字·scripts/market_clock_call.py POSITION_LADDER+HOT_LADDER_BONUS）：legacy 确认态 GREEN=0.80（HOT 日=0.95）/YELLOW=0.65/ORANGE=0.50/RED=0.20；deep proxy bull→0.80/chop→0.50（proxy 混同 YELLOW/ORANGE 取保守 0.50·如实披露）/bear→0.20；HOT 判据=热度历史工件（G-HEAT）·UNDETERMINED→非 HOT；
    - **袖份额**（O-2340 L2 ROUTE_TABLE_V1 rev_osc 列 import 逐字·版本台账通道=袖入链唯一正典面）：legacy GREEN=0.00/YELLOW(CHOP 行)=0.00/ORANGE=0.30/RED=0.05；deep proxy bull→0.00/chop→0.00/bear→0.05；
    - 组合权重（恒和=1）：w_rev(t)=cap(t)·rev_share(t)；w_core(t)=cap(t)−w_rev(t)；w_cash(t)=1−cap(t)；
    - **日收益**：A′(t)=w_core(t)·r_core(t)+w_rev(t)·r_rev(t)+w_cash(t)·r_repo(t)−rate·Σ_c|Δw_c(t)|（首日豁免·v1 env_daily 同构三列扩展 [core,rev,cash]）；r_core(t)=六员等权=att(t)/6+5·chop5(t)/6（成员曲线=Stage A 派生）；r_rev(t)=袖面序列按轴面板日切片（face 对应·base→x1 序列/x2→x2 序列·judged 内嵌成本不随包络 face 再缩放·如实披露）；r_repo(t)=GC001/100/252；
  - **B=最佳单一策略不换臂**：COMPOSITE-CE-01 全窗满仓单持（v1.1 §3 逐字重放）；
  - **C=被动基线**：EW buy&hold（v1.1 逐字）；
  - **D=六员等权不换臂**：1/6 静态等权（v1.1 逐字·唯一再平衡=漂移回锚如实计费·D 乐观方向披露同 v1）。
- **包络构造**：v1 §3 逐字复用（env_daily 公式+起点日初始建仓不计费+T+1 shift(1) 赋权）——A′ 三列权重扩展为公式直书（上）；B/D 恒权重零包络换手构造披露同 v1。
- **窗口族**：{6m=126, 12m=252, 24m=504}·P-5 切片法·**主判窗=12m**；partial 窗如实标记·主读=完整窗子集（v1 逐字）。
- **政体分段（披露维度非门）**：T-22 3-way proxy 逐字——全臂×段 beat 率单列披露。
- **null 对照**：臂间受控比较（A′ vs B/D）+被动基线 C（T-34/v1 先例无随机 null）；bootstrap B=2000·**seed=20261002**（已登记 science_gates.SEED_REGISTRY["decision_chain_v2"]·顺序律跑前登记零修正窗）。
- **成本口径**：成员曲线 faces {base,x2} 全网格（base=COST_X2_RATE/2·x2=COST_X2_RATE·运行时派生禁手抄）；包络摩擦=rate_side(face) 单边率（v1 逐字）；袖面序列内嵌 COST_X1 股票口径（judged 镜像·T-91 活面同源·不随 face 再缩放——袖腿在 x2 面的生存压力=袖面 x2 序列工件承载·如实披露）；现金腿零摩擦（逆回购费率已内含于利率面）。
- **账本**：finalize 步 science_gates.append_ledger(batch_name="DECISION_CHAIN_V2_P1", batch_trials=5,522, file_name="decision_chain_v2.json", evidence_cutoff="2026-09-22")——禁手抄 prev。
- **反重复铁律**：v1 网格已消费零复算（B/D 复算=G-REPRO-V2 门面·A1/A2=G-REPRO-V2 锚探针面·均非重判零重计）；袖参数 FY_BG_TP8=judged 冻结零重判（O-2335/T-87 血统 import）；权重族融合网格 0/45 判负不重试（v2 简化非重搜索）；进攻军 0 席如实注记（T-94 存活者补席=v3 触发面·票面逐字）。

## §4 判据【跑前写死·禁看结果调线】

- **J-TARGET（序列级主判据·v1.1 §4 冻结口径逐字·零改动）**：**A′ pooled beat 率 > B 同面读数（逐轴×窗×面 pooled）且 A′ 最差起点回撤 ≥ −0.10**；序列主判=A′ 全轴×全窗×全面（2×3×2=12 格全过=序列 PASS）；月胜率=次级咨询指标。**迭代目标：v1→v2→…迭代直至主判据成立**；序列主判据与 per-run 咨询判读两级读数分开披露禁合并叙事。
- **J-C 同构复验（per-run 咨询面·A′ 代 A1·判线 v1 逐字）**：J-C1=A′ vs B 12m beat 率 95% bootstrap CI 下界>0.50；J-C2=A′ vs D 下界>0.50；J-C3=A′ vs C 下界>0.50；J-C4（红线）=四臂最差起点 12m 回撤均≥−0.35；**J-L 族=N/A 如实注记**（半档梯 A2 已内化于 v2 机制·J-L1/L2=v1 已消费判读面不在本批复验）。
- **断环再定位（四环·A′ 链赢否皆产·量化表禁叙事替代）**：
  - 环①（温度计）：原始态翻转率 vs 滞回后梯切换率（滞回复救面量化）+分歧起点/一致起点 A′ 表现对照；
  - 环②（路由→梯+袖净效应）：A′−D 逐政体段 12m 差（删路由后政体条件化的净贡献面）；
  - 环③（摩擦）：A′ 梯切换均值×rate 年化摩擦占毛收益份额+零费反事实 A″（同权重 rate=0）对照差；
  - 环④（席位）：袖激活日份额（w_rev>0 日占比）+袖日/非袖日 A′ vs B 均差（熊席填充效果——v2 袖=首版非空熊席）。
- **D7 四必报（每臂×轴×窗）**：OOS 笔数/覆盖年数/独立政体窗数/CI 宽度+25td 间隔子采样 beat 率（v1 逐字）。
- 诚实边界：PROSPECT 22 员与进攻军新席不入本批；环②偏好面缺口如实标注（v4 评估项另批）；本批零注册零 paper 接线零路由 spec 变更。

## §5 跑前预测【写死于跑前·≥3 条·含极端日先验】

1. **G-REPRO-V2 双锚位级复现**（确定性管线·置信最高）：B/D base 12m==v1.1 committed 逐位；A1/A2 探针==t34 verdict 冻结读数逐位。
2. **滞回减切换**：legacy 原始态日翻转率（~0.05-0.08/日量级·v3 序列实测窗）经 5 日确认后梯切换率降至 [30%, 60%] 带内（数学必然：五连一致过滤单点翻转）；A′ 换手≈v1 A1 换防 48 次/12m 的 [15%, 40%]。
3. **A′ 最差起点 dd 改善主源=RED 段 cap 0.20+现金腿**：从 v1.1 A 臂最差 −0.3194（×2 面）改善至 **[−0.16, −0.08] 带**；J-TARGET dd 腿过线概率 [50%, 75%]。
4. **J-TARGET beat 腿难**：B=同书满仓（legacy base 0.6096），A′ 现金腿稀释 bull 段（GREEN cap 0.80/0.95<满仓）→ A′ pooled beat>B 需 RED 段避险+袖贡献足额反超——诚实预期序列 PASS 概率 **[10%, 35%]**（v2 仍不达=断环再定位驱动 v3=迭代律内建非失败叙事·与 v1.1 §5.7 同构）。
5. **摩擦环**：A′ 年化摩擦占毛收益 [0.5%, 3%] 带（梯切换稀疏+现金腿零摩擦 vs v1 换防摩擦 3%-12%）；零费反事实差 [0, 0.5pp]/年。
6. **极端日先验（v1 三件套同源）**：2024-09-24/10-08、2025-04-07、2026-01-19——5 日滞回=单点状态翻转不触发梯切换（确认期平滑·费率尖峰面较 v1 收窄）；判据面=整窗读数与 dd 非单点检测线，极端日经整窗路径内化无豁免。
7. **袖面贡献**：bear 段袖激活（RED 份额 0.05/ORANGE 0.30）小额增强；judged bear 段 0.615 先验→袖日 A′−D 差 [0, +2pp] 带内；袖-核心 corr 披露列预期中低（超跌反弹 vs 趋势/震荡成员书行为差）。

## §6 产物

- script：scripts/decision_chain_v2.py（run/status/finalize/repro/selftest 子命令；Stage A=t22/t34 原语重派生双面曲线 checkpoint 分片续跑；Stage B=v2 权重构造+四臂判读+断环表；import-face 复用 t34_early_signal+t22_virtual_timepoints 枚举/装载/锚门/包络原语禁重写；selftest hermetic 离线夹具 r116 律+B7b 契约腿 r297 律）。
- 产物：results/decision_chain_v2.json（顶层 evidence_cutoff+cutoff_meta+audit 段+四臂×双轴×窗全表+J-TARGET+J-C 读数+断环四环量化表+corr 披露+D7 四字段+G-SLEEVE/G-REPO/G-HEAT 门读数）+ research/shortline/decision_chain_v2_results.csv（小件入 git）+ 本文件 §7/§8 回填 + research/DECISION_CHAIN_LEDGER.md v2 行 verdict 翻面。
- 下游：月度四件套「链条健康」节消费 v2 基线；版本台账 append-only；CEO 结果面=O-2255 时间表「v2 结果落地即报（负也报）」。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（finalize 于收割轮回填：G 门读数+四臂全表+J-TARGET/J-C 读数+断环表+预测对账+账本行）

## §8 批后复盘【必填·s7-T】

（一次定稿；预测对账；门禁链损耗账 results/gate_attrition.json 追加一行；回执入轮报告+CODELY.md 行级追加；v2 简化是否复救环①②/是否触发 v3 呈 GM）

## §9 零跑修正案（预留·append-only·零格已烧窗内合法）

（本节预留：仅规格升格/虚假前提实证类零跑修正可入；判线语义零触碰铁律同 v1.1 §9 族。）

## §10 依赖与执行分片（物理面如实）

- **袖面/热度工件=bm-b 物理依赖**（Money02 stock panel+lhb parquet 均 bm-b 在位·bm-c 实测缺位）：MSG-20260928-0005 已发 bm-b 请求派生（分钟级 sim_cell×2 面+热度旗历史化·小件 git 提交）；工件未落地=Stage B finalize 阻塞（G-SLEEVE/G-HEAT 门红）·Stage A 曲线池烧不依赖工件先行开烧。
- **Stage A 双面重派生=bm-c 本机面**（无 checkpoint 诚实披露）；bm-b/bm-a 跑同批允许 checkpoint 复用（位级校验前提）——多机分片合法（票锁只锁科学面·shards 数组口径）。
- 顺序律：本预注册 commit 冻结 → runner（scripts/decision_chain_v2.py）建+selftest → Stage A 入池开烧 → 工件齐+曲线齐 → finalize 判读 → 台账 verdict 翻面+CEO 呈报（O-2255 时间表·负也报）。
