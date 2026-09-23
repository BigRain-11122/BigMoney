# Bigmoney 自动化开发能力（v1.0 · O-20260923-1538）

> 开发主链+质量门禁+无人值守能力总图。S 链唯一权威=`Tools/iteration_prompt.txt`；本文件=能力对外说明书+部门（工程部）宪法。

## 一、开发主链（需求到生产）

```
需求源 ──▶ 双板认领 ──▶ OS 循环执行 ──▶ 质量门禁 ──▶ 入库留痕 ──▶ 汇报回执
```

| 环节 | 机制 | 权威文件 |
|---|---|---|
| 需求源 | CEO 令（/CEO→orders 台账）· P1 队列（PLAN §7）· 部门 KPI 异常 · HQ-FEEDBACK · 进化提案 | `fleet/orders/` · `PLAN.md` |
| 认领 | job_list + `fleet/tasks/*.json` 双板，claimed 即锁（commit 锁），后到让路 | `fleet/README.md` §4 |
| 执行 | 10 分钟一轮 S 链：S0 pull→S0.5 令牌→S1 smoke→S2 板→S3 小闭环→S4 记忆→S5 轮账本→S6 数据链→S7 提交推送 | `Tools/iteration_prompt.txt` |
| 门禁 | smoke 全绿（FAIL=当轮唯一使命修红）· 反重复铁律（先读后写/复用禁重建/同仓单执行体退避） | `PLAN.md` §0 · prompt |
| 留痕 | commit=锁 · 轮报告一行制 · CODELY.md 记忆 · results/research 产物落盘 | `logs/iteration-loop/` |
| 回执 | 令牌执行回执（orders_ack）· 部门 KPI 汇总（总经理面呈 CEO） | `fleet/FLEET-OPS.md` §3 |

## 二、策略开发专用门禁（区别于工程开发）

- 门禁链 **G1'/G2**（策略上线闸）+ 判据科学层 v2=`research/BACKTEST_SCIENCE.md`（O-2215·试验数校正 DSR/前向锁盒/CI 必报/PBO/成本 v2·与 PLAN §4.2 冲突时从严者生效·工具任务单=`fleet/tasks/T-2026-09-23-02-P1.json`）+ PLAN §4.2 质量闸门（样本外 Sharpe≥0.8·交易≥30·回撤≤25%·无未来函数·换手<月频）+ §4.3 反过拟合（样本内外切分·参数≤5·季度漂移警报）。**引擎加性铁律（O-2250 §八）**：引擎/退出机/成本改动一律加性旗标且默认关=历史路径逐字节不变，锚定门免疫=交付判据。
- 入职→晋升→淘汰全自动化：`firm/hr.py`（月度/事件驱动考核，无人为干预；红线改值=T0）。

## 三、无人值守底座

- **Bigmoney-IterationLoop**（Windows 计划任务·10 分钟网格·round.lock 防双触发·静默门：交互会话在世则只读退避）。
- **数据链每日**：update_daily（exit 0-3 语义，2/3 必须原样上报）→ paper 锚定门禁 → build_status 面板刷新。
- **让位与保险丝**：用户 GUI 会话亲手执行>转发指令；传输 <500KB/s×30min 停报；上传窗口不推撞。
- **备份三级**：库内=GitHub 每轮 push；库外大资产=独立私库/云位（BigMoney-data 等）；身份/钥匙不备份（FLEET-OPS）。

## 四、度量与回滚

- 工程部 KPI：轮健康度（round_reports 逐轮可读）· 修红时延 · 交付吞吐（commit/journal 密度）。
- 回滚：git revert/reset + reflog 取证（脏树陷阱先 checkout 还原）；重大事故=总经理 T1 呈 CEO。

## 五、AI 赋能声明

本能力链无人类岗位：需求受理、任务认领、编码、测试、部署、留痕、汇报全 AI 执行；CEO 仅在 P1 署名、红线裁决、方向变更处出现（见 `firm/RULES.md` §2 权力分层）。
