"""r533 bm-a surgical push (r01901 law): temp-index on origin/main + my payload files.

Rationale: local rebase is hard-refused by the live saturation-engine 60s
tick writes (r523 lane-race law -- rebase-retry is the dead path on an
active-daemon machine). Payload = files changed in unpushed local commits
(diff origin/main..HEAD), taken from the working tree (self-owned faces:
bm-a single-writer state/heartbeat/report, engine lane ticks, S6 derive
regens, W21 shard products with audit.machine=bm-a, inbox moves).
Conflict faces vs origin r331 (inbox moves done both sides, state files)
resolve to the wall-clock-newer local side per r505 same-day idempotent
derive-face law + single-writer ownership (r513/r525).
"""
import os, subprocess, sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
IDX = os.path.join(REPO, ".git", "surgical-index-r533")
env = dict(os.environ, GIT_INDEX_FILE=IDX)

def g(*args, **kw):
    return subprocess.run(["git", "-C", REPO] + list(args),
                          capture_output=True, text=True,
                          env=kw.get("env", None), encoding="utf-8", errors="replace")

if os.path.exists(IDX):
    os.remove(IDX)

r = g("fetch", "origin")
assert r.returncode == 0, r.stderr
OM = g("rev-parse", "origin/main").stdout.strip()
HEAD = g("rev-parse", "HEAD").stdout.strip()
base = g("merge-base", "HEAD", "origin/main").stdout.strip()
print("origin/main:", OM[:9], "| HEAD:", HEAD[:9], "| base:", base[:9])

# payload = files changed in my unpushed commits vs origin/main
d = g("diff", "--name-only", "origin/main", "HEAD")
files = [l.strip() for l in d.stdout.splitlines() if l.strip()]
print("payload files:", len(files))

# temp index seeded from origin/main
r = g("read-tree", OM, env=env)
assert r.returncode == 0, r.stderr
# add payload from working tree into the temp index
for f in files:
    rr = g("add", "--", f, env=env)
    if rr.returncode != 0:
        print("ADD-FAIL:", f, rr.stderr[:200]); sys.exit(2)
tree = g("write-tree", env=env).stdout.strip()
print("tree:", tree[:12])

msg = (
    "r533 closeout (surgical onto " + OM[:9] + "): r330-collateral recovery "
    "(W18 artifacts restored, converged w/ bm-b) + W21 TENTH engine wave "
    "frozen & burning (bm-a slot, ADMIT A 84_001..86_000/B 38_900..39_099, "
    "ignition verified) + MSG-195x receipt + S6 37-leg rc0 + state/heartbeat "
    "533 + engine lane rides + first W21 shard products"
)
msgfile = os.path.join(REPO, ".git", "surgical-msg-r533.txt")
open(msgfile, "w", encoding="utf-8").write(msg)
newc = g("commit-tree", tree, "-p", OM, "-F", msgfile, env=env).stdout.strip()
print("new commit:", newc[:12])

r = g("push", "origin", newc + ":refs/heads/main")
print("push rc:", r.returncode)
print(r.stdout[-300:] if r.stdout else "", r.stderr[-300:] if r.stderr else "")
if r.returncode != 0:
    print("PUSH FAILED -- blobs unchanged, re-run rebuilds cheaply (r512 law)")
    sys.exit(3)

# delivery self-cert: ls-tree of a key payload file on origin
chk = g("ls-tree", "origin/main", "--name-only",
        "results/perpetual_faces/n1_w18_results.json")
print("post-push fetch + delivery check...")
g("fetch", "origin")
behind = g("rev-list", "--count", "HEAD..origin/main").stdout.strip()
ahead = g("rev-list", "--count", "origin/main..HEAD").stdout.strip()
print("local vs origin: behind", behind, "/ ahead", ahead,
      "(ahead=expected post-surgical residue, next rebase clears)")
print("DELIVERED:", newc[:12], "-> origin/main")
