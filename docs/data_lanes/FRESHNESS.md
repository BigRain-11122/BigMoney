# Data lane freshness -- 2026-10-30

Official reference: last day that must exist by 15:30 = **2026-10-29** (8797 calendar days loaded).

Verdict: **attention** -- 0/10 lanes in sync, 0/10 auditable from this machine, worst = `moneyflow`.

| lane | host | tail | missing (official days) | verdict | authority |
|---|---|---|---|---|---|
| `options` | bm-b | 2026-09-30 | 16: 2026-10-08, 2026-10-09, 2026-10-12, 2026-10-13, 2026-10-14, 2026-10-15 … | retired (copy said `stalled`) | unattributed |
| `moneyflow` | bm-b | 2026-10-19 | 8: 2026-10-20, 2026-10-21, 2026-10-22, 2026-10-23, 2026-10-26, 2026-10-27 … | unverifiable (copy said `stalled`) | unattributed |
| `repo` | bm-b | 2026-10-28 | 1: 2026-10-29 | unverifiable (copy said `behind_1d`) | unattributed |
| `astock_daily` | bm-b | 2026-10-29 | 0 | unverifiable (copy said `in_sync`) | unattributed |
| `etf_panel` | bm-a | 2026-10-29 | 0 | unverifiable (copy said `in_sync`) | unattributed |
| `futures` | bm-a | 2026-10-29 | 0 | unverifiable (copy said `in_sync`) | non_host_envelope |
| `heat` | bm-b | -- | 0 | absent | unattributed |
| `lhb` | bm-a | 2026-10-29 | 0 | unverifiable (copy said `in_sync`) | non_host_envelope |
| `marks` | bm-b | 2026-10-29 | 0 | unverifiable (copy said `in_sync`) | unattributed |
| `zt_pool` | bm-b | 2026-10-29 | 0 | unverifiable (copy said `in_sync`) | non_host_copy |

## Hosts that stopped reporting

These lanes cannot be certified here and the machine that is supposed to collect them has not written a heartbeat for more than 2.0h. Until it comes back the numbers below are this machine's stale copies, not the company's data.

- `bm-b`: last seen 2026-10-29T18:18:13+08:00 (12.17h ago) -- holding back moneyflow, repo, astock_daily, marks, zt_pool

## Why some lanes cannot be certified here

A status envelope is committed by whichever machine ran the leg, and every machine also keeps its own gitignored copy of the data. Neither names its writer, so a tail that reads late can be a dead lane or a stale copy of a live one.

- `moneyflow`: the envelope does not name the machine whose data it describes
- `repo`: the envelope does not name the machine whose data it describes
- `astock_daily`: the envelope does not name the machine whose data it describes
- `etf_panel`: the envelope does not name the machine whose data it describes
- `futures`: the envelope was written by bm-c, not by the lane host bm-a
- `lhb`: the envelope was written by bm-c, not by the lane host bm-a
- `marks`: the envelope does not name the machine whose data it describes
- `zt_pool`: read from this machine's local copy; the lane is hosted by bm-b
