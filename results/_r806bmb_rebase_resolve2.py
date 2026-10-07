"""r806 bm-b rebase resolve (generic daemon-face family) -- handles UU subset among:
  snapshots : p1d_gates.json (meta.date) / saturation face_bm-b / state_bm-b (deep ts) -> take-newer
  append-log: nulls.jsonl (k) / history_bm-b.jsonl (ts) -> line union zero-loss, sorted
  mixed     : autofill_state.bm-b.json (launches union cap50 asc, last_tick take-new, CRLF mirror)
Side law: ours = rebased branch (newer daemon states), theirs = replayed older absorb commit.
Usage: python results/_r806bmb_rebase_resolve2.py
"""
import subprocess, json, re, sys

def run(args):
    r = subprocess.run(args, capture_output=True)
    if r.returncode != 0:
        print("CMD FAIL", args, r.stderr.decode("utf-8", "replace")[:300]); sys.exit(1)
    return r.stdout

def blob(stage, path):
    return run(["git", "show", f":{stage}:{path}"])

def deep_ts(d):
    best = ""
    def scan(x):
        nonlocal best
        if isinstance(x, dict):
            for k, v in x.items():
                kk = str(k).lower().replace("_", "").replace("-", "")
                if isinstance(v, str) and ("ts" in kk or "time" in kk or "updated" in kk or "date" in kk) and re.match(r"^20\d{2}-", v):
                    if v > best: best = v
                else:
                    scan(v)
        elif isinstance(x, list):
            for v in x[:5]: scan(v)
    scan(d)
    return best

SNAP = {
    "results/p1d_gates.json": None,
    "results/saturation_engine/face_bm-b.json": None,
    "results/saturation_engine/state_bm-b.json": None,
}
JSONL = {
    "results/fund_divlowvol_p1/nulls.jsonl": "k",
    "results/saturation_engine/history_bm-b.jsonl": "ts",
    "results/paper/marks/marks-20261007.jsonl": "ts",
}

def resolve_snapshot(path):
    o = json.loads(blob(2, path).decode("utf-8"))
    t = json.loads(blob(3, path).decode("utf-8"))
    ot, tt = deep_ts(o), deep_ts(t)
    if ot >= tt:
        win, side = o, "ours"
    else:
        win, side = t, "theirs"
    raw = blob(2 if side == "ours" else 3, path)
    crlf = b"\r\n" in raw[:2000]
    body = json.dumps(win, ensure_ascii=False, indent=1)
    if crlf: body = body.replace("\n", "\r\n")
    enc = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    with open(path, "w", encoding=enc, newline="") as f:
        f.write(body)
    print(f"snapshot take-{side}: {path} (ours={ot} theirs={tt})")

def resolve_jsonl(path, skey):
    oraw = blob(2, path); traw = blob(3, path)
    olines = [l for l in oraw.decode("utf-8", errors="replace").splitlines() if l.strip()]
    tlines = [l for l in traw.decode("utf-8", errors="replace").splitlines() if l.strip()]
    seen, union = set(), []
    for l in olines + tlines:
        if l not in seen:
            seen.add(l); union.append(l)
    def key(l):
        try:
            v = json.loads(l).get(skey)
            return (0, v) if isinstance(v, (int, float)) else (1, str(v))
        except Exception:
            return (2, l)
    union.sort(key=key)
    crlf = b"\r\n" in oraw[:2000]
    sep = "\r\n" if crlf else "\n"
    enc = "utf-8-sig" if oraw.startswith(b"\xef\xbb\xbf") else "utf-8"
    with open(path, "w", encoding=enc, newline="") as f:
        f.write(sep.join(union) + sep)
    print(f"jsonl union: {path} ours={len(olines)} theirs={len(tlines)} -> {len(union)} (zero-loss)")
    return len(olines), len(tlines), len(union)

def resolve_autofill(path):
    oraw = blob(2, path); traw = blob(3, path)
    o = json.loads(oraw.decode("utf-8")); t = json.loads(traw.decode("utf-8"))
    lo, lt = o.get("launches", []), t.get("launches", [])
    seen, union = set(), []
    for l in lo + lt:
        ks = json.dumps(l, sort_keys=True, ensure_ascii=False)
        if ks not in seen:
            seen.add(ks); union.append(l)
    union.sort(key=lambda x: x.get("ts", ""), reverse=True)
    union = union[:50]
    union.sort(key=lambda x: x.get("ts", ""))
    olt, tlt = o.get("last_tick"), t.get("last_tick")
    if isinstance(olt, dict) and isinstance(tlt, dict):
        last = olt if olt.get("ts", "") >= tlt.get("ts", "") else tlt
    else:
        last = olt if olt else tlt
    assert isinstance(last, dict), "last_tick must be dict"
    merged = dict(o)
    merged["launches"] = union
    merged["last_tick"] = last
    for k, v in t.items():
        if k not in merged:
            merged[k] = v
    crlf = b"\r\n" in oraw[:2000]
    body = json.dumps(merged, ensure_ascii=False, indent=1)
    if crlf: body = body.replace("\n", "\r\n")
    enc = "utf-8-sig" if oraw.startswith(b"\xef\xbb\xbf") else "utf-8"
    with open(path, "w", encoding=enc, newline="") as f:
        f.write(body)
    json.loads(open(path, "rb").read().decode(enc))
    assert isinstance(json.loads(open(path, "rb").read().decode(enc)).get("last_tick"), dict)
    print(f"autofill mixed: launches {len(lo)}+{len(tl)} -> union {len(union)} (cap50 asc), last_tick take-new")

# detect conflicted set
out = run(["git", "diff", "--name-only", "--diff-filter=U"])
conflicted = [l for l in out.decode("utf-8").splitlines() if l.strip()]
print("conflicted:", conflicted)
for p in conflicted:
    if p in SNAP:
        resolve_snapshot(p)
    elif p in JSONL:
        resolve_jsonl(p, JSONL[p])
    elif p == "results/autofill_state.bm-b.json":
        resolve_autofill(p)
    else:
        print(f"UNHANDLED: {p}"); sys.exit(2)
# parse-validation gate on all touched json (r185)
for p in conflicted:
    if p.endswith(".json"):
        raw = open(p, "rb").read()
        if raw.startswith(b"\xef\xbb\xbf"): raw = raw[3:]
        json.loads(raw.decode("utf-8"))
print("RESOLVE2 OK")
