# INNOVATION_QUOTA_W1_PREREG · 创新配额槽-1：逆回购日历期限摆动族（REPO-CALENDAR-P1）judged 判决批

> 状态：**跑前冻结**（2026-09-28 r180 bm-c · 与 F-04 MSG-20260928-2035＋SEED_REGISTRY 登记同 commit）；跑后只许回填 §7 占位节，禁改判据禁重跑。
> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节+G-ANCHOR-FACE 四元组 O-20260928-1712 律）；令源=O-20260928-1614 §一.4 填充阶梯④创新配额（每闲置窗≥1 新假设族）+O-1721 借力律+RESEARCH_MECHANISM 常态线+O-20260926-2325 域解禁令（逆回购=明列解禁域+T-88 现金腿数据面）；票=T-2026-09-28-107 §4(d)+fill_ladder_catalog `INNOVATION-QUOTA-SLOT-1` 条目（lane_owner=null·enqueue_gates=prereg_frozen+runner_exists）。
> **族选防重核（r180 实读）**：①CN_KLINE_PATTERN_P1 四形态族=已判负族禁重开（verdict judged-negative 2026-09-27）②多 K 线形态复合轴=同族面不另立 ③LeBaron 波动率条件化=W4 VOL 门 461 格已判（r396 bm-b finalize·0 过 G2）语义撞=弃 ④repo 面=REPO_PANEL spec 明文「纯数据采集道——零回测零引擎」+research/ 全档零 REPO prereg=**仓内未试面实证**；数据面板 T-88 已建（11 期限·完整性行序守卫/overlap 校验/利率带 0<close<200 内建=DOMAIN_AUDIT 数据面已过），五步制（外源调研→数据审计→prereg→回测→纸盘）本批=第 3-4 步。
> 外源锚披露（借力律·宣称≠验证）：本轮无直接外源日历效应专文在册（jisilu digest 面=跨境 ETF 主面·逆回购仅侧写）——**外源直接锚=弱如实**；主证=仓内探针事实（§2 引用件）+结构性机制论证（§1）；CN 货币市场「月末季末节前资金面紧张」=常识面不作证据面。
> 统摄律：firm/RANDOM_LARGE_SAMPLE_LAW v1.0 + research/BACKTEST_SCIENCE.md v2（判据唯一权威）+ BACKTEST_PLAN.md 三铁律 + research/COMPUTE_AUDIT.md 批件纪律。

## §0 批件身份。【跑前。】

- 批名/批号：**REPO-CALENDAR-P1**（创新配额槽-1·逆回购日历期限摆动族）。N_eff = **4 judged cells + 2000 null draws = 2004**（CN_KLINE 同口径计数律；passive 基线=披露列不计 N）。
- 认领：F-04 先行已落（`fleet/inbox/MSG-20260928-2035-bmc-all-supply-prereg-freeze.md`）；任务引用=T-2026-09-28-107 §4(d)+fill_ladder_catalog tranche-1(d)。
- 部门归属：dept:策略（现金腿摆动族判决面）+ dept:数据（repo 面板消费面）joint。
- 算力预算：向量化日历引擎 3,735 日 ×4 格+2000 nulls+1000 虚拟起点+100 分窗 = 分钟级池批；>5min 入池（O-2100 执行面分离）·checkpoint 幂等。

## §1 α 机制段。【四选一+论证·D6 门槛。】

- [x] **结构性**：交易所回购市场双结构摩擦——①**期限溢价**：常态日借款方为锁定多日资金确定性支付期限溢价（仓内探针：GC007−GC001 非窗口日均值 **+0.275pp**·全样本中位 +0.155pp）②**日历边界资金集中**：月末/季末/长节前机构面临监管考核/资产负债表约束/备付需求→隔夜融资需求集中推高隔夜利率（仓内探针：GC001 月末末日 2 日均值 **4.01%** vs 非月末 **2.46%**·季末末日 5 日均值 4.36%·长节前 2 日均值 4.08%·p95 11.9-16.1%）。**谁付出代价**：常态日为期限确定性付费的借款方（期限溢价）+日历边界受约束机构（月末季末高价隔夜）；现金腿持有者=收取方。机理载体=现金腿摆动：常态日坐收期限溢价、窗口日滚隔夜收割边界尖峰。
- **同族相关性准入（D6）**：4 格日收益序列两两 |corr| + 对在册 6 CE 成员（core48 权益面）max|corr|——跨资产类预期 <0.1（现金腿 vs 权益面）；≥0.7=拒收；数值批报告 D6 表逐对列。
- 排除簿：已判精确核=CN_KLINE 四形态族/W4 VOL 门 461 格/W1/W2/MASS/W3 语法核零涉（本族非 K 线形态/非 ETF 语法轴·repo 利率面仓内首判）；判负族重试律不适用（repo 面零前判=新族合法开法非重试）。

## §2 数据与面板。【跑前探针事实·冻结引用件 `results/_r180bmc_supply_prereg_probe_facts.json`（r180 实读·cutoff 截断后）。】

- **面板四元组**：`data/repo_daily/*.csv`（11 期限）＋ raw `pd.read_csv` 直读（date,open,high,low,close,volume）＋ 2011-05-13 全史起算（GC001 3,735 行·cutoff 截断后）＋ **零预热窗**（利率序列无指标预热；日历窗=外生日历零预热）。**探针-锚同面断言**：runner 加载路径与本声明逐位比对（一面不等=配置错配 VOID·fail-closed 报「面错配」非「数据腐坏」·INCIDENT-20260928 R3 律）。
- **逐期限覆盖（cutoff=2026-09-22 截断后）**：GC001/003/004/007/014 全 3,735 行 2011-05-13→2026-09-22；GC028 3,735 行 2011-05-10 起；GC091 3,689 行 2006-11-01 起；GC182 3,376 行 2009-01-13 起；R-001/003/007 3,240-3,319 行 2012-12-10 起；**全 11 期限末行==2026-09-22**。利率带实证 0<close<200（GC001 max 53.44=2015-02-10 春节前真钱荒正典锚）。
- **judged 格期限域冻结**：沪市 GC 族（GC001/007/014/028）——深市 R- 族中位数 1.87-2.21 低于沪市（费率结构差·非本批域·披露不判）；GC091/182=超长期限低流动性（rows 缺口披露·不入格）。
- **日历窗定义（冻结编码·外生日历零前瞻）**：①**月末窗**=每公历月最后 2 个交易日（探针 370 日/15.4 年）②**季末窗**=每公历季最后 5 个交易日（310 日）③**长节前窗**=交易日历上下一缺口 ≥4 自然日的最后 2 个交易日（194 日·Spring Festival/National Day 族）——窗态在 d 日收盘前即已确定（外生日历·T+1 因果律零涉未来数据；交易日历主源=repo 面板自身日期序列=本地 ETF 交易日历同源族 15:30 约定）。
- **evidence_cutoff=2026-09-22**（P-5C 冻结口径 binding·判读与全判决族同锚）；cutoff 后新 bar 锁定不回流；结果 JSON 顶层必带 `science_gates.cutoff_meta("2026-09-22")`（缺字段=C2 VIOLATION）。
- 数据完备门（fail-closed·不过即 VOID 零产出）：G-PANEL 11 件 re-derive 且 GC001/007/014/028 末行==2026-09-22 且 GC001 rows==3,735；G-CALENDAR 月末窗 re-derive==370∧季末窗==310∧长节前窗==194；G-RATE 全格域利率 0<close<200。

## §3 方法学。【必填。】

- **引擎（确定性日计息摆动·冻结）**：状态机=(工具, 锁定利率, 到期日)；隔夜 GC001 于 d 日决策→次日单日计息 close/365；期限 GC-k 于 d 日决策→锁定 close_k(d)/365 × k 自然日（到期次交易日重决策）；窗口日与非窗口日目标工具按 §0 四格定义切换；无中途解约（真实约束：回购不可提前赎回）；日收益=计息利率/365 逐自然日累乘。
- **judged 格（4 格冻结·批内零选优）**：
  1. `CAL-SWITCH-GC007`：窗口日（月末末2+长节前末2）滚隔夜 GC001·余日 GC007 期限滚动；
  2. `CAL-SWITCH-GC014`：同窗口→隔夜·余日 GC014；
  3. `QW5-SWITCH-GC014`：季末末5+长节前末2→隔夜·余日 GC014（季强度变体）；
  4. `CAL-SWITCH-GC028`：窗口同格 1·余日 GC028（长期限溢价变体）。
- **passive 基线**：`PASSIVE-GC001-ROLL`=每日滚隔夜（skill_line passive_term 载体·披露列不计 N）。
- **null 对照**：K=2000 随机日历摆动 null——同窗日数/年随机置换日历位置（保摆动强度毁日历结构）·seed 基 `innovation_quota_w1_repo`=**20295000**（rng([20295000, k])·k<2000）；**虚拟起点** K=1000（k∈[2000,3000)·RANDOM_LARGE_SAMPLE_LAW §1 K≥1000）；**随机分窗** 100 窗（k∈[3000,3100)·律 §3 ≥100）。
- **成本口径**：零交易成本域（交易所回购佣金=按标准费率极低且对现金腿摆动恒在——**如实披露**：简化面=费率忽略·判读加注「费前口径」；若判正入册前补费后复核=五步制第 5 步纸盘面承载）。
- 账本：`science_gates.append_ledger("REPO_CALENDAR_P1", 2004, "results/innovation_quota/REPO-CALENDAR-P1.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev）。

## §4 判据。【跑前写死，禁看结果调线。】

- **G1' v2**：`science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=4, n_trades, n_entries)` 逐格（skill_line_v2=max(passive+0.10, μ_null+σ_null·√(2·ln N_eff))·passive=PASSIVE-GC001-ROLL 年化）；批报告逐列披露 skill_line/passive_term/null_term 全输入；胜率+回合期望双披露（O-1524 KPI 律）。
- **G2 注册资格 v2**：G1' 过 ∧ DSR≥0.95（`deflated_sharpe_ratio` 原始收益）∧ 族 PBO≤0.25（`screening/pbo.py` CSCV 8 块·4 格族）——过格=入册资格（STRATEGY_LIBRARY 现金腿袖候选·intake 另行走 CE admission 面）；不过=judged-negative 族关单+新证据重开注记（RANDOM_LARGE_SAMPLE_LAW §5）。
- **RANDOM_LARGE_SAMPLE_LAW 绑定**：K=1000 虚拟起点 beat_rate 全披露（6m/12m/24m 三窗）；100 随机分窗半窗 Sharpe 同号率 ≥80%=分段稳定（<80%=segment-unstable 旗如实）。
- 硬界设计三件套：本批判线=分布界口径（null p95/中位承载·非裸 max）；**利率上尾=收益有利向**（极端日=2013-06 钱荒/2015-02 春节前 53.44/2015-07 股灾周的窗口日隔夜尖峰=正尾非破线·逐日单列披露承载）；跑前极端日先验=§5。

## §5 跑前预测。【写死于跑前·≥3 条。】

1. 四格年化 vs passive 的 pickup 预测：CAL-SWITCH-GC007 ∈ **[+10, +50]bp**（仓内探针代数：常态日期限溢价 +0.275pp×~89% 权重 + 窗口日隔夜尖峰溢价 +1.55pp×~11% 权重≈+0.42pp 上界·费前口径·保守下界 10bp）；GC028 格 pickup 预测 ≤ GC007 格（长期限溢价中位 2.695 vs GC007 2.5 差距小+锁定成本高）。
2. null 对照预测：CAL-SWITCH-GC007 年化 ≥ 随机日历 null p95（日历结构真实≠随机）；若 <p95=预测错=日历效应不可检。
3. 极端日先验：2013-06 钱荒窗+2015-02-10（GC001 53.44 正典锚）+2015-07 股灾周的窗口日隔夜单日年化可破 30%——正尾逐日单列；2015 后利率中枢下移（GC001 中位 2.155）→分窗半窗同号率预测 ≥80%（2013-2015 高利率段与 2016-2026 低利率段两段均正=结构跨 regime 稳定主张）。
4. 风险预测：GC014/028 长期限格在利率下行段（2018-2024）锁定成本=逆风段——QW5/GC028 格分窗同号率预测可能 <80%（segment-unstable 旗候选如实）。

## §6 产物。

- runner `scripts/innovation_quota_w1.py`（**下轮建·selftest 先行**·梯 runner_exists 门届时自开）→ `results/innovation_quota/REPO-CALENDAR-P1.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+四格全量+nulls/虚拟起点/分窗记录+D6 表+funnel 双列：收割 1 族〔仓内未试面扫描〕vs 过闸 0/4 待判）。
- 本冻结 commit 面：本件+SEED_REGISTRY 新行+F-04 MSG+探针事实件。

## §7 跑后实证。【跑前必须为空——占位纪律：写数字即造假。】

（一次定稿；工程修复重跑须双跑留痕如实记账；确定性引擎产物写 bug 的合法重执行口径≠结果重跑。）

- **烧录回执**（r182 bm-c 收口·2026-09-28 21:06:58 runner 完成·回执 `results/innovation_quota/REPO-CALENDAR-P1.json`·账本 +2004→319863·损耗账行 `results/gate_attrition.json` runner 自写）：四格+passive 全烧，K=2000 nulls + K=1000 虚拟起点（6m/12m/24m）+ 100 随机分窗全跑。
- **G1' v2 判线读数**：skill_line_v2=**25.006**（passive_term 11.8962／μ_null 22.3153／σ_null 0.5344／N_eff 319863）。
- **逐格**：CAL-SWITCH-GC007 s=19.3526 **FAIL**（< μ_null 22.3153＝周期限日历摆动不可与随机日历 null 区分→**judged-negative 关单**·重开唯一通道=新 prereg+新证据 RANDOM_LARGE_SAMPLE_LAW §5）；CAL-SWITCH-GC014 s=29.1961 **PASS**；QW5-SWITCH-GC014 s=26.5594 **PASS**；CAL-SWITCH-GC028 s=34.8303 **PASS**。年化 8.23%／11.23%／10.79%／12.73% vs passive 4.63%（费前口径如实）。
- **G2 注册资格**：3/4 eligible（DSR=1.0≥0.95／族 PBO=0.0≤0.25／虚拟起点 beat_rate=1.0 三窗全格／分窗同号率 1.0（100 窗）全格 segment-stable／D6 对 6 员 max|corr|<0.7）→ **STRATEGY_LIBRARY 现金腿袖 intake 开票 T-2026-09-28-112**（CE admission 面另行走）。
- **§5 预测对账**：预测1 GC007 pickup [+10,+50]bp——实测 +360bp（8.23-4.63）**量级严重低估=错**（但 g1 判线仍负：pickup 真但不可与随机日历区分）；预测2 GC007≥null p95——**错**（19.35<μ_null，日历结构在周期限不可检）；预测3 极端日正尾——回执 extreme_day_tail 单列承载=如实；预测4 GC014/GC028 segment-unstable 风险——**未兑现**（同号率 1.0≥0.80，结构跨 regime 稳定主张成立）。
- **诚实披露**：①费前口径（§3 冻结）——入册前费后复核由 intake 票承载；②null 面=随机日历摆动（同窗日数保摆动强度）——周期限格败于此面而长期限格过线＝「锁定期溢价须够长才可检」为批内新事实。

## §8 批后复盘。【必填·s7-T。】

- 预测对账（对/部分/错）＋门禁链损耗账（`results/gate_attrition.json` 追加一行）＋判线 v2 当批读数（skill_line_v2 数字）；judged-negative 族=关单+重开注记；回执入轮报告＋CODELY.md 行级追加；若 G2 过格=STRATEGY_LIBRARY 现金腿袖 intake 面另行开票。
