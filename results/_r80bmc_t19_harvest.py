# -*- coding: utf-8 -*-
"""R80 bm-c T19 stage-2c harvest: pool done-flip (r314 flip-first) + gate_attrition row + ticket progress."""
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOW = time.strftime("%Y-%m-%d %H:%M:%S")


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8-sig"))


def dump(p, obj):
    raw = (ROOT / p).read_bytes()
    nl = b"\r\n" if b"\r\n" in raw[:2000] else b"\n"
    indent = 1
    for line in raw.decode("utf-8-sig").splitlines():
        s = line.lstrip(" ")
        if s and line != s:
            indent = len(line) - len(s)
            break
    (ROOT / p).write_bytes(
        (json.dumps(obj, ensure_ascii=False, indent=indent) + "\n")
        .encode("utf-8").replace(b"\n", nl))


# 1. pool done-flip (r314 flip-first: product landed on results/ -> done)
p = "results/runnable_pool.json"
pool = load(p)
e = [x for x in pool["entries"] if x.get("id") == "T19-PHANTOM-P1"][0]
assert e["status"] == "ready" and e["shards"][0]["status"] == "ready", \
    f"unexpected pool face: {e['status']}/{e['shards'][0]['status']}"
sh = e["shards"][0]
sh["status"] = "done"
sh["done_at"] = NOW
sh["result_ref"] = ("results/t19_phantom_contribution.json (+ .csv twin), landed 2026-09-27 12:18:49 "
                    "(single deterministic shard, seed 68_500)")
e["status"] = "done"
e["done_at"] = NOW
e["note_done"] = (
    "completed r80 bm-c control-round harvest: first complete run (12:10:02 autofill launch -> 12:18:49 "
    "landing) after crash-fix chain #1-#4 (all pre-first-complete-run, zero-run discipline held); "
    "G-REPRO 6/6 bit-exact vs T-14 pin face (t14_anchor_face.json src 4a5754a3) + G-SET v2 exact "
    "(3 actual + 150 placebo closures); zero ledger trials (measurement face per prereg); "
    "12:30:13 tick duplicate relaunch (pid 22408, pre-flip blind window) converges per r312 keep-last, "
    "deterministic identical output, zero data loss")
dump(p, pool)
chk = load(p)
ec = [x for x in chk["entries"] if x.get("id") == "T19-PHANTOM-P1"][0]
assert ec["status"] == "done" and ec["shards"][0]["status"] == "done"
print(f"pool flip ok: T19-PHANTOM-P1 -> done at {NOW}")

# 2. gate_attrition append (r248 law: write the 'entries' list)
p = "results/gate_attrition.json"
att = load(p)
assert "entries" in att, "r248 law: entries list must exist"
prev_total = att["entries"][-1].get("ledger_total_after")
entry = {
    "batch": "T19_PHANTOM_P1",
    "ts": NOW,
    "kind": "measurement",
    "retro_fill": False,
    "cells_ledger_delta": 0,
    "ledger_total_after": prev_total,
    "gates": {
        "g_repro": "PASS 6/6 bit-exact vs frozen T-14 pin face (src commit 4a5754a3)",
        "g_set_v2": "PASS family-window suppression exact (3 actual + 150 placebo closures); "
                    "downstream identity drift = disclosed face per v1.1 (CE-01 38/46, CE-02 96/103, DROUGHT 2/2)",
        "null_band": {
            "COMPOSITE-CE-01": "IS p100 beyond / OOS p100 beyond",
            "COMPOSITE-CE-02": "IS p100 beyond / OOS p100 beyond",
            "DROUGHT-CE-01": "IS p100 beyond / OOS p18 within"
        },
        "engine_crash_repair_reruns": "crashes #1-#4 all pre-first-complete-run; "
                                      "single complete run 12:10:02->12:18:49; zero completed-run reruns"
    },
    "eliminated": None,
    "refs": {
        "results": "results/t19_phantom_contribution.json",
        "csv": "results/t19_phantom_contribution.csv",
        "prereg": "research/T19_PHANTOM_P1.md",
        "ticket": "fleet/tasks/T-2026-09-24-19-P1.json",
        "decision_pack": "research/CONSOLIDATION_GOVERNANCE.md"
    },
    "note": ("phantom contribution quantification batch (stage-2c) = O-1325 option-a/b adjudication "
             "evidence; zero registration claims per prereg §4; dSharpe IS/OOS: CE-01 +0.3050/+0.6243, "
             "CE-02 +0.3115/+0.1628, DROUGHT +0.5767/-0.0001; 10-row attribution: d0 gap component "
             "dominates (official true-return components ~0); GM adjudication recorded in decision pack")
}
n_before = len(att["entries"])
att["entries"].append(entry)
dump(p, att)
chk = load(p)
assert len(chk["entries"]) == n_before + 1 and chk["entries"][-1]["batch"] == "T19_PHANTOM_P1"
print(f"gate_attrition append ok: entries {n_before} -> {len(chk['entries'])}, ledger_total_after={prev_total}")

# 3. ticket progress row
p = "fleet/tasks/T-2026-09-24-19-P1.json"
t = load(p)
assert t["status"] == "claimed"
t["note"] = (t.get("note") or "") + (
    " | r80 bm-c stage-2c DELIVERED (harvest round, dept:研究+数据): product "
    "results/t19_phantom_contribution.json + .csv landed 12:18:49 (first complete run after crash-fix "
    "chain #1-#4, zero-run discipline held); G-REPRO 6/6 + G-SET v2 exact; dSharpe IS/OOS = CE-01 "
    "+0.3050/+0.6243, CE-02 +0.3115/+0.1628, DROUGHT +0.5767/-0.0001 (percentile p100 beyond family-removal "
    "noise in 5/6 windows, DROUGHT OOS p18 within); 10-row attribution: d0 gap components dominate, official "
    "true-return components ~0 (phantom nature confirmed); pool shard flipped done (r314 flip-first); "
    "gate_attrition +1 measurement row (zero ledger); prereg §7/§8 backfilled; CONSOLIDATION_GOVERNANCE "
    "stage-2c row DONE + GM adjudication (O-1620 P1 lane): option-a stays default evaluation/paper "
    "consumption face, option-b stays clean-re-run asset (no default-panel switch), stage-2a HOLD "
    "unchanged (T-20 relay timing); remaining ticket face = stage-2a paper forward-protection (bm-a "
    "T-20 G6 relay) + stage-2b official announcement verification (unopened data-lane probe)")
dump(p, t)
chk = load(p)
assert "r80 bm-c stage-2c DELIVERED" in chk["note"]
print("ticket progress ok: T-2026-09-24-19 r80 row appended")
print("ALL HARVEST JSON EDITS OK")
