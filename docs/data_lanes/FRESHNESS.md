# Data lane freshness -- 2026-11-13

Official reference: last day that must exist by 15:30 = **2026-11-13** (8797 calendar days loaded).

Verdict: **attention** -- 5/15 lanes in sync, 10/15 auditable from this machine, worst = `ths_panel`.


## Whose disk these numbers are on

以本机 bm-a 的盘为基准：14 条在役车道里有 7 条的数字不在本机盘上：7 条在 bm-c 的盘上（心跳 0.7h 前）；留在本机盘上的 7 条里 7 条可核实。

- `bm-c`: ah_panel, astock_daily, lhb, marks, minute_feed, ths_panel, zt_pool
| lane | host | tail | missing (official days) | verdict | authority |
|---|---|---|---|---|---|
| `options` | bm-c | 2026-09-30 | 27: 2026-10-08, 2026-10-09, 2026-10-12, 2026-10-13, 2026-10-14, 2026-10-15 … | retired (copy said `stalled`) | unattributed |
| `ths_panel` | bm-c | 2026-10-19 | 19: 2026-10-20, 2026-10-21, 2026-10-22, 2026-10-23, 2026-10-26, 2026-10-27 … | unverifiable (copy said `stalled`) | unattributed |
| `sina_mf` | bm-c | 2026-10-26 | 14: 2026-10-27, 2026-10-28, 2026-10-29, 2026-10-30, 2026-11-02, 2026-11-03 … | in_sync (own window 14/20) | host_envelope |
| `moneyflow` | bm-c | 2026-11-10 | 3: 2026-11-11, 2026-11-12, 2026-11-13 | in_sync (own window 3/20) | host_envelope |
| `lhb` | bm-a | 2026-11-11 | 2: 2026-11-12, 2026-11-13 | stalled | declared_takeover |
| `lhb_inst` | bm-c | 2026-11-11 | 2: 2026-11-12, 2026-11-13 | stalled | host_envelope |
| `ah_panel` | bm-c | 2026-11-12 | 1: 2026-11-13 | unverifiable (copy said `today_pending`) | non_host_copy |
| `astock_daily` | bm-b | 2026-11-12 | 1: 2026-11-13 | today_pending | declared_takeover |
| `etf_panel` | bm-c | 2026-11-12 | 1: 2026-11-13 | today_pending | host_envelope |
| `marks` | bm-b | 2026-11-12 | 1: 2026-11-13 | today_pending | declared_takeover |
| `minute_feed` | bm-c | 2026-11-12 | 1: 2026-11-13 | unverifiable (copy said `today_pending`) | non_host_copy |
| `zt_pool` | bm-c | 2026-11-12 | 1: 2026-11-13 | unverifiable (copy said `today_pending`) | non_host_copy |
| `futures` | bm-a | 2026-11-13 | 0 | in_sync | host_envelope |
| `heat` | bm-a | 2026-11-13 | 0 | in_sync | host_envelope |
| `repo` | bm-a | 2026-11-13 | 0 | in_sync | host_envelope |

## Lanes where a missed day cannot be recovered

- `lhb_inst`: vendor re-serves the range on later pulls, so a missed month is recoverable by moving FIRST_DATE; the panel is append-only by key

## Lanes judged against their own window

These lanes do not owe every official day: their collector refreshes on a rolling window of trading days, so a gap inside that window is the design and the verdict is `in_sync`. The row's `missing` column counts official days since the tail; the window below is the lane's own promise, and the sessions-left number says when that promise runs out.

- `sina_mf`：尾部 2026-10-26，落后官方日历 **14** 个交易日，滚动窗 **20** 个交易日 → 还可再走 **7** 个交易日才欠一次刷新（差距超过 20 即读 `stalled`）。依据：采集器自己的 no-op 规则：只有面板尾部落后超过 20 个交易日才刷新
- `moneyflow`：尾部 2026-11-10，落后官方日历 **3** 个交易日，滚动窗 **20** 个交易日 → 还可再走 **18** 个交易日才欠一次刷新（差距超过 20 即读 `stalled`）。依据：采集器自己的 no-op 规则：只有面板尾部落后超过 20 个交易日才刷新

## Who was awake on the days that are missing

Each missing day below is classified by its own collector. `takeover_possible` means another machine was awake inside the capture window and nobody declared a stand-in: that day was movable *at the time*. Every other cause means no machine was sampling. Either way the day is behind us -- a takeover declared today starts capturing today.

- `marks`: 1 missing day(s) after the lane's last captured day, out of 12 hole(s) recorded since the lane started (host_down 1, host_offhours 4, lane_missed 1, takeover_possible 6)

## Owners that stopped reporting

A different question from the section above: these machines have written no heartbeat for more than 24.0h, so the lanes they own are being judged from whatever was last committed. A lane here can still read `in_sync` -- the number is old, the owner is gone, and nobody would notice the day the file stops being written.

- `bm-b`: last seen 2026-10-30T12:43:06+08:00 (342.75h ago) -- owns astock_daily, marks
  - already covered by a declared stand-in: astock_daily <- bm-c, marks <- bm-c (nothing to wait for)

## Why some lanes cannot be certified here

A status envelope is committed by whichever machine ran the leg, and every machine also keeps its own gitignored copy of the data. Neither names its writer, so a tail that reads late can be a dead lane or a stale copy of a live one.

- `ths_panel`: the envelope does not name the machine whose data it describes
- `ah_panel`: read from this machine's local copy; the lane is hosted by bm-c
- `minute_feed`: read from this machine's local copy; the lane is hosted by bm-c
- `zt_pool`: read from this machine's local copy; the lane is hosted by bm-c

## Envelopes older than the panel they describe

A status envelope is a committed file, so a branch switch or a rebase can restore an older copy of it. Where this host can read the panel itself the panel is the measurement: the staleness is printed here instead of being read as a stall.

- `futures`: envelope says 2026-11-11, panel holds 2026-11-13 (2 official days behind)

## Copies that hold less than their envelope claims

本机副本落后：5 条可读面板里有 3 条读到的不是车道认证的那一天的数：moneyflow 差 20 个交易日（本盘 2026-10-13 / 车道 2026-11-10，数据在 bm-c 盘上）；ah_panel 差 19 个交易日（本盘 2026-10-16 / 车道 2026-11-12，数据在 bm-c 盘上）；astock_daily 差 2 个交易日（本盘 2026-11-10 / 车道 2026-11-12，数据在 bm-c 盘上）。本机发起的研究要用这些车道的数据，读的是旧盘。

The envelope is what some machine says it collected; the panel is what is on this disk. Where the copy is behind its own envelope the row cannot be read as current here, even though the lane itself may be alive elsewhere.

- `moneyflow`: envelope says 2026-11-10, this copy holds 2026-10-13 (20 official days behind)
- `ah_panel`: envelope says 2026-11-12, this copy holds 2026-10-16 (19 official days behind)
- `astock_daily`: envelope says 2026-11-12, this copy holds 2026-11-10 (2 official days behind)

## Tails read from a sample

The per-symbol panels hold thousands of files, so their tail is read through an evenly spaced sample rather than a full sweep. A sample can miss a single laggard symbol; it cannot miss a panel that stopped weeks ago. Each row below says how many symbols were read out of how many.

- `moneyflow`: 40 of 5222 symbols read, tail 2026-10-13 (certification read 2026-10-19, this row reads 2026-10-13 -- this row is behind it, so its counts are not quoted here)
- `ah_panel`: 40 of 186 symbols read, tail 2026-10-16; the full scan holds it in 186 of 186 symbols (100.00%) (certified 2026-11-13T19:27:37)
- `astock_daily`: 40 of 5222 symbols read, tail 2026-11-10; the full scan holds it in 4,280 of 5,222 symbols (81.96%) (certified 2026-11-13T19:27:37)

Full-scan certification of exactly these rows: `scripts/data_lane_freshness.py certify` -> `docs/data_lanes/TAIL_CERTIFICATION.md` (it re-reads every file and names the symbols that sit behind the newest bar).

## Lanes whose clock is the statute, not the trading calendar

A quarterly report period cannot be judged by an official trading day: the unit is the period and the deadline is statutory.

| lane | host | panel cutoff | statute demands | missing | verdict | takeover path |
|---|---|---|---|---|---|---|
| `fund_statements` | bm-c | 20260630 | 20260930 (due 2026-10-31) | 1 | period_missing | yes |

- `fund_statements`: the statute demanded 20260930 from 2026-10-31; the panel on this disk stops at 20260630 (1 period(s) missing) -- host `bm-c` silent 0.7h

