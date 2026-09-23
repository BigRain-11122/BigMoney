# 数据源说明

## 推荐数据源（按优先级）

| 数据源 | 类型 | 频率 | 优点 | 注意 |
|---|---|---|---|---|
| AKShare | 免费开源 | 日线 | 无需 token，覆盖全市场 ETF | 接口可能随上游变动，需要定期测活 |
| Tushare Pro | 积分制 | 日线 | 数据稳定，字段规范 | 需要 token，高频接口需积分 |
| 聚宽/米筐 | 付费 | 日线/tick | 专业级，含复权 | 有费用 |
| 券商 API | 实时 | tick/日线 | 实盘同源 | 需券商开通 |

## 落地建议

**研究/回测阶段**：先用 AKShare 拉历史日线，落盘到 `data/daily/{SYMBOL}.csv`。
**实盘阶段**：用券商 API（如 QMT/Ptrade）取实时价，历史数据仍用 AKShare/Tushare。

## 拉数脚本接口约定

```
fetch_daily(symbol: str, start: str, end: str) -> List[Bar]
```

返回字段必须严格符合 `daily_bar_schema.md`。新增数据源时只需实现这个接口。

## 数据校验（每次拉数后跑）

- [ ] 行数 = 该区间交易日数 ± 1
- [ ] close ∈ [low, high]
- [ ] open ∈ [low, high]
- [ ] volume ≥ 0
- [ ] 无重复日期
- [ ] 无跳空超过 ±11%（ETF 涨跌停限制，异常值需人工核查）
