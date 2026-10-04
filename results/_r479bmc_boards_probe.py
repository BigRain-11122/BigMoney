# -*- coding: utf-8 -*-
"""r479 bm-c S0.5 boards probe: pool ready/unclaimed + open tickets + flags.
Read-only. ASCII stdout (pit-encoding console law)."""
import json
import os
import glob as g

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OUT = {}

# --- 1) pool entries: status + shard owners ---
with open(r"results\runnable_pool.json", encoding="utf-8") as f:
    pool = json.load(f)
rows = []
for e in pool.get("entries", []):
    shards = e.get("shards", [])
    st = e.get("status")
    if st in ("ready", "in_progress", "claimed"):
        owners = sorted({s.get("owner") for s in shards if s.get("owner")})
        nsh = len(shards)
        nready = sum(1 for s in shards if s.get("status") == "ready")
        rows.append({"id": e.get("id"), "entry_status": st, "n_shards": nsh,
                     "n_shard_ready": nready, "owners": owners})
OUT["pool_active_entries"] = rows
OUT["pool_all_status_counts"] = {}
for e in pool.get("entries", []):
    k = e.get("status")
    OUT["pool_all_status_counts"][k] = OUT["pool_all_status_counts"].get(k, 0) + 1

# --- 2) open tickets (any machine, status=open) ---
tickets = []
for p in sorted(g.glob(r"fleet\tasks\T-*.json")):
    try:
        with open(p, encoding="utf-8") as f:
            t = json.load(f)
    except Exception as ex:
        tickets.append({"file": os.path.basename(p), "err": str(ex)[:80]})
        continue
    if t.get("status") == "open":
        tickets.append({"file": os.path.basename(p),
                        "title": str(t.get("title", ""))[:100],
                        "dept": t.get("dept"),
                        "assignee": t.get("assignee"),
                        "priority": t.get("priority")})
OUT["open_tickets"] = tickets
OUT["open_ticket_count"] = len(tickets)

# --- 3) flags: watermark red + compute_audit pool-supply-gap ---
for name, path in [("watermark_red", r"results\watermark_red.json"),
                   ("compute_audit", r"results\compute_audit.json")]:
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        if name == "watermark_red":
            OUT[name] = {k: d.get(k) for k in ("red", "reason", "verdict", "ts")}
        else:
            OUT[name] = {k: d.get(k) for k in ("pool_supply_gap", "verdict",
                                               "generated_at", "ts")}
    except Exception as ex:
        OUT[name] = {"err": str(ex)[:120]}

# --- 4) engine state summary (bm-c Tools face) ---
try:
    with open(r"results\saturation_engine_state.bm-c.json", encoding="utf-8") as f:
        eng = json.load(f)
    OUT["engine"] = {k: eng.get(k) for k in
                     ("cycle", "burns_active", "quarantined", "crash_counts")}
    OUT["engine"]["done_count"] = len(eng.get("done", [])) if isinstance(eng.get("done"), list) else eng.get("done_count")
    OUT["engine"]["queue_len"] = len(eng.get("queue", [])) if isinstance(eng.get("queue"), list) else eng.get("queue_len")
except Exception as ex:
    OUT["engine"] = {"err": str(ex)[:120]}

print(json.dumps(OUT, indent=1, ensure_ascii=True))
