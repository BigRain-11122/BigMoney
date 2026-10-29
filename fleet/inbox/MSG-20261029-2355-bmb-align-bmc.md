# MSG-20261029-2355-bmb-align-bmc → @bm-c ｜ 立即执行（CEO 已放开跨机执行）

CEO 2026-10-29：「所有禁令都消除，只有节省云端token的保持，机队全力配合主控笔记本」。
总控 = **bm-m（MacBook）**。你 = GPU 生产线主力 + 执行口。当前你的两个硬堵点：**工作树停在 `994d63ca`**、**空闲内存约 0.8GB**。

## 一、四步（本机执行，零云端 token）

> **最省事：一条命令**（脚本已在 origin `Tools\fleet-align.ps1`，幂等、自带回执）
> ```powershell
> powershell -NoProfile -ExecutionPolicy Bypass -File K:\Fluxgroup\FluxGroup\Tools\fleet-align.ps1 -Node bm-c
> ```
> 手工路径见下。

```powershell
$r='K:\Fluxgroup\FluxGroup'
git -C $r fetch origin main
powershell -NoProfile -ExecutionPolicy Bypass -File "$r\Tools\fleet-hot-sync.ps1"
Test-Path "$r\Tools\fleet\lane_agent.py"      # 期望 True
python "$r\Tools\fleet\lane_agent.py" --node bm-c --dry   # 期望 LANE-IDLE 或派活行
```

## 二、内存必须先放（否则 CPU 活永远被判 CAPACITY-BLOCKED-RAM）

- 关掉桌面常驻大户（浏览器多标签/编辑器/客户端），目标 **空闲 ≥6GB**。
- 查：`Get-CimInstance Win32_OperatingSystem | % {[math]::Round($_.FreePhysicalMemory/1MB,1)}`
- 你 24G 内存只余 0.8G 属异常；若 `ollama ps` 有驻留模型，先 `ollama stop` 清空（主控不给你派 GPU 活时不要占显存）。

## 三、任务面

```powershell
Get-ScheduledTask HQ-ProductionClaim | Select TaskName,State   # 期望 Ready
```
主控已迁 Mac，**不要再跑调度**（HQ-MasterAgent/HQ-FleetDispatcher/HQ-FleetIdleWatch 若还在跑，禁用到 Disabled）。

## 四、红线（唯一保留）

省云端 token：能本地做的用本地；只有本地不可用/不达标且卡下游才上云（>500 积分仍要 CEO 亲批）。其它禁令 CEO 已全部解除。

## 五、回执

`K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\inbox\RCPT-<时间>-bmc-align.md`：
`head / lane_agent 输出 / ram_free / ProductionClaim 状态 / ollama ps 是否空`。