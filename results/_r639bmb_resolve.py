#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r639 bm-b push-race merge resolver (isolated worktree net path, r630 law).

Context: local chain (r638 set, HEAD cb849e25c) vs origin/main 00d8181d4
(bm-c r434 x2 + bm-a r647 closure + churn absorb). Main worktree occupied by
live daemons (satengine tick / trio burn / autofill, mtimes < 3min) so merge
executed in isolated worktree per r630 law 3.

2 UU faces, both snapshot class per bigmoney-conflict-resolve catalog
(R208 take-new by named ts key; r185 parse-verify before write-back):
- results/_attrition_guard_scan.json -> stage2/ours (origin side)
  ts 2026-10-03T23:31:39+08:00 > mine 2026-10-03T23:16:45+08:00
- results/lhb_update_status.json -> stage3/theirs (bm-b side)
  updated 2026-10-03 23:14:32 > origin 2026-10-03 22:56:08
Zero row-loss faces (jsonl/ledgers) auto-merged by git; pool faces settled
post-merge via merge_lane_views sync_face per S0-1 reland law.
"""
import json
import os
import subprocess
import sys

WT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.environ.get("TEMP", "/tmp"), "bmw639bmb")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DECISIONS = [
    # (path, git-stage-checkout side, winning ts, loser ts, law)
    ("results/_attrition_guard_scan.json", "ours",
     "2026-10-03T23:31:39+08:00", "2026-10-03T23:16:45+08:00", "R208 snapshot take-new"),
    ("results/lhb_update_status.json", "theirs",
     "2026-10-03 23:14:32", "2026-10-03 22:56:08", "R208 snapshot take-new"),
]


def git(*args):
    r = subprocess.run(["git", "-C", WT] + list(args),
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%s\n%s" % (args, r.returncode, r.stderr))
    return r.stdout


def stage_blob(stage, path):
    r = subprocess.run(["git", "-C", WT, "show", ":%s:%s" % (stage, path)],
                      capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("show :%s:%s rc=%s" % (stage, path, r.returncode))
    return r.stdout


def main():
    report = {"round": 639, "machine": "bm-b", "worktree": WT, "faces": []}
    for path, side, win_ts, lose_ts, law in DECISIONS:
        # snapshot ts re-probe on both stages (verify the recorded ordering still holds)
        s2 = json.loads(stage_blob(2, path).decode("utf-8-sig"))
        s3 = json.loads(stage_blob(3, path).decode("utf-8-sig"))
        probe2 = s2.get("ts") or s2.get("updated")
        probe3 = s3.get("ts") or s3.get("updated")
        expect = win_ts if side == "ours" else lose_ts
        if str(probe2) != (win_ts if side == "ours" else lose_ts) or \
           str(probe3) != (lose_ts if side == "ours" else win_ts):
            raise SystemExit("ts probe mismatch for %s: s2=%r s3=%r" % (path, probe2, probe3))
        arg = "--ours" if side == "ours" else "--theirs"
        git("checkout", arg, "--", path)
        resolved = open(os.path.join(WT, path), "rb").read().decode("utf-8-sig")
        for marker in ("<<<<<<<", "=======", ">>>>>>>"):
            if marker in resolved:
                raise SystemExit("conflict marker %s remains in %s" % (marker, path))
        json.loads(resolved)  # r185 parse-verify
        git("add", "--", path)
        report["faces"].append({"path": path, "class": "snapshot", "recipe": "take-new by ts",
                                "side_taken": side, "win_ts": win_ts, "lose_ts": lose_ts,
                                "law": law, "parse_verify": "PASS"})
    out = os.path.join(REPO, "results", "_r639bmb_resolve_report.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
