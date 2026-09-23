# 短线作战总纲 SHORTLINE PLAYBOOK（V1 · 2026-09-23 · CEO 令 O-20260923-1545）

> 研究部主文件。定位：把「做短线」的全量策略族/因子/指标/资料**收拢成可执行地图**——内部已有什么、外部补什么、怎么按门禁采纳。
> 纪律：生产采纳一律走 G1'/G2（PLAN §4.2 质量闸门+§4.3 反过拟合）；新市场/新数据源=P1 总经理署名制（O-20260923-1620 下放，实盘/红线/使命/重大资源仍归 CEO）；交易红线零触碰。

## §0 公司口径

- 短线 = **3-15 交易日日线波段**（`firm/risk/iron_rules.md` 口径不变）。
- 主战场 = 沪深 ETF；股票/期货能力启用=**总经理已批**（O-20260923-1620·CEO 下放非重大自决权，paper 域）；期权=暂不批（杠杆复杂，后续单独立项）。

## §1 策略族全景图

### 1.1 内部在库（生产资产）

| 库 | 覆盖 | 指针 |
|---|---|---|
| BigMoney 8 流派 40 策略函数 | 趋势/均值回归/动量轮动/波动率/情绪资金/日历/宏观过滤/事件缺口 | `strategies/README.md` |
| BigMoney 3 交易员 | COMPOSITE-CE-01/02·VOLATILITY-CE-01（复合+波动，EW 组合 OOS Sharpe 1.73） | `firm/traders/` |
| Money0923 前代 35 族 | 8 经典出处族 + 涨停系/缺口/尾盘/网格/RSRS/小市值/52 周高点/残差动量/Amihud/随机对照组/gamble 等 | `Money0923/quant/strategies.py` + 其 `SYSTEM_AUDIT.md` §4 |
| 因子引擎 27 因子 | 动量/反转/波动/流动性/趋势/隔夜分解/偏度峰态/微观结构 | `engine/factors.py` |

### 1.2 缺口分析（strategies/README 已自陈 + Money0923 已备知识）

| 短线族 | 知识状态 | 生产采纳路径 |
|---|---|---|
| 尾盘强势 `strong_close` | Money0923 已备 | **A 层：ETF 可用**——骨架迁入→门禁 |
| 网格收割 `grid_trade` | Money0923 已备（sane +27.7%） | A 层（震荡市 ETF） |
| RSRS 择时叠加 | Money0923 已备（光大研报族） | A 层（时序择时，横截面无关） |
| 残差动量 `resid_mom` / 相关滞涨 `pair_lag` / 52 周高点 `high_52` / 连阳 `streak` / 放量突破 `vol_break` | Money0923 已备 | A 层 |
| 打板系 `limitup_mom`/`dragon_head`/`ban_open`/跌停反核/小市值反转/次新 | Money0923 已备 | **B 层：总经理已批（O-20260923-1620）**——需股票池+涨跌停撮合+负面清单（`Money0923/quant/fundamental.py`），A 层批测后排期开工 |
| 期货 CTA `cta_trend` | Money0923 已备（自服务架构） | **C 层：总经理已批（同上），B 层后排期** |
| 舆情/NLP、资金流（北向/主力） | 数据源缺口 | **总经理已批修复立项（O-20260923-1620）**——北向 2024-08 后停实时披露走替代口径；舆情 NLP 数据源后议 |
| ETF 套利（申赎价差） | 需申赎清单数据 | 数据源缺口，暂不立 |
| 价值流（红利 ETF 近似） | 低优 | 备案 |

### 1.3 采纳分层纪律

- **A 层（ETF 域）**：研究部自主域——迁骨架→`smoke`→G1'/G2→注册候选交易员（走 `firm/review/promotion.md` 入职标准）。
- **B 层（股票池）**：**总经理已批（O-20260923-1620）**——A 层批测后开工，全链照走门禁+负面清单。
- **C 层（期货）**：总经理已批，B 层后排期；期权不批。

## §2 因子库全景

### 2.1 已备

- 内部 27 因子（`engine/factors.py`，宽面板 date×symbol 口径）+ 复合因子方法论（`research/COMPOSITE_FACTOR.md`、`FACTOR_RESEARCH.md`）。
- **GTJA 191**：已下载全套（`external/gtja191_*.py`，宽面板同构）——短周期价量因子经典全集。
- **WorldQuant 101**：已下载 MIT 实现（`external/worldquant101_*.py`，Polars 公式参照，平均持仓 0.6-6.4 天）。

### 2.2 适配要点（研究部执行注意）

1. **口径差**：101/191 为**个股**横截面设计；我方 ETF 池窄（数十只）→ **RANK 类横截面因子统计力弱，优先时序类因子**；101 中依赖 `cap`（市值）的 alpha 子集在 ETF 域不适用，先筛「无 cap 依赖」子集。
2. **价量字段**：GTJA191 需 OHLCV+amount——bars parquet 全有 ✓；个别因子需指数/benchmark（`data/index/` 有上证/沪深300/中证500）。
3. **A股规则**：qfq 复权、涨跌停、T+1 已在撮合层（`knowledge/market_rules.md`）；因子层无需重造。
4. **qlib 依赖**：191 中 ~10 个回归类因子可选 qlib rolling ops——缺则降级，不必装 qlib 整框架。

### 2.3 采纳管线（研究部 SOP）

```
因子子集批测 IC（screening/，ETF 池全史）→ 有效因子池报告（research/shortline/）
→ 合成（COMPOSITE_FACTOR.md 方法）→ 新策略骨架 → smoke → G1'/G2 → 候选交易员
```

- 反过拟合铁律照走：样本内外严格切分、参数≤5、季度漂移警报（PLAN §4.3）。
- gamble 随机对照组纪律（Money0923 可学清单 §三-6）：一切新因子/策略须跑赢随机基线才配谈超额。

## §3 指标库

- **生产口径**：内部向量化指标集（`engine/factors.py` + `Money0923/quant/indicators.py`：MA/RSI/MACD/KDJ/布林/ATR 等核心）——零外部依赖。
- **研究环境**：`pip install ta`（43 指标·MIT·纯 pandas；见 `requirements-research.txt`）。pandas-ta 原仓库已 404 不引入；TA-Lib C 依赖不装。

## §4 数据资产清单（短线燃料）

| 资产 | 状态 | 指针 |
|---|---|---|
| ETF/股票日线 bars（10444 件 parquet） | 传输中（BigMoney-data 仓，A-变体推送在途） | `fleet/TRANSFER.md` |
| 25 年日线面板（204 只全 regime 谱） | **已在库** | `Money0923/data/daily/` |
| 分钟语料（不可再生） | 已在库 | `Money0923/data/minute_store/` |
| 龙虎榜 19 年（265,831 行） | 已在库 | `Money02/data/lhb/`（B 层燃料） |
| 指数日线（上证/沪深300/中证500） | 已在库 | `Money02/data/index/` |
| 加密 26 币全史 | 已在库 | `Money02/data/mkt_crypto/` |
| 逆回购利率 2013→今 | 已在库 | `Money0923/data/repo_daily.csv` |
| akshare 扩展源（融资融券/ETF 份额/申赎清单） | 按需 | 已知坑：全部入口 20s 超时纪律；159xxx 深市源限流；北向实时披露 2024-08 已停 |

## §5 资料与外部资产

- 台账：`external/SOURCES.md`（件件带出处+许可）。
- 本文件即总目录；周进化轮维护更新（研究部 mandate，`firm/org_chart.md` v2）。

## §6 采纳路线（研究部排期）

| 期 | 内容 | 权级 |
|---|---|---|
| **P-1 因子批测** | GTJA191 时序类子集 + 101 无 cap 子集 → ETF 池全史 IC 批测 → 有效因子池报告 | 研究部自主域（T2） |
| **P-2 合成上线** | 有效因子合成→骨架→G1'/G2→注册候选交易员；A 层策略族（尾盘/网格/RSRS 叠加等）迁骨架过闸 | 研究部自主域 |
| **P-3 已批开工** | 股票池策略族启用（打板/小市值+负面清单）/ 资金流源修复 / 期货 CTA | **总经理已署名（O-20260923-1620）**——排期 A/B 后 |
| **P-4 风格动物园分批实现**（O-20260923-1705） | 按 `ASTYLE_ZOO.md` 三批次：①A 层易族（超跌反弹/深水锚定/定投式/换手异动）②M0923 迁族（打板四族+次新+网格+情绪周期 overlay+龙虎榜跟风——lhb 数据在库）③死扛族 spec（补仓摊薄引擎支持评估）——开工前 inbox 认领，走门禁链 | 研究部自主域（B 层照 O-1620 批件） |

## §7 维护

- 周进化轮（研究部）复核本文件；新外部资产必须入 `external/` + `SOURCES.md` 登记；失效资产清出台账。
