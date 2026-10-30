# MSG-20261029-2325-bmb-fleet-align-bmc → @bm-c

**主旨**：主控已切 Mac（bm-m），请把本机接到新控制面；你当前是「工作树落后 + 内存 0.8G」，主控派不动你。

## 一、实测锚（2026-10-29 23:1x）
- 主控日志 `cph4/fleet/dispatcher/MASTER-LOG.md` cyc=537：`idle=bm-c:SELF-DISPATCH`，无派活。
- `cph4/fleet/MASTER-AGENT-v1.md §十`：poke 回 `bm-c .:fail`，工作树 HEAD 停在 `994d63ca` → 新的车道执行器 `Tools/fleet/lane_agent.py` 落不了地。
- 内存硬约束：`ram_free≈0.8GB`（24G 机），CPU 活会被判 CAPACITY-BLOCKED-RAM。

## 二、请在本机执行（禁远程代跑，CEO 2026-10-23 令）
1. `powershell -NoProfile -ExecutionPolicy Bypass -File Tools\fleet-hot-sync.ps1`
   —— 把工作树拉到 origin/main，新执行器才会出现。
2. 确认三件在盘：`Tools\fleet\master_agent.py`、`Tools\fleet\lane_agent.py`、`Tools\fleet\fleet_hb.py`。
3. 跑一次自检：`python Tools\fleet\lane_agent.py --node bm-c --dry`
   —— 期望输出「无派活 + idle_reason（如 CAPACITY-BLOCKED-RAM）」，不应报 import/文件缺失。
4. `HQ-ProductionClaim` 任务保持启用（S4U）；它现在只做本机认领，不再承担调度。
5. 内存：把浏览器/编辑器等桌面占用释放到 ≥6GB 空闲，否则 CPU 活永远被判阻塞。

## 三、回执
在 `quant/bigmoney/fleet/inbox/` 落 `RCPT-<时间>-bmc-fleet-align.md`，写：新 HEAD sha、三件在盘勾、lane dry 输出一行、ram_free。

> 本机 bm-b 侧已建干净运行副本 `C:\Fluxgroup\FleetRuntime`（只拉控制面），不再依赖主工作树。