# 日线数据 Schema

所有回测和实盘使用同一份字段规范，避免来回转换。

## 文件命名

```
data/daily/{SYMBOL}.csv
例: data/daily/510300.csv
```

## 字段（CSV，UTF-8 无 BOM）

| 字段 | 类型 | 说明 |
|---|---|---|
| date | string | YYYY-MM-DD，交易日 |
| open | float | 开盘价（元） |
| high | float | 最高价（元） |
| low | float | 最低价（元） |
| close | float | 收盘价（元，不复权） |
| volume | float | 成交量（手） |
| amount | float | 成交额（元） |
| turnover | float | 换手率（%），可选 |
| adj_factor | float | 复权因子，可选；前复权价 = close * adj_factor |

## 关键约定

1. **价格用不复权 close**。ETF 分红少但仍有，回测时统一用前复权价计算收益率。
2. **交易日对齐**：所有标的必须按沪深交易日历对齐，缺数据的日子不要补 NaN，直接剔除该日。
3. **成交量单位**：手（1 手 = 100 份 ETF）。
4. **数据起点**：每只 ETF 至少保留上市后 250 个交易日才进入回测。
5. **禁止未来函数**：
   - 信号只能用当日及以前的 close
   - 成交用次日 open（或当日 close，二选一，全系统统一）
   - 本系统统一：**T 日收盘出信号，T+1 日开盘价成交**

## 衍生指标（在回测引擎里算，不存盘）

- MA5 / MA10 / MA20 / MA60
- 20 日年化波动率
- 20 日平均成交额（流动性过滤用）
- RSI(14)
- ATR(14)
