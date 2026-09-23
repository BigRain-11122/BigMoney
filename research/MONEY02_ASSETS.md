# Money02 资产清单与教训（前代系统）

> 2026-09-23 AI 接管整理。Money02 = 前代「A股短线量化交易系统」（原 E:\Money，2026-09-22 深夜整体迁入本仓库）。
> **旧自动化已全线停用**（用户令）：计划任务 MoneyQuantTick / MoneyQuantCryptoTick / MoneyQuantDaily 已禁用，不再执行。恢复：`schtasks /change /tn "\MoneyQuantTick" /enable`（三个同理）。
> Money02 以「资产库 + 设计参考」身份保留：全部代码、数据、研究产物均在 `Money02/` 原位，未拆散、未改名，保证内部引用与历史档案可溯。

## 一、数据资产（约 7.7 GB，最有价值，重下成本极高）

| 路径 | 内容 |
|---|---|
| `Money02/data/bars/` | 5221 只 A 股全史日线 parquet（1991-01→2026-09，全量回填 5221/5221 err=0）+ 新浪复权因子侧车 `{code}.factor.json`（10444 文件） |
| `Money02/data/index/` | 上证综指 / 沪深300 / 中证500 指数日线 |
| `Money02/data/cache/` | 引擎面板 npy（~60 字段：OHLCV + ma/rsi/adx/macd/cci/stoch/mfi 等 TA-Lib 块 + lhb_net + 涨跌停/可交易闸） |
| `Money02/data/lhb/` | 龙虎榜 265,831 行 × 19 年（2007-2026，净买额/换手/上榜原因；**后N日列为前视数据，永不读**） |
| `Money02/data/live/` | 全市场实时快照（5221 只，24h 滚动），qt.gtimg.cn 批量报价 7.5s 拉全市场 |
| `Money02/data/mkt_crypto/` | Gate.io 26 币日 K 全史（BTC 2015 起；Gate.io 是唯一实测可用的境内加密源） |
| `Money02/results/`、`results_crypto/` | 联赛 211 轮档案、名人堂 top12、冠军报告、fit_matrix（93候选×双市场）、模拟盘账本（100 万虚拟本金，2026-09-21 开张） |

## 二、设计资产（代码即文档，均实战跑通过）

- **data.py 免V8多源数据层**：个股=腾讯裸价 × 新浪复权因子（语义 qfq=raw÷F(t)，因子侧车检测重锚）；当日增量=qt.gtimg 实时报价（字段实证映射）；指数=腾讯 fqkline。坑录：腾讯qfq个股数据损坏勿用；baostock/东财本机 IP 被封。
- **strategies.py 31 策略基因家族**：8 原型（放量突破/首板/超跌/趋势回调/小盘动量/RPS/N字反包/量价起爆）+ 18 细分 + 12 融合 + lhb 龙虎榜聪明钱；**选择性计算**（只算有权重家族）+ **字段休眠闸**（面板缺字段零掩码不崩）。
- **evolve.py**：GA（pop40/elite4）+ 滚动 walk-forward（480 训练→60 盲测）+ 五门派互斥联赛（同窗同预算盲测、实盘超额加权夺权、零假设随机基因组基线）+ 基因组历史代语义重映射（61/119/181→186 维跨代迁移不断链）+ 断池自愈降级。
- **backtest.py**：A股真实规则（T+1、信号收盘→次日开盘成交、涨跌停禁买卖、佣金印花税滑点、5% 容量、整手、MIN_HOLD_DAYS=3）。
- **质量栈**：anti_cheat 四道机械审计（成交重放/指标因果/复权真值/幸存者披露）、certify 六道出厂门禁（含 G2 非重叠窗改造）、review 九道自检、verify_data/preflight_data。
- **markets.py**：10 市场规则注册表（cn/crypto/us/hk/jp/eu/fx/commodity/kr/tw：涨跌停/T+1/费率/日历），多市场=环境变量切 cache/results 目录。
- **运维范式**：pythonw+CREATE_NO_WINDOW 全静默、PID 锁+看门狗+超时自愈、BOM 感知日志读取（PS5.1 重定向=UTF-16LE 坑）、验证任务真跑看产物文件而非 LastResult=0。

## 三、核心教训（诚实结论，Bigmoney 必须继承）

1. **34 年盲测全毁**：GA 进化架构 34 年 walk-forward 盲测 **-97.8% / 夏普 -0.82 / 回撤 -97.9%**——A 股短线 GA 未找到能覆盖真实成本的可迁移优势。→ Bigmoney 纪律：**先证因子/策略真有效（IC + 非重叠样本外 + 防过拟合），再谈进化与加杠杆**。
2. **跨市场迁移首胜**：A 股基因组原样盲跑加密 480 日 **+37.3%（vs BTC -17.3%，超额 +54.6pp）**——价格量信号栈市场无关，crypto 值得作为第二市场候选。
3. **无全市场真 alpha**：fit_matrix 93 候选 × cn+crypto 双市场，无任何策略同时正超额（最适：crypto=confluence，cn=wrrev）。
4. **统计纪律**：多重检验需零假设基线与 deflated Sharpe；冠军主张必须可证伪；短窗选择≠长期生存。
5. 反作弊/门禁/盲测方法论 = 可整体移植到 Bigmoney 实盘前验证闸。

## 四、Bigmoney 复用路径

- 数据：A股个股/指数/龙虎榜可按需补 Bigmoney 数据缺口（Bigmoney 主战场=ETF，个股数据留作扩展弹药）。
- 规则：backtest 成交细节（涨跌停禁买/容量/整手）与 anti_cheat 审计思路移植到 engine/live 的验证闸。
- 扩展：未来上港股/美股/加密时复用 markets.py 规则档案设计 + Money02 的数据源探测结论（见其 CODELY.md）。
- 历史：Money02/CODELY.md = 用户全部历史指令与决策记录（只读档案）。
