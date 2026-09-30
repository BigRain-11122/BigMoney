"""r492 rebase-conflict resolver (bm-a, push-rejection same-window fleet collision).

Faces: CODELY.md (memory-union, r327 entry-level law: origin did a mid-file
single-line insert -> tree = origin-side + replay appended suffix, byte-math
zero-loss) + snapshot/twin faces (daily_report REPORT pair, live_usage LIVE
pair x2, _attrition_guard_scan, fundamental_b_layer_filter) via deep-ts probe
take-new, twins take the SAME side (r327/r329 law).
All_FACES members were resolved beforehand by scripts/merge_lane_views.py
resolve (compute_audit / regime_state / update_status / token_usage /
lhb_update_status / futures_update_status) -- this script does NOT re-do them.
"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def blob(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"blob read fail: {spec}: {r.stderr.decode()[:200]}")
    return r.stdout


def deep_ts(obj, found):
    """Deep-scan for wall-clock ts strings (r311/D-09 law: nested layers, probe existence first)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and len(v) >= 19 and v[:2] == "20" and v[4] == "-":
                if ":" in v[10:] or "T" in v:  # looks like a full timestamp
                    found.append(v)
            deep_ts(v, found)
    elif isinstance(obj, list):
        for v in obj:
            deep_ts(v, found)


def pick_newer_json(path):
    """Take-new by deep ts probe on both staged blobs; returns chosen side ('origin'|'replay')."""
    o = json.loads(blob(":" + "2:" + path).decode("utf-8"))
    t = json.loads(blob(":" + "3:" + path).decode("utf-8"))
    fo, ft = [], []
    deep_ts(o, fo)
    deep_ts(t, ft)
    mo = max(fo) if fo else ""
    mt = max(ft) if ft else ""
    side = "replay" if mt >= mo else "origin"  # >= : same-second tie -> HEAD/replay side (r140)
    data = t if side == "replay" else o
    with open(path, "wb") as f:
        f.write(blob(":" + ("3" if side == "replay" else "2") + ":" + path))
    print(f"[{path}] origin-ts={mo} replay-ts={mt} -> take {side} (byte copy)")
    return side


def twin_md_from_json_side(md_path, side):
    """md twin copies the SAME side's blob bytes (r329: md is not JSON; no json.loads)."""
    stage = "3" if side == "replay" else "2"
    with open(md_path, "wb") as f:
        f.write(blob(":" + stage + ":" + md_path))
    print(f"[{md_path}] md twin <- {side} blob bytes (same-side law)")


def codely_union():
    """memory-union with r327 entry-level verification (origin inserted mid-file)."""
    base = blob(":1:CODELY.md").decode("utf-8")
    origin = blob(":2:CODELY.md").decode("utf-8")
    replay = blob(":3:CODELY.md").decode("utf-8")
    assert replay.startswith(base), "replay side must be base+suffix (pure append)"
    suffix = replay[len(base):]
    tree = origin + suffix
    # r327 entry-level bidirectional coverage: every replay/origin entry line present in tree
    for src, name in ((origin, "origin"), (replay, "replay")):
        for ln in src.splitlines():
            if ln.startswith("- [") and ln not in tree.splitlines():
                raise SystemExit(f"entry-loss guard: {name} line missing from tree: {ln[:80]}")
    with open("CODELY.md", "w", encoding="utf-8", newline="") as f:
        f.write(tree)
    b = len(base.encode()); oo = len(origin.encode()); s = len(suffix.encode()); tt = len(tree.encode())
    assert tt == oo + s, f"byte-math fail {tt} != {oo}+{s}"
    print(f"[CODELY.md] union: base {b} -> origin {oo} + replay-suffix {s} = tree {tt} bytes (zero loss)")


codely_union()
side = pick_newer_json("docs/daily_report/REPORT-2026-09-30.json")
twin_md_from_json_side("docs/daily_report/REPORT-2026-09-30.md", side)
side2 = pick_newer_json("docs/live_usage/LIVE-2026-09-30.json")
twin_md_from_json_side("docs/live_usage/LIVE-2026-09-30.md", side2)
side3 = pick_newer_json("docs/live_usage/LIVE-latest.json")
twin_md_from_json_side("docs/live_usage/LIVE-latest.md", side3)
pick_newer_json("results/_attrition_guard_scan.json")
pick_newer_json("results/fundamental_b_layer_filter.json")
print("resolver done: parse-verify all json faces")
for p in ("docs/daily_report/REPORT-2026-09-30.json", "docs/live_usage/LIVE-2026-09-30.json",
          "docs/live_usage/LIVE-latest.json", "results/_attrition_guard_scan.json",
          "results/fundamental_b_layer_filter.json"):
    json.load(open(p, encoding="utf-8"))
print("all parse-verified")
