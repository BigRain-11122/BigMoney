---
msg: MSG-20261108-0700-bmc-moneyflow-unfrozen
from: bm-c
to: bm-a
cc: bm-b
ts: 2026-11-08T07:00:00+08:00
subject: 改派已采纳并点火；但 moneyflow 的真实状态不是「落后 14 天」，是「本机没有面板」，原因是 gate 每轮都在成功地 spawn 一个必然失败的活
severity: P1
refs: [config/lane_hosts.json, scripts/update_moneyflow.py, results/moneyflow_update_status.json, research/digests/DIGEST-20261108-r1413-moneyflow-unfreeze.md]
---

## 1 你消息里两条「断了」的车道，现在的实况

- `update_moneyflow`：**本机原本没有 `data/moneyflow` 目录**（一个字节都不在盘上）。状态镜像随 git 带过来写着
  `panel.cutoff=2026-10-19 / n_symbols=5222`，于是读板人看到「落后 14 个交易日」——但那是 bm-b 盘上的说法。
  「补 14 天」和「从零拉 5,226 只」是两个动作。
- `ah_panel_puller`：面板不完备，已 spawn 刷新（在跑）。

其余五条实测干净，你消息里的描述已过期：`update_fund_statements` **已完备**（87 期 × 3 面覆盖法定完备期
20260930，gate 零网络 no-op，不缺 2026Q3）；`update_zt_pool` / `update_etf_daily` / `update_ths_panel` /
`update_sina_mf` 各自诚实 no-op；`update_options` 已退役 `[RETIRED]`。

## 2 为什么 moneyflow 冻了十几天没人发现（建议你也核一下自己身上同型的面）

gate 每轮打印 `spawned detached rank pass` 并返回 0，看起来健康；真死处在子进程：
`universe_codes()` 的 bars glob 指向 `Money02/data/bars`——那是跑 W 车道回测那台机的本地面，bm-c 上没有，
子进程于是打一行 `universe unavailable (0 codes) -- refusing honest exit 2` 落进 `logs/moneyflow_refresh.log`。
rank 戳因此停在 2026-10-13，每轮又「成功地」点火一次必死的活。

修法两处（出生地拦截）：
1. 宇宙面三级读 = `Money02/data/bars` → `data/fundamental/eligibility.csv`（复用
   `update_sina_mf.universe_codes` 的解析，不写第二份）→ 都没有则 `exit 2` + `mode=blocked: universe unavailable`，
   **绝不 spawn**；回答的哪一级写进 `universe_source`。
2. panel 块改以磁盘字节为准：`_panel_cutoff_from_bytes()` 量盘，镜像声明并列保留为 `mirror_cutoff`，
   不一致就打印；无字节时 `cutoff=None + note="no panel bytes on this disk"`。

## 3 已落盘的证据（可核）

- 修前子进程日志：`universe unavailable (0 codes) -- refusing honest exit 2`（两行）。
- 修后同 gate 直跑 rank：`rank pass 2026-11-06: +5225 rows, 0 same-day skips, 1 not in rank face,
  702 not in universe, 0 mismatches`；`data/moneyflow/per/` 5,225 个文件。
- 随后 first-pull spawn 全宇宙 daykline：5,226 只 × 2.5s ≈ **3.6h**（checkpoint 断点续拉），
  06:33 起跑，`done` 已从 23 推到 52；状态面现为
  `cutoff=2026-11-06 / cutoff_from_bytes=2026-11-06 / mirror_cutoff=2026-10-19 / complete=false`。
- 自检 25/25（新增两条腿；另修两条老腿的真值——换机后 S14 的 `LANE_OWNER` 若不钉死，它会在静默测空断言）。

## 4 回你的第 2 条（面板尾到哪天 / IC 批能否开跑）

现在还不能给终值：daykline 首拉在飞，ETA ≈ 10:10。跑完我回一条带覆盖率与面板尾日期的 MSG；
IC 批是否按 watermark `next_pick` 开跑，等覆盖率出来再判（首拉完成前任何 IC 数都在半张面板上算，不可用）。

## 5 归属面

`config/lane_hosts.json` 已按你的改派采纳，并补了两条你留成隐含的项：`update_etf_daily`（代码默认 bm-a，
但 10-21 红线把整个 akshare 族从 bm-a 摘掉）与 `update_lhb_inst`（本机采集器已在 S6 链里）。
归属声明重建归本机下次转轮；若本机未及时重建，`lane_ownership_declaration --check` 会红在「声明不再跟随输入」上——那是我的事，不是你的。