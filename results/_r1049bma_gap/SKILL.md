---
name: memory-curator
description: 记忆治理席（集团三层记忆体系的预算守门人）。Use whenever a session is about to write memory (append_memory/update_memory), receives any memory-bloat / slimming / audit / budget task, sees CRIT-FLAG or MERGE-QUEUE from the 4h gate, or needs to know what belongs in L0/L1/L2/git. Triggers on 记忆膨胀/记忆瘦身/记忆审计/记忆预算/写入记忆/CODELY 膨胀/记忆治理/清理记忆.
---

# 记忆治理席工作法（memory-curator）

正典法源：cph4/memory.md §8（上链律）§9（四字令）§10（分层预算律·本席执法面）；工具=Tools/memory-budget-gate.py v2（确定性零 LLM）；台账=cph4/fleet/memory-slim/LEDGER.md；四小时静默闸=HQ-MemoryBudgetGate（S4U·every 4h）。
立项：CEO 令 2026-10-18「研究控制记忆膨胀+创立专门 agent」；首跑判例=R-20261018-memory-control-01.md（**联合回灌拉锯案：L0 union/replace-down 与预算闸打架的完整病根链，禁复活**）。

## 一、写入五问（写记忆前逐问·违一即停）

1. **已有同主题条目？** → 必须 update_memory 改写原条目，**禁 append 新版留旧版**（并档链病灶根因；同题 ≥2 版会被 4h 闸机械去重——别浪费那一拍）。
2. **超 300 字？** → 全文先落 L2 主题文件（`<home>\.codely-cli\memory\topics\<主题>.md`），记忆面只回写 1-2 行指针。
3. **跨机价值？**（项目状态/产线工艺/司域裁决）→ 走 git 正典（orders/cph4/L1），**禁入本机私有 L0**——跨机内容灌进 L0 的旧联合通道已退役（§10.2 路由正身）。
4. **已消费的执行态叙事？**（批次过程/在飞状态/已被新条取代）→ 不入记忆；git log + orders 已承载（入账四问·memory.md §1）。
5. **一个月后还重要？** → 否=跳过。

## 二、三层路由表（什么放哪）

| 层 | 位置 | 放什么 | 预算 |
|---|---|---|---|
| L0 注入层 | `<home>\.codely-cli\CODELY.md` | 跨域硬法（CEO 常设令原话要点）/用户长期事实/主题索引——**每会话强制注入=最高成本面** | 预警 35KB/80 条·执法 50KB/120 条 |
| L1 项目层 | 仓根 `CODELY.md`（git 分发） | 项目指针+项目级记忆 | ≤40KB/≤60 条 |
| L2 主题层 | `<home>\.codely-cli\memory\topics\` | 一切长文/状态/领域细节 verbatim | 按需读·不注入 |
| git 正典 | orders/cph4/各司仓 | 一切跨机价值正身 | 随 git |

**新立常设法时**：①条目落 L0（≤300 字）；②在 Tools/memory-budget-gate.py 的 KEEP_RULES 加一个白名单元组（或确认条目含 LAW_MARKERS：原话/长期律/常设/铁律/红线/硬门）——否则第 3 天起会被闸自动路由进主题文件。

## 三、会话省税律

启动注入已含 L0+L1 全文 → **禁再 read_memory 全量重读（scope=all=双倍成本）**；按需只读单个主题文件。检查本席旗标只看三个小文件：`memory\curator\last-report.json`、`MERGE-QUEUE.md`、`CRIT-FLAG.txt`。

## 四、巡检与瘦身 SOP

- **日常**：4h 闸自动执法（快照零删除→非法定路由主题→同题去重→台账落行）。会话无需手动跑。
- **手动瘦身**（接令/CRIT 旗时）：①`python Tools\memory-budget-gate.py --report` 看分类预算 → ②真跑（去 `--report`）→ ③复测字节数+条目数+法条锚点 grep 存活 → ④台账 LEDGER.md 落行。回滚=快照目录 cleanup-gate-* 原样拷回。
- **MERGE-QUEUE 人工摘要**（闸不碰法条，只排队）：超 1.5KB 法条 → 手写 ≤1.5KB 摘要版（规则本体保留+细节指针化），update_memory 替换；低相似同题对 → 人工合并保留现行有效版。
- **多窗协调**：动 L0 前先看 `cleanup-<date>` 目录是否他窗刚建+orders 是否已认领；本闸自带 mtime 守卫（竞写即 abort 重跑）；同令他窗已认领=零重做只补保险。

## 五、红线（违=闸失效复盘案）

- L0 联合回灌类机制（union 正本/镜像 replace-down）**永不复活**——与预算闸结构性打架（10-16~17 实锤）。
- 法条永不自动截断/自动删；一切删除走快照+git 史双通道（归档非清除）。
- L1 改写走平台工具或 py 字节补丁+git 原子推（bm-a project-scope EEXIST 在册）；跨机价值入 git 正典，**永不再造联合正本**。

## 六、部署面（新机/他机）

canon=cph4/skills/memory-curator/（git 分发）；装机=Tools\agent-library-sync.ps1；闸任务=task-register.ps1 正门注册 `daily` 或 `every:240m`（S4U 强制·fire test 必过）；部署机自加本机身份 KEEP_RULES 元组（bm-a 样例：("本机（C 机/bm-a）定位",)）。
