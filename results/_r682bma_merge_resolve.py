# -*- coding: utf-8 -*-
"""r682 bm-a merge resolver: 19 UU faces.
17 snapshot-regen faces -> ts-freshness newer-wins (r440 two-bucket law;
host=bm-a faces included -- ours are the freshest host writes 15:04-15:06);
token_usage.json -> per-key union on machines entries (r456/r466 law,
side_pick>0 asserted, zero-hit falls back to whole-face ts freshness);
CODELY.md -> block-level union (r675 heal law: MERGE_HEAD verbatim base +
HEAD-only lines appended in order, origin structure-row count preserved,
appended-line count==1 asserted);
runnable_pool.json -> theirs VERIFIED per-face (r474: only 3 trio shard
owner_since differ, all newer on origin 15:00:12 vs 14:50:12; delta receipt
results/_r682bma_pool_delta.py).
Both sides via git show HEAD:<p> / MERGE_HEAD:<p> raw bytes (r657 law:
add wipes :2:/:3: -- never re-stage from index stages)."""
import json, subprocess, sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

TS_KEYS = ["ts", "generated", "generated_at", "updated_at", "updated", "_ts",
           "timestamp", "date", "asof", "run_ts"]

def ts_of(obj):
    if isinstance(obj, dict):
        for k in TS_KEYS:
            if k in obj:
                return str(obj[k])
        for v in obj.values():
            t = ts_of(v)
            if t:
                return t
    return None

SNAP = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
]
UNION = ["results/token_usage.json"]
CODELY = "CODELY.md"
POOL = "results/runnable_pool.json"
MINE_LINE_KEY = "275_004..276_500"   # r682 pit line unique anchor

def pick_fresh(path):
    ours, theirs = show("HEAD", path), show("MERGE_HEAD", path)
    if ours is None:
        return "theirs", theirs
    if theirs is None:
        return "ours", ours
    to, tt = None, None
    if path.endswith(".json"):
        try:
            to = ts_of(json.loads(ours.decode("utf-8", "replace")))
            tt = ts_of(json.loads(theirs.decode("utf-8", "replace")))
        except Exception:
            pass
    if path.endswith(".md") or path.endswith(".js") or not to:
        for blob, which in ((ours, "o"), (theirs, "t")):
            head = blob.decode("utf-8", "replace")[:800]
            m = re.search(r"20\d\d-\d\d-\d\d[T ]\d\d:\d\d(:\d\d)?", head)
            if which == "o" and not to:
                to = m.group(0) if m else None
            elif which == "t" and not tt:
                tt = m.group(0) if m else None
    if to and tt:
        winner = "ours" if to >= tt else "theirs"
    elif to:
        winner = "ours"
    elif tt:
        winner = "theirs"
    else:
        winner = "ours"
    return winner, ours if winner == "ours" else theirs

def union_token(path):
    ours, theirs = show("HEAD", path), show("MERGE_HEAD", path)
    jo = json.loads(ours.decode("utf-8", "replace"))
    jt = json.loads(theirs.decode("utf-8", "replace"))
    side_pick = 0
    out = {}
    keys = set(jo) | set(jt)
    for k in keys:
        vo, vt = jo.get(k), jt.get(k)
        if k == "machines" and isinstance(vo, dict) and isinstance(vt, dict):
            m = {}
            for mk in set(vo) | set(vt):
                o, t = vo.get(mk), vt.get(mk)
                if o is not None and t is not None:
                    tso, tst = ts_of(o), ts_of(t)
                    if tso and tst and tst > tso:
                        m[mk] = t
                    else:
                        m[mk] = o
                    side_pick += 1
                else:
                    m[mk] = o if o is not None else t
                    side_pick += 1
            out[k] = m
        elif vo is not None and vt is not None:
            tso, tst = ts_of(vo), ts_of(vt)
            out[k] = vt if (tso and tst and tst > tso) else vo
            side_pick += 1
        else:
            out[k] = vo if vo is not None else vt
    if side_pick == 0:
        to, tt = ts_of(jo), ts_of(jt)
        winner = "ours" if (to and (not tt or to >= tt)) else "theirs"
        return winner, ours if winner == "ours" else theirs, 0
    return "union", json.dumps(out, ensure_ascii=False, indent=1).encode("utf-8"), side_pick

def union_codely(path):
    """r675 heal law: MERGE_HEAD verbatim base + HEAD-only lines appended in
    order; origin-side structure preserved (line count >= origin's); my new
    entry present exactly once."""
    ours, theirs = show("HEAD", path), show("MERGE_HEAD", path)
    ot = ours.decode("utf-8", "replace")
    tt = theirs.decode("utf-8", "replace")
    ol = ot.split("\n")
    tl = tt.split("\n")
    if MINE_LINE_KEY in tt:
        return "theirs-already", theirs
    mine_extra = [ln for ln in ol if ln not in tl]
    # keep ONLY lines that look like whole pit entries (start with "- [2026-") --
    # never re-append structural rows (r675 collapse law)
    mine_extra = [ln for ln in mine_extra if ln.startswith("- [2026-")]
    assert len(mine_extra) == 1, f"HEAD-only pit lines != 1: {len(mine_extra)}: {mine_extra[:2]}"
    # EOL convention from theirs
    eol = "\r\n" if tt.count("\r\n") * 2 > tt.count("\n") else "\n"
    base = tt
    if not base.endswith(eol):
        base += eol
    joined = base + mine_extra[0] + eol
    blob = joined.encode("utf-8")
    # post asserts
    jt2 = blob.decode("utf-8", "replace")
    assert jt2.count(MINE_LINE_KEY) == 1, "my pit line count != 1 after union"
    assert len(jt2.split("\n")) >= len(tl), "origin-side structure rows shrank"
    return "union-append-1", blob

report = {"resolved": [], "union_side_pick": None, "codely": None}
for p in SNAP:
    w, blob = pick_fresh(p)
    with open(os.path.join(REPO, p), "wb") as f:
        f.write(blob)
    report["resolved"].append([p, w])
for p in UNION:
    w, blob, sp = union_token(p)
    with open(os.path.join(REPO, p), "wb") as f:
        f.write(blob)
    report["union_side_pick"] = sp
    report["resolved"].append([p, w])
w, blob = union_codely(CODELY)
with open(os.path.join(REPO, CODELY), "wb") as f:
    f.write(blob)
report["codely"] = w
report["resolved"].append([CODELY, w])
# pool: theirs per r474 (delta verified: 3 trio owner_since faces, all newer
# on origin; receipt results/_r682bma_pool_delta.py in this commit)
blob = show("MERGE_HEAD", POOL)
with open(os.path.join(REPO, POOL), "wb") as f:
    f.write(blob)
report["resolved"].append([POOL, "theirs-verified-per-face (r474)"])

# marker check before add (r657 law + r644: content check, not rc)
bad = []
for p in SNAP + UNION + [CODELY, POOL]:
    b = open(os.path.join(REPO, p), "rb").read()
    for ln in b.split(b"\n"):
        if ln.startswith(b"<<<<<<<") or ln.startswith(b">>>>>>>"):
            bad.append(p)
            break
if bad:
    print("MARKER_REMAIN", bad)
    sys.exit(1)
with open(os.path.join(REPO, "results", "_r682bma_merge_resolve.json"), "w",
          encoding="utf-8", newline="\n") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("RESOLVE_DONE", len(report["resolved"]), "faces; codely:", report["codely"],
      "; union_side_pick:", report["union_side_pick"])
for p, w in report["resolved"]:
    print(f"  {w:>10}  {p}")
