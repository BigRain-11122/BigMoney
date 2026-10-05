# r717 bm-b fix-forward: heal 7 marker-contaminated faces committed in 5cef1b3f4
# (root cause: resolve2 union_ledger returned a str as 2nd element in bt-branch ->
#  crash at payload[k] -> pass-2 twins + post-sort snapshots never resolved ->
#  git add -A staged raw conflict-marker working files; rebase-continue does NOT
#  run the pre-commit claw -> markers entered pick-1 commit 5cef1b3f4)
# Sides for adjudication: origin=868b26f52:<p>, churn=4cf15abad:<p> (wave-2 pick-1 parents)
import subprocess, json, io, re

ORIGIN_SHA = "868b26f52"
CHURN_SHA  = "4cf15abad"

WAVE2_FACES = ["docs/live_usage/LIVE-2026-10-05.json","docs/live_usage/LIVE-2026-10-05.md",
               "docs/live_usage/LIVE-latest.json","docs/live_usage/LIVE-latest.md",
               "results/compute_audit.json","results/dashboard_status.js",
               "results/dashboard_status.json","results/fundamental_b_layer_filter.json",
               "results/futures_update_status.json","results/lhb_update_status.json",
               "results/regime_state.json","results/scorecard_v1.json",
               "results/strategy_scorecard.json","results/token_usage.json",
               "results/update_status.json"]

TSRE = re.compile(r"^20\d{2}-")
CLOCKRE = re.compile(r"[T ]\d{2}:\d{2}")
STEMS = ("asof","updated","generated","lastseen","lasttick","timestamp","cutoff",
         "heartbeat","lastrun","last","ts","time","date","epoch")

def gitshow(sha, path):
    r = subprocess.run(["git","show",f"{sha}:{path}"], capture_output=True)
    assert r.returncode == 0, f"git show {sha}:{path} rc={r.returncode}"
    b = r.stdout
    assert len(b) > 100, f"{sha}:{path} small {len(b)}B (r710-B)"
    return b

def normkey(k): return k.replace("_","").replace("-","").lower()
def normts(v): return v.replace("T"," ")[:19]

def deep_ts(obj, out=None):
    if out is None: out = []
    if isinstance(obj, dict):
        for k,v in obj.items():
            nk = normkey(k)
            if isinstance(v,str) and TSRE.match(v) and CLOCKRE.search(v) \
               and any(s in nk for s in STEMS):
                out.append(normts(v))
            deep_ts(v, out)
    elif isinstance(obj, list):
        for v in obj: deep_ts(v, out)
    return out

def face_ts(j):
    vals = deep_ts(j)
    return max(vals) if vals else ""

def md_ts(text):
    vals = [normts(m.group(0)) for m in re.finditer(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", text)]
    return max(vals) if vals else ""

report, lines = [], []

# 1) confirm contamination set in current tree
contaminated = []
for p in WAVE2_FACES:
    b = open(p,"rb").read()
    if b"<<<<<<<" in b or b">>>>>>>" in b:
        contaminated.append(p)
report.append("contaminated-in-HEAD: " + ", ".join(contaminated))

def take(p, sha, tag):
    b = gitshow(sha, p)
    if p.endswith(".json"):
        json.loads(b)
    open(p,"wb").write(b)
    back = open(p,"rb").read()
    assert b"<<<<<<<" not in back and b">>>>>>>" not in back
    report.append(f"{p}: FIX take:{tag} {len(b)}B")

# 2) json snapshot faces among contaminated: deep-ts probe both sides, tie->origin
side_of = {}
for p in [x for x in contaminated if x.endswith(".json") and x != "results/regime_state.json"]:
    b2, b3 = gitshow(ORIGIN_SHA,p), gitshow(CHURN_SHA,p)
    t2, t3 = face_ts(json.loads(b2)), face_ts(json.loads(b3))
    side_of[p] = 2 if t2 >= t3 else 3
    take(p, ORIGIN_SHA if side_of[p]==2 else CHURN_SHA, "origin" if side_of[p]==2 else "churn")
    report.append(f"{p}: probe t2={t2} t3={t3} -> {'origin' if side_of[p]==2 else 'churn'}")

# 3) regime_state.json: ledger union (fixed union_ledger), state take-new(churn)
if "results/regime_state.json" in contaminated:
    p = "results/regime_state.json"
    j2, j3 = json.loads(gitshow(ORIGIN_SHA,p)), json.loads(gitshow(CHURN_SHA,p))
    payload = dict(j3)
    for k in ("history","transitions"):
        by, dk = {}, None
        for side in (j2.get(k,[]), j3.get(k,[])):
            for e in side:
                if dk is None:
                    for cand in ("ts","asof"):
                        if cand in e: dk = cand; break
                assert dk and dk in e, f"dedup key missing {p}:{k} (r319)"
                by[e[dk]] = e
        merged = sorted(by.values(), key=lambda e: e[dk])
        expected = len(set([e[dk] for e in j2.get(k,[])] + [e[dk] for e in j3.get(k,[])]))
        assert len(merged) == expected, "union not zero-loss"
        payload[k] = merged
    b3 = gitshow(CHURN_SHA,p)
    if json.loads(b3) == payload:
        open(p,"wb").write(b3)
        report.append(f"{p}: FIX union==churn-blob verbatim history={len(payload['history'])} transitions={len(payload['transitions'])}")
    else:
        s = json.dumps(payload, indent=2, ensure_ascii=False)
        if b"\r\n" in b3: s = s.replace("\n","\r\n")
        if b3.endswith(b"\n"): s += "\r\n" if b"\r\n" in b3 else "\n"
        open(p,"wb").write(s.encode("utf-8"))
    rp = json.loads(open(p,"rb").read().decode("utf-8"))
    assert rp["history"] == payload["history"] and rp["state"] == j3["state"], "re-read mismatch (r704)"
    assert b"<<<<<<<" not in open(p,"rb").read()

# 4) twins follow their json decision (adjudicate clean json sides on demand)
for p in [x for x in contaminated if x.endswith(".md") or x.endswith(".js")]:
    tj = p[:-3]+".json" if p.endswith(".md") else "results/dashboard_status.json"
    if tj not in side_of:
        b2, b3 = gitshow(ORIGIN_SHA,tj), gitshow(CHURN_SHA,tj)
        t2, t3 = face_ts(json.loads(b2)), face_ts(json.loads(b3))
        side_of[tj] = 2 if t2 >= t3 else 3
        report.append(f"(twin-anchor {tj}: probe t2={t2} t3={t3} -> {'origin' if side_of[tj]==2 else 'churn'})")
    side = side_of[tj]
    take(p, ORIGIN_SHA if side==2 else CHURN_SHA, "twin-follows-json:" + ("origin" if side==2 else "churn"))

# 5) final marker scan over ALL wave2 faces (claw-compensation, r713 zero-UU analogue)
for p in WAVE2_FACES:
    b = open(p,"rb").read()
    assert b"<<<<<<<" not in b and b">>>>>>>" not in b, f"markers remain in {p}"
report.append("marker-scan: ALL 15 wave-2 faces CLEAN")

# twin family side consistency (r510)
live = {v for k,v in side_of.items() if "LIVE" in k}
assert len(live) <= 1, f"LIVE family split: {live}"

io.open(r"results\_r717bmb_resolve_report.txt","a",encoding="ascii").write(
    "== wave-2 fix-forward (heal 5cef1b3f4 contamination, pre-push) ==\n"
    + "\n".join(report) + "\n")
print("FIXFORWARD-OK")
for l in report: print(l)
