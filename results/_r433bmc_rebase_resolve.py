# -*- coding: utf-8 -*-
"""r433 bm-c rebase conflict resolver (pick2 S6-faces vs origin push-storm).

Laws applied:
- r432 take-ours absorb precedent: origin side wins when same-generation or
  newer (verified, not blind);
- r630: never blind --skip / never marker-surgery when a whole-side take is
  the correct semantic -- these are same-day idempotent regen faces (daily
  report / live usage / audit+status snapshots), each side internally
  consistent -> whole-blob side take per face;
- S0 reland环 shared-pool check: runnable_pool.json / crash_fuse.json NOT in
  conflict set (verified in main()) -> no per-face max-merge needed here;
- every chosen side must parse (JSON faces) + carry zero conflict markers.

Side semantics during rebase: stage2 = ours = origin/base (bm-a 22:3x regen),
stage3 = theirs = this commit (bm-c 22:33-36 regen). Newer ts wins; tie or
missing ts -> origin side (r432 fallback). Receipt -> stdout + JSON file.
"""
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
MARKERS = ("<<<<<<<", "=======", ">>>>>>>")

CONFLICTS = [
    "docs/daily_report/REPORT-2026-10-03.json",
    "docs/daily_report/REPORT-2026-10-03.md",
    "docs/live_usage/LIVE-2026-10-03.json",
    "docs/live_usage/LIVE-2026-10-03.md",
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

TS_KEYS = ["ts", "generated_at", "generated", "updated_at", "updated",
           "written_at", "asof", "time", "timestamp", "datetime"]


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, cwd=REPO,
                       creationflags=CREATE)
    return p.returncode, p.stdout, p.stderr


def get_side(stage, path):
    rc, out, err = git("show", ":%d:%s" % (stage, path))
    if rc != 0:
        return None
    return out


def ts_of(obj):
    if not isinstance(obj, dict):
        return None
    best = None
    for k in TS_KEYS:
        v = obj.get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            best = max(best or 0, float(v))
        elif isinstance(v, str):
            m = re.match(r"(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2})", v)
            if m:
                s = m.group(1) + " " + m.group(2)
                best = max(best or "", s)
    return best


def cmp_ts(a, b):
    if a is None and b is None:
        return 0
    if a is None:
        return -1
    if b is None:
        return 1
    return (a > b) - (a < b)


def main():
    assert os.path.isdir(os.path.join(REPO, ".git", "rebase-merge")), "no rebase in progress"
    # S0 reland环 law: shared-pool faces must not be silently whole-replayed
    for pool_face in ("results/runnable_pool.json", "results/crash_fuse.json"):
        rc, out, _ = git("status", "--porcelain")
        line = [l for l in out.decode("utf-8", "replace").splitlines()
                if pool_face.replace("/", os.sep) in l or pool_face in l]
        assert not line, "pool face %s dirty/conflicted -- per-face max-merge required" % pool_face

    receipt = []
    for path in CONFLICTS:
        ours = get_side(2, path)
        theirs = get_side(3, path)
        assert ours is not None and theirs is not None, "stage blob missing: " + path
        for blob, tag in ((ours, "ours"), (theirs, "theirs")):
            assert not any(m.encode() in blob for m in MARKERS), \
                "conflict markers inside stage %s blob: %s" % (tag, path)
        chosen, side, why = None, None, None
        if path.endswith(".json"):
            jo = jt = None
            try:
                jo = json.loads(ours.decode("utf-8", "replace"))
            except Exception:
                pass
            try:
                jt = json.loads(theirs.decode("utf-8", "replace"))
            except Exception:
                pass
            if jo is None and jt is None:
                print("FAIL both sides unparseable: %s" % path)
                return 2
            if jo is None:
                chosen, side, why = theirs, "theirs", "origin side unparseable"
            elif jt is None:
                chosen, side, why = ours, "ours", "mine side unparseable"
            else:
                c = cmp_ts(ts_of(jo), ts_of(jt))
                if c >= 0:
                    chosen, side, why = ours, "ours", "origin ts newer-or-equal (r432 absorb)"
                else:
                    chosen, side, why = theirs, "theirs", "mine ts newer"
            json.loads(chosen.decode("utf-8", "replace"))  # chosen side must parse
        else:
            chosen, side, why = ours, "ours", "same-day doc face, r432 take-ours precedent"
        wp = os.path.join(REPO, path.replace("/", os.sep))
        with open(wp, "wb") as f:
            f.write(chosen)
        rc, _, err = git("add", "--", path)
        assert rc == 0, "git add failed %s: %s" % (path, err.decode()[:120])
        receipt.append({"path": path, "side": side, "why": why,
                        "bytes": len(chosen)})
        print("RESOLVED %-46s -> %-6s (%s)" % (path, side, why))
    with open(os.path.join(REPO, "results", "_r433bmc_rebase_resolve.json"),
              "w", encoding="utf-8", newline="\n") as f:
        json.dump({"round": "r433 bm-c", "pick": "2/4 S6-faces absorb",
                   "faces": receipt,
                   "law": "r432 take-ours absorb + newer-ts-wins + JSON/marker gates"},
                  f, ensure_ascii=False, indent=1)
    print("RECEIPT results/_r433bmc_rebase_resolve.json (%d faces)" % len(receipt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
