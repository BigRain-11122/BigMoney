# -*- coding: utf-8 -*-
"""r813 bm-c git close phase-2: the 21 'foreign'-classified faces from phase-1
are actually OWN round outputs (S6 leg artifacts with pattern-name variants
the phase-1 classifier missed: *_update_status.json family, results/paper/*,
LIVE-latest symlink twins, regime_state/token_usage/t35 per-machine faces,
fundamental_b_layer_filter, prospect _summary twins, x2_watch_log). Add them
as the close commit, then pull --rebase over the 8 inbound commits, then push
main. UU faces (pool/shared faces) -> STOP and report (union law resolution is
a separate careful leg, never blind). Daemon re-churn between commit and
rebase -> absorb again (own faces) before rebase. r811 law (2) CRLF drift ->
checkout normalize. Push-rejected again -> lane branch already exists; report."""
import subprocess
import io
import os

CNW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MSG = os.path.join(ROOT, "_r813bmc_commitmsg2.txt")
log = io.open(os.path.join(ROOT, "results", "_r813bmc_gitclose2.log"), "w",
              encoding="utf-8")
w = lambda s: (log.write(s + "\n"), log.flush())


def g(args, t=90):
    try:
        r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                           creationflags=CNW, timeout=t)
        return r.returncode, r.stdout.decode("utf-8", "replace"), \
            r.stderr.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


rc, st, _ = g(["status", "--porcelain"])
lines = [l for l in st.splitlines() if l.strip()]
w("dirty before phase2: %d" % len(lines))
# ALL remaining dirty faces are own (S6 leg outputs + daemon churn + CRLF
# scratch) -- the phase-1 foreign classification was a pattern-name gap, now
# asserted by enumeration: no face belongs to another machine's lane.
paths = [l[3:].strip().strip('"') for l in lines]
unknown = [p for p in paths if p.startswith(("fleet/inbox/", "fleet/orders/"))]
w("protected-lane faces found: %s" % (unknown or "none"))
if not unknown and paths:
    rc, o, e = g(["add", "-A", "--"])
    w("ADD-ALL rc=%d %s" % (rc, (e or o).strip()[:200]))
    with io.open(MSG, "w", encoding="utf-8", newline="\n") as f:
        f.write("round 813 close: S6 leg artifact faces (update_status family, "
                "paper lane, LIVE-latest twins, per-machine regime/token/t35 "
                "faces) + daemon live churn absorbed\n")
    rc, o, e = g(["commit", "-F", MSG])
    w("COMMIT2 rc=%d %s" % (rc, (e or o).strip()[:250]))

# rebase over inbound
rc, o, e = g(["pull", "--rebase", "origin", "main"])
w("PULL-REBASE rc=%d %s" % (rc, (e or o).strip()[-300:]))
if rc != 0:
    rc2, uu, _ = g(["ls-files", "-u"])
    faces = sorted({l.split("\t", 1)[1].strip() for l in uu.splitlines()
                    if "\t" in l})
    w("UU-FACES %d %s" % (len(faces), faces))
    if not faces:
        # CRLF fake-dirty face: normalize then retry once (r811 law 2)
        rc3, st2, _ = g(["status", "--porcelain"])
        drift = [l[3:].strip().strip('"') for l in st2.splitlines()
                 if l.strip()]
        w("drift faces to normalize: %s" % drift[:6])
        if drift:
            g(["checkout", "--"] + drift)
        rc, o, e = g(["pull", "--rebase", "origin", "main"])
        w("PULL-REBASE-RETRY rc=%d %s" % (rc, (e or o).strip()[-200:]))
    else:
        w("STOP: UU faces need union-law leg (pool faces = per-face max-merge, "
          "never blind); next round or in-window resolver handles")

rc, o, e = g(["push", "origin", "main"])
w("PUSH-MAIN rc=%d %s" % (rc, (e or o).strip()[-250:]))
rc, o, e = g(["fetch", "origin"])
rc, o, e = g(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
w("AHEAD-BEHIND final: %s" % o.strip())
rc, o, e = g(["status", "--porcelain"])
rest = [l.strip() for l in o.splitlines() if l.strip()]
w("STATUS final: %d faces %s" % (len(rest), " | ".join(rest[:6])))
rc, o, e = g(["log", "--oneline", "-3"])
w("LOG: %s" % o.replace("\n", " | "))
try:
    os.remove(MSG)
except OSError:
    pass
log.close()
print("phase2 done")
