# Data lane freshness -- 2026-10-31

Official reference: last day that must exist by 15:30 = **2026-10-30** (8797 calendar days loaded).

Verdict: **attention** -- 2/10 lanes in sync, 2/10 auditable from this machine, worst = `moneyflow`.


## Whose disk these numbers are on

以本机 bm-c 的盘为基准：9 条在役车道里有 7 条的数字不在本机盘上：6 条在 bm-b 的盘上（19.91h 未报到）、1 条在 bm-a 的盘上（心跳 0.47h 前）；留在本机盘上的 2 条里 2 条可核实。

- `bm-b`: astock_daily, heat, marks, moneyflow, repo, zt_pool (host down)
- `bm-a`: etf_panel
| lane | host | tail | missing (official days) | verdict | authority |
|---|---|---|---|---|---|
| `options` | bm-b | 2026-09-30 | 17: 2026-10-08, 2026-10-09, 2026-10-12, 2026-10-13, 2026-10-14, 2026-10-15 … | retired (copy said `stalled`) | unattributed |
| `moneyflow` | bm-b | 2026-10-19 | 9: 2026-10-20, 2026-10-21, 2026-10-22, 2026-10-23, 2026-10-26, 2026-10-27 … | unverifiable (copy said `stalled`) | unattributed |
| `repo` | bm-b | 2026-10-28 | 2: 2026-10-29, 2026-10-30 | unverifiable (copy said `stalled`) | unattributed |
| `astock_daily` | bm-b | 2026-10-29 | 1: 2026-10-30 | unverifiable (copy said `behind_1d`) | unattributed |
| `marks` | bm-b | 2026-10-29 | 1: 2026-10-30 | unverifiable (copy said `behind_1d`) | unattributed |
| `zt_pool` | bm-b | 2026-10-29 | 1: 2026-10-30 | unverifiable (copy said `behind_1d`) | non_host_copy |
| `etf_panel` | bm-a | 2026-10-30 | 0 | unverifiable (copy said `in_sync`) | unattributed |
| `futures` | bm-a | 2026-10-30 | 0 | in_sync | host_envelope |
| `heat` | bm-b | -- | 0 | absent | unattributed |
| `lhb` | bm-a | 2026-10-30 | 0 | in_sync | host_envelope |

## Lanes where a missed day cannot be recovered

- `zt_pool`: pool day slices are terminal at the close; no superset arrives later

## Hosts that stopped reporting

These lanes cannot be certified here and the machine that is supposed to collect them has not written a heartbeat for more than 2.0h. Until it comes back the numbers below are this machine's stale copies, not the company's data.

- `bm-b`: last seen 2026-10-30T12:43:06+08:00 (19.91h ago) -- holding back moneyflow, repo, astock_daily, marks, zt_pool

## Why some lanes cannot be certified here

A status envelope is committed by whichever machine ran the leg, and every machine also keeps its own gitignored copy of the data. Neither names its writer, so a tail that reads late can be a dead lane or a stale copy of a live one.

- `moneyflow`: the envelope does not name the machine whose data it describes
- `repo`: the envelope does not name the machine whose data it describes
- `astock_daily`: the envelope does not name the machine whose data it describes
- `marks`: the envelope does not name the machine whose data it describes
- `zt_pool`: read from this machine's local copy; the lane is hosted by bm-b
- `etf_panel`: the envelope does not name the machine whose data it describes
