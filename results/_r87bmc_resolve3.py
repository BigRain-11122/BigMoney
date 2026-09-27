# -*- coding: utf-8 -*-
"""r87 bm-c resolve3: second push-collision batch (pull --rebase onto origin+3, replaying
b137e5bd r86'). Same recipes as resolve1/2 (r327 law: same-window second batch = same recipe,
no method change). Dynamic UU set; rolling-union uses per-face key probe + full-row dedup
(resolve2 fix, r319 law). Roles: :2=ours=origin new base, :3=theirs=my r86' replay.
Also read-only sanity check of git-auto-merged CODELY.md + archive (no markers / size).
"""
import io, json, re, subprocess, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)

def git(*a):
    return subprocess.run(["git", *a], capture_output=True).stdout

def blobs(path):
    return git("show", f":1:{path}"), git("show", f":2:{path}"), git("show", f":3:{path}")

def deep_ts(obj):
    best = [""]
    KEYS = ("ts", "generated", "generated_at", "updated", "updated_at", "asof", "last_run", "written_at")
    def scan(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in KEYS and isinstance(v, str) and len(v) >= 16:
                    nv = v.replace(" ", "T")[:19]
                    if nv > best[0]:
                        best[0] = nv
                scan(v)
        elif isinstance(x, list):
            for v in x:
                scan(v)
    scan(obj)
    return best[0]

def nb_of(b):
    return b"\r\n" if b"\r\n" in b else b"\n"

# read-only sanity on auto-merged faces (line-anchored: prose may quote marker substrings)
import re as _re
for p in ("CODELY.md", "research/memory-archive/202609.md"):
    txt = io.open(p, encoding="utf-8").read()
    bad = [l for l in txt.splitlines() if _re.match(r"^(<{7}|>{7}|={7})\s", l)]
    assert not bad, f"{p} auto-merge left conflict markers: {bad[:2]}"
    print(f"  [auto-merged check] {p}: size={len(txt.encode('utf-8'))}B markers=none", end="")
    if p == "CODELY.md":
        assert len(txt.encode("utf-8")) < 10240, "CODELY over 10KB after auto-merge"
        assert "r86 bm-c" in txt and "十六批" in txt
        print(" r86-pitlaw+16th-batch present <10KB")

uu = [l.decode().strip() for l in subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
     capture_output=True).stdout.splitlines() if l.strip()]
print(f"\nUU x{len(uu)}")
PAPER = [p for p in uu if p.startswith("results/paper/")]
EXPORT = [p for p in uu if p.startswith("results/paper_export/")]
resolved = set()
verdicts = []

# ---------------------------------------------------------------- autofill composite-union
p = "results/autofill_state.json"
if p in uu:
    b, o, t = blobs(p)
    jo, jt = json.loads(o), json.loads(t)
    KEYF = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")
    def key(r):
        return tuple(r.get(k) for k in KEYF)
    lo, lt = jo.get("launches", []), jt.get("launches", [])
    seen, union, flags = {}, [], []
    for r in lo + lt:
        k = key(r)
        if k in seen:
            old = seen[k]
            merged = dict(old)
            diverged = []
            for fk, fv in r.items():
                if fk in merged and merged[fk] not in (None, "", fv) and fv not in (None, ""):
                    diverged.append(fk)
                if fv is not None:
                    merged[fk] = fv
            if diverged:
                flags.append((k, diverged))
            seen[k] = merged
            i = [i for i, x in enumerate(union) if key(x) == k][0]
            union[i] = merged
        else:
            seen[k] = r
            union.append(r)
    n_union = len(union)
    union.sort(key=lambda r: r.get("ts", ""), reverse=True)
    union = union[:50]
    union.sort(key=lambda r: r.get("ts", ""))
    tlo, tlt = (jo.get("last_tick") or {}), (jt.get("last_tick") or {})
    last_tick = tlo if (tlo.get("ts", ""), "") >= (tlt.get("ts", ""), "") else tlt
    assert isinstance(last_tick, dict)
    m = dict(jo)
    m["launches"] = union
    m["last_tick"] = last_tick
    nb = nb_of(b)
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(m, ensure_ascii=False, indent=1) + ("\r\n" if nb == b"\r\n" else "\n"))
    back = json.loads(io.open(p, encoding="utf-8").read())
    assert isinstance(back["last_tick"], dict)
    resolved.add(p)
    verdicts.append((p, f"composite-union {len(lo)}|{len(lt)}->{n_union} cap{len(back['launches'])} asc; last_tick {'HEAD(:2)' if last_tick is tlo else 'mine(:3)'}; flags={flags if flags else 'none'}"))
    print(f"  {p}: {len(lo)}|{len(lt)}->{n_union} last_tick={'HEAD' if last_tick is tlo else 'mine'}")

# ---------------------------------------------------------------- rolling ledgers (per-face key + full-row dedup)
def rolling_union(path, ledger_keys):
    if path not in uu:
        return
    b, o, t = blobs(path)
    jo, jt = json.loads(o), json.loads(t)
    out = dict(jo)
    for lk in ledger_keys:
        lo, lt = jo.get(lk, []), jt.get(lk, [])
        if not isinstance(lo, list) or not isinstance(lt, list):
            continue
        keyf = next((k for k in ("ts", "asof", "date", "day") if lo and k in lo[0]), None)
        seen, un = set(), []
        for r in lo + lt:
            rk = json.dumps(r, ensure_ascii=False, sort_keys=True)
            if rk not in seen:
                seen.add(rk)
                un.append(r)
        coll = []
        if keyf:
            byk = {}
            for r in un:
                byk.setdefault(r.get(keyf), []).append(r)
            for k, rs in byk.items():
                if len(rs) > 1:
                    coll.append((keyf, k, len(rs)))
            un.sort(key=lambda r: r.get(keyf, ""))
        out[lk] = un
        print(f"  {path}[{lk}]: face-key={keyf} |ours|={len(lo)} |mine|={len(lt)} -> full-row-union={len(un)} coll={coll if coll else 'none'}")
    so, st = deep_ts(jo), deep_ts(jt)
    pick = jo if (so, "") >= (st, "") else jt
    for kk in set(jo) | set(jt):
        if kk not in ledger_keys:
            out[kk] = pick.get(kk, jo.get(kk, jt.get(kk)))
    nb = nb_of(b)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1) + ("\r\n" if nb == b"\r\n" else "\n"))
    json.loads(io.open(path, encoding="utf-8").read())
    resolved.add(path)
    verdicts.append((path, f"rolling-ledger full-row-union + snapshot take-{'HEAD(:2)' if pick is jo else 'mine(:3)'} ({so} vs {st})"))
    print(f"  {path}: snapshot={'HEAD' if pick is jo else 'mine'} ({so} vs {st})")

rolling_union("results/compute_audit.json", ("history",))
rolling_union("results/regime_state.json", ("history", "transitions"))

# ---------------------------------------------------------------- js wrapper
p = "results/dashboard_status.js"
if p in uu:
    b, o, t = blobs(p)
    mo = re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$", o.decode("utf-8"), re.S)
    mt = re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$", t.decode("utf-8"), re.S)
    so, st = deep_ts(json.loads(mo.group(1))), deep_ts(json.loads(mt.group(1)))
    data = o if (so, "") >= (st, "") else t
    with io.open(p, "wb") as f:
        f.write(data)
    resolved.add(p)
    verdicts.append((p, f"js-wrapper whole-bytes {'HEAD(:2)' if data is o else 'mine(:3)'} ({so} vs {st})"))
    print(f"  {p}: side={'HEAD' if data is o else 'mine'}")

# ---------------------------------------------------------------- x2 jsonl
p = "results/x2_watch_log.jsonl"
if p in uu:
    b, o, t = blobs(p)
    bl_, ol_, tl_ = b.decode("utf-8").splitlines(), o.decode("utf-8").splitlines(), t.decode("utf-8").splitlines()
    seen, out_l = set(bl_), list(bl_)
    n_o = n_t = 0
    for l in ol_:
        if l and l not in seen:
            seen.add(l); out_l.append(l); n_o += 1
    for l in tl_:
        if l and l not in seen:
            seen.add(l); out_l.append(l); n_t += 1
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out_l) + ("\n" if out_l else ""))
    resolved.add(p)
    verdicts.append((p, f"line union base={len(bl_)} +ours {n_o} +mine {n_t} -> {len(out_l)}"))
    print(f"  {p}: {len(bl_)}+{n_o}+{n_t}->{len(out_l)}")

# ---------------------------------------------------------------- paper coupled side
if PAPER:
    side_ts = {"ours": "", "mine": ""}
    for pp in PAPER:
        _, o2, t2 = blobs(pp)
        side_ts["ours"] = max(side_ts["ours"], deep_ts(json.loads(o2)))
        side_ts["mine"] = max(side_ts["mine"], deep_ts(json.loads(t2)))
    win = "ours" if (side_ts["ours"], "") >= (side_ts["mine"], "") else "mine"
    for pp in PAPER + EXPORT:
        _, o2, t2 = blobs(pp)
        with io.open(pp, "wb") as f:
            f.write(o2 if win == "ours" else t2)
        json.loads(io.open(pp, encoding="utf-8").read())
        resolved.add(pp)
    verdicts.append(("paper family + exports", f"coupled-side {win} x{len(PAPER)+len(EXPORT)} ({side_ts['ours']} vs {side_ts['mine']})"))
    print(f"  paper x{len(PAPER)} + export x{len(EXPORT)}: coupled side={win}")

# ---------------------------------------------------------------- twins
pj, pm = "docs/daily_report/REPORT-2026-09-27.json", "docs/daily_report/REPORT-2026-09-27.md"
if pj in uu:
    _, o2, t2 = blobs(pj)
    so, st = deep_ts(json.loads(o2)), deep_ts(json.loads(t2))
    win = "ours" if (so, "") >= (st, "") else "mine"
    for pp in (pj, pm):
        _, o2, t2 = blobs(pp)
        with io.open(pp, "wb") as f:
            f.write(o2 if win == "ours" else t2)
    json.loads(io.open(pj, encoding="utf-8").read())
    resolved.add(pj); resolved.add(pm)
    verdicts.append((pj + " & .md", f"coupled-side {win} ({so} vs {st})"))
    print(f"  twins: side={win}")

# ---------------------------------------------------------------- snapshots
def take_new_json(path):
    b, o2, t2 = blobs(path)
    jo2, jt2 = json.loads(o2), json.loads(t2)
    so, st = deep_ts(jo2), deep_ts(jt2)
    data = jo2 if (so, "") >= (st, "") else jt2
    nb = nb_of(b)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=1) + ("\r\n" if nb == b"\r\n" else "\n"))
    json.loads(io.open(path, encoding="utf-8").read())
    resolved.add(path)
    verdicts.append((path, f"take-new {'HEAD(:2)' if data is jo2 else 'mine(:3)'} ({so} vs {st})"))
    print(f"  {path}: take_new {'HEAD' if data is jo2 else 'mine'} ({so} vs {st})")

for pp in uu:
    if pp not in resolved and pp.endswith(".json") and not pp.startswith(("results/paper/", "results/paper_export/", "docs/daily_report/")):
        take_new_json(pp)

missing = [pp for pp in uu if pp not in resolved]
assert not missing, f"UNRESOLVED: {missing}"
print("\nALL", len(uu), "UU RESOLVED (batch-2):")
for pp, v in verdicts:
    print("  -", pp, "::", v)
print("RESOLVE3-OK")
