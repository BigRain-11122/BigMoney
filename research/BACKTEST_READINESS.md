# 回测全要素就绪清单（V1 · 2026-09-23 · CEO 令 O-20260923-1653）

> 「你给我把你做回测要用的所有都准备好！」——逐要素审计+证据指针；唯二在途项已明确 ETA。

| 要素 | 状态 | 证据/唯一权威指针 |
|---|---|---|
| 数据·核心池（48 ETF 日线） | ✅ 每日自动增量+新鲜度门+收盘守卫 | `scripts/update_daily.py`（smoke 每轮验数据项） |
| 数据·全史 bars（5221 A股+复权侧车 10444 件） | 🔄 传输 **75%**（BigMoney-data 通道，ETA ~17:0x） | `fleet/TRANSFER.md` + T-01 |
| 数据·25 年面板（204 只·全 regime 谱） | ✅ 2001-09 起 | `Money0923/data/daily/` |
| 数据·基准（上证/沪深300/中证500） | ✅ parquet | `Money02/data/index/` |
| 数据·专项燃料 | ✅ 龙虎榜 19 年/分钟语料/逆回购利率全史/加密 26 币 | `Money02/` + `Money0923/` 资产台账 |
| 回测引擎 | ✅ T+1/佣金 13bp/滑点/退出机/确定性（smoke 每轮 20/20 含引擎冒烟+确定性+T+1 零同日往返） | `engine/backtester.py` |
| 撮合规则与成本口径 | ✅ A股规则级 | `knowledge/market_rules.md` |
| 因子库 | ✅ 内部 27 + GTJA191 批测 harness 双机交付（宽筛池 89/严口径 0 两轨留档）+WQ101 移植排队 | `engine/factors.py` + `scripts/shortline_p1_ic.py` + `screening/gtja191_ops.py` |
| 策略库 | ✅ 8 流派 40 函数 + Money0923 35 族知识 + 3 在册交易员 | `strategies/` + `firm/traders/` |
| 质量闸门 | ✅ G1'/G2 + 零假设校准（10 步链上面板）+随机基线+试验账本 N=1312 | `research/NULL_CALIBRATION.md` + `results/*.json` |
| 纸面跟踪 | ✅ 锚定门禁+月度反造假+×2 成本安全垫 | `live/paper.py` |
| 算力 | ✅ bm-a 32 核 + bm-b 16 核（celery 分布式底座在库，P3 路线）；研究分工已裁定 | `tasks/` + `fleet/inbox/MSG-20260923-1700` |
| 观测 | ✅ build_status 数据链+dashboard+town+update_status 全绿 | `monitor/` |
| 研究环境 | ✅ 与生产隔离 | `research/shortline/requirements-research.txt` |

## 唯二在途（非缺口，是管道内件）

1. **bars 落位**：推送 75%，到仓后接收腿（clone→manifest 双侧 Verify→`Money02/data/bars`）→ T-01 done。
2. **sina 09-23 收盘 bar 源端未发布**（当日 sweep 与 paper accrual 等源，双机 8+ 次探针互证=源延迟非我方故障）。

—— bm-a quant 专管会话 · 2026-09-23 17:00
