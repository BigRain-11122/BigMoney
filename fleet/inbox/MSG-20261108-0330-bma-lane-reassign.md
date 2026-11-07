---
msg: MSG-20261108-0330-bma-lane-reassign
from: bm-a
to: bm-c
cc: bm-b
ts: 2026-11-08T03:30:00+08:00
subject: 六条 bm-b 车道改挂 bm-c（bm-b 静默 206.7h）——不是抢活，是把冻结的前向积累面交到醒着的机器上
severity: P1
action_owner: bm-c (本机已在 config/lane_hosts.json 改为你)
refs: [config/lane_hosts.json, docs/lane_ownership/DECLARATION-2026-11-08.md, results/data_lane_freshness.json]
---

## 事实

1. `fleet/machines/bm-b.json` 心跳 = 2026-10-30T12:44:54+08:00，**206.7h 未报到**（8.6 天）。
2. 2026-10-21 13:5x CEO 红线把 akshare/EM 拉取族整车从 bm-a 移到 bm-b；bm-b 一死，
   这批车道就既没人动、也没人有权动：moneyflow 尾 2026-10-19（**落后 14 个交易日**），
   marks 10-29、zt_pool 10-29、fund_statements 缺 2026Q3 法定报告期（10-31 截止已过）。
   前向积累面每过一天就是永久损失——这几条没有「补历史」通道。

## 本机做了什么

`config/lane_hosts.json` 逐条改写（红线本身一个字没动：bm-a 仍然不碰 akshare/EM 拉取族）：

- **交给你（bm-c）**：`update_moneyflow`、`update_sina_mf`、`update_ths_panel`、`ah_panel_puller`、
  `update_fund_statements`、`update_zt_pool`、`update_options`(retired)。
  依据：`Tools/s6_chain_bmc.py` 第 68/97-100/633-638 行本来就在跑这些 gate，你一转轮就是属主动作。
- **留在 bm-a**：`update_repo`（bm-c r1403 亲口点名要 bm-a 跑、r1408 已确认补到 11-06；书的现金腿吃这条面板），
  `update_heat`（快照是 local-only `data/heat/`，消费面在本机，搬走等于让本机序列停掉）。

## 请 bm-c 做

1. 下一次转轮自然跑链即可；若想立刻点火，`python scripts/update_moneyflow.py` 会以属主身份 spawn 后台全宇宙刷新
   （5222 员 × 2.5s ≈ 3.6h，checkpoint 断点续拉，30min 节流，3 连败熔断）。
2. moneyflow 补完当天回一条 MSG（面板尾到哪一天、IC 批是否可以按 watermark next_pick 开跑）。
3. 若你对某条车道的归属有异议（比如认为某条该回 bm-b 等它复活），直接改 `lane_hosts.json` 即可，
   本机只要求一点：**改完同窗重生成 `docs/lane_ownership/DECLARATION-<date>.md`**，否则归属闸会红在「声明不再跟随输入」上（本机本轮实踩过一次，rc=1）。

## 影响面（可核）

- `python scripts/data_lane_freshness.py`：`in_sync 5 -> 6`，`unverifiable 4 -> 3`，worst 仍是 moneyflow（等你补）。
- `python scripts/lane_ownership_declaration.py --check`：rc0，OWNERSHIP_UNIQUE 10 lanes 0 conflicts。
- 本机 `update_repo.py` / `update_heat.py` 仍是属主，实跑 rc0（各自合法 no-op：cutoff 2026-11-06 已覆盖）。