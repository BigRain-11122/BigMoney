# Data lane freshness -- 2026-11-08

Official reference: last day that must exist by 15:30 = **2026-11-06** (8797 calendar days loaded).

Verdict: **host_down** -- 9/11 lanes in sync, 9/11 auditable from this machine, worst = `marks`.


## Whose disk these numbers are on

以本机 bm-c 的盘为基准：10 条在役车道里有 1 条的数字不在本机盘上：1 条在 bm-b 的盘上（211.3h 未报到）；留在本机盘上的 9 条里 9 条可核实。

- `bm-b`: marks (host down)
| lane | host | tail | missing (official days) | verdict | authority |
|---|---|---|---|---|---|
| `options` | bm-c | 2026-09-30 | 22: 2026-10-08, 2026-10-09, 2026-10-12, 2026-10-13, 2026-10-14, 2026-10-15 … | retired (copy said `stalled`) | unattributed |
| `marks` | bm-b | 2026-10-29 | 6: 2026-10-30, 2026-11-02, 2026-11-03, 2026-11-04, 2026-11-05, 2026-11-06 | unverifiable (copy said `stalled`) | unattributed |
| `astock_daily` | bm-b | 2026-11-06 | 0 | in_sync | declared_takeover |
| `etf_panel` | bm-c | 2026-11-06 | 0 | in_sync | host_envelope |
| `futures` | bm-a | 2026-11-06 | 0 | in_sync | host_envelope |
| `heat` | bm-a | 2026-11-06 | 0 | in_sync | host_envelope |
| `lhb` | bm-a | 2026-11-06 | 0 | in_sync | host_envelope |
| `lhb_inst` | bm-c | 2026-11-06 | 0 | in_sync | host_envelope |
| `moneyflow` | bm-c | 2026-11-06 | 0 | in_sync | host_envelope |
| `repo` | bm-a | 2026-11-06 | 0 | in_sync | host_envelope |
| `zt_pool` | bm-c | 2026-11-06 | 0 | in_sync | host_copy |

## Lanes where a missed day cannot be recovered

- `marks`: an intraday tick capture: a day with no marks file cannot be rebuilt by any machine -- the file is append-only and the ticks it would have held are gone

## Who was awake on the days that are missing

Each missing day below is classified by its own collector. `takeover_possible` means another machine was awake inside the capture window and nobody declared a stand-in: that day was movable *at the time*. Every other cause means no machine was sampling. Either way the day is behind us -- a takeover declared today starts capturing today.

- `marks`: 6 missing day(s) after the lane's last captured day, out of 9 hole(s) recorded since the lane started (host_down 2, host_offhours 4, lane_missed 1, takeover_possible 2)

## Hosts that stopped reporting

These lanes cannot be certified here and the machine that is supposed to collect them has not written a heartbeat for more than 2.0h. Until it comes back the numbers below are this machine's stale copies, not the company's data.

- `bm-b`: last seen 2026-10-30T12:43:06+08:00 (211.3h ago) -- holding back marks

## Why some lanes cannot be certified here

A status envelope is committed by whichever machine ran the leg, and every machine also keeps its own gitignored copy of the data. Neither names its writer, so a tail that reads late can be a dead lane or a stale copy of a live one.

- `marks`: the envelope does not name the machine whose data it describes

## Tails read from a sample

The per-symbol panels hold thousands of files, so their tail is read through an evenly spaced sample rather than a full sweep. A sample can miss a single laggard symbol; it cannot miss a panel that stopped weeks ago. Each row below says how many symbols were read out of how many.

- `astock_daily`: 40 of 5223 symbols read, tail 2026-11-06; the full scan holds it in 5,216 of 5,223 symbols (99.87%) (certified 2026-11-08T07:59:06)
- `moneyflow`: 40 of 5226 symbols read, tail 2026-11-06; the full scan holds it in 5,225 of 5,226 symbols (100.00%) (certified 2026-11-08T07:59:06)

Full-scan certification of exactly these rows: `scripts/data_lane_freshness.py certify` -> `docs/data_lanes/TAIL_CERTIFICATION.md` (it re-reads every file and names the symbols that sit behind the newest bar).

## Lanes whose clock is the statute, not the trading calendar

A quarterly report period cannot be judged by an official trading day: the unit is the period and the deadline is statutory.

| lane | host | panel cutoff | statute demands | missing | verdict | takeover path |
|---|---|---|---|---|---|---|
| `fund_statements` | bm-c | 20260930 | 20260930 (due 2026-10-31) | 0 | in_sync | yes |

