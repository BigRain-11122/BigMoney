# -*- coding: utf-8 -*-
"""r493 rebase-collision resolver (bm-c r290 x bm-a r493 closeout, same-window
S6 shared faces) -- bigmoney-conflict-resolve skill recipes, manual classes:
  - snapshot take-new via hardened deep-ts probe (r311 deep-scan / r100 value
    shape ^20\\d{2}- + time-of-day / R350 no key-exclude lists)
  - twin-regen-md: json side picks by ts, md twin byte-copied SAME side (r329)
  - js-wrapper-snapshot: whole-byte take-side (R209)
  - memory-union: merge-base prefix assert + suffix direct concat (R208/r311)
Stage law (rebase, r351): :2: = origin/ours (bm-c), :3: = ours replayed (bm-a).
"""
import json
import re
import subprocess
import sys
import io

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def blob(stage, path):
    out = subprocess.run(["git", "show", ":%d:%s" % (stage, path)],
                         capture_output=True)
    if out.returncode != 0:
        return None
    return out.stdout


def deep_ts(obj, best=""):
    """Recursively find the max wall-clock ts value (must carry time-of-day)."""
    if isinstance(obj, dict):
        for v in obj.values():
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    elif isinstance(obj, str) and TS_RE.match(obj):
        if obj > best:
            best = obj
    return best


def pick_newer_json(path):
    a, b = blob(2, path), blob(3, path)
    if a is None and b is None:
        return None, None
    if a is None:
        return 3, b
    if b is None:
        return 2, a
    ja = json.loads(a.decode("utf-8"))
    jb = json.loads(b.decode("utf-8"))
    ta, tb = deep_ts(ja), deep_ts(jb)
    if ta == tb:
        side = 2  # same-second tie -> HEAD/origin side (r140)
        return side, a
    side = 2 if ta > tb else 3
    return side, (a if side == 2 else b)


def resolve_snapshot(path):
    side, data = pick_newer_json(path)
    if data is None:
        print("SKIP (no blobs):", path)
        return None
    with io.open(path, "wb") as fh:
        fh.write(data)
    json.loads(io.open(path, encoding="utf-8").read())  # parse-verify
    print("snapshot take-new side=%d ts-picked: %s" % (side, path))
    return side


def resolve_twin(json_path, md_paths):
    side, data = pick_newer_json(json_path)
    if data is None:
        print("SKIP twin:", json_path)
        return
    with io.open(json_path, "wb") as fh:
        fh.write(data)
    for md in md_paths:
        mdata = blob(side, md)
        if mdata is None:
            print("  md blob missing side %d: %s" % (side, md))
            continue
        with io.open(md, "wb") as fh:
            fh.write(mdata)
        print("  twin same-side %d byte-copy: %s" % (side, md))


def resolve_js_takeside(js_path, json_path, side):
    data = blob(side, js_path)
    if data is None:
        print("SKIP js:", js_path)
        return
    with io.open(js_path, "wb") as fh:
        fh.write(data)
    print("js-wrapper whole-byte side=%d: %s" % (side, js_path))


def resolve_memory(path):
    base = blob(1, path)
    a = blob(2, path)
    b = blob(3, path)
    if base is None or a is None or b is None:
        print("SKIP memory (missing blob):", path)
        return
    ba, bb, bbase = a.decode("utf-8"), b.decode("utf-8"), base.decode("utf-8")
    if not ba.startswith(bbase):
        print("PREFIX-ASSERT FAIL (origin side in-place edit):", path)
        sys.exit(2)
    if not bb.startswith(bbase):
        print("PREFIX-ASSERT FAIL (local side in-place edit):", path)
        sys.exit(2)
    merged = bbase + ba[len(bbase):] + bb[len(bbase):]
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(merged)
    print("memory-union concat: %s (base %d + A %d + B %d = %d bytes)" % (
        path, len(bbase.encode("utf-8")), len(ba) - len(bbase),
        len(bb) - len(bbase), len(merged.encode("utf-8"))))


def main():
    # 1) snapshot faces (deep-ts take-new)
    for p in ("results/fundamental_b_layer_filter.json",
              "results/strategy_scorecard.json",
              "results/scorecard_v1.json",
              "results/prospect_promotion/_summary.json",
              "results/_attrition_guard_scan.json"):
        resolve_snapshot(p)

    # 2) daily_scorecard.html: r378 single-writer host=bm-a -> local side (3)
    html = blob(3, "results/daily_scorecard.html")
    if html is not None:
        with io.open("results/daily_scorecard.html", "wb") as fh:
            fh.write(html)
        print("daily_scorecard.html host-guard take side=3 (bm-a writer)")

    # 3) REPORT twin (json picks, md same-side byte copy)
    resolve_twin("docs/daily_report/REPORT-2026-09-30.json",
                 ["docs/daily_report/REPORT-2026-09-30.md"])

    # 4) LIVE twins (dated json picks, all others same-side)
    side, _ = pick_newer_json("docs/live_usage/LIVE-2026-09-30.json")
    resolve_twin("docs/live_usage/LIVE-2026-09-30.json",
                 ["docs/live_usage/LIVE-2026-09-30.md",
                  "docs/live_usage/LIVE-latest.json",
                  "docs/live_usage/LIVE-latest.md"])

    # 5) dashboard pair: json take-new, js whole-byte SAME side
    side2, _ = pick_newer_json("results/dashboard_status.json")
    side2 = resolve_snapshot("results/dashboard_status.json") or side2
    if side2 in (2, 3):
        resolve_js_takeside("results/dashboard_status.js",
                            "results/dashboard_status.json", side2)

    # 6) CODELY.md memory union
    resolve_memory("CODELY.md")


if __name__ == "__main__":
    main()
