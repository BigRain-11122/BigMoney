# Data lane freshness -- 2026-11-09

Official reference: last day that must exist by 15:30 = **2026-11-09** (8797 calendar days loaded).

Verdict: **attention** -- 2/15 lanes in sync, 6/15 auditable from this machine, worst = `ths_panel`.


## Whose disk these numbers are on

以本机 bm-a 的盘为基准：14 条在役车道里有 8 条的数字不在本机盘上：7 条在 bm-c 的盘上（9.62h 未报到）、1 条在 bm-b 的盘上（246.87h 未报到）；留在本机盘上的 6 条里 6 条可核实。

- `bm-c`: ah_panel, etf_panel, lhb_inst, minute_feed, sina_mf, ths_panel, zt_pool (host down)
- `bm-b`: marks (host down)
| lane | host | tail | missing (official days) | verdict | authority |
|---|---|---|---|---|---|
| `options` | bm-c | 2026-09-30 | 23: 2026-10-08, 2026-10-09, 2026-10-12, 2026-10-13, 2026-10-14, 2026-10-15 … | retired (copy said `stalled`) | unattributed |
| `ths_panel` | bm-c | 2026-10-19 | 15: 2026-10-20, 2026-10-21, 2026-10-22, 2026-10-23, 2026-10-26, 2026-10-27 … | unverifiable (copy said `stalled`) | unattributed |
| `ah_panel` | bm-c | 2026-10-26 | 10: 2026-10-27, 2026-10-28, 2026-10-29, 2026-10-30, 2026-11-02, 2026-11-03 … | unverifiable (copy said `stalled`) | non_host_copy |
| `sina_mf` | bm-c | 2026-10-26 | 10: 2026-10-27, 2026-10-28, 2026-10-29, 2026-10-30, 2026-11-02, 2026-11-03 … | unverifiable (copy said `in_sync`) | unattributed |
| `marks` | bm-b | 2026-10-29 | 7: 2026-10-30, 2026-11-02, 2026-11-03, 2026-11-04, 2026-11-05, 2026-11-06 … | unverifiable (copy said `stalled`) | unattributed |
| `zt_pool` | bm-c | 2026-10-29 | 7: 2026-10-30, 2026-11-02, 2026-11-03, 2026-11-04, 2026-11-05, 2026-11-06 … | unverifiable (copy said `stalled`) | non_host_copy |
| `astock_daily` | bm-b | 2026-11-06 | 1: 2026-11-09 | today_pending | declared_takeover |
| `etf_panel` | bm-c | 2026-11-06 | 1: 2026-11-09 | unverifiable (copy said `today_pending`) | non_host_envelope |
| `lhb` | bm-a | 2026-11-06 | 1: 2026-11-09 | today_pending | host_envelope |
| `minute_feed` | bm-c | 2026-11-06 | 1: 2026-11-09 | unverifiable (copy said `today_pending`) | non_host_copy |
| `moneyflow` | bm-c | 2026-11-06 | 1: 2026-11-09 | today_pending | host_envelope |
| `repo` | bm-a | 2026-11-06 | 1: 2026-11-09 | today_pending | host_envelope |
| `futures` | bm-a | 2026-11-09 | 0 | in_sync | host_envelope |
| `heat` | bm-a | 2026-11-09 | 0 | in_sync | host_envelope |
| `lhb_inst` | bm-c | -- | 0 | absent | unattributed |

## Lanes where a missed day cannot be recovered

- `ah_panel`: a premium pair day is quotable only from that day's closes
- `marks`: an intraday tick capture: a day with no marks file cannot be rebuilt by any machine -- the file is append-only and the ticks it would have held are gone
- `zt_pool`: pool day slices are terminal at the close; no superset arrives later

## Who was awake on the days that are missing

Each missing day below is classified by its own collector. `takeover_possible` means another machine was awake inside the capture window and nobody declared a stand-in: that day was movable *at the time*. Every other cause means no machine was sampling. Either way the day is behind us -- a takeover declared today starts capturing today.

- `marks`: 7 missing day(s) after the lane's last captured day, out of 9 hole(s) recorded since the lane started (host_down 2, host_offhours 4, lane_missed 1, takeover_possible 2)

## Hosts that stopped reporting

These lanes cannot be certified here and the machine that is supposed to collect them has not written a heartbeat for more than 2.0h. Until it comes back the numbers below are this machine's stale copies, not the company's data.

- `bm-b`: last seen 2026-10-30T12:43:06+08:00 (246.87h ago) -- holding back marks
- `bm-c`: last seen 2026-11-09T09:58:00+08:00 (9.62h ago) -- holding back ths_panel, ah_panel, sina_mf, zt_pool, etf_panel, minute_feed

## Owners that stopped reporting

A different question from the section above: these machines have written no heartbeat for more than 24.0h, so the lanes they own are being judged from whatever was last committed. A lane here can still read `in_sync` -- the number is old, the owner is gone, and nobody would notice the day the file stops being written.

- `bm-b`: last seen 2026-10-30T12:43:06+08:00 (246.87h ago) -- owns astock_daily, marks
  - already covered by a declared stand-in: astock_daily <- bm-a (nothing to wait for)
  - nobody is covering these: marks

## Lanes nobody can pick up while the host is away

These are not waiting on patience. The host is silent and the collector has no declared-takeover path, so **no machine is allowed to move them** -- the last written envelope stays the newest number the company has, and each day that passes is gone for good where the face is forward-accumulation only. Unblocking one is a decision (reassign the lane, or give its collector the same stale-takeover rule the other eight lanes already have), not a retry.

- `ah_panel`: writer `ah_panel_puller` has no `TAKEOVER: declared stale takeover of` path
- `minute_feed`: writer `update_minute_feed` has no `TAKEOVER: declared stale takeover of` path
- `sina_mf`: writer `update_sina_mf` has no `TAKEOVER: declared stale takeover of` path
- `ths_panel`: writer `update_ths_panel` has no `TAKEOVER: declared stale takeover of` path

## Why some lanes cannot be certified here

A status envelope is committed by whichever machine ran the leg, and every machine also keeps its own gitignored copy of the data. Neither names its writer, so a tail that reads late can be a dead lane or a stale copy of a live one.

- `ths_panel`: the envelope does not name the machine whose data it describes
- `ah_panel`: read from this machine's local copy; the lane is hosted by bm-c
- `sina_mf`: the envelope does not name the machine whose data it describes
- `marks`: the envelope does not name the machine whose data it describes
- `zt_pool`: read from this machine's local copy; the lane is hosted by bm-c
- `etf_panel`: the envelope was written by bm-a, not by the lane host bm-c
- `minute_feed`: read from this machine's local copy; the lane is hosted by bm-c

## Envelopes older than the panel they describe

A status envelope is a committed file, so a branch switch or a rebase can restore an older copy of it. Where this host can read the panel itself the panel is the measurement: the staleness is printed here instead of being read as a stall.

- `futures`: envelope says 2026-11-06, panel holds 2026-11-09 (1 official days behind)

## Copies that hold less than their envelope claims

本机副本落后：5 条可读面板里有 2 条读到的不是车道认证的那一天的数：moneyflow 差 18 个交易日（本盘 2026-10-13 / 车道 2026-11-06，数据在 bm-c 盘上）；ah_panel 差 6 个交易日（本盘 2026-10-16 / 车道 2026-10-26，数据在 bm-c 盘上）。本机发起的研究要用这些车道的数据，读的是旧盘。

The envelope is what some machine says it collected; the panel is what is on this disk. Where the copy is behind its own envelope the row cannot be read as current here, even though the lane itself may be alive elsewhere.

- `ah_panel`: envelope says 2026-10-26, this copy holds 2026-10-16 (6 official days behind)
- `moneyflow`: envelope says 2026-11-06, this copy holds 2026-10-13 (18 official days behind)

## Tails read from a sample

The per-symbol panels hold thousands of files, so their tail is read through an evenly spaced sample rather than a full sweep. A sample can miss a single laggard symbol; it cannot miss a panel that stopped weeks ago. Each row below says how many symbols were read out of how many.

- `ah_panel`: 40 of 186 symbols read, tail 2026-10-16 (holder share unknown -- run `certify`)
- `astock_daily`: 40 of 5222 symbols read, tail 2026-11-06; the full scan holds it in 5,216 of 5,223 symbols (99.87%) (certified 2026-11-08T07:59:06)
- `moneyflow`: 40 of 5222 symbols read, tail 2026-10-13; the full scan holds it in 5,225 of 5,226 symbols (100.00%) (certified 2026-11-08T07:59:06)

Full-scan certification of exactly these rows: `scripts/data_lane_freshness.py certify` -> `docs/data_lanes/TAIL_CERTIFICATION.md` (it re-reads every file and names the symbols that sit behind the newest bar).

## Lanes whose clock is the statute, not the trading calendar

A quarterly report period cannot be judged by an official trading day: the unit is the period and the deadline is statutory.

| lane | host | panel cutoff | statute demands | missing | verdict | takeover path |
|---|---|---|---|---|---|---|
| `fund_statements` | bm-c | 20260630 | 20260930 (due 2026-10-31) | 1 | period_missing | yes |

- `fund_statements`: the statute demanded 20260930 from 2026-10-31; the panel on this disk stops at 20260630 (1 period(s) missing) -- host `bm-c` silent 9.62h

