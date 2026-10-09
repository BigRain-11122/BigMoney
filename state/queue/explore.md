# P3 新方向队列（Self-Drive v2.0·每 48h ≥1 调研件/prototype 面·O-20261009-1246 建面轮=2026-10-09 r804 bm-c）

> 派生=本司数据面先例+外源扫描方向（借力律 O-20260924-1721：外源先扫再自研·外源宣称=未验证假设）；新资产类落地=P1 级须 GM 署名（调研先行合法）。

| # | 待办 | 指针 | 状态 |
|---|---|---|---|
| E1 | 可转债 T+0 数据面可行性调研（akshare cb 源可达性+费率/回转规则·新资产类调研先行） | akshare+PLAN.md P3 | done |
| E2 | 期权 IV 面板 prereg 路线图（T-69 前向档 12 个月冻结窗计数·路线件先立） | scripts/update_options.py+T-67 §2 冻结律 | open |
| E3 | 北向资金数据源可达性扫描（akshare/东财源·情绪面因子候选） | 外源扫描两源交叉律 | open |
| E4 | 央行公开市场操作流动性指标面（OMO 净投放→REPO 利率联动·REPO_PANEL 消费） | research/shortline/REPO_PANEL.md | open |
| E5 | LHB 游资情绪因子形式化（情绪周期三轴门先例扩展·O-20260928-1522 国内打法优先律） | scripts/update_lhb.py+firm/RULES.md | open |
| E6 | 微盘股量化因子外源扫描（韭研/雪球/研报三源·小市值效应本土化） | 外源扫描+独立验证门禁链 | open |
| E7 | 行业轮动 ETF 网格族候选（core48 外行业 ETF 扩展·grid 族先例） | grid_paper.py 族先例 | open |
| E8 | 商品期货跨期价差监控面（9 品种主力连续面板消费·近远月价差序列化） | scripts/update_futures.py | open |
| E9 | 港股通 AH 折溢价均值回归深化（AH panel 消费面·T-17 后续候选） | scripts/ah_panel_puller.py | open |
| E10 | 涨停梯队接力打法数据面（zt_pool 四面联动·连板梯队生存分析） | scripts/update_zt_pool.py | open |
| E11 | 融资融券余额情绪面调研（margin 余额序列→短线情绪门候选） | 外源扫描 | open |
| E12 | 逆回购月末利率脉冲策略化（GC001 节前尖峰实证 53.44→现金腿择时门候选） | scripts/update_repo.py | open |

> r821 消耗记录（bm-b）：E1 本轮完成出列（**可转债 T+0 数据面可行性调研**：探针 `scripts/cb_data_probe.py`〔45s 超时夹克+2.5s 限速+零面板写+selftest 9/9〕+证据 `results/cb_data_probe.json`+调研件 `research/shortline/CB_T0_DATA_FEASIBILITY.md`；测量结论=日线级可行性成立〔sina spot 326 员宇宙+单券深史 1368~1433 bar≈5.5 年+活券尾=最新交易日 2026-10-09+日线×快照交叉验证 absdiff=0.0〕、分钟级源缺口〔sina min 活券上复测仍败=端点面〕、EM 两活一死〔bond_zh_cov 1059/bond_zh_cov_value_analysis 1380 活；bond_cov_comparison 二连败持久〕、JSL 强赎面免 token 318 行；T+0/±20%/适当性/费率规则面=置信标注+权威核验待做；落地门槛清单 5 项全未满足〔GM P1 票+T-67 12 个月前向窗+宇宙活性过滤+分钟源解决+独立成本假设〕；**零 prereg 零面板零回测纯调研**）。P3 队列 12→11（E2 队头）。
