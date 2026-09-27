# -*- coding: utf-8 -*-
"""r330 bm-b push-collision resolver (rebase replay of ed164cb5 vs bm-a r329).

Classifier: 13 classified + 17 UNKNOWN (fail-closed -> manual per-file verdicts
below). Rebase side map: :1=base, :2=ours(HEAD=bm-a landed face), :3=theirs(MY
replaying commit). Recipes per SKILL.md + r83 composite-key law + r85
coupled-paper-side + r140 tie->HEAD + r311 deep-ts probe + r223 CRLF mirror.
"""
import io, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def git(*a):
    return subprocess.run(["git", *a], capture_output=True).stdout

def blobs(path):
    b = git("show", f":1:{path}")
    o = git("show", f":2:{path}")
    t = git("show", f":3:{path}")
    return b, o, t

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

def take_new_json(path):
    b, o, t = blobs(path)
    jo, jt = json.loads(o), json.loads(t)
    so, st = deep_ts(jo), deep_ts(jt)
    win = "ours(:2)" if (so, "") >= (st, "") else "theirs(:3)"  # tie -> HEAD
    data = jo if win.startswith("ours") else jt
    nb = b"\r\n" if b"\r\n" in b else b"\n"
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=1) + ("\r\n" if nb == b"\r\n" else "\n"))
    json.loads(io.open(path, encoding="utf-8").read())
    print(f"  {path}: take_new {win} ts_ours={so} ts_theirs={st}")

verdicts = []

uu = [l.decode().strip() for l in subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
     capture_output=True).stdout.splitlines() if l.strip()]
print("UU files:", len(uu))
assert len(uu) == 30, f"expected 30 UU, got {len(uu)}"

PAPER = [p for p in uu if p.startswith("results/paper/")]
EXPORT = [p for p in uu if p.startswith("results/paper_export/")]

# -------------------------------------------------------------- 1. CODELY.md
path = "CODELY.md"
b, o, t = blobs(path)
base_l = b.decode("utf-8").splitlines()
ours_l = o.decode("utf-8").splitlines()   # bm-a landed face
mine_l = t.decode("utf-8").splitlines()   # my 16th-batch restructured face
bs, os_, ms = set(base_l), set(ours_l), set(mine_l)
their_new = [l for l in ours_l if l not in bs and l not in ms]
archived = [l for l in base_l if l.startswith("- [2026-09-27") and "坑律" in l]
final_l = mine_l + their_new
final = "\n".join(final_l) + "\n"
for l in archived:
    assert l not in final, "archived pitlaw leaked back into CODELY"
assert any("r330 bm-b" in l and "坑律" in l for l in final_l), "my new pitlaw missing"
assert any("十六批" in l for l in final_l), "16th-batch note missing"
size = len(final.encode("utf-8"))
assert size < 10240, f"CODELY {size}B over hard line"
with io.open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(final)
print(f"  CODELY.md: memory-union(restructure) mine + bm-a new x{len(their_new)}; size={size}B; archived9 kept OUT")
verdicts.append(("CODELY.md", f"memory-union manual: my archival face + bm-a {len(their_new)} new lines"))

# -------------------------------------------------------------- 2. archive
path = "research/memory-archive/202609.md"
b, o, t = blobs(path)
bd, od, td = b.decode("utf-8"), o.decode("utf-8"), t.decode("utf-8")
assert od.startswith(bd), "bm-a side not base-prefix (manual review!)"
assert td.startswith(bd), "my side not base-prefix (manual review!)"
their_suf = od[len(bd):]
my_suf = td[len(bd):]
final = od + my_suf
assert final.count("十六批（r330 bm-b") == 1
with io.open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(final)
print(f"  {path}: suffix-concat base + bm-a-suffix {len(their_suf)}B + my-suffix {len(my_suf)}B")
verdicts.append((path, "suffix-concat both suffixes zero loss"))

# -------------------------------------------------------------- 3. autofill_state
path = "results/autofill_state.json"
b, o, t = blobs(path)
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
        idx = [i for i, x in enumerate(union) if key(x) == k][0]
        union[idx] = merged
    else:
        seen[k] = r
        union.append(r)
n_union = len(union)
union.sort(key=lambda r: r.get("ts", ""), reverse=True)
union = union[:50]                     # cap 50 newest (R215)
union.sort(key=lambda r: r.get("ts", ""))  # write-back ascending (r245 law)
tlo, tlt = (jo.get("last_tick") or {}), (jt.get("last_tick") or {})
lt_ours, lt_theirs = tlo.get("ts", ""), tlt.get("ts", "")
last_tick = tlo if (lt_ours, "") >= (lt_theirs, "") else tlt   # tie -> HEAD
assert isinstance(last_tick, dict), "last_tick not dict"
merged = dict(jo)
merged["launches"] = union
merged["last_tick"] = last_tick
nb = "\r\n" if b"\r\n" in b else "\n"
with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(merged, ensure_ascii=False, indent=1) + nb)
back = json.loads(io.open(path, encoding="utf-8").read())
assert isinstance(back["last_tick"], dict)
print(f"  {path}: launches |ours|={len(lo)} |theirs|={len(lt)} -> union={n_union} cap-> {len(back['launches'])}"
      f" (dup-merged keyset identical); last_tick {'ours' if last_tick is tlo else 'theirs'}"
      f" {lt_ours} vs {lt_theirs}; flags={flags if flags else 'none'}")
verdicts.append((path, f"mixed-dict+ledger composite-union {len(lo)}|{len(lt)}->{n_union} cap50 asc-write,"
                       f" last_tick {'HEAD' if last_tick is tlo else 'mine'}"))

# -------------------------------------------------------------- 4. compute_audit
def rolling_union(path, ledger_keys, snap_new=True):
    b, o, t = blobs(path)
    jo, jt = json.loads(o), json.loads(t)
    out = dict(jo)
    for lk in ledger_keys:
        lo, lt = jo.get(lk, []), jt.get(lk, [])
        if not isinstance(lo, list) or not isinstance(lt, list):
            continue
        def k(r):
            return tuple(r.get(f) if isinstance(r, dict) else r for f in ("ts", "machine", "pid", "runner_sha256", "entry", "shard"))
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
        print(f"  {path}[{lk}]: |ours|={len(lo)} |theirs|={len(lt)} -> union={len(un)}")
    if snap_new:
        so, st = deep_ts(jo), deep_ts(jt)
        pick = jo if (so, "") >= (st, "") else jt
        for k in set(jo) | set(jt):
            if k not in ledger_keys:
                out[k] = pick.get(k, jo.get(k, jt.get(k)))
        print(f"  {path}: snapshot take_new ts_ours={so} ts_theirs={st}")
    nb = "\r\n" if b"\r\n" in b else "\n"
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1) + nb)
    json.loads(io.open(path, encoding="utf-8").read())
    verdicts.append((path, f"rolling-ledger union + snapshot take-new"))

rolling_union("results/compute_audit.json", ("history",))
rolling_union("results/regime_state.json", ("history", "transitions"))

# -------------------------------------------------------------- 5. js wrapper
path = "results/dashboard_status.js"
b, o, t = blobs(path)
mo = re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$", o.decode("utf-8"), re.S)
mt = re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$", t.decode("utf-8"), re.S)
so, st = deep_ts(json.loads(mo.group(1))), deep_ts(json.loads(mt.group(1)))
data = o if (so, "") >= (st, "") else t
with io.open(path, "wb") as f:
    f.write(data)
print(f"  {path}: js-wrapper take-side whole bytes ({'ours' if data is o else 'theirs'}) ts {so} vs {st}")
verdicts.append((path, "js-wrapper whole-bytes take-side"))

# -------------------------------------------------------------- 6. jsonl union
path = "results/x2_watch_log.jsonl"
b, o, t = blobs(path)
bl, ol, tl = b.decode("utf-8").splitlines(), o.decode("utf-8").splitlines(), t.decode("utf-8").splitlines()
seen = set(bl)
out = list(bl)
n_o = n_t = 0
for l in ol:
    if l and l not in seen:
        seen.add(l); out.append(l); n_o += 1
for l in tl:
    if l and l not in seen:
        seen.add(l); out.append(l); n_t += 1
with io.open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out) + ("\n" if out else ""))
print(f"  {path}: line union base={len(bl)} +ours {n_o} +theirs {n_t} -> {len(out)}")
verdicts.append((path, f"append-log line union +{n_o}+{n_t}"))

# -------------------------------------------------------------- 7. paper coupled side
side_ts = {"ours": "", "theirs": ""}
for p in PAPER:
    b, o, t = blobs(p)
    side_ts["ours"] = max(side_ts["ours"], deep_ts(json.loads(o)))
    side_ts["theirs"] = max(side_ts["theirs"], deep_ts(json.loads(t)))
win = "ours" if (side_ts["ours"], "") >= (side_ts["theirs"], "") else "theirs"
for p in PAPER + EXPORT:
    b, o, t = blobs(p)
    data = o if win == "ours" else t
    with io.open(p, "wb") as f:
        f.write(data)
    json.loads(io.open(p, encoding="utf-8").read())
print(f"  paper x{len(PAPER)}+export x{len(EXPORT)}: coupled side={win} (ts {side_ts['ours']} vs {side_ts['theirs']})")
verdicts.append(("results/paper/*_paper.json+paper_export/*", f"coupled-side {win} whole-bytes x{len(PAPER)+len(EXPORT)}"))

# -------------------------------------------------------------- 8. daily_report twins
pj = "docs/daily_report/REPORT-2026-09-27.json"
pm = "docs/daily_report/REPORT-2026-09-27.md"
b, o, t = blobs(pj)
so, st = deep_ts(json.loads(o)), deep_ts(json.loads(t))
win = "ours" if (so, "") >= (st, "") else "theirs"
for p in (pj, pm):
    b, o, t = blobs(p)
    with io.open(p, "wb") as f:
        f.write(o if win == "ours" else t)
json.loads(io.open(pj, encoding="utf-8").read())
print(f"  daily_report twins: coupled side={win} (json ts {so} vs {st})")
verdicts.append(("docs/daily_report/REPORT-2026-09-27.*", f"coupled-side {win} via json ts probe"))

# -------------------------------------------------------------- 9. plain take-new snapshots
for p in ("results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json", "results/heat_update_status.json",
          "results/lhb_update_status.json", "results/token_usage.json",
          "results/update_status.json", "results/daily_scorecard.json",
          "results/scorecard_v1.json", "results/strategy_scorecard.json",
          "results/t35_open_fill_verify.json", "results/prospect_paper/_summary.json",
          "results/prospect_promotion/_summary.json"):
    if p in uu:
        take_new_json(p)
        verdicts.append((p, "snapshot take-new deep-ts (tie->HEAD)"))

done = set(x[0] for x in verdicts) | {p for p in PAPER + EXPORT} | {"docs/daily_report/REPORT-2026-09-27.json", "docs/daily_report/REPORT-2026-09-27.md"}
covered = set()
for v in verdicts:
    if ("results/paper/" in v[0]) or ("paper_export" in v[0]):
        covered.update(PAPER); covered.update(EXPORT)
    elif "daily_report" in v[0]:
        covered.add("docs/daily_report/REPORT-2026-09-27.json"); covered.add("docs/daily_report/REPORT-2026-09-27.md")
    else:
        covered.add(v[0])
missing = [p for p in uu if p not in covered]
assert not missing, f"UNRESOLVED: {missing}"
print("\nALL", len(uu), "UU RESOLVED:")
for p, v in verdicts:
    print("  -", p, "::", v)
print("RESOLVE-OK")
