# -*- coding: utf-8 -*-
"""r746 bm-c push-race closeout: abort the conflicted pull-rebase, absorb via
merge ORT (r741/r742/r743/r745 canon for same-window S6 regen faces),
dynamic UU discovery, per-face embedded-ts newer-wins (deep-ts canon r738;
tie/parse-fail -> theirs per r440), five gates (G1 UU-rem / G2 splice / G3
marker / G4 origin-verbatim / G5 JSON), merge commit -F, push, delivery
self-verify. Receipt -> results/_r746bmc_merge_gates.json.
Pattern credit: Tools/_r742bmc_merge_resolve.py (canonical resolver)."""
import json
import os
import re
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(ROOT, "_r746bmc_mergemsg.txt")
TS_RE = re.compile(r"2026-10-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?")
APPEND_ONLY_PAT = re.compile(
    r"(pool_dualrun\..*\.jsonl|round_reports.*\.md|gate_attrition.*\.json|"
    r"trials_ledger|results/post_review\.jsonl)")


def g(args, check=True):
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
    receipt = {"round": 746, "mode": "rebase-abort -> merge ORT ts-newer-wins"}
    # 1) abort the conflicted rebase (round commit 9b098a96f + churn absorb
    #    84dd2f7c5 are safe on main)
    rc, out, err = g(["rebase", "--abort"])
    receipt["rebase_abort_rc"] = rc
    if rc != 0:
        print("REBASE ABORT FAILED:", err.decode("utf-8", "replace")[:400])
        return 2
    rc, out, _ = g(["rev-parse", "--abbrev-ref", "HEAD"])
    branch = out.decode().strip()
    receipt["branch"] = branch
    rc, out, _ = g(["rev-parse", "HEAD"])
    receipt["head_after_abort"] = out.decode().strip()[:9]
    rc, out, _ = g(["status", "--porcelain"])
    pre = [l for l in out.decode("utf-8", "replace").splitlines() if l.strip()]
    receipt["dirty_after_abort"] = len(pre)

    # 2) merge ORT
    rc, out, err = g(["merge", "origin/main"])
    receipt["merge_rc"] = rc
    if rc not in (0, 1):
        print("MERGE FAILED:", err.decode("utf-8", "replace")[:400])
        return 3
    if rc == 0:
        receipt["merge_clean"] = True
        print("merge clean, no UU faces")
    # 3) dynamic UU discovery
    rc, out, _ = g(["status", "--porcelain"])
    uu = [l[3:].strip().strip('"') for l in out.decode("utf-8", "replace").splitlines()
          if l.startswith("UU") or l.startswith("AA")]
    receipt["uu_faces"] = uu
    receipt["uu_count"] = len(uu)
    splice = [p for p in uu if APPEND_ONLY_PAT.search(p)]
    receipt["gate2_splice_faces"] = len(splice)
    if splice:
        print("SPLICE FACES IN UU SET (append-only law violation):", splice)
        return 4

    faces = {}
    for path in uu:
        rc, ours, _ = g(["show", ":2:%s" % path])
        rc2, theirs, _ = g(["show", ":3:%s" % path])
        t_ours, t_theirs = max_ts(ours), max_ts(theirs)
        if t_ours is not None and (t_theirs is None or t_ours > t_theirs):
            winner, blob = "ours", ours
        else:
            winner, blob = "theirs", theirs
        full = os.path.join(ROOT, *path.split("/"))
        with open(full, "wb") as fh:
            fh.write(blob)
        rc, _, err = g(["add", "--", path])
        faces[path] = {"winner": winner, "ts_ours": t_ours,
                       "ts_theirs": t_theirs, "add_rc": rc, "bytes": len(blob)}
        if rc != 0:
            print("ADD-FAIL", path, err.decode("utf-8", "replace")[:200])
            return 5
    receipt["faces"] = faces

    # G1: no UU/AA remaining
    rc, out, _ = g(["status", "--porcelain"])
    uu_left = [l for l in out.decode("utf-8", "replace").splitlines()
               if l.startswith("UU") or l.startswith("AA")]
    receipt["gate1_uu_remaining"] = len(uu_left)
    # G3: conflict-marker scan on resolved faces (line-start level, r651 law)
    marker_hits = []
    for path in uu:
        full = os.path.join(ROOT, *path.split("/"))
        for i, line in enumerate(open(full, encoding="utf-8", errors="replace").read().splitlines()):
            if line.startswith(("<<<<<<<", "=======", ">>>>>>>")):
                marker_hits.append("%s:L%d" % (path, i + 1))
    receipt["gate3_marker_hits"] = marker_hits
    # G4: origin-verbatim for origin-exclusive faces (their side only)
    rc, out, _ = g(["diff", "--name-only", "HEAD...origin/main"])
    their_all = set(out.decode("utf-8", "replace").splitlines())
    their_exclusive = sorted(their_all - set(uu))
    verbatim_fail = []
    for path in their_exclusive:
        full = os.path.join(ROOT, *path.split("/"))
        if not os.path.exists(full):
            verbatim_fail.append(path + " (missing)")
            continue
        rc, h_wt, _ = g(["hash-object", full])
        rc, h_or, _ = g(["rev-parse", "origin/main:%s" % path])
        if h_wt.decode().strip() != h_or.decode().strip():
            verbatim_fail.append(path)
    receipt["gate4_their_exclusive_n"] = len(their_exclusive)
    receipt["gate4_verbatim_fail"] = verbatim_fail
    # G5: JSON validity for resolved .json faces
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
        print("GATES FAILED:", json.dumps({k: receipt[k] for k in (
            "gate1_uu_remaining", "gate2_splice_faces", "gate3_marker_hits",
            "gate4_verbatim_fail", "gate5_json_fail")}, indent=1))
        return 6

    # 4) merge commit + push + delivery verify
    staged = g(["diff", "--cached", "--name-only"])[1].decode("utf-8", "replace")
    if staged.strip() or receipt.get("merge_clean"):
        if os.path.exists(os.path.join(ROOT, ".git", "MERGE_HEAD")):
            with open(MSG, "w", encoding="utf-8", newline="\n") as f:
                f.write("round 746: merge absorb bm-a same-window S6 regen faces (ts-newer-wins, five gates)\n")
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
    outp = os.path.join(ROOT, "results", "_r746bmc_merge_gates.json")
    with open(outp, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1)
    print(json.dumps({k: receipt.get(k) for k in (
        "rebase_abort_rc", "head_after_abort", "dirty_after_abort", "merge_rc",
        "uu_count", "gate1_uu_remaining", "gate2_splice_faces",
        "gate3_marker_hits", "gate4_their_exclusive_n", "gate4_verbatim_fail",
        "gate5_json_fail", "all_gates_pass", "commit_rc", "push_rc",
        "delivery_ahead", "delivery_behind", "final_head")}, indent=1))
    for p, v in faces.items():
        print("%-46s %-7s ours=%s theirs=%s" % (p, v["winner"], v["ts_ours"], v["ts_theirs"]))
    if a or b:
        print("DELIVERY INCOMPLETE")
        return 9
    print("DELIVERED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
