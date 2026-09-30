# G2_OVERLAP_CENSUS_P2 预注册 —— G2 M4/M5 矿因子面×在库已判决族公式级重叠普查（廉价 census 续片·零回测零网络零引擎）

> 【状态：FROZEN——跑前 commit 冻结】本件=GITHUB_MINING_SUPPLY_G2.md §四.1 M1-M5 因子族普查批的**第二片**（P1=478 面 r493 已烧收口：431 DUP/35 DRIFT/12 NEW-FACE；本片=M4/M5 两矿）。矿源 r494 装后（anchors 见 §2）与在库判负/已判决族撞号防重烧，去重后新面入 FACTOR_CENSUS_REGISTRY 登记（零发明律）。跑后只许回填 §7/§8，禁改判据禁重跑（工程修复重跑须双跑留痕）。

## §0 批件身份【必填·跑前】

- 批名 / 批号：**G2_OVERLAP_CENSUS_P2**·批内格数=**237 分类行**（M4 213 注册装饰面：add_001-030〔30〕+alpha_001-101 子集〔9〕+best_001-021〔21〕+better_001-028〔28〕+change_001-005〔5〕+extra_001-014〔14〕+market 名键〔6〕+old_027-076〔50〕+original_001-028〔28〕+stock_001-022〔22〕＋ M5 24 面：alpha_001..alpha_025 去 alpha_010〔24〕·DEMO_FACTORS 元组==方法集断言已过）。每行一分类判定，**非回测格零烧**——本批=测量面非注册面，不入 trials_ledger，marks +0·SEED +0·null 零（census/verify 先例：TSGATE-P1/GATE-RECHECK-A158/G2_OVERLAP_CENSUS_P1 同族）。
- 认领：F-04 先行——fleet/inbox/ MSG-20260930-2330 bm-a 声明 P2 认领＋本件即任务板引用（板空触发试用劳动力常设线·r493 next 指针首位=M4/M5 普查续片·r492/493 供给面窗 ≤48h 延续）。
- 部门归属：dept:研究（G2 矿源供给链·O-20260930-1132 规模化采掘第二波·O-20260930-2054 供给面）。
- 算力预算：est 30-120s 单进程纯文件解析+字符串规范化（零网络零引擎零数据面板）·trivial compute in-round 合法（O-2100 先例）；worker 数=1；批报告必带 audit 段。**预算上限=180s 超限合法停**（O-1901 ③）。
- **与 P1 的关系（冻结声明）**：P1 判据与其 478 行分类**不因本批翻面**（判负线禁翻案律 O-20260925-1105）；P1 的 35 DRIFT 面在 P1 账面永为 DRIFT（fail-closed）；本片引入的 norm_v2 书写变体预筛**只用于本片 M4/M5 腿自身的等价判定**，P1 漂移面的升级路径仍=SLOT 轮数值对照（P1 §7 原文）。

## §0.5 禁开方向硬闸【必填·跑前】

- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/G2_OVERLAP_CENSUS_P2.md`——退出 0=放行；退出 1=不受理（fail-closed）。
- 命中已证伪九方向检查：本批=清单普查非策略批，无策略方向主张；命中 BAN-__：无。矿源面若语义命中已证伪方向，SLOT 预注册轮逐面过闸（本批不豁免任何后续闸）。

## §1 α 机制段【必填·D6——本批适配声明】

- 四选一：**不适用声明**——本批=矿源去重普查（census），无策略/因子入册主张；普查机制角色=**防重烧**（G2 spec §四.1：「与在库已判负族相关性 ≥0.7→并族留痕」「重叠族→引用在库 verdict 不重烧」）。各族入池烧批时的 α 机制段+§1.2 散户凭什么赢由**各族 SLOT 预注册**逐族补齐（届时再判不迟，本批不预支）。
- **同族相关性准入检查【D6·本批即其执行载体】**：公式级前置替身（编号/公式/名称级去重——公式等价⇒收益序列构造性同源，强于 0.7 阈值判定；数值 0.7 口径归后续 SLOT 批）。对照清单见 §3。

## §2 数据与面板【必填·跑前探针事实】

- 宇宙/池：**非行情面板批**——数据面=纯文件系统清点（零网络零行情零引擎）。矿源面（r494 安装锚·ls-remote 实锚+克隆后 HEAD 逐字节一致已验）：
  - M4 initial-d/ml-quant-trading：`toolstack/repos/ml-quant-trading/src/mlquant/features/_factors_*.py`（HEAD=a770825f841504e41581f057b4d94160e6a50c2e·depth-1）＋加载函数=P2 runner `export_m4_faces`（ast 解析 `@register_*` 装饰器面：函数名+docstring 公式行〔WQ 语法单源〕）＋起算窗=安装态（2026-09-30 装后未变）＋预热窗=na（无计算）。**宣称 213 因子 vs 注册面实测 213=逐位一致**（r494 探针 results/_r494bma_face_freeze.py 输出冻结）——M4=代码级诚实矿（对照 M2/M3/M5 纸宇宙宣称降级先例）。
  - M5 JunQHuang/Machine_Learning-Quant-Stock-Selection：`toolstack/repos/Machine_Learning-Quant-Stock-Selection/multifactor_demo/factors.py`（HEAD=b3e3712935deb909d143334942edb2ca438c3a26·depth-1）＋`export_m5_faces`（`AlphaFactorEngine.alpha_NNN` 方法体代码面+DEMO_FACTORS 断言）＋安装态＋na。**宣称 120 vs 安装实测 24=诚实降级**（README 自述「public factor set is intentionally generic…without exposing any production factor selection」——demo 面如实）。
  - **在库判决对照面（P1 同一单源集·零改动）**：`research/shortline/wq101_ic_results.csv`（82 ok+19 skip）＋`research/shortline/gtja191_ic_results.csv`（191 行）＋`scripts/a158_tsgate_probe.py::alpha158_factors`（Qlib verbatim 157 名集）＋`scripts/factor_registry.py::IC_FAMILIES/ENGINE_FACES/ZOO_FAMILIES`（登记簿机器面单源）＋`research/FACTOR_CENSUS_REGISTRY.md`（A-G+H 行·P1 已入 12 面）＋**P1 产物 `results/g2_overlap_census_p1.json`**（478 行分类=第二对照面：M4/M5 与 M1/M3 同公式互译撞号时引用其在库族 verdict）＋M1 矿源公式面（`toolstack/repos/Vibe-Trading/agent/src/factors/zoo/**`·HEAD 锚同 P1）。
- **evidence_cutoff（前向锁盒 D2）=2026-09-30**：cutoff 面=矿源安装态（上表 HEAD SHA）+在库判决件现状（git tracked 可验）；cutoff 后矿源上游漂移不回流本批（re-clone 改面=新普查批）。结果 JSON 顶层必须带 `evidence_cutoff`+`science_gates.cutoff_meta` 字段（缺字段=science_audit C2 VIOLATION）。
- 数据完备门（不过门禁跑批）：①M4 features 目录 `@register_*` 实测=213 逐位（≠213=面错配 VOID 拒烧）②M5 DEMO_FACTORS 元组==alpha_NNN 方法集断言且 N=24（≠24 拒烧）③在库对照件全在位（逐路径 exists）④`a158_tsgate_probe.alpha158_factors` import 成功且 N_FACTORS 断言——任一不符=exit 2 拒烧。
- 探针-锚同面断言：runner 实测计数 vs 本节锚逐位比对，一面不符=面错配 VOID（fail-closed 报「面错配」非「数据腐坏」）。

## §3 方法学【必填·跑前冻结】

- **矿源面导出（M4）**：逐 `@register_*("name")` 装饰函数提取四元=①注册名 ②docstring 公式行（WQ 语法·单源——M4 无 formula_latex 双写，**单源腿如实**：矿源自证腿=na，等价判定完全依赖与在库/对照源的公式恒等）③子族标签（add/best/better/change/extra/market/old/original/stock/alpha101 由注册名前缀分派）④文件锚。
- **矿源面导出（M5）**：逐 `alpha_NNN` 方法提取二元=①编号 NNN（001-025 去 010）②方法体代码面（纯代码无 docstring 公式——**代码即公式腿**：与 M1 alpha_NNN 实现代码的算子序列结构比对〔算子名+参数序列归一〕；代码-公式跨形态恒等不可证时=诚实降级为编号撞号单证）。
- **公式规范化函数 v2（本片冻结·P1 v1 的超集）**：`norm_formula_v2(s)`＝P1 norm_formula 全部规则（小写化→去空白→函数/变量/常数归一）**＋书写变体预筛（r493 教训入法）**：去冗余括号——仅剥「单原子/单数字包裹层」`(x)`→`x`、`((x))`→`x`、`(2.)`→`2`，**不剥语义括号**（函数实参表/显式优先级结构不动）；预筛后字符串恒等=等价。保守性声明：预筛只降「同公式异书写」的 DRIFT 噪声，不引入数值求值（廉价原则不变）。
- **撞号判定四腿（冻结对照表）**：
  1. **M4-WQ101 腿（9 面）**：alpha_001..101 子集编号 ↔ `wq101_ic_results.csv` 编号空间；公式验证=M4 docstring vs M1 同编号 formula_latex（norm_v2）。
  2. **M4-OLD/GTJA 疑似腿（old_027-076〔50〕+original/add/best/better/change/extra/stock 六族〔~148〕=名键面）**：注册名与在库族名空间零交（old_/add_ 等前缀在库无）——**公式恒等腿为主判**：norm_v2(M4 docstring) vs 在库公式语料全量（M1 WQ101 101 式+M1 GTJA191 191 式+A158 probe 公式面+登记簿 A-H 行公式面）恒等 → **DUP-FORMULA-VERIFIED**（撞号面=公式级同源，引用对应族 verdict 不重烧）；恒等不成立 → 名字级近亲检查（ENGINE_FACES 28+ZOO 构造器名+登记簿行名）→ 命中=DUP-FAMILY-DRIFT（名字近亲·公式异）；双不中=NEW-FACE 候选。
  3. **M4-MARKET 腿（6 面：cs_rank_close 等）**：名键=cs_rank_ 前缀 → 在库 ZOO/ENGINE 名字近亲判定+公式恒等腿同上。
  4. **M5-WQ101 腿（24 面）**：编号 001-025（去 010）⊂ wq101 编号空间 001-101 → **编号撞号成立**；公式验证=M5 方法体算子序列 vs M1 同编号实现（算子名+常数+窗口序列归一比对）；跨形态不可证=**编号撞号单证分类**（DUP-NUMBER·variant 面如实标注 code-face-unverified——分类态四选一内归 DUP-NUMBER-VERIFIED/DRIFT 按算子序列比对结果，不可证=DRIFT 态诚实标 code-face-limit）。
- **skip 集合并入纪律（r493 教训入法）**：在库不可算面（WQ101 19 neutralized skip 面）必须从 vendored 模块 ast 静态单源并入判决空间——漏并=编号误判 NEW-FACE（r493 实弹 19 面假阳性教训）；P2 runner 复用 P1 已并的 skip 集（g2_overlap_census.py 单源），禁重抄。
- null 对照：**零 null**（非统计判批）；被动基线：na（无收益计算）。
- 成本口径：na（零回测零成本）。
- 账本：**非试验账本批零 append**（census/verify 先例）；判据节禁手抄判线——本批无注册面；各族 SLOT 烧批时归 `science_gates.g1_prime_v2/g2_registration_v2` 共享库。
- **闭合族对号声明【M3·必填·D-20260930-37】**：本批 family_key=`g2_overlap_census_p2`——不在 `science_gates.CLOSED_FAMILIES` 六行册=open 照跑；本批撞号面引用的族 verdict（wq101/gtja191/a158 及 P1 分类）不因普查翻面。

## §4 判据【必填·跑前写死，禁看结果调线】

每面一行四态分类（census 结构判据·非注册判据·与 P1 同构）：

1. **DUP-NUMBER-VERIFIED / DUP-FORMULA-VERIFIED**：编号撞号或公式恒等（norm_v2）成立且验证腿过 → **族级撞号：引用在库/P1 verdict 不重烧**（随行引用在库判决读数）。
2. **DUP-FAMILY-DRIFT**：撞号成立但验证腿败（含 M5 code-face 不可证面）→ 族撞号留痕+漂移面单列（后续烧漂移面=新预注册声明 delta）。
3. **NEW-FACE**：全腿无撞号 → 新面候选：追加 `research/FACTOR_CENSUS_REGISTRY.md` H 行（append-only·零发明律）+SLOT 泊位候选标记+DATA_GATE 标记若数据面缺位（M4 market/tensor 系依赖 Panel 面板结构——若依赖 torch/专有数据结构则如实标 DATA_GATE/VENDOR-LOCK）。
4. **UNVERIFIABLE**：公式源缺/解析失败/映射歧义 → 诚实标注不入池不烧。

- **普查完成判据（批级）**：237 行全分类+四腿对照表逐行落 JSON+audit 段（时长/面计数对账）——缺行=未完成。
- **多重检验披露**：零统计检验零 null——「分类」非「判决」（NEW-FACE≠入册资格，SLOT 三验照常）。
- 判负处置预案（O-1820 三验③）：全撞号零新面=合法产出（矿源价值=第三方实现复用+管线资产，转向 M6 策略源普查——G2 spec 后续片）；新面富集=按消费面紧迫度逐族 SLOT 预注册（禁一次性全量判决烧——O-1901 ①）。

## §5 跑前预测【必填·写死于跑前，跑后对账】

1. **M5-WQ101 腿 24/24 编号撞号成立**（24 面 ⊂ 001-101 已判决空间）；其中算子序列与 M1 一致（VERIFIED）预估 **≥20/24**——独立翻译代码风格差（变量名/链式写法）致比对失败面预估 ≤4（DRIFT·code-face-limit 诚实态）；M5 NEW-FACE=**0**（编号空间全撞）。
2. **M4-WQ101 腿 9/9 编号撞号**；docstring vs M1 formula_latex norm_v2 一致 ≥7/9（norm_v2 预筛吸收括号变体——P1 同型 15 DRIFT 面教训）。
3. **M4-OLD 疑似 GTJA 腿**：old_027-076 若为 GTJA191/WQ 再编号——公式恒等命中 ≥30/50；连号 027-076 暗示某矿源子集抽取，恒等腿将定谳其真实族属（预测区间宽=诚实：30-50）。
4. **M4 六名字键族（add/best/better/change/extra/stock ~148 面）**：公式恒等命中（WQ101/GTJA191 语料内）预估 **≥80/148**（再编号复用先例：M4 宣称与注册逐位一致暗示工程化抄录矿）；名字近亲（DRIFT）预估 ≤20；NEW-FACE 预估 **10-30**（better_/stock_ 族可能含原创组合式）。
5. **M4-MARKET 腿 6 面**：cs_rank_* 名字与在库 cs/rank 构造器近亲——DRIFT/NEW-FACE 各半预估（2-4 NEW-FACE）。
6. **净 NEW-FACE 合计预估 12-34 面**；供料池 ready 面 7→19-41 级（G2 spec §四.1 目标 30+ 级**本片大概率达标**——达不达标如实披露）。
7. **解析异常面 ≤8**（M4 单源 docstring 行格式变体+M5 代码面抽取失败）——异常=UNVERIFIABLE 诚实处理禁跳过。
8. **极端日先验（硬界设计三件套 (c)·本批适配）**：无行情面无极端日风险；替代先验=解析异常面（见 7）。

## §6 产物

- script=`scripts/g2_overlap_census.py`（扩展 P2 腿：export_m4_faces/export_m5_faces+norm_v2+四腿；selftest 子命令扩 P2 夹具——离线自检）；
- results JSON=`results/g2_overlap_census_p2.json`（顶层 `evidence_cutoff`+`science_gates.cutoff_meta`+逐行 237 分类+四腿对照表+audit 段）；
- 登记簿追加=`research/FACTOR_CENSUS_REGISTRY.md` H 行（P2 面·append-only·NEW-FACE 逐面带 DATA_GATE/VENDOR-LOCK 标记）；
- 本文件 §7 回填。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（空）

## §8 批后复盘【必填·s7-T】

（空）
