# r415 bm-b: probe both staged blobs (take 2: ours=6eb3da16f bm-a r419 merge-back, theirs=dba9db889 bm-b r414)
import subprocess, json, re

FILES = [
    "docs/daily_report/REPORT-2026-09-29.json",
    "docs/live_usage/LIVE-2026-09-29.json",
    "docs/live_usage/LIVE-latest.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/runnable_pool.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def blob(path, stage):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else None

def deep_ts(obj, path=""):
    best = None
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).replace("_", "").replace("-", "").lower()
            if isinstance(v, str) and re.match(r"^20\d{2}-", v) and re.search(r"[T ]\d{2}:\d{2}", v):
                if any(nk.startswith(p) for p in ("asof", "generated", "updated", "cutoff", "timestamp")) or nk == "ts":
                    cand = v.replace("T", " ")
                    if best is None or cand > best[0]:
                        best = (cand, path + "/" + str(k))
            b2 = deep_ts(v, path + "/" + str(k))
            if b2 and (best is None or b2[0] > best[0]):
                best = b2
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            b2 = deep_ts(v, path + "/%d" % i)
            if b2 and (best is None or b2[0] > best[0]):
                best = b2
    return best

for f in FILES:
    res = {}
    for stage, tag in ((2, "ours(bm-a-r419)"), (3, "bm-b-r414")):
        raw = blob(f, stage)
        if raw is None:
            res[tag] = "MISSING"; continue
        txt = raw.decode("utf-8", "replace")
        try:
            res[tag] = deep_ts(json.loads(txt))
        except Exception:
            m = re.search(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", txt)
            res[tag] = (m.group(0), "regex") if m else None
    o, b = res.get("ours(bm-a-r419)"), res.get("bm-b-r414")
    pick = "?"
    if isinstance(o, tuple) and isinstance(b, tuple):
        pick = "ours(bm-a)" if o[0] > b[0] else ("bm-b" if b[0] > o[0] else "TIE->ours(HEAD)")
    print("%-55s ours=%s bmb=%s => %s" % (f, o, b, pick))

# runnable_pool structure
for stage, tag in ((2, "ours(bm-a-r419)"), (3, "bm-b-r414")):
    raw = blob("results/runnable_pool.json", stage)
    j = json.loads(raw)
    print(tag, "runnable_pool top:", sorted(j.keys())[:10])
    tasks = j.get("tasks") or j.get("pool") or j.get("items")
    if isinstance(tasks, list):
        print(tag, "tasks len:", len(tasks), "entry keys:", sorted(tasks[0].keys()) if tasks else None)
