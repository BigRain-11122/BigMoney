# 金融资料交接差异 · DASHENG ↔ FLUXGROUP

- 对端清单：`research/INGEST/INVENTORY-DASHENG-20261124.json`（generated 2026-11-24T23:28:35+08:00 · head 203419437e4e）
- 本机清单：`research/INGEST/INVENTORY-FLUXGROUP-20261125.json`（generated 2026-11-25T00:28:09+08:00 · head e9e94573092e）

**COMPLETE**

- 共有入库件 35051 个，其中 **35049** 个两边都有 sha256（可内容定谳）
- 他们有而我们没有：**1** 个（例：results/_selftest_sub/c_arm_metrics.json）
- 两边都有但**内容不同**：**9621** 个（例：.gitattributes, .gitignore, CODELY.md, HQ-FEEDBACK.md, Money02/CODELY.md）
- 无法定谳（至少一侧无 sha256、大小又相同）：**0** 个
- 我们独有的：921 个（正常，本机写出了新结果）
- 他们未提交：416 件 · git 状态：{"branch": "main", "head": "203419437e4e94a0b30d0d60d7b29763a8c9c6e6", "ahead_of_origin": "0", "behind_origin": "482", "stash": ["stash@{0}: On main: r1321 pre-integration derived faces (79)", "stash@{1}: autostash", "stash@{2}: On main: r1299 inherited dirty faces (pre-integration)", "stash@{3}: On main: r1296 inherited dirty outputs (dead window 11-13..11-16)", "stash@{4}: autostash", "stash@{5}: autostash", "stash@{6}: On main: r1286 pre-sync local heartbeat+review", "stash@{7}: On main: r1285 pre-integration derived faces (187 staged + dirty, 20:50-00:35 window)", "stash@{8}: On main: r1284 push-retry derived faces", "stash@{9}: On main: r1284 pre-integration derived faces", "stash@{10}: On main: r1026 s0 pre-ff residual face"]}

> 本面**不用 mtime 判新旧**（它记的是检出时间，不是内容年龄）。若拿 mtime 比，会得到 16960 条「他们更新」——那是尺子坏了，不是差距。

## 差异归因（谁动了这个文件）

- 对端 head：`203419437e4e`；与本机 HEAD 之间变更 **3258** 个路径
- **提交版本不同**（`git pull` 即可同步，本机领先 482 个提交）：**2336** 个
- **仅 worktree 字节不同**（行尾过滤/未提交，非交接缺口）：**7271** 个，其中抽样 **60** 个经 `git hash-object` 复核、**60** 个与 `HEAD:<path>` 逐位相同
- 对端**未提交**（真正可导入）：**14** 个（例：docs/daily_report/REPORT-2026-11-18.json, docs/daily_report/REPORT-2026-11-18.md, docs/lane_ownership/DECLARATION-2026-11-18.md, docs/live_book/BASE-BASIS.md, docs/live_book/LIVE-BOOK-20261118.json）
- 本机**未提交**（我们自己的半成品）：**0** 个
- 本机在对端 head 之后**删除**的：**1** 个（不是缺口）
- **无法解释**：**0** 个
- ⚠ 归因边界：their dirty list is capped at 200 -- a path outside it is not proof of clean · our dirty list is capped at 200 -- same caveat · filter-only proof sampled 60 of 7271

## 那 14 个「对端未提交」里，真正该看的有几个

| 分类 | 数量 | 含义 |
|---|---|---|
| 他人属主面 | 2 | 文件名带别的机器 id（如 `.bm-a.`），本机导入即谎报作者 |
| 本机已有更新代 | 7 | 同名面本机已有更晚日期，导入等于回填过期的一天 |
| 滚动面 | 2 | 名字无日期、每天重写，历史副本没有读者 |
| 两边各自重生成 | 3 | 两边共用同一提交基线、各有一份未提交重生成：本机重生，别导入对端 |
| **需人工过目** | **0** | 唯一需要动作的一类 |

> 他人属主面：`results/_orphan_face_probe.bm-a.json`, `results/compute_audit.bm-a.json`

## 数据车道（git 搬不动）

| 车道 | 他们 | 我们 | 文件差 | bar 更新方 |
|---|---|---|---|---|
| astock_daily | 5222 文件 / 2026-11-18 | 5221 文件 / 2026-11-24 | +1 | ours |
| moneyflow | 5223 文件 / None | 5229 文件 / None | -6 | same |
| lhb_inst | 2 文件 / None | 2 文件 / None | +0 | same |
| options | 256 文件 / None | 256 文件 / None | +0 | same |
| futures_contracts | 335 文件 / 2026-11-17 | 418 文件 / 2026-11-24 | -83 | ours |
| futures_daily | 10 文件 / 2026-11-18 | 10 文件 / 2026-11-24 | +0 | ours |
| index_daily | 4 文件 / 2026-11-18 | 4 文件 / 2026-11-23 | +0 | ours |
| daily | 1725 文件 / 2026-11-18 | 1725 文件 / 2026-11-24 | +0 | ours |
| cb_daily | None 文件 / None | 1051 文件 / 2026-11-20 | -1051 | ours |
| repo_daily | 11 文件 / 2026-11-18 | 11 文件 / 2026-11-20 | +0 | ours |
| zt_pool | 5 文件 / None | 5 文件 / None | +0 | same |
| fundamental | 3 文件 / None | 3 文件 / None | +0 | same |
| heat | 125 文件 / None | 2 文件 / None | +123 | same |
| ext_slots | 1 文件 / None | 1 文件 / None | +0 | same |
| minute_feed | 10 文件 / 2026-11-17 | 10 文件 / 2026-11-24 | +0 | ours |

车道差异不能靠 git 解决：要么他们给重建脚本，要么按 ≤95MB 分包。

> 对端已交付 15/15 条车道的重建命令（`research/INGEST/LANES-DASHENG.json`），所以上表的文件数差异属于「重跑脚本」，不是「导入文件」。


> 本面由 `scripts/ingest_crossdiff.py` 生成；未写 `DIFF-latest.*`（那是对端无关的自我对照面）。
