# -*- coding: utf-8 -*-
"""r746 bm-c closeout continuation: daemon live-write race healing (r727/
r642/r730 family). The round commit 9b098a96f is safe; post-commit daemon
faces re-ticked mid-window -> absorb them first (clean-tree law), then
pull --rebase onto origin (behind=1, bm-a active window), push, delivery
self-verify. HARD FAIL on any conflict so the session resolves per canon
(ts-newer-wins, r738 deep-ts) instead of guessing."""
import os
import re
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(REPO, "_r746bmc_commitmsg2.txt")

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
        print(out.strip()[:900])
    if err.strip():
        print("STDERR:", err.strip()[:900])
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
        print("FOREIGN FACES, absorb refused:", foreign)
        return 2
    print("dirty own faces: %d" % len(dirty))
    for p in dirty:
        git(["add", "--", p], check=False)
    cached = git(["diff", "--cached", "--name-only"])
    names = [l for l in cached.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
    if names:
        with open(MSG, "w", encoding="utf-8", newline="\n") as f:
            f.write("round 746: churn absorb (daemon live-write race, pre-closeout)\n")
        git(["commit", "-F", MSG])
    else:
        print("no churn to absorb")

    git(["pull", "--rebase"])
    st2 = git(["status", "--porcelain"])
    uu = [l for l in st2.stdout.decode("utf-8", "replace").splitlines()
          if l.startswith("UU") or l.startswith("AA")]
    if uu:
        print("REBASE CONFLICTS:", uu)
        return 6
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
