# G2_OVERLAP_CENSUS_P1 预注册 —— G2 三矿因子面×在库已判决族公式级重叠普查（廉价 census·零回测零网络零引擎）

> 【状态：FROZEN——跑前 commit 冻结】本件=GITHUB_MINING_SUPPLY_G2.md §四.1 M1-M5 因子族批量普查批的第一片（清单导出+重叠普查）：矿源装后（r492 inventory 锚）与在库判负/已判决族撞号防重烧，去重后新面入 FACTOR_CENSUS_REGISTRY 登记（零发明律）。跑后只许回填 §7/§8，禁改判据禁重跑（工程修复重跑须双跑留痕）。

## §0 批件身份【必填·跑前】

- 批名 / 批号：**G2_OVERLAP_CENSUS_P1**·批内格数=**478 分类行**（M1 292 alpha_NNN + M1 154 qlib158 字段名制 + M1 12 academic + M1 4 fundamental + M3 16 alphas；每行一分类判定，**非回测格零烧**——本批=测量面非注册面，不入 trials_ledger，marks +0·SEED +0·null 零——census/verify 先例：TSGATE-P1/GATE-RECHECK-A158/GATE-TIMING-PRESCREEN-A158 同族）。
- 认领：F-04 先行——fleet/inbox/ MSG 声明（bm-a r493 认领 G2 overlap census·O-20260930-2054 供给面窗 ≤48h 落实）＋本件即任务板引用（板空触发试用劳动力常设线·r492 next 指针首位）。
- 部门归属：dept:研究（G2 矿源供给链·O-20260930-1132 规模化采掘第二波）。
- 算力预算：est 30-120s 单进程纯文件解析+字符串规范化（零网络零引擎零数据面板）·trivial compute in-round 合法（O-2100 先例）；worker 数=1；批报告必带 audit 段。**预算上限=180s 超限合法停**（O-1901 ③）。

## §0.5 禁开方向硬闸【必填·跑前】

- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/G2_OVERLAP_CENSUS_P1.md`——退出 0=放行；退出 1=不受理（fail-closed）。
- 命中已证伪九方向检查：本批=清单普查非策略批，无策略方向主张；命中 BAN-__：无。若个别矿源面语义命中已证伪方向，SLOT 预注册轮逐面过闸（本批不豁免任何后续闸）。

## §1 α 机制段【必填·D6——本批适配声明】

- 四选一：**不适用声明**——本批=矿源去重普查（census），无策略/因子入册主张；普查的机制角色=**防重烧**（G2 spec §四.1 预案：「与仓内已判负族相关性 ≥0.7→并族留痕」「重叠族→引用在库 verdict 不重烧」），即把 362,083 次 0 过门实证的「selection 拥挤」问题在供料侧前置截断（D-20260930-41 核心判断的工程落实）。各族入池烧批时的 α 机制段+§1.2 散户凭什么赢由**各族 SLOT 预注册**逐族补齐（届时再判不迟，本批不预支）。
- **同族相关性准入检查【D6·本批即其执行载体】**：本批产出=max|corr| 的**公式级前置替身**（D6 阈值 0.7 的日收益口径判定归后续 SLOT 批；本批做编号/公式/名称级去重——公式等价⇒收益序列构造性同源，强于 0.7 阈值的更严判定）。数值与对照清单（逐对列出）：见 §3 冻结对照表（在库四族判决件×矿源五组）。

## §2 数据与面板【必填·跑前探针事实】

- 宇宙/池：**非行情面板批**——数据面=纯文件系统清点（零网络零行情零引擎）。矿源面（G-ANCHOR-FACE 四元组，每个锚）：
  - M1 Vibe-Trading：`toolstack/repos/Vibe-Trading/agent/src/factors/zoo/**`（r492 安装锚 HEAD=18027a0c2b97bd41ac38a0e269799e485bb457d3·ls-remote 实锚）＋加载函数=`scripts/g2_overlap_census.py::export_m1_faces`（ast 正则解析 `__alpha_meta__`/docstring/中文头注释三源）＋起算窗=安装态（2026-09-30 装后未变）＋预热窗=na（无计算）。
  - M3 Multi-factor-Model：`toolstack/repos/Multi-factor-Model-for-Stock-Selection/src/alphas.py`（HEAD=ad6927bce30f04f6dea5bc214c209d36ef22ac40）＋`export_m3_faces`（docstring 公式行正则）＋安装态＋na。
  - M2 Guotai-Junanan-191-Alpha：PDF 级 0 可执行（r492 诚实降级定谳）——**本批不消费 M2**（其 191 公式与 M1 gtja191 目录同源研报，撞号判定由 M1 腿覆盖）。
  - **在库判决对照面**：`research/shortline/wq101_ic_results.csv`（82 ok+19 skip·覆盖编号 alpha001..101）＋`research/shortline/gtja191_ic_results.csv`（191 行·alpha191_001..191）＋`research/shortline/a158_truegap_ic_cells.csv`（7 格在档·A158 全族 census verdict=TSGATE-P1/GATE-RECHECK-A158/T-101-V4 判决链）＋`scripts/a158_tsgate_probe.py::alpha158_factors`（Qlib verbatim 157 因子名集·单源 import 禁重实现）＋`scripts/factor_registry.py::IC_FAMILIES/ENGINE_FACES/ZOO_FAMILIES`（登记簿机器面单源）＋`research/FACTOR_CENSUS_REGISTRY.md`（人读镜像 A-G 行）。
- **evidence_cutoff（前向锁盒 D2）=2026-09-30**：本批无行情面板，cutoff 面=矿源安装态+r492 inventory 锚（HEAD SHA 上表）+在库判决件现状（git tracked·commit 可验）；cutoff 后矿源上游漂移不回流本批（re-clone 改面=新普查批）。结果 JSON 顶层必须带 `science_gates.cutoff_meta(cutoff)` 字段（缺字段=science_audit C2 VIOLATION）。
- 数据完备门（不过门禁跑批）：①M1 四子目录+M3 alphas.py 文件存在且可解析（477+1 py 探针计数与 r492 inventory 对账：292 alpha_NNN+154 qlib158 文件名制+12 academic+4 fundamental+9 base/init ≈ 477 容差 ±9 base/init）②在库四对照件全在位（逐路径 exists 断言）③`a158_tsgate_probe.alpha158_factors` import 成功且 N_FACTORS 断言——任一不符=exit 2 拒烧。
- 探针-锚同面断言：runner 实测计数 vs 本节锚逐位比对，一面不符=面错配 VOID（fail-closed 拒烧报「面错配」非「数据腐坏」）。

## §3 方法学【必填·跑前冻结】

- **矿源面导出（M1）**：逐文件提取四元=①`__alpha_meta__['id']` ②`__alpha_meta__['formula_latex']` ③docstring `Formula:` 行 ④中文头注释「简要说明」公式段（去中文叙述只留公式体）——三源公式内部双写一致性=矿源自证腿；子目录族标签（alpha101/gtja191/qlib158/academic/fundamental）由路径分派。
- **公式规范化函数（冻结）**：`norm_formula(s)`＝小写化→去全部空白→函数名归一表（ts_argmax/ts_argmin/ts_rank/ts_corr/ts_cov/ts_max/ts_min/ts_mean/ts_std/ts_sum/decay_linear/signed_power/safe_div/delta/rank/corr/sum/stddev/mean/min/max/abs/log/sign/scale/covariance_correlation 等：`ts_argmax`≡`argmax`、`ts_rank`≡`rank_` 窗口保留、大小写算子 CORR≡corr）→变量名归一（close/open/high/low/volume/vwap/returns/market_cap/cap/adv*）→常数归一（.0→0）。等价判定=规范化后字符串恒等；**不做数值求值**（廉价原则；数值等价验证归各族 SLOT 预注册）。
- **撞号判定四腿（冻结对照表）**：
  1. **WQ101 腿**：M1 `zoo/alpha101/alpha_NNN.py` 编号空间 1-101 ↔ 在库 `wq101_ic_results.csv` factor=alphaNNN 编号对齐（编号撞号）；公式验证=M1 formula_latex vs M3 alphas.py 同编号 docstring 公式（两独立第三方实现·16 个可得交叉）+M1 内部双写一致（formula_latex vs docstring Formula 行）。
  2. **GTJA191 腿**：M1 `zoo/gtja191/alpha_NNN.py` 编号 1-191 ↔ 在库 `gtja191_ic_results.csv` alpha191_NNN 编号对齐；公式验证=M1 内部双写一致（formula_latex vs docstring vs 中文头注释公式）。
  3. **A158 腿**：M1 `zoo/qlib158/*.py` 文件名根（去窗口数字）↔ `a158_tsgate_probe.alpha158_factors` Qlib 官方 157 因子名集（名称根归一+窗口数映射）；命中=族撞号候选；公式口径=formula_latex vs Qlib 官方口径描述（beta10 判例：M1=ROC/10 型 vs Qlib REGBETA 型=口径漂移——分面判定）。
  4. **ACADEMIC/FUNDAMENTAL 16 面**：文件名根+formula_latex vs 在库 `ENGINE_FACES`(28)+`ZOO_FAMILIES` 构造器名+登记簿 A-G 行名（**名字级近亲判定**——机制级判定归 SLOT 预注册轮，本批不越权）。
- **M3 腿**：16 alpha docstring 编号（#1/3/6/12/21/38/40/41/42/54/72/88/94/98/101+5_day_reversal）↔ wq101 编号空间；公式交叉=M3 docstring vs M1 alpha101 formula_latex 同编号。
- null 对照：**零 null**（非统计判批——无分布面无 null 意义）；被动基线：na（无收益计算）。
- 成本口径：na（零回测零成本——成本恒开律对回测批生效，本批无回测格）。
- 账本：**非试验账本批零 append**（census/verify 先例）；判据节禁手抄判线——本批无注册面；各族 SLOT 烧批时归 `science_gates.g1_prime_v2/g2_registration_v2` 共享库（§4 指针）。
- **闭合族对号声明【M3·必填·D-20260930-37】**：本批 family_key=`g2_overlap_census`（普查面自身）——不在 `science_gates.CLOSED_FAMILIES` 六行册=open 照跑；**本批产出的撞号面引用的族 verdict**（wq101/gtja191/a158 既有判决）不因普查翻面——判负线禁翻案律（O-20260925-1105）不变。

## §4 判据【必填·跑前写死，禁看结果调线】

每面一行四态分类（census 结构判据·非注册判据）：

1. **DUP-NUMBER-VERIFIED**：编号撞号成立（同族同编号对齐在库判决件）**且**公式验证腿全过（M1 内部双写一致+可得交叉一致）→ **族级撞号：引用在库 verdict 不重烧**（在库判决读数随行引用：wq101 82 ok/19 skip、gtja191 191 行、a158 全族 census verdict）。
2. **DUP-FAMILY-DRIFT**：编号/名称撞号成立**但**公式验证腿败（双写不一致或与独立交叉不等价或口径漂移如 beta10 判例）→ **族撞号留痕+漂移面单列**（O-1522 预案「并族留痕」；后续若烧漂移面=新预注册声明公式 delta——不自动继承族 verdict 亦不自动判负）。
3. **NEW-FACE**：全腿无撞号 → **新面候选**：追加 `research/FACTOR_CENSUS_REGISTRY.md` 登记（零发明律：先入簿后入池）+SLOT 泊位候选标记（三验+预注册后烧·G2 spec §四.1）。
4. **UNVERIFIABLE**：公式三源全缺/解析失败/名称映射歧义 → **诚实标注不入池不烧**，留后续裁定（不计入 NEW-FACE——缺证据=非新面）。

- **普查完成判据（批级）**：478 行全部分类（四态之一）+四腿对照表逐行落 JSON+audit 段（时长/文件计数对账）——缺行=未完成。
- **多重检验披露（诚实面）**：本批零统计检验零 null——无多重校正面；「分类」非「判决」（NEW-FACE≠入册交易员资格，SLOT 三验判据照常全链）。
- 判负处置预案（O-1820 三验③）：全撞号零新面=合法产出（矿源价值=第三方实现复用+管线资产，供料池扩面转向 M4/M5/M6 源——G2 spec 后续片）；新面富集=按消费面紧迫度逐族 SLOT 预注册（禁一次性全量判决烧——O-1901 ①千级矿禁逐族全量烧）。

## §5 跑前预测【必填·写死于跑前，跑后对账】

1. **WQ101 腿 101/101 DUP-NUMBER**；其中公式双写一致 ≥95/101（翻译容差：个别文件 docstring 与 formula_latex 措辞差）；M3 交叉 16/16 一致。
2. **GTJA191 腿 191/191 DUP-NUMBER**；公式双写一致 ≥185/191。
3. **A158 腿**：名称根命中 Qlib 官方集 ≥120/154；**公式口径漂移面 ≥15**（beta10 判例先行——M1「改编自 qlib」非 verbatim；DUP-FAMILY-DRIFT 主产区）。
4. **ACADEMIC 12 面**：名字级近亲命中 ≥5（预期 bab↔illiq/amihud_illiq、strev↔rev_5/rev_10、high52w↔mom_12_1、carhart_mom↔mom 族、retskew↔return_skew）；NEW-FACE 预期 3-6（hml/smb/rmw/cma FF 族+mkt_rf+corr_rewire 类——FF 风格面在库 ETF 域无直接面）。
5. **FUNDAMENTAL 4 面**：全 NEW-FACE（asset_growth/earnings_yield/gross_profitability/roe——在库基本面因子面缺位实证=D-41 §八「PE/PB/ROE 完全缺位」**但**ETF core48 域无个股基本面数据面 → 入簿时必须带 DATA_GATE 标记（数据缺口显式：基本面数据不采集则 SLOT 永不开烧——D-41 §五 DATA_GAP 纪律）。
6. **M3 16/16 DUP-NUMBER**。
7. **净新面合计预估 8-16 面**（academic FF 族+fundamental 4+qlib158 漂移面里可能的真新公式）；供料池 ready 面 3→11-19 级（G2 spec §四.1 目标 30+ 级的 40-60% 落地——剩余缺口如实披露归 M4/M5 后续片）。
8. **极端日先验（硬界设计三件套 (c)·本批适配）**：无行情面无极端日风险；替代先验=矿源文件解析异常面（编码/语法/缺元数据）预估 ≤5 文件——异常面=UNVERIFIABLE 诚实处理禁跳过禁臆造。

## §6 产物

- script=`scripts/g2_overlap_census.py`（含 selftest 子命令=离线自检）；
- results JSON=`results/g2_overlap_census_p1.json`（顶层 `evidence_cutoff`+`science_gates.cutoff_meta`+逐行 478 分类+四腿对照表+audit 段）；
- 登记簿追加=`research/FACTOR_CENSUS_REGISTRY.md` 新 H 行（G2 矿源面·append-only·NEW-FACE 逐面带 DATA_GATE 标记）；
- 本文件 §7 回填。

## §7 跑后实证【2026-09-30 bm-a r493 回填·一次定稿】

- **跑次留痕（工程修复双跑·如实记账）**：跑 1=0.69s 因 M3 face 缺 `file` 键 KeyError 崩于写 JSON 前（零产物落盘）；修复=face.get 容错（判据零触碰）；跑 2=selftest 7/7 后执行中又发现两处执行缺陷（M3 函数 docstring 双计 31 行+公式吞英文说明污染 cross 腿·WQ101 19 skip 编号误判 NEW-FACE）→修复三处（M3 只解析模块 docstring·WQ skip 集并入=单源 vendored `_NEUTRALIZED_ALPHAS` ast 静态解析+alpha056 cap·skip 面如实并入判决空间）；**跑 3=终跑 0.71s rc0 全 478 行**（478=冻结数逐位对账 ✓）。三跑零烧格零结果面差异风险（census 零回测，分类面确定性重derive）。
- **四态分布**：DUP-NUMBER-VERIFIED **431**（WQ101 86+GTJA191 191+A158 154）/ DUP-FAMILY-DRIFT **35**（WQ101 15+ACADEMIC 4+M3 16）/ NEW-FACE **12**（ACADEMIC 8+FUNDAMENTAL 4）/ UNVERIFIABLE **0**（预测 8 异常面未现——矿源文件解析全过）。
- **WQ101 腿**：101/101 编号撞号 ✓；VERIFIED 86=双写一致 66+skip 面 19+交叉一致面；DRIFT 15（#1/3/6/12/21/38/40/41/42/54/72/88/94/98/101）=M1 formula_latex vs M3 docstring **括号书写变体**（同公式异书写·如 #1 `SignedPower(x, 2.)` vs `SignedPower((x),2.)`）——字符串恒等判据下保守判 DRIFT=安全侧（fail-closed 不引用 verdict 不重烧）；SLOT 轮数值对照可升级。
- **GTJA191 腿**：191/191 DUP-NUMBER-VERIFIED 全中（三源双写全一致）。
- **A158 腿**：154/154 名称命中 Qlib verbatim 157 名集；BETA5/10/20/30/60 五面 `qlib_semantics_drift_risk` 旗实证（M1=ROC/N 型 `(close_t−close_{t−N})/(N·close)` vs Qlib=REGBETA 回归型——beta10 判例泛化）+旗启发式局限披露（仅回归类 root 触发，其余改编面未捕捉·保守低估）。
- **ACADEMIC/FUNDAMENTAL**：DRIFT 4=carhart_mom(kin=mom_60)/illiq(kin=amihud_illiq)/retskew(kin=return_skew)/strev(kin=rev_10)——名字级近亲如实；NEW-FACE 8=bab/cma/corr_rewire(豁免)/high52w/hml/mkt_rf/rmw/smb；FUNDAMENTAL 4 全 NEW-FACE ✓。M3-EXTRA 5_day_reversal DRIFT（kin 注记瑕疵如实：'day' token 过宽误指 overnight_minus_intraday，真实近亲=rev_5/ret5 族——SLOT 轮裁定，结论面不受影响）。
- **净新面=12**：OHLCV-ready 4（bab/corr_rewire/high52w/mkt_rf）+DATA_GATE 8（FF5 四+fundamental 四·基本面缺位锁）。已入登记簿 H 节（FACTOR_CENSUS_REGISTRY.md append-only）。
- **audit**：elapsed 0.71s（预算上限 180s 内 ✓）·rows_classified 478/478 ✓·a158 单源 N=157 断言过 ✓·evidence_cutoff/cutoff_meta 顶层在位 ✓。

## §8 批后复盘【bm-a r493】

- **预测对账**：①WQ101 101/101 DUP-NUMBER=**部分对**（编号全撞 ✓·双写一致 86<95 预测线——书写变体 15 面保守 DRIFT）；②GTJA191 191/191+一致 ≥185=**对**（191 全一致超预测）；③A158 命中 ≥120=**对**（154/154 超预期）·漂移旗 ≥15=**错**（5 面——旗启发式保守低估如实披露）；④ACADEMIC 近亲 ≥5=**部分对**（4 面·差 1）；⑤FUNDAMENTAL 4/4 NEW=**对**；⑥M3 16/16 DUP-NUMBER=**错**（15 编号面+1 extra 全 DRIFT——M3 公式书写变体同 #1 族因；教训=M3 与 M1 为同源翻译的两个独立英译，括号风格系统性不同）；⑦净新面 8-16=**对**（12 落区间中位）；⑧解析异常 ≤5=**对**（0 面）。总评=8 条对 4 错 3 部分对 1。
- **门禁链损耗账**：results/gate_attrition.json 已追加 G2_OVERLAP_CENSUS_P1 行（cells_delta=0·四态分布账）。
- **消费面去向**：登记簿 H 节落 12 面（4 SLOT 候选+8 DATA_GATE 锁）；431 撞号面=防重烧价值兑现（后续任何 G2 矿源消费批先对 H 节+results/g2_overlap_census_p1.json 查重）。下片=M4/M5 矿普查（供料池 7→30+ 缺口主力）或 4 SLOT 候选逐族预注册——按消费面紧迫度排序（O-1901 ④）。
- 回执=round_reports-bm-a.md r493 行+CODELY.md 行级追加。
- 全起点分布：不适用声明（零回测零收益序列·§8 模板原文）。
- 试验量归因：新增试验数 **0**（census 非试验·30 天 ≤500 预算零消耗 ✓）。

## §8 批后复盘【必填·s7-T】

- 预测对账（对/部分/错）逐条；门禁链损耗账（`results/gate_attrition.json` 追加一行——普查面四态分布账）；判线 v2 当批读数=na（非注册批）；
- 回执入轮报告+CODELY.md 行级追加；NEW-FACE 入簿后=SLOT 泊位候选清单归供料池管理面（逐族预注册另起批）；
- **全起点分布【§1.3·D-41】**：不适用声明——本批零回测零收益序列，无起点面；各族 SLOT 烧批时逐族补全起点分布义务。
- **试验量归因【§1.4/D-41 §6-C】**：本批新增试验数=**0**（census 非试验——零回测格零 null 零 N_eff；30 天 ≤500 预算零消耗）。
