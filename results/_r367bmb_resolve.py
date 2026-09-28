"""r367 bm-b S0 push-storm wave-1 resolver (discharge r366 escape branch per skill bigmoney-conflict-resolve).
State: rebase replaying 4d9acacf (r366) onto 70b42c69 (origin = bm-a r391 + bm-c r145).
Sides: stage2=ours=origin(newest 07:47-07:49), stage3=theirs=local r366(07:34-07:37).
Recipes: 21x take-new(checkout --ours) / compute_audit history-union cap200+latest-new /
x2_watch_log line-union ts-sorted / regime_state whole-ours (probe: parsed-equal except updated).
"""
import subprocess, json, sys

TAKE_NEW = [
 "docs/daily_report/REPORT-2026-09-28.json","docs/daily_report/REPORT-2026-09-28.md",
 "results/daily_scorecard.json","results/dashboard_status.js","results/dashboard_status.json",
 "results/fundamental_b_layer_filter.json","results/futures_update_status.json",
 "results/lhb_update_status.json",
 "results/paper/COMPOSITE-CE-01_paper.json","results/paper/COMPOSITE-CE-02_paper.json",
 "results/paper/DROUGHT-CE-01_paper.json","results/paper/ENGULF-CE-01_paper.json",
 "results/paper/NEEDLE-DE-01_paper.json","results/paper/VOLATILITY-CE-01_paper.json",
 "results/paper_export/export-2026-09-24.json","results/paper_export/latest.json",
 "results/prospect_paper/_summary.json","results/prospect_promotion/_summary.json",
 "results/t35_open_fill_verify.json","results/token_usage.json","results/update_status.json",
]
CA = "results/compute_audit.json"       # history union cap 200 (producer law L272), latest=take-new
X2 = "results/x2_watch_log.jsonl"       # append-log line union
RS = "results/regime_state.json"        # parsed-equal except 'updated' -> whole ours
MARK = (b"<<<<<<<", b">>>>>>>")

def blob(stage, path):
    r = subprocess.run(["git","show",":%d:%s"%(stage,path)],capture_output=True)
    if r.returncode!=0: sys.exit("blob read fail %s" % path)
    return r.stdout

def nows_markers(b, path):
    if MARK[0] in b or MARK[1] in b: sys.exit("conflict markers remain in %s" % path)

def validate(path):
    b = open(path,"rb").read(); nows_markers(b,path)
    if path.endswith(".json"):
        json.loads(b.decode("utf-8"))
    elif path.endswith(".jsonl"):
        for l in b.decode("utf-8").splitlines():
            if l.strip(): json.loads(l)
    elif path.endswith(".js"):
        assert b.startswith(b"window.DASH_DATA = ") and b.rstrip().endswith(b";"), "js wrapper broken"
    print("  OK %s" % path)

# --- 1. take-new: whole ours bytes ---
for p in TAKE_NEW+[RS]:
    r = subprocess.run(["git","checkout","--ours","--",p],capture_output=True)
    if r.returncode!=0: sys.exit("checkout --ours fail %s: %s"%(p,r.stderr.decode()))
    validate(p)

# --- 2. regime_state: confirm parsed-equal-except-updated gate before whole-ours stands ---
jo, jt = json.loads(blob(2,RS)), json.loads(blob(3,RS))
diffk = [k for k in set(jo)|set(jt) if jo.get(k)!=jt.get(k)]
if not set(diffk) <= {"updated"}:
    sys.exit("regime_state unexpected diff keys %r -- hand-resolve" % diffk)
print("  regime_state gate: diff keys %r (subset of updated) -> whole-ours stands" % diffk)

# --- 3. compute_audit: history union (dedupe by row bytes, ts asc, cap last 200), latest=newest ---
o, t = blob(2,CA), blob(3,CA)
jo, jt = json.loads(o.decode("utf-8")), json.loads(t.decode("utf-8"))
seen, merged = set(), []
for row in jo.get("history",[])+jt.get("history",[]):
    key = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if key not in seen: seen.add(key); merged.append(row)
merged.sort(key=lambda r: r.get("ts",""))
cap = merged[-200:]
n_o, n_t = len(jo.get("history",[])), len(jt.get("history",[]))
print("  compute_audit history: ours=%d theirs=%d union=%d -> cap200=%d" % (n_o,n_t,len(merged),len(cap)))
assert len(cap) == len(set(json.dumps(r,sort_keys=True,ensure_ascii=False) for r in cap)), "cap dup"
lo, lt = jo.get("latest",{}).get("ts"), jt.get("latest",{}).get("ts")
assert lo and (not lt or lo >= lt), "latest not newest?!"
out = dict(jo); out["history"] = cap
tail = b"\n" if o.endswith(b"}\n") else b""
open(CA,"wb").write(json.dumps(out, indent=2, ensure_ascii=False).encode("utf-8")+tail)
validate(CA)

# --- 4. x2_watch_log: line-level union sorted by ts, mirror ours newline ---
# r389 CRLF lineage law: blob lines carry trailing \r when CRLF; strip before re-join
# (wave-1 bug: joined \r-carrying lines with \r\n -> \r\r\n doubled terminator)
o, t = blob(2,X2), blob(3,X2)
nl = b"\r\n" if b"\r\n" in o else b"\n"
def _strip(l):
    while l.endswith(b"\r"): l = l[:-1]
    return l
strip = _strip
ol, tl = [strip(l) for l in o.split(b"\n") if l.strip()], [strip(l) for l in t.split(b"\n") if l.strip()]
seen, merged = set(), []
for l in ol+tl:
    if l not in seen: seen.add(l); merged.append((json.loads(l.decode("utf-8")).get("ts",""), l))
merged.sort(key=lambda x: x[0])
u_o, u_t = len(set(ol)-set(tl)), len(set(tl)-set(ol))
print("  x2_watch_log: ours=%d theirs=%d ours-only=%d theirs-only=%d union=%d" % (len(ol),len(tl),u_o,u_t,len(merged)))
assert len(merged)==len(set(ol)|set(tl)), "union not zero-loss"
open(X2,"wb").write(nl.join(l for _,l in merged)+(nl if o.endswith(b"\n") else b""))
validate(X2)

print("WAVE1 RESOLVED: %d take-new/whole-ours + %d union-ledgers" % (len(TAKE_NEW)+1, 2))
