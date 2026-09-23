# 策略流派库

8 大流派，覆盖 A 股常见交易风格。每个函数输入 OHLCV，输出仓位信号（0/1）或权重矩阵。

## 流派清单

### 1. 趋势跟踪流 `trend.py`
| 函数 | 逻辑 | 适用 |
|---|---|---|
| `donchian_breakout` | 20 日新高买入，10 日新低卖出（海龟） | 趋势市 |
| `dual_ma_cross` | MA5/MA20 金叉 | 所有市 |
| `triple_ma` | MA5>MA20>MA60 多头排列 | 强趋势 |
| `parabolic_sar` | PSAR 转向 | 趋势跟踪 |
| `supertrend` | Supertrend 指标 | 趋势跟踪 |

### 2. 均值回归流 `mean_reversion.py`
| 函数 | 逻辑 | 适用 |
|---|---|---|
| `bollinger_breakout` | 跌破布林下轨买入 | 震荡市 |
| `rsi_revert` | RSI<30 买入，>70 卖出 | 震荡市 |
| `zscore_revert` | z-score<-2 买入 | 震荡市 |
| `pullback_bounce` | 上升趋势中回调 5% 买入 | 牛市回调 |
| `rsi2` | Connors RSI-2<10（极短） | 超短反弹 |

### 3. 动量轮动流 `momentum.py`
| 函数 | 逻辑 | 适用 |
|---|---|---|
| `cross_sectional_momentum` | 选过去 120 日最强 5 只（skip 20 日） | 月频 |
| `dual_momentum` | 相对动量 + 绝对动量过滤 | 月频 |
| `time_series_momentum` | 价格 > MA200 | 长牛 |
| `relative_strength_rotation` | 相对沪深300 强弱 | 行业轮动 |
| `momentum_acceleration` | 快动量 > 慢动量 | 趋势加速 |

### 4. 波动率流 `volatility.py`
| 函数 | 逻辑 | 适用 |
|---|---|---|
| `low_vol_long` | 选波动率最低 5 只 | 全时段 |
| `vol_target` | 仓位 = 15%/实际波动 | 风控 |
| `vol_breakout` | 波动率从低位扩张 | 趋势启动 |
| `vol_regime_switch` | 低波+趋势才持仓 | 熊市保护 |

### 5. 情绪/资金流 `sentiment.py`
| 函数 | 逻辑 | 适用 |
|---|---|---|
| `turnover_surge` | 成交量 > 2 倍均量 | 放量突破 |
| `amount_rank` | 选成交额最大 10 只 | 机构关注 |
| `price_volume_trend` | 价涨 + 量涨 | 趋势确认 |
| `intraday_momentum` | 日内收益持续为正 | 日内 |
| `overnight_drift` | 隔夜收益漂移 | A 股 T+0 |

### 6. 日历/季节流 `seasonal.py`
| 函数 | 逻辑 | 适用 |
|---|---|---|
| `month_seasonality` | 指定月份持仓 | 日历效应 |
| `month_end_effect` | 月末 3 天 | 月末效应 |
| `weekday_effect` | 指定星期几持仓 | 周内效应 |
| `holiday_effect` | 春节/国庆前后 | 假期效应 |
| `trend_by_season` | 季节过滤+趋势 | 组合 |

### 7. 宏观/市场状态流 `macro.py`
| 函数 | 逻辑 | 作用 |
|---|---|---|
| `csi300_trend_filter` | 沪深300 > MA200 才开仓 | 牛熊过滤 |
| `csi300_momentum_filter` | 沪深300 60 日动量为正 | 中期过滤 |
| `volatility_regime_filter` | 市场波动率低于中位数 | 平静期 |
| `drawdown_filter` | 大盘回撤<15% 才开仓 | 熊市空仓 |

### 8. 事件/缺口流 `event.py`
| 函数 | 逻辑 | 适用 |
|---|---|---|
| `gap_fill` | 隔夜跳空 -1% 且收盘收回 | 恐慌反转 |
| `breakout_confirm` | 突破新高 + 放量 | 趋势启动 |
| `double_bottom` | 双底形态 | 底部反转 |

## 使用方式

```python
from strategies import trend, momentum, macro

# 单标的信号
sig = trend.donchian_breakout(close, high, low)

# 横截面轮动
weights = momentum.cross_sectional_momentum(close_panel, n=120, top_k=5)

# 加宏观过滤
risk_on = macro.csi300_trend_filter(close_panel, csi300_close)
weights = weights.mul(risk_on, axis=0)
```

## 没建的流派（数据缺口）

- **打板流**：ETF 很少一字涨停，不直接适用。要用得切到个股。
- **舆情/新闻流**：需要新闻/NLP 数据源（东财股吧、微博、雪球），未接。
- **套利流**：需要 ETF 申赎清单 + 一二级市场价差数据。
- **资金流**：需要北向资金、主力资金流数据（akshare 接口部分挂了）。
- **价值流**：ETF 没有 PE/PB 估值因子（红利 ETF 可以近似）。
