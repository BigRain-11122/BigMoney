# -*- coding: utf-8 -*-
# r675 bm-b: FUND trio NULLS burn stewardship probe (r674 lineage, pool-leg fixed)
# fixes vs r674: pool shards live under entries[].shards[] (r674 probed nonexistent
#   top-level "shards" key -> NOT-FOUND false read for all three families).
# evidence trio for burn health: (a) k growth vs last round, (b) nulls.jsonl mtime
#   freshness, (c) pool entry+shard owner_since keepalive freshness (r288 gate).
import json, os, subprocess, time, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

OUT = {}
FAMS = ["fund_value_p1", "fund_quality_p1", "fund_divlowvol_p1"]
POOL_IDS = {"fund_value_p1": "FUND-VALUE-P1-NULLS",
            "fund_quality_p1": "FUND-QUALITY-P1-NULLS",
            "fund_divlowvol_p1": "FUND-DIVLOWVOL-P1-NULLS"}

# --- 1) pool entry+shard claim state (entries[].shards[], r675 fix) ---
pool = json.load(open(r"results\runnable_pool.json", encoding="utf-8"))
entries = pool.get("entries", [])
OUT["pool_trio"] = {}
fam_entry = {}
for e in entries:
    eid = e.get("id", "")
    for fam, pid in POOL_IDS.items():
        if eid == pid:
            fam_entry[fam] = e
            OUT["pool_trio"][fam] = {
                "entry_status": e.get("status"),
                "shards": [{"key": s.get("key"), "status": s.get("status"),
                            "owner": s.get("owner"), "owner_since": s.get("owner_since")}
                           for s in e.get("shards", [])],
            }

# --- 2) burn progress k/N + mtime + worker-claim files (shard-owner truth) ---
now = time.time()
now_dt = datetime.datetime.now()
prog = {}
for fam in FAMS:
    path = os.path.join("results", fam, "nulls.jsonl")
    k, mtime, claims = 0, None, []
    if os.path.exists(path):
        with open(path, "rb") as f:
            for _ in f:
                k += 1
        mtime = os.path.getmtime(path)
    cdir = os.path.join("results", fam)
    if os.path.isdir(cdir):
        claims = sorted(fn for fn in os.listdir(cdir) if fn.endswith(".json") and ".bm-" in fn)
    prog[fam] = {"k": k, "total": 2000, "pct": round(100.0 * k / 2000, 1),
                 "mtime_age_sec": round(now - mtime, 0) if mtime else None,
                 "mtime": datetime.datetime.fromtimestamp(mtime).isoformat(timespec="seconds") if mtime else None,
                 "claim_files": claims[:4]}

# --- 3) rate via git history of nulls.jsonl (last two commits) ---
def k_at(rev, fname):
    r = subprocess.run(["git", "show", rev + ":results/" + fname + "/nulls.jsonl"],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.count(b"\n")

for fam in FAMS:
    # daemon self-commits are frequent (per-tick): take last 12 commits and use
    # the widest pair (newest vs oldest) for a stable hourly rate (r675 fix:
    # r674-form used only the last two -> dt<0.1h gate starved rate to None).
    r3 = subprocess.run(["git", "log", "-12", "--format=%H %ct", "--",
                         "results/" + fam + "/nulls.jsonl"], capture_output=True)
    lines = [l.decode() for l in r3.stdout.splitlines() if l.strip()]
    rate, eta_str = None, None
    if len(lines) >= 2:
        try:
            c1, t1 = lines[0].split()
            c2, t2 = lines[-1].split()
            k1, k2 = k_at(c1, fam), k_at(c2, fam)
            if k1 is not None and k2 is not None:
                dt_h = (int(t1) - int(t2)) / 3600.0
                dk = k1 - k2
                if dt_h >= 0.25 and dk > 0:
                    rate = dk / dt_h
                    remain = 2000 - prog[fam]["k"]
                    if rate > 0 and remain > 0:
                        eta_dt = now_dt + datetime.timedelta(hours=remain / rate)
                        eta_str = eta_dt.strftime("%Y-%m-%dT%H")
                    elif remain <= 0:
                        eta_str = "COMPLETE"
        except Exception as ex:
            prog[fam]["rate_err"] = str(ex)[:120]
    prog[fam]["rate_per_h"] = round(rate, 1) if rate else None
    prog[fam]["eta"] = eta_str

OUT["burn_progress"] = prog

# --- 4) delta vs r674 watch face (growth check = liveness evidence (a)) ---
prev_path = r"results\_r674bmb_trio_watch.json"
OUT["delta_vs_r674"] = {}
if os.path.exists(prev_path):
    try:
        prev = json.load(open(prev_path, encoding="utf-8"))
        for fam in FAMS:
            pk = prev.get("burn_progress", {}).get(fam, {}).get("k")
            OUT["delta_vs_r674"][fam] = (prog[fam]["k"] - pk) if isinstance(pk, int) else None
    except Exception as ex:
        OUT["delta_vs_r674"] = {"err": str(ex)[:120]}

# --- 5) keepalive freshness from pool entry shard owner_since (evidence (c)) ---
OUT["keepalive_freshness"] = {}
for fam in FAMS:
    e = fam_entry.get(fam, {})
    for s in e.get("shards", []) if isinstance(e, dict) else []:
        os_since = s.get("owner_since", "")
        age = None
        if os_since:
            try:
                t = datetime.datetime.strptime(os_since, "%Y-%m-%d %H:%M:%S")
                age = (now_dt - t).total_seconds() / 60.0
            except Exception:
                age = None
        OUT["keepalive_freshness"][fam] = {"owner": s.get("owner"),
                                           "owner_since": os_since,
                                           "age_min": round(age, 1) if age is not None else None,
                                           "healthy": (age is not None and age < 30.0)}

# verdict: three-evidence health call per family
OUT["verdict"] = {}
for fam in FAMS:
    p = prog[fam]
    kf = OUT["keepalive_freshness"].get(fam, {})
    growth = OUT["delta_vs_r674"].get(fam)
    m_ok = (p["mtime_age_sec"] is not None and p["mtime_age_sec"] < 1800)
    k_ok = kf.get("healthy")
    g_ok = (growth is None) or (growth >= 0)  # None = r674 face absent; do not fail open-faced
    OUT["verdict"][fam] = {"mtime_fresh": m_ok, "keepalive_fresh": k_ok, "growth_nonneg": g_ok,
                           "burning": bool(m_ok and k_ok and g_ok)}

with open(r"results\_r675bmb_trio_watch.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)

eta = {"generated": now_dt.isoformat(timespec="seconds"), "machine": "bm-b", "trio": {
    fam: {"k": prog[fam]["k"], "pct": prog[fam]["pct"],
          "rate_per_h": prog[fam]["rate_per_h"], "eta": prog[fam]["eta"]} for fam in FAMS}}
with open(r"results\trio_burn_eta.json", "w", encoding="utf-8") as f:
    json.dump(eta, f, ensure_ascii=False, indent=1)
print("OK")
