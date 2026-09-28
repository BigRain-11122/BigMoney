"""r392 resolve #3: rebase stop #4 (commit 82587515, my round-392) -- 16 files.

Skill: bigmoney-conflict-resolve. REBASE stage semantics: :2:=ours=
upstream(origin + replayed r391), :3:=theirs=my round-392 commit.
Same-window double-run of the S6 chain on both machines -- most faces are
snapshot take-new (R208/R216) adjudicated by VALUE-SHAPE-ONLY wall-clock
probe (r100/R350: no key-exclude lists, candidates must be ^20YY-MM-DD with
time-of-day; date-only never feeds the max); ledgers/pool union zero-loss
(r188/R208/r312); js-wrapper taken as whole bytes with its json twin (R209);
parquet binary = append-collector superset face (row-count + subset assert).
"""
import io
import json
import subprocess

import pandas as pd


def blob_bytes(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"],
                           capture_output=True).stdout


def blob_json(stage, path):
    return json.loads(blob_bytes(stage, path))


TS_SHAPE = __import__("re").compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def wallclock_max(obj, best=""):
    """Value-shape-only probe (r100/R350): any string ^20YY-MM-DD[T ]HH:MM
    anywhere in the doc feeds the max; date-only values never feed."""
    if isinstance(obj, dict):
        for v in obj.values():
            best = wallclock_max(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = wallclock_max(v, best)
    elif isinstance(obj, str) and TS_SHAPE.match(obj):
        best = max(best, obj)
    return best


def take_new_json(path):
    a, b = blob_json(2, path), blob_json(3, path)
    ta, tb = wallclock_max(a), wallclock_max(b)
    pick = a if tb <= ta else b
    open(path, "w", encoding="utf-8").write(json.dumps(
        pick, ensure_ascii=False, indent=1))
    print(f"{path}: take-new {'ours' if pick is a else 'theirs'} "
          f"(probe ours={ta or '-'} theirs={tb or '-'})")
    return pick


# ---- simple snapshots: value-shape probe ---------------------------------
SNAPSHOTS = [
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
picked = {}
for p in SNAPSHOTS:
    picked[p] = take_new_json(p)

# ---- js wrapper twin: whole bytes, SAME side as its json twin (R209) ------
P = "results/dashboard_status.js"
ja = wallclock_max(blob_json(2, "results/dashboard_status.json"))
jb = wallclock_max(blob_json(3, "results/dashboard_status.json"))
side = 2 if jb <= ja else 3
open(P, "wb").write(blob_bytes(side, P))
print(f"{P}: whole-bytes take side {':2:ours' if side == 2 else ':3:theirs'} "
      f"(twin probe {ja} vs {jb})")

# ---- live_usage twins: same-day idempotent, one side for both -------------
P = "docs/live_usage/LIVE-2026-09-28.json"
la, lb = blob_json(2, P), blob_json(3, P)
ta, tb = wallclock_max(la), wallclock_max(lb)
side = 2 if tb <= ta else 3
open(P, "wb").write(blob_bytes(side, P))
open("docs/live_usage/LIVE-2026-09-28.md", "wb").write(
    blob_bytes(side, "docs/live_usage/LIVE-2026-09-28.md"))
print(f"live_usage twins: take side {':2:ours' if side == 2 else ':3:theirs'} "
      f"(probe {ta} vs {tb})")

# ---- compute_audit.json: rolling-ledger union + latest take-new -----------
P = "results/compute_audit.json"
A, B = blob_json(2, P), blob_json(3, P)
seen, union = set(), []
for row in A.get("history", []) + B.get("history", []):
    k = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if k not in seen:
        seen.add(k)
        union.append(row)
union.sort(key=lambda r: r.get("ts", ""))
la = (A.get("latest") or {}).get("ts") or ""
lb = (B.get("latest") or {}).get("ts") or ""
latest = (A if lb <= la else B).get("latest")
merged = {"history": union, "latest": latest}
open(P, "w", encoding="utf-8").write(json.dumps(
    merged, ensure_ascii=False, indent=1))
print(f"compute_audit: union {len(A['history'])}+{len(B['history'])} -> "
      f"{len(union)} rows; latest take-new ts={max(la, lb)}")

# ---- regime_state.json: transitions/history union + state take-new --------
P = "results/regime_state.json"
A, B = blob_json(2, P), blob_json(3, P)
merged = {}
for key in ("history", "transitions"):
    if key in A or key in B:
        ha, hb = A.get(key, []), B.get(key, [])
        s2, u2 = set(), []
        for row in ha + hb:
            k = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if k not in s2:
                s2.add(k)
                u2.append(row)
        u2.sort(key=lambda r: r.get("ts", r.get("date", "")))
        merged[key] = u2
        print(f"regime_state.{key}: {len(ha)}|{len(hb)} -> union {len(u2)}")
state_side = A if wallclock_max(B) <= wallclock_max(A) else B
for k, v in state_side.items():
    if k not in merged:
        merged[k] = v
open(P, "w", encoding="utf-8").write(json.dumps(
    merged, ensure_ascii=False, indent=1))
print("regime_state: state fields take-new "
      f"{'ours' if state_side is A else 'theirs'} "
      f"(probe {wallclock_max(A)} vs {wallclock_max(B)})")

# ---- runnable_pool.json: per-entry done-union (r312) ----------------------
P = "results/runnable_pool.json"
A, B = blob_json(2, P), blob_json(3, P)
ea = {e["id"]: e for e in A["entries"]}
eb = {e["id"]: e for e in B["entries"]}
merged_entries, log = [], []
for e in A["entries"]:
    k = e["id"]
    if k not in eb:
        merged_entries.append(e)
        continue
    o = eb[k]
    sa_, sb_ = e["status"], o["status"]
    if sa_ == sb_ and e.get("shards") and o.get("shards"):
        se, so = e["shards"][0], o["shards"][0]
        pick = e if (se.get("owner_since") or "") >= (so.get("owner_since") or "") else o
    elif sa_ == sb_:
        # empty-shards entries: richer record wins (zero info loss)
        pick = (e if len(json.dumps(e, sort_keys=True, default=str))
                >= len(json.dumps(o, sort_keys=True, default=str)) else o)
    elif "done" in (sa_, sb_):
        pick = e if sa_ == "done" else o
    else:
        rank = {"done": 3, "ready": 2, "waiting": 1}
        pick = e if rank.get(sa_, 0) >= rank.get(sb_, 0) else o
    other = o if pick is e else e
    for fk, fv in other.items():
        if fk not in pick:
            pick[fk] = fv
    merged_entries.append(pick)
    log.append(f"{k}:{'A' if pick is e else 'B'}")
for e in B["entries"]:
    if e["id"] not in ea:
        merged_entries.append(e)
        log.append(f"{e['id']}:B-only")
top = {k: v for k, v in A.items() if k != "entries"}
top["updated_at"] = max(A.get("updated_at", ""), B.get("updated_at", ""))
top["entries"] = merged_entries
json.loads(json.dumps(top))
open(P, "w", encoding="utf-8").write(json.dumps(
    top, ensure_ascii=False, indent=1))
print("runnable_pool:", "; ".join(log))

# ---- parquet binaries: append-collector superset face ---------------------
for P in ["Money02/data/lhb/lhb_detail.parquet",
          "Money02/data/lhb/chunks/2026Q3.parquet"]:
    da = pd.read_parquet(io.BytesIO(blob_bytes(2, P)))
    db = pd.read_parquet(io.BytesIO(blob_bytes(3, P)))
    ka = set(map(tuple, da.astype(str).values.tolist()))
    kb = set(map(tuple, db.astype(str).values.tolist()))
    only_a, only_b = len(ka - kb), len(kb - ka)
    if only_a == 0 and len(kb) >= len(ka):
        side, sup = 3, db
    elif only_b == 0 and len(ka) >= len(kb):
        side, sup = 2, da
    else:
        raise SystemExit(
            f"PARQUET FAIL-CLOSE {P}: A-only={only_a} B-only={only_b} "
            f"-- neither side is a superset; manual review required")
    open(P, "wb").write(blob_bytes(side, P))
    print(f"{P}: take side {':2:ours' if side == 2 else ':3:theirs'} "
          f"superset rows={len(sup)} (other-only rows=0, zero loss)")

print("resolve3 done")
