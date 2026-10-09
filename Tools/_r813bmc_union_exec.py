# -*- coding: utf-8 -*-
"""r813 bm-c C-03 rectification executor (group-tree sync + zero-loss union):
Facts (from _r813bmc_ws_classify.txt):
  - local HEAD = 0 ahead / 121 behind origin/main (pure-behind, no unique commits)
  - fleet-nodes.json + 2 settings.json = STALE SUBSET (origin strictly newer,
    zero local value) -> reset --hard loses nothing
  - gaming/CODELY.md disk superset of origin (+2 local-only memory lines),
    quant/CODELY.md disk superset (+3 local-only lines) -> UNION REQUIRED:
    disk content itself IS the union (origin_minus_disk=0 both faces)
Procedure:
  A) byte-backup both CODELY.md disk faces to bigmoney results/ (insurance)
  B) git reset --hard origin/main  (tree == HEAD sha; A-check PASS face)
  C) copy backed-up superset content back over the fresh files
     (union by construction; git diff vs origin/main = added lines only)
  D) commit + push; push-rejected -> pull --rebase once -> retry once
  E) post-verify: HEAD==origin/main, status of the two faces, diff line count
Every git leg: CREATE_NO_WINDOW + 75s timeout jacket."""
import subprocess
import io
import os
import shutil

CNW = 0x08000000
G = "K:/Fluxgroup/FluxGroup"
R = "K:/Fluxgroup/FluxGroup/quant/bigmoney"
log = io.open(os.path.join(R, "results", "_r813bmc_union_exec.log"), "w",
              encoding="utf-8")
w = lambda s: (log.write(s + "\n"), log.flush())


def g(args, t=75):
    try:
        r = subprocess.run(["git", "-C", G] + args, capture_output=True,
                           creationflags=CNW, timeout=t)
        return r.returncode, r.stdout.decode("utf-8", "replace"), \
            r.stderr.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


UNION_FACES = ["gaming/CODELY.md", "quant/CODELY.md"]
MSG = os.path.join(G, "_r813bmc_unionmsg.txt")

# --- A) byte backup ---
for f in UNION_FACES:
    src = os.path.join(G, f.replace("/", "\\"))
    dst = os.path.join(R, "results", "_r813bmc_union_backup_" +
                       f.replace("/", "_"))
    shutil.copyfile(src, dst)
    w("BACKUP %s -> %s (%dB)" % (f, dst, os.path.getsize(dst)))

# --- B) reset --hard origin/main ---
rc, o, e = g(["reset", "--hard", "origin/main"])
w("RESET rc=%d %s %s" % (rc, o.strip()[:120], e.strip()[:200]))
rc, o, e = g(["rev-parse", "HEAD", "origin/main"])
w("HEAD now: %s" % o.replace("\n", " "))

# --- C) union re-apply (superset copy-back) ---
for f in UNION_FACES:
    src = os.path.join(R, "results", "_r813bmc_union_backup_" +
                       f.replace("/", "_"))
    dst = os.path.join(G, f.replace("/", "\\"))
    shutil.copyfile(src, dst)
    w("UNION-APPLY %s (%dB)" % (f, os.path.getsize(dst)))

# --- D) commit + push ---
rc, o, e = g(["add", "--"] + UNION_FACES)
w("ADD rc=%d %s" % (rc, (e or o).strip()[:150]))
with io.open(MSG, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("bm-c r813 workspace union (C-20261009-03 rectification): "
             "2 gaming + 3 quant local-only memory entries re-linked "
             "(append-only union, zero loss; disk was strict superset)\n")
rc, o, e = g(["commit", "-F", MSG])
w("COMMIT rc=%d %s" % (rc, (e or o).strip()[:250]))
rc, o, e = g(["push", "origin", "main"])
w("PUSH rc=%d %s" % (rc, (e or o).strip()[:300]))
if rc != 0:
    rc2, o2, e2 = g(["pull", "--rebase", "origin", "main"])
    w("PULL-REBASE rc=%d %s" % (rc2, (e2 or o2).strip()[-250:]))
    if rc2 == 0:
        rc, o, e = g(["push", "origin", "main"])
        w("PUSH-RETRY rc=%d %s" % (rc, (e or o).strip()[:300]))

# --- E) post-verify ---
rc, o, e = g(["rev-parse", "HEAD", "origin/main"])
w("VERIFY head==origin: %s" % (
    o.split()[0] == o.split()[1] if len(o.split()) >= 2 else "?"))
rc, o, e = g(["status", "--porcelain"])
w("STATUS after: %s" % " | ".join(
    [l.strip() for l in o.splitlines() if l.strip()][:12]))
for f in UNION_FACES:
    rc, o, e = g(["diff", "--numstat", "origin/main", "--", f])
    w("DIFF %s vs origin/main: %s" % (f, o.strip()[:80]))
rc, o, e = g(["log", "--oneline", "-2"])
w("LOG top: %s" % o.replace("\n", " | "))
try:
    os.remove(MSG)
except OSError:
    pass
log.close()
print("union exec done")
