# G2_SLOT_TAIL_P1 预注册 · G2 矿供尾段合并普查面（core48 消费面·6 族 69 面+2 修正面·两段制第一段）

> **FROZEN v1.0（2026-10-03 bm-a r644 冻结窗）**：本件 commit 冻结先于任何 census run（R99 律）；冻结窗证链=①r639 族选探针（results/_r639bma_g2_slot_family_probe.json·priority_table rank3-8=六非主力族·69 NEW-FACE 面）②r644 merged-tail roster+vendor 冒烟探针 **PASS**（results/_r644bma_slot_tail_roster_probe.json：vendor HEAD==装锚 a770825 恒等·126 tail 面 smoke 全绿·**vendor 实现级可导出裁定 69/69**〔r639 词元规则 54/69 的 15 面误降级全数纠正：eps=数值 epsilon/log2=算子/cs_rank=算子/中间量简写——_r644bma_vendor_adjudication.py 逐面 panel attr 扫描+合成面板 fail-closed 冒烟双证〕·core48 48 员 1631 td·vwap 可导出最差 0.991217·roster_freeze sha16 `4e4d5317750a2860`）③**old 族 roster 修正腿**（old_047/old_067：r640 窗按 r639 词元规则误降级基本面道——vendor 实现=纯面板〔doc_formula '+eps'=clamp_min(1e-9) 数值 epsilon 非 earnings〕·**首次测量非重烧**·old 族 0/41 判负在其已测集上不动·两面并入本批后 census P2 126 NEW-FACE 泊位达成全覆盖 41+2+14+69=126）④种子带 g2_slot_tail_p1_nulls=20550000 同冻结窗先注册（science_gates.SEED_REGISTRY·撞带扫描零命中·与 stock 族基 20540000 净距 10000·band [20550000,20550020) disjoint）⑤banned_direction_gate 对本终稿 ADMIT rc0（回执见冻结 commit）。冻结后禁改 §0-§6 判据面；跑后只回填 §7/§8。
>
> 令链血统：O-20260930-1132（G2 矿供规模化第二波）+O-20260930-2054（供给面）→ G2_OVERLAP_CENSUS_P2（126 NEW-FACE 泊位·§8 下片）→ old 族泊位收口（G2_SLOT_OLD_P1 r641：0/41 提名·诚实负向·族已答）→ stock 族泊位收口（G2_SLOT_STOCK_P1 r643：0/14·两主力族同谳=x2 翻译层结构性判负）→ **本件=尾段合并普查面（r643 下轮指针的泊位决策：逐族分泊 vs 合并尾段——本窗裁定=合并尾段）**；O-20260930-1901（意义性令四硬闸①廉价普查先行·富集才升烧）+O-20260930-1901 姊妹令（判负真关线禁保满载续烧）——**合并尾段设计 rationale（意义门三问自答）**：两主力族同层判负后，逐族分泊×6 将把已被结构回答的 x2 翻译层问题再问 6 遍；合并尾段以同冻结判线一次问完每族的 IC 富集问题（族级 verdict 仍逐族可导出=逐族纪律的判定面保持），算力 1 批 vs 6 批，信息/算力比最大化；**族级裁定不受合并影响**——每族提名计数独立落盘，判负族照真关线，富集族照 §4 提名线走 stage-2 独立冻结。部门=dept:研究（G2 矿源线·judgment 面=阶段二）+dept:工程（vendor 引擎接线）；lane=单机短批 in-round 合法（O-2100 先例）。模板=research/PREREG_TEMPLATE.md＋结构镜像 G2_SLOT_STOCK_P1.md（同族前片·r642/r643 先例全链）。

> **ERRATUM r644-b（冻结窗内·跑前·census run 之前）**：本件首版冻结（commit 1d9ec9202）的 roster_freeze sha16 转录笔误——首版写作 4e4d5317750a2880，探针件确定性真值=4e4d5317750a2860（末位 8→6；runner selftest L1 锚断言当场抓取·探针复跑双证恒等）。本勘误=锚指针字面归正，判据面（判线/roster 内容/种子/机制段/BAN 规则）零触碰；勘误 commit 仍先于任何 census run（R99 序保持）。

## §0 批件身份【必填·跑前】

- 批名/批号：**G2_SLOT_TAIL_P1**。类别=**候选探索两段制 stage-1 富集普查面**（census 先例族：TSGATE-P1/GATE-RECHECK-A158/G2_OVERLAP_CENSUS_P2/CENSUS_FUS_S2/G2_SLOT_OLD_P1/G2_SLOT_STOCK_P1）——**零判决宣称、零注册资格、零纸盘资格，一切输出 exploration 标注**；存活者的全量判决面（stage-2）=独立段冻结（本件 §9 追加节模式，跑前 commit）后才烧（MASS_TRIAL_W1 §9 同律）。
- 批内格数：**N_rows=91**＝71 vendor 面（69 尾段 NEW-FACE＋2 old 族 roster 修正面·每面 1 行富集测量）＋20 same-mask 随机 null（对照不占消费面）；ledger 记账行=91（见 §3 账本）。RETAIL_QUANT_TRACK 预算归因：30 日窗试验增量=91 行（<100 单批免归因线·<500 窗帽·如实申报），消费面=试炼语法族候选供给（wave-3 roster 合并面·MASS_TRIAL_W1 §10「语法可用即并入」条款）。
- 认领（F-04 先行）：fleet/inbox/ **MSG-2026-10-03-2155**（开工声明·双机在制窗口互不可见防撞车）＋任务票 **T-2026-10-03-161-P1**（bm-a 开票+同轮认领·O-1730 即时律血统·票号 fresh 核 origin max=T-160 @21:52 fetch）；G2_OVERLAP_CENSUS_P2 §8 下片引用（尾段合并收口片）。
- 部门归属：dept:研究（矿源供给·G2 线）+dept:工程（vendor 接线）；烧批 lane=**bm-a in-round 单进程短批**。
- 算力预算：实测预估 **30-120s 单进程**（71+20 面 × [T=1631,N=48] torch CPU 张量算；同构先验=old 族 61 行 21.1s·stock 族 34 行 18.3s·线性外推 91 行 ≈25-50s）；**预算上限 300s（O-1901 ③）**，超限合法停如实披露；<5min=in-round 合法不入池（O-2100 先例）；批报告必带 audit 段（无 audit 段的结果不入账本）。

## §0.5 禁开方向硬闸【必填·跑前·D-20260930-41 §1.2】

- 跑前过闸（冻结窗）：`python Tools/banned_direction_gate.py --prereg research/G2_SLOT_TAIL_P1.md` → 退出 0=放行（fail-closed）·冻结 commit 内回执。
- 人工预读结论：**本批=vendor 引擎尾段族（量价交互+价格结构混合）**——族级零命中预期与两主力族先验同源（ETF 48 员横截面·周频 blend 消费面·两族实测 x2 翻译层全灭）；§1 机制段不写已判负方向的词面（机器闸为准·r483 清洗律）。
- **BAN-01/BAN-02 逐面并族规则（冻结·与 G2_SLOT_OLD_P1/G2_SLOT_STOCK_P1 §0.5 同文·census「重叠族→引用在库 verdict 不重烧」律的批内载体）**：census 输出按公式 token 机械分类每面输入集——**纯价格面**（输入仅 open/close/high/low/returns·无 volume/vwap/amount/adv20/cap 任一）且其排序内容为价格变化类（`delta(`/`rank(close|open|high|low|ret)`/`corr(price,price)` 形态）=落入 BAN-01/BAN-02 原判负机制面（ETF 横截面裸动量/裸反转·falsified_by docs/audits/retail-quant-conclusions-v2-20260930.md#3·年度 −7.65%/−2.81% 实测），**该类面无论富集与否一律不提名 stage-2**（并族留痕·引用在库 verdict 禁重烧）；**量价交互面**（输入含 volume/vwap/amount 至少一项）=原判负未覆盖的新机制主张——按本批富集读数裁定，提命名才升阶段二。
- **本批机械预读（非判据·burn 时 runner classify_ban 机械落格·results/_r644bma_ban_preread.py 冻结窗实跑）**：71 面中量价交互面 38；纯价格面 33（price_other 32+price_banned 1）；price_banned=best_011（`cs_rank(open / delay(close, 1) - 1)`=1 日价格变化类排序面·机械命中 BAN-01/02 原判负形态·**测量照跑提名禁入**·并族留痕）；其余 32 price_other 面机械不字面命中价格变化类形态=按本批判读如实记账。规则按冻结面 as-is 执行如实披露，禁本窗临时加宽（判线漂移=红面）。
- 命中差证申报（若闸命中）：唯一可预期命中=词面误触（本节及 §1 避写禁向词面）；若实命中=按 exception_clause (b) 以本节并族规则+量价交互机制论证重呈，重呈不过=判不受理。
- 未补例外=判不受理；已烧格数计入浪费台账。

## §0.6 出场轴显式声明【O-20261001-1108 立法·TRIAL_LABOR_LAW §4·M02 双件门】

- 本批=stage-1 富集普查面（blend 腿=周频排序轮换近似·census 先例正典），**非 engine 判决路径**；出场轴声明：**②持有到底（周频排序轮换）**——blend 腿成员只因周频再平衡日落出 Top-16 排名离场（排序轮换离场=唯一出场），**无价格类出场**（无止盈/无止损/无衰减踢出/无持有上限）；null 腿同构。
- stage-2 判决面（§9 独立冻结）届时按 FUND 族双通道逐键申报补全（engine 缺省出场栈显式禁用双通道互斥断言+律 A 烧后出场原因普查 20% 门）；本节为 census 近似面的如实降级披露（blend 腿非 engine 口径、判据面零宣称）。

## §1 α 机制段【必填·D6·四选一】

- 机制勾选：**[x] 行为偏差（主）+ [x] 微观结构（辅）**——量价背离族谱系（与 old/stock 族同属 vendor 引擎量价信息结构家族）：成交量/成交额是知情度与拥挤度的低噪声载体（相对价格），价动量亏与量结构错位=情绪性/噪声性价格行为与知情资金足迹的可分信息；尾段六族（add/better/best/extra/original/change）端口形态=量价相关性/量能形态/价格结构位置/变化率族（日频横截面面非时序择时面）；该信息结构的超额来自**为情绪性价格波动提供对手盘的行为交易者**（处置效应/追高兑现支付方）与**订单流冲击未完全收敛的微观摩擦**。风险溢价/结构性两格不勾（本批无跨期风险承担主张、无制度日历主张）。
- **散户凭什么赢【§1.2·D-20260930-41 必填】**：**容量/制度面**——¥1,000,000 级账户在 48 员 ETF 面周频 Top-16 等权=容量无限、零杠杆、无执行竞争（机构不覆盖 48 员窄横截面的量价残差面）；速度面不赢也不依赖（周频慢执行·成本先扣 x2 保守口径如实测量）；数据面零独有（OHLCV 公开）——**强优势主张无法预先成立，本批恰是要测的问题本身**（机制主张以 burn 读数检验不以本段宣称为准）；机构已验证结论不复跑（本批 69 尾段面全部为 census NEW-FACE 非重复面·r644 探针三源交叉 69/69·56 UNVERIFIABLE 散文面+1 DUP 面不烧如实披露·old_047/old_067=roster 修正首测面非重烧面）。
- **同族相关性准入检查【必填·D6·census P2 §1「数值 0.7 口径归 SLOT 批」的执行载体】**：census 输出件计算每面 **x1 成本 blend 腿日收益序列** vs **在册六员全部成员**日收益序列（marks/paper 账本口径·sleeve-tag 先例）逐对 |corr|＋**批内 71×70/2 逐对**——(i) vs 在册成员 **max|corr| ≥ 0.7 → 该面 stage-2 不提名（并族留痕）**；(ii) 批内 ≥0.7=同族聚类披露（同源端口族预期高聚·census 阶段不处置·阶段二判面族去重时消费本清单）；数值与逐对清单全部落盘 results/g2_slot_tail_p1/d6_numeric.json 后 §7 才许回填。

## §2 数据与面板【必填·跑前探针事实，非结果】

- 宇宙/面板：**core48 在役白名单 48 员**（knowledge/panel_gate.INSERVICE_WHITELIST·sha16 `abf3d43b9ca13ea5`·RW-4 冻结面）；**锚面四元组**：`data/daily/<code>.csv`＋raw `pd.read_csv` 直读截断（非引掣 load_core 池面·census 面缩窗）＋2020-01-02 起算（r644 探针：union 1631 td）＋预热窗=各面自含（vendor 算子 ts_* 窗内自掩·无外部 min_periods）。探针事实（results/_r644bma_slot_tail_roster_probe.json leg5·2026-10-03 已跑绿）：48 员全在位、零缺列、min_rows/member=797（晚上市员 588080 族·面内 mask 处理）、union 末 bar=**cutoff 当日**。
- **vendor 引擎锚**（G-ANCHOR 同律·矿源件四元组）：`toolstack/repos/ml-quant-trading`（install_root=quant/toolstack/repos·主仓 gitignored 空间·r494 装锚）＋`HEAD==a770825f841504e41581f057b4d94160e6a50c2e`（r644 探针恒等实证）＋`mlquant.features.legacy_factors.LEGACY_REGISTRY` import 面＋torch 2.11.0+cu128 **CPU 跑**（GPU 不用=compute_audit 越权旗规避·微张量无 GPU 必要）；六族模块 sha256（_factors_add/_factors_better/_factors_best/_factors_extra/_factors_original/_factors_change.py）+legacy_factors.py/tensor_factors.py 冻结于探针件；**工程依赖披露**：装锚件包链含 yfinance import（数据加载器面·本批零调用）——r640 窗已 pip 补装（venv 本机面·零 token 零网络拉数据）。
- **面 roster 冻结**：**71 烧面**＝**69 尾段 NEW-FACE**（census P2 NEW-FACE·r639 探针 family rank3-8·r644 探针三源交叉 69/69·vendor 实现级可导出 69/69〔r639 词元规则 54/69 修正：15 误降级面全数归队——eps=数值 epsilon/log2=log 底 2 算子/cs_rank=横截面排序算子/close_loc·vwap_loc·volume_5=中间量简写/alpha=EWMA 衰减参数/close[t]=时序记号·_r644bma_vendor_adjudication.py 逐面 panel attr 扫描实证〕）＋**2 old 族 roster 修正面**（old_047/old_067·r640 窗 r639 词元规则误降级基本面道的同族假阳性〔doc_formula '+eps'=clamp_min(1e-9)〕·vendor 实现纯面板〔old_047=high/low/close·old_067=high/volume/vwap+cs_rank 算子〕·**首次测量非重烧**·old 族 0/41 判负在已测集不动）＝**census P2 126 NEW-FACE 泊位全覆盖收口片**（41+2+14+69=126）；排除面如实披露：56 UNVERIFIABLE 散文面（无可机读公式面·census 冻结 sec.4 state-4·smoke 虽绿但公式 provenance 未验证不烧）＋1 DUP-FORMULA-VERIFIED（在库 verdict 引用不重烧）＝vendor 126 − 69 burn − 57 排除，零丢失；roster 逐面清单冻结于探针件 `roster_freeze` 块·sha256 前缀 `4e4d5317750a2860`（全文见探针件）；runner selftest 断言 roster sha 恒等。
- 窗口与 **evidence_cutoff=2026-09-22**（D2 前向锁盒·P 族系同界；cutoff 后新 bar 锁定不得回流本批）；结果 JSON 顶层 `evidence_cutoff` + `science_gates.cutoff_meta("2026-09-22")` 双字段（缺字段=science_audit C2 VIOLATION）。
- **mask 定义（冻结·与 old/stock 族同文）**：六字段（open/high/low/close/volume/amount）全 notna 且 volume>0 且 amount>0（r644 探针：vwap 可导出行占比最差 0.991217→不满行 mask 掉如实计数）＋上市前行 mask（vendor Panel 语义=pre-IPO masked）；vwap=amount/volume（p1c Stage-A 惯例·census W2-A 先例）。
- 数据完备门（不过门禁跑·fail-closed）：①48 员 csv 全在位零缺列（探针已绿）②union 末 bar≤cutoff 且 ==2026-09-22③vendor HEAD==装锚（探针已绿）④roster sha 恒等⑤种子带 disjoint（§3）。

## §3 方法学【必填·冻结·与 G2_SLOT_STOCK_P1 §3 同构】

- **面计算（冻结）**：每面 `LEGACY_REGISTRY[f](panel)` → [T,N] masked 因子张量（torch CPU·float32；vendor 算子语义零重写零重实现——vendor 单源 import 禁改 vendor 件）。
- **腿 (i) fwd-5d rank-IC**：逐日横截面 Spearman（masked 员内）因子 vs 5 交易日前瞻收益；输出=全窗逐日 IC 序列与 mean/std/IR；fwd-1d IC 副披露列。
- **腿 (ii) 周频 Top-16 blend 袖**：信号=每周首个交易日收盘因子值（masked 内取值）；持仓=该日因子值最高 16 员等权（Top-16=48 员 top tercile·census fusion 先例形）；执行=次一交易日开盘近似（census blend 腿先例·非 engine T+1 正典=stage-2 判面事）；成本=每换手单边 **13.041bp×成本面**（`rev_osc_stock_p1.COST_X1` 单源 import 禁手抄·runner 断言恒等·CN-C7 往返=26.082bp 申报）；**x1=13.041bp/边 主披露·x2=26.082bp/边 提名判面**；被动基线=同窗 48 员等权 B&H（EW48）；统计=全窗收益/maxDD＋滚动 126 td 窗 beat-rate（步长 21·T-22 caliber 镜像）。
- **腿 (iii) null 对照（BACKTEST_PLAN 三铁律）**：**20 same-mask 随机袖**——同 mask 同周频同 Top-16 等权同成本面，唯一差异=每周从当日合格宇宙均匀随机选 16 员（`rng([20550000, k])` 子流律·K=20）；null 带=20 袖 |mean IC| p95 与 beat-rate 分布（提名线 (i) 的分位基准）。**种子带先登记再跑**：`science_gates.SEED_REGISTRY["g2_slot_tail_p1_nulls"]=20550000`（本冻结窗落键·撞带扫描零命中·与 stock 族基 20540000 净距 10000·band [20550000,20550020) disjoint）。
- **腿 (iv) D6 数值面**：§1 清单逐对落盘。
- **腿 (v) 族级聚合（合并尾段设计的判定面载体·冻结）**：每面按 roster `families` 块+`old_roster_correction` 归族标签；族级 verdict=族内提名计数（0 提名=族已答判负真关线；≥1 提名=族进入 stage-2 短名单·独立 §9 冻结后烧）；族级计数落 census JSON `family_verdicts` 块——**合并尾段不稀释逐族裁定**。
- **账本（冻结）**：finalize 步 `science_gates.append_ledger(batch_name="G2_SLOT_TAIL_P1", batch_trials=91, file_name="results/g2_slot_tail_p1/g2_slot_tail_p1_census.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev）。
- **政体分段**：逐面 blend 腿按 510300 t22 3-way proxy 政体标签分段统计（描述披露·census 无门）。

## §4 判据【必填·跑前写死，禁看结果调线】

- **本批=census 面：零注册/零判决判据**（exploration 标注一切输出；无 paper 资格、无入册宣称）。
- **提命名线（stage-2 短名单规则·冻结·与 old/stock 族同文）**：面被提名 stage-2 当且仅当**全部三条**——①`|mean fwd-5d IC| > null 20 袖 |mean IC| 的 p95`；②**x2 成本面**全窗 blend 收益 > 同窗 EW48 被动；③x2 面 rolling-126td beat-rate ≥ 0.60；且不触 §0.5 BAN-01/02 并族规则（price_banned 面测量照跑提名禁入）、不触 §1 D6 vs 在册成员 ≥0.7 并族面。提命名≠注册≠纸盘资格——stage-2 判面须独立 §9 冻结后按 `science_gates.g1_prime_v2/g2_registration_v2` 共享库全判据走（判线禁手抄·缺输入=诚实拒收）。
- **族级裁定线（§3 腿 v 载体）**：族内 0 提名=族已答（O-1901 family-answered rule）判负真关线禁翻案禁重烧；族内 ≥1 提名=该族不关线、提名面进 stage-2 短名单待独立冻结。old 修正腿（old_047/old_067）单独归族裁定：两面 0 提名=old 族全覆盖收口确认（41+2）；任一面过三条件=新提名面首测入短名单（非 old 族判负翻案——该面从未在已测集内）。
- **硬界设计三件套【D-20260925-01①】**：本批无数据腐坏检测类判线（census 测量面）·max 硬界 N/A；极端日先验入 §5(c)。

## §5 跑前预测【必填·写死于跑前，跑后对账】

- (a) **存活稀疏**：提命名面 ≤2/71（同面板同机制先验=old 族 0/41〔r641·IC 层弱富集存在 18/41 过线但 blend 翻译层全灭〕+stock 族 0/14〔r643·IC 层 2/14〕两主力族同谳=x2 翻译层结构性判负先验最强；尾段六族同引擎同面板同消费面，预期同构；若 ≥6 面过线=先查未来函数（vendor 算子 delay/shift 语义与 cutoff 截断面）再信富集）。
- (b) **族间结构差**：better 族量价交互面占比 17/19（六族最高），add 族 12/24、best 族 5/13（含 1 banned）、extra 族 3/7、original 族 0/4（纯价格结构族·IC 先验近 stock 族 price_other 面）、change 族 0/2——量价交互占比高的族 IC 层富集概率高于纯价格结构族（old 族 31/41 量价面 18/41 过线先验），但 x2 翻译层预期全灭同构（周频 Top-16 换手成本拖累 > 信号毛益·两族已证）；**两主力族同窗实证先验（r641/r643）**：机制先验不是放弃理由·判负真关线·负结果如实入 §7；族级回答=泊位收口不重烧。
- (c) **极端日先验**：2024-09-30/10-08 级单日 ±8-10%（涨停簇日·mask 无涨跌停价列=不 mask 涨停日·如实披露）＋2020-02-03 疫情首日；blend 周频腿在簇日有集中换仓暴露（描述披露非判据）。
- (d) **null 带（两族实测校准后带）**：|mean IC| p95 预期 0.008-0.02（old 族实测 0.01153·stock 族实测 0.009649·indicator-null 周频有效样本≈345 周→se≈0.008 同阶）；null beat-rate 均值预期 **0.00-0.10**（old 族实测 0.0025·stock 族实测 0.0117·随机周频重选袖周换手 ~2/3 仓位→x2 成本拖累 ~13-17%/年 vs 零成本 EW48 B&H=恒输非半输·成本不对称面 r641 已实证入册）。若 null p95 ≥0.10=随机机制异常先查袖构造。
- (e) **批内聚类**：71 面袖收益逐对 |corr|≥0.7 预期 ≥1200 对（2485 对中·同源端口族强聚先验=old 族 626/820=76%·stock 族 84/91=92%·尾段六族同引擎血缘预期同阶）；vs 在册六员预期全对 <0.7（ETF 周频袖 vs 在册月频/日频策略族低重合——以实测为准）。

## §6 产物

- runner=`scripts/g2_slot_tail_p1.py`（**待建·冻结后**；结构=scripts/g2_slot_stock_p1.py 同构适配：tail 六前缀+old 修正面 roster 源/新种子带 20550000/新产物目录/面计数门 71+族级聚合腿 v/classify_ban 前缀过滤拓宽·selftest 子命令=roster sha 恒等+cutoff 截断+mask 门+种子 disjoint+确定性双跑字节恒等+F1 面计数+族级聚合断言）；
- probe=`results/_r644bma_slot_tail_roster_probe.py`（已建已跑·**PASS**·事实件·r644 冻结窗）＋裁定辅助件 results/_r644bma_vendor_adjudication.py/_r644bma_ban_preread.py（冻结窗事实件）；
- results：`results/g2_slot_tail_p1/g2_slot_tail_p1_census.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+gates 块+family_verdicts 块）＋d6_numeric.json＋IC 逐面 CSV；
- 本文件 §7/§8 回填；轮报告回执。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

> **跑后回填（2026-10-03 bm-a r644·单次烧批窗）**：runner=scripts/g2_slot_tail_p1.py（selftest 7/7 PASS 8.6s→census run 22.8s·预算 300s 帽内·门 10/10 PASS）；产物=results/g2_slot_tail_p1/{g2_slot_tail_p1_census.json, d6_numeric.json, ic_by_face.csv, ic_daily.csv}；账本 append 91 行（batch_trials=91·total 622431→622522）。

- **族级判负·0/71 提名 stage-2**（exploration 标注·零注册零纸盘资格）——三条件全过者 0 面；BAN 机械分类=38 量价交互+32 price_other+1 price_banned（best_011·与 §0.5 冻结机械预读 38/32/1 逐位恒等）。
- **IC 层（腿 i）**：71 面 ic5_mean ∈ [−0.000007, +0.027517]（绝对值域）；过 cond1（|IC|>null p95=0.010833）者 **27 面**（add 11·best 6·better 4·extra 2·original 0·change 0·old 修正 2·其余归 add/better/best 混合——明细件 ic_by_face.csv）——IC 层富集显著强于 stock 族（2/14）近 old 族（18/41）·前五=add_011（−0.027538）/add_029（+0.027517）/add_017（+0.02491）/best_015（−0.023045）/better_006（+0.021254）；**old 修正腿双面过线**（old_067 +0.019509 过 p95·old_047 亦在册）——roster 修正腿有科学实质（假降级若未纠正=该信号面从未被测量）。
- **blend 翻译层（腿 ii·x2=26.082bp/边）**：**0/71 全灭**——cond2（x2 全窗>EW48）0 面·cond3（beat≥0.60）0 面（最高 beat 0.45）；x2 年化 ∈ [−0.149, +0.0701] vs 同窗 EW48 被动 +0.431289——与 old 族（0/41·r641）/stock 族（0/14·r643）**第三次族级同构实证**：IC 富集存在、成本面翻译层全灭（周频 Top-16 轮换换手成本拖累 > 信号毛益）。
- **null 带（腿 iii）**：20 袖 |mean IC| p95=**0.010833**（预测带 0.008-0.02 内 ✓·old 0.01153/stock 0.009649 同阶）；null x2 beat-rate 均值 **0.0192**（预测 0.00-0.10 内 ✓）；种子带 20550000 rng([seed,k]) 子流律无撞带。
- **D6 数值面（腿 iv）**：vs 在册六员逐对 max|corr| ∈ [0.280, 0.4333] 全 71 面 <0.7=**零并族面**（预测「全对 <0.7」✓）；批内 71×70/2=2485 对中 **1305 对 |corr|≥0.7**（预测 ≥1200 ✓·52.5% 同源端口族聚·族去重清单落 d6_numeric.json 备档零消费）。
- **族级聚合（腿 v·family_verdicts 块）**：add 24/0·better 19/0·best 13/0·extra 7/0·original 4/0·change 2/0·old_roster_correction 2/0——**七族全部 family-answered-negative**（O-1901·判负真关线·禁翻案禁重烧）；failed_faces=0。

## §8 批后复盘【必填·s7-T】【跑前必须为空】

> **跑后回填（2026-10-03 bm-a r644）**：§5 跑前预测逐条对账——**(a) 存活稀疏 ✓**（0/71 ≤ 预测 ≤2/71；富集本就稀疏且翻译层全灭与先验一致·无未来函数疑点触发）；**(b) 族间结构差 ✓ 方向命中**（IC 层 27/71 过线=富集显著·量价占比高的 add/better/best 族贡献主力；x2 翻译层 0/71 全灭=old/stock 后第三次同构实证：**vendor 引擎横截面量价/价格结构面在 core48 ETF 周频 blend 消费面的 x2 翻译层结构性判负已是三族级证据**——IC 信号存在但周频 Top-16 换手成本拖累 > 信号毛益）；**(c) 极端日**：簇日集中换仓暴露如实披露未入判线（regime 分段落 JSON）；**(d) null 带 ✓ 全落预测区间**（p95 0.010833∈[0.008,0.02]·beat 0.0192∈[0,0.10]·无随机机制异常）；**(e) 批内聚类 ✓**（1305/2485 对 ≥0.7 ≥ 预测 1200·D6 vs 在册全 <0.7 双向命中）。
>
> **族级裁定**：尾段六族+old 修正腿全部收口——**G2_OVERLAP_CENSUS_P2 126 NEW-FACE 泊位全覆盖完成且全链判负**（old 0/41 + stock 0/14 + tail 0/71 = 0/126 提名·合并尾段设计一次问完六族=决策正确性实证：若逐族分泊×6 将用 6 轮重问同一结构性死亡层）；负结果如实入负结果台账不粉饰。**链级科学遗产（描述面·非判据）**：全链 IC 层富集面 47/126（old 18+stock 2+tail 27）过各批 null p95——该清单已落各批 ic_by_face.csv，任何未来「低成本翻译层变体」（如低换手翻译口径）=新翻译口径新预注册（非本链翻案·判负线不受影响·须独立 D6/门禁全链走）；stage-2 短名单=空（零提名=零冻结面）。**方法学副产物（已入方法论资产卡 E22）**：r639 词元可导出规则假阳性族（eps=数值 epsilon 等 17 面）—roster 判定正典改为 vendor 实现级 panel-attr 扫描+合成面板 fail-closed 冒烟双证。
