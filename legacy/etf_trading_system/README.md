# etf_trading_system

沪深 ETF 3-15 天日线波段交易系统 — 顶层数据与知识库。

本目录只放**地基**：标的池、数据规范、交易规则、合规边界、风控基准。
策略和回测引擎在后续步骤接入。

## 目录

```
etf_trading_system/
├── universe/                  # 标的池
│   ├── etf_universe.csv       # 47 只主流 ETF（宽基/行业/跨境/商品/债券）
│   ├── industry_map.csv       # 行业 → 代表 ETF 映射
│   └── README.md
├── data_schema/               # 数据规范
│   ├── daily_bar_schema.md    # 日线字段定义、复权、成交假设
│   └── data_sources.md        # AKShare/Tushare/券商 API 选择
└── knowledge/                 # 知识库
    ├── trading_rules.md       # 沪深交易时间、T+1、费用、涨跌停
    ├── etf_rules.md          # 折溢价、跨境 QDII、商品 ETF、T+0
    ├── compliance.md         # 合规红线、适当性、数据合规
    └── risk_baseline.md      # 持仓铁律、组合风控、成本假设
```

## 已锁定的设计决策

1. **标的**：只做 A 级流动性 ETF（日均成交额 > 5 亿），共 47 只初筛。
2. **周期**：3-15 个交易日日线波段，T 日收盘出信号，T+1 开盘成交。
3. **持仓铁律**：亏 8 天必走 / 盈 15 天必走 / 全局 15 天硬顶 / 个股 -8% 止损。
4. **成本**：双边千分之 0.8，回测必须扣除。
5. **合规**：个人研究自用，不对外荐股，不配资，不高频。

## 下一步

- [ ] 用 AKShare 把 47 只 ETF 的历史日线拉到 `data/daily/`
- [ ] 校准 `liquidity_tier` 和 `list_date`
- [ ] 接入回测引擎（参考 `../hold_period_system/` 和 `../quant_trading_system/`）
- [ ] 写第一个行业轮动 / 动量策略
