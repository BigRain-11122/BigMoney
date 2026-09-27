# -*- coding: utf-8 -*-
"""r87 bm-c inherited-rebase resolver (onto c3ca1fe9, replaying my r86 d1271fbf).
30-UU canon-resolved per SKILL.md + r330bmb same-shape precedent:
  CODELY entry-union (:2 skeleton = origin most-restructured face, + my 2 new lines; my 6 live
  pitlaws already archived on origin side = zero loss), archive suffix-concat, autofill
  composite-union keyset-identical + last_tick inner-ts, rolling-ledger unions, coupled-side
  paper/export/twins, js-wrapper whole-bytes, snapshot take-new deep-ts tie->HEAD, x2 line-union.
Verify-then-add per r185. EOL mirror base blob (:1:). List derived programmatically (r327).
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
    def scan(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in KEYS and isinstance(v, str) and len(v) >= 16:
                    nv = v.replace(" ", "T")[:19]
                    if nv > best[0]:
                        best[0] = nv
                scan(v)
        elif isinstance(o, list):
            for v in o:
                scan(v)
    scan(obj)
    return best[0]

def nb_of(b):
    return b"\r\n" if b"\r\n" in b else b"\n"

resolved = set()
def mark(p):
    resolved.add(p)

uu = [l.decode().strip() for l in subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
     capture_output=True).stdout.splitlines() if l.strip()]
assert len(uu) == 30, f"expected 30 UU, got {len(uu)}"
PAPER = [p for p in uu if p.startswith("results/paper/")]
EXPORT = [p for p in uu if p.startswith("results/paper_export/")]
verdicts = []

# ---------------------------------------------------------------- 1. CODELY.md
p = "CODELY.md"
b, o, t = blobs(p)
bl, ol, tl = b.decode("utf-8").splitlines(), o.decode("utf-8").splitlines(), t.decode("utf-8").splitlines()
bs, os_, ms = set(bl), set(ol), set(tl)
mine_new = [l for l in tl if l not in bs and l not in os_]
assert len(mine_new) == 2, f"mine_new != 2 lines: {len(mine_new)}"
my16 = [l for l in mine_new if "十六批外迁（r86 bm-c" in l]
mypit = [l for l in mine_new if "r86 bm-c" in l and "坑律" in l]
assert len(my16) == 1 and len(mypit) == 1, "my 16th-batch line / pitlaw entry not found"
idx = [i for i, l in enumerate(ol) if "十六批外迁" in l]
if idx:
    at = idx[-1] + 1
    final_l = ol[:at] + my16 + ol[at:]
else:
    final_l = list(ol)
final_l = final_l + mypit
nl = "\r\n" if b"\r\n" in b else "\n"
final = nl.join(final_l) + nl
archived = [l for l in bl if l.startswith("- [2026-09-27") and "坑律" in l]
for l in archived:
    assert l not in final, "archived pitlaw leaked back"
assert mypit[0] in final and my16[0] in final
size = len(final.encode("utf-8"))
assert size < 10240, f"CODELY {size}B over 10KB hard line"
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(final)
mark(p)
verdicts.append((p, f"entry-union: origin-skeleton {len(o)}B + mine x2 (16th-batch line + r86 pitlaw); size={size}B; base pitlaws x{len(archived)} kept archived-out"))
print(f"  {p}: size={size}B ({len(ol)}+2 lines)")

# ---------------------------------------------------------------- 2. archive
p = "research/memory-archive/202609.md"
b, o, t = blobs(p)
bd, od, td = b.decode("utf-8"), o.decode("utf-8"), t.decode("utf-8")
assert od.startswith(bd) and td.startswith(bd), "archive prefix assertion failed (manual review)"
my_suf = td[len(bd):]
final = od + my_suf
assert final.encode("utf-8").count("十六批".encode("utf-8")) >= 3
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(final)
mark(p)
verdicts.append((p, f"suffix-concat origin {len(o)}B + my-suffix {len(my_suf.encode('utf-8'))}B zero loss"))
print(f"  {p}: {len(o)}+{len(my_suf.encode('utf-8'))}B")

# ---------------------------------------------------------------- 3. autofill_state
p = "results/autofill_state.json"
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
union.sort(key=lambda r: r.get("ts", ""))  # write-back ascending (r245)
tlo, tlt = (jo.get("last_tick") or {}), (jt.get("last_tick") or {})
last_tick = tlo if (tlo.get("ts", ""), "") >= (tlt.get("ts", ""), "") else tlt  # tie -> HEAD(:2)
assert isinstance(last_tick, dict)
merged_state = dict(jo)
merged_state["launches"] = union
merged_state["last_tick"] = last_tick
nb = nb_of(b)
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(merged_state, ensure_ascii=False, indent=1) + ("\r\n" if nb == b"\r\n" else "\n"))
back = json.loads(io.open(p, encoding="utf-8").read())
assert isinstance(back["last_tick"], dict)
mark(p)
verdicts.append((p, f"mixed-dict+ledger composite-union {len(lo)}|{len(lt)}->{n_union} cap{len(back['launches'])} asc-write; last_tick {'HEAD(:2)' if last_tick is tlo else 'mine(:3)'} {tlo.get('ts')} vs {tlt.get('ts')}; flags={flags if flags else 'none'}"))
print(f"  {p}: launches {len(lo)}|{len(lt)}->{n_union}; last_tick {'HEAD' if last_tick is tlo else 'mine'}")

# ---------------------------------------------------------------- 4. rolling ledgers
def rolling_union(path, ledger_keys):
    b, o, t = blobs(path)
    jo, jt = json.loads(o), json.loads(t)
    out = dict(jo)
    for lk in ledger_keys:
        lo, lt = jo.get(lk, []), jt.get(lk, [])
        if not isinstance(lo, list) or not isinstance(lt, list):
            continue
        def k(r):
            return tuple(r.get(f) if isinstance(r, dict) else r for f in KEYF)
        seen, un = {}, []
        for r in lo + lt:
            kk = k(r)
            if kk not in seen:
                seen[kk] = r
                un.append(r)
        try:
            un.sort(key=lambda r: r.get("ts", "") if isinstance(r, dict) else "")
        except Exception:
            pass
        out[lk] = un
        print(f"  {path}[{lk}]: |ours|={len(lo)} |mine|={len(lt)} -> union={len(un)}")
    so, st = deep_ts(jo), deep_ts(jt)
    pick = jo if (so, "") >= (st, "") else jt
    for kk in set(jo) | set(jt):
        if kk not in ledger_keys:
            out[kk] = pick.get(kk, jo.get(kk, jt.get(kk)))
    nb = nb_of(b)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1) + ("\r\n" if nb == b"\r\n" else "\n"))
    json.loads(io.open(path, encoding="utf-8").read())
    mark(path)
    verdicts.append((path, f"rolling-ledger union + snapshot take-{'HEAD(:2)' if pick is jo else 'mine(:3)'} (ts {so} vs {st})"))
    print(f"  {path}: snapshot side={'HEAD' if pick is jo else 'mine'} ({so} vs {st})")

rolling_union("results/compute_audit.json", ("history",))
rolling_union("results/regime_state.json", ("history", "transitions"))

# ---------------------------------------------------------------- 5. js wrapper
p = "results/dashboard_status.js"
b, o, t = blobs(p)
mo = re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$", o.decode("utf-8"), re.S)
mt = re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$", t.decode("utf-8"), re.S)
so, st = deep_ts(json.loads(mo.group(1))), deep_ts(json.loads(mt.group(1)))
data = o if (so, "") >= (st, "") else t
with io.open(p, "wb") as f:
    f.write(data)
mark(p)
verdicts.append((p, f"js-wrapper whole-bytes take-{'HEAD(:2)' if data is o else 'mine(:3)'} ({so} vs {st})"))
print(f"  {p}: side={'HEAD' if data is o else 'mine'}")

# ---------------------------------------------------------------- 6. x2 jsonl
p = "results/x2_watch_log.jsonl"
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
mark(p)
verdicts.append((p, f"append-log line union base={len(bl_)} +ours {n_o} +mine {n_t} -> {len(out_l)}"))
print(f"  {p}: {len(bl_)}+{n_o}+{n_t}->{len(out_l)}")

# ---------------------------------------------------------------- 7. paper coupled side
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
    mark(pp)
verdicts.append(("results/paper/*_paper.json + paper_export/*", f"coupled-side {win} whole-bytes x{len(PAPER)+len(EXPORT)} (ts {side_ts['ours']} vs {side_ts['mine']})"))
print(f"  paper x{len(PAPER)} + export x{len(EXPORT)}: coupled side={win}")

# ---------------------------------------------------------------- 8. daily_report twins
pj, pm = "docs/daily_report/REPORT-2026-09-27.json", "docs/daily_report/REPORT-2026-09-27.md"
_, o2, t2 = blobs(pj)
so, st = deep_ts(json.loads(o2)), deep_ts(json.loads(t2))
win = "ours" if (so, "") >= (st, "") else "mine"
for pp in (pj, pm):
    _, o2, t2 = blobs(pp)
    with io.open(pp, "wb") as f:
        f.write(o2 if win == "ours" else t2)
json.loads(io.open(pj, encoding="utf-8").read())
mark(pj); mark(pm)
verdicts.append((pj + " & .md", f"coupled-side {win} via json ts probe ({so} vs {st}), md byte-copied same side"))
print(f"  twins: side={win}")

# ---------------------------------------------------------------- 9. snapshot take-new
def take_new_json(path):
    b, o2, t2 = blobs(path)
    jo2, jt2 = json.loads(o2), json.loads(t2)
    so, st = deep_ts(jo2), deep_ts(jt2)
    data = jo2 if (so, "") >= (st, "") else jt2  # tie -> HEAD(:2)
    side = "HEAD(:2)" if data is jo2 else "mine(:3)"
    nb = nb_of(b)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=1) + ("\r\n" if nb == b"\r\n" else "\n"))
    json.loads(io.open(path, encoding="utf-8").read())
    mark(path)
    verdicts.append((path, f"snapshot take-new {side} (ts {so} vs {st})"))
    print(f"  {path}: take_new {side} ({so} vs {st})")

for pp in uu:
    if pp in resolved or pp in (p,):
        continue
    if pp.endswith(".json") and not pp.startswith(("results/paper/", "results/paper_export/", "docs/daily_report/")):
        take_new_json(pp)

# ---------------------------------------------------------------- coverage
missing = [pp for pp in uu if pp not in resolved]
assert not missing, f"UNRESOLVED: {missing}"
print("\nALL 30 UU RESOLVED:")
for pp, v in verdicts:
    print("  -", pp, "::", v)
print("RESOLVE-OK")
