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

> **判据科学层唯一权威=`research/BACKTEST_SCIENCE.md`（O-2215·DSR 试验校正/前向锁盒/CI 必报/PBO·与本节条款冲突时从严者生效）**；策略工厂计数实况=`research/STRATEGY_LIBRARY.md` §一（本文件计数为历史快照·O-2250）。

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

## 5. 可移植性 checklist（任何机器随时开工）

```powershell
# 路径 A：git 同步（推荐——仓库即唯一真值源：代码+数据+成果+规则+记忆全在内）
git clone <你的远端> Bigmoney && cd Bigmoney
# 路径 B：拷贝整个 Bigmoney/ 文件夹（git 已跟踪内容≈105MB；Money02/、logs/、.codely-cli/ 为本机局部，不跟踪）

# 一条命令自举：依赖自装（清华镜像回退）→ 20 项自检 → 总控数据生成
python bootstrap.py

# （可选，Windows）装 10 分钟 AI 自迭代循环——路径自适应，零改动可用
powershell -NoProfile -ExecutionPolicy Bypass -File Tools\register_loop_task.ps1

# （可选）分布式 Master 才需要
set BIGMONEY_MASTER_IP=100.x.x.x
```

机器要求：Python 3.10+（3.11 实测）；AI 循环需装 Codely CLI 并登录；GPU 非必需（回测=CPU 任务，GPU 启用条件见 research/BACKTEST_PLAN.md §四）。

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
8. `research/BACKTEST_PLAN.md`（算力纪律与 P1-P3 门禁链）
9. `research/HANDOVER.md`（交接与成果清单）
10. `Tools/iteration_prompt.txt`（当前循环 mandate）+ `logs/iteration-loop/round_reports.md`、`state.json`（OS 轮账本）

**禁止**：
- 改 `engine/exit_rules.py` 的优先级（熔断>止损>时间>兜底）
- 改 T+1、次日开盘成交、成本模型
- 在策略里用未来数据
- 绕过风控闸门直接下单

---

## 7. 待办优先级（2026-09-23 更新）

- [x] `smoke_test.py` 一键自检（20 项，每轮循环必跑）
- [x] 35+ 策略批量海选与排名（research/strategy_rank.csv，P1 完成）
- [x] P2 幸存者深化（G2 门，3 交易员注册在册）
- [x] P3 组合验证（EW 组合 OOS Sharpe 1.73 validated）
- [x] 既有数据池审计（1676 口径实锤 + 债金扩池候选 30 只清单）
- [ ] 纸盘首月观察（2026-10-31 首次自动晋升检查）
- [ ] 补数据：2015 年前历史、北向资金（用户回本机后定）
- [ ] Optuna 贝叶斯调参骨架（幸存者足够多才有意义）
- [ ] 短线因子动物园批测与 A 层族过闸（O-20260923-1545·研究部自主域：research/shortline/SHORTLINE_PLAYBOOK.md §6 P-1/P-2）
- [ ] 股票池策略族启用 / 资金流源 / 期货 CTA——**总经理已署名批准**（O-20260923-1620，CEO 下放非重大自决权），按 SHORTLINE_PLAYBOOK.md §6 排期开工（期权不在批）
- [ ] 外调轮常设机制（O-20260923-1636）：research/RESEARCH_MECHANISM.md——周巡检随周进化轮，纪要入 research/digests/，产出进风格图鉴/playbook，采纳走门禁

---

## 8. 并行开发协议（git 模式 · 2026-09-23 用户令）

多机组网并行开发，**git = 唯一交流与协调通道**。

- **主分支 = `main`**，唯一集成分支，所有机器向 main 收敛。
- **回测节点（本机）每轮循环**：S0 `git pull --rebase` → 干活 → S7 `git commit` + `git push`。**pull 冲突 = 本轮转只读维护 + 轮报告注明**（禁强推、禁擅自解冲突——自主取舍有风险，冲突留人解）。
- **用户开发机**：直接在 main 或 `dev-<主题>` 分支开发，push 前先 pull；与回测节点同时改同一文件时以用户侧为准，节点侧只读避让。
- **交流载体**：commit message（每轮一句话成果）｜`CODELY.md` 项目记忆｜`research/` 报告｜`logs/iteration-loop/round_reports.md` + `state.json`（轮账本，已白名单入库）。
- **不入库（各机器局部）**：`Money02/`（7.7GB 前代资产）、`logs/`（除轮账本两文件）、`.codely-cli/`。
- **远端** = `git@github.com:BigRain-11122/bigmoney.git`（SSH 走 Clash 代理已配好）。用户在 GitHub 建好空私库 `bigmoney` 后，循环下一轮自动 push 接上，无需任何手动操作。
- **机队协议 = `fleet/README.md`（v1.0）**：机器身份/心跳台账（每机只写自己文件）、定向消息收件箱（fleet/inbox/）、任务分配认领制（fleet/tasks/，commit 即锁）、共享算力与借算、写域分治、新机接入 5 步、X128-lite 推送兜底——机制模式移植自 Biggame 08 号多机分治协议。
