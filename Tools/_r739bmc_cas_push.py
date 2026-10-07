"""r739 bm-c CAS direct-commit of OH-20261008-bigmoney.md to group tree
origin/main (O-20261008-0650 ③ receipt carrier). Zero working-tree touch:
temp-index + commit-tree + push <sha>:main. Laws: r849 (UTF-8 msg file, explicit
origin param), r731 (no amend, ls-remote precheck), CAS hard validation
(40-hex on blob/tree/commit + push output keyword scan + duplicate-delivery
gate + tip verify)."""
import os
import re
import subprocess
import sys

GROUP = r"K:\Fluxgroup\FluxGroup"
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
SRC = os.path.join(REPO, "results", "_r739bmc_oh_bigmoney_tmp.md")
TARGET = "cph4/oss-harvest/OH-20261008-bigmoney.md"
IDX = os.path.join(REPO, "results", "_r739bmc_cas.index")
MSG = os.path.join(REPO, "results", "_r739bmc_cas_msg.txt")

MSG_TEXT = ("cph4/oss-harvest: OH-20261008-bigmoney innovation radar domain "
            "slice (O-20261008-0650 ③ nine-company claim window; quant/finance "
            "face: GitHub API 7-face + HN 2-face live reads; 7 candidates "
            "gated, zero adoption; evidence bigmoney results/_r739bmc_"
            "innovation_scan.json; delivered by bm-c r739 same-round "
            "claim+start per CEO immediate-order law)\n")


def g(args, env=None):
    p = subprocess.run(["git", "-C", GROUP] + args, capture_output=True, env=env)
    return p.returncode, p.stdout.decode("utf-8", "replace").strip(), \
        p.stderr.decode("utf-8", "replace").strip()


def main():
    # duplicate-delivery gate: target must not exist on origin/main
    rc, _, _ = g(["cat-file", "-e", f"origin/main:{TARGET}"])
    if rc == 0:
        print("ABORT: target already exists on origin/main (duplicate delivery)")
        return 3
    rc, base, err = g(["rev-parse", "origin/main"])
    if rc != 0 or not re.fullmatch(r"[0-9a-f]{40}", base or ""):
        print("ABORT: bad base", rc, err)
        return 3
    # blob
    p = subprocess.run(["git", "-C", GROUP, "hash-object", "-w", SRC],
                       capture_output=True)
    blob = p.stdout.decode().strip()
    if not re.fullmatch(r"[0-9a-f]{40}", blob):
        print("ABORT: bad blob", blob, p.stderr.decode()[:200])
        return 3
    # temp index: read-tree base + add entry
    env = dict(os.environ, GIT_INDEX_FILE=IDX)
    if os.path.exists(IDX):
        os.remove(IDX)
    rc, _, err = g(["read-tree", base], env=env)
    if rc != 0:
        print("ABORT: read-tree", err[:200])
        return 3
    rc, _, err = g(["update-index", "--add", "--cacheinfo",
                    "100644", blob, TARGET], env=env)
    if rc != 0:
        print("ABORT: update-index", err[:200])
        return 3
    rc, tree, err = g(["write-tree"], env=env)
    if rc != 0 or not re.fullmatch(r"[0-9a-f]{40}", tree or ""):
        print("ABORT: bad tree", rc, err[:200])
        return 3
    # commit-tree with python-written UTF-8 message file (r849 law)
    with open(MSG, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(MSG_TEXT)
    rc, newc, err = g(["commit-tree", tree, "-p", base, "-F", MSG])
    if rc != 0 or not re.fullmatch(r"[0-9a-f]{40}", newc or ""):
        print("ABORT: bad commit", rc, err[:200])
        return 3
    print("blob", blob)
    print("tree", tree)
    print("commit", newc, "base", base)
    # push with explicit origin (r849 ②)
    rc, out, err = g(["push", "origin", f"{newc}:main"])
    combined = (out + " " + err).lower()
    bad = any(k in combined for k in ("fatal", "rejected", "failed", "error"))
    if rc != 0 or bad:
        print("PUSH-FAIL rc", rc, "OUT", out[:300], "ERR", err[:300])
        return 2
    print("PUSH OK:", out, err)
    # tip verify
    rc, tip, err = g(["ls-remote", "origin", "main"])
    tip_sha = (tip or "").split("\t")[0] if tip else ""
    if tip_sha != newc:
        print("VERIFY-FAIL: remote tip", tip_sha[:12], "!= commit", newc[:12])
        return 2
    print("TIP VERIFIED", tip_sha[:12])
    for f in (IDX, MSG):
        if os.path.exists(f):
            os.remove(f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
