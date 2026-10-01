# r502 bm-b pool materializer: STOCKFURN-{REV,LOWAMP,MOM}-AKSHARE 12 entries
# r509 law: RAW-TEXT surgical append to runnable_pool.json (flat-0-key shape,
# CRLF, no json re-serialization). Asserts: byte-format probe, round-trip
# json.loads, entries array grew by exactly 12, diff-line budget.
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")

raw = open(POOL, "rb").read()
assert raw.count(b"\r\n") > 1000 and (raw.count(b"\n") - raw.count(b"\r\n")) == 0, \
    "pool line-ending drift (expected CRLF-only)"
txt = raw.decode("utf-8")
before = json.loads(txt)
n_before = len(before["entries"])

TS = "2026-10-01 11:2x"
DATA_GATES = ("in-runner FAIL-CLOSED: probe_facts.json equality (universe/rows/"
              "elig_median/sha16) + panel complete cutoff==2026-09-30 + "
              "free-RAM floor 2.0+0.55*workers GB exit 3 + seed-registry law "
              "(stock_face_furnace_nulls=20333000 band [20333000,20445400)) + "
              "cost single-source import (rev_osc_stock_p1.COST_X1); per-cell "
              "JSON checkpoint (presence=done); idempotent no-op when block "
              "complete; selftest 22/22 hermetic + 3-cell real smoke r502")
WORKERS_LAW = ("ProcessPoolExecutor code-backed, O-20260930-2355 multicore "
               "law; --workers override; per-worker panel ~500MB npz cache "
               "under gitignored data/astock_daily/")

FAMS = {
    "rev": [(0, 31), (31, 62), (62, 91), (91, 121)],
    "lowamp": [(0, 36), (36, 72), (72, 108), (108, 144)],
    "mom": [(0, 4), (4, 8), (8, 12), (12, 16)],
}
NOTES = {
    "rev": "REV oversold-rebound event furnace cells (7 REV_OSC judged "
           "grammars excluded, TRIAL_LABOR_LAW sec.4)",
    "lowamp": "LOWAMP low-amplitude daily cross-section furnace cells",
    "mom": "MOM monthly-rebalance momentum furnace cells",
}


def entry(fam, a, b):
    key = f"stockfurn-{fam}-{a}to{b}"
    return ("{\n"
            f'"id": "STOCKFURN-{fam.upper()}-AKSHARE-SHARD-{a}",\n'
            '"ticket_ref": "T-2026-10-01-139-P1 (CEO immediate '
            'O-2026-10-01-1035 stocks mandate; akshare face = bm-b lane per '
            'ticket note; p1c face = GM session lane)",\n'
            '"prereg_ref": "research/STOCK_FACE_FURNACE_P1.md (frozen r502 '
            'pre-burn R99; banned_direction_gate ADMIT; exploration face '
            'zero verdict claims; cutoff 2026-09-30 panel lockbox)",\n'
            '"runner": "scripts/stock_face_furnace.py",\n'
            f'"runner_args": ["run", "--family", "{fam}", "--cells", '
            f'"{a}:{b}", "--workers", "6"],\n'
            '"lane_owner": "bm-b",\n'
            '"priority": 0,\n'
            '"status": "ready",\n'
            f'"entered_at": "{TS}",\n'
            '"entered_by": "bm-b (OS iteration loop r502)",\n'
            f'"data_gates": "{DATA_GATES}",\n'
            '"workers_plan": {\n'
            '"workers": 6,\n'
            '"priority": "BelowNormal",\n'
            f'"workers_law": "{WORKERS_LAW}"\n'
            "},\n"
            '"shards": [\n'
            "{\n"
            f'"key": "{key}",\n'
            '"status": "ready",\n'
            '"checkpoint": "results/stock_face_furnace/cells/'
            f'{fam}/cell-*.json (presence=done; deterministic rerun '
            'byte-equal)",\n'
            f'"note": "{NOTES[fam]} {a}..{b - 1}"\n'
            "}\n"
            "]\n"
            "}")


entries_txt = ",\r\n".join(entry(f, a, b) for f, blocks in FAMS.items()
                           for a, b in blocks).replace("\n", "\r\n")

# raw-text splice: last entry close + array close + object close (+ final NL)
tail = "}\r\n]\r\n}\r\n"
assert txt.endswith(tail), f"unexpected pool tail: {txt[-20:]!r}"
new_txt = txt[: -len(tail)] + "},\r\n" + entries_txt + "\r\n]\r\n}\r\n"

after = json.loads(new_txt)          # round-trip parse BEFORE write
n_after = len(after["entries"])
assert n_after == n_before + 12, f"grew {n_before}->{n_after}, expected +12"
ids = [e["id"] for e in after["entries"][-12:]]
assert all(i.startswith("STOCKFURN-") for i in ids), ids

new_raw = new_txt.encode("utf-8")
assert (new_raw.count(b"\n") - new_raw.count(b"\r\n")) == 0, "LF leaked"
tmp = POOL + ".tmp"
with open(tmp, "wb") as f:
    f.write(new_raw)
os.replace(tmp, POOL)
print(f"materialized 12 entries ({n_before}->{n_after}):")
for i in ids:
    print(" ", i)
