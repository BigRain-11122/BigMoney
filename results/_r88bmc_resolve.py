# -*- coding: utf-8 -*-
"""r88 bm-c resolve (stage-1): pull --rebase onto origin+2 (bm-a r332 d3fb2b84 + r333 27138221),
replaying r87 pair 7405352c. Same recipes as r87 resolve3 (r327 law: same-window batch = same
recipe, no method change) + CODELY.md entry-union block (r86-rescue resolve1 recipe, this batch
CODELY is UU not auto-merged). Roles: :2=ours=origin new base, :3=theirs=my r87 replay, :1=base.
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
PAPER = [p for p in uu if p.startswith("results/paper/")]
EXPORT = [p for p in uu if p.startswith("results/paper_export/")]
resolved = set()
verdicts = []

# ---------------------------------------------------------------- 1. CODELY.md entry-union (r86-rescue recipe)
p = "CODELY.md"
if p in uu:
    b, o, t = blobs(p)
    bl, ol, tl = b.decode("utf-8").splitlines(), o.decode("utf-8").splitlines(), t.decode("utf-8").splitlines()
    bs, os_, ms = set(bl), set(ol), set(tl)
    mine_new = [l for l in tl if l not in bs and l not in os_]
    orig_new = [l for l in ol if l not in bs and l not in ms]
    # every mine_new/orig_new line must be a legitimate appended entry/idx line
    for l in mine_new + orig_new:
        assert (l.startswith("- [") and "坑律" in l) or l.startswith("- 十"), f"unexpected new line: {l[:80]}"
    my_pit = [l for l in mine_new if l.startswith("- [") and "坑律" in l]
    my_idx = [l for l in mine_new if l.startswith("- 十")]
    assert my_pit, "my pitlaw entry not found in mine_new"
    final_l = list(ol)  # origin skeleton keeps bm-a r332 entry position
    for il in my_idx:
        at = max([i for i, l in enumerate(final_l) if "批外迁" in l], default=len(final_l) - 1) + 1
        final_l = final_l[:at] + [il] + final_l[at:]
    final_l = final_l + my_pit
    # bidirectional zero-loss verify (r331 canon): every :3: line and every :2:-new line in final
    fs = set(final_l)
    miss3 = [l for l in tl if l.strip() and l not in fs]
    miss2n = [l for l in orig_new if l not in fs]
    assert not miss3, f":3: lines lost: {[x[:60] for x in miss3]}"
    assert not miss2n, f":2: new lines lost: {[x[:60] for x in miss2n]}"
    nl = nb_of(b).decode("utf-8")
    final = nl.join(final_l) + nl
    # line-anchored marker check (r87 pitlaw: prose may quote marker substrings)
    bad = [l for l in final_l if re.match(r"^(<{7}|>{7}|={7})\s", l)]
    assert not bad, f"markers leaked: {bad[:2]}"
    size = len(final.encode("utf-8"))
    moved = []
    if size >= 10240:
        # in-window 17th-batch archival (this round's own surgery recipe, proven r88):
        # move the two oldest standalone pitlaw entries (r328 bm-a + r330 bm-b) to the archive
        # suffix-concat + strict-subset canon-pointer-line dedup. Zero loss at THIS commit.
        # NOTE: archive suffix bytes must EXACTLY equal my r88 commit's suffix so stage-3
        # replay merges as identical-change-both-sides (no duplicate section).
        canons = [l for l in final_l if l.startswith("- 坑律正典全量归档")]
        drop_canon = None
        if len(canons) == 2:
            A, B = canons
            if B.startswith(A) and B != A:
                drop_canon = A
            elif A.startswith(B) and A != B:
                drop_canon = B
        keep_l = []
        for l in final_l:
            if l.startswith("- [2026-09-27 14:5x r328 bm-a] 坑律"):
                moved.append(l); continue
            if l.startswith("- [2026-09-27 14:5x r330 bm-b] 坑律"):
                moved.append(l); continue
            if drop_canon is not None and l == drop_canon:
                continue  # drop strict-subset duplicate canon pointer line
            keep_l.append(l)
        assert len(moved) == 2, f"archival move count {len(moved)} != 2"
        final_l = keep_l
        final = nl.join(final_l) + nl
        size = len(final.encode("utf-8"))
        fs = set(final_l)
        miss3 = [l for l in tl if l.strip() and l not in fs and l not in moved]
        # canon-family exception: strict-subset line dropped while strict-superset retained = zero info loss
        miss3 = [l for l in miss3 if not (l.startswith("- 坑律正典全量归档")
                 and any(l2 != l and l2.startswith(l) for l2 in final_l))]
        assert not miss3, f":3: lines lost: {[x[:60] for x in miss3]}"
        assert size < 10240, f"CODELY still {size}B over 10KB after archival"
        # archive suffix-concat: land the moved entries verbatim NOW (zero loss at this commit)
        ap = "research/memory-archive/202609.md"
        ab, ao, at = blobs(ap)
        assert ao.startswith(ab) and at.startswith(ab), "archive prefix assertion failed"
        a_txt = io.open(ap, encoding="utf-8").read()
        a_nb = nb_of(ab)
        sec_hdr = "## 十七批外迁（r88 bm-c·2026-09-27·水位律当窗整编·行级零丢失）"
        assert sec_hdr not in a_txt, "17th-batch header already in archive worktree"
        sec = a_nb + sec_hdr.encode("utf-8") + a_nb + a_nb.join(m.encode("utf-8") for m in moved) + a_nb
        with io.open(ap, "wb") as f:
            f.write(a_txt.encode("utf-8") + sec)
        resolved.add(ap)
        verdicts.append((ap, f"17th-batch suffix-concat: moved entries x{len(moved)} landed verbatim (stage-1 in-window archival, bytes == r88 suffix)"))
        print(f"  {ap}: +{len(moved)} entries (stage-1 archival)")
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(final)
    resolved.add(p)
    verdicts.append((p, f"entry-union origin-skeleton {len(o)}B + mine x{len(mine_new)} (pit x{len(my_pit)} idx x{len(my_idx)}); size={size}B; bidirectional zero-loss verified"))
    print(f"  {p}: origin {len(o)}B + mine x{len(mine_new)} -> {size}B")

# ---------------------------------------------------------------- 2. archive (suffix-concat, only if UU)
p = "research/memory-archive/202609.md"
if p in uu:
    b, o, t = blobs(p)
    bd, od, td = b.decode("utf-8"), o.decode("utf-8"), t.decode("utf-8")
    assert od.startswith(bd) and td.startswith(bd), "archive prefix assertion failed"
    final = od + td[len(bd):]
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(final)
    resolved.add(p)
    verdicts.append((p, "suffix-concat zero loss"))
    print(f"  {p}: suffix-concat")

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
    verdicts.append((path, f"rolling-ledger full-row-union + snapshot take-{'origin(:2)' if pick is jo else 'mine(:3)'} ({so} vs {st})"))
    print(f"  {path}: snapshot={'origin' if pick is jo else 'mine'} ({so} vs {st})")

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
    verdicts.append((p, f"js-wrapper whole-bytes {'origin(:2)' if data is o else 'mine(:3)'} ({so} vs {st})"))
    print(f"  {p}: side={'origin' if data is o else 'mine'}")

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

# ---------------------------------------------------------------- paper coupled side
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
    if pp not in resolved and pp.endswith(".json") and not pp.startswith(("results/paper/", "results/paper_export/", "docs/daily_report/")):
        take_new_json(pp)

missing = [pp for pp in uu if pp not in resolved]
assert not missing, f"UNRESOLVED: {missing}"
print("\nALL", len(uu), "UU RESOLVED (r88 stage-1):")
for pp, v in verdicts:
    print("  -", pp, "::", v)
print("RESOLVE-R88S1-OK")
