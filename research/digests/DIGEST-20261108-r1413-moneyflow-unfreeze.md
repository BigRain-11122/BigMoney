# DIGEST 2026-11-08 r1413 (bm-c) — 搬机器的车道：先继承声明，后继承字节

## 起因

`MSG-20261108-0330-bma-lane-reassign`（bm-a，P1，`action_owner: bm-c`）：bm-b 心跳停在 2026-10-30T12:44
（206.7h），10-21 红线交给它的 akshare/EM 拉取族全部冻住，前向积累面每过一天就是永久损失。
六条车道改挂 bm-c，按「归属已改，动作自然」处理。

## 本轮做的事（都是可核的实物）

### 1 继承面的核实，而不是照抄

| 车道 | 消息里的说法 | 实测（bm-c 本机） |
|---|---|---|
| `update_fund_statements` | 缺 2026Q3（10-31 截止已过） | **已完备**：87 期 × 3 面覆盖法定完备期 20260930，gate 直接 no-op 零网络 |
| `update_zt_pool` | 尾在 10-29 | gate `no-op: panel covers all bar-landed trading days` |
| `update_etf_daily` | — | cutoff 2026-11-06 = 期望完整 bar 日 |
| `update_ths_panel` | — | daily 2026-11-06.csv 已在，幂等 no-op |
| `update_sina_mf` | — | cutoff 2026-10-26，在其 20td/250td 滚动窗内 |
| `update_options` | 退役 | `[RETIRED]` 诚实 no-op |
| `ah_panel_puller` | — | **面板不完备 → 已 spawn 刷新**（在跑） |
| `update_moneyflow` | 尾 2026-10-19，落后 14td | **本机根本没有面板目录**（见下） |

结论：七条里只有两条真的断了，两条都是「冷启动」，其余是陈旧的二手描述。

### 2 moneyflow：一个「成功地点火了一个必然失败的活」的 gate

- 状态镜像随 git 带过来，写着 `panel.cutoff=2026-10-19 / n_symbols=5222`；`data/moneyflow` **不存在**。
  对读者来说，「补 14 天」和「从零拉 5226 只」是两个完全不同的动作，面上只印了前者。
- gate 每轮打印 `spawned detached rank pass` 并返回 0；真正死处的证据只在子进程日志里：
  `universe unavailable (0 codes) -- refusing honest exit 2`——`universe_codes()` 的 bars glob 指向
  `Money02/data/bars`，那是跑 W 车道回测那台机的本地面，bm-c 上没有。rank 戳因此停在 2026-10-13。

**修两处（出生地拦截，而不是事后补数）**

1. 宇宙面三级读：`Money02/data/bars` → `data/fundamental/eligibility.csv`（链内每机刷新，sibling 采集器
   早已这样读，解析器直接复用 `update_sina_mf.universe_codes`，不写第二份）→ 无则 gate **exit 2** 并写
   `mode=blocked: universe unavailable`，绝不 spawn；回答的是哪一级写进 `universe_source`。
2. panel 块以字节为准：`_panel_cutoff_from_bytes()` 量磁盘，镜像声明并列保留为 `mirror_cutoff`，
   不一致就打印；盘上无字节时 `cutoff=None + note="no panel bytes on this disk"`。

**实测证据**

- 修前：子进程 `universe unavailable (0 codes)`（logs/moneyflow_refresh.log 两行）。
- 修后同一 gate 直接跑 `rank`：`rank pass 2026-11-06: +5225 rows, 0 same-day skips, 1 not in rank face,
  702 not in universe, 0 mismatches`，`data/moneyflow/per/` 落 5,225 个文件。
- 随后 gate 以 first-pull 身份 spawn 全宇宙 daykline 刷新（5,226 只 × 2.5s ≈ 3.6h，checkpoint 断点续拉），
  开跑时 `done` 从 23 → 52 逐只推进；状态面如实写
  `panel.cutoff=2026-11-06 / cutoff_from_bytes=2026-11-06 / mirror_cutoff=2026-10-19 / complete=false`。
- 自检：`scripts/update_moneyflow.py selftest` **25/25 PASS**（S22 宇宙面三级腿、S23 panel 块字节优先腿；
  S11/S14 两条老腿按新事实钉死：S11 传 `elig_path` 保持无网络 hermetic，S14 把 `LANE_OWNER` 钉成 `bm-a`
  才还在测「非属主不写镜像」——不改这两条，车道换机后它们会静默变成空断言）。

### 3 归属声明的落地

`config/lane_hosts.json`（bm-a r1270 改派 + 本机补 `update_etf_daily`/`update_lhb_inst` 两条隐含项）本轮核实后
采纳：`owned` 面 `update_moneyflow` 现在能以 bm-c 属主身份写面板与状态，实跑已证明。

## 下一窗

- moneyflow 刷新 ETA ≈ 3.6h（若源健康）：完成后核对 `done=5226`、面板覆盖率、回一条 MSG 给 bm-a
  （面板尾到哪天 + IC 批能否按 watermark next_pick 开跑）。
- ah_panel 刷新结果核对（`status complete` 与其自身 overlap 校验）。
- 死窗遗产（`scripts/update_lhb_inst.py`、`scripts/zoo99_lhb_inst_netratio_probe.py`、结果件、卡 E420）
  本轮只跑到两脚本 selftest（13/13、12/12）通过即提交，**未重跑整批**——重跑归下一窗按「最终树上重跑而非重放」处理。