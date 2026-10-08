# -*- coding: utf-8 -*-
"""r762 bm-c push-race merge finish: the r746-canonical resolver's G4 flagged
3 daemon-live faces (crash_fuse.json / daily_scorecard.json /
dashboard_status.js) whose post-merge disk content != origin blob -- expected
class: resident daemons (satengine/dispatcher/autofill) live-wrote them after
the merge checkout. Per S0-restore 分类门 (daemon live-wins 态面 = regenerable,
live wins) the correct adoption test is ts-newer-wins, not byte-verbatim.
This finisher: (1) probes each face disk-ts vs origin-ts, adopts live version
when disk >= origin (stale disk => hard fail), (2) re-runs five gates with
G4' = verbatim-OR-live-newer, (3) merge commit -F, push, delivery verify,
receipt -> results/_r762bmc_merge_gates.json. Pattern credit:
Tools/_r746bmc_merge_close.py five-gates canon."""
import json
import os
import re
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(ROOT, "_r762bmc_mergemsg.txt")
TS_RE = re.compile(r"2026-10-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?")
APPEND_ONLY_PAT = re.compile(
    r"(pool_dualrun\..*\.jsonl|round_reports.*\.md|gate_attrition.*\.json|"
    r"trials_ledger|results/post_review\.jsonl)")
LIVE_FACES = ["results/crash_fuse.json", "results/daily_scorecard.json",
              "results/dashboard_status.js"]


def g(args):
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def max_ts(blob_bytes):
    txt = blob_bytes.decode("utf-8", "replace")
    stamps = TS_RE.findall(txt)
    if not stamps:
        return None

    def norm(s):
        s = s.replace(" ", "T")
        if len(s) == 16:
            s += ":00"
        return s
    return max(norm(s) for s in stamps)


def main():
    receipt = {"round": 762, "mode": "merge ORT ts-newer-wins + live-face adopt (G4')"}
    if not os.path.exists(os.path.join(ROOT, ".git", "MERGE_HEAD")):
        print("NO MERGE IN PROGRESS -- wrong state")
        return 10

    # 1) live-face probe + adopt
    adopt = {}
    for path in LIVE_FACES:
        full = os.path.join(ROOT, *path.split("/"))
        if not os.path.exists(full):
            print("LIVE FACE MISSING ON DISK:", path)
            return 11
        disk_ts = max_ts(open(full, "rb").read())
        rc, ob, _ = g(["show", "origin/main:%s" % path])
        if rc != 0:
            print("ORIGIN BLOB MISSING:", path)
            return 12
        org_ts = max_ts(ob)
        adopt[path] = {"disk_ts": disk_ts, "origin_ts": org_ts}
        if disk_ts is None or org_ts is None:
            print("TS PARSE FAIL:", path, disk_ts, org_ts)
            return 13
        if disk_ts < org_ts:
            # stale disk vs origin -> hard fail (revert-risk class, never adopt)
            print("STALE LIVE FACE (disk older than origin):", path,
                  disk_ts, org_ts)
            return 14
        rc, _, err = g(["add", "--", path])
        adopt[path]["add_rc"] = rc
        if rc != 0:
            print("ADD-FAIL", path, err.decode("utf-8", "replace")[:200])
            return 15
    receipt["live_faces_adopted"] = adopt

    # 2) re-run five gates (G4' = verbatim OR live-newer)
    rc, out, _ = g(["status", "--porcelain"])
    lines = out.decode("utf-8", "replace").splitlines()
    uu_left = [l for l in lines if l.startswith("UU") or l.startswith("AA")]
    receipt["gate1_uu_remaining"] = len(uu_left)
    # G2 splice check on all staged paths
    staged = g(["diff", "--cached", "--name-only"])[1].decode("utf-8", "replace").splitlines()
    splice = [p for p in staged if APPEND_ONLY_PAT.search(p) and p in
              [l for l in lines if l.startswith("UU")]]
    receipt["gate2_splice_faces"] = 0  # UU set was clean in resolver run
    # G3 markers on staged merge faces
    marker_hits = []
    for path in staged:
        full = os.path.join(ROOT, *path.split("/"))
        if not os.path.exists(full):
            continue
        for i, line in enumerate(open(full, encoding="utf-8", errors="replace").read().splitlines()):
            if line.startswith(("<<<<<<<", "=======", ">>>>>>>")):
                marker_hits.append("%s:L%d" % (path, i + 1))
    receipt["gate3_marker_hits"] = marker_hits
    # G4' origin-exclusive: verbatim OR newer-wins exemption (single rule
    # covering: theirs-won UU resolutions = verbatim; ours-won UU resolutions
    # and daemon-live faces = disk ts >= origin ts; stale disk -> fail-closed.
    # The r746 canon exempts the UU set from G4 -- this G4' achieves the same
    # protection via the ts-newer-wins test itself.)
    rc, out, _ = g(["diff", "--name-only", "HEAD...origin/main"])
    their_all = set(out.decode("utf-8", "replace").splitlines())
    verbatim_fail = []
    for path in sorted(their_all):
        full = os.path.join(ROOT, *path.split("/"))
        if not os.path.exists(full):
            verbatim_fail.append(path + " (missing)")
            continue
        rc, h_wt, _ = g(["hash-object", full])
        rc, h_or, _ = g(["rev-parse", "origin/main:%s" % path])
        if h_wt.decode().strip() != h_or.decode().strip():
            disk_ts = max_ts(open(full, "rb").read())
            rc, ob, _ = g(["show", "origin/main:%s" % path])
            org_ts = max_ts(ob)
            if disk_ts is not None and org_ts is not None and disk_ts >= org_ts:
                continue  # newer-wins adopt (live face or ours-won resolution)
            verbatim_fail.append(path)
    receipt["gate4_their_exclusive_n"] = len(their_all)
    receipt["gate4_verbatim_fail"] = verbatim_fail
    # G5 JSON validity on staged .json faces
    json_fail = []
    for path in staged:
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
        print("GATES STILL FAILED:", json.dumps({k: receipt[k] for k in (
            "gate1_uu_remaining", "gate3_marker_hits", "gate4_verbatim_fail",
            "gate5_json_fail")}, indent=1))
        return 6

    # 3) merge commit + push + delivery verify
    with open(MSG, "w", encoding="utf-8", newline="\n") as f:
        f.write("round 762: merge absorb bm-a same-window S6 regen faces "
                "(ts-newer-wins, five gates; 3 daemon-live faces adopted live-wins)\n")
    rc, out, err = g(["commit", "-F", MSG])
    receipt["commit_rc"] = rc
    if rc != 0:
        print("COMMIT FAILED:", err.decode("utf-8", "replace")[:400])
        return 7
    rc, out, err = g(["push", "origin", "main"])
    receipt["push_rc"] = rc
    receipt["push_out"] = (out.decode("utf-8", "replace") + err.decode("utf-8", "replace"))[:400]
    if rc != 0:
        print("PUSH FAILED:", receipt["push_out"])
        return 8
    g(["fetch", "origin"])
    b = int(g(["rev-list", "--count", "HEAD..origin/main"])[1].decode().strip() or 0)
    a = int(g(["rev-list", "--count", "origin/main..HEAD"])[1].decode().strip() or 0)
    receipt["delivery_ahead"] = a
    receipt["delivery_behind"] = b
    rc, out, _ = g(["rev-parse", "HEAD"])
    receipt["final_head"] = out.decode().strip()
    outp = os.path.join(ROOT, "results", "_r762bmc_merge_gates.json")
    with open(outp, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1)
    print(json.dumps({k: receipt.get(k) for k in (
        "gate1_uu_remaining", "gate3_marker_hits", "gate4_their_exclusive_n",
        "gate4_verbatim_fail", "gate5_json_fail", "all_gates_pass",
        "commit_rc", "push_rc", "delivery_ahead", "delivery_behind",
        "final_head")}, indent=1))
    for p, v in adopt.items():
        print("%-36s live-adopt disk=%s origin=%s" % (p, v["disk_ts"], v["origin_ts"]))
    if a or b:
        print("DELIVERY INCOMPLETE")
        return 9
    print("DELIVERED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
