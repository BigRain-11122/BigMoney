# -*- coding: utf-8 -*-
"""r377 bm-c: reparent #2 -- wrap payload onto bm-b r585 close (e77cad0bb).

Same r523 law as reparent #1 (which landed the product commit after the
bm-b W106 freeze race). My wrap commit d4d885373 sits on 83438cc37; origin
advanced to e77cad0bb (bm-b r585 close: their state/heartbeat/report +
CODELY union). Shared-name derive faces (token_usage.json etc.) are S6
re-derived every round -- last-writer-wins is the accepted pattern
("next round re-derives", bm-b r585 note).
"""
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = r"K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\msg-r377c-wrap.txt"
NW = 0x08000000


def git(*a, check=True):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, creationflags=NW)
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    if check and r.returncode != 0:
        print("GITFAIL", list(a)[:3], err[:300])
        sys.exit(1)
    return r.returncode, out, err


def main():
    rc, out, _ = git("rev-parse", "HEAD")
    head = out.strip()
    rc, out, _ = git("rev-parse", "origin/main")
    om = out.strip()
    if head == om:
        print("ALREADY_DELIVERED", om[:9])
        sys.exit(0)
    # MY payload = files changed by my wrap commit
    rc, out, _ = git("diff", "--name-only", head + "~1", head)
    my_set = {l.strip() for l in out.splitlines() if l.strip()}
    print("my payload N =", len(my_set))
    rc_code = subprocess.run(["git", "merge-base", "--is-ancestor", head + "~1", om],
                             cwd=REPO, capture_output=True, creationflags=NW).returncode
    if rc_code != 0:
        print("UNEXPECTED: wrap parent not ancestor of origin")
        sys.exit(2)
    print("reparent", head[:9], "onto", om[:9])

    git("reset", "--mixed", om)
    r = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                       capture_output=True, creationflags=NW)
    out = r.stdout.decode("utf-8", "replace")
    add_m, add_del, add_new, checkout, foreign_untracked = [], [], [], [], []
    for l in out.splitlines():
        if not l.strip():
            continue
        st, path = l[:2], l[3:].strip().strip('"')
        if path in my_set:
            if st == "??":
                add_new.append(path)
            elif "D" in st:
                add_del.append(path)
            else:
                add_m.append(path)
        else:
            if st == "??":
                foreign_untracked.append(path)
            else:
                checkout.append(path)
    print("add-mine:", len(add_m), "add-del:", add_del, "add-new:", add_new)
    print("checkout(origin):", checkout)
    print("foreign-untracked:", foreign_untracked)
    if checkout:
        git("checkout", "--", *checkout)
    if add_m or add_del or add_new:
        git("add", "--", *(add_m + add_del + add_new))
    rc, out, _ = git("diff", "--cached", "--stat")
    print("staged files:", out.strip().splitlines()[-1] if out.strip() else "(empty)")
    rc, out, err = git("commit", "-F", MSG, check=False)
    print("commit rc", rc, (out or err)[:160])
    if rc != 0:
        sys.exit(3)
    rc, out, err = git("push", "origin", "main", check=False)
    print("push rc", rc, (out or err)[:300])
    if rc != 0:
        print("PUSH BLOCKED AGAIN -- rerun after next fetch")
        sys.exit(4)
    git("fetch", "origin")
    rc, out, _ = git("rev-list", "--count", "HEAD..origin/main")
    print("behind-count:", out.strip())
    rc, out, _ = git("log", "--oneline", "-n", "2", "origin/main")
    print("origin tip:", out.strip()[:120])
    rc, out, _ = git("status", "--porcelain")
    print("post-status:\n" + out)
    print("REPARENT2_DELIVERED")


if __name__ == "__main__":
    main()
