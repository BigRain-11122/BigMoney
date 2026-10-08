# -*- coding: utf-8 -*-
"""r745 bm-c push-race window leg-1: churn-absorb (r642 net-tree law) +
merge origin/main (--no-edit) -> capture outcome + UU face list for the
resolver clone. Rebase-merge mid-state guard (r868 law) before any write.
Pattern credit: r742/r743 addendum windows; resolution follows in
_r745bmc_merge_resolve.py (r738 deep-ts canon)."""
import json
import os
import re
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(ROOT, "_r745bmc_commitmsg2.txt")

OWN_PAT = re.compile(
    r"^(_r\d+bmc_|Tools/_r\d+bmc_|qa/(smoke|equity-curve)-r\d+\.(md|png)|"
    r"results/(_orphan_face_probe\.json|dispatcher_state\.bm-c\.json|"
    r"saturation_engine/face_bm-c\.json|saturation_engine_state\.bm-c\.json|"
    r"idle_trigger\.bm-c\.json|token_usage\.json|compute_audit\.json))")


def git(args, check=True):
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    print("git %s rc=%d" % (" ".join(args[:2]), p.returncode))
    if out.strip():
        print(out.strip()[:600])
    if err.strip():
        print("STDERR:", err.strip()[:600])
    if check and p.returncode not in (0, 1):
        print("HARD FAIL on:", " ".join(args))
        sys.exit(p.returncode)
    return p


def main():
    if os.path.isdir(os.path.join(ROOT, ".git", "rebase-merge")):
        print("REBASE-MERGE MID-STATE PRESENT: refuse, handle per r868 law")
        return 4
    facts = {}
    st = git(["status", "--porcelain"])
    lines = [l for l in st.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
    dirty = [l[3:].strip().strip('"') for l in lines]
    foreign = [p for p in dirty if not OWN_PAT.match(p)]
    facts["dirty"] = dirty
    facts["foreign"] = foreign
    if foreign:
        print(json.dumps(facts, indent=1))
        print("FOREIGN FACES: absorb refused")
        return 2
    if dirty:
        for p in dirty:
            git(["add", "--", p], check=False)
        with open(MSG, "w", encoding="utf-8", newline="\n") as f:
            f.write("round 745: absorb daemon churn (push-race window 2nd absorb)\n")
        git(["commit", "-F", MSG])
    else:
        print("no churn to absorb (clean tree)")
    git(["fetch", "origin"])
    p = git(["merge", "origin/main", "--no-edit"], check=False)
    facts["merge_rc"] = p.returncode
    st2 = git(["status", "--porcelain"])
    uu = []
    for l in st2.stdout.decode("utf-8", "replace").splitlines():
        if not l.strip():
            continue
        if l[:2] in ("UU", "AA") or l[1:3] in ("UU", "AA"):
            uu.append(l[3:].strip().strip('"'))
    facts["uu_faces"] = uu
    print("RACE-LEG1:", json.dumps(facts, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
