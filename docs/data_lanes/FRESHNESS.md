# Data lane freshness -- 2026-11-27

Official reference: last day that must exist by 15:30 = **2026-11-26** (8797 calendar days loaded).

Verdict: **attention** -- 9/16 lanes in sync, 15/16 auditable from this machine, worst = `heat`.

Built on **bm-c** at 2026-11-27T08:43:51: every tail and period below is a reading of that machine's disk. A copy of this file on another machine says nothing about that machine's panels -- run the board there to read its own bytes.


## Whose disk these numbers are on

以本机 bm-c 的盘为基准：15 条在役车道的数字全都落在本机盘上，其中 15 条有署名可核实。

| lane | host | tail | missing (official days) | verdict | authority |
|---|---|---|---|---|---|
| `options` | bm-c | 2026-09-30 | 36: 2026-10-08, 2026-10-09, 2026-10-12, 2026-10-13, 2026-10-14, 2026-10-15 … | retired (copy said `stalled`) | unattributed |
| `heat` | bm-a | 2026-11-19 | 5: 2026-11-20, 2026-11-23, 2026-11-24, 2026-11-25, 2026-11-26 | stalled | declared_takeover |
| `cb_panel` | bm-c | 2026-11-20 | 4: 2026-11-23, 2026-11-24, 2026-11-25, 2026-11-26 | stalled | host_copy |
| `lhb_inst` | bm-c | 2026-11-20 | 4: 2026-11-23, 2026-11-24, 2026-11-25, 2026-11-26 | stalled | host_envelope |
| `moneyflow` | bm-c | 2026-11-20 | 4: 2026-11-23, 2026-11-24, 2026-11-25, 2026-11-26 | in_sync (own window 4/20) | host_envelope |
| `sina_mf` | bm-c | 2026-11-24 | 2: 2026-11-25, 2026-11-26 | in_sync (own window 2/20) | host_envelope |
| `lhb` | bm-a | 2026-11-25 | 1: 2026-11-26 | behind_1d | declared_takeover |
| `repo` | bm-a | 2026-11-25 | 1: 2026-11-26 | behind_1d | declared_takeover |
| `ah_panel` | bm-c | -- | 0 | absent | host_copy |
| `astock_daily` | bm-b | 2026-11-26 | 0 | in_sync | declared_takeover |
| `etf_panel` | bm-c | 2026-11-26 | 0 | in_sync | host_envelope |
| `futures` | bm-a | 2026-11-26 | 0 | in_sync | declared_takeover |
| `marks` | bm-b | 2026-11-26 | 0 | in_sync | declared_takeover |
| `minute_feed` | bm-c | 2026-11-26 | 0 | in_sync | host_copy |
| `ths_panel` | bm-c | 2026-11-26 | 0 | in_sync | host_envelope |
| `zt_pool` | bm-c | 2026-11-26 | 0 | in_sync | host_copy |

## Lanes where a missed day cannot be recovered

- `heat`: a missed day is permanent: the guba rank is a live rolling list with no retrievable history (HEAT_ATTENTION_SPEC §1)
- `cb_panel`: vendor re-serves each bond's full history by code, so a missed day is recoverable; the failure mode here is silent staleness -- fetch used to skip every bond whose file existed, so the panel could not move without --tail-after
- `lhb_inst`: vendor re-serves the range on later pulls, so a missed month is recoverable by moving FIRST_DATE; the panel is append-only by key

## Whose clock is the gap on

A lane that lands its bars after midnight reads `behind_1d` every ordinary afternoon. The arrival face measures that clock (days from a session to the commit that carries it, bulk imports excluded); a gap inside it is the writer's own schedule, and only a gap past it is a bar nobody fetched.

- `repo`: verdict `behind_1d`, gap 1 day(s) vs the collector's own clock (median 1 / p90 5 day(s), 68.6% next-day-or-later, n=35, face built 2026-11-27T03:11) -- inside the clock

## Lanes judged against their own window

These lanes do not owe every official day: their collector refreshes on a rolling window of trading days, so a gap inside that window is the design and the verdict is `in_sync`. The row's `missing` column counts official days since the tail; the window below is the lane's own promise, and the sessions-left number says when that promise runs out.

- `moneyflow`：尾部 2026-11-20，落后官方日历 **4** 个交易日，滚动窗 **20** 个交易日 → 还可再走 **17** 个交易日才欠一次刷新（差距超过 20 即读 `stalled`）。依据：采集器自己的 no-op 规则：只有面板尾部落后超过 20 个交易日才刷新
- `sina_mf`：尾部 2026-11-24，落后官方日历 **2** 个交易日，滚动窗 **20** 个交易日 → 还可再走 **19** 个交易日才欠一次刷新（差距超过 20 即读 `stalled`）。依据同上（本节首行）

## Who was awake on the days that are missing

Each missing day below is classified by its own collector. `takeover_possible` means another machine was awake inside the capture window and nobody declared a stand-in: that day was movable *at the time*. Every other cause means no machine was sampling. Either way the day is behind us -- a takeover declared today starts capturing today.

- `marks`: 0 missing day(s) after the lane's last captured day, out of 18 hole(s) recorded since the lane started (host_down 1, host_offhours 4, lane_missed 1, takeover_possible 12)

## Owners that stopped reporting

A different question from the section above: these machines have written no heartbeat for more than 24.0h, so the lanes they own are being judged from whatever was last committed. A lane here can still read `in_sync` -- the number is old, the owner is gone, and nobody would notice the day the file stops being written.

- `bm-a`: last seen 2026-11-18T19:53:03+08:00 (204.85h ago) -- owns futures, heat, lhb, repo
  - already covered by a declared stand-in: futures <- bm-c, heat <- bm-c, lhb <- bm-c, repo <- bm-c (nothing to wait for)
- `bm-b`: last seen 2026-10-30T12:43:06+08:00 (668.01h ago) -- owns astock_daily, marks
  - already covered by a declared stand-in: astock_daily <- bm-c, marks <- bm-c (nothing to wait for)

## Members sitting outside the active cohort

These are named by the face that audits the panel, with the reason the lane's own receipt gives. A pinned member and a source that ended are decisions already taken; a member with **no declaration** is a feed that stopped, and that is the only line here that needs somebody to act.

- `etf_panel`: `510880_t73` (declared_out_of_scope@2026-09-22), `sh512390` (source_ended@2026-09-04), `sh530080` (source_ended@2026-11-12), `sz159528` (source_ended@2026-11-18) -- all declared (audited by exchange_calendar_audit (E136))

## Tails read from a sample

The per-symbol panels hold thousands of files, so their tail is read through an evenly spaced sample rather than a full sweep. A sample can miss a single laggard symbol; it cannot miss a panel that stopped weeks ago. Each row below says how many symbols were read out of how many. Small panels read whole (marked `files`) are listed too whenever a full-scan certification exists for them: that scan can be older than the tail this board prints, and this section is where that older tail is named.

- `moneyflow`: 40 of 5228 symbols read, tail 2026-11-20; the full scan holds it in 5,226 of 5,228 symbols (99.98%) (certified 2026-11-27T08:43:50)
- `repo`: 11 of 11 files read, tail 2026-11-25; the full scan holds it in 11 of 11 symbols (100.00%) (certified 2026-11-27T08:43:50)
- `astock_daily`: 40 of 5221 symbols read, tail 2026-11-26; the full scan holds it in 5,194 of 5,221 symbols (99.48%) (certified 2026-11-27T08:43:50)
- `futures`: 10 of 10 files read, tail 2026-11-26; the full scan holds it in 10 of 10 symbols (100.00%) (certified 2026-11-27T08:43:50)

Full-scan certification of exactly these rows: `scripts/data_lane_freshness.py certify` -> `docs/data_lanes/TAIL_CERTIFICATION.md` (it re-reads every file and names the symbols that sit behind the newest bar).

## Lanes whose clock is the statute, not the trading calendar

A quarterly report period cannot be judged by an official trading day: the unit is the period and the deadline is statutory. The `panel cutoff` cell is read from **bm-c**'s disk.

| lane | host | panel cutoff | statute demands | missing | verdict | takeover path |
|---|---|---|---|---|---|---|
| `fund_statements` | bm-c | 20260930 | 20260930 (due 2026-10-31) | 0 | in_sync | yes |

