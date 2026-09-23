# A股短线量化交易系统（E:\Money）

自动化、自我进化的 A 股短线交易研究与模拟盘系统。**100 万虚拟本金**、滚动样本外（walk-forward）验证、A股真实规则（T+1、涨跌停、佣金印花税滑点、流动性容量）。**10 分钟一轮自我进化 tick**（盘中只深化不碰数据；收盘后自动全周期）。

## 结构
| 文件 | 职责 |
|---|---|
| `config.py` | 全局参数（本金/费率/进化规模/股票池规则） |
| `data.py` | 免V8多源数据层（TX裸价×新浪复权因子 + qt实时报价 + 腾讯指数）+ (T,N) 面板矩阵 |
| `indicators.py` | 向量化指标 |
| `strategies.py` | **8 个策略基因家族**：放量突破/首板接力/超跌反弹/趋势回调/小盘动量/RPS相对强度(欧奈尔系)/N字反包/量价起爆 |
| `regime.py` | 市场状态识别（多头/震荡/急跌/修复）→ 风格自适应权重 |
| `backtest.py` | A股规则组合回测器 + 适应度 |
| `evolve.py` | GA进化 + 滚动 walk-forward（多进程并行）+ 10分钟深化模式 |
| `report.py` | 样本外报告/净值图/次日信号 |
| `run_daily.py` | 全周期闭环：更新数据→模拟盘执行→进化→报告→信号 |
| `run_tick.py` | **10分钟tick**：盘中只深化（GA代数推进），收盘后新数据自动触发全周期 |
| `loop.ps1` / `run_once.ps1` | 循环/OS任务入口（MoneyQuantTick 每10分钟） |
| `smoke.py` | 端到端冒烟（隔离小样本） |
| `test_refresh.py` / `verify_data.py` | 数据增量精度回归 / 数据质量验证 |

## 运行
```powershell
python run_daily.py        # 手动全周期（幂等）
python run_tick.py         # 单次10分钟tick（进化深化+按需全周期）
powershell loop.ps1        # 手动持续循环模式
python smoke.py            # 端到端冒烟测试
```
OS 计划任务 `MoneyQuantTick` 已注册：每 10 分钟自动 tick（删除：`Unregister-ScheduledTask MoneyQuantTick`）。

## 产出
- `results/<日期>/report.md` + `equity.png`：样本外验证报告（与沪深300/中证500对比）
- `results/latest/`：最新报告与信号
- `results/signals.json`：次日买入候选（模拟盘自动执行）
- `results/paper.json`：100万模拟盘持仓与净值历史
- `results/live_genome.json`：当前活体基因组（tick 持续深化）
- `results/history.jsonl` / `ticks.jsonl`：逐日/逐tick进化绩效日志

## 原理（防过拟合/防未来函数）
- 信号收盘生成→**次日开盘成交**；T+1 结构性满足
- 每折基因只在训练窗内进化，盲测 60 日零调参——拼接业绩为真实样本外
- 精英跨折延续 + 市场状态条件权重（4态×8家族）= 风格与时俱进的自我进化
- 10分钟tick在最新480日窗上持续推进GA代数（种子=当前活体基因组）

## 数据源（2026-09-19 实战定案，详见 CODELY.md 记忆）
个股=TX裸价×新浪复权因子（qfq=raw÷F）；当日增量=qt.gtimg实时报价（真成交额/流通市值）；指数=腾讯 proxy.finance.qq.com。**腾讯qfq个股数据损坏勿用**；baostock/东财因并发被本机IP拉黑/限流。
