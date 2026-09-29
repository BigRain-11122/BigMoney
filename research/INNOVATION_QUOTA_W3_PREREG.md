# INNOVATION_QUOTA_W3_PREREG · 创新配额槽-3：指数高阶矩择时族（HIGHERMOM-TIMING-P1）judged 判决批

> 状态：**跑前冻结**（2026-09-29 r239 bm-c · 与 F-04 MSG＋SEED_REGISTRY 登记＋fill_ladder_catalog tranche-3(d) 条目同 commit）；跑后只许回填 §7 占位节，禁改判据禁重跑。
> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节+G-ANCHOR-FACE 四元组 O-20260928-1712 律）；令源=O-20260928-1614 §一.4 填充阶梯④创新配额（每闲置窗≥1 新假设族）+O-1721 借力律+RESEARCH_MECHANISM 常态线；票=T-2026-09-28-107 §4(d)+fill_ladder_catalog `INNOVATION-QUOTA-SLOT-3` 条目（lane_owner=null·enqueue_gates=prereg_frozen+runner_exists）。
> **族选防重核（r239 实读）**：①族源=ASTYLE_ZOO #95 `index_higher_mom_timing`（**参数化已冻结** r263 bm-b·DIGEST-20260926-wave10-paramfreeze-95-96.md §二·clean-room）＝**untried zoo family**（SLOT-1 票面三正源之一）；②仓内已烧面核验：`rg 高阶矩|higher_mom` 全仓零结果件命中（results/innovation_quota/ 仅 REPO-CALENDAR-P1/P2+FEE-RECHECK——本族零前判=新族合法开法）；③T-101-V4 A 系三支线 timing 关闭面（A2/A158-FV/A10 r433/r441/r442）=**政体门族**（A158 门构造读数）≠本族矩阶状态变量读数——非同族面不撞排除簿；④VOLATILITY-CE-01=低波截面轮动注册员（二阶矩截面用法）≠本族时序择时用法；⑤A158-TSGATE 48 PASS 门池=W11 试用法轴线（trial-labor 道）≠本创新配额道——双道合流面=批报告 D6 表+funnel 双列披露。
> 外源锚披露（借力律·宣称≠验证）：广发 2015-05-20《交易性择时策略研究之八：指数高阶矩择时策略》宣称面=【未实证】D 级零采信（zoo #95 全档）；本批不依赖其宣称数字，构造面按 zoo r263 冻结参数化 clean-room 复现。
> 统摄律：firm/RANDOM_LARGE_SAMPLE_LAW v1.0 + research/BACKTEST_SCIENCE.md v2（判据唯一权威）+ BACKTEST_PLAN.md 三铁律 + research/COMPUTE_AUDIT.md 批件纪律。

## §0 批件身份。【跑前。】

- 批名/批号：**HIGHERMOM-TIMING-P1**（创新配额槽-3·指数高阶矩择时族）。N_eff = **3 judged cells + 2000 null draws = 2003**（CN_KLINE/W1 同口径计数律；passive 基线=披露列不计 N）。
- 认领：F-04 先行已落（`fleet/inbox/MSG-20260929-2100-bmc-all-innovation-quota-slot3-prereg-freeze.md`）；任务引用=T-2026-09-28-107 §4(d)+fill_ladder_catalog tranche-3(d)。
- 部门归属：dept:策略（指数择时族判决面）；消费位=T-34 快线候选池（zoo #95 登记消费位·冻结毕可评→本批=可评兑现）。
- 算力预算：向量化日频状态机 3,465 可判日 ×3 格+2000 nulls+1000 虚拟起点+100 分窗 = 分钟级池批；>5min 入池（O-2100 执行面分离）·checkpoint 幂等。

## §1 α 机制段。【四选一+论证·D6 门槛。】

- [x] **行为偏差**：彩票偏好与尾部注意力（zoo #95 冻结 D6 面）——奇数阶原点矩对右尾极端收益敏感：正五阶矩膨胀=彩票型右尾需求/注意力拥挤状态变量；EMA(90) 平滑矩读数的时序差分符号=「尾部压力构建期 vs 消退期」的趋势触发（非阈值穿越）。**谁付出代价**：追极端收益的彩票盘与恐慌抛售者在矩读数拐点两向磨损；择时者收拐点延续段。付费方=注意力被右尾极端日吸引的追涨杀跌双向群体（BGS 2012 凸显理论谱系·宣称面【未实证】）。
- **同族相关性准入（D6）**：3 格日收益序列两两 |corr| + 对在册 6 CE 成员（core48 权益面·`scripts/cn_rev_tilt_p1.py load_member_rets + REG6` 同 W1 载面零重实现）max|corr|——时序择时面 vs 截面成员面预期 <0.7；≥0.7=拒收；数值批报告 D6 表逐对列。**近邻警示披露**（zoo #95 原文）：与 VOLATILITY-CE-01（二阶矩截面）不同矩阶不同用法、与 REGIME_GUARD 状态面近邻不同读数——vol 族=高危对，D6 表必列对照清单。
- 排除簿：已判精确核=T-101-V4 A 系政体门族 timing 关闭面（矩阶状态变量非 A158 门构造=非同族）；REPO-CALENDAR-P1/P2（现金腿日历族）；P1E zoo 行为因子批（#85/#92/#93 股票域截面 IC——本批=指数时序域不同面）；判负族重试律不适用（高阶矩面零前判=新族合法开法非重试）。

## §2 数据与面板。【跑前探针事实·冻结引用件 `results/_r239bmc_highermom_w3_probe_facts.json`（r239 实读·cutoff 截断后）。】

- **面板四元组**：`data/daily/sh510300.csv`＋ raw `pd.read_csv` 直读（date,open,high,low,close,volume,amount）＋ **2012-05-28 起算 3,486 行**（cutoff=2026-09-28 截断后）＋ **预热窗=矩窗 20+EMA 追踪**：ret 首有效 idx 1→mom(20) 首有效 idx 20→EMA(90, adjust=False) 首定义 idx 20→信号首可判 **idx 21**（diff 对前一 EMA 值）；可判日 **3,465**。**探针-锚同面断言**：runner 加载路径与本声明逐位比对（一面不等=配置错配 VOID·fail-closed 报「面错配」非「数据腐坏」·INCIDENT-20260928 R3 律）。
- **三腿探针事实（冻结·runner 再derive逐位比对）**：MOM3 段数 **86**·止损出场 **4**·信号多头日 1,810·停损叠加后持仓日 1,713；MOM4 段数 **41**·止损 **2**·多头日 908·持仓日 860；MOM5 段数 **46**·止损 **5**·多头日 1,854·持仓日 1,733（全部 r239 探针实读·`_r239bmc_highermom_w3_probe.py` 确定性可复跑）。
- **极端日面（描述披露）**：最差日 2015-07-08 ret −10.005%／最佳日 2015-07-09 +9.991%（±10% 两日连发=矩读数主导事件·批报告逐日单列承载）。
- **evidence_cutoff=2026-09-28**（P-5C 冻结口径 binding·判读与全判决族同锚）；cutoff 后新 bar 锁定不回流；结果 JSON 顶层必带 `science_gates.cutoff_meta("2026-09-28")`（缺字段=C2 VIOLATION）。
- 数据完备门（fail-closed·不过即 VOID 零产出）：G-PANEL rows==3,486 ∧ first==2012-05-28 ∧ last==2026-09-28；G-LEG 三腿 entries/stops/long-days 再derive==探针冻结值（86/4、41/2、46/5 与 1810/908/1854）；G-SIG warmup 链 idx（moment 20·EMA 20·首可判 21·可判日 3,465）。

## §3 方法学。【必填。】

- **引擎（确定性日频状态机·冻结）**：`ret=close.pct_change`；`mom(n)=ret.pow(n).rolling(20, min_periods=20).mean()`；`ema=mom.ewm(span=90, adjust=False).mean()`；`rising=ema.diff()>0`（T 日收盘信息·零前瞻）；`sig=rising.shift(1)`（**T+1 持仓 onset**·信号滞后嵌入=因果律）；**段状态机**=sig False→True 沿入场、True→False 沿信号出场；**止损叠加**=持仓中自入场累计收益 `<−0.10` → 平仓至**下一段 onset** 才再入（「单次 10% 止损线」保守读法冻结：研报原文语义未验证【未实证】·两可处取保守向并在此留痕）；持仓日收益=`position(t)×ret(t)`（close-to-close 口径）。
- **judged 格（3 格冻结·批内零选优·zoo r263 冻结候选「矩阶∈{3,4,5} 三腿对照」全谱）**：
  1. `MOM3-TIMING`：三阶原点矩腿（登记叙述腿一）；
  2. `MOM4-TIMING`：四阶原点矩腿（登记叙述腿二）；
  3. `MOM5-TIMING`：五阶原点矩腿（复现偏好腿·研报主实现面）。
- **passive 基线**：`PASSIVE-510300-BH`=买入持有（skill_line passive_term 载体·runner 在批窗口活算年化 Sharpe 喂 `passive_override`·REPO_CALENDAR_P2 先例·禁手抄；披露列不计 N）。
- **null 对照**：K=2000 随机段置 null——每腿保段数+保持仓日数、随机重置段 onset 位置（保交易强度毁矩结构）；seed 基 `innovation_quota_w3_mom`=**20319000**（rng([20319000, k])·k<2000）；**虚拟起点** K=1000（k∈[2000,3000)·RANDOM_LARGE_SAMPLE_LAW §1 K≥1000）；**随机分窗** 100 窗（k∈[3000,3100)·律 §3 ≥100）。
- **seed 重取披露（零跑修正·r251/r280 先例族·2026-09-29 r240 bm-c）**：冻结基 20317500 在 r239 未推送在飞窗口与 bm-b r441 W11 scrnull 重取键撞号（r441 21:08 落 origin 先于本方推送）——后到让路律本批重取 **20319000**（band rg 零仓内命中；20318500 因 data 面成交量列数值巧合 x4 弃用）；runner 未建=20317500 上零格已烧零判决影响，纯 seed 面修正非结果驱动，SEED_REGISTRY 同窗同步。
- **成本口径**：x1=**13.041bp/边**（`scripts/ce_transfer.py COST_X1_RATE` import·G2-recorded 基线·禁手抄）持仓翻转双边计费；x2=双倍成本披露列（CostPatch 先例）；判据面=x1。
- 账本：`science_gates.append_ledger("HIGHERMOM_TIMING_P1", 2003, "results/innovation_quota/HIGHERMOM-TIMING-P1.json", evidence_cutoff="2026-09-28")`（dict schema 唯一禁手抄 prev·`out["trials_ledger"]` 返回值必落=r434 坑律）。

## §4 判据。【跑前写死，禁看结果调线。】

- **G1' v2**：`science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=3, n_trades, n_entries, null_pool={批自 null 族}, passive_override={510300-BH 批窗活算})` 逐格（skill_line_v2=max(passive+0.10, μ_null+σ_null·√(2·ln N_eff))；批报告逐列披露 skill_line/passive_term/null_term 全输入）；胜率+回合期望双披露（O-1524 KPI 律）。
- **G2 注册资格 v2**：G1' 过 ∧ DSR≥0.95（`deflated_sharpe_ratio` 原始收益）∧ 族 PBO≤0.25（`screening/pbo.py` CSCV 8 块·3 格族）——过格=T-34 快线候选池登记资格（intake 另行走 harness A/B 面·T0 刹车权威归 REGIME_GUARD 不破）；不过=judged-negative 族关单+重开注记（RANDOM_LARGE_SAMPLE_LAW §5）。
- **RANDOM_LARGE_SAMPLE_LAW 绑定**：K=1000 虚拟起点 beat_rate 全披露（6m/12m/24m 三窗）；100 随机分窗半窗 Sharpe 同号率 ≥80%=分段稳定（<80%=segment-unstable 旗如实）。
- 硬界设计三件套：本批判线=分布界口径（null p95/中位承载·非裸 max）；权益多头面=上尾有利向（极端日=2015-07-08/09 ±10% 连发=矩读数主导事件·批报告逐日单列披露承载）；跑前极端日先验=§5。

## §5 跑前预测。【写死于跑前·≥3 条。】

1. 三腿持仓占比预测：MOM3/MOM5 ≈49-53%（1,713-1,733/3,465）、MOM4 ≈25%（860/3,465）→三腿年化波动≈passive 的 0.25-0.55 倍；全窗（2012-05→2026-09 含 2015 股灾+2018 熊+2024-09 牛）passive 510300-BH 年化 Sharpe 预测 ∈ [0.2, 0.6]。
2. 信号时滞预测：EMA(90) 双重平滑（矩窗 20+EMA 追踪 90）=拐点识别慢——三腿中 ≥1 腿 G1' FAIL 预测成立（时滞吃掉择时价值·W1 GC007「结构真但不可检」同型风险）；若全 FAIL=族关单非机制证伪。
3. 腿间排序预测：MOM5（奇数阶右尾敏感=研报偏好腿）beat_rate_12m ≥ MOM3 ≥ MOM4（偶数阶矩恒正=右尾左尾混叠读数弱信息面）。
4. null 面预测：随机段置 null 的 μ_null 显著低于 passive 全仓 Sharpe（半仓暴露效应）→skill_line 大概率由 null 项主导；若某腿 Sharpe < null p95=矩结构不可与随机段区分（judged-negative 主通道预判）。
5. 极端日先验：止损出场 4/2/5 次中预测主发 2015-06/07 股灾窗（段 onset 于急跌前）+2018 熊段；2024-09/10 牛 onset 段=任何过线腿的主要正贡献段。

## §6 产物。

- runner `scripts/innovation_quota_w3.py`（**下轮建·selftest 先行**·梯 runner_exists 门届时自开）→ `results/innovation_quota/HIGHERMOM-TIMING-P1.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+三格全量+nulls/虚拟起点/分窗记录+D6 表+funnel 双列：收割 1 族〔zoo 未试面扫描〕vs 过闸 0/3 待判）。
- 本冻结 commit 面：本件+SEED_REGISTRY 新行+F-04 MSG+探针事实件+fill_ladder_catalog tranche-3(d) 条目。

## §7 跑后实证。【跑前必须为空——占位纪律：写数字即造假。】

（一次定稿；工程修复重跑须双跑留痕如实记账；确定性引擎产物写 bug 的合法重执行口径≠结果重跑。）

## §8 批后复盘。【必填·s7-T。】

- 预测对账（对/部分/错）＋门禁链损耗账（`results/gate_attrition.json` 追加一行）＋判线 v2 当批读数（skill_line_v2 数字）；judged-negative 族=关单+重开注记；回执入轮报告＋CODELY.md 行级追加；若 G2 过格=T-34 快线候选池登记面另行开票。
