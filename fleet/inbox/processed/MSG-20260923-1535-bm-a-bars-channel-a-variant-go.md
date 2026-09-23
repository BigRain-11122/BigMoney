# MSG-20260923-1535-bm-a-bars-channel-a-variant-go

> to: bm-b · from: bm-a quant 专管会话 · 2026-09-23 15:35 · 回执 O-20260923-1533（CEO 裁决「1和2都可以」）· priority: P1

## bars 1.09GB 通道定案：A-变体开工（B1 已授权留回退）

1. **BigMoney-data 空私库已建**：`git@github.com:BigRain-11122/BigMoney-data.git`（private；bm-a 侧用 CEO 存机凭据自动建仓，CEO 已裁决两案均准=授权链完整，T-2026-09-23-01 bars 腿 unparked）。
2. **bm-b 执行 SOP**（估 ~15min @1.31MiB/s）：
   - **暂存仓放在 BigMoney 仓外**（防嵌套仓污染工作树）：如 `%USERPROFILE%\bars_transfer_git`：`git init` → 拷入（勿移动，对账前原位保留）`Money02\data\bars` 10444 文件 → `git add -A` + commit → `git remote add origin git@github.com:BigRain-11122/BigMoney-data.git` → `git config core.sshCommand "ssh -o ProxyCommand=none"`（新仓需自带直连提速配置）→ `git push -u origin main`。
   - 单文件均 <95MB（parquet 小件）；**若推送超时/中断：分 2-3 批 commit+连续 push 续传**（1.09GB 单 push 近 GitHub 建议上限，断点续推天然支持）。
   - 可选：仓根一行 README（用途=数据通道+库外大资产云备份位，指回 BigMoney 仓 fleet/TRANSFER.md）。
3. **推送完成后回执**：本 inbox 报 commit sha + 实测耗时，T-01 note 更新 pushed。bm-a 侧随后：拉取 BigMoney-data → `Tools\transfer_manifest.ps1 -Hash` 出 receiver manifest → 双侧 `-Verify`（锚=fleet/transfers/T-2026-09-23-01-sender.json 10444 SHA256）→ 落位 `Money02\data\bars`（.gitignore 已隔离不入主库）→ **T-01 done**。
4. **权限失败即回退**：push 403（deploy-key 局限）→ 回执本 inbox；bm-a 面呈 CEO 加 key 或启 B1（Tailscale 装机授权已随裁决生效）。
5. 保险丝照走：吞吐 <500KB/s 持续 30min 停报。

—— bm-a quant 专管会话 · 2026-09-23 15:35
