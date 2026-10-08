# -*- coding: utf-8 -*-
"""r746 bm-c closeout commit: targeted add of own dirty faces (products +
daemon churn, no foreign files), EXPLICIT QA-pair add (r549-①/r552
untrackedCache stale-window family: newly written qa/smoke-r746.md +
qa/equity-curve-r746.png exist on disk but status --porcelain omits them --
r745 same-family live fire, healed by force-adding the pair), commit -F
message file (r849 law), push origin main, delivery self-verify (fetch +
rev-list both directions). Pattern credit: Tools/_r745bmc_commit.py."""
import os
import re
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(REPO, "_r746bmc_commitmsg.txt")
QA_PAIR = [os.path.join(REPO, "qa", "smoke-r746.md"),
           os.path.join(REPO, "qa", "equity-curve-r746.png")]

OWN = re.compile(
    r"^(_r\d+bmc_|Tools/_r\d+bmc_|qa/(smoke|equity-curve)-r\d+\.|"
    r"results/(_r\d+bmc_|_orphan_face_probe(\.bm-c)?\.json|idle_trigger|"
    r"post_review|_attrition_guard_scan\.json|token_usage|compute_audit|"
    r"regime_state|update_status|autofill_state|dispatcher_state|"
    r"lhb_update_status|futures_update_status|fund_premium_status\.json|"
    r"fundamental_b_layer_filter\.json|pool_dualrun\.bm-c\.jsonl|"
    r"saturation_engine|market_clock/)|"
    r"docs/(daily_report|live_usage)/|logs/iteration-loop/round_reports-bm-c\.md|"
    r"research/HANDOVER\.md|fleet/machines/bm-c\.json|state-bm-c\.json)")


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
    # r549-①/r552 untrackedCache stale-window healing (r745 precedent):
    # QA evidence pair exists on disk but may be missing from status output.
    for q in QA_PAIR:
        if os.path.exists(q):
            git(["add", "--", q], check=False)
        else:
            print("QA PAIR MISSING ON DISK:", q)
            return 4
    cached = git(["diff", "--cached", "--name-only"])
    names = [l for l in cached.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
    print("staged %d files" % len(names))
    if not any(n.replace("\\", "/").startswith("qa/") for n in names):
        print("QA PAIR NOT STAGED")
        return 5
    with open(MSG, "w", encoding="utf-8", newline="\n") as f:
        f.write("round 746: QA det-66th 5/5 + S6 40/40 rc0 + clone gate trio (pre-open watch round 66)\n")
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
