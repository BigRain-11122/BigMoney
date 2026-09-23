# Bigmoney 底层技术栈（v1.0 · O-20260923-1538）

> 分层地图+指针。节点拓扑/CPU-GPU 分工唯一权威=`PLAN.md` §1；本文不复制数值。
> 设计宪法=PLAN.md §0（可拷贝迁移/回测模拟实盘同源/AI 可接管等六条）。

```
L5 自治层   OS 循环（Tools/iteration_prompt.txt S链）· fleet 机队 · orders 令牌   ←公司神经系统
L4 观测层   monitor/（build_status·dashboard·rich_dashboard）· bigmoney.html · dashboard.html · town.html
L3 交易层   firm/traders/（3 员在册）· live/（paper 锚定）· firm/risk/ 铁律 · firm/hr.py 考核
L2 策略层   strategies/（8 流派 35 策略）· 门禁链 G1'/G2 · 零假设校准（research/NULL_CALIBRATION.md）
L1 引擎层   engine/（backtester·exit_rules·factors·metrics）· screening/ —— 回测/模拟/实盘同源
L0 数据层   scripts/update_daily.py 多源日线链 · data/ 语料（bars parquet 10444·Money02 前代库·Money0923 25年面板）· 纪元/校验
```

- **分布式底座**：`tasks/`（celery_app·backtest_task·local_runner）+ PLAN.md §1 节点拓扑；现役机队：bm-a（32 核·开发节点）+ bm-b（16 核·回测节点），协议=`fleet/FLEET-OPS.md`。
- **技术演进槽**（均须 P1 署名，见 firm/RULES.md §2）：Optuna 贝叶斯调参（J 队）→ J13 本地 LLM 研究助理 → Money0923 可学清单 12 条（`research/MONEY0923_TRIAGE.md` §三：QMT 实盘桥/逆回购现金管理/GPU 海选/数据纪元/防作弊审计等）。
- **新能力入列规则**：先过门禁链（PLAN.md §4.2 质量闸门）再上生产；跨公司共享能力登记集团 `cph4/`（引用不复制）。
