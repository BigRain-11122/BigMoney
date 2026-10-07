"""r700 bm-c rebase E42 third-state escape (r835 canon 3-step):
1) manual commit of resolved r699-close pick via author-script env
   injection + -F .git/rebase-merge/message (r808 author-date law);
2) git rebase --quit (abandon stuck sequence);
3) symbolic-ref detached self-check -> branch -f main HEAD + checkout main
   (r624 law);
then content-equivalent rebuild of remaining todo (5 churn-absorb picks,
all daemon live-faces superseded by current worktree state) as ONE fresh
absorb commit per r835 precedent. Push + origin-verify tail."""
import os
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
RB = os.path.join(REPO, ".git", "rebase-merge")
MSGFILE = os.path.join(REPO, "_r700bmc_commitmsg.txt")


def git(args, env=None, check=True):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True, env=env)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    if check and p.returncode != 0:
        print("GIT FAIL rc=%d: %s" % (p.returncode, out[:400]))
        raise SystemExit(2)
    return p.returncode, out


def parse_author_script():
    raw = open(os.path.join(RB, "author-script"), "rb").read()
    vals = {}
    for ln in raw.split(b"\n"):
        if b"=" not in ln:
            continue
        k, v = ln.split(b"=", 1)
        v = v.strip()
        if v.startswith(b"'") and v.endswith(b"'"):
            v = v[1:-1]
        try:
            vals[k.decode()] = v.decode("gbk")
        except Exception:
            vals[k.decode()] = v.decode("utf-8", "replace")
    return vals


# -- step 1: manual commit of the resolved pick --
env = os.environ.copy()
av = parse_author_script()
env["GIT_AUTHOR_NAME"] = av.get("GIT_AUTHOR_NAME", "")
env["GIT_AUTHOR_EMAIL"] = av.get("GIT_AUTHOR_EMAIL", "")
env["GIT_AUTHOR_DATE"] = av.get("GIT_AUTHOR_DATE", "")
print("author env:", {k: env[k] for k in ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_AUTHOR_DATE")})
rc, out = git(["commit", "-F", os.path.join(RB, "message")], env=env, check=False)
print("commit rc=%d" % rc)
print(out[:400])
assert rc == 0, "manual pick commit failed"

# -- step 2: rebase --quit --
rc, out = git(["rebase", "--quit"], check=False)
print("rebase --quit rc=%d" % rc)

# -- step 3: detached check + branch re-home --
rc, out = git(["symbolic-ref", "HEAD"], check=False)
if rc != 0:
    print("HEAD detached as expected -> re-home main")
    rc, out = git(["branch", "-f", "main", "HEAD"])
    print("branch -f rc=%d" % rc)
    rc, out = git(["checkout", "main"], check=False)
    print("checkout main rc=%d" % rc)
    print(out[:200])
else:
    print("HEAD on ref:", out.strip())

rc, out = git(["log", "--oneline", "-3"])
print(out)

# -- step 4: content-equivalent rebuild = ONE fresh churn absorb --
targets = [
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/pool_red_flags.jsonl",
    "results/runnable_pool.bm-c.json",
    "results/runnable_pool.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
    "Tools/_r700bmc_s0.py",
    "Tools/_r700bmc_s0_absorb.py",
    "Tools/_r700bmc_rebase_resolve.py",
    "results/_r700bmc_s0_facts.json",
]
live = [t for t in targets if os.path.exists(os.path.join(REPO, t))]
rc, out = git(["add", "--"] + live)
print("add rc=%d files=%d" % (rc, len(live)))
with open(MSGFILE, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("lane: bm-c daemon churn absorb r700 post-quit rebuild (r620/r832/r835 laws; replaces 5 stale absorb picks with current live face state)\n")
rc, out = git(["commit", "-F", MSGFILE], check=False)
print("rebuild absorb commit rc=%d" % rc)
print(out[:200])

# -- push + origin verify --
rc, out = git(["push"], check=False)
print("push rc=%d" % rc)
print(out[-400:])
rc, out = git(["fetch", "origin"])
rc, out = git(["rev-list", "--count", "HEAD..origin/main"])
behind = int(out.strip() or 0)
rc, out = git(["rev-list", "--count", "origin/main..HEAD"])
ahead = int(out.strip() or 0)
print("behind=%d ahead=%d" % (behind, ahead))
rc, out = git(["status", "--porcelain"])
print("dirty:", out.strip() or "(clean)")
