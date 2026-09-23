# Bigmoney 开发计划 v1.0

> 本文件是 AI 自我迭代的顶层契约。任何 agent 接手时**先读本文件**，再按阶段推进。
> 所有路径相对项目根；所有 IP/账号/密钥走环境变量；所有代码必须在新机器上 `pip install -r requirements.txt && python -m smoke_test` 跑通。

---

## 0. 设计原则（不可妥协）

1. **可拷贝迁移**：整个文件夹拷到新机器就能跑。禁止硬编码绝对路径、机器名、公网 IP。
2. **Master 瘦，Worker 傻**：Master 只做调度/聚合/实盘；Worker 无状态，丢了重连即可。
3. **CPU/GPU 各司其职**：见 §1.3。
4. **回测/模拟/实盘同源**：一套代码，三个开关，禁止分叉。
5. **AI 可接管**：每个模块有明确接口、输入输出、单测。codely 读 README + PLAN 就能改。
6. **先不进场**：任何实盘动作前必须有 ≥6 个月模拟盘 + 样本外验证。

---

## 1. 系统架构

### 1.1 节点拓扑

```
┌──────────────────────── Master (笔记本) ────────────────────────┐
│  数据下载  因子计算  策略调度  实盘网关  结果聚合  AI 进化大脑    │
│  SQLite/parquet 数据仓  Redis 队列  Dashboard                   │
└───────────────┬─────────────────────────────────────────────────┘
                │ Tailscale 100.x.x.x
   ┌────────────┼────────────┐
   ▼            ▼            ▼
 Worker1     Worker2      Worker3
 CPU 回测    CPU 回测     GPU 训练
 (pandas)    (pandas)    (torch/lgbm)
```

### 1.2 职责划分

| 节点 | 角色 | 任务 |
|---|---|---|
| Master | 大脑 | 数据、因子、信号、实盘、结果聚合、AI 调参 |
| Worker1/2 | 算力 | 消费回测队列，纯 CPU，多进程 |
| Worker3 | GPU | 跑 ML 模型训练（LightGBM/Torch）、大规模因子矩阵 |

### 1.3 CPU vs GPU 分工（写死）

| 任务 | 跑哪 | 为什么 |
|---|---|---|
| 日线回测循环 | **CPU** | pandas 向量化足够快，GPU 反而慢 |
| 因子横截面计算 | **CPU** | 48×1600 矩阵，GPU 启动开销 > 计算 |
| 432 组参数网格 | **CPU 并行**（每 Worker 多进程） | 任务级并行，不需要 GPU |
| LightGBM/XGBoost 训练 | **CPU**（树模型多核快于 GPU） | |
| LSTM/Transformer 时序模型 | **GPU** | 序列模型必须 GPU |
| 大规模因子库（>100 因子）矩阵化 | **GPU（torch）** | 批量 Z-score、IC 矩阵 |
| 遗传算法/贝叶斯调参 | **CPU** | 每个个体是一次回测，CPU 并行 |

**判断规则**：计算能向量化成 (N_days × N_assets) 小矩阵（<100万元素）→ CPU；模型训练或 >100 因子批量 → GPU。

---

## 2. 目录与接口契约

### 2.1 接口契约（AI 接手必读）

每个策略模块必须导出：

```python
# strategies/xxx.py
def signal(prices: dict[str, pd.DataFrame], params: dict) -> pd.DataFrame:
    """输入: {symbol: df[date,open,high,low,close,volume,amount]}
       输出: DataFrame[date, symbol] -> 0/1 仓位
       约束: 不使用未来数据（信号 shift(1)，次日 open 成交）"""
```

每个回测任务必须导出：

```python
# tasks/backtest_task.py
def run(params: dict) -> dict:
    """输入: 参数字典
       输出: {annual_return, max_drawdown, sharpe, win_rate, trades: [...]}
       约束: 纯函数，无全局状态，异常必须捕获返回 error 字段"""
```

### 2.2 可移植性规范

- 所有路径用 `config.settings.PATHS`（基于项目根 `Path(__file__).parent.parent`）
- 所有网络配置从环境变量读：`BIGMONEY_MASTER_IP`、`BIGMONEY_REDIS_PORT`、`BIGMONEY_API_KEY`
- 禁止 `C:\`、`/home/` 硬编码
- 禁止依赖本机已安装的非 pip 包
- 新增文件必须能被 `python -c "import strategies"` 不报错

---

## 3. 阶段路线图

### P0 · 数据与基础设施（当前 ~60%）

- [x] 48 只 ETF 日线下载
- [x] 30 因子 IC 研究
- [x] 8 流派 35 策略骨架
- [x] 回测引擎 P0 修复
- [ ] **补数据**：全 A 股 ETF（约 800 只）、2015 年前历史、北向资金、申万行业
- [ ] **SQLite/parquet 数据仓**：替换 CSV 散文件，支持增量更新
- [ ] **smoke_test.py**：一键验证环境+数据+回测

### P1 · 策略工厂（2 周）

- [ ] 对 35 个策略函数批量跑 IC + 回测，输出排名
- [ ] 自动剔除 IC<0.01 的策略
- [ ] **策略模板**：每个流派写 3 个变体（参数不同），共 ~100 个候选
- [ ] 过拟合检测：70/30 样本外切分，Sharpe 衰减 >30% 自动淘汰

### P2 · AI 进化大脑（2 周）

- [ ] **参数进化**：贝叶斯优化（Optuna）替代网格搜索，每轮 50 组
- [ ] **策略生成**：LLM 根据研究笔记自动写新策略骨架，人工 review
- [ ] **自动复盘**：每日收盘后 LLM 读交易记录，写改进建议到 `research/auto/`
- [ ] **因子挖掘**：遗传算法变异因子表达式（如 `mom_20 - vol_60*2`），自动测 IC

### P3 · 分布式与 GPU（1 周）

- [ ] Tailscale 组网验证（3 台 Worker 真实连通）
- [ ] Celery 队列 + 心跳 + 断线重投
- [ ] Worker3 装 PyTorch，跑 LSTM 时序模型
- [ ] 结果聚合到 Master SQLite，Dashboard 实时刷新

### P4 · 实盘网关（3 周，最后做）

- [ ] 模拟盘 2 周（QMT/Ptrade 模拟账户）
- [ ] 风控闸门：单票 ≤10%、总仓 ≤80%、日亏 >3% 停开新仓
- [ ] 实盘 1 个月观察期，仓位 ≤20%
- [ ] 稳定 3 个月后加仓

---

## 4. AI 自我迭代机制

### 4.1 进化循环（每周自动跑）

```
1. 拉最新数据
2. 对当前 Top10 策略跑样本外回测
3. 若 Sharpe 衰减 >30% → 自动下线，从候选池补位
4. LLM 读本周交易日志 + 因子 IC 变化 → 写新策略 idea 到 research/ideas.md
5. 对 idea 自动生成代码 → 单测 → 回测 → 进入候选池
6. 每周日生成周报到 research/weekly/
```

### 4.2 质量闸门（任何新策略必须过）

- 交易次数 ≥30（统计显著）
- 样本外 Sharpe ≥0.8
- 最大回撤 ≤25%
- 年化 > 沪深300 同期
- 无未来函数（代码审查）
- 换手率 < 月频（成本可控）

### 4.3 反过拟合

- 样本内/外严格切分（2020-2024 训练，2025-2026 测试）
- 参数数量 ≤5（避免高维拟合）
- 每季度重新跑一次全量回测，参数漂移 >20% 触发警报

---

## 5. 可移植性 checklist（拷贝到新机器时）

```bash
# 1. 拷贝整个 Bigmoney/ 文件夹
# 2. 装 Python 3.11+
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# 3. 一键自检
python -m smoke_test

# 4. 设环境变量（Master 才需要）
set BIGMONEY_MASTER_IP=100.x.x.x

# 5. 跑
python -m tasks.local_runner
```

---

## 6. codely 接手清单

新 agent 第一次进来时按顺序读：

1. 本文件 `PLAN.md`
2. `README.md`（目录总览）
3. `strategies/README.md`（8 流派）
4. `research/FACTOR_RESEARCH.md`（哪些因子有效）
5. `engine/backtester.py`（回测引擎接口）
6. `engine/exit_rules.py`（持仓铁律）
7. `knowledge/market_rules.md`（合规边界）

**禁止**：
- 改 `engine/exit_rules.py` 的优先级（熔断>止损>时间>兜底）
- 改 T+1、次日开盘成交、成本模型
- 在策略里用未来数据
- 绕过风控闸门直接下单

---

## 7. 待办优先级（下周）

1. 补数据：全 A 股 ETF 池（800 只）+ 2015 年前历史
2. 写 `smoke_test.py` 一键自检
3. 把 CSV 数据迁到 parquet（增量更新快 10 倍）
4. 对 35 个策略批量跑 IC，输出 `research/strategy_ic.csv`
5. 写 Optuna 贝叶斯调参骨架
