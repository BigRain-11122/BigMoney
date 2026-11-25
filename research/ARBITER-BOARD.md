# 资源共享仲裁看板（量化 × 自媒体）

generated 2026-11-25T11:21:39+08:00 | 契约 v1.0

| 资源 | 实测 | 谁在用 | 规则 |
|---|---|---|---|
| GPU | util 1% · VRAM 2194/16384MB · Comfy 队列 None/None | media（本机 GPU 归自媒体） | 量化永不申请 GPU |
| CPU | load 5.4% | media 1 个活 · quant 2 个 | heavy 要求 media 空且 load<50 |
| RAM | free 25.87GB | media 占 3.8GB | heavy 需 ≥6GB · light 需 ≥2GB |
| 自媒体排队 | 清单 0 单 · None 已有 None 个产物 · 最近推进 Noneh 前 | media 产线 | 自媒体有活时量化 heavy 让路 |

## 当前在跑

- media pid 17700 · 3896MB · `D:\ComfyUI\python_embeded\python.exe -s D:\ComfyUI\ComfyUI\main.py --listen 127.0.0.1 --port 8189 --disable-sm`
- quant pid 87268 · 75MB · `wscript.exe //B //nologo K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\InvisibleRunner.vbs powershell.exe -NoPro`
- quant pid 87344 · 305MB · `C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -File K:\Fluxgrou`

## 最近一次裁决

- tick → **DENY** (STATE_ONLY)
- 证据：{}

## 边界

- 仲裁只决定「开不开新活」，不杀任何正在跑的进程；被拒的格子保持 pending。
- 租约 30 分钟自动过期；执行体崩溃不会永久占坑。
- 自动调参只 ±1 档、每天最多一次、需 ≥24 次决策样本；其余提案只报不改。
