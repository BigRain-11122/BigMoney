# -*- coding: utf-8 -*-
# r675 bm-b merge resolver: 33 UU faces (push-race vs bm-c r477-478 + bm-a r680 wave).
# Lineage: r674 resolver verbatim-adapted + 3 new categories this window:
#   CODELY block-union (base=MERGE_HEAD full text + HEAD-only lines appended,
#     whole-file line-dedup FORBIDDEN per r675 bm-a collapse pit -- structural
#     blank lines preserved), x2_watch_log jsonl line-union (superset-or-union,
#     dual containment zero-loss assert), 21 snapshot faces + 5 twins.
# Laws kept: HEAD:/MERGE_HEAD: raw-byte side probes (r657: add wipes :2:/:3:),
# deep-ts probe r100 key-normalize + R350 shape, twins follow json same-side,
# tie->HEAD r140, tool faces via scripts/merge_lane_views.py single-source,
# probe-miss default-ours + explicit dual-face print (r656 law), marker
# content-check at line start (r453/r644), parse-verify, EOL probe r657.
import io
import json
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              errors="replace")
CREATE = 0x08000000


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True,
                       creationflags=CREATE)
    return p.returncode, p.stdout, p.stderr


def side_blob(side, path):
    rc, out, _ = git("show", "%s:%s" % (side, path))
    return out if rc == 0 else None


WALL_NORM = {k.replace("_", "").replace("-", "").lower() for k in
             ("ts", "generated", "generated_at", "updated", "updated_at",
              "scan_time", "time", "written_at", "state_updated")}
DATE_NORM = {"asof", "asofdate", "asofutc", "cutoff", "date", "cutoffdate"}
WALL_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")
DATE_RE = re.compile(r"20\d{2}-\d{2}-\d{2}$")


def _collect(obj, out, path="", depth=0):
    if depth > 6:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).replace("_", "").replace("-", "").lower()
            if isinstance(v, str):
                if WALL_RE.match(v):
                    out.append((1 if nk in WALL_NORM else 2, v, path + "/" + k))
                elif DATE_RE.fullmatch(v) and nk in DATE_NORM:
                    out.append((3, v, path + "/" + k))
            else:
                _collect(v, out, path + "/" + str(k), depth + 1)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:20]):
            _collect(v, out, path + "[%d]" % i, depth + 1)


def find_ts_json(blob):
    try:
        doc = json.loads(blob.decode("utf-8", "replace"))
    except Exception:
        return None, "parse-fail"
    c = []
    _collect(doc, c)
    if not c:
        return None, "no-ts"
    tier = min(t[0] for t in c)
    best = max((t for t in c if t[0] == tier), key=lambda t: t[1])
    return best[1], "t%d %s" % (tier, best[2])


TOOL_FACES = [
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/token_usage.json",
]
CODELY_FACE = "CODELY.md"
JSONL_UNION = ["results/x2_watch_log.jsonl"]
SNAP_JSON = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
]
TWIN_OF = {
    "docs/daily_report/REPORT-2026-10-04.md": "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md": "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}

fails = 0

# --- 0) CODELY.md block-union: MERGE_HEAD full text + HEAD-only lines appended ---
rc, base_b, err = git("show", "MERGE_HEAD:CODELY.md")
rc2, mine_b, err2 = git("show", "HEAD:CODELY.md")
if rc == 0 and rc2 == 0:
    base_txt = base_b.decode("utf-8", "replace")
    mine_txt = mine_b.decode("utf-8", "replace")
    base_lines = base_txt.split("\n")
    mine_lines = mine_txt.split("\n")
    base_set = set(base_lines)
    increment = [l for l in mine_lines if l not in base_set]
    if increment:
        produced = base_txt
        if not produced.endswith("\n"):
            produced += "\n"
        produced += "\n".join(increment)
        if not produced.endswith("\n"):
            produced += "\n"
    else:
        produced = base_txt
    prod_lines = produced.split("\n")
    # anti-collapse + superset asserts (r675 bm-a law)
    assert len(prod_lines) >= len(base_lines), "CODELY collapse: base lines lost"
    assert set(base_lines) <= set(prod_lines), "CODELY base rows lost"
    assert all(l in set(prod_lines) for l in increment), "CODELY increment lost"
    with io.open("CODELY.md", "w", encoding="utf-8", newline="") as f:
        f.write(produced)
    rc3, _, err3 = git("add", "CODELY.md")
    print("[codely] block-union: base %d lines + increment %d lines -> %d lines rc=%d"
          % (len(base_lines), len(increment), len(prod_lines), rc3))
    if rc3 != 0:
        print("  add fail:", err3.decode("utf-8", "replace")[:150])
        fails += 1
else:
    print("[codely] side probe fail", rc, rc2)
    fails += 1

# --- 1) jsonl line-union (superset-or-union + dual containment) ---
for f in JSONL_UNION:
    b = side_blob("MERGE_HEAD", f)
    m = side_blob("HEAD", f)
    if b is None or m is None:
        print("[jsonl] %s side probe fail base=%s mine=%s" % (f, b is not None, m is not None))
        fails += 1
        continue
    bl = [l for l in b.decode("utf-8", "replace").split("\n") if l.strip()]
    ml = [l for l in m.decode("utf-8", "replace").split("\n") if l.strip()]
    bs, ms = set(bl), set(ml)
    if bs <= ms:
        out_lines, mode = ml, "ours-superset"
    elif ms <= bs:
        out_lines, mode = bl, "theirs-superset"
    else:
        out_lines = bl + [l for l in ml if l not in bs]
        mode = "union +%d ours-only" % len([l for l in ml if l not in bs])
    prod = "\n".join(out_lines) + "\n"
    ps = set(out_lines)
    assert bs <= ps and ms <= ps, "jsonl containment FAIL %s" % f
    with io.open(f, "w", encoding="utf-8", newline="") as fh:
        fh.write(prod)
    rc4, _, err4 = git("add", f)
    print("[jsonl] %s %s -> %d lines rc=%d" % (f, mode, len(out_lines), rc4))
    if rc4 != 0:
        fails += 1

# --- 2) tool faces: single-source recipes ---
for f in TOOL_FACES:
    r = subprocess.run([sys.executable, "scripts/merge_lane_views.py",
                        "resolve", f], capture_output=True, creationflags=CREATE)
    out = ((r.stdout or b"") + (r.stderr or b"")).decode("utf-8", "replace")
    tail = " ; ".join([l for l in out.strip().splitlines() if l.strip()][-2:])
    print("[tool] %s rc=%d | %s" % (f, r.returncode, tail[:220]))
    if r.returncode != 0:
        fails += 1
        continue
    rc5, _, err5 = git("add", f)
    if rc5 != 0:
        print("  add fail:", err5.decode("utf-8", "replace")[:200])
        fails += 1

verdicts = {}


def take_side(f, side, why):
    rc6, _, err6 = git("checkout", "--" + side, "--", f)
    if rc6 != 0:
        print("[snap] %s checkout fail: %s" % (f, err6.decode("utf-8", "replace")[:150]))
        return False
    rc7, _, err7 = git("add", f)
    if rc7 != 0:
        print("[snap] %s add fail: %s" % (f, err7.decode("utf-8", "replace")[:150]))
        return False
    verdicts[f] = side
    print("[snap] %s -> %s | %s" % (f, side, why))
    return True


# --- 3) snapshot json faces: deep-ts probe on HEAD/MERGE_HEAD raw bytes ---
for f in SNAP_JSON:
    ours, theirs = side_blob("HEAD", f), side_blob("MERGE_HEAD", f)
    if theirs is None and ours is None:
        print("[snap] %s NO SIDES" % f)
        fails += 1
        continue
    if theirs is None:
        if not take_side(f, "ours", "theirs missing"):
            fails += 1
        continue
    if ours is None:
        if not take_side(f, "theirs", "ours missing"):
            fails += 1
        continue
    ts_o, why_o = find_ts_json(ours)
    ts_t, why_t = find_ts_json(theirs)
    if ts_o and ts_t:
        side = "ours" if ts_o >= ts_t else "theirs"
        why = "ours %s (%s) vs theirs %s (%s)%s" % (ts_o, why_o, ts_t, why_t,
                                                    " tie->HEAD" if ts_o == ts_t else "")
    else:
        side = "ours"  # r652 lineage default, dual-face print below (r656 law)
        why = "probe-miss ours=%s(%s) theirs=%s(%s) -> default ours" % (ts_o, why_o, ts_t, why_t)
        print("  !! PROBE-MISS on %s -- default-ours taken; dual sides retained in this print" % f)
    if not take_side(f, side, why):
        fails += 1

# --- 4) twins follow their json twin (same-side law) ---
for f, twin in TWIN_OF.items():
    side = verdicts.get(twin)
    if side is None:
        print("[twin] %s twin %s has no verdict -- SKIPPED" % (f, twin))
        fails += 1
        continue
    if not take_side(f, side, "twin-follow %s" % twin):
        fails += 1

# --- 5) marker check on ALL staged (line-start content check r453/r644) + parse-verify ---
rc8, out8, _ = git("grep", "-l", "-E", "^(<{7} |={7}$|>{7} )", "--cached")
if rc8 == 0:
    print("MARKER RESIDUAL in staged:", out8.decode("utf-8", "replace"))
    fails += 1
elif rc8 == 1:
    print("marker_residual: NONE (all staged)")
else:
    print("grep rc=%d" % rc8)

bad = 0
for f in TOOL_FACES + JSONL_UNION + SNAP_JSON:
    if not f.endswith((".json", ".jsonl")):
        continue
    rc9, txt, _ = git("show", ":%s" % f)
    if rc9 != 0:
        print("stage0 miss", f)
        bad += 1
        continue
    try:
        json.loads(txt)
    except Exception as e:
        print("PARSE-FAIL", f, repr(e)[:120])
        bad += 1
print("resolver done: fails=%d parse_fail=%d snap_verdicts=%d"
      % (fails, bad, len(verdicts)))
sys.exit(1 if (fails or bad) else 0)
