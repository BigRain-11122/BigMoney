# BACKTEST_READINESS 回测全要素就绪清单（O-20260923-1653 交付件）

> CEO 令「你给我把你做回测要用的所有都准备好！」（via bm-a quant 专管会话 16:53，总经理自决域执行）。
> 审计时点=2026-09-23 17:05 本地钟；件件带证据指针；缺口=即补或精确派发。
> **V2.1 增量刷新 19:55**（quant 专管会话）：bars 落地/WQ101 交付/账本 N=2020/缺口#1#5 对齐实况；17:05 快照原件见 git 历史（b7f5dc3）。

## §0 判定

**全要素可开跑。** 六面要素（数据/引擎/因子/撮合成本/闸门/算力依赖）全部就绪（V2.1 时点：bars 已落地、WQ101 已交付，缺口台账仅余源侧延迟与候选移植件）。

## §1 数据要素

| 资产 | 状态 | 证据指针 |
|---|---|---|
| core48 日线（主战场燃料） | ✅ 就绪 | `data/daily` 48 裸码 CSV，cutoff 2026-09-22；增量链 `scripts/update_daily.py` 在飞（`results/update_status.json`：48 符号/收盘守卫≥15:30/8 次探针 sina 未发布 09-23 bar=源延迟，发布即自动 sweep） |
| A股全史 bars 1.09GB/10444 件 | ✅ 已落地 | r10 接收腿双侧 SHA256 Verify PASS（10444 件/1,167,172,943 字节）→ T-01 done（回执 MSG-1725）；BigMoney-data main=`81b93d3`；已落位 `Money02\data\bars`，Stage-A 股票池缓存建于其上（R12 双门 PASS）——**688 volume 单位警报见 TURNOVER_DERIVATION.md §3** |
| 25 年日线面板（204→215 只全政体谱） | ✅ 就绪 | `Money0923\data\daily`（215 CSV，O-1514 盘点令入仓） |
| 基准指数（上证/沪深300/中证500） | ✅ 就绪 | `Money02\data\index\{sse,hs300,csi500}.parquet` |
| 分钟语料（不可再生） | ✅ 就绪 | `Money0923\data\minute_store`（O-1514：57.2MB） |
| 龙虎榜 19 年 | ✅ 就绪 | `Money02\data\lhb`（B 层燃料，265,831 行） |
| 逆回购利率全史 | ✅ 就绪 | `Money0923\data\repo_daily.csv` |
| 加密 26 币 | ✅ 就绪 | `Money02\data\mkt_crypto`（跨市场验证燃料） |

## §2 引擎要素

- `engine/backtester.py`（信号适配器 entry/exit=DataFrame 已泛化，J7）+ `engine/exit_rules.py`（**退出优先级/T+1/成本模型=红线禁改**，红线台账指针 `firm/risk/iron_rules.md`）+ `engine/metrics.py`。
- **20 项 smoke 背书**（`python -m smoke_test`，含引擎冒烟/确定性逐位/T+1 零同日往返/费率 13bp/T+0 清单/paper 锚定门禁 3 员复现）。
- 参数网格 432 组 `config/param_grid.py`（combo_hash 确定性 smoke 断言）。

## §3 因子要素

- **内部 27 因子**：`engine/factors.py` FACTORS 注册表（宽面板 date×symbol 口径）；IC 工具 `scripts/factor_ic.py`+`scripts/composite_ic.py`（含 core/all 宇宙去重口径）。
- **外部 GTJA191（191 因子）批测已毕，双件互证**：
  - **canonical（§4 撞车裁定采此）**=bm-b OS轮-32：`research/shortline/P1_FACTOR_SCREEN.md`（跑前写死）+ `research/shortline/screening/p1_factor_screen.py` + 净室算子层 `research/shortline/screening/gtja191_ops.py`（9/9 selftest）→ **0/183 严门判负**（V1=max(0.02,null p95)/V2 IR≥0.30/V3 OOS 同号+衰减<50%），近失簇 081/100/097 带 snooping 折价记录；账本 **N=1312**。
  - 补充件=bm-a R9：`research/shortline/P1_GTJA191_IC.md` + `scripts/shortline_p1_ic.py`（IC 等价门禁 3.33e-16+shim 自检双门禁）→ 183 计算位/89 宽筛池/白噪声 null 局限注记（宽筛≠有效名单）。
  - 互证：计算位一致（183）、跳过集一致（030/143 unfinished、005 pandas3、turn 族缺字段、qlib 3 件降级）、头部簇一致（081/100/165/097 反转 DNA 负 IC）——两机独立实现同一库同一宇宙，结论同向。
- **外部 WorldQuant101**：R11 已交付（P1_WQ101_IC.md：82/82 可算，h10 严口径 0/82——与 GTJA191 0/183 同判「单因子过墙无望、合成是唯一路径」双库实证；池 36/强档 32 留作宽筛合成素材）。
- 合成方法论：`research/COMPOSITE_FACTOR.md`（z 合成）+ `research/NULL_CALIBRATION.md`（零假设校准）。

## §4 撮合规则与成本口径

- 单一真源 `knowledge/rules.py` v2026.09.22（引擎读此不硬编码）：FeeSchedule（佣金万2.5+经手 0.0341‰+证管 0.002%双边+滑点 A 级 0.1%/C 级 0.3% → **单边 13bp smoke 实证**）；PriceLimit（主板 10%/创科 20%/北交 30%）；T+0 白名单 17 只；min_lot 100 股；tick 0.001。
- A股规则知识库：`knowledge/market_rules.md`。

## §5 质量闸门（反过拟合链）

- **G1'（有效性门）**：四条款+技能线 0.4004（`research/NULL_CALIBRATION.md` §3 预注册写死；随机基线 n=100+被动 null 双对照）。
- **G2（出厂门）**：±邻域全绿+成本 ×2/×3 存活+逐年无崩年（`research/G2_DEEPENING.md` 范式）。
- **三铁律**：先过有效性门才扫参数/每批同跑随机基线+账本 N 记账/样本外 2025+ 恒盲+成本恒开+禁止跑到达标为止（`research/BACKTEST_PLAN.md`）。
- 在册交易员 3 员（`firm/traders/`，全过 G2 门禁链 10 步）+ paper 管道（`live/paper.py` 锚定门禁+evidence_cutoff+月度反造假）+ 晋升条款（`firm/hr.py` paper_months_min=1）。
- 试验账本：**N=2020**（P-5/P-4①/P-4②A 后现值；双机账面竞态差由 main 集成轮收口）。

## §6 算力与依赖环境

- 本机 bm-a：32 核/空闲 RAM ~46GB/RTX3070 空闲 VRAM ~3GB。GPU 门未开（BACKTEST_PLAN P4 三条件：≥2 策略过 G2 ✓/ML 任务在制 ✗/显存够走 keepwarm 礼仪——**不满足不开**）。
- 核心依赖实证：numpy 2.5.2/pandas 3.0.6/scipy 1.18.1（smoke PASS）。
- 研究环境：`research/shortline/requirements-research.txt`——**ta 未装**（playbook §3 明令零外部 C 依赖、纯 pandas 替代）、**polars 未装**（WQ101 移植时处理）、**qlib 不装**（191 回归类降级条款，playbook §2.2）。
- 新机自举：`bootstrap.py` 一条命令（依赖自装+20 项 smoke+面板数据生成）。

## §7 缺口台账（件件带处置）

| # | 缺口 | 处置 |
|---|---|---|
| 1 | bars 接收落地 | **已闭环**（r10 双侧 Verify PASS+T-01 done+MSG-1725） |
| 2 | WorldQuant101 无 cap 子集 | 已派发研究部循环轮（polars→pandas 移植+预注册），不阻塞 A 层 |
| 3 | sina 09-23 收盘 bar 源延迟 | 发布即自动 sweep（update_daily 钩子已接线 live.paper），无需人工 |
| 4 | alpha191_005 pandas3 相容（Rolling.rank axis） | vendored 资产不中途改，登记移植候选 |
| 5 | turn/liquidity_value 字段缺（191 中 2+1 件） | **分板推导已实证**（TURNOVER_DERIVATION.md：非 688=volume/osh、688=volume/100/osh；附 688 volume 单位警报）——Stage-B 内联推导可解除，入批由其预注册自裁 |
| 6 | GTJA191 依赖 qlib rolling_slope 3 件 | 降级条款已用（缺则跳过记账）；如需可另开纯 pandas 移植预注册 |

## §8 结论

做回测要用的所有要素=**数据六类全备（bars 分钟级在飞）、引擎+撮合+成本单一真源并 smoke 锁定、因子内外库+双 harness 跑通互证、闸门链+账本制+反过拟合三铁律在制、算力依赖环境健康**。可立即开跑；下一场预注册回测（P-2 合成/A 层骨架族）不受上述任一缺口阻塞。

—— O-20260923-1653 执行体：bm-a 循环轮 R9（dept:研究）· 2026-09-23 17:05
