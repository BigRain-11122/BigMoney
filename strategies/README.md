# 策略流派库

11 大流派，覆盖 A 股常见交易风格+民间手法。每个函数输入 OHLCV，输出仓位信号（0/1）或权重矩阵。

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

### 9. 技术分析经典流 `ta.py`（P-4 批 2A · CEO 令 O-20260923-1828；+排队批 5 函数 O-20260923-2210）
M0923 迁族 6 + 经典 K 线形态 2 + 排队批经典振荡/收缩系 5；语义/参数冻结见 `research/shortline/P4_BATCH2A.md`+`P4_QUEUE.md` 预注册。
| 函数 | 逻辑 | 出处 |
|---|---|---|
| `strong_close` | 收盘位于日内区间顶部≥0.85+放量 1.5×+收阳→持有，日内位置跌回 0.5 离场 | M0923 尾盘强势 |
| `macd_trend` | DIF>DEA 金叉态且 DIF>0 零轴确认（12/26/9） | Appel·MACD |
| `kdj_reversal` | KDJ 的 J<0 超卖+价格在 MA60 上，J>80 离场（9/0/80/60） | 中国市场经典 |
| `rsrs_timing` | 18 日 high~low 回归斜率 β 滚动 z（250 窗）>0.8 持有、<−0.8 清仓 | 光大 2017·RSRS |
| `streak_up` | 连续 3 日收阳接力，断阳离场 | M0923 连阳 |
| `vol_breakout` | close 破前 20 日 high+量≥1.5×均量，破前 10 日 low 离场 | M0923 放量突破 |
| `hammer_reversal` | 锤子线（小实体+下影≥2×实体+近无上影）+5 日跌≥5% 语境，收回 MA20 离场 | K 线形态新设计 |
| `engulf_reversal` | 阳包阴（阳线实体吞没前阴实体）+5 日跌≥5% 语境，收回 MA20 离场 | K 线形态新设计 |
| `cci_revert` | CCI<−100 超卖+MA60 趋势上，CCI>+100 离场（20） | 经典 CCI（排队批） |
| `williams_reversal` | 威廉 %R<−80+收阳日入场，%R>−20 离场（14） | 经典 %R（排队批） |
| `nr7_breakout` | 前 bar 7 日最窄幅+今收破其高；破其低离场 | 经典 NR7（排队批） |
| `bb_squeeze_breakout` | 布林带宽 60 日最低（收缩）+收破上轨；跌破中轨离场 | 经典挤压突破（排队批） |
| `rsi_divergence` | 价 30 日新低而 RSI 高于其 60 日低点+5（MACD 背离同族折扣披露） | 经典 RSI 背离（排队批） |

### 10. K 线形态流 `patterns.py`（P-4 民间大扩容 · CEO 令 O-20260923-2134）
经典+民间 K 线/均线结构形态；反转类离场=收回 MA20、延续类离场=跌破 MA10（批 2A 范式）。语义/参数冻结见 `research/shortline/P4_FOLK_EXPANSION.md` 预注册。
| 函数 | 逻辑 | 出处 |
|---|---|---|
| `morning_star` | 大阴+小实体+深入阴体阳线三日反转 | Wikipedia 晨星 |
| `three_soldiers` | 三连阳实体递增续势 | Wikipedia 红三兵 |
| `piercing_line` | 跳空低开+收盘深入前阴实体上半 | Wikipedia 曙光初现 |
| `needle_probe` | 长下影深水针+次日收复针高点确认（锤子近族） | 民间金针探底 |
| `three_methods_up` | 大阳+三小回调内包+再阳破前高 | 经典上升三法 |
| `island_reversal` | 下跳空+上跳空留孤岛底 | 经典岛形反转 |
| `doji_at_low` | 深水后十字星止跌 | 民间低位十字星 |
| `big_yin_shakeout` | 上升途中大阴次日收复=洗盘完成 | 民间大阴洗盘 |
| `macd_divergence` | 价 30 日新低而 DIF 不创新低 | 民间 MACD 底背离 |
| `obv_divergence` | 价新低而 OBV 强于 60 日均值=吸筹 | 民间 OBV 背离 |
| `vol_drought_reversal` | 60 日极缩量+深水+首阳 | 民间「地量出地价」 |
| `inside_bar_breakup` | 内包母子线后向上破母线高 | 经典内包突破 |
| `yang_break_3ma` | 三线粘合后单阳穿 MA5/10/20 | 民间一阳穿三线 |
| `ma_converge_break` | 三线粘合后 MA5>MA10>MA20 多头堆叠状态 | 民间均线粘合 |
| `duck_head` | MA5 缩头下穿 MA10 后回穿（MA60 上） | 民间老鸭头 |
| `box_breakout` | 20 日窄箱体上沿突破+量确认（近族 vol_breakout） | 民间平台突破 |
| `immortal_guide` | 长上影试探+3 日内收复上影高点 | 民间仙人指路 |
| `n_shape` | 涨-回调-N 形过前高 | 民间 N 字反包 |

### 11. 民间手法流 `folk.py`（P-4 民间大扩容 · CEO 令 O-20260923-2134）
民间谚语/手法 ETF 日线域版；全冻结参数，有效性由门禁裁决（zoo §十二）。
| 函数 | 逻辑 | 出处 |
|---|---|---|
| `low_suction` | 上升趋势回踩 20 日线缩量企稳 | 「低吸富三代」（近族 pullback_bounce） |
| `lian_yin_first_yang` | ≥3 连阴后首阳博反弹 | 民间连阴首阳 |
| `false_break_back` | 破 60 日线 1-3 日内收回=假摔 | 民间假摔洗盘 |
| `ants_climb` | 6 日内 5 小阳慢爬=吸筹 | 民间蚂蚁上树 |
| `volume_mound` | 5 日均量 1.3×60 日均量+价格缓升 | 民间量堆吸筹 |
| `second_wave` | 前高回踩不破再起 | 民间二波确认 |
| `gap_up_hold` | 上跳空缺口不回补持有 | 民间跳空不补 |
| `rsi_low_flat` | RSI<25 钝化+价格两日不再新低 | 民间超卖钝化 |

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
