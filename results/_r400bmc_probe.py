"""r400 bm-c probe: temp-repo git show stderr text for a missing path
(MSG-0612 proposal-2 selftest leg diagnosis). Evidence file, keep."""
import tempfile
import subprocess
import os

NO = 0x08000000


def g(args, repo):
    return subprocess.run(["git", "-C", repo] + args,
                          capture_output=True, creationflags=NO)


td = tempfile.mkdtemp()
repo = os.path.join(td, "repo")
g(["init", "-q", "--initial-branch=main", repo], td)
os.makedirs(os.path.join(repo, "results"), exist_ok=True)
with open(os.path.join(repo, "results", "a.txt"), "w") as fh:
    fh.write("x")
g(["add", "-A"], repo)
g(["-c", "user.name=st", "-c", "user.email=st@t",
  "commit", "-q", "-m", "base"], repo)
r = g(["show", "HEAD:results/runnable_pool.json"], repo)
print("rc=", r.returncode)
print("stderr=", repr(r.stderr.decode(errors="replace")))
f = g(["fetch", "origin"], repo)
print("fetch rc=", f.returncode,
      "fetch err=", f.stderr.decode(errors="replace")[:120])
r2 = g(["show", "HEAD:results/runnable_pool.json"], repo)
print("rc2=", r2.returncode,
      "stderr2=", repr(r2.stderr.decode(errors="replace")))
