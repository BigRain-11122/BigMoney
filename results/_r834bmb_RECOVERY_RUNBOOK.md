# r834bm-b git-loss recovery runbook (written 2026-10-10 14:0x, THIS round's唯一使命)

## Incident (evidence: results/_r834bmb_gitloss_forensics.json)
- Window [13:11:23, 13:22:02] 2026-10-10: bigmoney 独立仓 `.git` + dirs {data,docs,engine,firm,fleet,knowledge,legacy,live} + root {CODELY.md,HQ-FEEDBACK.md,.gitignore} 递归删除；幸存=logs/monitor/Money02/Money0923/qa/QuantBull/research/results/screening/scripts/state/strategies/tasks/Tools/__pycache__ + 根文件 PLAN/README/state*.json 等。
- 13:17:02 runner 25min 超时击杀 r834 进程树时删除被中断（幸存面即明证）。r834 会话终笔 13:16:41=删组仓 sparse-checkout.lock+sparse-add 重试；其转录/子代理/外来会话经 13:22 轮+本轮双审计未见破坏命令（真凶命令疑在被杀前未落账）。组仓索引/历史 CLEAN（ls-files quant/bigmoney=0，零 commit 触碰）→ 非组仓锥削。
- 12:52/13:22 两轮会话均 25min 超时死亡（.err MCP noise），state 未跳轮：本文件所在轮=r834。

## In-flight assets (bm-b local, NOT in git)
- CLONE (detached, survives rounds): `C:\Users\Administrator\r836bmb_git` = `git clone --no-checkout git@github.com:BigRain-11122/bigmoney.git` — logs: C:\Users\Administrator\r836bmb_clone.{out,err}。完成标志=clone.err 出现 "done." 或 git 进程消失+无 .keep pack。origin tip=fec72330715e6277d640b1addbd971dda009a8b3。
- WT BACKUP (belt+suspenders): `C:\Users\Administrator\r836bmb_wtbackup\` = 35 件 13:0x S6 产物 (results/*, LWT>12:50) + state.json 快照。正常恢复不需它（--mixed 保幸存面），仅兜底。
- Forensics: C:\Users\Administrator\.codely-cli\tmp\05e45db...\chats\0a542d86-*.jsonl (r834 主转录) + 同 tasks\ 下子代理转录 + 13:22 轮转录 d54e48a6*；NTFS USN 深挖 (fsutil usn readjournal C:) + 僵尸 git PID 24568 (09:18:04 起, cmdline 不可读, r832 kill 实际失败) 取证待续。

## Next-round recovery procedure (MUST follow, in order)
1. `git pull` 禁止（无 .git）。验证 clone 完成：Test-Path C:\Users\Administrator\r836bmb_git\.git\HEAD；未完成=等（DiT 下载抢带宽，ETA 未知），只做值守。
2. Move: `Move-Item C:\Users\Administrator\r836bmb_git\.git C:\Fluxgroup\FluxGroup\quant\bigmoney\.git`；clone 目标目录残留根杂件一并移入/清理。
3. **禁 `git reset --hard`**（会回滚幸存的 13:0x 工作面+本文件时代的 state/轮报改动）。正解：
   - `git reset --mixed HEAD`（重建 index，零工作树触碰）
   - `git checkout HEAD -- .gitignore CODELY.md HQ-FEEDBACK.md data docs engine firm fleet knowledge legacy live`（只补缺失面）
   - `git status --porcelain` 应显示：幸存修改件 (13:0x results 等) + 本轮新增 untracked 件；零 "deleted"。
4. 重装双爪（.git 亡时丢失）：`& Tools\register_precommit_claw.ps1` + `& Tools\register_prepush_claw.ps1`（进程内调用）。
5. `python -m smoke_test` 全绿为准（fleet/ 恢复后 F 系应过）。
6. Commit+push（定向 add：state.json+logs\iteration-loop\round_reports.md+results/_r834bmb_*+fleet/inbox/MSG-*+恢复的 13:0x 修改件），消息 `round 834: git-loss recovery (forensics+runbook+inbox alert) [via bm-b]`。push 撞则 fetch+rebase 单次重试。
7. 心跳 fleet\machines\bm-b.json 更新（epoch int + clock_read T 分隔）；HANDOVER 不动（r835=5 倍数轮义务，届时办）。
8. 防复发铁律（本 runbook 立法，直至根因定谳）：**禁对集团树 C:\Fluxgroup\FluxGroup 跑任何 sparse-checkout/clean/checkout -- . 操作；组树消费一律 `git show origin/main:<path>` 零树触碰**（D-20261004-02③ 本就如此）。r833 遗留的 "verify group tree sparse-disable" 任务方向作废——sparse 保持开启（12:52 会话已定谳：全量加载会撞 DiT 下载），sparse-disable 待根因定谳+CEO 车道空窗再议。
9. 根因续查（低优先，恢复后）：USN journal 定删除进程名；审 24568 僵尸；grep 三外来会话 (cf4d812 13:17:36 呼叫) 全文。

## Score (Executive Protocol v1.1)
本轮=灾修轮：实物=本 runbook+forensics JSON+inbox 告警+分离克隆在飞（实际文件改动+可跑交付物）；无 commit（.git 亡）如实记录，恢复轮（下轮）以 origin 重建为准。
