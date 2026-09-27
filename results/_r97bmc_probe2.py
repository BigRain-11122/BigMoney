# -*- coding: utf-8 -*-
"""r97 bm-c probe2: special faces deep-dive (rolling ledgers, equal-size conflicts)."""
import subprocess, json

MINE = "32b4edae"

def side(ref, path):
    return subprocess.run(["git", "show", "%s:%s" % (ref, path)], capture_output=True).stdout

def j(ref, path):
    return json.loads(side(ref, path).decode("utf-8"))

# 1) autofill_state.json: last_tick blocks + launches census
for name, ref in (("A", "HEAD"), ("M", MINE)):
    d = j(ref, "results/autofill_state.json")
    lt = d.get("last_tick", {})
    launches = d.get("launches", [])
    print("AUTOFILL", name, "last_tick=", lt, "| launches n=", len(launches),
          "| last-launch keys=", sorted(launches[-1].keys()) if launches else None)
    if launches:
        print("   last launch:", json.dumps(launches[-1], ensure_ascii=False)[:300])

# 2) compute_audit.json: structure + history rows both sides
for name, ref in (("A", "HEAD"), ("M", MINE)):
    d = j(ref, "results/compute_audit.json")
    hist = d.get("history", [])
    print("AUDIT", name, "top-keys=", sorted(d.keys())[:12], "| history n=", len(hist),
          "| hist[0] ts=", hist[0].get("ts") if hist else None,
          "| hist[-1] ts=", hist[-1].get("ts") if hist else None,
          "| head ts=", d.get("ts"), "machine=", d.get("machine"))

# 3) daily_scorecard.json: where do sides differ?
a, m = side("HEAD", "results/daily_scorecard.json"), side(MINE, "results/daily_scorecard.json")
if a == m:
    print("DAILY_SCORECARD: byte-identical")
else:
    da, dm = json.loads(a.decode()), json.loads(m.decode())
    diffk = [k for k in set(da) | set(dm) if da.get(k) != dm.get(k)]
    print("DAILY_SCORECARD diff keys:", diffk[:10])

# 4) paper_export twins: byte compare
for p in ("results/paper_export/export-2026-09-24.json", "results/paper_export/latest.json"):
    a, m = side("HEAD", p), side(MINE, p)
    print("EXPORT", p, "identical=", a == m, "| lenA=", len(a), "lenM=", len(m))
    if a != m:
        da, dm = json.loads(a.decode()), json.loads(m.decode())
        diffk = [k for k in set(da) | set(dm) if da.get(k) != dm.get(k)]
        print("   diff keys:", diffk[:10])

# 5) token_usage.json: structure + per-machine rows
for name, ref in (("A", "HEAD"), ("M", MINE)):
    d = j(ref, "results/token_usage.json")
    print("TOKEN", name, "top-keys=", sorted(d.keys()))
    for k, v in d.items():
        if isinstance(v, dict):
            print("   ", k, "->", {kk: (str(vv)[:40]) for kk, vv in list(v.items())[:6]})

# 6) x2_watch_log.jsonl: line-level diff census
a = side("HEAD", "results/x2_watch_log.jsonl").decode("utf-8").splitlines()
m = side(MINE, "results/x2_watch_log.jsonl").decode("utf-8").splitlines()
sa, sm = set(a), set(m)
print("X2LOG linesA=%d linesM=%d | A-only=%d M-only=%d | common=%d" % (len(a), len(m), len(sa - sm), len(sm - sa), len(sa & sm)))
for ln in sorted(sa - sm)[-3:]:
    print("  A-only tail:", ln[:150])
for ln in sorted(sm - sa)[-3:]:
    print("  M-only tail:", ln[:150])
print("  A tail:", a[-1][:150])
print("  M tail:", m[-1][:150])
