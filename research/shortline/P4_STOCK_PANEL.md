# P-4②a 预注册：股票池面板构建+涨停/情绪因子批算（跑前写死 · 2026-09-23 17:50 · O-1705/1738）

> 执行者：bm-a quant 专管会话（总经理亲跑）；数据=MONEY02 bars 5222 件 parquet（已双侧 Verify 入库）。
> 性质=**纯数据/因子构建批**（同 J9a 口径：零引擎跑、零统计推断、试验账本 N 不变）；产物供 B 层策略与情绪 overlay 后续预注册消费。

## 一、输入与涨停判定（日线口径）

- 列：date/open/close/high/low/volume/amount/pct_chg/preclose/outstanding_share/turnover。
- **涨停判定**（数据驱动分板）：`pct_chg∈[9.85,10.3]`=10% 板涨停（60/00 主板）；`[19.7,20.6]`=20% 板（30 创业/68 科创）；`[4.85,5.3]`=5% 板（ST 无名单以阈值近似，记 tier 旗）；炸板=当日 high 达涨停带而 close 未达（用 pct_chg 与 (high/preclose-1) 双近似）。
- 磁盘宇宙=5222 文件（5221 股+可能的 1 件杂项，实测后如实记）。

## 二、每symbol因子（全部过去向，零未来数据）

| 因子 | 定义 |
|---|---|
| zt_count_60 | 60 日涨停次数 |
| lb_height | 当前连续涨停高度（连板 streak） |
| days_since_zt | 距最近涨停天数 |
| zt_dist | 距涨停距离（1−pct_chg/板限） |
| bias_extreme_20 | 20 日乖离深水位（close/close.shift(20)−1） |
| zt_ret_60 | 涨停日次日收益（滞后口径：最近 60 日涨停后次日 open/close 收益均值——**全部 shift(1) 过去向**） |

## 三、市场级情绪温度计（跨symbol逐日聚合，B 层 overlay 燃料）

`zt_total`（全市场涨停家数）/`zt5`（5% 板家数）/`zhanban`（炸板家数代理）/`lb_height_mean`（连板高度均值=情绪核心）/`mood_temp`（zt_total 的 60 日 z-score）——**2015 泡沫期应现涨停家数爆炸**（年代合理性锚）。

## 四、产物（体量克制）

1. `results/stock_mood_daily.csv`：全史逐日市场温度计（~8000 行）。
2. `results/stock_factors_snapshot.parquet`：每 symbol 最新快照因子（5221 行，B 层筛选输入）。
3. 完整逐symbol因子历史**不落盘**（IC 批测另行预注册、就地计算不存中间件）。
4. 全程审计：耗时/worker 数/覆盖统计入 JSON。

## 五、算力与预测（跑前）

workers=min(floor(32×0.8), 空闲GB/0.5, 25)=**25**；预估 10-30 分钟持续满载。诚实预判：宇宙≥5000 只；2015-06 前后 zt_total 应见 >500 家/日级峰；mood_temp 与 CSI300 相关为负向情绪逆指标（后验观察项非门）。
