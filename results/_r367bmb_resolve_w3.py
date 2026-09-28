"""r367 bm-b wave-3 resolver: 9 UU vs bm-c r147 S6 faces. take-new by ts per file; compute_audit = history union + latest-new."""
import subprocess, json, re, sys

SNAP = ["docs/daily_report/REPORT-2026-09-28.json","docs/daily_report/REPORT-2026-09-28.md",
        "results/fundamental_b_layer_filter.json","results/futures_update_status.json",
        "results/lhb_update_status.json","results/regime_state.json","results/token_usage.json",
        "results/update_status.json"]
CA = "results/compute_audit.json"
TS_RE = re.compile(r'"(generated_at|generated|updated|ts|now)"\s*:\s*"?(\d{4}-\d{2}-\d{2}[T ][\d:.]+)\??', re.S)

def blob(stage, path):
    r = subprocess.run(["git","show",":%d:%s"%(stage,path)],capture_output=True)
    if r.returncode: sys.exit("blob fail "+path)
    return r.stdout

def maxts(b):
    hits = TS_RE.findall(b.decode("utf-8","replace"))
    return max((t for _, t in hits), default="")

for p in SNAP:
    o, t = blob(2,p), blob(3,p)
    mo, mt = maxts(o), maxts(t)
    side = 2 if mo >= mt else 3
    why = "ours(origin)" if side==2 else "theirs(local r367)"
    if mo == mt and o != t:
        # same max ts but bytes differ -> deeper look: prefer origin unless local has strictly-newer content
        side = 2 if len(o) >= len(t) else 3
        why = "tie->%s" % ("ours" if side==2 else "theirs")
    r = subprocess.run(["git","checkout","--%s"%("ours" if side==2 else "theirs"),"--",p],capture_output=True)
    if r.returncode: sys.exit("checkout fail "+p)
    b = open(p,"rb").read()
    assert b"<<<<<<<" not in b and b">>>>>>>" not in b
    if p.endswith(".json"): json.loads(b.decode("utf-8"))
    print("  %-46s %s (o=%s t=%s)" % (p, why, mo[:19], mt[:19]))

o, t = blob(2,CA), blob(3,CA)
jo, jt = json.loads(o.decode("utf-8")), json.loads(t.decode("utf-8"))
seen, merged = set(), []
for row in jo.get("history",[])+jt.get("history",[]):
    k = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if k not in seen: seen.add(k); merged.append(row)
merged.sort(key=lambda r: r.get("ts",""))
cap = merged[-200:]
lo, lt = jo.get("latest",{}).get("ts",""), jt.get("latest",{}).get("ts","")
base = jo if lo >= lt else jt   # take-new side = whichever latest is newer (here local r367 08:01:32 > origin 07:58:42)
out = dict(base); out["history"] = cap
tail = b"\n" if o.endswith(b"}\n") else b""
open(CA,"wb").write(json.dumps(out, indent=2, ensure_ascii=False).encode("utf-8")+tail)
json.loads(open(CA,encoding="utf-8").read())
print("  compute_audit union: o=%d t=%d -> %d (latest side=%s ts=%s)" % (len(jo["history"]),len(jt["history"]),len(cap), "origin" if lo>=lt else "local", max(lo,lt)))
print("WAVE3 RESOLVED")
