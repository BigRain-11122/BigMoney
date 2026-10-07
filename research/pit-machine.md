# pit-machine.md -- machine-state / Ollama / GPU face pit laws (domain file, D-20261002-06)
# Migration: r703 bm-c mini-split (from CODELY.md main file, byte-verbatim, zero-loss asserted).
# Read before: machine-state pause/resume legs, Ollama pin/resume diagnostics, per-process VRAM probes.

- [2026-10-07 21:29:55] [2026-10-07 21:5x] Ollama 0.40.0 resume GPU 误判坑（全面开工首战实录·v4 pause 面续章）：自升 0.40.0（10-06 18:13 落地·新 runner 按需解压布局）后，pause→resume 首次 pin 时若显存被游戏残留占用→Ollama 判 GPU 不可用整模型落 CPU（size_vram=0·8 tok/s·诊断面=llama-server 命令行无 -ngl 参数）。正法=先杀「ollama app」托盘再杀 serve→净重启→重 pin（13.1-13.3GB 上卡·62 tok/s）。两个负案：OLLAMA_KV_CACHE_TYPE=q8_0 反而 5.3 tok/s（FA 回退路径·User env 已清并复验）=禁用；显存不足强挤全层=OOM 风险。逐进程显存诊断正法=Get-Counter '\GPU Process Memory(*)\Dedicated Usage'（魔改卡 nvidia-smi query-compute 全显 [N/A] 不可用）。本次挤占真凶=StarCraft 720MB+dwm 1666MB（游戏会话）非 GameViewer/FlowCapture（<100MB）——CEO 关游戏后净重启即可回 88-91 tok/s。How to apply：①resume 后 pin 报 ok 但 tok/s 个位数→按本条排查；②杀序=托盘先 serve 后；③machine-state v5 候选=pin 后探 size_vram==0 自动净重启重 pin 一次。


- 对账行 r703 bm-c: entry bytes=1141 sha16=9ef7bfe3f7d0df47 verbatim-in-file (zero-loss asserted; receipt=results/_r703bmc_codely_minisplit.json)
