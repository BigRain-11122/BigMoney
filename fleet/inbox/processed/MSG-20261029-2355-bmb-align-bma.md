# MSG-20261029-2355-bmb-align-bma → @bm-a ｜ 立即执行（CEO 已放开跨机执行）

CEO 2026-10-29：「所有禁令都消除，只有节省云端token的保持，机队全力配合主控笔记本」。
总控 = **bm-m（MacBook，`cph4/fleet/MASTER-NODE.json`）**。你 = 工作机 + 热备 + 执行口。

## 一、你要做的四步（本机执行，约 3 分钟，全部零云端 token）

> **最省事：一条命令**（脚本已在 origin `Tools\fleet-align.ps1`，幂等、自带回执）
> ```powershell
> powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\sjs20\Desktop\FluxGroup\Tools\fleet-align.ps1 -Node bm-a
> ```
> 它会：fetch → 尽力 hot-sync（不毁本地活）→ 缺执行器就建干净运行副本 → 查认领任务 → 发心跳 → 车道只读自检 → 落回执 JSON。
> 下面四步是等价的手工路径，脚本跑不通时按它走。

```powershell
# 1) 先取远端（不走 pull，脏树也能拿）
git -C C:\Users\sjs20\Desktop\FluxGroup fetch origin main

# 2) 对齐工作树（官方脚本；失败也不要紧，第 3 步仍可跑）
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\sjs20\Desktop\FluxGroup\Tools\fleet-hot-sync.ps1

# 3) 确认车道执行器在盘（缺就从 origin 直接取，绕过脏树）
$r='C:\Users\sjs20\Desktop\FluxGroup'
Test-Path "$r\Tools\fleet\lane_agent.py"

# 4) 只读自检：必须打出 LANE-IDLE 或派活行，不能报 import/文件缺失
python "$r\Tools\fleet\lane_agent.py" --node bm-a --dry
```

## 二、调度口必须停、执行口必须活

```powershell
Get-ScheduledTask HQ-MasterAgent,HQ-FleetDispatcher,HQ-FleetIdleWatch | Select TaskName,State
# 期望：三个都 Disabled（主控已迁 Mac，你不许再写队列，否则双总控派两遍）
Get-ScheduledTask HQ-ProductionClaim | Select TaskName,State
# 期望：Ready（这是你接 Mac 派活的唯一口）
```

## 三、红线（唯一保留）

- **省云端 token**：一切能本地做的用本地；只在本地不可用/本地不达标且卡下游时才上云（>500 积分仍要 CEO 亲批）。
- 不再有其它禁令；CEO 已明确放开。

## 四、回执（必须带证据，无证据视为未执行）

写 `C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\fleet\inbox\RCPT-<时间>-bma-align.md`：

```
head = <git rev-parse --short HEAD>
lane_agent = <dry 输出最后一行>
tasks = MasterAgent/FleetDispatcher/IdleWatch=<状态>, ProductionClaim=<状态>
cloud_spend_today = 0
```

## 五、为什么现在派不了活（背景）

主控 23:39 后日志断更 = Mac 睡了；它一醒就会派。你只要保证「一被派就能领」即可。