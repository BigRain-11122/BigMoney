# Data lane freshness -- 2026-11-12

Official reference: last day that must exist by 15:30 = **2026-11-11** (8797 calendar days loaded).

Verdict: **attention** -- 12/15 lanes in sync, 13/15 auditable from this machine, worst = `marks`.


## Whose disk these numbers are on

以本机 bm-c 的盘为基准：14 条在役车道里有 1 条的数字不在本机盘上：1 条在 bm-b 的盘上（309.29h 未报到）；留在本机盘上的 13 条里 13 条可核实。

- `bm-b`: marks (host down)
| lane | host | tail | missing (official days) | verdict | authority |
|---|---|---|---|---|---|
| `options` | bm-c | 2026-09-30 | 25: 2026-10-08, 2026-10-09, 2026-10-12, 2026-10-13, 2026-10-14, 2026-10-15 … | retired (copy said `stalled`) | unattributed |
| `sina_mf` | bm-c | 2026-10-26 | 12: 2026-10-27, 2026-10-28, 2026-10-29, 2026-10-30, 2026-11-02, 2026-11-03 … | in_sync (own window 12/20) | host_envelope |
| `marks` | bm-b | 2026-10-29 | 9: 2026-10-30, 2026-11-02, 2026-11-03, 2026-11-04, 2026-11-05, 2026-11-06 … | unverifiable (copy said `stalled`) | unattributed |
| `ah_panel` | bm-c | 2026-11-10 | 1: 2026-11-11 | behind_1d | host_copy |
| `moneyflow` | bm-c | 2026-11-10 | 1: 2026-11-11 | in_sync (own window 1/20) | host_envelope |
| `astock_daily` | bm-b | 2026-11-11 | 0 | in_sync | declared_takeover |
| `etf_panel` | bm-c | 2026-11-11 | 0 | in_sync | host_envelope |
| `futures` | bm-a | 2026-11-11 | 0 | in_sync | declared_takeover |
| `heat` | bm-a | 2026-11-11 | 0 | in_sync | declared_takeover |
| `lhb` | bm-a | 2026-11-11 | 0 | in_sync | declared_takeover |
| `lhb_inst` | bm-c | 2026-11-11 | 0 | in_sync | host_envelope |
| `minute_feed` | bm-c | 2026-11-11 | 0 | in_sync | host_copy |
| `repo` | bm-a | 2026-11-11 | 0 | in_sync | declared_takeover |
| `ths_panel` | bm-c | 2026-11-11 | 0 | in_sync | host_envelope |
| `zt_pool` | bm-c | 2026-11-11 | 0 | in_sync | host_copy |

## Lanes where a missed day cannot be recovered

- `marks`: an intraday tick capture: a day with no marks file cannot be rebuilt by any machine -- the file is append-only and the ticks it would have held are gone
- `ah_panel`: a premium pair day is quotable only from that day's closes

## Lanes judged against their own window

These lanes do not owe every official day: their collector refreshes on a rolling window of trading days, so a gap inside that window is the design and the verdict is `in_sync`. The row's `missing` column counts official days since the tail; the window below is the lane's own promise, and the sessions-left number says when that promise runs out.

- `sina_mf`: tail 2026-10-26, **12** official day(s) behind, window **20** trading days -> **9 more** session(s) may pass before this lane owes a refresh (it reads `stalled` once the gap passes 20). Basis: the collector's own no-op rule: it refreshes only when the panel tail is more than 20 trading days stale
- `moneyflow`: tail 2026-11-10, **1** official day(s) behind, window **20** trading days -> **20 more** session(s) may pass before this lane owes a refresh (it reads `stalled` once the gap passes 20). Basis: the collector's own no-op rule: it refreshes only when the panel tail is more than 20 trading days stale

## Who was awake on the days that are missing

Each missing day below is classified by its own collector. `takeover_possible` means another machine was awake inside the capture window and nobody declared a stand-in: that day was movable *at the time*. Every other cause means no machine was sampling. Either way the day is behind us -- a takeover declared today starts capturing today.

- `marks`: 9 missing day(s) after the lane's last captured day, out of 12 hole(s) recorded since the lane started (host_down 1, host_offhours 4, lane_missed 1, takeover_possible 6)

## Hosts that stopped reporting

These lanes cannot be certified here and the machine that is supposed to collect them has not written a heartbeat for more than 2.0h. Until it comes back the numbers below are this machine's stale copies, not the company's data.

- `bm-b`: last seen 2026-10-30T12:43:06+08:00 (309.29h ago) -- holding back marks

## Owners that stopped reporting

A different question from the section above: these machines have written no heartbeat for more than 24.0h, so the lanes they own are being judged from whatever was last committed. A lane here can still read `in_sync` -- the number is old, the owner is gone, and nobody would notice the day the file stops being written.

- `bm-a`: last seen 2026-11-11T01:14:51+08:00 (32.76h ago) -- owns futures, heat, lhb, repo
  - already covered by a declared stand-in: futures <- bm-c, heat <- bm-c, lhb <- bm-c, repo <- bm-c (nothing to wait for)
- `bm-b`: last seen 2026-10-30T12:43:06+08:00 (309.29h ago) -- owns astock_daily, marks
  - already covered by a declared stand-in: astock_daily <- bm-c (nothing to wait for)
  - nobody is covering these: marks

## Why some lanes cannot be certified here

A status envelope is committed by whichever machine ran the leg, and every machine also keeps its own gitignored copy of the data. Neither names its writer, so a tail that reads late can be a dead lane or a stale copy of a live one.

- `marks`: the envelope does not name the machine whose data it describes

## Tails read from a sample

The per-symbol panels hold thousands of files, so their tail is read through an evenly spaced sample rather than a full sweep. A sample can miss a single laggard symbol; it cannot miss a panel that stopped weeks ago. Each row below says how many symbols were read out of how many.

- `ah_panel`: 40 of 187 symbols read, tail 2026-11-10; the full scan holds it in 187 of 187 symbols (100.00%) (certified 2026-11-12T03:49:10)
- `moneyflow`: 40 of 5226 symbols read, tail 2026-11-10; the full scan holds it in 5,225 of 5,226 symbols (100.00%) (certified 2026-11-12T03:49:10)
- `astock_daily`: 40 of 5223 symbols read, tail 2026-11-11; the full scan holds it in 1,985 of 5,223 symbols (38.00%) (certified 2026-11-12T03:49:10)

Full-scan certification of exactly these rows: `scripts/data_lane_freshness.py certify` -> `docs/data_lanes/TAIL_CERTIFICATION.md` (it re-reads every file and names the symbols that sit behind the newest bar).

## Lanes whose clock is the statute, not the trading calendar

A quarterly report period cannot be judged by an official trading day: the unit is the period and the deadline is statutory.

| lane | host | panel cutoff | statute demands | missing | verdict | takeover path |
|---|---|---|---|---|---|---|
| `fund_statements` | bm-c | 20260930 | 20260930 (due 2026-10-31) | 0 | in_sync | yes |

