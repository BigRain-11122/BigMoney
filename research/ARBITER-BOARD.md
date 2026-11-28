# 资源共享仲裁看板（量化 × 自媒体）

generated 2026-11-28T20:51:37+08:00 | 契约 v1.0

| 资源 | 实测 | 谁在用 | 规则 |
|---|---|---|---|
| GPU | util 0% · VRAM 1917/16384MB · Comfy 队列 0/0 | media（本机 GPU 归自媒体） | 量化永不申请 GPU |
| CPU | load 16.7% | media 2 个活 · quant 3 个 | heavy 要求 media 空且 load<50 |
| RAM | free 29.52GB | media 占 7.22GB | heavy 需 ≥6GB · light 需 ≥2GB |
| 自媒体排队 | 清单 0 单 · None 已有 None 个产物 · 最近推进 Noneh 前 | media 产线 | 自媒体有活时量化 heavy 让路 |

## 当前在跑

- media pid 8664 · 3492MB · `D:\ComfyUI\python_embeded\python.exe -s D:\ComfyUI\ComfyUI\main.py --listen 127.0.0.1 --port 8189 --disable-sm`
- media pid 18716 · 3900MB · `D:\ComfyUI\python_embeded\python.exe -s D:\ComfyUI\ComfyUI\main.py --listen 127.0.0.1 --port 8188`
- quant pid 34316 · 159MB · `C:\Users\Dasheng\AppData\Local\Programs\Python\Python313\pythonw.exe -m smoke_test`
- quant pid 38416 · 304MB · `C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -File K:\Fluxgrou`
- quant pid 43392 · 74MB · `wscript.exe //B //nologo K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\InvisibleRunner.vbs powershell.exe -NoPro`

## 最近一次裁决

- tick → **DENY** (STATE_ONLY)
- 证据：{}

## 边界

- 仲裁只决定「开不开新活」，不杀任何正在跑的进程；被拒的格子保持 pending。
- 租约 30 分钟自动过期；执行体崩溃不会永久占坑。
- 自动调参只 ±1 档、每天最多一次、需 ≥24 次决策样本；其余提案只报不改。
