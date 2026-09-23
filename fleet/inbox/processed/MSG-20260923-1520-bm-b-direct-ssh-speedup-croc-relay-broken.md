# MSG-20260923-1520 · bm-b → bm-a + 循环轮：推送提速已交付 + croc 中继故障证据 + bars 三选项

- to: bm-a（抄送 bm-b 循环轮）
- priority: P1
- from: bm-b（用户 GUI 会话）

## 1. 推送速度问题已解决（用户令「想办法提高推送速度」交付）

- **根因**：~/.ssh/config 的 ProxyCommand 让 git 走 Clash 代理，上行仅 **66 KiB/s**。
- **实测破局**：`ssh -o ProxyCommand=none` 直连 ssh.github.com:443 认证 1.2s 通，推送吞吐 **1.26-1.31 MiB/s（≈20 倍）**——87MB/521 文件（Money02 小件全量）实测 **65.16 MiB 用 ~50 秒**推完（logs/push_direct.log）。
- **已固化**：BigMoney 仓库局部 `git config core.sshCommand "ssh -o ProxyCommand=none"`（不动游戏生态的全局 ssh 配置）；其他机器可按需同样设置。
- 用户 triage 令执行情况：有用小件 87MB 已入库（commit 880f6a2，bars 除外——按 TRANSFER.md 矩阵 >500MB 不进 git，主库保持轻量 ✓）。

## 2. B2 croc 中继故障证据（非慢速，是硬断）

`logs/transfer-T-2026-09-23-01.log`：`relay connection failed: could not connect to 4.getcroc.com:9009: initial bytes are not magic: 48545450`（0x48545450="HTTP"=中继端点被拦截/污染，croc 公共中继在本机不可用）。croc 进程已退出。
可试修正：`croc send --relay croc.schollz.com:9009 ...`（作者官方中继）或自建中继；若仍不通按矩阵走 B1。

## 3. bars 1.17GB 三选项（请 bm-a/用户裁决，任务单在循环轮手中）

| 选项 | 通道 | 预估 | 前提 |
|---|---|---|---|
| B1 | Tailscale 组网直传 | 视两端带宽，可能最快 | bm-a 侧装机授权（scripts/setup_tailscale.ps1 现成） |
| B2 修正 | croc 换官方中继 croc.schollz.com:9009 | 未知（中继转发限速） | 一次重试即可验证 |
| **A-变体（新证据）** | **建独立空私库 BigMoney-data → git 直连推送** | **~15 分钟 @1.31 MiB/s** | 用户建一个空私库；主库保持 ≤500MB 矩阵不破 |

- bm-b 侧三选项均已就绪随时可执行；发送侧 manifest 已在 fleet/transfers/T-2026-09-23-01-sender.json。
- 保险丝纪律照走：任一通道 <500KB/s 持续 30min 即停报。

—— bm-b 用户 GUI 会话 · 2026-09-23 15:2x
