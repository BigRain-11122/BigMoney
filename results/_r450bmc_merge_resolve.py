"""r450 bm-c merge UU resolver (r449 recipe, extended: +daily_scorecard.{html,json};
UU-set completeness assertion before resolving -- only UU faces are touched,
auto-merged faces left alone). Categories:
  A (regen faces): embedded-ts compare ours(:2) vs theirs(:3), winner verbatim.
  B (compute_audit.json): history cross-machine union (dedupe identical rows,
    ts-sorted) + latest = newer-ts side.
  C (token_usage.json): per-machine union inside "machines", top-level = ours.
Zero-marker assertion after all writes (r644 content law) + JSON reparse.
"""
import json
import os
import re
import subprocess

RB = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREATE = 0x08000000

REGEN = [
    ("docs/daily_report/REPORT-2026-10-04.json", True),
    ("docs/daily_report/REPORT-2026-10-04.md", False),
    ("docs/live_usage/LIVE-2026-10-04.json", True),
    ("docs/live_usage/LIVE-2026-10-04.md", False),
    ("docs/live_usage/LIVE-latest.json", True),
    ("docs/live_usage/LIVE-latest.md", False),
    ("results/_attrition_guard_scan.json", True),
    ("results/daily_scorecard.html", False),
    ("results/daily_scorecard.json", True),
    ("results/dashboard_status.js", False),
    ("results/dashboard_status.json", True),
    ("results/fundamental_b_layer_filter.json", True),
    ("results/futures_update_status.json", True),
    ("results/lhb_update_status.json", True),
    ("results/prospect_promotion/_summary.json", True),
    ("results/regime_state.json", True),
    ("results/scorecard_v1.json", True),
    ("results/strategy_scorecard.json", True),
    ("results/update_status.json", True),
]
UNION_CA = "results/compute_audit.json"
UNION_TU = "results/token_usage.json"
KNOWN = set(p for p, _ in REGEN) | {UNION_CA, UNION_TU}


def git(*a):
    p = subprocess.run(["git", "-C", RB] + list(a), capture_output=True, creationflags=CREATE)
    if p.returncode != 0:
        raise RuntimeError("git %s rc=%d :: %s" % (" ".join(a), p.returncode, p.stdout + p.stderr))
    return p.stdout


uu = [l.strip() for l in git("diff", "--name-only", "--diff-filter=U").decode("utf-8").splitlines() if l.strip()]
uu_set = set(uu)
print("UU-FACES=%d" % len(uu_set))
unknown = uu_set - KNOWN
assert not unknown, "UNKNOWN UU faces (must classify first): %r" % sorted(unknown)


def blob(rev, path):
    return git("show", "%s:%s" % (rev, path))


def write(path, data):
    full = os.path.join(RB, path.replace("/", os.sep))
    with open(full, "wb") as fh:
        fh.write(data)


def face_ts(raw, is_json):
    if is_json:
        try:
            d = json.loads(raw.decode("utf-8"))
            if isinstance(d, dict):
                for k in ("ts", "generated", "asof", "updated_at", "updated", "last_run", "time", "written_at"):
                    v = d.get(k)
                    if isinstance(v, str) and "2026-" in v:
                        return v
        except Exception:
            pass
    m = re.search(rb"2026-10-\d\dT\d\d:\d\d:\d\d", raw) or re.search(rb"2026-10-\d\d \d\d:\d\d:\d\d", raw)
    return m.group(0).decode("ascii") if m else ""


# --- Category A: take-new-by-ts (UU regen faces only)
for path, is_json in REGEN:
    if path not in uu_set:
        continue
    o, t = blob(":2", path), blob(":3", path)
    ts_o, ts_t = face_ts(o, is_json), face_ts(t, is_json)
    if ts_o >= ts_t:
        win, side = o, "ours"
    else:
        win, side = t, "theirs"
    write(path, win)
    git("add", "--", path)
    print("TAKE-NEW %s side=%s ours_ts=%s theirs_ts=%s" % (path, side, ts_o or "?", ts_t or "?"))

# --- Category B: compute_audit.json union (if UU)
if UNION_CA in uu_set:
    ca_ours = json.loads(blob(":2", UNION_CA).decode("utf-8"))
    ca_theirs = json.loads(blob(":3", UNION_CA).decode("utf-8"))
    o_rows = ca_ours.get("history", [])
    t_rows = ca_theirs.get("history", [])
    seen = set()
    union = []
    for row in o_rows + t_rows:
        key = json.dumps(row, ensure_ascii=False, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        union.append(row)

    def row_ts(r):
        v = r.get("ts") if isinstance(r, dict) else None
        return v or ""

    union.sort(key=row_ts)
    ca_ours["history"] = union
    lo = ca_ours.get("latest") or {}
    lt = ca_theirs.get("latest") or {}
    if str(row_ts(lt) or "") > str(row_ts(lo) or ""):
        ca_ours["latest"] = lt
    write(UNION_CA, json.dumps(ca_ours, ensure_ascii=False, indent=1).encode("utf-8"))
    git("add", "--", UNION_CA)
    print("COMPUTE-AUDIT-UNION ours_rows=%d theirs_rows=%d union=%d" % (len(o_rows), len(t_rows), len(union)))

# --- Category C: token_usage.json per-machine union (if UU)
if UNION_TU in uu_set:
    tu_ours = json.loads(blob(":2", UNION_TU).decode("utf-8"))
    tu_theirs = json.loads(blob(":3", UNION_TU).decode("utf-8"))
    m_o = tu_ours.get("machines", {})
    m_t = tu_theirs.get("machines", {})
    merged = {}
    n_ours_taken = n_theirs_taken = 0
    for mid in set(m_o) | set(m_t):
        eo, et = m_o.get(mid), m_t.get(mid)
        if eo is None:
            merged[mid] = et
            n_theirs_taken += 1
            continue
        if et is None:
            merged[mid] = eo
            n_ours_taken += 1
            continue
        to_ = eo.get("generated") or eo.get("last_ts") or ""
        tt_ = et.get("generated") or et.get("last_ts") or ""
        if str(tt_) > str(to_):
            merged[mid] = et
            n_theirs_taken += 1
        else:
            merged[mid] = eo
            n_ours_taken += 1
    tu_ours["machines"] = merged
    write(UNION_TU, json.dumps(tu_ours, ensure_ascii=False, indent=1).encode("utf-8"))
    git("add", "--", UNION_TU)
    print("TOKEN-USAGE-PERMACHINE-UNION ours=%d theirs=%d machines=%d" % (n_ours_taken, n_theirs_taken, len(merged)))

# --- zero-marker + JSON reparse on all touched faces (r644 content law)
MARKERS = (b"<<<<<<< HEAD", b">>>>>>> origin/main", b">>>>>>>", b"|||||||")
touched = [p for p, _ in REGEN if p in uu_set] + [p for p in (UNION_CA, UNION_TU) if p in uu_set]
bad = []
for path in touched:
    data = open(os.path.join(RB, path.replace("/", os.sep)), "rb").read()
    for m in MARKERS:
        if m in data:
            bad.append((path, m))
assert not bad, "marker residue: %r" % bad
for path, is_json in REGEN:
    if path in uu_set and is_json:
        json.loads(open(os.path.join(RB, path.replace("/", os.sep)), "rb").read().decode("utf-8"))
for path in (UNION_CA, UNION_TU):
    if path in uu_set:
        json.loads(open(os.path.join(RB, path.replace("/", os.sep)), "rb").read().decode("utf-8"))
print("ZERO-MARKER + JSON-REPARSE ALL PASS (%d touched of %d UU)" % (len(touched), len(uu_set)))
