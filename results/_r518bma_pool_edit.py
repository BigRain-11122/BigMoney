# r518 bm-a: pool surgical edit (r509 raw-text law; zero json re-serialization)
# (1) append 3 T-139 stage-B entries (SHARD-0 / SHARD-1 / NULLS)
# (2) flip LOWAMP-P2-NULLS both layers (entry+shard) ready->done with provenance
# Verify: json.loads full + line-level diff assertions before write-back.
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
FP = "results/runnable_pool.json"
raw = open(FP, "rb").read().decode("utf-8")
assert raw.endswith("}\r\n"), "tail shape drift"
assert raw.count('"status": "ready"') >= 2

# ---- probe the inter-entry separator byte pattern (mirror exactly)
i = raw.find('"LOWAMP-P2-NULLS"')
j = raw.find('"LOWAMP-P2-SENS"')
sep_probe = raw[raw.find("}", i + 200): raw.find("}", i + 200) + 3]
print("entry-close bytes:", repr(sep_probe))
# bytes between NULLS entry end and next entry start:
end_nulls = raw.find("},", i)
next_start = raw.find("{", end_nulls)
sep = raw[end_nulls + 2: next_start]
print("inter-entry separator:", repr(sep))

NOW = "2026-10-01 14:58:00"
TS = "2026-10-01T14:58:00+08:00"
PREREG = ("research/REFINE_BENCH_STOCK_REV_P2.md (freeze 5c2afb10c r518; "
          "banned_direction_gate ADMIT rc0 BAN-04 new_data exception; "
          "exit-axis explicit: strategy-own pure time H20, engine default "
          "exit stack never constructed; N_eff=2020)")
TICKET = ("T-2026-10-01-139-P1 family-1 stage-B (CEO direct "
          "O-2026-10-01-1035 + ignition order O-20261001-1332 sec.1.1 "
          "bm-a immediate prereg+ignite)")
GATES = ("in-runner FAIL-CLOSED: probe.json PASS required (panel T=8792 "
         "N=5222 cutoff 2026-09-22 D2 lockbox + survivor freeze assertion vs "
         "census_ranking.json top10_independent + closed_family open + seed "
         "20263300 registry); per-cell-face checkpoint presence=done (r488); "
         "worker claim handshake (r497); RAM floor 16GB exit 3")
WLAW = ("ProcessPoolExecutor via parallel_runner (O-20260930-2355); "
        "workers=min(cap,6) ~8GB/worker stock panel guard; core-dist line "
        "in round report")


def entry(eid, args, shard_key, note):
    return {
        "id": eid,
        "ticket_ref": TICKET,
        "prereg_ref": PREREG,
        "runner": "scripts/refine_bench_rev_p2.py",
        "runner_args": args,
        "lane_owner": "ANY",
        "priority": 0,
        "status": "ready",
        "entered_at": NOW,
        "entered_by": "bm-a (OS iteration loop r518)",
        "data_gates": GATES,
        "workers_plan": {"workers": 6, "priority": "BelowNormal",
                         "workers_law": WLAW},
        "shards": [{
            "key": shard_key,
            "status": "ready",
            "checkpoint": ("results/refine_bench_stock/rev_p2/ "
                           "per-unit checkpoint presence=done"),
            "note": note,
        }],
    }


E0 = entry("REFINE-BENCH-REV-P2-SHARD-0",
           ["run", "--shard", "0", "--of", "2"], "rev-p2-0of2",
           "cells 0-4 (D-15|raw|base, Dtop10|raw|base, D-25|raw|base, "
           "D-15|yang|base, D-25|yang|base) x {x1,x2} = 10 cell-faces; "
           "est 2-5min multicore burn")
E1 = entry("REFINE-BENCH-REV-P2-SHARD-1",
           ["run", "--shard", "1", "--of", "2"], "rev-p2-1of2",
           "cells 5-9 (Dtop10|yang|base, D-15|raw|liq2, D-25|raw|liq2, "
           "Dtop10|raw|liq2, D-15|yang|liq2) x {x1,x2} = 10 cell-faces; "
           "est 2-5min multicore burn")
E2 = entry("REFINE-BENCH-REV-P2-NULLS",
           ["run", "--nulls"], "rev-p2-nulls",
           "K=2000 same-mask random event nulls H=20 time-exit x1 cost "
           "rng(20263300+k), 20 chunks x 100 via ProcessPool; phase-2 "
           "52-cohort synthetic annual Sharpe -> nulls_pool.json; "
           "est 15-35min; feeds skill_line_v2 null_pool")


def ser(e):
    return json.dumps(e, ensure_ascii=False, indent=0).replace("\n", "\r\n")


# ---- (2) NULLS flip: both layers within the NULLS block only
ni = raw.find('"id": "LOWAMP-P2-NULLS"')
nend = raw.find('"id": ', ni + 20)          # next entry id anchor
if nend == -1:
    nend = len(raw)
block = raw[ni:nend]
assert block.count('"status": "ready"') == 2, \
    f"NULLS block ready count: {block.count(chr(34) + 'status' + chr(34) + ': ' + chr(34) + 'ready' + chr(34))}"
nb = block.replace('"status": "ready"', '"status": "done"', 1)   # entry layer
nb = nb.replace('"status": "ready"', '"status": "done"', 1)      # shard layer
old_tail = '"owner_since": "2026-10-01 13:42:07"'
new_tail = ('"owner_since": "2026-10-01 13:42:07",\r\n'
            '"done_at": "' + NOW + '",\r\n'
            '"harvested_by": "bm-a",\r\n'
            '"harvest_claim": "lowamp-p2-nulls-0of1.bm-a.json"')
assert nb.count(old_tail) == 1
nb = nb.replace(old_tail, new_tail)
# entry-level provenance after the flipped entry status
old_es = '"status": "done",'
new_es = ('"status": "done",\r\n'
          '"done_by": "bm-a",\r\n'
          '"done_at": "' + NOW + '",\r\n'
          '"done_note": "r497 handshake claim on origin (pid 66764 closed '
          '13:57:21); bm-b daemon 13:42 claim superseded per MSG-1345 '
          'kill-advice + bm-c r318 yield; reunion 2000/2000 delivered '
          'cf4cb64a8",')
assert nb.count(old_es) >= 1
nb = nb.replace(old_es, new_es, 1)
raw = raw[:ni] + nb + raw[nend:]

# ---- (1) append 3 entries before the final closing bracket
tail_anchor = "}\r\n]\r\n}\r\n"
assert raw.endswith(tail_anchor), "tail anchor drift"
add = ("},\r\n" + ser(E0) + ",\r\n" + ser(E1) + ",\r\n" + ser(E2)
       + "]\r\n}\r\n")
raw = raw[:-len(tail_anchor)] + add

# ---- verify before write
p = json.loads(raw)                      # full-file parse gate
ents = p.get("entries", p) if isinstance(p, dict) else p
if isinstance(ents, dict):
    ents = list(ents.values())
from collections import Counter
print("post-edit pool:", len(ents), dict(Counter(e.get("status")
                                                 for e in ents)))
ids = [e["id"] for e in ents]
for want in ("REFINE-BENCH-REV-P2-SHARD-0", "REFINE-BENCH-REV-P2-SHARD-1",
             "REFINE-BENCH-REV-P2-NULLS", "LOWAMP-P2-NULLS"):
    assert want in ids, want
nulls = [e for e in ents if e["id"] == "LOWAMP-P2-NULLS"][0]
assert nulls["status"] == "done" and \
    nulls["shards"][0]["status"] == "done", "NULLS flip incomplete"
out = raw.encode("utf-8")
open(FP, "wb").write(out)
print("written bytes:", len(out))
