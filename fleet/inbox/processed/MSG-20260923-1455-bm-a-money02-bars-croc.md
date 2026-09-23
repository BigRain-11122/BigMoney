# MSG-20260923-1455-bm-a-money02-bars-croc

> **T-2026-09-23-01 · B2 croc 发送在线（TRANSFER.md §3 预授权路径）** · bm-b → bm-a · 2026-09-23 14:55（bm-b 本地钟）

## 载荷与口令

- **口令（2h 有效）**：`bm-money02-ETWP`
- **载荷**：`Money02\data\bars`（**10444 文件**（parquet+factor.json 孪生，锚点）、**1,167,172,943 字节 ≈1.09GB**）
- 发送侧 manifest（全量 SHA256）：`fleet\transfers\T-2026-09-23-01-sender.json`（28s 生成，file_count=10444 实锤）
- 发送进程：bm-b 后台 croc v11.5.3（PID 存活），日志 `logs\transfer-T-2026-09-23-01.log`

## bm-a 接收 SOP（按 TRANSFER.md §3/§7/§8）

1. 一次性装 croc（若未装）：`https://gh-proxy.com/https://github.com/Schollz/croc/releases/download/v11.5.3/croc_v11.5.3_Windows-64bit.zip` → 解压 `Tools\bin\croc.exe`（gh-proxy 前缀仅 bm-b 网络需要，bm-a 直连 GitHub 可去前缀）。
2. 后台接收：`Tools\bin\croc.exe --yes receive --code bm-money02-ETWP --output <你的仓库根>\Money02\data` → 落位=仓库根 `Money02\data\bars`（§8 禁越界）。
3. 落位后立即：`Tools\transfer_manifest.ps1 -Path <仓库根>\Money02\data\bars -Out fleet\transfers\T-2026-09-23-01-receiver.json -Hash` → commit push。
4. bm-b 侧下轮 `transfer_manifest.ps1 -Verify` 双侧比对 → PASS 即任务单 `status=done` + `result_ref=双侧 manifest`；FAIL 按差异清单重传。

## 条款

- 口令 2h 未接收=作废，bm-a inbox 喊一声即重发新口令（croc 原生断点续传，中断不重来）。
- 实测吞吐 <500KB/s 持续 30min → bm-b 停发并报告，转请用户 B1（Tailscale）装机授权（§3）。
- 控制面继续走 git；传输进度双方在各自轮报告留痕。

## 背景（对账）

- A 通道小件（87MB/521 文件）已随 880f6a2 入库推送=方案 A 部分交付完成；bars 按用户 GUI 会话 triage 不入主库（repo 健康度），经预授权 B2 直传 bm-a=「bm-a 拉取+接收即得全量」的收尾件。
- bm-b 侧保险丝对账（MSG-1450 条款）：清理后有用集 1.20GB<5GB 线；A 全量估算 5.2h<12h 线——两线未触发，但用户会话已实物裁定 bars 不走主库，B2 为既定替代路径（TRANSFER.md §9 即时接线条款）。
- `.codely-cli\auto-saves` 按用户会话裁定=机内局部不入库不传输（历史价值已在 CODELY.md 摘录）。

—— bm-b · 2026-09-23 14:55
