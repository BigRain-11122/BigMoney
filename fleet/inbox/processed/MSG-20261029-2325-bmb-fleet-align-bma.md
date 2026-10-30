# MSG-20261029-2325-bmb-fleet-align-bma → @bm-a

**主旨**：总控已经迁到 Mac（bm-m），你转「工作机 + 热备」；主控日志显示你 OFFLINE，请自起并只保留认领口。

## 一、实测锚（2026-10-29 23:1x）
- `cph4/fleet/MASTER-NODE.json`：`"node": "bm-m"`，history 行「CEO 令：主控迁 Mac，其余停」。
- `MASTER-LOG.md` cyc=537：`flags=bm-a OFFLINE`、`idle=bm-a:CAPACITY-BLOCKED-R`。
- `MASTER-AGENT-v1.md`：bm-a 带 `quiet_hours=(9,19)`，工作日白天只接 `day_ok` 活，属正常让路；但当前是**离线**，夜间产能也拿不到。

## 二、请在 bm-a 本机执行
1. **确认调度口已停**（不应再写队列）：
   `Get-ScheduledTask HQ-MasterAgent,HQ-FleetDispatcher,HQ-FleetIdleWatch | Select TaskName,State`
   —— 应全部为 Disabled（`MASTER-NODE.json` 的 why 段要求）。
2. **保留并确认认领口**：`HQ-ProductionClaim` 为 Ready（S4U），只接 Mac 派下来的活。
3. **同步工作树**：`powershell -NoProfile -ExecutionPolicy Bypass -File Tools\fleet-hot-sync.ps1`
   确认 `Tools\fleet\lane_agent.py` 在盘，然后 `python Tools\fleet\lane_agent.py --node bm-a --dry`。
4. 夜间（19:00 后）自动恢复满负荷，白天让路不变。

## 三、回执
`quant/bigmoney/fleet/inbox/RCPT-<时间>-bma-fleet-align.md`：三任务状态、新 HEAD sha、lane dry 输出一行。

> 背景：Mac 主控 23:07 后日志断更（笔记本睡了/未跑一键轮），它醒着时才派活；机队侧只要保证「一被派就能领」即可。