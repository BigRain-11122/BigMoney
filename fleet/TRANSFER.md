# TRANSFER.md — 机队公网互传机制 v1.0

> 2026-09-23 建 · 用户令「git作为方案A，公网互传方案B，有其他方案也可以」· bm-a 起草
> 适用：Bigmoney 机队任意两机间的大数据/资产传输。本文档随 git 同步，任何机器的 AI 会话按此执行。
> 配套工具：`Tools/transfer_manifest.ps1`（manifest 生成+校验）；传输留痕目录：`fleet/transfers/`。

## 0. 总原则

1. **发起**：任何传输 = 任务单 `fleet/tasks/T-*.json`（`type=transfer`），spec 写明方向（发送机→接收机）、数据集路径、选用方案、落位路径、校验锚点（文件数/字节数/manifest 引用）。
2. **控制面走 git，数据面走选定通道**：握手、口令、进度、完成通报一律经 `fleet/inbox/` 消息；数据本体走方案 A/B/C/D 通道。
3. **交付判据 = manifest 双侧一致**：发送机出 `fleet/transfers/<taskid>-sender.json`，接收机出 `-receiver.json`，经 `transfer_manifest.ps1 -Verify` 比对通过才算 done（done 必带 result_ref 指向双侧 manifest）。
4. 传输进程一律 `Start-Process` 后台化 + 日志留痕（`logs/transfer-<taskid>.log`），禁阻塞循环轮（round 35min 限时）。

## 1. 选型矩阵

| 场景 | 方案 | 说明 |
|---|---|---|
| ≤500MB · 代码/成果/文档 | **A · git 分批** | 既有通道；规则见 §2 |
| 0.5–10GB · 一次互传 · 双方在线 | **B2 · croc 中继直传** | 零账号零安装，AI 可全自助编排（§3） |
| ≥5GB · 常态互传 · 长期主力 | **B1 · Tailscale 组网直拷** | 一次性装机（用户授权）后 100.x 直连 robocopy（§4） |
| 超大档案 / 一方离线 / 一对多 | **C · 云中转** | rclone→Cloudflare R2（免费10GB）/ OneDrive / 网盘（§5） |
| 机器间网络全断 | **D · 离线摆渡** | 移动硬盘人肉通道（§6） |

**决策顺序**：默认 A → A 触发保险丝（预估 >12h 或数据集 >5GB）→ **自动切 B2，不必等用户裁决** → B2 实测吞吐 <500KB/s 持续 30min → 停下报 bm-a/用户，请求 B1 装机授权 → 一方离线 → C。

## 2. 方案 A（git 分批 · 既有）

- 分批 commit ≤1.5GB、每批一 push；单件 >95MB 预检排除并报告（GitHub 100MB 硬限）；单次 push >2GB 会被拒，批内勿超。
- 后台顺序推送、日志留痕；push 被拒 = `pull --rebase` 重试一次，再拒即停并报告，**禁 force-push、禁双 push 撞锁**（round 20-22 实录）。
- 保险丝：预估总传输 >12h 或数据集 >5GB → 停，切 B2。
- 适合：代码、研究结果、中小数据集；一次入库全机队随 clone 分发。

## 3. 方案 B2（croc · AI 全自助中继直传）

- **一次性安装**：从 GitHub Releases（schollz/croc）下载 windows_amd64 zip，解压至 `Tools\bin\croc.exe`。该目录已 gitignore，各机局部。无账号、无 NAT 配置、天然加密。
- **发送机**：后台 `croc send --code <口令> --relays <relay> <数据集路径>`；口令自生成（`bm-<任务短名>-<4位随机>` 格式，禁敏感词）；日志 `logs/transfer-<taskid>.log`。
- **口令交换**：口令+预计体量+落位路径经 `fleet/inbox/` 定向消息发接收机（私库，仅机队可见）。
- **接收机**：收到消息的当轮后台 `croc --yes receive --code <口令> --output <落位路径>`；完成后立即出 manifest 回比对。
- **断点**：croc 原生 partial resume（`.part` 件），中断后同口令重发即续传。
- **超时**：口令 2 小时未被接收 = 作废重发新口令（防挂死/泄露）。
- **已知风险**：croc 公共中继在境内直连可能慢/不通；实测 <500KB/s 持续 → 升级请求 B1。

## 4. 方案 B1（Tailscale 组网 · 需用户一次性装机授权）

- 两机安装 Tailscale（或 ZeroTier）+ 同一账号登录 → 各得 100.x.x.x 虚拟 IP。
- 传文件 = `robocopy <源> \\100.x\...` / `scp` / `rsync`，打洞成功时≈双方出口带宽直连。
- **装机与常驻服务属用户授权项**：任何机器禁擅自安装常驻网络服务（安全红线）；申请路径 = 任务单 note 注明 + bm-a 转报用户。

## 5. 方案 C（云中转）

- 通道：rclone → Cloudflare R2（免费 10GB、无出口费）/ OneDrive / 国内网盘客户端。
- 链接经 inbox 传；**凭证/密钥永禁入库**（本地 `.env` 或用户直给）。
- 适合：一方离线、单机对多机分发、>20GB 档案。

## 6. 方案 D（离线摆渡）

- 移动硬盘人肉通道。唯一保底，速度=物流。用于 A/B/C 全不可用时的兜底。
- 拷贝后仍须 manifest 双侧校验（§0 第3条）。

## 7. 校验与交付 SOP

```powershell
# 发送机：生成 manifest（大体量加 -Hash 全量哈希，~10k 文件 ≈ 3 分钟）
Tools\transfer_manifest.ps1 -Path <数据集> -Out fleet\transfers\<taskid>-sender.json [-Hash]
# 接收机：落位后生成 + 比对
Tools\transfer_manifest.ps1 -Path <落位目录> -Out fleet\transfers\<taskid>-receiver.json [-Hash]
Tools\transfer_manifest.ps1 -Path <落位目录> -Verify fleet\transfers\<taskid>-sender.json [-Hash]
```
- PASS → 任务单 `status=done` + `result_ref=双侧 manifest 路径` + 双侧 commit push；FAIL → 差异清单（缺/多/哈希坏）入轮报告，按差异重传。

## 8. 安全

- croc 口令一次性、2h 过期；经私库 inbox 传递可接受；凭证/密钥/API token 永不入库。
- 常驻服务（Tailscale/网盘客户端）装机须用户逐次授权。
- 收发双方路径须落在各自仓库根内（Money02 落位 = 仓库根 `Money02\`），禁越界写系统目录。

## 9. 变更记录

- v1.0（2026-09-23）：bm-a 建立（用户令）。现行任务 `T-2026-09-23-01` 即时接线：A 保险丝触发 → 自动切 B2，无需再等用户裁决；B2 慢则报 bm-a 请求 B1 授权。
