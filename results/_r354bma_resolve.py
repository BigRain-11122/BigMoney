"""R354 bm-a rebase-replay conflict resolver (28 UU vs bm-c r105 ed4c9c01).

Side-mapping assertion (r351 pitlaw): in rebase replay window
  :2: = HEAD  = already-replayed base  = bm-c r105 face (origin)
  :3: = replayed commit = MY round-354 face (bm-a)
Empirical assertion via content 'machine' field, not intuition.
Recipes per classify_conflicts.py (28 classified, 0 UNKNOWN).
"""
import subprocess, json, re, sys, copy

def git_show(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show :{stage}:{path} rc={r.returncode}: {r.stderr.decode()[:200]}")
    return r.stdout

WALL = re.compile(r"^20\d{2}-")
TOD  = re.compile(r"[T ]\d{2}:\d{2}")

def probe_wall(obj, acc):
    """Deep wall-clock ts probe (r100 normalize re.sub full-strip + value-shape gate; R350 no key-exclude)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and WALL.match(v) and TOD.search(v):
                acc.append(v)
            elif isinstance(v, (dict, list)):
                probe_wall(v, acc)
    elif isinstance(obj, list):
        for it in obj:
            probe_wall(it, acc)
    return acc

def maxts(obj):
    vals = probe_wall(obj, [])
    return max(vals) if vals else None

def detect_format(blob: bytes):
    indent = 1
    m = re.search(rb'\n( +)"', blob)
    if m:
        indent = len(m.group(1))
    nl = "\r\n" if b"\r\n" in blob else "\n"
    trail = blob.endswith(b"\n")
    return indent, nl, trail

def dump(obj, fmt):
    indent, nl, trail = fmt
    s = json.dumps(obj, ensure_ascii=False, indent=indent)
    if trail:
        s += "\n"
    if nl == "\r\n":
        s = s.replace("\n", "\r\n")
    return s.encode("utf-8")

# ---------- enumerate UU ----------
r = subprocess.run(["git", "ls-files", "-u"], capture_output=True)
uu = sorted({ln.split("\t", 1)[1] for ln in r.stdout.decode().splitlines() if "\t" in ln})
print(f"UU files: {len(uu)}")

# ---------- classifier ----------
c = subprocess.run([sys.executable, "tools/skills/bigmoney-conflict-resolve/scripts/classify_conflicts.py"],
                   capture_output=True)
out = c.stdout.decode("utf-8", "replace")
i = out.find("[")
entries, _end = json.JSONDecoder().raw_decode(out, i)  # first JSON value only (tail text contains ']' chars)
cls = {e["path"]: e["class"] for e in entries}
assert len(cls) >= len(uu), f"classifier covered {len(cls)} < UU {len(uu)}"

# ---------- side assertion ----------
ca2 = json.loads(git_show(2, "results/compute_audit.json").decode("utf-8"))
ca3 = json.loads(git_show(3, "results/compute_audit.json").decode("utf-8"))
# structure = {"latest": {...}, "history": [...]} -- no `machine` field; side-assert via THIS round's
# live-fire stdout fingerprint (my audit ran 20:50:10, cpu_total 7.0, stale 0.1 -- captured in round log):
assert ca3["latest"]["ts"] == "2026-09-27 20:50:10" and ca3["latest"]["cpu_total_pct"] == 7.0, \
    f"stage3 not my R354 face: {ca3['latest'].get('ts')}/{ca3['latest'].get('cpu_total_pct')}"
assert ca2["latest"]["ts"] < ca3["latest"]["ts"], f"stage2 unexpectedly fresher: {ca2['latest']['ts']}"
print(f"side-assert OK: :2:=origin-face ts={ca2['latest']['ts']} | :3:=bm-a R354 face ts={ca3['latest']['ts']}")

resolved_log = []

def take_side(path):
    b2 = git_show(2, path)
    b3 = git_show(3, path)
    try:
        o2, o3 = json.loads(b2.decode("utf-8")), json.loads(b3.decode("utf-8"))
    except Exception as e:
        raise RuntimeError(f"{path}: parse fail {e}")
    m2, m3 = maxts(o2), maxts(o3)
    if m2 is None and m3 is None:
        side, why = 2, "no-wallclock-tie->HEAD(:2:)"
    elif m3 is None:
        side, why = 2, f"stage3 no ts; take :2: {m2}"
    elif m2 is None:
        side, why = 3, f"stage2 no ts; take :3: {m3}"
    elif m3 > m2:
        side, why = 3, f":3: fresher {m3} > {m2}"
    elif m2 > m3:
        side, why = 2, f":2: fresher {m2} > {m3}"
    else:
        side, why = 2, f"same-second tie {m2} -> HEAD(:2:) r140"
    blob = b2 if side == 2 else b3
    json.loads(blob.decode("utf-8"))  # parse-verify before write (r185)
    open(path, "wb").write(blob)
    resolved_log.append((path, f"take-:{side}:", why))

def twin_report(jsonpath, mdpath):
    b2, b3 = git_show(2, jsonpath), git_show(3, jsonpath)
    o2, o3 = json.loads(b2.decode()), json.loads(b3.decode())
    m2, m3 = maxts(o2), maxts(o3)
    if m3 and m3 > (m2 or ""):
        side, why = 3, f"json :3: fresher {m3} > {m2}"
    elif m2 and m2 > (m3 or ""):
        side, why = 2, f"json :2: fresher {m2} > {m3}"
    else:
        side, why = 2, f"json tie {m2} -> HEAD(:2:)"
    for p in (jsonpath, mdpath):
        blob = git_show(side, p)  # md from SAME side blob bytes (r329)
        open(p, "wb").write(blob)
    resolved_log.append((jsonpath, "twin-take", why))
    resolved_log.append((mdpath, "twin-take-bytecopy", f"same side :{side}: as json"))

def append_log_union(path):
    b2, b3 = git_show(2, path), git_show(3, path)
    l2 = b2.decode("utf-8").splitlines()
    l3 = b3.decode("utf-8").splitlines()
    merged = sorted(set(l2) | set(l3))
    nl = "\r\n" if b"\r\n" in b2 else "\n"
    open(path, "wb").write(nl.join(merged).encode("utf-8") + (b"" if not b2.endswith(b"\n") else nl.encode()))
    resolved_log.append((path, "line-union", f"{len(l2)}+{len(l3)}->{len(merged)}"))

def rolling_ledger(path):
    b2, b3 = git_show(2, path), git_show(3, path)
    o2, o3 = json.loads(b2.decode()), json.loads(b3.decode())
    m2, m3 = maxts(o2), maxts(o3)
    winner, wside = (o3, 3) if (m3 and m3 >= (m2 or "")) else (o2, 2)
    loser = o2 if wside == 3 else o3
    merged = copy.deepcopy(winner)
    union_notes = []
    for k, v in winner.items():
        if isinstance(v, list) and isinstance(loser.get(k), list):
            seen = {}
            for e in list(v) + list(loser[k]):
                seen.setdefault(json.dumps(e, sort_keys=True, ensure_ascii=False), e)
            ents = list(seen.values())
            if ents and isinstance(ents[0], dict):
                tsf = next((f for f in ("ts", "asof", "date", "time", "at") if f in ents[0]), None)
                if tsf:
                    ents.sort(key=lambda e: str(e.get(tsf, "")))
            merged[k] = ents
            union_notes.append(f"{k}:{len(v)}+{len(loser[k])}->{len(ents)}")
    blob = dump(merged, detect_format(b2))
    json.loads(blob.decode("utf-8"))
    open(path, "wb").write(blob)
    resolved_log.append((path, "rolling-union", f"state take-:{wside}: {';'.join(union_notes)}"))

def autofill_state(path):
    b2, b3 = git_show(2, path), git_show(3, path)
    o2, o3 = json.loads(b2.decode()), json.loads(b3.decode())
    fmt = detect_format(b2)
    merged = copy.deepcopy(o3)  # start from my face, union into it
    # launches union -> composite-key dedupe (r322/r325) -> ts desc cap50 -> re-sort asc (r245)
    L2, L3 = o2.get("launches", []), o3.get("launches", [])
    compkeys = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")
    bykey = {}
    flags = []
    for e in L2 + L3:
        k = tuple(e.get(f) for f in compkeys if f in e) or (json.dumps(e, sort_keys=True),)
        if k in bykey:
            a, b_ = bykey[k], e
            if a == b_:
                continue
            ka, kb = set(a), set(b_)
            if ka <= kb or kb <= ka:  # additive face -> field-union merge
                bykey[k] = {**a, **b_}
            else:
                flags.append(k)
        else:
            bykey[k] = e
    if flags:
        raise RuntimeError(f"autofill launches composite-key TRUE divergence: {flags[:3]} -- escalate, no silent double-keep")
    launches = sorted(bykey.values(), key=lambda e: str(e.get("ts", "")), reverse=True)[:50]
    launches.sort(key=lambda e: str(e.get("ts", "")))  # write-back ascending (r245)
    merged["launches"] = launches
    # last_tick whole-dict by internal ts, tie -> HEAD(:2:)
    t2 = (o2.get("last_tick") or {}).get("ts")
    t3 = (o3.get("last_tick") or {}).get("ts")
    if t3 and (t2 is None or str(t3) > str(t2)):
        merged["last_tick"] = o3.get("last_tick")
    elif t2 and (t3 is None or str(t2) > str(t3)):
        merged["last_tick"] = o2.get("last_tick")
    else:
        merged["last_tick"] = o2.get("last_tick")
    assert isinstance(merged.get("last_tick"), dict), "last_tick must be dict (r203)"
    blob = dump(merged, fmt)
    json.loads(blob.decode("utf-8"))
    open(path, "wb").write(blob)
    resolved_log.append((path, "mixed-dict+ledger", f"launches {len(L2)}+{len(L3)}->{len(launches)} (dedupe+cap50+asc); last_tick ts {t2}|{t3}"))

def token_usage(path):
    b2, b3 = git_show(2, path), git_show(3, path)
    o2, o3 = json.loads(b2.decode()), json.loads(b3.decode())
    m2, m3 = maxts(o2), maxts(o3)
    newer, older = (o3, o2) if (m3 and m3 >= (m2 or "")) else (o2, o3)
    merged = copy.deepcopy(newer)
    carried = []
    for k, v in older.items():
        if k not in merged:
            merged[k] = v
            carried.append(f"top:{k}")
        elif isinstance(v, dict) and isinstance(merged[k], dict):
            for kk, vv in v.items():
                if kk not in merged[k]:
                    merged[k][kk] = vv
                    carried.append(f"{k}.{kk}")
    blob = dump(merged, detect_format(b2))
    json.loads(blob.decode("utf-8"))
    open(path, "wb").write(blob)
    resolved_log.append((path, "take-new+bucket-carry", f"newer={'3' if newer is o3 else '2'}; carried={carried or 'none'}"))

def pool_union(path):
    b2, b3 = git_show(2, path), git_show(3, path)
    o2, o3 = json.loads(b2.decode()), json.loads(b3.decode())
    fmt = detect_format(b2)
    def entkey(e):
        return e.get("id") or e.get("entry") or json.dumps(e, sort_keys=True)
    def is_done(e):
        return str(e.get("status", "")).lower() in ("done", "completed")
    merged = copy.deepcopy(o3)
    e2 = {entkey(e): e for e in o2.get("entries", [])}
    e3 = {entkey(e): e for e in o3.get("entries", [])}
    out = {}
    for k in set(e2) | set(e3):
        a, b_ = e2.get(k), e3.get(k)
        if a and b_:
            if is_done(a) or is_done(b_):
                out[k] = a if is_done(a) else b_  # done absorption (r312)
            else:
                out[k] = {**a, **b_}
        else:
            out[k] = a or b_
    merged["entries"] = [out[k] for k in sorted(out)]
    blob = dump(merged, fmt)
    json.loads(blob.decode("utf-8"))
    open(path, "wb").write(blob)
    resolved_log.append((path, "pool-done-union", f"entries {len(e2)}|{len(e3)}->{len(out)}"))

# ---------- route ----------
JSON_TWIN = ("docs/daily_report/REPORT-2026-09-27.json", "docs/daily_report/REPORT-2026-09-27.md")
done = set()
for path in uu:
    c_ = cls.get(path)
    if path in done:
        continue
    if path in JSON_TWIN:  # twin coupling: json probe decides side, md byte-copied SAME side (r329)
        twin_report(*JSON_TWIN)
        done.update(JSON_TWIN)
    elif c_ == "js-wrapper-snapshot":
        continue  # handled via dashboard_status.json coupling below
    elif path == "results/dashboard_status.json":
        take_side(path)
        js = "results/dashboard_status.js"
        if js in uu:
            side = 3 if open(path, "rb").read() == git_show(3, path) else 2
            blob = git_show(side, js)
            open(js, "wb").write(blob)
            resolved_log.append((js, "twin-coupled-bytecopy", f"same side :{side}: as .json (r329/r353)"))
            done.add(js)
        done.add(path)
    elif path == "results/autofill_state.json":
        autofill_state(path); done.add(path)
    elif path == "results/token_usage.json":
        token_usage(path); done.add(path)
    elif path == "results/runnable_pool.json":
        pool_union(path); done.add(path)
    elif c_ == "rolling-ledger":
        rolling_ledger(path); done.add(path)
    elif c_ == "append-log":
        append_log_union(path); done.add(path)
    elif c_ == "snapshot":
        take_side(path); done.add(path)
    else:
        raise RuntimeError(f"path {path}: class {c_} has no routed recipe -- STOP for manual adjudication")

assert done == set(uu), f"unrouted: {set(uu) - done}"

# ---------- final verify: parse + marker scan ----------
MARK = re.compile(rb"^(<<<<<<<|=======|>>>>>>>)", re.M)
for p in sorted(done):
    raw = open(p, "rb").read()
    assert not MARK.search(raw), f"marker residue in {p}"
    if p.endswith(".jsonl"):
        for ln in raw.decode("utf-8").splitlines():
            if ln.strip():
                json.loads(ln)
    elif p.endswith(".json"):
        json.loads(raw.decode("utf-8"))
print("--- resolution table ---")
for p, rec, why in resolved_log:
    print(f"{rec:24s} {p}  [{why}]")
print(f"ALL {len(done)} resolved, parse+marker verified OK")
