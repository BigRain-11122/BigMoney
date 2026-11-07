# Data lane freshness -- 2026-11-07

Official reference: last day that must exist by 15:30 = **2026-11-06** (8797 calendar days loaded).

Verdict: **host_down** -- 5/10 lanes in sync, 5/10 auditable from this machine, worst = `moneyflow`.


## Whose disk these numbers are on

以本机 bm-a 的盘为基准：9 条在役车道里有 4 条的数字不在本机盘上：4 条在 bm-b 的盘上（191.98h 未报到）；留在本机盘上的 5 条里 5 条可核实。

- `bm-b`: heat, marks, moneyflow, zt_pool (host down)
| lane | host | tail | missing (official days) | verdict | authority |
|---|---|---|---|---|---|
| `options` | bm-b | 2026-09-30 | 22: 2026-10-08, 2026-10-09, 2026-10-12, 2026-10-13, 2026-10-14, 2026-10-15 … | retired (copy said `stalled`) | unattributed |
| `moneyflow` | bm-b | 2026-10-19 | 14: 2026-10-20, 2026-10-21, 2026-10-22, 2026-10-23, 2026-10-26, 2026-10-27 … | unverifiable (copy said `stalled`) | unattributed |
| `marks` | bm-b | 2026-10-29 | 6: 2026-10-30, 2026-11-02, 2026-11-03, 2026-11-04, 2026-11-05, 2026-11-06 | unverifiable (copy said `stalled`) | unattributed |
| `zt_pool` | bm-b | 2026-10-29 | 6: 2026-10-30, 2026-11-02, 2026-11-03, 2026-11-04, 2026-11-05, 2026-11-06 | unverifiable (copy said `stalled`) | non_host_copy |
| `heat` | bm-b | 2026-11-05 | 1: 2026-11-06 | unverifiable (copy said `behind_1d`) | unattributed |
| `astock_daily` | bm-b | 2026-11-06 | 0 | in_sync | declared_takeover |
| `etf_panel` | bm-a | 2026-11-06 | 0 | in_sync | host_envelope |
| `futures` | bm-a | 2026-11-06 | 0 | in_sync | host_envelope |
| `lhb` | bm-a | 2026-11-06 | 0 | in_sync | host_envelope |
| `repo` | bm-b | 2026-11-06 | 0 | in_sync | declared_takeover |

## Lanes where a missed day cannot be recovered

- `zt_pool`: pool day slices are terminal at the close; no superset arrives later
- `heat`: a missed day is permanent: the guba rank is a live rolling list with no retrievable history (HEAT_ATTENTION_SPEC §1)

## Hosts that stopped reporting

These lanes cannot be certified here and the machine that is supposed to collect them has not written a heartbeat for more than 2.0h. Until it comes back the numbers below are this machine's stale copies, not the company's data.

- `bm-b`: last seen 2026-10-30T12:43:06+08:00 (191.98h ago) -- holding back moneyflow, marks, zt_pool, heat

## Lanes nobody can pick up while the host is away

These are not waiting on patience. The host is silent and the collector has no declared-takeover path, so **no machine is allowed to move them** -- the last written envelope stays the newest number the company has, and each day that passes is gone for good where the face is forward-accumulation only. Unblocking one is a decision (reassign the lane, or give its collector the same stale-takeover rule the other eight lanes already have), not a retry.

- `marks`: the row reads another face rather than a collector of its own, so there is nothing to reassign
- `moneyflow`: writer `update_moneyflow` has no `TAKEOVER: declared stale takeover of` path

## Why some lanes cannot be certified here

A status envelope is committed by whichever machine ran the leg, and every machine also keeps its own gitignored copy of the data. Neither names its writer, so a tail that reads late can be a dead lane or a stale copy of a live one.

- `moneyflow`: the envelope does not name the machine whose data it describes
- `marks`: the envelope does not name the machine whose data it describes
- `zt_pool`: read from this machine's local copy; the lane is hosted by bm-b
- `heat`: the lane publishes no tail and this reading is this machine's local copy; it is hosted by bm-b
