# -*- coding: utf-8 -*-
"""r89 bm-c resolver: inherited r88-session rebase (started 15:57:56, died mid-pick 15:59:53,
rescued+continued 16:08 by r89 S0 as b26e7b0d) -- push rejected (origin +1 bm-a r334) -> stash tick
16:10:02 keepalive -> pull --rebase retry onto 14e18c3b replaying r87 pair + r88'.
Same canon recipes as r88 resolve/resolve2 (r327 same-window law) with two r89 deltas:
- CODELY: mine_new filtered by origin-archive (:2:) text -- origin 18th-batch (f3a01cb5 9608->7567B)
  stub-landing must NOT be regressed by re-appending my :3: pre-archival full texts; those lines are
  zero-loss-accounted via oa_text instead of re-entering CODELY.
- pointer-stub accounting: a dropped :3: line whose header-prefix (- [.. rN machine] 坑律) matches a
  full-text line in either archive side = accounted (stub->full archival linkage).
Archive: prefix-verified suffix-concat coexist (probe r89: both prefixes hold, 十七批 x2, r328 dup=2
tolerated per r88 precedent) with line-union fallback if prefix shape breaks at later picks.
Generic handlers (ledgers/autofill/twins/paper/x2/js/snapshots) carried verbatim for picks 2-3.
"""
import io, json, re, subprocess

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

uu = [l.decode().strip() for l in subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
     capture_output=True).stdout.splitlines() if l.strip()]
print(f"UU x{len(uu)}")
resolved = set()
verdicts = []

# ---------------------------------------------------------------- 1. archive (suffix-concat coexist, line-union fallback)
p = "research/memory-archive/202609.md"
if p in uu:
    b, o, t = blobs(p)
    bd, od, td = b.decode("utf-8"), o.decode("utf-8"), t.decode("utf-8")
    if od.startswith(bd) and td.startswith(bd):
        my_suf = td[len(bd):]
        final = od + my_suf  # both sections coexist verbatim, zero overwrite
        mode = "suffix-concat coexist"
        n17 = final.count("十七批")
        assert "r330 bm-b] 坑律：**移植" in final, "r330 full text missing from coexist union"
        assert n17 >= 2, f"expect both 17th sections, count={n17}"
    else:
        # fallback: line-union, origin body + mine-only lines appended (dup-tolerant zero-loss)
        ol_l, tl_l = [x for x in od.splitlines()], [x for x in td.splitlines()]
        seen = set(ol_l)
        add = [x for x in tl_l if x not in seen]
        final = od + (nb_of(o).decode("utf-8") if od.endswith("\n") or od.endswith("\r\n") else "\n") + nb_of(o).decode("utf-8").join(add) + (nb_of(o).decode("utf-8") if add else "")
        mode = f"line-union fallback (+{len(add)} mine-only)"
        miss_t = [x for x in tl_l if x.strip() and x not in final]
        assert not miss_t, f"archive line-union lost mine lines: {[x[:60] for x in miss_t[:3]]}"
    nb = nb_of(b)
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(final)
    resolved.add(p)
    verdicts.append((p, f"{mode}: final={len(final.encode('utf-8'))}B 十七批={final.count('十七批')} r328dup={final.count('r328 bm-a] 坑律：**腾讯')} (tolerated per r88 precedent)"))
    print(f"  {p}: {mode} final={len(final.encode('utf-8'))}B")

# ---------------------------------------------------------------- 2. CODELY entry-union (r89 deltas: oa-filter + pointer accounting)
p = "CODELY.md"
if p in uu:
    b, o, t = blobs(p)
    bl, ol, tl = b.decode("utf-8").splitlines(), o.decode("utf-8").splitlines(), t.decode("utf-8").splitlines()
    bs, os_, ms = set(bl), set(ol), set(tl)
    oa_text = blobs("research/memory-archive/202609.md")[1].decode("utf-8")
    ta_text = blobs("research/memory-archive/202609.md")[2].decode("utf-8")
    # r89 delta: drop my lines origin has ALREADY archived (18th-batch stub-landing intact)
    mine_new = [l for l in tl if l not in bs and l not in os_ and l not in oa_text]
    orig_new = [l for l in ol if l not in bs and l not in ms]
    for l in mine_new:
        assert l.startswith("- [") and "坑律" in l, f"unexpected mine_new: {l[:80]}"
    assert mine_new, "no new pitlaw entry from :3:"
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
        if l.startswith("- [2026-09-27 14:5x r330 bm-b] 坑律：**移植"):
            # full-text form only: my :3: archived it (probe: full in ta_text); pointer form
            # (（十七批外迁·指针）) is origin's 18th-batch landing discipline -- kept in final.
            assert "r330 bm-b] 坑律：**移植" in ta_text, "r330 full not in my archive section"
            continue  # my :3: archival intent; full text preserved in coexist archive
        if drop_canon is not None and l == drop_canon:
            continue  # strict-subset canon dedup, superset retained
        final_l.append(l)
    final_l = final_l + mine_new
    fs = set(final_l)
    miss3 = [l for l in tl if l.strip() and l not in fs]
    accounted = []
    still = []
    for l in miss3:
        if l in oa_text or l in ta_text:
            accounted.append(l)
        elif l.startswith("- 坑律正典全量归档") and any(l2 != l and l2.startswith(l) for l2 in final_l):
            accounted.append(l)  # canon strict-subset drop
        else:
            # r89 delta: pointer-stub whose full text is archived (header-prefix match)
            hdr = (l.split("坑律")[0] + "坑律") if "坑律" in l else None
            if hdr and any(al.startswith(hdr) for al in (oa_text + "\n" + ta_text).splitlines()):
                accounted.append(l)
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
    assert size < 10240, f"CODELY {size}B over 10KB"
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(final)
    resolved.add(p)
    verdicts.append((p, f"entry-union r89: origin skeleton + mine x{len(mine_new)} (oa-filtered); :3: zero-loss accounted x{len(accounted)}; canon_drop={'Y' if drop_canon else 'N'}; size={size}B"))
    print(f"  {p}: size={size}B mine+{len(mine_new)} accounted={len(accounted)} canon_drop={'Y' if drop_canon else 'N'}")

# ---------------------------------------------------------------- rolling ledgers
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
        if keyf:
            un.sort(key=lambda r: r.get(keyf, ""))
        out[lk] = un
        print(f"  {path}[{lk}]: face-key={keyf} |origin|={len(lo)} |mine|={len(lt)} -> union={len(un)}")
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
    verdicts.append((path, f"rolling-ledger union + snapshot take-{'origin(:2)' if pick is jo else 'mine(:3)'} ({so} vs {st})"))
    print(f"  {path}: snapshot={'origin' if pick is jo else 'mine'}")

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
PAPER = [pp for pp in uu if pp.startswith("results/paper/")]
EXPORT = [pp for pp in uu if pp.startswith("results/paper_export/")]
if PAPER:
    side_ts = {"origin": "", "mine": ""}
    for pp in PAPER:
        _, o2, t2 = blobs(pp)
        side_ts["origin"] = max(side_ts["origin"], deep_ts(json.loads(o2)))
        side_ts["mine"] = max(side_ts["mine"], deep_ts(json.loads(t2)))
    win = "origin" if (side_ts["origin"], "") >= (side_ts["mine"], "") else "mine"
    for pp in PAPER + EXPORT:
        _, o2, t2 = blobs(pp)
        with io.open(pp, "wb") as f:
            f.write(o2 if win == "origin" else t2)
        json.loads(io.open(pp, encoding="utf-8").read())
        resolved.add(pp)
    verdicts.append(("paper family + exports", f"coupled-side {win} x{len(PAPER)+len(EXPORT)} ({side_ts['origin']} vs {side_ts['mine']})"))
    print(f"  paper x{len(PAPER)} + export x{len(EXPORT)}: coupled side={win}")

# ---------------------------------------------------------------- twins
pj, pm = "docs/daily_report/REPORT-2026-09-27.json", "docs/daily_report/REPORT-2026-09-27.md"
if pj in uu:
    _, o2, t2 = blobs(pj)
    so, st = deep_ts(json.loads(o2)), deep_ts(json.loads(t2))
    win = "origin" if (so, "") >= (st, "") else "mine"
    for pp in (pj, pm):
        _, o2, t2 = blobs(pp)
        with io.open(pp, "wb") as f:
            f.write(o2 if win == "origin" else t2)
    json.loads(io.open(pj, encoding="utf-8").read())
    resolved.add(pj); resolved.add(pm)
    verdicts.append((pj + " & .md", f"coupled-side {win} ({so} vs {st})"))
    print(f"  twins: side={win}")

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
    verdicts.append((p, f"line union base={len(bl_)} +origin {n_o} +mine {n_t} -> {len(out_l)}"))
    print(f"  {p}: {len(bl_)}+{n_o}+{n_t}->{len(out_l)}")

# ---------------------------------------------------------------- snapshots fallback (deep-ts take-new)
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
    verdicts.append((path, f"take-new {'origin(:2)' if data is jo2 else 'mine(:3)'} ({so} vs {st})"))
    print(f"  {path}: take_new {'origin' if data is jo2 else 'mine'} ({so} vs {st})")

for pp in uu:
    if pp not in resolved and pp.endswith(".json"):
        take_new_json(pp)

missing = [pp for pp in uu if pp not in resolved]
assert not missing, f"UNRESOLVED: {missing}"
print("\nALL", len(uu), "UU RESOLVED (r89):")
for pp, v in verdicts:
    print("  -", pp, "::", v)
print("RESOLVE-R89B-OK")
