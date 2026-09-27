# -*- coding: utf-8 -*-
"""r335 bm-b S0 fold resolver v2 (DYNAMIC): tick-race-tolerant canonical rebuild.

Context: 2nd-fold rebase (chain onto 72bea1dd bm-c r91) stopped at pick 2 (0a9dda27, r334 face)
while the autofill tick keeps racing this window (17:13 blind-add / ~17:27 stash-pop UU /
~17:30 more staging). Instead of asserting a frozen UU snapshot, this resolver REBUILDS every
expected conflict file canonically from its two sides -- preferring live index stages :2/:3,
falling back to HEAD: / REBASE_HEAD: direct blob reads when the tick destroyed stages
(r331 stage-loss recovery law, bm-c r91 stash-pop same-family law) -- then the driver
re-adds them explicitly in the same shell invocation (atomic window vs tick).

Side map at stop: :1=base(f2907bef original tick) :2=ours=HEAD(pick-1 replay, bm-c-r91 lineage)
:3=theirs=REBASE_HEAD(0a9dda27 r334 face). Recipes per bigmoney-conflict-resolve canon.
"""
import datetime
import io
import json
import re
import subprocess

NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

FILES = [
    ("CODELY.md", "codely"),
    ("docs/daily_report/REPORT-2026-09-27.json", "take_new"),
    ("docs/daily_report/REPORT-2026-09-27.md", "take_new_md"),
    ("research/memory-archive/202609.md", "archive"),
    ("results/autofill_state.json", "autofill"),
    ("results/compute_audit.json", "compute"),
    ("results/daily_scorecard.json", "take_new"),
    ("results/dashboard_status.js", "take_new_js"),
    ("results/dashboard_status.json", "take_new"),
    ("results/fundamental_b_layer_filter.json", "take_new"),
    ("results/futures_update_status.json", "take_new"),
    ("results/heat_update_status.json", "take_new"),
    ("results/lhb_update_status.json", "take_new"),
    ("results/paper/COMPOSITE-CE-01_paper.json", "take_new"),
    ("results/paper/COMPOSITE-CE-02_paper.json", "take_new"),
    ("results/paper/DROUGHT-CE-01_paper.json", "take_new"),
    ("results/paper/ENGULF-CE-01_paper.json", "take_new"),
    ("results/paper/NEEDLE-DE-01_paper.json", "take_new"),
    ("results/paper/VOLATILITY-CE-01_paper.json", "take_new"),
    ("results/paper_export/export-2026-09-24.json", "take_new"),
    ("results/paper_export/latest.json", "take_new"),
    ("results/prospect_paper/_summary.json", "take_new"),
    ("results/prospect_promotion/_summary.json", "take_new"),
    ("results/regime_state.json", "regime"),
    ("results/scorecard_v1.json", "take_new"),
    ("results/strategy_scorecard.json", "take_new"),
    ("results/t35_open_fill_verify.json", "take_new"),
    ("results/token_usage.json", "take_new"),
    ("results/update_status.json", "take_new"),
    ("results/x2_watch_log.jsonl", "x2"),
]

uu = set(l.decode().strip() for l in subprocess.run(
    ["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True
).stdout.splitlines() if l.strip())
print(f"UU at resolver start ({len(uu)}): tick-drift tolerated; canonical rebuild for all expected files")


def raw(run_args):
    return subprocess.run(run_args, capture_output=True).stdout


def sides(path):
    """Prefer live stages :2/:3; fallback to HEAD:/REBASE_HEAD: blob reads (stage-loss recovery)."""
    a = raw(["git", "show", f":2:{path}"])
    b = raw(["git", "show", f":3:{path}"])
    src = "stages"
    if not a.strip():
        a = raw(["git", "show", f"HEAD:{path}"]); src = "HEAD-fallback"
    if not b.strip():
        b = raw(["git", "show", f"REBASE_HEAD:{path}"]); src = src if src != "stages" else "REBASE_HEAD-fallback"
    return a, b, src


def eol_of(b):
    crlf = b.count(b"\r\n")
    return "\r\n" if crlf >= (b.count(b"\n") - crlf) and crlf > 0 else "\n"


def deep_ts(obj):
    best = [""]
    KEYS = ("ts", "generated", "generated_at", "updated", "updated_at", "asof",
            "last_run", "written_at", "last_attempt", "now", "generated_from_state_updated")

    def scan(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in KEYS and isinstance(v, str) and len(v) >= 16:
                    nv = v.replace(" ", "T")[:19]
                    if nv > NOW:      # r334 bm-a future-sentinel
                        continue
                    if nv > best[0]:
                        best[0] = nv
                scan(v)
        elif isinstance(o, list):
            for v in o:
                scan(v)
    scan(obj)
    return best[0]


def jload(b):
    return json.loads(b.decode("utf-8"))


results_log = []


def emit(path, msg):
    results_log.append(f"{path}: {msg}")


# ------------------------------------------------------------- per-file rebuild
for path, kind in FILES:
    in_uu = path in uu
    a, b, src = sides(path)
    if not a.strip() and not b.strip():
        emit(path, f"SKIP no-sides-recoverable (in_uu={in_uu})")
        continue
    tag = f"inUU={in_uu} src={src}"
    if kind == "codely":
        diff = raw(["git", "diff", "REBASE_HEAD^", "REBASE_HEAD", "--", "CODELY.md"]).decode("utf-8")
        mine_new = [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
        ol = a.decode("utf-8").splitlines()
        added = 0
        for l in mine_new:
            if l.strip() and l not in ol:
                ol.append(l)
                added += 1
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write("\n".join(ol) + eol_of(a))
        emit(path, f"oa-filter ours={len(a)}B +{added} mine_new -> {len(open(path,'rb').read())}B ({tag})")
    elif kind == "archive":
        al, tl = a.decode("utf-8").splitlines(), b.decode("utf-8").splitlines()
        pre = 0
        while pre < min(len(al), len(tl)) and al[pre] == tl[pre]:
            pre += 1
        res = al + tl[pre:]       # direct-concat suffixes, dup-section coexist precedent (Fifteenth Batch)
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write("\n".join(res) + eol_of(a))
        emit(path, f"archive concat common_pre={pre} A={len(al)} B={len(tl)} -> {len(res)} ({tag})")
    elif kind == "autofill":
        da, db = jload(a), jload(b)
        key = lambda r: (r.get("ts"), r.get("machine"), r.get("entry"), r.get("shard"), r.get("pid"), r.get("verdict"))
        seen, union = set(), []
        for r in da.get("launches", []) + db.get("launches", []):
            if key(r) not in seen:
                seen.add(key(r))
                union.append(r)
        precap = len(union)
        union.sort(key=lambda r: r.get("ts") or "", reverse=True)
        union = union[:50]
        union.sort(key=lambda r: r.get("ts") or "")       # r245 ts-asc write-back
        res = dict(da)
        for k in db:
            res.setdefault(k, db[k])
        res["launches"] = union
        ta, tb = da.get("last_tick", {}), db.get("last_tick", {})
        if isinstance(tb, dict) and (tb.get("ts") or "") > (ta.get("ts") or ""):
            res["last_tick"] = tb                          # r140 whole-dict inner-ts, tie->ours
        assert isinstance(res.get("last_tick"), dict)
        eol = eol_of(b)
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(json.dumps(res, ensure_ascii=False, indent=1).replace("\n", eol))
        chk = jload(open(path, "rb").read())
        assert chk["launches"] == union
        emit(path, f"launches A={len(da.get('launches', []))} B={len(db.get('launches', []))} "
                   f"union_precap={precap} kept={len(union)} last_tick.ts={chk['last_tick'].get('ts')} ({tag})")
    elif kind == "compute":
        da, db = jload(a), jload(b)
        ha, ht = da.get("history", []), db.get("history", [])
        kf = [f for f in ("ts", "machine", "cores", "pid", "entry", "shard") if ha and f in ha[-1]]
        seen, un = set(), []
        for r in ha + ht:
            kk = tuple(r.get(f) for f in kf) if kf else (json.dumps(r, sort_keys=True),)
            if kk not in seen:
                seen.add(kk)
                un.append(r)
        un.sort(key=lambda r: (r.get("ts") or r.get("asof") or ""))
        expected = len({json.dumps(r, sort_keys=True) for r in ha} | {json.dumps(r, sort_keys=True) for r in ht})
        assert len(un) == expected, f"compute union {len(un)} != |A\u222aB| {expected}"
        res = dict(da)
        sa, st = deep_ts(da), deep_ts(db)
        if st > sa:
            for k in set(da) | set(db):
                if k != "history":
                    res[k] = db.get(k, da.get(k))
        res["history"] = un
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(json.dumps(res, ensure_ascii=False, indent=1) + eol_of(a))
        emit(path, f"history A={len(ha)} B={len(ht)} -> union={len(un)}(==|A\u222aB| {expected}) "
                   f"latest {'theirs' if st > sa else 'ours'} (A={sa or '-'} B={st or '-'}) ({tag})")
    elif kind == "regime":
        da, db = jload(a), jload(b)
        for lk in ("history", "transitions"):
            ra, rt = da.get(lk, []), db.get(lk, [])
            if not (isinstance(ra, list) and isinstance(rt, list)):
                continue
            kf = [f for f in ("ts", "asof", "state", "raw_level", "updated") if ra and f in ra[0]]
            seen, un = set(), []
            for r in ra + rt:
                kk = tuple(r.get(f) for f in kf) if kf else (json.dumps(r, sort_keys=True),)
                if kk not in seen:
                    seen.add(kk)
                    un.append(r)
            expected = len({json.dumps(r, sort_keys=True) for r in ra} | {json.dumps(r, sort_keys=True) for r in rt})
            assert len(un) == expected, f"regime {lk} union {len(un)} != {expected}"
            da[lk] = un
        sa, st = deep_ts(da), deep_ts(db)
        if st > sa:
            for k in set(da) | set(db):
                if k not in ("history", "transitions"):
                    da[k] = db.get(k, da.get(k))
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(json.dumps(da, ensure_ascii=False, indent=1) + eol_of(a))
        emit(path, f"regime face {'theirs' if st > sa else 'ours'} (A={sa or '-'} B={st or '-'}) ({tag})")
    elif kind == "x2":
        al, tl = a.decode("utf-8").splitlines(), b.decode("utf-8").splitlines()
        seen, out = set(), []
        for l in al + tl:
            if l and l not in seen:
                seen.add(l)
                out.append(l)
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(out) + ("\n" if out else ""))
        emit(path, f"line union A={len(al)} B={len(tl)} -> {len(out)} zero-loss ({tag})")
    else:  # take_new family
        if kind == "take_new_js":
            m = re.compile(rb"window\.DASH_DATA\s*=\s*(.*?);\s*$", re.S)
            ja, jb = json.loads(m.search(a).group(1)), json.loads(m.search(b).group(1))
        elif kind == "take_new_md":
            ja = {"ts": re.search(rb"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", a).group(1).decode()}
            jb = {"ts": re.search(rb"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", b).group(1).decode()}
        else:
            ja, jb = jload(a), jload(b)
        sa, sb = deep_ts(ja), deep_ts(jb)
        win, data = ("ours", a) if sa >= sb else ("theirs", b)   # r140 tie -> ours/HEAD
        with io.open(path, "wb") as f:
            f.write(data)
        emit(path, f"take_new {win} (A={sa or '-'} B={sb or '-'}) ({tag})")

# ------------------------------------------------------------- verify all
bad = []
for path, _ in FILES:
    p = open(path, "rb").read()
    lines = p.decode("utf-8", "replace").splitlines()
    if any(l.startswith("<<<<<<<") or l.startswith(">>>>>>>") or l.startswith("=======") for l in lines):
        bad.append((path, "marker"))
    if path.endswith(".json"):
        try:
            json.loads(p.decode("utf-8"))
        except Exception as ex:
            bad.append((path, f"parse {ex}"))
    elif path.endswith(".jsonl"):
        for l in lines:
            if l.strip():
                json.loads(l)
assert not bad, f"verify FAIL: {bad}"
for line in results_log:
    print("  " + line)
print(f"RESOLVER-OK {len(FILES)} files canonical-rebuilt + verified (dynamic sides, zero conflict markers)")
