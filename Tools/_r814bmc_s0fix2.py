# -*- coding: utf-8 -*-
"""r814 bm-c S0 fixer leg 2: origin/main already fetched (18:07-18:09 window),
so skip the fetch leg entirely -- checkout renormalize + DIRECT
`git rebase origin/main` in a tight retry loop (max 4) to dodge the live
daemon mid-write race (autofill/dispatcher/saturation faces rewrite every
~minute; r811 three-reject precedent). Zero autostash (r642 law). UU faces
reported only (pit-git-surgery domain, no unilateral resolution).
Then: inbound commit subjects + group orders.md added-rows (verbatim, CEO
to-do physical-item zone consumption face). CREATE_NO_WINDOW + jackets."""
import subprocess
import time

CNW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"


def g(cwd, args, timeout=75):
    try:
        r = subprocess.run(["git", "-C", cwd] + args, capture_output=True,
                           creationflags=CNW, timeout=timeout)
        return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
            (r.stderr or b"").decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def rebase_once():
    rc, st, _ = g(ROOT, ["status", "--porcelain"])
    drift = [l[3:].strip().strip('"') for l in st.splitlines()
             if l.strip() and l.strip()[0] in "MMARC"]
    if drift:
        rc, o, e = g(ROOT, ["checkout", "--"] + drift)
        if rc != 0:
            return False, "checkout rc=%d %s" % (rc, (e or o)[:150])
    rc, o, e = g(ROOT, ["rebase", "origin/main"])
    if rc == 0:
        return True, "REBASE-OK"
    uu_probe = g(ROOT, ["ls-files", "-u"])[1]
    if "\t" in uu_probe:
        return None, "UU-CONFLICT"   # hard stop, surgery domain
    return False, "refuse: %s" % (e or o).strip()[:200]


def main():
    rc, o, _ = g(ROOT, ["log", "--format=%h %an %s",
                        "HEAD..origin/main"], timeout=30)
    print("INBOUND (pre-rebase):")
    for l in o.splitlines():
        if l.strip():
            print("  IN| " + l[:160])
    ok, msg = False, ""
    for i in range(1, 5):
        ok, msg = rebase_once()
        print("ATTEMPT-%d %s %s" % (i, "OK" if ok is True else
                                    ("UU-STOP" if ok is None else "retry"),
                                   msg[:180]))
        if ok is not None:
            break
        time.sleep(2)
    if ok is not True:
        print("REBASE-FINAL: %s" % ("UU-CONFLICT surgery domain" if ok is None
                                    else "still refused after 4 attempts"))
        return 1
    rc, cnt, _ = g(ROOT, ["rev-list", "--left-right", "--count",
                          "HEAD...origin/main"])
    print("AHEAD-BEHIND %s" % cnt.strip())
    rc, head, _ = g(ROOT, ["rev-parse", "--short", "HEAD"])
    print("HEAD %s" % head.strip())

    # -- group orders.md delta: added rows verbatim --
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
            print("ADD| " + l[:500])
    else:
        print("OLD-BLOB-UNAVAILABLE -- will re-derive via state watermark")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
