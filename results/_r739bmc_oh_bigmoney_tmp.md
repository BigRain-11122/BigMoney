# OH-20261008-bigmoney — 创新机制研究专项轮·BigMoney 域切片（O-20261008-0650 ③ 认领窗）

- **认领行**：O-20261008-0650 ③ 九司域切片自领窗（≤10-10 12:00）——BigMoney（量化子公司）域切片=quant/金融面，认领机=bm-c（r739 轮，2026-10-08 07:0x 窗内认领+当窗交付）。
- **立项三问**：为谁而研=BigMoney 三线三判（SPM 稳定线/激进线/配置线）+研究管线（W14+ 波次/题材战法 T-173/潜力池/判决台）；仓内已有=O-20260930-1121/1132 采掘令在册池（G1/G2 矿：qlib 191+Alpha101/213+Vibe-Trading 452+paperswithbacktest 1,687+A股原生族 5 仓）+akshare 在役采集链+polars/vectorbt/pandas-ta-classic 许可门已清（OH-20260929/1005 两件）——本切片=最新趋势增量扫描非重采；判据预注册=每候选带「装在哪→判负条件→消费面」。
- **采集窗口与源分级**：2026-10-08 06:5x-07:0x；源=GitHub 官方 search API 七面（fresh_quant_finance/fresh_trading_strategy/topic:quantitative-finance/topic:backtesting/cn_market_tools/llm_finance_agent/factor_alpha_mining）+HN Algolia 两面（trading/quant finance）·零登录墙实读；星数/许可/建日=API 当场实读 ✓；功能描述=README 摘要转述（B 级·未深跑）；证据件=bigmoney `results/_r739bmc_innovation_scan.json`（轮内落盘）。本件零装机动作——全部候选态。
- **反重复门基线（三面实跑）**：①集团面=姊妹 OH 件 grep：OH-20260929-bigmoney/OH-20261005-bigmoney（polars/vectorbt/pandas-ta 族）与本窗候选零撞+OH-20261008-cph4 横切首轮（Strata/JPEG XL/AIHOT/filmcraft 族）域不交；②仓内面=bigmoney 全仓 grep（`a-stock-data|free-stockdb|TradingAgents|akquant|alphasift|daily_stock_analysis`）*.md/*.txt/*.py 零命中；③在册矿族核对=G1/G2 清单（O-20261006-1218 ②） qlib/Vibe-Trading/awesome-quant/awesome-systematic-trading=反重复命中**不重采**（判负归档）。

## 一、发现清单（域内候选·五门快评：契合/不重复/科学使用/许可/维护）

| # | 件（许可·星·建日） | 源 | 五门快评 | 判定 |
|---|---|---|---|---|
| 1 | simonlin1212/a-stock-data（Apache-2.0·10,661★·2026-05-11） | A | 契合✓A股全栈数据 87 端点/34 源（研报/舆情/打板/资金面/公告/事件驱动）／不重复🟡与 akshare 部分重叠须逐端点差集核／许可✓／维护✓push 10-07 | **候选→T-173 特征工程验证单** |
| 2 | hello245m/free-stockdb（MIT·2,802★·2026-05-08） | A | 契合✓A股日K/分钟K/ETF分钟本地引擎／不重复✓（T-104 深史回填缺口零在册解）／许可✓／维护✓push 10-04 | **候选→T-104 回填验证单** |
| 3 | simonlin1212/TradingAgents-astock（Apache-2.0·3,639★·2026-05-13）+上游 TauricResearch/TradingAgents（Apache-2.0·110,132★） | A | 契合✓A股多 Agent 投研（龙虎榜/游资/解禁适配+辩论决策）／不重复✓（T-102 游资理论道外源参照空白）／许可✓／维护✓ | **调研参照位（学实现不搬件）** |
| 4 | HiThink-Tech/Financial-API（MIT·4,111★·2026-06-09） | A | 契合✓同花顺官方数据 API（涨停/板块/LHB 族）／不重复✓（LHB 源 RC=3 隔离态候选解）／许可✓／维护🟡push 09-22 | **候选→数据缺口台账（key 物理件窗）** |
| 5 | akfamily/akquant（MIT·2,395★·2026-01-30） | A | 契合🟡Rust 高性能研究框架／重复⚠️平台重叠（own engine+science_gates 在役）／许可✓（akshare 同作者） | **parked（重叠维持）** |
| 6 | ZhuLinsen/daily_stock_analysis（MIT·66,002★·2026-01-10） | A | 契合🟡LLM 多市场分析（新闻/看板/推送）／星速 66k/9 月=超高档⚠️三验铁律前置／许可✓ | **三验队列（未验不采）** |
| 7 | TimeCopilot（MIT·619★）+Nixtla TimeGPT-2.1（NOASSERTION·4,019★） | A | 契合🟡GenAI 时序预测/时序基础模型=W14+ 新族苗观察／许可△（Nixtla 须原文验+疑似 token 依赖） | 观察位 |

**判负归档面**：qlib/Vibe-Trading（G1/G2 矿在册反重复命中）·awesome-quant/awesome-systematic-trading（在册清单源）·OpenBB/FinceptTerminal/QuantDinger（平台重叠）·hummingbot/StockSharp（域外 crypto/.NET）·pybroker（平台重叠）·TradingView-API/The-Quant-Trading-Vault（许可缺失门）·penecho/oinone（AGPL 禁入）·chengzuopeng/stock-sdk（前端域外）·Superior-Trade/trading-terminal（crypto 域外）·HN 三小件（QuantSupport/Amber/Rust-TSDB·低分观察）。

## 二、结论应用表（research-protocol §结论应用律强制·无表=未交付）

| 候选 | 装在哪/谁消费 | 落地动作 | 判负条件 | 状态 |
|---|---|---|---|---|
| a-stock-data | T-173 题材战法 R2 特征工程腿+O-20261006-1218 P4 数据缺口（研报/舆情 free 源） | 三验（ls-remote+LICENSE+release）→与 akshare 逐端点差集核→抽验 3 连后接口引用/学实现（venv 范式） | 三验不过/重复 >80% 零新增面/抽验 3 连败 | **候选** |
| free-stockdb | T-104 minute_feed 深史回填缺口（现瓶颈=sina 1m ~2000bar 前向积累律） | 三验→数据源可采性核验→ETF 分钟覆盖实证→与 in-repo 面板 overlap 校验 | 源不可采/覆盖不符/三验不过 | **候选** |
| TradingAgents-astock（+上游） | T-102 游资理论道/T-173 folk 判据数值化管线外源参照（L1 本地 qwen3.6 可承载） | 调研件：folk 判据→数值特征映射与在册框架 diff（学实现不搬件） | 方法面零增量/LLM 成本超本地红线 | **参照位** |
| HiThink Financial-API | LHB 源 RC=3 隔离态候选解+涨停池四面交叉源 | 注册 key=物理件→记数据缺口台账；key 到手后配额/限速 vs S6 节律评估 | 无 key 通道/配额不满足采集节律 | **候选（物理件窗）** |
| akquant | L1 因子普查提速线（polars cleared 姊妹参照） | 零装·Rust 引擎范式记档（pandas 瓶颈触发时与 polars 对打） | 平台重叠恒判（engine/science_gates 在役） | **parked** |
| daily_stock_analysis | 题材热度特征工程的新闻采集范式参照 | 三验铁律前置（66k 星速高档）→过则范式参照不过归档 | 三验不过 | **三验队列** |
| TimeCopilot/TimeGPT-2.1 | W14+ 新机制族苗（时序预测面） | 观察位：机制与在册族重复性+许可/依赖核验后定 | 族重复/云端 token 依赖不过 LOCAL_FIRST | **观察位** |

- **parked+理由**：akquant=平台重叠（与 vectorbt 同理由 parked）·Rust 范式记档待 pandas 瓶颈真实触发；TimeGPT=许可 NOASSERTION 未验+token 依赖疑。
- **下窗指针**：a-stock-data 三验+差集核=T-173 研究部开票面；free-stockdb=T-104 回填验证单（须先过数据源合法性）；HiThink=key 物理件入数据缺口台账（O-20261006-1218 P4 承接）。
- **回执**：本件=O-20261008-0650 ③ 认领+交付双落（bm-c r739 轮·2026-10-08 07:0x·当窗完成=认领与开动同轮律）；实搜面 9 处 API 实读 ✓；回执另落本司轮报告 r739 行+心跳——orders 本令行收取归委员会（本司禁写集团台账）。
