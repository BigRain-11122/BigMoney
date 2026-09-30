"""r475 bm-b: interrupted-rebase conflict resolver (canonical recipes per bigmoney-conflict-resolve skill).

State probed: ours(:2) = new base (bm-a r485 + bm-b r474 prereg/burn already replayed);
theirs(:3) = ec72e60f8 (bm-b round 474 S6 spine closeout, LAST pick in todo).
All recipes fail-closed: missing ts anchor on a take-new face -> exit 2 with file flagged.
"""
import json, subprocess, sys, os

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

def stage_blob(path, stage):
    r = subprocess.run(["git", "-C", REPO, "show", f":{stage}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show :{stage}:{path}: {r.stderr.decode('utf-8','replace')[:200]}")
    return r.stdout

def write_bytes(path, data):
    full = os.path.join(REPO, path)
    with open(full, "wb") as f:
        f.write(data)

def loadj(b):
    return json.loads(b.decode("utf-8-sig"))

TS_KEYS = ["generated", "generated_at", "updated", "updated_at", "ts", "asof", "as_of",
           "last_run", "cutoff", "date", "run_ts", "timestamp", "time"]

def find_ts(d):
    """Return (key, value) of first ts-like top-level key with string/number value."""
    for k in TS_KEYS:
        if k in d and isinstance(d[k], (str, int, float)):
            return k, str(d[k])
    return None, None

log = []
def note(msg):
    log.append(msg)
    print(msg)

def resolve_take_new(path, ts_key_hint=None):
    a, b = stage_blob(path, 2), stage_blob(path, 3)
    da, db = loadj(a), loadj(b)
    ka, va = find_ts(da) if ts_key_hint is None else (ts_key_hint, da.get(ts_key_hint))
    kb, vb = find_ts(db) if ts_key_hint is None else (ts_key_hint, db.get(ts_key_hint))
    if ka is None or kb is None or va is None or vb is None:
        note(f"FAIL-CLOSED {path}: no ts anchor (ours keys={list(da)[:8]})")
        return False
    if str(va) >= str(vb):  # ISO ts: lexicographic OK; same-second tie -> HEAD (r140)
        side, blob, tag = "ours(HEAD)", a, str(va)
    else:
        side, blob, tag = "theirs(replay)", b, str(vb)
    json.loads(blob.decode("utf-8-sig"))  # parse-validate before write (r185)
    write_bytes(path, blob)
    note(f"take-new {path}: {side} ts[{ka}]={tag} (other={vb})")
    return True

def resolve_json_twin_by_ts(json_path, md_path):
    """Pick side by the JSON twin's ts; write both members from that side (twin consistency)."""
    if not resolve_take_new(json_path):
        return False
    # determine chosen side by re-reading written file vs stages
    a, b = stage_blob(json_path, 2), stage_blob(json_path, 3)
    with open(os.path.join(REPO, json_path), "rb") as f:
        cur = f.read()
    src = None
    if cur == a:
        src = 2
    elif cur == b:
        src = 3
    if src is None:
        note(f"FAIL-CLOSED {md_path}: cannot map chosen side")
        return False
    write_bytes(md_path, stage_blob(md_path, src))
    note(f"twin {md_path}: copied from side :{src} (same side as {json_path})")
    return True

def union_list_by_rows(a_rows, b_rows):
    """Zero-loss row union, dedupe identical rows, preserve first-seen order, stable by insertion."""
    out, seen = [], set()
    for row in a_rows + b_rows:
        key = json.dumps(row, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            out.append(row)
    return out

def resolve_rolling_ledger(path, ledger_keys):
    a, b = stage_blob(path, 2), stage_blob(path, 3)
    da, db = loadj(a), loadj(b)
    merged = dict(da)
    for k in ledger_keys:
        ra, rb = da.get(k), db.get(k)
        if isinstance(ra, list) and isinstance(rb, list):
            merged[k] = union_list_by_rows(ra, rb)
            note(f"union {path}[{k}]: |ours|={len(ra)} |theirs|={len(rb)} -> |union|={len(merged[k])}")
        elif isinstance(ra, dict) and isinstance(rb, dict):
            m = dict(ra)
            for kk, vv in rb.items():
                m.setdefault(kk, vv)
            merged[k] = m
            note(f"union-dict {path}[{k}]: keys {len(ra)}+{len(rb)} -> {len(m)}")
    # take-new the non-ledger top-level fields by ts
    ka, va = find_ts(da); kb, vb = find_ts(db)
    if va is not None and vb is not None and str(vb) > str(va):
        for k, v in db.items():
            if k not in ledger_keys:
                merged[k] = v
        note(f"state-fields take-new {path}: theirs ts={vb} newer than ours {va}")
    else:
        note(f"state-fields keep-ours {path}: ts {va} >= {vb}")
    out = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
    json.loads(out.decode("utf-8"))  # parse-validate (r185)
    write_bytes(path, out)
    return True

def resolve_memory_union(path):
    a = stage_blob(path, 2).decode("utf-8-sig").splitlines()
    b = stage_blob(path, 3).decode("utf-8-sig").splitlines()
    setA = set(a)
    only_b = [ln for ln in b if ln not in setA]
    if not only_b:
        note(f"memory-union {path}: theirs subset of ours, keep ours")
        write_bytes(path, ("\r\n".join(a) + ("\r\n" if a else "")).encode("utf-8"))
        return True
    # insert theirs-only lines at position right after their last shared anchor in ours
    out = list(a)
    inserted = 0
    for ln in only_b:
        # find last shared line preceding this line in theirs, locate it in ours
        idx_b = b.index(ln)
        anchor = None
        for j in range(idx_b - 1, -1, -1):
            if b[j] in setA and b[j] != "":
                anchor = b[j]
                break
        if anchor is not None:
            pos = len(out) - 1 - out[::-1].index(anchor)
            out.insert(pos + 1, ln)
        else:
            out.insert(0, ln)
        inserted += 1
    note(f"memory-union {path}: inserted {inserted} theirs-only lines (zero loss, ours order base)")
    write_bytes(path, ("\r\n".join(out) + "\r\n").encode("utf-8"))
    return True

def resolve_js_wrapper(path):
    """dashboard_status.js: strip `window.DASH_DATA = ` wrapper, compare inner ts vs json twin's chosen side, take whole bytes (R209)."""
    a, b = stage_blob(path, 2), stage_blob(path, 3)
    def inner(blob):
        s = blob.decode("utf-8-sig").strip()
        assert s.startswith("window.DASH_DATA =") and s.endswith(";"), f"wrapper format drift in {path}"
        return json.loads(s[len("window.DASH_DATA ="):].rsplit(";", 1)[0])
    da, db = inner(a), inner(b)
    ka, va = find_ts(da); kb, vb = find_ts(db)
    if va is None or vb is None:
        note(f"FAIL-CLOSED {path}: no ts anchor in wrapper payload")
        return False
    chosen = a if str(va) >= str(vb) else b
    write_bytes(path, chosen)
    note(f"js-wrapper {path}: take {'ours' if chosen is a else 'theirs'} ts={max(str(va),str(vb))}")
    return True

fails = []

def need(ok, path):
    if not ok:
        fails.append(path)

# --- current-wave UU set filter (r473: re-probe direction each wave; only resolve what's conflicted now)
def current_uu():
    r = subprocess.run(["git", "-C", REPO, "status", "--porcelain"], capture_output=True)
    out = []
    for ln in r.stdout.decode("utf-8").splitlines():
        if ln[:2] in ("UU", "AA", "DU", "UD"):
            out.append(ln[3:].strip().strip('"'))
    return set(out)

UU_NOW = current_uu()
note(f"wave UU set: {sorted(UU_NOW)}")

def guarded(fn, *args):
    """Only run recipe if the path is currently conflicted; else report already-clean."""
    path = args[0] if isinstance(args[0], str) else args[1]
    if path not in UU_NOW:
        note(f"skip {path}: not in current UU set (auto-merged or untouched)")
        return True
    return fn(*args)

# 1) memory-union
need(guarded(resolve_memory_union, "CODELY.md"), "CODELY.md")

# 2) rolling-ledger faces
need(guarded(resolve_rolling_ledger, "results/compute_audit.json", ["history", "launches", "runs"]),
     "results/compute_audit.json")
need(guarded(resolve_rolling_ledger, "results/regime_state.json", ["history", "transitions", "launches"]),
     "results/regime_state.json")

# 3) js-wrapper snapshot
def resolve_dashboard_pair():
    """dashboard_status.{js,json}: ts lives in meta sub-dict (build_status.py writer).
    Decide by meta ts; take whole bytes of that side for BOTH files (R209 wrapper safety)."""
    ja, jb = loadj(stage_blob("results/dashboard_status.json", 2)), loadj(stage_blob("results/dashboard_status.json", 3))
    ma, mb = ja.get("meta", {}), jb.get("meta", {})
    va, vb = None, None
    for k in TS_KEYS:
        if isinstance(ma.get(k), (str, int, float)):
            va = str(ma[k]); break
    for k in TS_KEYS:
        if isinstance(mb.get(k), (str, int, float)):
            vb = str(mb[k]); break
    if va is None or vb is None:
        note(f"FAIL-CLOSED dashboard_status: meta ts missing ours={va} theirs={vb}")
        return False
    src = 2 if va >= vb else 3
    write_bytes("results/dashboard_status.json", stage_blob("results/dashboard_status.json", src))
    write_bytes("results/dashboard_status.js", stage_blob("results/dashboard_status.js", src))
    note(f"dashboard_status pair: take side :{src} (ours meta ts={va}, theirs meta ts={vb})")
    return True

if not ({"results/dashboard_status.js", "results/dashboard_status.json"} & UU_NOW):
    note("skip dashboard pair: not in current UU set")
else:
    need(resolve_dashboard_pair(), "results/dashboard_status.*")

# 4) plain snapshots (take-new by ts)
for p in ["results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json",
          "results/lhb_update_status.json",
          "results/token_usage.json", "results/update_status.json",
          "results/_attrition_guard_scan.json"]:
    need(guarded(resolve_take_new, p), p)

# 5) UNKNOWN manual classification (fail-closed): derived regen faces -> take-new by ts
#    daily_report twin (json decides, md follows)
need(guarded(resolve_json_twin_by_ts, "docs/daily_report/REPORT-2026-09-30.json",
             "docs/daily_report/REPORT-2026-09-30.md"), "docs/daily_report/REPORT-2026-09-30.*")
#    live_usage twins (day-stamped + latest aliases)
for jp, mp in [("docs/live_usage/LIVE-2026-09-30.json", "docs/live_usage/LIVE-2026-09-30.md"),
               ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md")]:
    need(guarded(resolve_json_twin_by_ts, jp, mp), jp)
#    scorecard derived faces (strategy_scorecard.py re-derives whole doc each round)
for p in ["results/scorecard_v1.json", "results/strategy_scorecard.json",
          "results/prospect_promotion/_summary.json"]:
    need(guarded(resolve_take_new, p), p)

# guard: any current-wave UU file outside the known recipe set -> fail-closed
known = set(["CODELY.md", "results/compute_audit.json", "results/regime_state.json",
             "results/dashboard_status.js", "results/dashboard_status.json",
             "results/_attrition_guard_scan.json",
             "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
             "results/lhb_update_status.json", "results/token_usage.json", "results/update_status.json",
             "docs/daily_report/REPORT-2026-09-30.json", "docs/daily_report/REPORT-2026-09-30.md",
             "docs/live_usage/LIVE-2026-09-30.json", "docs/live_usage/LIVE-2026-09-30.md",
             "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
             "results/scorecard_v1.json", "results/strategy_scorecard.json",
             "results/prospect_promotion/_summary.json"])
unhandled = UU_NOW - known
if unhandled:
    note(f"FAIL-CLOSED unhandled UU files: {sorted(unhandled)}")
    fails.extend(sorted(unhandled))

print("\n=== SUMMARY ===")
if fails:
    print("FAILED:", fails)
    sys.exit(2)
print("ALL RESOLVED OK; now git add resolved paths then rebase --continue")
