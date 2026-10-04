# r717 bm-b merge-mode resolver (r708 canon) -- generic, fixed bt-branch return
# Stage mapping MERGE mode (r701-3): :2: = ours (local HEAD), :3: = theirs (origin).
# Canon: deep-ts take-newer (r98/r100/R350 probes, r711 format-normalized);
# tie -> origin (r140); twins follow json (r510/r708); ledger union zero-loss
# (r188/R208); bm-b-owned faces take ours (lane ownership, R31/r669 basename filter);
# parse-verify before write (r185); re-read verify (r704); no key-exclusion (R350).
import subprocess, json, io, re, sys

MODE = sys.argv[1] if len(sys.argv) > 1 else "merge"
# stage numbers: (ours_stage, theirs_stage)
OURS, THEIRS = ("2","3") if MODE == "merge" else ("3","2")

TSRE = re.compile(r"^20\d{2}-")
CLOCKRE = re.compile(r"[T ]\d{2}:\d{2}")
STEMS = ("asof","updated","generated","lastseen","lasttick","timestamp","cutoff",
         "heartbeat","lastrun","last","ts","time","date","epoch")
LEDGER = {"results/compute_audit.json": ["history"],
          "results/regime_state.json": ["history","transitions"]}
TWIN_OF = {"results/dashboard_status.js": "results/dashboard_status.json"}
BM_B_OWNED_PAT = re.compile(r"\.bm-b\.|_bm-b\.|bmb|nulls\.jsonl$|pool_dualrun")

def sh(a): return subprocess.run(a, capture_output=True)

def uu_faces():
    r = sh(["git","diff","--name-only","--diff-filter=U"])
    return [l for l in r.stdout.decode("utf-8","replace").splitlines() if l.strip()]

def blob(stage, path):
    r = sh(["git","show",f":{stage}:{path}"])
    assert r.returncode == 0, f"git show :{stage}:{path} rc={r.returncode}"
    b = r.stdout
    assert len(b) > 60, f"stage {stage} {path} small {len(b)}B (r710-B)"
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
    v = deep_ts(j); return max(v) if v else ""

def md_ts(text):
    v = [normts(m.group(0)) for m in re.finditer(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", text)]
    return max(v) if v else ""

def union_entries(a, b, k, path):
    by, dk = {}, None
    for side in (a, b):
        for e in side:
            if dk is None:
                for cand in ("ts","asof"):
                    if cand in e: dk = cand; break
            assert dk and dk in e, f"dedup key missing {path}:{k} (r319)"
            by[e[dk]] = e
    merged = sorted(by.values(), key=lambda e: e[dk])
    expected = len(set([e[dk] for e in a] + [e[dk] for e in b]))
    assert len(merged) == expected, f"union not zero-loss {path}:{k}"
    return merged

def emit(path, payload_dict, base_blob, tag):
    s = json.dumps(payload_dict, indent=2, ensure_ascii=False)
    if b"\r\n" in base_blob: s = s.replace("\n","\r\n")
    if base_blob.endswith(b"\n"): s += "\r\n" if b"\r\n" in base_blob else "\n"
    data = s.encode("utf-8")
    json.loads(data.decode("utf-8"))               # r185
    open(path,"wb").write(data)
    rp = json.loads(open(path,"rb").read().decode("utf-8"))
    assert rp == payload_dict, f"re-read mismatch {path} (r704)"
    return tag

def take_raw(path, data, tag):
    if path.endswith(".json"):
        json.loads(data)                            # r185 on winning blob
    open(path,"wb").write(data)
    back = open(path,"rb").read()
    assert b"<<<<<<<" not in back and b">>>>>>>" not in back
    return tag

report, side_of = [], {}
faces = sorted(uu_faces())

for p in faces:
    bo, bt = blob(OURS,p), blob(THEIRS,p)
    if BM_B_OWNED_PAT.search(p):
        report.append(f"{p}: take-ours(bm-b-owned lane) {take_raw(p, bo, f'{len(bo)}B')}")
        continue
    if p.endswith(".jsonl"):
        # append-log: line-level union zero-loss (r188), tolerate pre-existing bad lines (r707)
        lo = [l for l in bo.decode("utf-8","replace").splitlines() if l.strip()]
        lt = [l for l in bt.decode("utf-8","replace").splitlines() if l.strip()]
        bad_o = {l for l in lo if not l.startswith("{")}
        bad_t = {l for l in lt if not l.startswith("{")}
        merged = []
        seen = set()
        for l in lo + lt:
            if l in seen: continue
            seen.add(l); merged.append(l)
        assert all(l.startswith("{") for l in merged if l not in bad_o and l not in bad_t)
        data = ("\r\n" if b"\r\n" in bo else "\n").join(merged).encode("utf-8")
        if bo.endswith(b"\n"): data += b"\r\n" if b"\r\n" in bo else b"\n"
        open(p,"wb").write(data)
        report.append(f"{p}: jsonl line-union |A|={len(lo)} |B|={len(lt)} |AUB|={len(merged)}")
        continue
    if p.endswith(".json"):
        jo, jt = json.loads(bo), json.loads(bt)
        if p in LEDGER:
            to, tt = face_ts(jo), face_ts(jt)
            base = jo if to >= tt else jt          # state fields take-new
            payload = dict(base)
            for k in LEDGER[p]:
                payload[k] = union_entries(jo.get(k,[]), jt.get(k,[]), k, p)
            tag = f"union keys={ {k: len(payload[k]) for k in LEDGER[p]} } state={'ours' if base is jo else 'theirs'}"
            if json.loads(bo) == payload:
                report.append(f"{p}: {take_raw(p, bo, 'union==ours-blob verbatim')}")
            elif json.loads(bt) == payload:
                report.append(f"{p}: {take_raw(p, bt, 'union==theirs-blob verbatim')}")
            else:
                report.append(f"{p}: {emit(p, payload, bo, tag)}")
        else:
            to, tt = face_ts(jo), face_ts(jt)
            side = "ours" if to > tt else "theirs"   # tie -> theirs/origin (r140)
            side_of[p] = side
            report.append(f"{p}: take-{side} t_ours={to} t_theirs={tt} {take_raw(p, bo if side=='ours' else bt, '')}")
    else:
        tj = TWIN_OF.get(p) or (p[:-3]+".json" if p.endswith(".md") else None)
        if tj and tj in side_of:
            side = side_of[tj]
        elif tj:
            bjo, bjt = blob(OURS,tj), blob(THEIRS,tj)
            to, tt = face_ts(json.loads(bjo)), face_ts(json.loads(bjt))
            side = "ours" if to > tt else "theirs"
        else:
            to, tt = md_ts(bo.decode("utf-8","replace")), md_ts(bt.decode("utf-8","replace"))
            side = "ours" if to > tt else "theirs"
        data = bo if side == "ours" else bt
        report.append(f"{p}: twin/text take-{side} {take_raw(p, data, f'{len(data)}B')}")

# marker scan over all resolved faces (claw-compensation; rebase-continue claw blind)
for p in faces:
    b = open(p,"rb").read()
    assert b"<<<<<<<" not in b and b">>>>>>>" not in b, f"markers remain {p}"

# LIVE family same side (r510)
live = {v for k,v in side_of.items() if "LIVE" in k}
assert len(live) <= 1, f"LIVE family split: {live}"

io.open(r"results\_r717bmb_resolve_report.txt","a",encoding="ascii").write(
    f"== merge-mode wave-3 (MODE={MODE}) ==\n" + "\n".join(report) + "\n")
print(f"RESOLVED-MERGE {len(report)} faces")
for l in report: print(l)
