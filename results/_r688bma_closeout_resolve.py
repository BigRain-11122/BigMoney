"""r688 bm-a closeout UU resolver: 14 S6 regenerable faces, per-face ts newer-wins (r440/r440-extend).

All 14 faces are regenerable snapshot faces (S6 chain outputs) -- no append-only
bookkeeping among them. Per-face freshness probe: extract 'ts'/'generated' field
from both sides via git show HEAD:/MERGE_HEAD: raw bytes (r657 law 2), newer wins.
"""
import json
import re
import subprocess

FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]


def side_bytes(ref, path):
    r = subprocess.run(["git", "show", ref + ":" + path], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def ts_of(blob):
    if blob is None:
        return ""
    # try json ts fields
    try:
        d = json.loads(blob.decode("utf-8"))
        for k in ("ts", "generated", "generated_at", "asof", "cutoff", "written_at"):
            if isinstance(d, dict) and k in d:
                return str(d[k])
    except Exception:
        pass
    # md/text: first ts-looking string
    m = re.search(rb"20\d\d-\d\d-\d\d[T ]\d\d:\d\d(:\d\d)?", blob)
    return m.group(0).decode() if m else ""


resolved = 0
for path in FACES:
    ours = side_bytes("HEAD", path)
    theirs = side_bytes("MERGE_HEAD", path)
    if ours is None or theirs is None:
        print("SKIP (missing side):", path)
        continue
    t_ours, t_theirs = ts_of(ours), ts_of(theirs)
    # normalize ts forms for compare (T vs space, per r461 ts_norm law)
    def norm(t):
        t = t.strip().replace("T", " ")
        return t[:19] if len(t) >= 19 else t
    n_o, n_t = norm(t_ours), norm(t_theirs)
    if n_o >= n_t:
        winner, side = ours, "ours"
    else:
        winner, theirs, side = theirs, None, "theirs"
    with open(path, "wb") as f:
        f.write(winner)
    # verify no markers and parseable if json
    b = open(path, "rb").read()
    assert b.count(b"<<<<<<<") == 0 and b.count(b">>>>>>>") == 0
    if path.endswith(".json"):
        json.loads(b.decode("utf-8"))
    print("RESOLVED %s -> %s (ours=%s theirs=%s)" % (path, side, n_o, n_t))
    resolved += 1

print("resolved:", resolved, "of", len(FACES))
