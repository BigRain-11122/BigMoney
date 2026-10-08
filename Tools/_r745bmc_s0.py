"""r745 bm-c S0: round-start status probe + targeted absorb of own dirty faces
+ pull --rebase (no push here; push at closeout). r849 family law: commit -F
message file via python subprocess. Auto-discovers dirty faces from
status --porcelain; refuses to absorb if any foreign (non-own) face appears.
Pattern credit: Tools/_r744bmc_s0.py (canonical S0 driver chain)."""
import json
import os
import re
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(REPO, "_r745bmc_commitmsg.txt")

# own-face classifier: daemon live faces + own round leftovers (bm-c churn canon)
OWN_PAT = re.compile(
    r"^(_r\d+bmc_|Tools/_r\d+bmc_|results/(_orphan_face_probe\.json|dispatcher_state\.bm-c\.json|"
    r"saturation_engine/face_bm-c\.json|saturation_engine_state\.bm-c\.json|"
    r"idle_trigger\.bm-c\.json|token_usage\.json|compute_audit\.json))")


def git(args, check=True):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    print("git %s rc=%d" % (args[0], p.returncode))
    if out.strip():
        print(out.strip()[:800])
    if err.strip():
        print("STDERR:", err.strip()[:800])
    if check and p.returncode != 0:
        print("HARD FAIL on:", " ".join(args))
        sys.exit(p.returncode)
    return p


def main():
    facts = {}
    st = git(["status", "--porcelain"])
    lines = [l for l in st.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
    dirty = []
    for l in lines:
        code, path = l[:2], l[3:].strip().strip('"')
        dirty.append({"code": code, "path": path})
    facts["dirty"] = dirty
    foreign = [d for d in dirty if not OWN_PAT.match(d["path"])]
    facts["foreign_count"] = len(foreign)
    facts["foreign"] = foreign

    if foreign:
        print(json.dumps(facts, indent=1))
        print("FOREIGN FACES PRESENT: absorb refused, handle manually")
        return 2

    for d in dirty:
        p = git(["add", "--", d["path"]], check=False)
        if p.returncode != 0:
            print("ADD FAILED:", d["path"])
            return 3
    cached = git(["diff", "--cached", "--name-only"])
    names = [l for l in cached.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
    facts["staged"] = names
    print("staged %d files: %s" % (len(names), names))
    if names:
        with open(MSG, "w", encoding="utf-8", newline="\n") as f:
            f.write("round 745: absorb own daemon live faces (pre-open S0 window)\n")
        git(["commit", "-F", MSG])

    git(["fetch", "origin"])
    behind = git(["rev-list", "--count", "HEAD..origin/main"])
    ahead = git(["rev-list", "--count", "origin/main..HEAD"])
    facts["behind"] = int(behind.stdout.decode().strip() or 0)
    facts["ahead"] = int(ahead.stdout.decode().strip() or 0)
    print("behind=%d ahead=%d" % (facts["behind"], facts["ahead"]))

    if facts["behind"]:
        git(["pull", "--rebase"])
        st2 = git(["status", "--porcelain"])
        rem = [l for l in st2.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
        facts["post_rebase_dirty"] = rem
    print("S0 DONE:", json.dumps(facts, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
