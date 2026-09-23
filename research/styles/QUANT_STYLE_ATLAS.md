# 量化全风格图鉴 QUANT STYLE ATLAS（V1 · 2026-09-23 · O-20260923-1636 首场全风格调研）

> 研究部主文件。全风格×现状×评级地图；短线细节见 `research/shortline/SHORTLINE_PLAYBOOK.md`。
> 评级口径：**A**=ETF 日线域即用（研究部自主过闸）· **B**=已批域开工（股票池/期货 paper 域，O-1620）· **C**=需数据源/基础设施立项 · **D**=知识储备暂不立。

| # | 风格 | 代表方法/文献 | 我方现状 | 外部参照 | 评级 | 下一步 |
|---|---|---|---|---|---|---|
| 1 | 趋势跟踪/CTA | 海龟 Donchian、Supertrend、PSAR | `strategies/trend.py` 5 函数；Money0923 `cta_trend` 期货自服务架构 | 经典公开（海龟法则） | **A**（ETF）/B（期货已批） | A 层骨架已备；期货走 B 排期 |
| 2 | 动量（横截面/时序） | Jegadeesh-Titman 1993、Antonacci 双动量、12-1 | `strategies/momentum.py` 5 函数 | 经典公开 | **A** | 在册交易员复合体主力 |
| 3 | 均值回归/反转 | Connors RSI2、布林 Z 分数 | `strategies/mean_reversion.py` 5 函数 | 经典公开 | **A** | 已有 |
| 4 | 波动率 | 低波异象 Baker-Haugen、vol target、vol regime 切换 | `strategies/volatility.py` 4 函数；低波冠军历史战绩 | Money0923 low_vol 223 局 79% 正收益 | **A** | 已有 |
| 5 | 轮动（行业/风格/大小盘） | 二八轮动、ETF 动量轮动 | `strategies/composite_rotation.py`；Money0923 rotation_28/sector_momentum | 光大 RSRS 时序择时（Money0923 已备） | **A** | RSRS 叠加入 A 层队列 |
| 6 | 多因子选股 | GTJA191、WorldQuant 101、Fama-French | `engine/factors.py` 27 因子+合成方法论 | **external/ 已入库 292 因子全套**（O-1545） | **A**（ETF 批测）/B（股票池） | P-1 批测已排（playbook §6） |
| 7 | 打板/涨停族（A 股特有） | 涨停动量、龙头战法、炸板回封、跌停反核 | Money0923 4 族全备+**龙虎榜 19 年在库** | 内部归档=权威 | **B**（已批） | A 层批测后开工 |
| 8 | 网格收割 | 区间网格 | Money0923 `grid_trade`（sane +27.7%/回撤 -7.7%） | 内部归档 | **A** | 骨架迁入过闸 |
| 9 | 统计套利/配对 | Gatev 1999 协整配对、Kalman filter | `pair_lag` 相关滞涨雏形 | `stock-pairs-trading` 库（10mohi6·MIT·pip 可装·含协整/回测用例） | **A-**（ETF 相关对可行） | 专项：ETF 高相关对协整研究→门禁 |
| 10 | 事件驱动 | 指数调仓、年报、分红 | 无事件数据源 | — | **C** | 数据源立项后开工 |
| 11 | 日历/季节 | 月末效应、星期效应、假日效应 | `strategies/seasonal.py` 5 函数 | 经典公开 | **A** | 已有 |
| 12 | ML/DL 预测 | LightGBM、LSTM/Transformer、HIST/TRA | Money0923 遗留 LightGBM IC≈0.17 线索；J13 本地 LLM 载体已上线 | **qlib**：Alpha158/360+22 模型 zoo+DDG-DA 漂移适应（MIT） | **C**（P2 AI 大脑路线图） | Optuna→P2 排期；qlib 按需取件不整框架 |
| 13 | 高频/做市 | Avellaneda-Stoikov | 需 tick/订单簿 | — | **D** | 知识储备（分钟语料已在库） |
| 14 | 市场中性 | 多空中性 | A 股融券受限 | — | **D** | 知识储备 |
| 15 | 风险平价/资产配置 | 现金管理+股债金 ETF | **逆回购利率全史在库**（repo_daily 2013→今） | Money0923 repo.py 三端一致设计 | **A** | 现金腿方案入研究队列 |
| 16 | 宏观/市场状态 | 大盘趋势过滤、波动分位、宽度 | `strategies/macro.py` 4 函数 | Money0923 regime 引擎（风格识别） | **A** | regime 精度提升项 |
| 17 | 资金流/情绪 | 北向/主力/换手 | 数据源缺口（北向 2024-08 停实时披露） | akshare 替代口径 | **B**（修复立项已批） | 替代源专项调研=下场外调队首 |
| 18 | 期权波动率 | 波动率曲面 | 期权**不批**（O-1620） | — | **D** | 知识储备 |
| 19 | 加密 | 趋势/轮动迁移 | **mkt_crypto 26 币全史在库** | Money02 归档 | **D** | 数据在库，单独立项再议 |
| 20 | 套利（ETF 申赎/期现/折溢价） | 一二级价差 | 需申赎清单/期货实盘 | — | **C/D** | 数据源缺口 |

## 维护

- 外调轮（`research/RESEARCH_MECHANISM.md`）每场复核本表：评级升降、新风格入行、失效行清出。
- 首场纪要：`research/digests/DIGEST-20260923-styles-sweep.md`。
