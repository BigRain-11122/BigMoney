# EXIT_OVERLAY_P1 预注册（交易管理解锁·出场 overlay 对照判决批）· T-2026-09-26-78 s1 · O-20260926-0958

> 本件按 `research/PREREG_TEMPLATE.md` 起草，跑前 commit 冻结；跑后只回填 §7/§8，禁改判据禁重跑。
> 收敛声明（O-0958 纪律锚①）：引擎退出优先级**冻结不动**（熔断>止损>时间>兜底；exit_rules.py P1–P6 零改动）；本批全部 overlay=运行时参数/加性旗标，None→legacy 字节恒等（staged_entry L191 先例）。

## §0 批件身份

- 批名 / 批号：**EXIT-OVERLAY-P1**（批内格数＝6 员载体 ×（1 锚 + 4 overlay cells）＝30 配对格，N_eff=30 判决格；×2 压测=胜者面另计不入 N_eff）；
- 认领：任务板 `fleet/tasks/T-2026-09-26-78-P1.json`（bm-b r240 认领，CEO 即时票）；本件=s1（overlay 设计+prereg 冻结）；s2=加性旗标机械（dd_control）+网格引擎；s3=本批跑数；s4=胜者接线纸盘；
- 部门归属：dept:策略（出场设计·冻结律内）+ 组合与资金部（配对判决）+ 工程部（旗标机械）联合；
- 算力预算：30–40 跑 serial 预计 <2 分钟（J15 12 跑 6s 同构）；inline 合法（<5min 阈），批报告必带 audit 段。

## §1 α 机制段【D6】

- [x] **行为偏差**：处置效应纪律化——止盈阶梯强制分批落袋（对冲散户「赢小亏大」过早全卖赢家/死扛亏家）；跟踪止损=后悔厌恶的机械化纪律；组合回撤帽=恐慌性追涨杀跌的免疫面。付费方=未纪律化的往返流量（震荡带内追涨杀跌者的滑点与错位成本）。
- [ ] 风险溢价 / [ ] 结构性 / [ ] 微观结构。

**同族相关性准入检查【D6·本批形态声明】**：本批**非新信号注册批**——overlay=在册员出场参数修改的**配对对照判决**（加了对不对由数据裁，O-0958 纪律锚②），无新成员入候选池；故不适用新信号 `max|corr|≥0.7` 拒收律，同族面=每 overlay-ON 变体对**自家 OFF 基线**的日收益配对差分（§4 判据全部建立在 Δ 面）。成员本身的注册资格早已过 G2（在册事实），本批只裁 overlay 增益面。

## §2 数据与面板

- 宇宙/池：core48 裸码池（`live.paper.load_core`，48 只，无扩池）；
- 窗口与 **evidence_cutoff（前向锁盒 D2）**：面板全史截断到 runner 读取日最新完整 bar（cutoff 惯例=上一个完整交易日，lockbox 生效）；结果 JSON 顶层必带 `science_gates.cutoff_meta(cutoff)`；
- 数据完备门：`live.paper.self_test_patches()` PASS＋48/48 OHLCV 可读＋**6 员锚复现硬门**（任一 BROKEN=批 VOID）。

## §3 方法学

- 载体＝在册 6 员：COMPOSITE-CE-01 / COMPOSITE-CE-02 / DROUGHT-CE-01 / ENGULF-CE-01 / NEEDLE-DE-01 / VOLATILITY-CE-01（各员基线=注册件信号+exit_overrides 全量复现）。**AGGR-REGIME/AGGR-CONC-TOP2=纸面宿主非本批回测载体**（其 sleeve 消费在册成员，胜者 overlay 落成员 exit_overrides 后 AGGR 经 sleeve 继承；直接 AGGR 级 overlay 回测=s4 后纸面前向面，披露不混判）；
- overlay 实施（J15 唯一正确姿势，引擎文件零改动）：桥接字段（take_profit_levels / trailing_stop_activate / trailing_lock）走 params；非桥接字段（take_profit_fractions）走 ExitPatch 工厂注入，桥接 kwargs 恒优先；**ov_dd_control=新加性引擎旗标**（s2 机械：组合 NAV 运行峰回撤>trigger → 敞口缩至 de_risk_to（余量入现金腿），回撤收窄至 re_up_at 恢复；None→legacy 字节恒等+夹具镜像生产形态 r157 律）；
- **五件→四格映射（收敛披露，反重复）**：unlock①止盈阶梯+⑤分批出场=同一机械面（引擎 P3 分层止盈即分批出场梯度——levels+fractions 参数化即「分批止盈 overlay·组合级可配参」，**不另建 staged_exit 旗标**，P3 已是出场分批机械，重建=违反复用铁律）；unlock②移动止损=引擎 P2 高水位跟踪已在册（unlock=参数面+判决）；unlock③组合级回撤控制=新旗标；unlock④网格引擎=CN-GRID-SLEEVE 另开预注册（§9）；
- cells（冻结，CEO 例忠实）：
  | cell | 参数（相对各自基线） | 解锁面 |
  |---|---|---|
  | ov_tp_ladder | levels=(0.05,0.08)＋fractions=(0.5,0.5)（+5% 减半/+8% 再减半/余仓 P2 移动跟踪） | ①+⑤ |
  | ov_trail_peak | trailing_activate=0.03＋trailing_lock=0.05（+3% 激活·峰值回撤 5% 出场） | ② |
  | ov_dd_control | dd_trigger=-0.10 · de_risk_to=0.50 · re_up_at=-0.05（回撤>10%→半仓现金腿，收窄<5% 复仓） | ③ |
  | ov_full | 三者合并（CEO 例合成面） | ①②③⑤ |
- 成本口径：**V1 legacy 13bp ×1 主判**＋**×2 压测仅胜者面**（描述性生存披露）；T+1/成本模型/退出优先级本体零改动；
- null 对照：不适用（非注册批，判据=配对 Δ 面，§4）；账本：`science_gates.append_ledger("EXIT-OVERLAY-P1", batch_trials=30, file_name="results/exit_overlay_p1.json", evidence_cutoff=...)`（dict schema 唯一）。

## §4 判据【跑前写死】

- **锚复现硬门**：6 员 OFF 基线对注册件/正典读数 |ΔSharpe|<0.002（任一失守=批 VOID）；
- **配对判决（每员×cell 独立裁定，冻结）**：cell **WIN** ⇔ Δ(full Sharpe) ≥ 0 **且** Δ(OOS Sharpe) ≥ 0（双面不受损；OOS 切分恒 2025-01-01）。任一面负=REJECT（判负照报，禁事后挑面）；两 Δ 恰零=REJECT（无增益不接线）；
- 胜者面 ×2 压测=描述性（Δ×2full ≥ 0 披露，不作门）；描述条款：Δ年化/ΔmaxDD/Δ笔数/逐年最差全列披露；
- **注册效应（s4 纪律）**：WIN 配置→成员注册件 exit_overrides 更新（独立 commit+纸盘接线+smoke 锚定门期望值同轮再derive——锚数字会变，属预期更新非腐坏，三态标注立法/生效/验收）；REJECT 配置→不接线，教训入 §8。

## §5 跑前预测【写死于跑前】

1. ov_tp_ladder：砍赢家面在趋势收割员（VOLATILITY/COMPOSITE 族）大概率 Δfull<0（J15 c1 探针绿系 decay 放宽语境，默认紧面无此福利）；预测 2–4/6 员诚实负，高换手员（DROUGHT/ENGULF）存活 odds 最高；
2. ov_trail_peak：紧跟踪（3%/5%）在震荡员=多出场多吃滑点，Δ笔数显著上行、ΔSharpe 负向；预测 ≤2/6 双面不受损；
3. ov_dd_control：ΔmaxDD 机械改善全员，但 2024-09-24 型 V 反弹窗踏空 → ΔOOS 面分裂；预测半数员 ΔOOS<0；
4. ov_full：合成面最易在单点翻车；预测 ≤1/6 WIN；
5. 总体：**诚实负为主预期**（13bp 紧成本面+外部手法多负先例 J15/CTA/T-33 同向）；极端日先验：2015-07 救市/2016-01 熔断/2026-01-19 极端溢价日——跟踪止损在 T+1 跳空下面成交（滑点真实）、dd_control 在跳空簇发日集中触发；本批无 max 硬界（配对 Δ 面），极端日只流入 ΔmaxDD/Δann 描述面。

## §6 产物

- `scripts/exit_overlay_p1.py`（s3 交付：selftest 腿（ExitPatch 注入/恢复+dd_control 夹具镜像）→锚→cells→配对判决→JSON/CSV）；
- `results/exit_overlay_p1.json`（顶层 evidence_cutoff＋逐员×cell Δ 全表＋audit 段）＋`research/exit_overlay_p1_results.csv`；
- 本文件 §7/§8 回填＋`results/gate_attrition.json` 追加一行（判决面记账）。

## §7 跑后实证【跑前必须为空——写数字即造假】

（占位）

## §8 批后复盘【必填·s7-T】

（占位）

## §9 网格引擎面（unlock④·CN-GRID-SLEEVE）——本节=s1 设计冻结，预注册=s2 交付

- **血统**：T-73 s3 件由 T-78 提前解锁收编（O-0958；T-73 s3 标记 consumed-by-T-78，防重复协调）；**与 GRID-P1（T-40 slice-2 网格收割信号）非同物已收线诚实负禁翻案**——本件=ETF 网格交易**执行引擎**（区间+格距+每格仓位+破带处置的确定性机械），非通道位置信号选股；两件零重叠；
- 设计骨架（冻结待 s2 细化）：单一/少量 ETF 载体；band=滚动 250d 分位带（p20–p80 入带）；格距=带内 n_grids 等分；每格固定名义现金（grid_cash）；价格每下一格买入一格/每上一格卖出一格（T+1 开盘执行）；**破带处置**：收盘破下轨 p10 → 暂停新买单（带重建后重臂）；收盘破上轨 p90 → 网格持仓全平（破带=趋势接管，震荡假设失效诚实退出）；带=滚动重算（月频重建，避免频繁迁移）；
- 判读面：网格捕获率（每格往返实现价差×频次）/震荡 vs 趋势分段绩效/趋势段鞭打成本（诚实负预期——A股趋势段长而陡）；独立袖+独立纸盘账户族 GRID-*（¥1,000,000/账户，PROS-* 白名单范式独立车道）；
- 五步制：本节设计→GRID_SLEEVE_P1.md 预注册冻结（s2）→回测→判决→纸盘；α 机制段=行为偏差（区间内往返流量的流动性供给方，付费方=追涨杀跌往返客）——GRID-P1 §1 同源主张，引擎面新证。

## §10 s4 接线纪律（胜者面）

WIN 配置按 §4 注册效应落地：成员 exit_overrides 更新（独立 commit）→纸盘接线（live/paper 消费注册件自然继承）→AGGR 宿主经 sleeve 继承→smoke 锚定门期望再 derive→三态标注（立法=commit/生效=判据过/验收=复审✓）。纸面前向=最终裁判（CEO 实战出真知元律）。
