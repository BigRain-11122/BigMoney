# Data lane freshness -- 2026-11-17

Official reference: last day that must exist by 15:30 = **2026-11-17** (8797 calendar days loaded).

Verdict: **attention** -- 3/15 lanes in sync, 14/15 auditable from this machine, worst = `marks`.

Built on **bm-c** at 2026-11-17T16:07:00: every tail and period below is a reading of that machine's disk. A copy of this file on another machine says nothing about that machine's panels -- run the board there to read its own bytes.


## Whose disk these numbers are on

以本机 bm-c 的盘为基准：14 条在役车道的数字全都落在本机盘上，其中 14 条有署名可核实。

| lane | host | tail | missing (official days) | verdict | authority |
|---|---|---|---|---|---|
| `options` | bm-c | 2026-09-30 | 29: 2026-10-08, 2026-10-09, 2026-10-12, 2026-10-13, 2026-10-14, 2026-10-15 … | retired (copy said `stalled`) | unattributed |
| `sina_mf` | bm-c | 2026-10-26 | 16: 2026-10-27, 2026-10-28, 2026-10-29, 2026-10-30, 2026-11-02, 2026-11-03 … | in_sync (own window 16/20) | host_envelope |
| `moneyflow` | bm-c | 2026-11-10 | 5: 2026-11-11, 2026-11-12, 2026-11-13, 2026-11-16, 2026-11-17 | in_sync (own window 5/20) | host_envelope |
| `marks` | bm-b | 2026-11-12 | 3: 2026-11-13, 2026-11-16, 2026-11-17 | stalled | declared_takeover |
| `heat` | bm-a | 2026-11-13 | 2: 2026-11-16, 2026-11-17 | stalled | host_envelope |
| `lhb` | bm-a | 2026-11-13 | 2: 2026-11-16, 2026-11-17 | stalled | host_envelope |
| `lhb_inst` | bm-c | 2026-11-13 | 2: 2026-11-16, 2026-11-17 | stalled | host_envelope |
| `repo` | bm-a | 2026-11-13 | 2: 2026-11-16, 2026-11-17 | stalled | declared_takeover |
| `ah_panel` | bm-c | 2026-11-16 | 1: 2026-11-17 | today_pending | host_copy |
| `astock_daily` | bm-b | 2026-11-16 | 1: 2026-11-17 | today_pending | declared_takeover |
| `etf_panel` | bm-c | 2026-11-16 | 1: 2026-11-17 | today_pending | host_envelope |
| `futures` | bm-a | 2026-11-16 | 1: 2026-11-17 | today_pending | host_envelope |
| `minute_feed` | bm-c | 2026-11-16 | 1: 2026-11-17 | today_pending | host_copy |
| `ths_panel` | bm-c | 2026-11-16 | 1: 2026-11-17 | today_pending | host_envelope |
| `zt_pool` | bm-c | 2026-11-17 | 0 | in_sync | host_copy |

## Lanes where a missed day cannot be recovered

- `marks`: an intraday tick capture: a day with no marks file cannot be rebuilt by any machine -- the file is append-only and the ticks it would have held are gone
- `heat`: a missed day is permanent: the guba rank is a live rolling list with no retrievable history (HEAT_ATTENTION_SPEC §1)
- `lhb_inst`: vendor re-serves the range on later pulls, so a missed month is recoverable by moving FIRST_DATE; the panel is append-only by key

## Lanes judged against their own window

These lanes do not owe every official day: their collector refreshes on a rolling window of trading days, so a gap inside that window is the design and the verdict is `in_sync`. The row's `missing` column counts official days since the tail; the window below is the lane's own promise, and the sessions-left number says when that promise runs out.

- `sina_mf`：尾部 2026-10-26，落后官方日历 **16** 个交易日，滚动窗 **20** 个交易日 → 还可再走 **5** 个交易日才欠一次刷新（差距超过 20 即读 `stalled`）。依据：采集器自己的 no-op 规则：只有面板尾部落后超过 20 个交易日才刷新
- `moneyflow`：尾部 2026-11-10，落后官方日历 **5** 个交易日，滚动窗 **20** 个交易日 → 还可再走 **16** 个交易日才欠一次刷新（差距超过 20 即读 `stalled`）。依据同上（本节首行）

## Who was awake on the days that are missing

Each missing day below is classified by its own collector. `takeover_possible` means another machine was awake inside the capture window and nobody declared a stand-in: that day was movable *at the time*. Every other cause means no machine was sampling. Either way the day is behind us -- a takeover declared today starts capturing today.

- `marks`: 3 missing day(s) after the lane's last captured day, out of 14 hole(s) recorded since the lane started (host_down 1, host_offhours 4, lane_missed 1, takeover_possible 8)

## Owners that stopped reporting

A different question from the section above: these machines have written no heartbeat for more than 24.0h, so the lanes they own are being judged from whatever was last committed. A lane here can still read `in_sync` -- the number is old, the owner is gone, and nobody would notice the day the file stops being written.

- `bm-b`: last seen 2026-10-30T12:43:06+08:00 (435.4h ago) -- owns astock_daily, marks
  - already covered by a declared stand-in: astock_daily <- bm-c, marks <- bm-c (nothing to wait for)

## Envelopes older than the panel they describe

A status envelope is a committed file, so a branch switch or a rebase can restore an older copy of it. Where this host can read the panel itself the panel is the measurement: the staleness is printed here instead of being read as a stall.

- `futures`: envelope says 2026-11-13, panel holds 2026-11-16 (1 official days behind)

## Members sitting outside the active cohort

These are named by the face that audits the panel, with the reason the lane's own receipt gives. A pinned member and a source that ended are decisions already taken; a member with **no declaration** is a feed that stopped, and that is the only line here that needs somebody to act.

- `etf_panel`: `510880_t73` (declared_out_of_scope@2026-09-22), `sh512390` (source_ended@2026-09-04) -- all declared (audited by exchange_calendar_audit (E136))

## Tails read from a sample

The per-symbol panels hold thousands of files, so their tail is read through an evenly spaced sample rather than a full sweep. A sample can miss a single laggard symbol; it cannot miss a panel that stopped weeks ago. Each row below says how many symbols were read out of how many.

- `moneyflow`: 40 of 5226 symbols read, tail 2026-11-10; the full scan holds it in 5,225 of 5,226 symbols (100.00%) (certified 2026-11-17T15:56:49)
- `ah_panel`: 40 of 187 symbols read, tail 2026-11-16; the full scan holds it in 186 of 187 symbols (99.47%) (certified 2026-11-17T15:56:49)
- `astock_daily`: 40 of 5221 symbols read, tail 2026-11-16; the full scan holds it in 5,205 of 5,221 symbols (99.69%) (certified 2026-11-17T15:56:49)

Full-scan certification of exactly these rows: `scripts/data_lane_freshness.py certify` -> `docs/data_lanes/TAIL_CERTIFICATION.md` (it re-reads every file and names the symbols that sit behind the newest bar).

## Lanes whose clock is the statute, not the trading calendar

A quarterly report period cannot be judged by an official trading day: the unit is the period and the deadline is statutory. The `panel cutoff` cell is read from **bm-c**'s disk.

| lane | host | panel cutoff | statute demands | missing | verdict | takeover path |
|---|---|---|---|---|---|---|
| `fund_statements` | bm-c | 20260930 | 20260930 (due 2026-10-31) | 0 | in_sync | yes |

