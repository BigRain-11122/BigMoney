# 金融资料交接差异 · FLUXGROUP ↔ FLUXGROUP

their inventory 2026-11-24T22:58:10+08:00 | ours 2026-11-24T22:58:10+08:00

**COMPLETE**

- 他们有而我们没有的入库件：**0** 个
- 他们更新而我们落后的：**0** 个
- 我们独有的：0 个（正常，本机写出了新结果）
- 他们未提交：2290 件 · git 状态：{"branch": "main", "head": "49f1ef94e0b97eade4a9b161a792c1cf722e714e", "ahead_of_origin": "0", "behind_origin": "0", "stash": ["stash@{0}: On main: r1640 pre-rebase dirty 2358 (2026-11-13 20:17)", "stash@{1}: autostash", "stash@{2}: On main: bmc-r1589 rebase2 derived", "stash@{3}: On main: bmc-r1589 pre-rebase derived faces", "stash@{4}: autostash", "stash@{5}: On main: bmc-r1480-postchain-backup", "stash@{6}: On main: bmc-r1479-prewindow-backup", "stash@{7}: On main: r1380-estate", "stash@{8}: On main: r1335 absorb: derived faces from prior window (regenerable; kept for rollback)", "stash@{9}: On main: r1156 daemon faces", "stash@{10}: On main: r1142-s0-livefaces", "stash@{11}: On main: r1138-attrition", "stash@{12}: On main: r1067-s0-livefaces", "stash@{13}: r1008bmc pre-rebase bridge (restored by r1029 mis-drop heal)", "stash@{14}: autostash", "stash@{15}: On main: r959-S0-livefaces", "stash@{16}: On main: r918-s0-bmc-faces", "stash@{17}: On main: r874 push-storm churn"]}

## 数据车道（git 搬不动）

| 车道 | 他们 | 我们 | 文件差 | bar 更新方 |
|---|---|---|---|---|
| astock_daily | 5221 文件 / 2026-11-24 | 5221 文件 / 2026-11-24 | +0 | same |
| moneyflow | 5229 文件 / None | 5229 文件 / None | +0 | same |
| lhb_inst | 2 文件 / None | 2 文件 / None | +0 | same |
| options | 256 文件 / None | 256 文件 / None | +0 | same |
| futures_contracts | 418 文件 / 2026-11-24 | 418 文件 / 2026-11-24 | +0 | same |
| futures_daily | 10 文件 / 2026-11-24 | 10 文件 / 2026-11-24 | +0 | same |
| index_daily | 4 文件 / 2026-11-23 | 4 文件 / 2026-11-23 | +0 | same |
| daily | 1725 文件 / 2026-11-24 | 1725 文件 / 2026-11-24 | +0 | same |
| cb_daily | 1051 文件 / 2026-11-20 | 1051 文件 / 2026-11-20 | +0 | same |
| repo_daily | 11 文件 / 2026-11-20 | 11 文件 / 2026-11-20 | +0 | same |
| zt_pool | 5 文件 / None | 5 文件 / None | +0 | same |
| fundamental | 3 文件 / None | 3 文件 / None | +0 | same |
| heat | 2 文件 / None | 2 文件 / None | +0 | same |
| ext_slots | 1 文件 / None | 1 文件 / None | +0 | same |
| minute_feed | 10 文件 / 2026-11-24 | 10 文件 / 2026-11-24 | +0 | same |

车道差异不能靠 git 解决：要么他们给重建脚本，要么按 ≤95MB 分包。
