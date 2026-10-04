import subprocess, json, io, os

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
faces = [
 "docs/daily_report/REPORT-2026-10-04.json",
 "docs/daily_report/REPORT-2026-10-04.md",
 "docs/live_usage/LIVE-2026-10-04.json",
 "docs/live_usage/LIVE-2026-10-04.md",
 "docs/live_usage/LIVE-latest.json",
 "docs/live_usage/LIVE-latest.md",
 "results/_attrition_guard_scan.json",
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

def blob(rev, path):
    r = subprocess.run(["git", "-C", ROOT, "show", rev + ":" + path],
                       capture_output=True, timeout=30)
    return r.stdout, r.returncode

def jget(b, keys):
    try:
        d = json.loads(b.decode("utf-8", "replace"))
    except Exception:
        return None
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return None
    return d

lines = []
for f in faces:
    ours, orc = blob("HEAD", f)
    theirs, trc = blob("MERGE_HEAD", f)
    same = ours == theirs
    o_ts = jget(ours, ["ts"]) or jget(ours, ["generated_at"]) or jget(ours, ["asof"]) or jget(ours, ["updated"])
    t_ts = jget(theirs, ["ts"]) or jget(theirs, ["generated_at"]) or jget(theirs, ["asof"]) or jget(theirs, ["updated"])
    lines.append("%s same=%s ours_ts=%s theirs_ts=%s ours_len=%d theirs_len=%d" % (f, same, o_ts, t_ts, len(ours), len(theirs)))

# token_usage machines keys per side
ou, _ = blob("HEAD", "results/token_usage.json")
tu, _ = blob("MERGE_HEAD", "results/token_usage.json")
try:
    od = json.loads(ou.decode("utf-8", "replace"))
    td = json.loads(tu.decode("utf-8", "replace"))
    om = set((od.get("machines") or {}).keys())
    tm = set((td.get("machines") or {}).keys())
    lines.append("token_usage ours_machines=%s" % sorted(om))
    lines.append("token_usage theirs_machines=%s" % sorted(tm))
    lines.append("token_usage top keys ours=%s theirs=%s" % (sorted(od.keys()), sorted(td.keys())))
except Exception as e:
    lines.append("token_usage probe exc %r" % (e,))

out = os.path.join(ROOT, "results", "_r676bmb_uu_probe.txt")
with io.open(out, "w", encoding="utf-8") as fh:
    fh.write("\n".join(str(x) for x in lines))
print("OK " + out)
