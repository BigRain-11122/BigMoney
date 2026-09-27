# -*- coding: utf-8 -*-
"""r363 bm-a rebase-storm side probe (pre-resolution sanity, commit-blob sourced):
:2: = 5c8e4542 (rebase HEAD = onto-chain origin face), :3: = 9ddf5883 (my r362 face).
Prints wall-clock max + structure faces for the 15 S6-family UU files.
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TS_RE = re.compile(r"^20\d{2}-")
TOD_RE = re.compile(r"[T ]\d{2}:\d{2}")
OURS, MINE = "d62f7d43", "ade08dbb"


def blob(rev, path):
    p = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git show {rev}:{path} rc={p.returncode}")
    return p.stdout


def wallocks(obj):
    out = []

    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str) and TS_RE.match(x) and TOD_RE.search(x):
            out.append(x)
    walk(obj)
    return out


def face(rev, path):
    d = json.loads(blob(rev, path).decode("utf-8"))
    w = wallocks(d)
    return d, (max(w) if w else None)


paths = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "results/autofill_state.json",
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for p in paths:
    da, wa = face(OURS, p)
    db, wb = face(MINE, p)
    extra = ""
    if p.endswith("autofill_state.json"):
        la, lb = da.get("launches", []), db.get("launches", [])
        ka = {(r.get("ts"), r.get("machine"), r.get("pid"), r.get("runner_sha256"), r.get("entry"), r.get("shard")) for r in la}
        kb = {(r.get("ts"), r.get("machine"), r.get("pid"), r.get("runner_sha256"), r.get("entry"), r.get("shard")) for r in lb}
        lta, ltb = da.get("last_tick", {}), db.get("last_tick", {})
        shared = set(da) & set(db) - {"launches", "last_tick"}
        diff_shared = {k: (da[k], db[k]) for k in shared if json.dumps(da[k], sort_keys=True) != json.dumps(db[k], sort_keys=True)}
        extra = f" launches {len(la)}+{len(lb)} keys {len(ka | kb)} (mine-only {len(kb - ka)} origin-only {len(ka - kb)}) last_tick {lta.get('ts')}/{ltb.get('ts')} shared-diff-keys {sorted(diff_shared)}"
    if p.endswith("compute_audit.json"):
        ha, hb = da.get("history", []), db.get("history", [])
        extra = f" history {len(ha)}+{len(hb)} union {len({r.get('ts') for r in ha} | {r.get('ts') for r in hb})} first/last-a {ha[0].get('ts') if ha else None}/{ha[-1].get('ts') if ha else None} first/last-b {hb[0].get('ts') if hb else None}/{hb[-1].get('ts') if hb else None}"
    if p.endswith("regime_state.json"):
        ta, tb = da.get("transitions", []), db.get("transitions", [])
        extra = f" transitions {len(ta)}+{len(tb)} union {len({r.get('ts') for r in ta} | {r.get('ts') for r in tb})} state={da.get('state')}/{db.get('state')} topkeys-a {sorted(da)} topkeys-b {sorted(db)}"
    print(f"{p}\n  ours({OURS})={wa}  mine({MINE})={wb}{extra}")
