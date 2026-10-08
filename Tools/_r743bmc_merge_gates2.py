# -*- coding: utf-8 -*-
"""r743 bm-c merge gates2: corrected G4 origin-verbatim check. First pass
hash-object raw CRLF working-tree bytes vs LF blob = r417-family comparison
methodology false positive (git diff working-tree-vs-index clean proves
content equality; the 6 flagged faces are checkout-eol conversion cases).
Correct law: compare INDEX blob sha (git ls-files -s, filter-neutral repo
sha) vs origin/main blob sha (git rev-parse). Also re-asserts G1/G3/G5 on the
resolved set and computes the proper their_exclusive basis (their_all minus
my_changed minus UU). Receipt -> results/_r743bmc_merge_gates2.json."""
import json
import os
import re
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
UU = [
    "docs/daily_report/REPORT-2026-10-08.json",
    "docs/daily_report/REPORT-2026-10-08.md",
    "docs/live_usage/LIVE-2026-10-08.json",
    "docs/live_usage/LIVE-2026-10-08.md",
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


def g(args):
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def main():
    rc, base, _ = g(["merge-base", "HEAD", "origin/main"])
    base = base.strip()
    rc, their_out, _ = g(["diff", "--name-only", base + "..origin/main"])
    their_all = set(x for x in their_out.splitlines() if x)
    rc, my_out, _ = g(["diff", "--name-only", base + "..HEAD"])
    my_changed = set(x for x in my_out.splitlines() if x)
    their_exclusive = sorted(their_all - my_changed - set(UU))
    both_modified = sorted(their_all & my_changed - set(UU))
    verbatim_fail = []
    for path in their_exclusive:
        rc, ls, _ = g(["ls-files", "-s", "--", path])
        parts = ls.split()
        idx_sha = parts[1] if len(parts) >= 2 else ""
        rc, or_sha, _ = g(["rev-parse", "origin/main:%s" % path])
        if idx_sha != or_sha.strip():
            verbatim_fail.append(path)
    # re-assert G1: no UU left
    rc, out, _ = g(["status", "--porcelain"])
    uu_left = [l for l in out.splitlines() if l.startswith("UU") or l[1:3] == "AA"]
    # re-assert G3: line-start marker scan on resolved set
    marker_hits = []
    for path in UU:
        full = os.path.join(ROOT, *path.split("/"))
        for i, line in enumerate(open(full, encoding="utf-8", errors="replace").read().splitlines()):
            if line.startswith(("<<<<<<<", "=======", ">>>>>>>")):
                marker_hits.append("%s:L%d" % (path, i + 1))
    # re-assert G5: JSON validity
    json_fail = []
    for path in UU:
        if not path.endswith(".json"):
            continue
        try:
            json.load(open(os.path.join(ROOT, *path.split("/")), encoding="utf-8"))
        except Exception as e:
            json_fail.append("%s (%s)" % (path, e))
    receipt = {
        "round": 743,
        "gate4_method": "ls-files index sha vs origin/main blob sha (filter-neutral)",
        "merge_base": base[:12],
        "their_all_n": len(their_all),
        "my_changed_n": len(my_changed),
        "their_exclusive_n": len(their_exclusive),
        "both_modified_automerged": both_modified,
        "gate1_uu_remaining": len(uu_left),
        "gate3_marker_hits": marker_hits,
        "gate4_verbatim_fail": verbatim_fail,
        "gate5_json_fail": json_fail,
        "g4_firstpass_falsepos_basis": ("hash-object raw CRLF worktree bytes vs LF blob; git diff worktree-vs-index clean on all 6 = content equal; eol checkout conversion cases"),
    }
    receipt["all_gates_pass"] = (not uu_left and not marker_hits
                                 and not verbatim_fail and not json_fail)
    outp = os.path.join(ROOT, "results", "_r743bmc_merge_gates2.json")
    with open(outp, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1)
    print(json.dumps({k: receipt[k] for k in ("their_all_n", "my_changed_n",
                                              "their_exclusive_n", "both_modified_automerged",
                                              "gate1_uu_remaining", "gate3_marker_hits",
                                              "gate4_verbatim_fail", "gate5_json_fail",
                                              "all_gates_pass")}, indent=1))
    return 0 if receipt["all_gates_pass"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
