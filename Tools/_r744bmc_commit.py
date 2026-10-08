# -*- coding: utf-8 -*-
"""r744 bm-c closeout commit: targeted add of own dirty faces (products +
daemon churn, no foreign files), commit -F message file (r849 law), push
origin main, delivery self-verify (fetch + rev-list both directions)."""
import os
import re
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(REPO, "_r744bmc_commitmsg.txt")

OWN = re.compile(
    r"^(_r\d+bmc_|Tools/_r\d+bmc_|qa/(smoke|equity-curve)-r\d+\.|"
    r"results/(_r\d+bmc_|_orphan_face_probe\.bm-c\.json|idle_trigger|"
    r"post_review|_attrition_guard_scan\.json|token_usage|compute_audit|"
    r"regime_state|update_status|autofill_state|dispatcher_state|"
    r"lhb_update_status|futures_update_status|fund_premium_status\.json|"
    r"fundamental_b_layer_filter\.json|pool_dualrun\.bm-c\.jsonl|"
    r"saturation_engine|market_clock/)|"
    r"docs/(daily_report|live_usage)/|logs/iteration-loop/round_reports-bm-c\.md|"
    r"fleet/machines/bm-c\.json|state-bm-c\.json)")


def git(args, check=True):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    print("git %s rc=%d" % (args[0], p.returncode))
    if out.strip():
        print(out.strip()[:700])
    if err.strip():
        print("STDERR:", err.strip()[:700])
    if check and p.returncode != 0:
        print("HARD FAIL on:", " ".join(args))
        sys.exit(p.returncode)
    return p


def main():
    st = git(["status", "--porcelain"])
    lines = [l for l in st.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
    dirty = [l[3:].strip().strip('"') for l in lines]
    foreign = [p for p in dirty if not OWN.match(p)]
    if foreign:
        print("FOREIGN FACES, commit refused:", foreign)
        return 2
    print("own faces to add: %d" % len(dirty))
    for p in dirty:
        git(["add", "--", p], check=False)
    cached = git(["diff", "--cached", "--name-only"])
    names = [l for l in cached.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
    print("staged %d files" % len(names))
    with open(MSG, "w", encoding="utf-8", newline="\n") as f:
        f.write("round 744: QA det-64th 5/5 + S6 40/40 rc0 + clone gate trio (pre-open watch round 64)\n")
    git(["commit", "-F", MSG])

    git(["fetch", "origin"])
    behind = int(git(["rev-list", "--count", "HEAD..origin/main"]).stdout.decode().strip() or 0)
    print("behind=%d" % behind)
    if behind:
        git(["pull", "--rebase"])
    git(["push", "origin", "main"])
    git(["fetch", "origin"])
    b = int(git(["rev-list", "--count", "HEAD..origin/main"]).stdout.decode().strip() or 0)
    a = int(git(["rev-list", "--count", "origin/main..HEAD"]).stdout.decode().strip() or 0)
    print("DELIVERY: ahead=%d behind=%d" % (a, b))
    if a or b:
        print("DELIVERY INCOMPLETE")
        return 3
    print("DELIVERED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
