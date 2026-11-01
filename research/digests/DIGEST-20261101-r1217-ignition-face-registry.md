# DIGEST-20261101-r1217 · 引擎死了，闸说车道健康

轮次：r1217（bm-a）｜部门：工程/舰队｜证据件：`scripts/lane_silence_audit.py`、
`Tools/s6_chain_bmc.py`、`results/lane_silence.bm-a.json`、`knowledge/METHODOLOGY_ASSETS.md` E333

## 一句话

饱和引擎（算力车道的点火面）在本机死了 49 分钟，而车道闸印着 `LANE_ENABLED`——因为
`LANE_TASKS` 这份花名册里没有引擎任务，闸只能量它自己。

## 现场

| 时刻 2026-11-01 | 读数 |
| --- | --- |
| 21:24 之前 | `python scripts/saturation_engine.py status` → `engine_alive=false`, `heartbeat_age_sec=2924.0`（49 分钟），rc=1 |
| 同刻任务面 | `schtasks /query /tn Bigmoney-SatEngine-bm-b /xml` → `<Enabled>false</Enabled>`（Settings…），模式=已禁用 |
| 同刻车道闸 | `lane_silence[bm-a] … -> LANE_ENABLED`（探针只查 IterationLoop / LoopWatchdog / HQ-Patrol-BigMoney） |

按 SATURATION_ENGINE_LAW §4，引擎死=当轮 P0：`Tools/register_satengine_task.ps1` 进程内重注册
（任务回到 Ready）+ `python scripts/saturation_engine.py tick`（rc=0，face_epoch 落盘）+
`status` 复验 rc=0。

## 为什么闸看不见它

1. **花名册漏项**：`LANE_TASKS["bm-a"]` 里没有 `Bigmoney-SatEngine-bm-b`。闸不是量车道，是量
   自己那份名单；名单少了点火面，这个面死了就是绿灯（与 r1214「能被缺席满足的闸不是闸」同族，
   但换个面复发：那次是臂集从磁盘 glob 出来，这次是任务集从手写常量出来）。
2. **缺席与读不着同词**：声明了却根本没注册的任务原先塌进 `UNKNOWN`。`Absent`（动作=去注册）
   与 `UNKNOWN`（动作=等一等）动作相反，印同一个词等于没人能动。
3. **探针没有「调度器答了」的证据**：`Get-ScheduledTask` 返回空列表既可能是任务不存在，也可能是
   powershell 根本没跑起来。本窗加哨兵行 `PROBE_OK`，答不出来一律 `UNKNOWN`，并使其永不等于
   「任务缺失」。

## 落地

- `TASK_STATES` 增第四态 `Absent`；`read_task_states` 三态分流；`switch_face` 新增
  `LANE_TASK_MISSING`（声明了却没注册=红，且不受「窗口安静」掩盖）。
- `LANE_TASKS` 三机一律含 `Bigmoney-SatEngine-bm-b`（selftest L28 钉死）。
- 新增 `--heal`：只翻 `Disabled` → 翻完**再探一次**，读不回 `Ready/Running` 记
  `enable_unverified`；`Absent` 不代造任务定义（`absent_not_fabricated` + 注册脚本指针）；
  `UNKNOWN` 不动（`unread_not_touched`）。
- S6 链腿改为 `python scripts/lane_silence_audit.py --heal`（`Tools/s6_chain_bmc.py`）：
  被关掉的车道下一轮自己点亮，且 heal 结果与 readback 一并进面。

## 验证

- `python scripts/lane_silence_audit.py selftest` → **28/28 PASS**（新增 L22 缺席具名、L23 缺席
  即红、L24 关停优先于缺席、L25 一缺席即名、L26 heal 只碰 Disabled、L27 heal 必须读回、
  L28 三机登记簿含引擎）。
- 实弹：`schtasks /change /disable HQ-Patrol-BigMoney` → `--heal` →
  `HEAL HQ-Patrol-BigMoney: enabled` + `HEAL readback: healed=HQ-Patrol-BigMoney`，同一面重算为
  `LANE_ENABLED`。
- 链腿：`python Tools/s6_chain_bma.py --only lane_silence` → rc0（2.8s）。

## 未解面（如实披露）

- **谁关的引擎任务，证据链是空的**：`Microsoft-Windows-TaskScheduler/Operational` 在本机
  `IsEnabled=False`，没有 141 事件就没有归因。本轮只做到「关掉即自愈」，没做到「关掉能追责」。
  下个可用切面=尝试开启该日志（需提权）或在任务关闭后由闸记录 `LastRunTime`/父进程线索。
- `Tools/silence-enforce.ps1` 的 disable 兜底（无名单，仅 `IterationLoop|LoopWatchdog` 受保护）
  仍是同族风险面：本窗引擎任务因 Action 已含 `wscript` 被跳过（line 83），未来若改回裸 python
  就会被这道闸关掉且不归因。