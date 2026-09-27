# -*- coding: utf-8 -*-
"""r336 bm-b S0 fold resolver v3 (DYNAMIC, UU-gated): tick-race-tolerant canonical rebuild.

Context: land machine/bm-b-r335 folded chain onto origin/main 2665c962 (bm-a r339 d9f7326a
+ tick 79dd44b9 + bm-c r92 2665c962). Replays 7 local picks; autofill tick keeps racing the
window (fire :X0:02 -> commit ~:X2:5x). Inherits r335 resolver v2 dynamic-sides law
(:2:/:3: preferred, HEAD:/REBASE_HEAD: blob fallback when tick destroyed stages, r331
stage-loss law) with three hardening changes:
  1. UU-gating: rebuild ONLY files in the live UU set at this stop (v2 rebuilt all expected
     files -- safe then, but v3 must not clobber cleanly auto-merged faces).
  2. UNKNOWN gate: any UU file not in FILES -> print + exit 2 (classify-first discipline,
     no blind resolve; extend FILES or hand-adjudicate).
  3. Self-add: each rebuilt file is verified (parse/zero-loss/marker/bare-CR churn check
     r338 law) then `git add`-ed inside this same process = atomic window vs tick; final
     assert live UU set is empty before driver may `rebase --continue`.
Recipes per bigmoney-conflict-resolve canon (law anchors in skill table).
"""
import datetime
import glob as globmod
import io
import json
import re
import subprocess
import sys

NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

FILES = [
    ("CODELY.md", "codely"),
    ("docs/daily_report/REPORT-2026-09-27.json", "take_new"),
    ("docs/daily_report/REPORT-2026-09-27.md", "take_new_md"),
    ("research/memory-archive/202609.md", "archive"),
    ("results/autofill_state.json", "autofill"),
    ("results/ah_panel_status.json", "take_new"),
    ("results/compute_audit.json", "compute"),
    ("results/daily_scorecard.json", "take_new"),
    ("results/dashboard_status.js", "take_new_js"),
    ("results/dashboard_status.json", "take_new"),
    ("results/fundamental_b_layer_filter.json", "take_new"),
    ("results/futures_update_status.json", "take_new"),
    ("results/heat_update_status.json", "take_new"),
    ("results/lhb_update_status.json", "take_new"),
    ("results/moneyflow_update_status.json", "take_new"),
    ("results/options_update_status.json", "take_new"),
    ("results/repo_update_status.json", "take_new"),
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
    ("results/prospect_promotion/PROS-*.json", "take_new_glob"),
    ("results/market_clock/call_latest.json", "take_new"),
    ("results/market_clock/CALL-*.json", "take_new_glob"),
    ("results/regime_state.json", "regime"),
    ("results/scorecard_v1.json", "take_new"),
    ("results/strategy_scorecard.json", "take_new"),
    ("results/t35_open_fill_verify.json", "take_new"),
    ("results/token_usage.json", "take_new"),
    ("results/update_status.json", "take_new"),
    ("results/watermark_red.json", "take_new"),
    ("results/x2_watch_log.jsonl", "x2"),
]

# expand glob entries against the working tree once
EXPANDED = []
for pat, kind in FILES:
    if kind.endswith("_glob"):
        for m in sorted(globmod.glob(pat)):
            EXPANDED.append((m.replace("\\", "/"), kind[: -len("_glob")]))
        EXPANDED.append((pat, kind))  # keep pattern itself for unknown-gate matching
    else:
        EXPANDED.append((pat, kind))

uu = set(l.decode().strip() for l in subprocess.run(
    ["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True
).stdout.splitlines() if l.strip())

known_pats = {p for p, _ in EXPANDED}
import fnmatch
unknown = sorted(f for f in uu if f not in known_pats and not any(fnmatch.fnmatch(f, p) for p, k in EXPANDED if k.endswith("_glob")))
if unknown:
    print("UNKNOWN-UU (classify-first discipline, extend FILES or hand-adjudicate):")
    for f in unknown:
        print("  " + f)
    sys.exit(2)
print(f"UU at stop ({len(uu)}): {sorted(uu)}")

rb = subprocess.run(["git", "rev-parse", "--short", "REBASE_HEAD"], capture_output=True).stdout.decode().strip()
print(f"REBASE_HEAD pick: {rb}")


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


def churn_check(path, data):
    """r338 bare-CR churn law: written artifact must carry no bare CR."""
    bare_cr = data.count(b"\r") - data.count(b"\r\n")
    if bare_cr:
        print(f"CHURN-FAIL {path}: bare-CR x{bare_cr}")
        return False
    return True


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
                    nv = v.replace(" ", "T")[:19]      # r335: separator-normalize before compare
                    if nv > NOW:      # future sentinel -> ignore
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


def finish(path, data):
    """verify + self-add (atomic window vs tick)."""
    lines = data.decode("utf-8", "replace").splitlines()
    if any(l.startswith("<<<<<<<") or l.startswith(">>>>>>>") or l.startswith("=======") for l in lines):
        print(f"VERIFY-FAIL {path}: conflict marker present"); sys.exit(3)
    if path.endswith(".json"):
        try:
            json.loads(data.decode("utf-8"))
        except Exception as ex:
            print(f"VERIFY-FAIL {path}: parse {ex}"); sys.exit(3)
    elif path.endswith(".jsonl"):
        for l in lines:
            if l.strip():
                try:
                    json.loads(l)
                except Exception as ex:
                    print(f"VERIFY-FAIL {path}: jsonl line parse {ex}"); sys.exit(3)
    if not churn_check(path, data):
        sys.exit(3)
    with io.open(path, "wb") as f:
        f.write(data)
    r = subprocess.run(["git", "add", "--", path], capture_output=True)
    if r.returncode != 0:
        print(f"ADD-FAIL {path}: {r.stderr.decode()}"); sys.exit(3)


# ------------------------------------------------------------- per-file rebuild
for path, kind in EXPANDED:
    if path not in uu:
        continue                                  # UU-gate: never touch clean/auto-merged faces
    a, b, src = sides(path)
    if not a.strip() and not b.strip():
        emit(path, f"SKIP no-sides-recoverable")
        continue
    tag = f"src={src}"
    if kind == "codely":
        # D-20260927-09: NO line-level dedupe (collapses entry structure live-fire). Entry-granular
        # oa-filter: replayed commit's added-lines split into contiguous blocks (entries) kept
        # verbatim; block appended only if its first non-empty line (entry header) absent in ours.
        # Fold context: r334/r335 content largely already landed via 1158a1ea convergence -> most
        # blocks skip, result ~ ours base (pure-append prefix law inapplicable: archivals = in-place
        # edits, classifier's prefix-identity assertion would fail -> this IS the manual review).
        diff = raw(["git", "diff", "REBASE_HEAD^", "REBASE_HEAD", "--", "CODELY.md"]).decode("utf-8")
        blocks, cur = [], []
        for l in diff.splitlines():
            if l.startswith("+") and not l.startswith("+++"):
                cur.append(l[1:])
            elif cur:
                blocks.append(cur); cur = []
        if cur:
            blocks.append(cur)
        ol = a.decode("utf-8").splitlines()
        n_blk, added = 0, 0
        for blk in blocks:
            hdr = next((x for x in blk if x.strip()), "")
            if hdr and hdr in ol:
                continue
            ol.extend(blk)
            n_blk += 1
            added += len(blk)
        data = ("\n".join(ol) + eol_of(a)).encode("utf-8")
        finish(path, data)
        emit(path, f"oa-filter entry-granular ours={len(a)}B blocks={len(blocks)} appended={n_blk}"
                   f"(+{added}L) -> {len(data)}B ({tag})")
    elif kind == "archive":
        al, tl = a.decode("utf-8").splitlines(), b.decode("utf-8").splitlines()
        pre = 0
        while pre < min(len(al), len(tl)) and al[pre] == tl[pre]:
            pre += 1
        res = al + tl[pre:]       # direct-concat suffixes, dup-section coexist precedent (Fifteenth Batch)
        data = ("\n".join(res) + eol_of(a)).encode("utf-8")
        finish(path, data)
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
        data = json.dumps(res, ensure_ascii=False, indent=1).replace("\n", eol).encode("utf-8")
        finish(path, data)
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
        data = (json.dumps(res, ensure_ascii=False, indent=1) + eol_of(a)).encode("utf-8")
        finish(path, data)
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
        data = (json.dumps(da, ensure_ascii=False, indent=1) + eol_of(a)).encode("utf-8")
        finish(path, data)
        emit(path, f"regime face {'theirs' if st > sa else 'ours'} (A={sa or '-'} B={st or '-'}) ({tag})")
    elif kind == "x2":
        al, tl = a.decode("utf-8").splitlines(), b.decode("utf-8").splitlines()
        seen, out = set(), []
        for l in al + tl:
            if l and l not in seen:
                seen.add(l)
                out.append(l)
        data = ("\n".join(out) + ("\n" if out else "")).encode("utf-8")
        finish(path, data)
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
        finish(path, data)
        emit(path, f"take_new {win} (A={sa or '-'} B={sb or '-'}) ({tag})")

# ------------------------------------------------------------- final gate
left = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True).stdout
left = set(l.decode().strip() for l in left.splitlines() if l.strip())
if left:
    print(f"LEFTOVER-UU after resolve: {sorted(left)}"); sys.exit(4)
for line in results_log:
    print("  " + line)
n = sum(1 for p, _ in EXPANDED if p in uu)
print(f"RESOLVER-OK rebuilt+verified+self-added {n} UU files at pick {rb} (dynamic sides, zero markers, bare-CR clean)")
