# EXCLUSION-MARGINAL-P1 预注册（排除规则边际值扫描·D-20260930-41 交付件 #3）

> 冻结：2026-09-30 bm-b r475 ｜ 轨道：research/RETAIL_QUANT_TRACK.md §二 #3 ｜ 令源：D-20260930-41（CEO 原话「排除」是机构因仓位要求做不到的动作；第一铁律〔R-配1 亏损股不配〕已实测 alpha 5.63%→14.80%——实测配置不在本仓，本批以本仓冻结配置独立复测边际值，无义务复现该数字，如实披露）
> 效力边界自查：§1.2 禁开面九方向不含本批（本批=令钦定五件事 #3；基线「低量选股」=令原文引用的两条站立结论之一；低价/小市值禁面不触发——本批规则=排除卫生面非信号方向）。

## §0 批件身份

- 批名：EXCLUSION-MARGINAL-P1 ｜ 批号格数：**16 cells**（FULL/NONE/6×LOO/6×AOI/RAND-FULL/RAND-NONE；每格=1 试验计入 N_eff）
- 认领：F-04 先行=本窗 fleet/inbox/ MSG（berth=bm-b，承心跳 r474 宣告）＋任务板引用：RETAIL_QUANT_TRACK §二 #3 行
- 部门归属：dept:研究（供给轨道五件事）
- 算力预算：烧批预估 20-40min（5217 文件×16 格全史月频重算）；>10min=后台化入 runnable_pool 提交（O-2100 执行面分离律）；批报告带 audit 段
- runner：`scripts/exclusion_marginal_scan.py`（probe/selftest 已落地实证本窗；run=引擎腿下片，本窗诚实 rc=2 拒跑零烧）

## §1 α 机制段

- [x] **结构性**（主）＋行为偏差（辅）：排除规则=制度性结构摩擦规避——退市整理/戴帽连续跌停/仙股操纵崩塌段的损失由「无排除约束的被动持有者」付出代价；散户无仓位要求=该维度对机构结构性不可得，对散户可得。
- **散户凭什么赢【§1.2 必填】**：**制度**——机构因指数跟踪/建仓量约束物理上做不到逐股排除（令原文逻辑本体）；本账户独有约束例外三问：①独有约束=无仓位要求 ✓（本问即答案）②本市场未验证=否（引用台账 ⑤2024-01 小微盘踩踏为排除价值的机构侧证据，引用编号 §1.1-⑤）③样本外新数据=否。过三问=自跑合法。
- **同族相关性准入检查**：本批为**测量扫描零注册面**（产物=边际值表，不注册交易员）→ 在册相关性检查=**N/A 声明**（表内格间相关性=报告面非准入面；FULL 格日后若注册=另开预注册再过 D6）。若日后入册：与在册 B 层/股票族算 max|corr| 于彼批冻结。

## §2 数据与面板（探针事实已落 results/exclusion_marginal_scan/probe_facts.json）

- **数据锚面四元组（G-ANCHOR-FACE）**：
  ① `data/astock_daily/per/<code>.csv` ＋ `pandas.read_csv` ＋ 全史（最早 1991-04-03）＋ amt20 min_periods=20、age250 需 250 bars（探针样本三件 sha16 已钉 facts）；
  ② `data/fundamental/eligibility.csv` ＋ `firm.risk.b_layer_filter.load_eligibility` ＋ 快照制（24h 刷新）＋ 静态无预热；
  ③ `data/fundamental/b_layer_mask.csv` ＋ `firm.risk.b_layer_filter.load_mask` ＋ 快照 ＋ 静态无预热。
- **探针-锚同面断言**：runner 引擎腿加载路径与上列逐位比对；一面不相等=面错配 VOID（fail-closed 拒烧，报「面错配」非「数据腐坏」）。
- 探针实证（本窗 19:2x）：panel_files=**5217**；eligibility 0/3/6 前缀=**5229**（收集器口径 universe_n=5228 差 1=eligibility 侧新码漂移候选，烧批门=掩码∩面板交集逐码断言钉死）；mask_total=**5222**（r1_loss 1506/r2_st 27/复合 172）。
- **evidence_cutoff=2026-09-22**（P-5C 绑定，ALLOC-POLICY-SCAN-P1 同锚；面板现 cutoff 2026-09-29→烧批统一截断到 2026-09-22，锁盒 D2：cutoff 后新 bar 禁回流）；结果 JSON 顶层带 `science_gates.cutoff_meta`。
- 数据完备门：烧批前三门=①面板 complete 且 cutoff≥2026-09-22 ②mask all_pass ③eligibility 快照<24h——任一败=拒烧诚实披露。
- **DATA_GAP 显式声明（§五纪律）**：**DATA_GAP#3**（历史逐日 ST 缺失）→ r1/r2 用今日快照套全史=机构已认可保守近似（b_layer_filter 契约自认 caveat，本批沿用并披露）；ST 政体动态代理（封 5% 板滚动判定）**不可算**——qfq 面板无 raw pct_chg/preclose（P4_BATCH2 明禁 qfq 比价判板）→ 该规则不入格、以 r2_st 静态面承载，**非静默跳过**。

## §3 方法学（全冻结·零调参自由）

- **基线策略（低量选股·经典单一参数化）**：每月末交易日信号（年月分组末位）→ 按 **20 日均成交额升序**排名 → 过本格排除集 → 取前 **N=10** 等权（¥1,000,000 初始）→ **次一交易日开盘执行**（T+1 保守代理，O-1132 先例）持有 1 月；停牌入场=跳过（错过诚实）、停牌出场=复牌首日开盘；单标的 10% 等权=全局硬规则 1 合规。
- **排除规则集（6 条·SS2/铁律镜像，格内开关）**：
  | id | 规则 | 口径 |
  |---|---|---|
  | r1_loss | 亏损股不配 | eligibility r1_loss 静态掩码（铁律 R-配1） |
  | r2_st | ST 名单不配 | eligibility r2_st 静态掩码（铁律 R-配2 今日快照近似） |
  | l1_liq5000w | 流动性地板 | 信号日 20 日均成交额 ≥¥5000 万（SS2 原文） |
  | l2_price1y | 价格地板 | 信号日收盘 ≥¥1（SS2 原文） |
  | l3_age250 | 次新排除 | 信号日上市 ≥250 bars（SS2 20-250 窗取严端·经典 1 年律，偏差披露） |
  | l4_active10td | 停牌/僵尸排除 | 信号日前 10 交易日内有 bar（SS2 250td 建时态规则的回放态收紧等价，偏差披露） |
- **格构造（16 cells）**：FULL（全开）/NONE（全关）/6×LOO（每次关 1）/6×AOI（每次只开 1）/RAND-FULL、RAND-NONE（**随机选股 null 基线**=同执行同成本随机等权 10 只——三铁律随机基线律+排除价值×基线类型交互面）。排序面零选择自由：格=规则开关全组合的既定子集（ORDER §5-2 全量公布型例外），禁删格禁加格。
- **null 对照**：RAND 两格=随机 null（seed=science_gates.SEED_REGISTRY 新登记再跑，禁现编）；无被动基线（股票域无单一被动锚，RAND-NONE 即参照）。
- **成本口径（CN-C7·D-20260930-40）**：V2 股票面=`knowledge/rules.py fee_schedule_for`（佣金 ¥5 最低临界/印花税卖边 5bp/过户费双边 0.1bp）+ADV20 三层滑点；**往返 bp=跑前由 `knowledge/cost_spec.py` 派生申报**（探针已接 face；跑前数字钉入批报告禁手抄）；×2 成本压测=描述面全格双跑披露。
- 账本：烧批时 `science_gates.append_ledger("EXCLUSION-MARGINAL-P1", 16, "exclusion_marginal_scan", evidence_cutoff="2026-09-22")`。
- **闭合族对号（M3）**：family_key=`exclusion_marginal_p1`——不在 CLOSED_FAMILIES（引擎腿烧前跑 `closed_family_check` 断言，rejected=拒烧）。
- **M1 t 面**：边际主张（FULL−LOO 差分）无直接 t=以全起点 Δ 分布（16 起点 sign 型证据）承载并如实标注；FULL/NONE 格描述面报 `t_from_sharpe` 派生 t（无门角色=测量批零注册主张，披露非准入）。

## §4 判据（跑前写死·禁看结果调线）

- **M1 边际值主判（逐规则）**：`Δ=ann_ret_net(FULL)−ann_ret_net(LOO−rule)` 三条同时成立=**该规则边际值为正**：
  ① 全期 Δ>0；② 全起点（2007..2022 每年 1 月首个交易日 16 起点）Δ 正份额 ≥0.50（多数起点成立律·令 #1 措辞镜像）；③ 全起点 Δ 中位 >0。
  AOI 面（Δ'=AOI−NONE）同判据独立评定；两面结论可以背离（背离=边际值依赖基线语境，如实披露非异常）。
- **全起点分布【§1.3 必填】**：每格报 ann_ret_net 最好/最坏/p25/中位/p75＋滚动 3/5/10 年窗最差；**只报单一起点=结论无效**。
- 描述面（不替代主判）：Δmaxdd/ΔSharpe/两格成本拖累/换手率/格间重叠持仓占比全披露；RAND 交互面=报告用。
- 无注册门（G1'/G2 不适用=零注册面）；极端日纪律：本批判据为分布界（全起点份额/中位）非裸 max，熔断/踩踏窗内极端回撤在描述面单列披露。

## §5 跑前预测（写死于跑前·跑后对账）

1. **r1_loss 边际正值最大**（令引 5.63→14.80 方向；量级不承诺——卫生规则叠满后边际或小于该引用值）。
2. **l1_liq5000w 在低量基线上边际为负或近零**（排除集直接切除 alpha 源=本扫描核心张力面；若为正=「可交易性溢价」证据，方向反直觉同披露）。
3. l4_active10td 边际为正（2015-2018 停牌潮窗贡献集中）。
4. r2_st 边际为正但量级小于 r1_loss（与 r1/l2 高重叠）。
5. **极端日先验**：2015-06 股灾/2016-01 熔断/2024-01 小微盘踩踏（引用 §1.1-⑤）三窗内 NONE/RAND-NONE 格将现最深回撤（低量+无卫生=踩踏段重灾面）；FULL 格月频换手+地板规则应显著削尾。

## §6 产物

`scripts/exclusion_marginal_scan.py`（run 腿引擎下片）＋ `results/exclusion_marginal_scan/scan.json`（顶层 evidence_cutoff+16 格全指标+per-rule 边际表）＋ `scan_cells.csv` ＋ 本件 §7 回填＋载体件 research/EXCLUSION_MARGINAL.md 边际值表。

## §7 跑后实证（占位·写数字即造假）

（空——烧后一次定稿回填）

## §8 批后复盘

- 预测对账逐条（对/部分/错）＋gate_attrition 追加一行＋试验量归因：**本批 +16**（318/500 累计·单批 <100 无归因义务仍一句：16 格=6 规则×2 测量面+2 基线+2 随机 null=最小完备边际读数集）。
- 回执入轮报告＋CODELY 行级；无新注册面→无 SIGNAL_BUILDERS 接线义务。
- 下片精确续作点：runner run 腿引擎（月频重算+停牌出场+V2 成本+RAND seeds 登记）→selftest 扩腿→runnable_pool 入池→烧批→§7 回填。
