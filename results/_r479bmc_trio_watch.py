# -*- coding: utf-8 -*-
# r479 bm-c: FUND trio NULLS watch probe (read-only steward, NOT the ETA-face owner)
# baseline = results/_r478bmc_trio_watch.json (V796/Q619/D464, bm-c r478, freshest).
# bm-c evidence caliber (r631 pit: local mtime = checkout artifact, NOT burn time):
#   (a) k growth vs r478 face, (b) git-sync commit age of nulls.jsonl,
#   (c) pool entries[].shards[] owner_since keepalive age (<30min healthy, r288 gate).
# Zero writes to shared faces: only results/_r479bmc_trio_watch.json (eta face = bm-b single-writer).
import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

CREATE = 0x08000000
NOW = time.time()
NOW_DT = datetime.datetime.now()
FAMS = ["fund_value_p1", "fund_quality_p1", "fund_divlowvol_p1"]
POOL_IDS = {"fund_value_p1": "FUND-VALUE-P1-NULLS",
            "fund_quality_p1": "FUND-QUALITY-P1-NULLS",
            "fund_divlowvol_p1": "FUND-DIVLOWVOL-P1-NULLS"}
TOTAL = 2000

OUT = {"generated": NOW_DT.isoformat(timespec="seconds"), "machine": "bm-c", "probe": "r479"}

# --- 1) pool entry+shard claim state (read-only) ---
with open(r"results\runnable_pool.json", encoding="utf-8") as f:
    pool = json.load(f)
fam_entry = {}
for e in pool.get("entries", []):
    for fam, pid in POOL_IDS.items():
        if e.get("id") == pid:
            fam_entry[fam] = e
OUT["pool_trio"] = {}
for fam in FAMS:
    e = fam_entry.get(fam, {})
    OUT["pool_trio"][fam] = {
        "entry_status": e.get("status"),
        "shards": [{"key": s.get("key"), "status": s.get("status"),
                    "owner": s.get("owner"), "owner_since": s.get("owner_since")}
                   for s in e.get("shards", [])],
    }

# --- 2) k/N + last-commit sync age (git face, not local mtime) ---
def last_commit_age(path):
    r = subprocess.run(["git", "log", "-1", "--format=%ct", "--", path],
                       capture_output=True, creationflags=CREATE)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return round(NOW - int(r.stdout.strip()), 0)

def k_at(rev, fam):
    r = subprocess.run(["git", "show", rev + ":results/" + fam + "/nulls.jsonl"],
                       capture_output=True, creationflags=CREATE)
    if r.returncode != 0:
        return None
    return r.stdout.count(b"\n")

prog = {}
for fam in FAMS:
    path = os.path.join("results", fam, "nulls.jsonl")
    k = 0
    if os.path.exists(path):
        with open(path, "rb") as f:
            for _ in f:
                k += 1
    prog[fam] = {"k": k, "total": TOTAL, "pct": round(100.0 * k / TOTAL, 1),
                 "last_commit_age_sec": last_commit_age("results/" + fam + "/nulls.jsonl")}

# --- 3) wide-window rate from git history (r675 widest-pair caliber) ---
for fam in FAMS:
    r3 = subprocess.run(["git", "log", "-12", "--format=%H %ct", "--",
                         "results/" + fam + "/nulls.jsonl"],
                        capture_output=True, creationflags=CREATE)
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
                    remain = TOTAL - prog[fam]["k"]
                    if remain <= 0:
                        eta_str = "COMPLETE"
                    elif rate > 0:
                        eta_dt = NOW_DT + datetime.timedelta(hours=remain / rate)
                        eta_str = eta_dt.strftime("%Y-%m-%dT%H")
        except Exception as ex:
            prog[fam]["rate_err"] = str(ex)[:120]
    prog[fam]["rate_per_h"] = round(rate, 1) if rate else None
    prog[fam]["eta_wide"] = eta_str
OUT["burn_progress"] = prog

# --- 4) delta vs r478 baseline face ---
OUT["baseline_face"] = "results/_r478bmc_trio_watch.json"
OUT["delta_vs_r478"] = {}
prev = None
try:
    with open(r"results\_r478bmc_trio_watch.json", encoding="utf-8") as f:
        prev = json.load(f)
except Exception as ex:
    OUT["delta_vs_r478"] = {"err": str(ex)[:120]}
if prev is not None:
    for fam in FAMS:
        pk = prev.get("burn_progress", {}).get(fam, {}).get("k")
        OUT["delta_vs_r478"][fam] = (prog[fam]["k"] - pk) if isinstance(pk, int) else None

# --- 5) keepalive freshness + 3-evidence verdict ---
OUT["keepalive_freshness"] = {}
OUT["verdict"] = {}
for fam in FAMS:
    verdicts = []
    for s in fam_entry.get(fam, {}).get("shards", []):
        os_since = s.get("owner_since", "")
        age = None
        if os_since:
            try:
                t = datetime.datetime.strptime(os_since, "%Y-%m-%d %H:%M:%S")
                age = (NOW_DT - t).total_seconds() / 60.0
            except Exception:
                age = None
        verdicts.append({"owner": s.get("owner"), "owner_since": os_since,
                         "age_min": round(age, 1) if age is not None else None,
                         "healthy": (age is not None and age < 30.0)})
    OUT["keepalive_freshness"][fam] = verdicts
    growth = OUT["delta_vs_r478"].get(fam)
    keep_ok = bool(verdicts) and all(v["healthy"] for v in verdicts)
    sync_ok = (prog[fam]["last_commit_age_sec"] is not None
               and prog[fam]["last_commit_age_sec"] < 3600)
    g_ok = (growth is None) or (growth >= 0)
    complete = prog[fam]["k"] >= TOTAL
    OUT["verdict"][fam] = {
        "growth_delta_vs_r478": growth, "keepalive_fresh": keep_ok,
        "git_sync_fresh_1h": sync_ok, "growth_nonneg": g_ok, "complete": complete,
        "healthy_watch": bool((keep_ok and g_ok) or complete),
    }

with open(r"results\_r479bmc_trio_watch.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=True, indent=1)
print("OK " + " ".join("%s=%d/%d" % (fam.split("_")[1], prog[fam]["k"], TOTAL) for fam in FAMS))
