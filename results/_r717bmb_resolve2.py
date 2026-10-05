# r717 bm-b generic per-face rebase resolver (wave-2) -- r712 lineage
# Auto-adjudicates ALL UU faces: deep-ts probe (R350 hardened, cross-side format
# normalized per r711/r709), tie->origin (:2:) per r140, twins same side (r510/r708),
# rolling-ledger union zero-loss (r188/R208), parse-verify before write (r185),
# stage-blob reads via python subprocess bytes (r710-A/B).
import subprocess, json, io, re, sys

TSRE = re.compile(r"^20\d{2}-")
CLOCKRE = re.compile(r"[T ]\d{2}:\d{2}")
STEMS = ("asof","updated","generated","lastseen","lasttick","timestamp","cutoff",
         "heartbeat","lastrun","last","ts","time","date","epoch")

def sh(args):
    return subprocess.run(args, capture_output=True)

def uu_faces():
    r = sh(["git","diff","--name-only","--diff-filter=U"])
    return [l for l in r.stdout.decode("utf-8","replace").splitlines() if l.strip()]

def blob(stage, path):
    r = sh(["git","show",f":{stage}:{path}"])
    assert r.returncode == 0, f"git show :{stage}:{path} rc={r.returncode}"
    b = r.stdout
    assert len(b) > 100, f"stage {stage} {path} small ({len(b)}B) r710-B"
    return b

def normkey(k):
    return k.replace("_","").replace("-","").lower()

def normts(v):
    # r711/r709 cross-side fair compare: strip tz, unify T->space, keep 19 chars
    return v.replace("T"," ")[:19]

def deep_ts(obj, path="", out=None):
    if out is None: out = []
    if isinstance(obj, dict):
        for k,v in obj.items():
            nk = normkey(k)
            if isinstance(v,str) and TSRE.match(v) and CLOCKRE.search(v) \
               and any(s in nk for s in STEMS):
                out.append(normts(v))
            deep_ts(v, path+"/"+k, out)
    elif isinstance(obj, list):
        for v in obj:
            deep_ts(v, path, out)
    return out

def face_ts(j):
    vals = deep_ts(j)
    return max(vals) if vals else ""

def md_ts(text):
    vals = [normts(m) for m in re.findall(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", text)]
    return max(vals) if vals else ""

LEDGER = {"results/compute_audit.json": (["history"], "ts"),
          "results/regime_state.json": (["history","transitions"], None)}

TWIN_OF = {"dashboard_status.js": "results/dashboard_status.json"}

def twin_json(path):
    if path in TWIN_OF:
        return TWIN_OF[path]
    if path.endswith(".md"):
        return path[:-3] + ".json"
    return None

def union_ledger(path, j2, j3):
    keys, _ = LEDGER[path]
    payload = dict(j3)                      # state fields take-new (replay side = bm-b regen newer)
    for k in keys:
        by, dk = {}, None
        for side in (j2.get(k,[]), j3.get(k,[])):
            for e in side:
                if dk is None:
                    for cand in ("ts","asof"):
                        if cand in e: dk = cand; break
                assert dk and dk in e, f"dedup key missing in {path}:{k} (r319)"
                by[e[dk]] = e
        merged = sorted(by.values(), key=lambda e: e[dk])
        expected = len(set([e[dk] for e in j2.get(k,[])] + [e[dk] for e in j3.get(k,[])]))
        assert len(merged) == expected, "union not zero-loss"
        payload[k] = merged
    # if replay blob already equals union result, keep its bytes verbatim
    b3 = blob("3", path)
    if json.loads(b3) == payload:
        return b3, f"union==churn-blob verbatim ({len(merged_keys(keys,payload))})"
    return None, payload

def merged_keys(keys, payload):
    return {k: len(payload[k]) for k in keys}

report = []
faces = uu_faces()
resolved_side = {}

# pass 1: adjudicate all .json (and ledger unions)
for p in sorted(faces):
    if not p.endswith(".json"):
        continue
    b2, b3 = blob("2", p), blob("3", p)
    j2, j3 = json.loads(b2), json.loads(b3)
    if p in LEDGER:
        bt, payload = union_ledger(p, j2, j3)
        if bt is not None:
            data = bt
            resolved_side[p] = "churn-verbatim"
        else:
            s = json.dumps(payload, indent=2, ensure_ascii=False)
            if b"\r\n" in b2: s = s.replace("\n", "\r\n")
            if b2.endswith(b"\n"): s += "\r\n" if b"\r\n" in b2 else "\n"
            data = s.encode("utf-8")
            json.loads(data.decode("utf-8"))          # r185 parse-verify
            chk = json.loads(open(p,"rb").read().decode("utf-8")) if False else payload
            resolved_side[p] = f"union {merged_keys(LEDGER[p][0],payload)}"
        open(p,"wb").write(data)
        # r704 re-read verify
        rp = json.loads(open(p,"rb").read().decode("utf-8"))
        if p in LEDGER:
            for k in LEDGER[p][0]:
                assert rp[k] == payload[k], f"re-read mismatch {p}:{k}"
        report.append(f"{p}: {resolved_side[p]}")
    else:
        t2, t3 = face_ts(j2), face_ts(j3)
        side = 2 if t2 >= t3 else 3                # tie -> origin (r140)
        data = b2 if side == 2 else b3
        json.loads(data)                            # r185 parse-verify winning blob
        open(p,"wb").write(data)
        rp = json.loads(open(p,"rb").read().decode("utf-8"))
        assert rp == (j2 if side==2 else j3), f"re-read mismatch {p}"
        resolved_side[p] = side
        report.append(f"{p}: take:{'origin' if side==2 else 'churn'} t2={t2} t3={t3}")

# pass 2: twins (.md / .js) follow their json decision
for p in sorted(faces):
    if p.endswith(".json"): continue
    tj = twin_json(p)
    if tj and tj in resolved_side:
        side = resolved_side[tj]
        if isinstance(side, str) and "union" in str(side):
            side = 3   # ledger: json came from churn side
        if isinstance(side, int):
            data = blob(str(side), p)
            open(p,"wb").write(data)
            report.append(f"{p}: twin-follows-json take:{'origin' if side==2 else 'churn'}")
        else:
            raise SystemExit(f"twin {p} cannot follow unresolved json {tj}")
    else:
        # no json twin in UU set: adjudicate by text ts probe
        b2, b3 = blob("2", p), blob("3", p)
        t2, t3 = md_ts(b2.decode("utf-8","replace")), md_ts(b3.decode("utf-8","replace"))
        side = 2 if t2 >= t3 else 3
        open(p,"wb").write(b2 if side==2 else b3)
        report.append(f"{p}: text-ts take:{'origin' if side==2 else 'churn'} t2={t2} t3={t3}")

# twin-side assertion for LIVE family (r510): all LIVE-* same side
live_sides = {v for k,v in resolved_side.items() if "LIVE" in k}
assert len(live_sides) <= 1, f"LIVE family split sides: {live_sides}"

# zero-UU recheck (r713) happens in shell after add
io.open(r"results\_r717bmb_resolve_report.txt","a",encoding="ascii").write(
    "== wave-2 (replay 4cf15abad onto 868b26f52) ==\n" + "\n".join(report) + "\n")
print(f"RESOLVED-WAVE2 {len(report)} faces")
for line in report: print(line)
