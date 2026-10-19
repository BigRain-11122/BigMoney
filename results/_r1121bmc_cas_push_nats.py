# -*- coding: utf-8 -*-
# r1121 bm-c: CAS surgical push of the NATS receipt MSG to group-tree origin/main
# (r705 净路: temp-index + commit-tree -p origin/main + push sha:main; 40-hex hard validation r1020 law).
import subprocess, sys, os
sys.stdout.reconfigure(encoding="utf-8")
GRP = r"K:\Fluxgroup\FluxGroup"
MSG = r"cph4/fleet/inbox/MSG-1653-bmc-natsbus.md"
env = dict(os.environ, GIT_INDEX_FILE=os.path.join(GRP, ".git", "cas-index-r1121"))

def g(*args, env_extra=None):
    r = subprocess.run(["git", "-C", GRP] + list(args), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env_extra or os.environ)
    if r.returncode != 0:
        raise SystemExit("GIT FAIL %s: %s" % (args[:3], (r.stderr or "")[:400]))
    return r.stdout.strip()

base = g("rev-parse", "origin/main")
print("base origin/main:", base)
g("read-tree", base, env_extra=env)
blob = subprocess.run(["git", "-C", GRP, "hash-object", "-w", os.path.join(GRP, MSG)],
                      capture_output=True, text=True, encoding="utf-8").stdout.strip()
assert len(blob) == 40 and all(c in "0123456789abcdef" for c in blob), "blob not 40hex: %r" % blob
print("msg blob:", blob)
g("update-index", "--add", "--cacheinfo", "100644,%s,%s" % (blob, MSG), env_extra=env)
tree = g("write-tree", env_extra=env)
assert len(tree) == 40 and all(c in "0123456789abcdef" for c in tree), "tree not 40hex: %r" % tree
print("tree:", tree)
newc = subprocess.run(["git", "-C", GRP, "commit-tree", tree, "-p", base, "-m",
                       "NATS总线bm-c铺装回执(MSG-1653): 三步全PASS bootstrap钉版gh-proxy愈合+心跳任务deploy-ignite 16:48:58+BUS OK+KV rev71+netdiag全文+三机行全绿 [溯源:orders 16:1x @bm-c派单 via bm-a] [bm-c r1121-continuation]"],
                      capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()
assert len(newc) == 40 and all(c in "0123456789abcdef" for c in newc), "commit not 40hex: %r" % newc
print("commit:", newc)
r = subprocess.run(["git", "-C", GRP, "push", "origin", newc + ":refs/heads/main"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
out = (r.stdout + r.stderr)
print("push rc:", r.returncode)
print(out[:400])
low = out.lower()
if r.returncode != 0 or any(k in low for k in ("fatal", "rejected", "failed", "error", "non-fast-forward")):
    raise SystemExit("PUSH FAILED")
ver = g("rev-parse", "origin/main") if False else None
r2 = subprocess.run(["git", "-C", GRP, "fetch", "origin"], capture_output=True, text=True)
r3 = subprocess.run(["git", "-C", GRP, "rev-parse", "origin/main"], capture_output=True, text=True)
print("origin/main after fetch:", r3.stdout.strip())
print("LANDED" if r3.stdout.strip() == newc else "NOT-LANDED (raced?)")
# cleanup temp index
try:
    os.remove(env["GIT_INDEX_FILE"])
except OSError:
    pass
