# P-1c 预注册：GTJA191+WQ101 股票池全宇宙 IC 批测（跑前写死 · 2026-09-23 18:12 · O-1738/MSG-1800）

> 执行者：**bm-a 循环轮**（认领=MSG-20260923-1812，先于任何跑数）；GM 派单=MSG-1800 §2「P-1c（新挂，bm-a 认领）」。
> 数据=MONEY02 bars 5222 件 parquet（双侧 SHA256 Verify 已过，T-01 done）+ 复权因子侧车 5222 件。
> 性质=**因子批测**（统计推断入账本）；零引擎跑（IC 层不触 engine/backtester，不产策略不注册交易员）。

## §1 任务定义与动机

- P-1a（GTJA191，core48）/P-1b（WQ101，core48）双库同判：**48 ETF 截面上单因子过墙无望**（严口径 0/183、0/82），合成是唯一路径。
- P-1c 问的是：**把截面从 48 换成 ~5130 只 A股全史**，反转/动量类经典异象（GTJA 反转 DNA 簇 081/097/100/165、George-Hwang、52 周高点等）是否在足够宽的截面上显出可用单因子？——宽截面=IC_IR 的噪声缩减来自横截面宽度，48 只的 V2 线（IR≥0.30）在 5130 只上是完全不同的统计环境。
- 结论定位：**选料批**（为 P-2' 跨库合成与 B 层股票池策略供素材），非交易员注册批。

## §2 宇宙与数据（跑前实测口径）

- 磁盘宇宙=5222 件 parquet（P-4-2a 实测：ok 5130 / short_history(<250 行) 92 排除 / read_error 0）；P-1c 宇宙=**ok 集 5129 只**（构建实测：≥250 行且复权侧车可读——1 只侧车不可读保守排除、symbol 与因由记 meta sidecar_error_syms，对 P-4-2a 的 5130 差 1 如实披露）。
- 字段：date/open/high/low/close/volume/amount/pct_chg/preclose/outstanding_share/turnover（datetime64[us]+float64）。
- **复权口径（§2.1 跑前修订 · 2026-09-23 18:28 · 缓存构建实证）**：初版写「adj = raw / f(t)」——**实证推翻：bars parquet 价格本身已是前复权**（000001 事件日 bar 日收益与 pct_chg 逐位一致如 +35.0376%=+35.0376%，十事件 dev=0.0；1991 bar=0.105 为复权后价非原始 46 元），侧车 f=产生该复权的累计因子=参考元数据**不再施加**（初版双重复权被 §2 跑前校验门当场拦下，缓存重建后过门）。OHLC/vwap/volume/amount/turnover/pct_chg 全按 bars 原值入缓存。
- **跑前校验门（缓存构建内置）**：①事件日 adj_close 日收益 vs pct_chg 偏差≤0.5%（抽 3 只全事件核）；②随机 3 只×3 字段 parquet 重读 vs 缓存切片 rel-tol 1e-5；不过门=中止不跑批。
- 幸存者偏差披露：bars 含已退市股与否以磁盘实测为准（meta.json 记录上市最早/最晚日分布），不做删失修正，读数时按「可能偏高」折价。

## §3 因子集（名义 273 = GTJA191 + WQ101 no-cap 82）

- **GTJA191**：注册公式全集 minus P-1a/b 结构性排除账本（030/143 unfinished、005 vendor pandas3 Rolling.rank bug）；**股票池字段可用性再审计**：`turnover` 在 → **033/062 从 skip 升级可算**（早期年份 NaN 由 IC 掩码处理，如实记）；021/116/147 用 R11 REGRESI 闭式复测实现。
- **WQ101 no-cap 子集 82**：18 个 neutralized 因子仍缺行业分类保持排除；**alpha056（cap 排序类）股票池有 outstanding_share 技术上可算，但为跨批可比性与 GM 273 口径保持排除**，记为候选扩展（另开预注册才动）。
- 有效可算数=跑时实测记账（期望 186 GTJA + 82 WQ = 268 上下），每因子 status 逐行留痕（bm-b r32 分类法：ok/skip_*/error）。

## §4 方法论与门禁（全部复用既有口径，禁重写）

- IC=逐日横截面 spearman（`_ic_series_fast`：**先掩码后排名**，等价自检门禁 vs `composite_ic.ic_series` max|diff|≤1e-6 跑批前置）；`stats_block`；**IS_END=2024-12-31**（OOS=2025+，样本外恒盲）。
- 期限：h5/h10/h20 报告列，**主口径=h10 严判**（与 P-1a 裁定准绳一致，h20 越线=留档不翻案带 snooping 折价声明）。
- fwd_ret = adj_close.shift(-h)/adj_close − 1（同 P-1a 口径）。
- **门=V1/V2/V3（bm-b r32 严口径）**：V1=|IC_mean| > max(0.02, 股票池 null p95)；V2=|IC_IR| ≥ 0.30；V3=OOS 同号且 |OOS IC_mean| ≥ 0.5×|IS IC_mean|；附 A3 期数门 n_periods≥500。
- **null=股票池口径自算（MSG-1800 令）**：K=50 白噪声因子（seed=20260923+i 连续账本），掩码=tradability 同真因子；null 线 p95 按 h 分列；null 成本=50×3h×单次 IC pass，独立 checkpoint 步。

## §5 工程与算力（O-1738 政策）

- **Stage A（R12）=一次性缓存**：bars→`Money02/data/cache/p1c_stock/`（gitignored，可再生）：主日历=全宇宙日期并集；9 字段 float32 memmap（T×N，T≈8800、N=5130→~1.6GB 磁盘）；日期 int64(µs)+syms 清单+meta.json（构建耗时/覆盖统计/校验结果）。25 workers 直写 memmap（Windows spawn 无 COW，禁大对象过管道）。
- **Stage B（R13+）=probe 先行**：3 代表因子（1 简单滚动 / 1 重滑动窗 / 1 WQ corr 类）全宇宙端到端计时 → 定 worker 数与全批 ETA；**探针不过自检不进全批**。
- **规模适配层（独立新代码，零改既有口径）**：`_wma/_max_distance/_min_distance` 在 (8700,5130) 上 sliding_window_view 物化=内存炸弹 → FIR 卷积流式化（scipy.signal.lfilter，b=权重翻转、a=1）与分块 argmax（strided view 不物化，按 256 列分块）；与既有小面板实现等价自检后才替换（R9 einsum 教训：**每个替换算子配等价门禁**）。
- worker 上限=min(25, floor(空闲RAM×0.8/单worker峰值面板内存))；probe 实测单worker峰值后定数，20% 系统保留铁律不变。
- 断点续：逐因子写 `results/shortline/p1c_partial/<factor>.json`，重跑跳过已完成；中断轮零损失。

## §6 分轮计划与骑手任务

- R12=本预注册+缓存构建+校验门（本闭环节）；R13=probe（3 因子计时）+炸板修正；R14+=全批（GTJA→WQ→null→门禁判定表）→收批报告+build_status 接线（第 12 步）另行小步。
- **骑手（MSG-1800 令顺带）**：P-4-2a 炸板判定分板修正——现实现 `((hi_pct>=9.7)|(hi_pct>=19.5))&~zt` 对 10% 板用 9.7% 阈值误高（未触板也计炸板）；修正=按板带分档（10% 板 hi_pct≥9.95 / 20% 板 ≥19.9 / 5% 板 ≥4.95）+ mood/snapshot 重算，修正前后 mood 差异留痕。独立小步，不阻塞 IC 批。

## §7 账本、预测与诚实条款（跑前写死）

- **N 记账**：缓存构建=纯数据工程 N 不变（J9a/P-4-2a 口径）；因子批测按 bm-b r32 因子账本口径记 N（+有效因子数），引擎账本不动；跑时以合并后 trials_ledger.total 为真值源基（当前双机账面 1556(bm-b)/1559(GM 会话) 竞态差由 main 集成轮收口，P-1c 以收口值为基）。
- **跑前预测（对照用）**：GTJA 反转簇在宽截面 IC 会显著强于 48 ETF 池（预判 |IC| 0.03-0.08、081 类 IR 有望过 V2）；h10 严口径三线全过幸存 0-8 个；WQ101 量价类弱于 GTJA 反转类。预测错=如实记，预注册工具链自纠（J19 范式）。
- **禁令**：禁止跑到达标为止；跑后禁调门槛禁换口径；本批不注册交易员不接线策略；IC 过线≠可交易（股票池 T+1 成本+冲击按 P-2'/B 层另算）；未来数据零容忍（因子全过去向，fwd_ret 仅入 IC 目标侧）。
- **坑预防**：J7 对齐坑族第 5 例风险（面板列名/日期 dtype 全程 date×sym 统一）；float32 缓存→IC rank 在 float64 上做（ties 语义）；PS→python 跨编码禁管道传中文；子进程 -u 防假挂起。
