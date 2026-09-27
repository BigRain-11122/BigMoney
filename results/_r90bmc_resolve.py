# -*- coding: utf-8 -*-
"""r90 bm-c resolver: S0 fold rebase (6 local commits onto origin/main+9, inherited
from r89 fallback-branch fold plan). Same-recipe canon per r327 law -- recipes are the
r87-resolve3/r89 generic unions, de-special-cased for multi-pick reuse:
- CODELY: entry-union, origin-skeleton + mine_new (oa-filter: drop lines origin already
  archived) + pointer-stub accounting (r89 fix: full-text form only) + canon strict-subset
  dedup + 10KB hard line.
- archive 202609.md: suffix-concat coexist when both extend base, line-union fallback.
- autofill_state: composite-union (ts,machine,pid,runner,entry,shard key), cap50 asc,
  last_tick by ts.
- compute_audit/regime_state: rolling full-row-dedup union (r87 lesson: asof-key
  false-union -> full-row dedup) + snapshot take-new by deep_ts.
- token_usage/update_status/dashboard_status/futures/heat/lhb/fundamental/scorecards:
  take-new by deep_ts + mine-unique-key carry-over (zero-loss guard).
- paper family/export twins/daily twins/x2 jsonl/js wrapper: r87-resolve3 recipes.
Runs per pick; UU set dynamic; asserts zero-loss both sides. Areas = encode bytes (r89 canon).
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
    KEYS = ("ts", "generated", "generated_at", "updated", "updated_at", "asof",
            "last_run", "written_at", "now", "last_attempt", "snapshot_at", "run_at")
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

uu = [l.decode().strip() for l in subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
     capture_output=True).stdout.splitlines() if l.strip()]
print(f"UU x{len(uu)}")
PAPER = [p for p in uu if p.startswith("results/paper/")]
EXPORT = [p for p in uu if p.startswith("results/paper_export/")]
resolved = set()
verdicts = []

# read-only sanity on auto-merged CODELY/archive (line-anchored marker check)
for p in ("CODELY.md", "research/memory-archive/202609.md"):
    if p not in uu and os.path.exists(p):
        txt = io.open(p, encoding="utf-8").read()
        bad = [l for l in txt.splitlines() if re.match(r"^(<{7}|>{7}|={7})\s", l)]
        assert not bad, f"{p} auto-merge left markers: {bad[:2]}"
        print(f"  [auto-merged check] {p}: {len(txt.encode('utf-8'))}B markers=none")

# ---------------------------------------------------------------- 1. archive (suffix-concat coexist, line-union fallback)
p = "research/memory-archive/202609.md"
if p in uu:
    b, o, t = blobs(p)
    bd, od, td = b.decode("utf-8"), o.decode("utf-8"), t.decode("utf-8")
    if od.startswith(bd) and td.startswith(bd):
        my_suf = td[len(bd):]
        final = od + my_suf
        mode = "suffix-concat coexist"
        assert final.startswith(od) and final.endswith(my_suf), "coexist verbatim check"
    else:
        nl_o = nb_of(o).decode("utf-8")
        ol_l, tl_l = od.splitlines(), td.splitlines()
        seen = set(ol_l)
        add = [x for x in tl_l if x not in seen]
        final = od + (nl_o if not od.endswith(("\n", "\r\n")) else "") + nl_o.join(add) + (nl_o if add else "")
        mode = f"line-union fallback (+{len(add)} mine-only)"
        miss_t = [x for x in tl_l if x.strip() and x not in final]
        assert not miss_t, f"archive line-union lost mine lines: {[x[:60] for x in miss_t[:3]]}"
    nb = nb_of(b)
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(final)
    resolved.add(p)
    size = len(final.encode("utf-8"))
    verdicts.append((p, f"{mode}: final={size}B"))
    print(f"  {p}: {mode} final={size}B")

# ---------------------------------------------------------------- 2. CODELY entry-union (r89 generic: oa-filter + pointer accounting)
p = "CODELY.md"
if p in uu:
    b, o, t = blobs(p)
    bl, ol, tl = b.decode("utf-8").splitlines(), o.decode("utf-8").splitlines(), t.decode("utf-8").splitlines()
    bs, os_, ms = set(bl), set(ol), set(tl)
    # r90 fix: auto-merged archive face has NO :2:/:3: stages (result lands at stage 0) --
    # empty blob = fall back to worktree merged file (contains both sides' content, so
    # accounting against it stays zero-loss valid).
    _ab = blobs("research/memory-archive/202609.md")
    _oa_b, _ta_b = _ab[1], _ab[2]
    if _oa_b.strip():
        oa_text = _oa_b.decode("utf-8")
        ta_text = _ta_b.decode("utf-8") if _ta_b.strip() else oa_text
    else:
        oa_text = ta_text = io.open("research/memory-archive/202609.md", encoding="utf-8").read()
    mine_new = [l for l in tl if l not in bs and l not in os_ and l not in oa_text]
    orig_new = [l for l in ol if l not in bs and l not in ms]
    # r90 delta: accept pitlaw entries AND batch-exile navigation pointer family
    # (r89 pointer-retention discipline); anything else = garbage guard.
    def _ok_mine(l):
        if l.startswith("- [") and "坑律" in l:
            return True  # pitlaw entry family
        if l.startswith("- 十") and "批外迁" in l:
            return True  # batch-exile navigation pointer family (r89 retention discipline)
        return False
    for l in mine_new:
        assert _ok_mine(l), f"unexpected mine_new: {l[:80]}"
    print(f"  CODELY: mine_new x{len(mine_new)} orig_new x{len(orig_new)}")
    canons = [l for l in ol if l.startswith("- 坑律正典全量归档")]
    drop_canon = None
    if len(canons) == 2:
        A, B = canons
        if B.startswith(A) and B != A:
            drop_canon = A
        elif A.startswith(B) and A != B:
            drop_canon = B
    final_l = []
    for l in ol:
        if drop_canon is not None and l == drop_canon:
            continue  # strict-subset canon dedup, superset retained
        final_l.append(l)
    # r90 pick-5 delta: pointer/full swap union -- my pointer line whose entry-header
    # matches an existing ol FULL-text line = my archival intent applied to the union
    # side (drop full, verbatim must be in ta_text; <=10KB hard line requires it).
    # My pointer whose entry-header matches an existing ol POINTER line = duplicate
    # (origin archived the same entry) -> drop mine, origin's pointer retained.
    kept_mine, swapped_fulls, dup_ptrs = [], [], []
    for l in mine_new:
        hdr = (l.split("坑律")[0] + "坑律") if "坑律" in l else None
        if hdr and "十九批外迁·指针" in l:
            ol_ptr = [x for x in final_l if x.startswith(hdr + "（")]
            if ol_ptr:
                dup_ptrs.append(l)
                continue
            ol_full = [x for x in final_l if x.startswith(hdr + "：**")]
            if ol_full:
                for x in ol_full:
                    assert x in ta_text, f"swap-archival full not verbatim in my archive: {x[:60]}"
                    final_l = [y for y in final_l if y != x]
                    swapped_fulls.append(x)
                kept_mine.append(l)
                continue
        kept_mine.append(l)
    mine_new = kept_mine
    if swapped_fulls or dup_ptrs:
        print(f"  CODELY swap-union: archived-fulls x{len(swapped_fulls)} -> pointers; dup-pointers dropped x{len(dup_ptrs)} (origin's retained)")
    final_l = final_l + mine_new
    fs = set(final_l)
    miss3 = [l for l in tl if l.strip() and l not in fs]
    accounted, still = [], []
    for l in miss3:
        if l in oa_text or l in ta_text:
            accounted.append(l)  # my archival intent, full text preserved in archive
        elif l.startswith("- 坑律正典全量归档") and any(l2 != l and l2.startswith(l) for l2 in final_l):
            accounted.append(l)
        else:
            hdr = (l.split("坑律")[0] + "坑律") if "坑律" in l else None
            if hdr and any(al.startswith(hdr) for al in (oa_text + "\n" + ta_text).splitlines()):
                accounted.append(l)  # pointer-stub -> archived full text linkage
            else:
                still.append(l)
    assert not still, f":3: lines lost unaccounted: {[x[:70] for x in still]}"
    miss2n = [l for l in orig_new if l not in fs]
    assert not miss2n, f":2: new lines lost: {[x[:70] for x in miss2n]}"
    bad = [l for l in final_l if re.match(r"^(<{7}|>{7}|={7})\s", l)]
    assert not bad, f"markers leaked: {bad[:2]}"
    nl = nb_of(b).decode("utf-8")
    final = nl.join(final_l) + nl
    size = len(final.encode("utf-8"))
    assert size < 10240, f"CODELY {size}B over 10KB hard line"
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(final)
    resolved.add(p)
    verdicts.append((p, f"entry-union r90: origin skeleton + mine x{len(mine_new)} (oa-filtered); :3: accounted x{len(accounted)}; canon_drop={'Y' if drop_canon else 'N'}; size={size}B"))
    print(f"  {p}: size={size}B mine+{len(mine_new)} accounted={len(accounted)} canon_drop={'Y' if drop_canon else 'N'}")

# ---------------------------------------------------------------- rolling ledgers (full-row dedup, r87 lesson)
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
        print(f"  {path}[{lk}]: face-key={keyf} |ours|={len(lo)} |mine|={len(lt)} -> union={len(un)} coll={coll if coll else 'none'}")
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
    verdicts.append((path, f"rolling full-row-union + snapshot take-{'origin(:2)' if pick is jo else 'mine(:3)'} ({so} vs {st})"))
    print(f"  {path}: snapshot={'origin' if pick is jo else 'mine'} ({so} vs {st})")

rolling_union("results/compute_audit.json", ("history",))
rolling_union("results/regime_state.json", ("history", "transitions"))

# ---------------------------------------------------------------- autofill composite-union (r322/r83 canon)
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
    verdicts.append((p, f"composite-union {len(lo)}|{len(lt)}->{n_union} cap{len(back['launches'])} asc; last_tick {'origin(:2)' if last_tick is tlo else 'mine(:3)'}; flags={flags if flags else 'none'}"))
    print(f"  {p}: {len(lo)}|{len(lt)}->{n_union} last_tick={'origin' if last_tick is tlo else 'mine'}")

# ---------------------------------------------------------------- x2 jsonl line-union
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
    verdicts.append((p, f"js-wrapper whole-bytes {'origin(:2)' if data is o else 'mine(:3)'} ({so} vs {st})"))
    print(f"  {p}: side={'origin' if data is o else 'mine'}")

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

# ---------------------------------------------------------------- daily twins
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

# ---------------------------------------------------------------- snapshots: take-new + mine-unique-key carry-over
def take_new_json(path):
    b, o2, t2 = blobs(path)
    jo2, jt2 = json.loads(o2), json.loads(t2)
    so, st = deep_ts(jo2), deep_ts(jt2)
    data = jo2 if (so, "") >= (st, "") else jt2
    side = "origin(:2)" if data is jo2 else "mine(:3)"
    carried = []
    if isinstance(jo2, dict) and isinstance(jt2, dict):
        out = dict(data)
        for k in jt2:
            if k not in out:
                out[k] = jt2[k]  # mine-unique keys carried, zero-loss guard
                carried.append(k)
        data = out
    nb = nb_of(b)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=1) + ("\r\n" if nb == b"\r\n" else "\n"))
    json.loads(io.open(path, encoding="utf-8").read())
    resolved.add(path)
    verdicts.append((path, f"take-new {side} ({so} vs {st})" + (f"; carried mine-keys {carried}" if carried else "")))
    print(f"  {path}: take_new {side} ({so} vs {st})" + (f" carried={carried}" if carried else ""))

for pp in uu:
    if pp not in resolved and pp.endswith(".json") and not pp.startswith(("results/paper/", "results/paper_export/", "docs/daily_report/")):
        take_new_json(pp)

missing = [pp for pp in uu if pp not in resolved]
assert not missing, f"UNRESOLVED: {missing}"
print("\nALL", len(uu), "UU RESOLVED (r90 pick):")
for pp, v in verdicts:
    print("  -", pp, "::", v)
print("RESOLVE-R90-OK")
