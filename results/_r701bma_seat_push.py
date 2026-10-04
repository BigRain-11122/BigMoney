# r701 surgical seat push (r565 law): single-file commit-tree over HEAD, deletion-set EMPTY.
# Tree is dirty with daemon faces -> temp index surgical path (r436 law family).
import subprocess, sys, os, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEAT = "fleet/inbox/MSG-2026-10-04-2323-bma-w119-seat.md"
MSG = ("r701 bm-a W119 seat published=reserved (r565 pre-freeze law): A 281_004..283_003 / "
       "B 65_450..65_649 machine-derived (pre-seat probe rc0, 109th engine wave / bm-a 35th "
       "owned, single state W2..W118; THREE in-flight upstream seats W116/W117/W118 honest "
       "note) + D-19 receipts (decisions regression state recorded / group orders consumed "
       "to 34BCD6B5, L279 non-BigMoney zero action)")

def run(args, env=None, check=True):
    r = subprocess.run(args, cwd=ROOT, capture_output=True, env=env)
    if check and r.returncode != 0:
        print("FAIL:", args[:4], "->", r.stderr.decode("utf-8", "replace")[:400])
        sys.exit(1)
    return r

run(["git", "fetch", "origin"])
# base must be origin/main tip at push time; work on fresh base
base = run(["git", "rev-parse", "origin/main"]).stdout.decode().strip()
print("base", base)

tmp = tempfile.mktemp(prefix="idx_w119seat_")
env = os.environ.copy()
env["GIT_INDEX_FILE"] = tmp
run(["git", "read-tree", base], env=env)
run(["git", "add", "--", SEAT], env=env)  # adds only the seat file to the temp index
tree = run(["git", "write-tree"], env=env).stdout.decode().strip()
print("tree", tree)
# deletion-set proof: diff-tree base->tree must show ONLY the seat as added
d = run(["git", "diff-tree", "--name-status", "-r", base, tree]).stdout.decode()
print("diff-tree:", d.strip())
lines = [l for l in d.strip().splitlines() if l]
assert len(lines) == 1 and lines[0].startswith("A") and lines[0].endswith(SEAT), \
    f"deletion-set / payload violation: {lines}"
sha = subprocess.run(["git", "commit-tree", tree, "-p", base, "-m", MSG],
                     cwd=ROOT, capture_output=True)
if sha.returncode != 0:
    print("commit-tree FAIL:", sha.stderr.decode()[:300]); sys.exit(1)
commit = sha.stdout.decode().strip()
print("commit", commit)
# CAS push: only fast-forward from base
p = run(["git", "push", "origin", f"{commit}:refs/heads/main"], check=False)
out = (p.stdout + p.stderr).decode("utf-8", "replace")
print("push rc", p.returncode, "|", out.strip()[:300])
if p.returncode != 0:
    sys.exit(2)
# delivery proof: fetch + ls-remote
run(["git", "fetch", "origin"])
tip = run(["git", "rev-parse", "origin/main"]).stdout.decode().strip()
print("origin tip after push:", tip, "==", commit, tip == commit)
assert tip == commit, "DELIVERY FAILED"
# verify seat content on origin
s = run(["git", "show", f"origin/main:{SEAT}"]).stdout.decode("utf-8", "replace")
assert "W119 seat published=reserved" in s and "A 281_004..283_003" in s
print("SEAT DELIVERED", commit)
os.remove(tmp)
