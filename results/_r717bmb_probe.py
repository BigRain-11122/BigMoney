# r717 bm-b rebase-window UU adjudication probe (in-memory only, no writes)
# rebase stage mapping: :2: = origin/upstream tip, :3: = replayed churn-absorb (r701-3)
# hardened deep-ts probe per r100/R350: key normalize strip _-, value must match ^20\d{2}-,
# wall-clock max requires time-of-day in value; no key-exclusion lists; tie -> :2: (r140 canon)
import subprocess, json, sys, re, io

FACES = [
    "docs/daily_report/REPORT-2026-10-05.json",
    "docs/daily_report/REPORT-2026-10-05.md",
    "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

STEMS = ("asof","updated","generated","lastseen","lasttick","timestamp","cutoff","heartbeat","lastrun","last","ts","time","date","epoch")
TSRE = re.compile(r"^20\d{2}-")
CLOCKRE = re.compile(r"[T ]\d{2}:\d{2}")

def blob(stage, path):
    r = subprocess.run(["git","show",f":{stage}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None

def norm(k):
    return k.replace("_","").replace("-","").lower()

def deep_ts(obj, path="", out=None):
    if out is None: out = []
    if isinstance(obj, dict):
        for k,v in obj.items():
            nk = norm(k)
            if isinstance(v,str) and TSRE.match(v) and any(s in nk for s in STEMS):
                out.append((path+"/"+k, v))
            deep_ts(v, path+"/"+k, out)
    elif isinstance(obj, list):
        for i,v in enumerate(obj):
            deep_ts(v, f"{path}[{i}]", out)
    return out

def wallclock_max(pairs):
    vals = [v for _,v in pairs if CLOCKRE.search(v)]
    return max(vals) if vals else None

def probe(path):
    b2, b3 = blob("2",path), blob("3",path)
    res = {"path":path, "ok2":b2 is not None, "ok3":b3 is not None}
    if path.endswith(".json"):
        try:
            j2 = json.loads(b2); j3 = json.loads(b3)
            p2, p3 = deep_ts(j2), deep_ts(j3)
            w2, w3 = wallclock_max(p2), wallclock_max(p3)
            res["w2"],res["w3"] = w2,w3
            res["win"] = "origin" if (w2 or "") >= (w3 or "") else "churn"
            res["n2"],res["n3"] = len(p2),len(p3)
        except Exception as e:
            res["err"] = repr(e)[:80]
    elif path.endswith(".js"):
        res["win"] = "TWIN-FOLLOWS-JSON"
    else:  # .md twins
        res["win"] = "TWIN-FOLLOWS-JSON"
    return res

out = []
for f in FACES:
    r = probe(f)
    out.append(f"{f} | {r.get('win')} | w2={r.get('w2')} w3={r.get('w3')} | {r.get('err','')}")
# ledger faces: report key structure for union design
for f in ("results/compute_audit.json","results/regime_state.json"):
    b2 = blob("2",f); b3 = blob("3",f)
    for tag,b in (("org",b2),("chn",b3)):
        try:
            j = json.loads(b)
            out.append(f"STRUCT {f} {tag}: keys={sorted(j.keys())[:12]}")
            for k in ("history","transitions","launches"):
                if k in j and isinstance(j[k],list):
                    out.append(f"  {k}: n={len(j[k])} sample={json.dumps(j[k][-1])[:160] if j[k] else 'EMPTY'}")
        except Exception as e:
            out.append(f"STRUCT {f} {tag} ERR {repr(e)[:60]}")
rep = "\n".join(out)
io.open(r"results\_r717bmb_probe_out.txt","w",encoding="ascii",errors="backslashreplace").write(rep)
print("WROTE results/_r717bmb_probe_out.txt", len(out))
