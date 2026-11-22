# 资源共享仲裁看板（量化 × 自媒体）

generated 2026-11-22T23:31:47+08:00 | 契约 v1.0

| 资源 | 实测 | 谁在用 | 规则 |
|---|---|---|---|
| GPU | util 19% · VRAM 12220/16384MB · Comfy 队列 1/0 | media（本机 GPU 归自媒体） | 量化永不申请 GPU |
| CPU | load 97.5% | media 5 个活 · quant 2 个 | heavy 要求 media 空且 load<50 |
| RAM | free 3.08GB | media 占 33.75GB | heavy 需 ≥6GB · light 需 ≥2GB |

## 当前在跑

- media pid 17792 · 29MB · `C:\Users\Dasheng\AppData\Local\Programs\Python\Python313\python.exe cph4/fleet/mv-album-001-jay/local-i2v/h3_i`
- media pid 38804 · 150MB · `C:\Users\Dasheng\AppData\Local\Programs\Python\Python313\python.exe Tools/voicebank/vb_worker.py --voice v06 -`
- media pid 39292 · 26897MB · `D:\ComfyUI\python_embeded\python.exe -s D:\ComfyUI\ComfyUI\main.py --listen 127.0.0.1 --port 8188 --disable-sm`
- media pid 41368 · 4082MB · `C:\Users\Dasheng\AppData\Local\Programs\Python\Python313\python.exe K:\Fluxgroup\FluxGroup\Tools\voicebank\vb_`
- media pid 52840 · 100MB · `C:\Program Files\PowerShell\7\pwsh.exe -NoProfile -Command Write-Output "=== 断点续跑版 v6 点火（7 张缓存跳过·剩 16 张续烧+训练）=`
- media pid 54292 · 2183MB · `D:\ComfyUI\python_embeded\python.exe -s D:\ComfyUI\ComfyUI\main.py --listen 127.0.0.1 --port 8189 --disable-sm`
- media pid 55568 · 21MB · `D:\ComfyUI\python_embeded\python.exe -u K:\Fluxgroup\.codely-cli\tmp\heroine_lora_factory.py ql`
- media pid 56928 · 122MB · `C:\Program Files\PowerShell\7\pwsh.exe -NoProfile -Command cd K:\Fluxgroup\FluxGroup; $env:PYTHONIOENCODING='u`
- quant pid 58360 · 44MB · `C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -File K:\Fluxgrou`
- quant pid 59232 · 19MB · `wscript.exe //B //nologo K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\InvisibleRunner.vbs powershell.exe -NoPro`

## 最近一次裁决

- tick → **DENY** (STATE_ONLY)
- 证据：{}

## 边界

- 仲裁只决定「开不开新活」，不杀任何正在跑的进程；被拒的格子保持 pending。
- 租约 30 分钟自动过期；执行体崩溃不会永久占坑。
- 自动调参只 ±1 档、每天最多一次、需 ≥24 次决策样本；其余提案只报不改。
