"""r400 bm-c probe 2: reproduce the failing selftest leg end-to-end
against the real Tools/git_claw module. Evidence file, keep."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Tools.git_claw as claw  # noqa: E402

NO = claw._NO_WINDOW


def g(args, repo):
    return claw._git(args, repo)


td = tempfile.mkdtemp()
repo = os.path.join(td, "repo")
g(["init", "-q", "--initial-branch=main", repo], td)
os.makedirs(os.path.join(repo, "results"), exist_ok=True)
with open(os.path.join(repo, "results", "a.txt"), "w") as fh:
    fh.write("x")
g(["add", "-A"], repo)
g(["-c", "user.name=st", "-c", "user.email=st@t",
  "commit", "-q", "-m", "base"], repo)
pre = g(["rev-parse", "HEAD"], repo).stdout.decode().strip()

fp = os.path.join(repo, *claw.POOL_PATH.split("/"))
with open(fp, "w") as fh:
    fh.write('{"version": "t", "entries": [{"id": "E1", "shards": '
             '[{"key": "S1", "owner": "bm-z", '
             '"owner_since": "2026-10-03 10:00:00", '
             '"status": "claimed"}]}]}')
g(["add", claw.POOL_PATH], repo)
g(["-c", "user.name=st", "-c", "user.email=st@t",
  "commit", "-q", "-m", "pool1"], repo)
p1 = g(["rev-parse", "HEAD"], repo).stdout.decode().strip()

r_old = claw._pool_owner_since_map(pre, repo)
print("old_map =", r_old)
try:
    r_new = claw._pool_owner_since_map(p1, repo)
    print("new_map =", r_new)
except Exception as exc:
    print("new_map RAISED:", repr(exc))
print("regressions =",
      claw.pool_claim_regressions(pre, p1, repo))
