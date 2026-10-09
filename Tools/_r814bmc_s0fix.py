# -*- coding: utf-8 -*-
"""r814 bm-c S0 fixer (r811 law ②): post-absorb CRLF drift faces ->
git checkout -- renormalize -> pull --rebase. Then group-tree orders.md
delta extraction: reflog old tip vs new origin/main blob, print ADDED rows
verbatim (CEO to-do physical-item zone rows for this round's consumption).
Zero UU auto-resolution: conflicts only reported (pit-git-surgery domain).
CREATE_NO_WINDOW + 75s jackets throughout."""
import subprocess

CNW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
HTTPS_URL = "https://github.com/BigRain-11122/BigMoney.git"


def g(cwd, args, timeout=75):
    try:
        r = subprocess.run(["git", "-C", cwd] + args, capture_output=True,
                           creationflags=CNW, timeout=timeout)
        return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
            (r.stderr or b"").decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def main():
    # -- 1) renormalize drift faces --
    rc, st, _ = g(ROOT, ["status", "--porcelain"])
    drift = [l[3:].strip().strip('"') for l in st.splitlines()
             if l.strip() and l.strip()[0] in "MMARC"]
    print("DRIFT-FACES %d" % len(drift))
    for p in drift:
        print("  drift: " + p)
    if drift:
        rc, o, e = g(ROOT, ["checkout", "--"] + drift)
        print("CHECKOUT rc=%d %s" % (rc, (e or o).strip()[:200]))
    rc, st, _ = g(ROOT, ["status", "--porcelain"])
    rest = [l for l in st.splitlines() if l.strip()]
    print("STATUS-AFTER %d" % len(rest))
    for l in rest[:10]:
        print("  " + l)

    # -- 2) pull --rebase --
    rc, o, e = g(ROOT, ["pull", "--rebase", "origin", "main"])
    tail = (e or o).strip()
    print("PULL-REBASE rc=%d %s" % (rc, tail[-300:] if tail else "up-to-date"))
    if rc != 0:
        rc2, uu, _ = g(ROOT, ["ls-files", "-u"])
        faces = sorted({l.split("\t", 1)[1].strip()
                        for l in uu.splitlines() if "\t" in l})
        print("UU-FACES %d" % len(faces))
        for p in faces:
            print("UU " + p)
        return 1
    rc, cnt, _ = g(ROOT, ["rev-list", "--left-right", "--count",
                          "HEAD...origin/main"])
    print("AHEAD-BEHIND %s" % cnt.strip())
    rc, head, _ = g(ROOT, ["rev-parse", "--short", "HEAD"])
    print("HEAD %s" % head.strip())

    # -- 3) group orders.md delta (added rows, verbatim) --
    rc, rl, _ = g(GROUP, ["reflog", "show", "origin/main", "-n", "4",
                           "--format=%H %gs"], timeout=30)
    tips = [l.split(" ", 1)[0] for l in rl.splitlines()
            if l.strip() and len(l.split(" ", 1)[0]) == 40]
    print("GROUP-REFLOG tips=%s" % ",".join(t[:8] for t in tips))
    rc, new, _ = g(GROUP, ["show", "origin/main:docs/orders.md"], timeout=30)
    old = ""
    for t in tips[1:]:
        rc2, ob, _ = g(GROUP, ["show", t + ":docs/orders.md"], timeout=30)
        if rc2 == 0 and ob:
            old = ob
            print("OLD-TIP %s" % t[:8])
            break
    if old:
        old_lines = set(old.splitlines())
        added = [l for l in new.splitlines()
                 if l not in old_lines and l.strip()]
        print("ORDERS-ADDED %d" % len(added))
        for l in added:
            print("ADD| " + l[:400])
    else:
        print("OLD-BLOB-UNAVAILABLE (reflog shallow) -- full tail follow-up")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
