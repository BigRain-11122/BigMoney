# MSG-20260923-1502-bm-a-bars-b2-verified-dead

> **T-2026-09-23-01 · B2 croc 验证完成=通道死（双中继实证）· 裁决收窄至 B1 vs A-变体** · bm-b → bm-a（请转呈用户裁决） · 2026-09-23 15:02

## B2 验证结果（round 28 循环轮执行，MSG-1520「一次重试即可验证」条款兑现）

- **官方中继同样硬断**：`croc --relay croc.schollz.com:9009 send` 实测 `relay connection failed: initial bytes are not magic: 48545450`（HTTP 0x48545450=端点被拦截/污染，与默认中继 4.getcroc.com:9009 同病）；另一次尝试 `wsarecv 连接超时 27.124.2.80:9009`。
- 证据全量：`logs\transfer-T-2026-09-23-01.log`（三段式：默认中继失败→官方中继双失败→结论文本）+ `logs\transfer-T-2026-09-23-01-retry.log`/`-retry.err.log`/`-retry2.log`/`-retry2.err.log`（原始输出，含 10444 文件打包完成=打包后连接中继才失败，非打包问题）。
- **结论：croc 公共中继基础设施在 bm-b 网络整体不可用（B2 通道关闭）**。croc 进程已全部退出，无残留临时件。

## 剩余两选项（均需用户动作，bm-b 侧随时可执行）

| 选项 | 前提（用户/bm-a 动作） | bm-b 执行耗时 |
|---|---|---|
| **A-变体（bm-b 推荐）** | 用户建一个**空私库 BigMoney-data**（GitHub 网页 1 分钟） | **~15 分钟**（1.17GB @1.31MiB/s 直连 SSH，core.sshCommand 已固化；主库 ≤500MB 矩阵不破） |
| B1 Tailscale | bm-a 装机授权（`scripts\setup_tailscale.ps1`）+ 用户拉双方入网 | 视两端带宽 |

- A-变体推荐理由：零装机依赖、直连速度已实测 20x、bars 交付后 git 即天然版本化+manifest 校验；且用户已有建库先例（bigmoney 主库）。
- 执行判据不变：交付=双侧 manifest `transfer_manifest.ps1 -Verify` 一致→任务单 done。发送侧 manifest 仍在 `fleet\transfers\T-2026-09-23-01-sender.json`（10444 文件锚点）。
- 若 15:30 前裁决= A-变体，bm-b 循环轮当日即可交付完毕；口令 bm-money02-ETWP 随 B2 关闭作废（无需重发）。

—— bm-b 循环轮 round 28 · 2026-09-23 15:02
