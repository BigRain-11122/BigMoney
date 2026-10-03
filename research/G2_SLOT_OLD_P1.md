# G2_SLOT_OLD_P1 预注册 · G2 矿供 old 族 SLOT 泊位·阶段一富集普查面（core48 消费面·41 vendor 面·两段制第一段）

> **FROZEN v1.0（2026-10-03 bm-a r640 冻结窗）**：本件 commit 冻结先于任何 census run（R99 律）；冻结窗证链=①r639 族选探针（results/_r639bma_g2_slot_family_probe.json·first_family=old 43 面）②r640 roster+vendor 冒烟探针 **PASS**（results/_r640bma_slot_old_roster_probe.json：vendor HEAD==装锚 a770825 恒等·43 面全 smoke 绿·41 面日面板可导出·2 面 eps 诚实降级基本面道·core48 48 员 1631 td·vwap 可导出最差 0.9912）③种子带 g2_slot_old_p1_nulls=20530000 同冻结窗先注册（science_gates.SEED_REGISTRY·撞带扫描零命中·最高在册基 20520500 净距 9500）④banned_direction_gate 对本终稿 ADMIT rc0（回执见冻结 commit）。冻结后禁改 §0-§6 判据面；跑后只回填 §7/§8。
>
> 令链血统：O-20260930-1132（G2 矿供规模化第二波）+O-20260930-2054（供给面）→ G2_OVERLAP_CENSUS_P2（126 NEW-FACE 泊位·§8 下片「old_/stock_ 主力族先行」）→ r639 族选探针（first_family=old）→ **本件=old 族 SLOT 泊位**；O-20260930-1901（a)-1 廉价普查先行·逐族·禁一次性全量判决烧；TRIAL_LABOR_LAW 常设供给线。部门=dept:研究（G2 矿源线·judgment 面=阶段二）+dept:工程（vendor 引擎接线）；lane=单机短批 in-round 合法（O-2100 先例）。模板=research/PREREG_TEMPLATE.md＋结构镜像 G2_OVERLAP_CENSUS_P2（census 面）+MASS_TRIAL_W1（两段制 stage-1 面）+FUND-QUALITY-P1（§0.6 出场轴与 D6 段式）。

## §0 批件身份【必填·跑前】

- 批名/批号：**G2_SLOT_OLD_P1**。类别=**候选探索两段制 stage-1 富集普查面**（census 先例族：TSGATE-P1/GATE-RECHECK-A158/G2_OVERLAP_CENSUS_P2/CENSUS_FUS_S2）——**零判决宣称、零注册资格、零纸盘资格，一切输出 exploration 标注**；存活者的全量判决面（stage-2）=独立段冻结（本件 §9 追加节模式，跑前 commit）后才烧（MASS_TRIAL_W1 §9 同律）。
- 批内格数：**N_rows=61**＝41 vendor 面（每面 1 行富集测量）＋20 same-mask 随机 null（对照不占消费面）；ledger 记账行=61（见 §3 账本）。RETAIL_QUANT_TRACK 预算归因：30 日窗试验增量=61 行（<100 单批免归因线·<500 窗帽·如实申报），消费面=试炼语法族候选供给（wave-3 roster 合并面·MASS_TRIAL_W1 §10「语法可用即并入」条款）。
- 认领（F-04 先行）：fleet/inbox/ **MSG-2026-10-03-2015**（开工声明·双机在制窗口互不可见防撞车）＋任务票 **T-2026-10-03-159-P1**（bm-a 开票+同轮认领·O-1730 即时律·票号 fresh 核 origin max=T-158）；G2_OVERLAP_CENSUS_P2 §8 下片引用。
- 部门归属：dept:研究（矿源供给·G2 线）+dept:工程（vendor 接线）；烧批 lane=**bm-a in-round 单进程短批**。
- 算力预算：实测预估 **60-180s 单进程**（41+20 面 × [T=1631,N=48] torch CPU 张量算·r640 冒烟探针实证每面毫秒级）；**预算上限 300s（O-1901 ③）**，超限合法停如实披露；<5min=in-round 合法不入池（O-2100 先例）；批报告必带 audit 段（无 audit 段的结果不入账本）。

## §0.5 禁开方向硬闸【必填·跑前·D-20260930-41 §1.2】

- 跑前过闸（冻结窗）：`python Tools/banned_direction_gate.py --prereg research/G2_SLOT_OLD_P1.md` → 退出 0=放行（fail-closed）·冻结 commit 内回执。
- 人工预读结论：**族级零命中预期**——本族机制主张=量价交互/微观结构（volume-conditional information faces），非裸价格动量/反转；§1 机制段不写横截面动量/反转词面（机器闸为准·r483 清洗律）。
- **BAN-01/BAN-02 逐面并族规则（冻结·census「重叠族→引用在库 verdict 不重烧」律的批内载体）**：census 输出按公式 token 机械分类每面输入集——**纯价格面**（输入仅 open/close/high/low/returns·无 volume/vwap/amount 任一）且其排序内容为价格变化类（delta/rank(close)/rank(returns) 形态）=落入 BAN-01/BAN-02 原判负机制面（ETF 横截面裸动量/裸反转·falsified_by docs/audits/retail-quant-conclusions-v2-20260930.md#3·年度 −7.65%/−2.81% 实测），**该类面无论富集与否一律不提名 stage-2**（并族留痕·引用在库 verdict 禁重烧）；**量价交互面**（输入含 volume/vwap/amount 至少一项）=原判负未覆盖的新机制主张（(b) 型例外：原判负证伪的是「裸价格横截面动量/反转」，量价条件交互结构不在其覆盖面）——按本批富集读数裁定，提命名才升阶段二。
- 命中差证申报（若闸命中）：唯一可预期命中=词面误触（本节及 §1 避写禁向词面）；若实命中=按 exception_clause (b) 以本节并族规则+量价交互机制论证重呈，重呈不过=判不受理。
- 未补例外=判不受理；已烧格数计入浪费台账。

## §0.6 出场轴显式声明【O-20261001-1108 立法·TRIAL_LABOR_LAW §4·M02 双件门】

- 本批=stage-1 富集普查面（blend 腿=周频排序轮换近似·census 先例正典），**非 engine 判决路径**；出场轴声明：**②持有到底（周频排序轮换）**——blend 腿成员只因周频再平衡日落出 Top-16 排名离场（排序轮换离场=唯一出场），**无价格类出场**（无止盈/无止损/无衰减踢出/无持有上限）；null 腿同构。
- stage-2 判决面（§9 独立冻结）届时按 FUND 族双通道逐键申报补全（engine 缺省出场栈显式禁用双通道互斥断言+律 A 烧后出场原因普查 20% 门）；本节为 census 近似面的如实降级披露（blend 腿非 engine 口径、判据面零宣称）。

## §1 α 机制段【必填·D6·四选一】

- 机制勾选：**[x] 行为偏差（主）+ [x] 微观结构（辅）**——量价背离族：成交量是知情度与拥挤度的低噪声载体（相对价格），价格动而无量配合=情绪性/噪声性动量（散户追价不追量）、放量而价滞=知情资金进出未扩散；该信息结构的超额来自**为情绪性价格波动提供对手盘的行为交易者**（处置效应/追涨杀跌支付方）与**订单流冲击未完全收敛的微观摩擦**（放量日的执行足迹）。风险溢价/结构性两格不勾（本族无跨期风险承担主张、无制度日历主张）。
- **散户凭什么赢【§1.2·D-20260930-41 必填】**：**容量/制度面**——¥1,000,000 级账户在 48 员 ETF 面周频 Top-16 等权=容量无限、零杠杆、无执行竞争（机构不覆盖 48 员窄横截面的量价残差面）；速度面不赢也不依赖（周频慢执行·成本先扣 x2 保守口径如实测量）；数据面零独有（OHLCV 公开）——**强优势主张无法预先成立，本批恰是要测的问题本身**（机制主张以 burn 读数检验不以本段宣称为准）；机构已验证结论不复跑（WQ101 82 面在库判负已由 census 引用不重烧·本批 41 面全部为 census NEW-FACE 非重复面·r640 探针 leg2 三源交叉验证 43/43）。
- **同族相关性准入检查【必填·D6·census P2 §1「数值 0.7 口径归 SLOT 批」的执行载体】**：census 输出件计算每面 **x1 成本 blend 腿日收益序列** vs **在册六员全部成员**日收益序列（marks/paper 账本口径·sleeve-tag 先例）逐对 |corr|＋**批内 41×40/2 逐对**——(i) vs 在册成员 **max|corr| ≥ 0.7 → 该面 stage-2 不提名（并族留痕）**；(ii) 批内 ≥0.7=同族聚类披露（量价交互面同源端口预期高聚·census 阶段不处置·阶段二判面族去重时消费本清单）；数值与逐对清单全部落盘 results/g2_slot_old_p1/d6_numeric.json 后 §7 才许回填。

## §2 数据与面板【必填·跑前探针事实，非结果】

- 宇宙/面板：**core48 在役白名单 48 员**（knowledge/panel_gate.INSERVICE_WHITELIST·sha16 `abf3d43b9ca13ea5`·RW-4 冻结面）；**锚面四元组**：`data/daily/<code>.csv`＋raw `pd.read_csv` 直读截断（非引掣 load_core 池面·census 面缩窗）＋2020-01-02 起算（r640 探针：union 1631 td）＋预热窗=各面自含（vendor ts_* 算子窗内自掩·无外部 min_periods）。探针事实（results/_r640bma_slot_old_roster_probe.json leg5·2026-10-03 已跑绿）：48 员全在位、零缺列、min_rows/member=797（晚上市员 588080 族·面内 mask 处理）、union 末 bar=**cutoff 当日**。
- **vendor 引擎锚**（G-ANCHOR 同律·矿源件四元组）：`toolstack/repos/ml-quant-trading`（install_root=quant/toolstack/repos·主仓 gitignored 空间·r494 装锚）＋`HEAD==a770825f841504e41581f057b4d94160e6a50c2e`（r640 探针恒等实证）＋`mlquant.features.legacy_factors.LEGACY_REGISTRY` import 面＋torch 2.11.0+cu128 **CPU 踣**（GPU 不用=compute_audit 越权旗规避·微张量无 GPU 必要）；`_factors_old.py/legacy_factors.py/tensor_factors.py` sha256 三值冻结于探针件；**工程依赖披露**：装锚件包链含 yfinance import（数据加载器面·本批零调用）——2026-10-03 20:1x pip 补装（venv 本机面·零 token 零网络拉数据）。
- **面 roster 冻结**：41 烧面（probe family 43 − 2 降级）＋2 降级面（old_047/old_067·公式含 `eps` 标识=r640 探针 leg3 机械判**日面板不可导出**→诚实降级基本面道·转 T-2026-10-02-145 fundamental 线未来面·本批不烧不预支）；roster 逐面清单+公式冻结于探针件 `roster_freeze` 块·sha256 前缀 `a14f997673adf038`（全文见探针件）；runner selftest 断言 roster sha 恒等。
- 窗口与 **evidence_cutoff=2026-09-22**（D2 前向锁盒·P 族系同界；cutoff 后新 bar 锁定不得回流本批）；结果 JSON 顶层 `evidence_cutoff` + `science_gates.cutoff_meta("2026-09-22")` 双字段（缺字段=science_audit C2 VIOLATION）。
- **mask 定义（冻结）**：六字段（open/high/low/close/volume/amount）全 notna 且 volume>0 且 amount>0（r640 探针：vwap 可导出行占比最差 0.9912→不满行 mask 掉如实计数）＋上市前行 mask（vendor Panel 语义=pre-IPO masked）；vwap=amount/volume（p1c Stage-A 惯例·census W2-A 先例）。
- 数据完备门（不过门禁跑·fail-closed）：①48 员 csv 全在位零缺列（探针已绿）②union 末 bar≤cutoff 且 ==2026-09-22③vendor HEAD==装锚（探针已绿）④roster sha 恒等⑤种子带 disjoint（§3）。

## §3 方法学【必填·冻结】

- **面计算（冻结）**：每面 `LEGACY_REGISTRY[f](panel)` → [T,N] masked 因子张量（torch CPU·float32；vendor 算子语义零重写零重实现——vendor 单源 import 禁改 vendor 件）。
- **腿 (i) fwd-5d rank-IC**：逐日横截面 Spearman（masked 员内）因子 vs 5 交易日前瞻收益；输出=全窗逐日 IC 序列与 mean/std/IR；fwd-1d IC 副披露列。
- **腿 (ii) 周频 Top-16 blend 袖**：信号=每周首个交易日收盘因子值（masked 内取值）；持仓=该日因子值最高 16 员等权（Top-16=48 员 top tercile·census fusion 先例形）；执行=次一交易日开盘近似（census blend 腿先例·非 engine T+1 正典=stage-2 判面事）；成本=每换手单边 **13.041bp×成本面**（`rev_osc_stock_p1.COST_X1` 单源 import 禁手抄·runner 断言恒等·CN-C7 往返=26.082bp 申报）；**x1=13.041bp/边 主披露·x2=26.082bp/边 提名判面**；被动基线=同窗 48 员等权 B&H（EW48）；统计=全窗收益/maxDD＋滚动 126 td 窗 beat-rate（步长 21·T-22 caliber 镜像）。
- **腿 (iii) null 对照（BACKTEST_PLAN 三铁律）**：**20 same-mask 随机袖**——同 mask 同周频同 Top-16 等权同成本面，唯一差异=每周从当日合格宇宙均匀随机选 16 员（`rng([20530000, k])` 子流律·K=20）；null 带=20 袖 |mean IC| p95 与 beat-rate 分布（提名线 (i) 的分位基准）。**种子带先登记再跑**：`science_gates.SEED_REGISTRY["g2_slot_old_p1_nulls"]=20530000`（本冻结窗落键·撞带扫描零命中·与最高在册基 20520500 净距 9500·band [20530000,20530020) disjoint）。
- **腿 (iv) D6 数值面**：§1 清单逐对落盘。
- **账本（冻结）**：finalize 步 `science_gates.append_ledger(batch_name="G2_SLOT_OLD_P1", batch_trials=61, file_name="results/g2_slot_old_p1/g2_slot_old_p1_census.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev）。
- **政体分段**：逐面 blend 腿按 510300 t22 3-way proxy 政体标签分段统计（描述披露·census 无门）。

## §4 判据【必填·跑前写死，禁看结果调线】

- **本批=census 面：零注册/零判决判据**（exploration 标注一切输出；无 paper 资格、无入册宣称）。
- **提命名线（stage-2 短名单规则·冻结）**：面被提名 stage-2 当且仅当**全部三条**——①`|mean fwd-5d IC| > null 20 袖 |mean IC| 的 p95`；②**x2 成本面**全窗 blend 收益 > 同窗 EW48 被动；③x2 面 rolling-126td beat-rate ≥ 0.60；且不触 §0.5 BAN-01/02 并族规则、不触 §1 D6 vs 在册成员 ≥0.7 并族面。提命名≠注册≠纸盘资格——stage-2 判面须独立 §9 冻结后按 `science_gates.g1_prime_v2/g2_registration_v2` 共享库全判据走（判线禁手抄·缺输入=诚实拒收）。
- **硬界设计三件套【D-20260925-01①】**：本批无数据腐坏检测类判线（census 测量面）·max 硬界 N/A；极端日先验入 §5(c)。

## §5 跑前预测【必填·写死于跑前，跑后对账】

- (a) **存活稀疏**：提命名面 ≤3/41（在库 WQ101 82 面 0 显著先验＋C4 跨域单向门（股票域行为类迁 ETF 即死）双重压；若 ≥8 面过线=先查未来函数（vendor 算子 delay/shift 语义与 cutoff 截断面）再信富集）。
- (b) **量价结构差**：输入含 volume/vwap 的面（预期占多数）在 48 员 ETF 面的 IC 弱于纯价格面在股票面的历史先验——量在 ETF 指数化环境下信息含量低于单股（ETF 成交量=申赎+T+0 套利足迹·非个股知情度）；纯价格面则多落入 §0.5 并族规则不提名——**双面挤压=本族在 ETF 面富集预期低是机制先验不是放弃理由**（判负真关线·负结果如实入 §7）。
- (c) **极端日先验**：2024-09-30/10-08 级单日 ±8-10%（涨停簇日·mask 无涨跌停价列=不 mask 涨停日·如实披露）＋2020-02-03 疫情首日＋2015 段不在窗（2020 起算）；blend 周频腿在簇日有集中换仓暴露（描述披露非判据）。
- (d) **null 带**：|mean IC| p95 预期 0.02-0.05；beat-rate null 均值预期 0.35-0.55（随机袖 vs EW48 恒半输附近）。若 null p95 ≥0.10=随机机制异常先查袖构造。
- (e) **批内聚类**：41 面袖收益逐对 |corr|≥0.7 预期 ≥10 对（同源端口族）；vs 在册六员预期全对 <0.7（ETF 周频袖 vs 在册月频/日频策略族低重合——以实测为准）。

## §6 产物

- runner=`scripts/g2_slot_old_p1.py`（**待建·冻结后**；结构=census fusion w2 机制 import 复用+MASS_TRIAL load 面缩窗；selftest 子命令=roster sha 恒等+cutoff 截断+mask 门+种子 disjoint+确定性双跑字节恒等+F1 面计数）；
- probe=`results/_r640bma_slot_old_roster_probe.py`（已建已跑·PASS·事实件）；
- results：`results/g2_slot_old_p1/g2_slot_old_p1_census.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+gates 块）＋d6_numeric.json＋IC 逐面 CSV；
- 本文件 §7/§8 回填；轮报告回执。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】（2026-10-03 r641 bm-a 一次定稿回填）

- **执行实况**：selftest 6/6 PASS（roster sha 恒等/cutoff 截断/mask 门/种子带 disjoint/COST_X1 单源+vendor HEAD 锚/双跑字节恒等+F1 计数）→ gates 10/10 PASS → 正烧 **rc0·21.1s**（预算 300s 帽用量 7%·单进程 CPU）；41 面全计算零失败零缺信号周；grid=345 信号周（首信号 2020-01-02）；ledger 链 622336→**622397**（+61 行=41 面+20 null）；gate_attrition 行已追加（cells_ledger_delta=61·nominated=0）。
- **§5 对账**：(a) ✓ 提名 0/41 ≤3 预测线内；(b) ✓ 双面挤压实证落地——IC 层弱富集存在（18/41 面 |mean ic5| > null p95 0.01153·最大 |ic5|=0.0336〔old_064·负向〕）但 blend 翻译层全灭（x2 全窗 0/41 胜 EW48〔同窗 EW48=+46.45%〕·x2 beat-rate 0/41 过 0.60 线·最佳 0.40〔old_032〕）；(c) 政体分段披露面在件（census 无门）；(d) **两预测被证伪如实记**——null p95|meanIC|=0.01153 低于预测带 0.02-05（indicator-null 有效样本≈周频 ~345 周→se≈0.008→p95≈0.015 同阶，预测带定高；<0.10 机制异常线未触）；null beat-rate 均值 **0.0025** vs 预测 0.35-55 **证伪**——随机周频重选袖周换手 ~2/3 仓位→x2 成本拖累 ~13-17%/年 vs 零成本 EW48 B&H（+46%）→随机袖恒输非半输（预测漏了成本不对称面）；(e) ✓ vs 在册六员 max|corr|=0.432（old_046）全对 <0.7 零 D6 拒；批内 ≥0.7 对 **626/820=76%**（预测 ≥10 对大幅超额确认=同源端口族强聚类，阶段二若开族去重必消费本清单）。
- **并族分类面**：量价交互面 31（新机制主张按本批判读）/纯价格非变化内容 6/落入 BAN-01/02 并族 4 面（无论富集一律不提名·引用在库 verdict 不重烧）。
- **负向 IC 结构**：41 面中 20 面 mean ic5<0；|IC| 前 6 名负向占 4（old_064 −0.0336/old_038 −0.0300/old_027 −0.0259 等）——族级方向结构以反向（低量价配合面跌后反指）为主；冻结 §3 blend 腿按因子值最高 16 员 as-is 持多（无符号翻转声明）→负向面机械买入最差成员=全窗负收益如实测量（as-is 方向判决=本批冻结语义）。
- **本批判决面读数**：**0/41 提名 stage-2**（cond1 过 18/41·cond2 0/41·cond3 0/41·BAN 4·D6 拒 0）——老族量价面在 48 员 ETF 面有边际信息但冻结语法翻译不出正收益，负结果照报不粉饰；x1 披露面最佳 beat=0.6333（old_052·x1 非提名判面）供族谱档案。
- 产物：results/g2_slot_old_p1/{g2_slot_old_p1_census.json, d6_numeric.json, ic_by_face.csv, ic_daily.csv}（顶层 evidence_cutoff+science_gates.cutoff_meta+trials_ledger 块齐备）。

## §8 批后复盘【必填·s7-T】（r641 同窗回填）

- gate_attrition 行已追加（entries 列表面·r248 律）：batch=G2_SLOT_OLD_P1·kind=measurement·delta=61·total=622397·gates 块含提名线/分类/null 面。
- post_review 行已注册（results/post_review.jsonl append·id=G2-SLOT-OLD-P1-CENSUS·status=open·7 检全过：selftest 6/6+gates 10/10+四产物在位+ledger 块+attrition 行+cutoff 双字段+refuse-if-exists 守卫在位）。
- 判线 v2 当批读数回执：**不适用声明**——本批 census 探索面零注册零判决宣称（§4 冻结），无 g1_prime_v2/g2_registration_v2 消费面；stage-2 若立项须独立 §9 冻结+出场轴 FUND 族双通道逐键补全+science_gates 共享库判线（判线禁手抄）。
- 方法论资产卡：无新方法（机制 import 复用 census 先例族；indicator-null 构造为既有 sleeve-tag 先例的本批实例化非新方法论）——knowledge/METHODOLOGY_ASSETS.md 零追加（捕获律收口步如实）。
- 工程复盘：runner 新建 scripts/g2_slot_old_p1.py（约 870 行·vendor 单源 import 零重写·flat-cost 袖=census blend accrual 镜像+冻结成本面）；selftest 四犯修复（SEED_REGISTRY 字符串值 int 容错/REG6 NEEDLE-DE-01 笔误/k_nulls 未透传 null_sleeves/vendor sys.path 序）零 origin 伤害全在烧前窗内收敛。
