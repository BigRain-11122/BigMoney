# -*- coding: utf-8 -*-
# r674 bm-b: FUND trio NULLS burn stewardship probe
# checks: pool shard claim state (owner/owner_since/status), daemon liveness (CIM full-scan dual-form per r659/r661),
#         burn progress k/N + rate + ETA refresh -> results/trio_burn_eta.json (r674 quantitative watch face)
import json, os, subprocess, time, datetime

OUT = {}

# --- 1) pool shard claim state for trio ---
pool = json.load(open(r"results\runnable_pool.json", encoding="utf-8"))
FAMILY = {"fund_value_p1": None, "fund_quality_p1": None, "fund_divlowvol_p1": None}
for sh in pool.get("shards", []) if isinstance(pool, dict) else []:
    key = sh.get("key", "")
    for fam in FAMILY:
        if fam in key:
            FAMILY[fam] = sh
OUT["pool_trio"] = {}
for fam, sh in FAMILY.items():
    if sh is None:
        OUT["pool_trio"][fam] = "NOT-FOUND"
    else:
        OUT["pool_trio"][fam] = {k: sh.get(k) for k in ("key", "status", "owner", "owner_since", "note") if k in sh}

# --- 2) burn daemons liveness: CIM full-scan (dual-form law r659/r661) ---
r = subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -match 'nulls_burn|fund.*p1.*burn|burn_daemon'} | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],
                   capture_output=True)
try:
    procs = json.loads(r.stdout.decode("utf-8", "replace") or "[]")
    if isinstance(procs, dict):
        procs = [procs]
except Exception:
    procs = []
OUT["burn_procs"] = [{"pid": p.get("ProcessId"), "created": p.get("CreationDate"),
                      "cmd": (p.get("CommandLine") or "")[:180]} for p in procs]
OUT["burn_proc_count"] = len(procs)

# --- 3) burn progress k/N + rate + ETA ---
now = time.time()
now_dt = datetime.datetime.now()
eta = {"generated": now_dt.isoformat(timespec="seconds"), "machine": "bm-b", "trio": {}}
for fam, fname in (("fund_value_p1", "fund_value_p1"), ("fund_quality_p1", "fund_quality_p1"),
                   ("fund_divlowvol_p1", "fund_divlowvol_p1")):
    path = os.path.join("results", fname, "nulls.jsonl")
    k = 0
    mtime = None
    if os.path.exists(path):
        with open(path, "rb") as f:
            for _ in f:
                k += 1
        mtime = os.path.getmtime(path)
    sh = FAMILY[fam]
    total = 2000
    OUT.setdefault("burn_progress", {})[fam] = {"k": k, "total": total, "pct": round(100.0 * k / total, 1),
                                               "mtime_age_sec": round(now - mtime, 0) if mtime else None}

# rates from git history of nulls.jsonl (per r674 watch face: count k at recent commits vs now)
def k_at(rev):
    r2 = subprocess.run(["git", "show", rev + ":results/" + fname + "/nulls.jsonl"], capture_output=True)
    if r2.returncode != 0:
        return None
    return r2.stdout.count(b"\n")

# find last two commits touching each nulls.jsonl for rate estimate
for fam, fname in (("fund_value_p1", "fund_value_p1"), ("fund_quality_p1", "fund_quality_p1"),
                   ("fund_divlowvol_p1", "fund_divlowvol_p1")):
    r3 = subprocess.run(["git", "log", "-3", "--format=%H %ct", "--", "results/" + fname + "/nulls.jsonl"],
                        capture_output=True)
    lines = [l.decode() for l in r3.stdout.splitlines() if l.strip()]
    k_now = OUT["burn_progress"][fam]["k"]
    rate = None
    eta_str = None
    if len(lines) >= 2:
        try:
            (c1, t1) = lines[0].split()
            (c2, t2) = lines[1].split()
            k1 = k_at(c1)
            k2 = k_at(c2)
            if k1 is not None and k2 is not None:
                dt_h = (int(t1) - int(t2)) / 3600.0
                dk = k1 - k2
                if dt_h > 0.1 and dk > 0:
                    rate = dk / dt_h
                    remain = 2000 - k_now
                    if rate > 0:
                        eta_h = remain / rate
                        eta_dt = now_dt + datetime.timedelta(hours=eta_h)
                        eta_str = eta_dt.strftime("%Y-%m-%dT%H")
        except Exception as e:
            OUT.setdefault("rate_err", {})[fam] = str(e)[:120]
    OUT["burn_progress"][fam]["rate_per_h"] = round(rate, 1) if rate else None
    OUT["burn_progress"][fam]["eta"] = eta_str
    eta["trio"][fam] = {"k": k_now, "rate_per_h": OUT["burn_progress"][fam]["rate_per_h"],
                        "eta": eta_str}

with open(r"results\_r674bmb_trio_watch.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
with open(r"results\trio_burn_eta.json", "w", encoding="utf-8") as f:
    json.dump(eta, f, ensure_ascii=False, indent=1)
print("OK")
