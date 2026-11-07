# Data lane freshness -- 2026-11-07

Official reference: last day that must exist by 15:30 = **2026-11-06** (8797 calendar days loaded).

Verdict: **host_down** -- 5/10 lanes in sync, 5/10 auditable from this machine, worst = `moneyflow`.


## Whose disk these numbers are on

以本机 bm-a 的盘为基准：9 条在役车道里有 4 条的数字不在本机盘上：4 条在 bm-b 的盘上（194.12h 未报到）；留在本机盘上的 5 条里 5 条可核实。

- `bm-b`: astock_daily, marks, moneyflow, zt_pool (host down)
| lane | host | tail | missing (official days) | verdict | authority |
|---|---|---|---|---|---|
| `options` | bm-b | 2026-09-30 | 22: 2026-10-08, 2026-10-09, 2026-10-12, 2026-10-13, 2026-10-14, 2026-10-15 … | retired (copy said `stalled`) | unattributed |
| `moneyflow` | bm-b | 2026-10-19 | 14: 2026-10-20, 2026-10-21, 2026-10-22, 2026-10-23, 2026-10-26, 2026-10-27 … | unverifiable (copy said `stalled`) | unattributed |
| `marks` | bm-b | 2026-10-29 | 6: 2026-10-30, 2026-11-02, 2026-11-03, 2026-11-04, 2026-11-05, 2026-11-06 | unverifiable (copy said `stalled`) | unattributed |
| `zt_pool` | bm-b | 2026-10-29 | 6: 2026-10-30, 2026-11-02, 2026-11-03, 2026-11-04, 2026-11-05, 2026-11-06 | unverifiable (copy said `stalled`) | non_host_copy |
| `astock_daily` | bm-b | 2026-11-06 | 0 | unverifiable (copy said `in_sync`) | unattributed |
| `etf_panel` | bm-a | 2026-11-06 | 0 | in_sync | host_envelope |
| `futures` | bm-a | 2026-11-06 | 0 | in_sync | host_envelope |
| `heat` | bm-b | 2026-11-06 | 0 | in_sync | declared_takeover |
| `lhb` | bm-a | 2026-11-06 | 0 | in_sync | host_envelope |
| `repo` | bm-b | 2026-11-06 | 0 | in_sync | declared_takeover |

## Lanes where a missed day cannot be recovered

- `zt_pool`: pool day slices are terminal at the close; no superset arrives later

## Hosts that stopped reporting

These lanes cannot be certified here and the machine that is supposed to collect them has not written a heartbeat for more than 2.0h. Until it comes back the numbers below are this machine's stale copies, not the company's data.

- `bm-b`: last seen 2026-10-30T12:43:06+08:00 (194.12h ago) -- holding back moneyflow, marks, zt_pool, astock_daily

## Lanes nobody can pick up while the host is away

These are not waiting on patience. The host is silent and the collector has no declared-takeover path, so **no machine is allowed to move them** -- the last written envelope stays the newest number the company has, and each day that passes is gone for good where the face is forward-accumulation only. Unblocking one is a decision (reassign the lane, or give its collector the same stale-takeover rule the other eight lanes already have), not a retry.

- `marks`: the row reads another face rather than a collector of its own, so there is nothing to reassign

## Why some lanes cannot be certified here

A status envelope is committed by whichever machine ran the leg, and every machine also keeps its own gitignored copy of the data. Neither names its writer, so a tail that reads late can be a dead lane or a stale copy of a live one.

- `moneyflow`: the envelope does not name the machine whose data it describes
- `marks`: the envelope does not name the machine whose data it describes
- `zt_pool`: read from this machine's local copy; the lane is hosted by bm-b
- `astock_daily`: bm-a declared a stand-in in `takeover{}` but published no `authority.took_over_by` -- the envelope does not name the machine whose data it describes

## Copies that hold less than their envelope claims

The envelope is what some machine says it collected; the panel is what is on this disk. Where the copy is behind its own envelope the row cannot be read as current here, even though the lane itself may be alive elsewhere.

- `moneyflow`: envelope says 2026-10-19, this copy holds 2026-10-13 (4 official days behind)

## Tails read from a sample

The per-symbol panels hold thousands of files, so their tail is read through an evenly spaced sample rather than a full sweep. A sample can miss a single laggard symbol; it cannot miss a panel that stopped weeks ago. Each row below says how many symbols were read out of how many.

- `moneyflow`: 40 of 5222 symbols read, tail 2026-10-13; the full scan holds it in 2 of 5,222 symbols (0.04%) -- **thin tail**: that is a handful of symbols' bar, not the panel's state (certified 2026-11-07T13:47:58)
- `astock_daily`: 40 of 5222 symbols read, tail 2026-11-06; the full scan holds it in 4,783 of 5,222 symbols (91.59%) (certified 2026-11-07T13:47:58)

Full-scan certification of exactly these rows: `scripts/data_lane_freshness.py certify` -> `docs/data_lanes/TAIL_CERTIFICATION.md` (it re-reads every file and names the symbols that sit behind the newest bar).
