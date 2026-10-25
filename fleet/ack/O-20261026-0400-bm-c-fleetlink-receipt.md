# O-20261026-0400-bm-c 回执（bm-c 本机活窗执行，2026-10-26 04:0x）

令号：O-20261026-0400-bm-c（FleetLink 传感面自愈 + RAM 让路）
执行机：bm-c（FLUXGROUP / 100.123.74.104）

## §1 结论：不是监听器不在，是它只绑了回环地址

- 执行前实况：`Get-NetTCPConnection -LocalPort 8790 -State Listen` = **127.0.0.1:8790 only**，
  属主 PID 24880（`powershell -File K:\Fluxgroup\FluxGroup\Tools\fleet-link.ps1`，起于 2026-10-25 20:20:22）。
- 因此 bm-a 侧对 `100.123.74.104:8790` 得到 TCP 拒连 **而不是超时**——与「监听器不在」同形，但进程一直活着，
  本地 `http://127.0.0.1:8790/status` 全程 HTTP 200。ICMP/tailscale 正常与本次故障无因果关系。
- 根因（作进脚本注释）：机器 20:20 开机时本进程早于 tailscale 网卡拿到地址启动，`Try-Bind` 对
  `100.123.74.104` 记一次 bind-fail，只绑住回环；此后每轮 supervisor 的健康门只看「同版本 listener 占着端口」
  = 判健康 → **回环孤岛可以活到下次重启**。

## §2 修复（两件）

1. **即时**：`Stop-Process 24880` + `Start-ScheduledTask FluxGroup-FleetLink` → 绑定变为
   `100.123.74.104:8790` + `127.0.0.1:8790`（PID 29244）。
2. **根治**（改集团树 `Tools\fleet-link.ps1`，升 v1.9.5）：
   - 健康门新增判据——节点 `tailnet_ip` **必须出现在 listen 地址集**里，否则置 `rebindNeeded`
     且取消 same-version 健康标记；
   - 接管分支从 `runningVers != Vers` 放宽为 `runningVers != Vers -or rebindNeeded`，
     即「同版本但只绑回环」本轮就会被顶掉重绑，不再靠人工/重启。
   - 语法校验：PSParser 解析通过（4332 tokens）。
   - 自愈实测：触发一次 supervisor → state.json 变 `version=1.9.5`，
     `bound=["100.123.74.104:8790","127.0.0.1:8790"]`（PID 48780，04:00:07 起）。

## §3 验收物（本机侧证据）

| 项 | 实测 |
| --- | --- |
| 监听 | 127.0.0.1:8790 + 100.123.74.104:8790，单 PID 48780，v1.9.5 |
| status 经 tailnet 地址 | `Invoke-WebRequest http://100.123.74.104:8790/status` → **HTTP 200**，30880 bytes，含 `origin_main` |
| 版本 | state.json `version=1.9.5`（旧 1.9.4 已被自愈顶掉） |

## §4 RAM 让路实况（§2）

- 常驻 LLM：**本机早已无 ollama/llama-server 进程**（10-17 退役未被重启拉起），本次零可停项。
- ComfyUI：仅一台常驻监听进程（20:20 起），GPU 空闲（util 3%，VRAM free 14.0GB），**未起第二个**；
  该面属 GPU 生产车道，按令红线不作停机动作。
- codely 并发：无第二个交互会话在本仓动手（已核 python 在途进程=ComfyUI/sidecar 族，无 quant 批）。
- 现值：**free 1.03GB / 23.9GB，cpu_load 53%** → 满足令内「load < 90%」一半目标；free 未达 1.5GB，
  主因是 Windows 文件缓存+用户桌面进程（Doubao×2、Platform、NVIDIA Overlay），无本司常驻可停项。
  下一班若 free 继续压低，建议由 CEO-PROXY 侧指定可停的桌面进程或允许停 ComfyUI 常驻。

## §5 顺带发现（供代理席）

本机 `quant/bigmoney` 推送 8790 的同步腿仍在报 bm-b (`100.82.175.0:8790`) 连接失败——
即 bm-b 的对端传感面同样可能处于「回环孤岛」形态；v1.9.5 修复复制到 bm-b 后应自愈（其 supervisor 下一轮
会把旧版本/回环监听顶掉重绑）。本机侧不改他机。