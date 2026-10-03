"""r448 bm-c merge UU resolver (r446/r651 recipe categories, take-new-by-ts BOTH
directions honest compare).

Category A (12 regen faces): embedded-ts compare ours(:2) vs theirs(:3), winner
  blob verbatim -- expected ours 06:35-06:38 > bm-b r652 06:2x, but the code
  takes whichever is honestly newer.
Category B (compute_audit.json): history cross-machine union (dedupe identical
  rows, ts-sorted) + latest = newer-ts side.
Category C (token_usage.json): per-machine union inside "machines" (newer
  generated per machine), top-level scalars = ours.
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
    ("results/fundamental_b_layer_filter.json", True),
    ("results/futures_update_status.json", True),
    ("results/lhb_update_status.json", True),
    ("results/regime_state.json", True),
    ("results/update_status.json", True),
]


def blob(rev, path):
    p = subprocess.run(["git", "-C", RB, "show", "%s:%s" % (rev, path)],
                       capture_output=True, creationflags=CREATE)
    if p.returncode != 0:
        raise RuntimeError("blob %s:%s rc=%d" % (rev, path, p.returncode))
    return p.stdout


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


# --- Category A: take-new-by-ts
for path, is_json in REGEN:
    o, t = blob(":2", path), blob(":3", path)
    ts_o, ts_t = face_ts(o, is_json), face_ts(t, is_json)
    if ts_o >= ts_t:
        win, side = o, "ours"
    else:
        win, side = t, "theirs"
    write(path, win)
    print("TAKE-NEW %s side=%s ours_ts=%s theirs_ts=%s" % (path, side, ts_o or "?", ts_t or "?"))

# --- Category B: compute_audit.json union
ca_ours = json.loads(blob(":2", "results/compute_audit.json").decode("utf-8"))
ca_theirs = json.loads(blob(":3", "results/compute_audit.json").decode("utf-8"))
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
write("results/compute_audit.json", json.dumps(ca_ours, ensure_ascii=False, indent=1).encode("utf-8"))
print("COMPUTE-AUDIT-UNION ours_rows=%d theirs_rows=%d union=%d" % (len(o_rows), len(t_rows), len(union)))

# --- Category C: token_usage.json per-machine union
tu_ours = json.loads(blob(":2", "results/token_usage.json").decode("utf-8"))
tu_theirs = json.loads(blob(":3", "results/token_usage.json").decode("utf-8"))
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
write("results/token_usage.json", json.dumps(tu_ours, ensure_ascii=False, indent=1).encode("utf-8"))
print("TOKEN-USAGE-PERMACHINE-UNION ours=%d theirs=%d machines=%d" % (n_ours_taken, n_theirs_taken, len(merged)))

# --- zero-marker assertion + JSON reparse (r644 content law)
MARKERS = (b"<<<<<<< HEAD", b">>>>>>> origin/main", b"|||||||")
allfaces = [p for p, _ in REGEN] + ["results/compute_audit.json", "results/token_usage.json"]
bad = []
for path in allfaces:
    data = open(os.path.join(RB, path.replace("/", os.sep)), "rb").read()
    for m in MARKERS:
        if m in data:
            bad.append((path, m))
assert not bad, "marker residue: %r" % bad
for path, is_json in REGEN:
    if is_json:
        json.loads(open(os.path.join(RB, path.replace("/", os.sep)), "rb").read().decode("utf-8"))
for path in ("results/compute_audit.json", "results/token_usage.json"):
    json.loads(open(os.path.join(RB, path.replace("/", os.sep)), "rb").read().decode("utf-8"))
print("ZERO-MARKER + JSON-REPARSE ALL PASS (%d faces)" % len(allfaces))
