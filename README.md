# Bigmoney

**量化交易公司系统 · CEO 视角**

沪深 ETF 3-15 天日线波段交易。1 主控 + 3 Worker 分布式回测，自动参数进化，实盘部署。

## 目录结构

```
Bigmoney/
├── README.md                 # 本文件
├── requirements.txt          # Python 依赖
├── dashboard.html            # 像素风监控面板
├── bigmoney.html             # Bigmoney 主界面
│
├── config/                   # 全局配置
│   ├── settings.py           # 路径/Redis/参数
│   ├── param_grid.py         # 回测参数网格（432 组）
│   └── universe.py           # ETF 标的池
│
├── engine/                   # 核心引擎
│   ├── backtester.py         # 回测引擎（T+1、次日开盘、成本）
│   ├── exit_rules.py         # 持仓铁律（分层止盈/移动止损/时间衰减）
│   ├── factors.py            # 30 因子库（15 经典 + 15 特色）
│   ├── risk.py               # 风控
│   └── cost.py               # 交易成本
│
├── strategies/               # 8 大流派 35 个策略
│   ├── trend.py              # 趋势跟踪（唐奇安/海龟/MA/PSAR/Supertrend）
│   ├── mean_reversion.py     # 均值回归（布林/RSI/z-score/RSI-2）
│   ├── momentum.py           # 动量轮动（横截面/双动量/TS/RS）
│   ├── volatility.py         # 波动率（低波/目标/突破/状态切换）
│   ├── sentiment.py          # 情绪资金（放量/成交额/量价/日内/隔夜）
│   ├── seasonal.py           # 日历季节（月/周末/假期）
│   ├── macro.py              # 宏观过滤（沪深300 MA200/回撤）
│   ├── event.py              # 事件缺口（缺口回补/放量突破/双底）
│   └── README.md
│
├── data/                     # 数据
│   ├── daily/                # 48 只 ETF 日线（新浪源，1724 文件）
│   ├── basic/                # 基础数据（沪深300、ETF 池）
│   └── sector/               # 行业指数
│
├── research/                 # 研究笔记
│   ├── FACTOR_RESEARCH.md    # 30 因子 IC 报告
│   ├── CEO_HANDBOOK.md       # CEO 运营手册
│   └── MONEY02_ASSETS.md     # 前代系统资产清单与教训
│
├── results/                  # 回测结果
│   ├── factor_ic.json        # 因子 IC 原始数据
│   ├── *.json                # 432 组参数网格回测结果（按 hash 命名）
│   └── ranking.csv           # 筛选排名（2026-09-23 实证：top 0 = 内置均线信号全灭）
│
├── screening/                # 策略筛选排名
├── live/                      # 实盘网关（骨架）
├── monitor/                   # 监控面板
├── tasks/                     # 分布式任务（Celery + local fallback）
├── scripts/                   # 脚本
│   ├── download_etf.py       # 下载 ETF 日线
│   ├── download_index.py     # 下载指数
│   ├── factor_ic.py          # 因子 IC 分析
│   └── check_rules_update.py
├── knowledge/                 # 市场规则
│   ├── market_rules.md       # 全量规则 v2026.09.22
│   └── rules.py              # 结构化规则（费率/T+0 清单）
├── logs/                      # 运行日志
├── Money02/                   # 前代A股短线系统资产库（7.7GB 数据+设计参考，旧自动任务已停用，详见 research/MONEY02_ASSETS.md）
└── legacy/                    # 历史归档
    ├── hold_period_system/    # 第一版持仓铁律
    └── etf_trading_system/    # 第一版 ETF 标的池
```

## 网络架构（Tailscale）

```
Master (笔记本) 100.x.x.x ── Redis :6379 (bind Tailscale only)
   │
   ├── Worker1 100.y.y.y   ── celery -Q backtest_queue
   ├── Worker2 100.z.z.z   ── celery -Q backtest_queue
   └── Worker3 100.w.w.w   ── celery -Q backtest_queue
```

实盘券商 API 走公网直连，**不经过 Tailscale**；交易指令仅 Master 本机生成。

## 快速开始（任何机器，一条命令）

```powershell
# 1. git clone git@github.com:BigRain-11122/bigmoney.git（多机并行开发交流全靠 git；拷贝文件夹仅为离线后备）
# 2. 一条命令自举：依赖自装（清华镜像回退）→ 20 项自检 → 总控数据生成
python bootstrap.py
# 3. 打开总控 bigmoney.html；（可选，Windows）装 10 分钟 AI 自迭代循环（路径自适应零改动）：
powershell -NoProfile -ExecutionPolicy Bypass -File Tools\register_loop_task.ps1
```

常用命令：`python -m tasks.local_runner`（432 组回测）｜`python scripts\ce_transfer.py`（复现 CE 迁移）｜`python -m screening.rank`（排名重建）｜交接指南=`research/HANDOVER.md`

## 当前状态

- ✅ 48 只 ETF 真实日线（2020-01 ~ 2026-09）
- ✅ 30 因子 IC 研究完成
- ✅ 8 大流派 35 个策略函数
- ✅ 回测引擎 P0 修复（T+1、未来函数、成本）
- ✅ 持仓铁律（分层止盈 + 移动止损 + 亏损 8 天强平）
- ✅ 市场规则备案
- ❌ 2026-09-23 实证：432 组内置均线信号全灭（最好 Sharpe 0.44 / 年化 3.8%，ranking top 0）——策略层换血中（复合因子 + 策略工厂）
- ⏳ 36 个策略函数未接回测
- ⏳ 3 台 Worker 未部署
- ⏳ 实盘未接券商 API
- ⏳ 北向资金/行业指数数据缺口
- 🤖 2026-09-23 起 AI 全面接管开发：每 10 分钟自迭代循环（任务板驱动，PLAN.md 为契约）；前代系统 Money02 并入为资产库
- 📦 2026-09-23 11:30 起转入「回测算力节点」模式：自动化开发暂停（用户赴另一台机器开发），本机循环只跑回测计划与维护；**交接与取数指南 = `research/HANDOVER.md`**

## 下一步

1. 对 35 个策略跑 IC/回测，看哪些在 ETF 上真有效
2. 双因子组合：0.3×(-vol_60) + 0.3×(-intraday_range) + 0.2×mom_12_1 + 0.2×price_position
3. 补数据：北向资金、2015 年前历史
4. Tailscale 组网 + 3 Worker 部署
5. 模拟盘 2 周后切实盘

## 技能面（集团动员令 P-2026-09-26-01 登记）

源入司仓 `tools/skills/`（随 git 分发·安装副本 gitignored）；会话内置（codely-guide/skill-creator/tuanjie-cli）+跨司源（MiniGame tick-loop 先例）盘点在册。

- **bigmoney-conflict-resolve**（2026-09-26 建）：跨机 git push/rebase 冲突正典解法——UU/AA 批量件按形态分类（rolling-ledger union/append-log/js-wrapper 保真/snapshot 取新/HANDOVER 锚前插增/CODELY 行级 union/digest 让号重编），配确定性分类器 `scripts/classify_conflicts.py`（selftest 16 例），覆盖 r161~r220 实弹坑律族。触发场景：push 被拒、rebase UU 状态面、同窗双机撞车批解冲突。
