# -*- coding: utf-8 -*-
"""r746 bm-c merge gates2 (corrected G4, r743 precedent): the first pass
flagged 3 origin-side faces (crash_fuse/daily_scorecard/dashboard_status)
via working-tree hash-object -- the r417 CRLF false-positive family; the
r743-canon comparison is INDEX sha (git ls-files -s) vs origin blob sha
(git rev-parse origin/main:path), which is immune to working-tree CRLF
state and to post-merge daemon live-write churn. Re-runs G1/G3/G5 too,
then commits the merge, pushes, delivery self-verify.
Receipt -> results/_r746bmc_merge_gates2.json."""
import json
import os
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(ROOT, "_r746bmc_mergemsg.txt")
G1 = os.path.join(ROOT, "results", "_r746bmc_merge_gates.json")


def g(args):
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def main():
    receipt = {"round": 746, "mode": "gates2 corrected-G4 (r743 canon: ls-files index sha vs origin blob sha)"}
    # UU face list from .git/MERGE_MSG Conflicts section (first-pass receipt
    # was never written -- gates failed before the write; git's own record is
    # the authoritative source, r742-canonical 14-face set)
    mm = open(os.path.join(ROOT, ".git", "MERGE_MSG"), encoding="utf-8",
              errors="replace").read()
    uu = [l[2:].strip() for l in mm.splitlines() if l.startswith("#\t")]

    # G1 recheck: no unmerged paths
    rc, out, _ = g(["status", "--porcelain"])
    uu_left = [l for l in out.decode("utf-8", "replace").splitlines()
              if l.startswith("UU") or l.startswith("AA")]
    receipt["gate1_uu_remaining"] = len(uu_left)

    # G3 recheck: marker scan on resolved faces (line-start level, r651 law)
    marker_hits = []
    for path in uu:
        full = os.path.join(ROOT, *path.split("/"))
        for i, line in enumerate(open(full, encoding="utf-8", errors="replace").read().splitlines()):
            if line.startswith(("<<<<<<<", "=======", ">>>>>>>")):
                marker_hits.append("%s:L%d" % (path, i + 1))
    receipt["gate3_marker_hits"] = marker_hits

    # G4-corrected: INDEX sha vs origin blob sha for origin-side faces
    rc, out, _ = g(["diff", "--name-only", "HEAD...origin/main"])
    their_all = set(out.decode("utf-8", "replace").splitlines())
    their_exclusive = sorted(their_all - set(uu))
    verbatim_fail = []
    for path in their_exclusive:
        rc, s, _ = g(["ls-files", "-s", "--", path])
        parts = s.decode("utf-8", "replace").split()
        idx_sha = parts[1] if len(parts) >= 2 else ""
        rc, o, _ = g(["rev-parse", "origin/main:%s" % path])
        org_sha = o.decode().strip()
        if idx_sha != org_sha:
            verbatim_fail.append("%s (idx=%s origin=%s)" % (path, idx_sha[:12], org_sha[:12]))
    receipt["gate4_method"] = "ls-files -s index sha vs rev-parse origin/main blob sha"
    receipt["gate4_their_exclusive_n"] = len(their_exclusive)
    receipt["gate4_verbatim_fail"] = verbatim_fail

    # G5 recheck: JSON validity for resolved .json faces
    json_fail = []
    for path in uu:
        if not path.endswith(".json"):
            continue
        full = os.path.join(ROOT, *path.split("/"))
        try:
            json.load(open(full, encoding="utf-8"))
        except Exception as e:
            json_fail.append("%s (%s)" % (path, e))
    receipt["gate5_json_fail"] = json_fail

    ok = (not uu_left and not marker_hits and not verbatim_fail and not json_fail)
    receipt["all_gates_pass"] = ok
    if not ok:
        print("GATES2 FAILED:", json.dumps({k: receipt[k] for k in (
            "gate1_uu_remaining", "gate3_marker_hits",
            "gate4_verbatim_fail", "gate5_json_fail")}, indent=1))
        return 6

    # commit the merge (index carries the resolution; unstaged daemon churn floats)
    if os.path.exists(os.path.join(ROOT, ".git", "MERGE_HEAD")):
        with open(MSG, "w", encoding="utf-8", newline="\n") as f:
            f.write("round 746: merge absorb bm-a same-window S6 regen faces (ts-newer-wins, five gates pass)\n")
        rc, out, err = g(["commit", "-F", MSG])
        receipt["commit_rc"] = rc
        if rc != 0:
            print("COMMIT FAILED:", err.decode("utf-8", "replace")[:400])
            return 7
    else:
        receipt["commit_rc"] = "no-op (merge already committed)"

    rc, out, err = g(["push", "origin", "main"])
    receipt["push_rc"] = rc
    receipt["push_out"] = (out.decode("utf-8", "replace") + err.decode("utf-8", "replace"))[:400]
    if rc != 0:
        print("PUSH FAILED:", receipt["push_out"])
        return 8
    g(["fetch", "origin"])
    b = int(g(["rev-list", "--count", "HEAD..origin/main"])[1].decode().strip() or 0)
    a = int(g(["rev-list", "--count", "origin/main..HEAD"])[1].decode().strip() or 0)
    rc, out, _ = g(["rev-parse", "HEAD"])
    receipt["delivery_ahead"] = a
    receipt["delivery_behind"] = b
    receipt["final_head"] = out.decode().strip()
    outp = os.path.join(ROOT, "results", "_r746bmc_merge_gates2.json")
    with open(outp, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1)
    print(json.dumps({k: receipt.get(k) for k in (
        "gate1_uu_remaining", "gate3_marker_hits", "gate4_their_exclusive_n",
        "gate4_verbatim_fail", "gate5_json_fail", "all_gates_pass",
        "commit_rc", "push_rc", "delivery_ahead", "delivery_behind", "final_head")}, indent=1))
    if a or b:
        print("DELIVERY INCOMPLETE")
        return 9
    print("DELIVERED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
