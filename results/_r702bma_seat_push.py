# r702 surgical seat push (r565 law): single-file commit-tree over fresh origin
# tip, deletion-set EMPTY (adapted from _r701bma_seat_push.py).
import subprocess, sys, os, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEAT = "fleet/inbox/MSG-2026-10-04-2349-bma-w120-seat.md"
MSG = ("r702 bm-a W120 seat published=reserved (r565 pre-freeze law): A 283_004..285_003 / "
       "B 65_650..65_849 machine-derived (pre-seat probe rc0, 110th engine wave / bm-a 36th "
       "owned, single state W2..W119; FOUR in-flight upstream seats W116/W117/W118/W119 "
       "honest note -- W119 12/12 burned this window, finalize FAIL-CLOSED on missing W116 "
       "upstream, clean fail) + D-19 receipts (decisions MATCH 4E5BE321 restoration evidence "
       "for MSG-2330 / group orders consumed to f06e044f)")

def run(args, env=None, check=True):
    r = subprocess.run(args, cwd=ROOT, capture_output=True, env=env)
    if check and r.returncode != 0:
        print("FAIL:", args[:4], "->", r.stderr.decode("utf-8", "replace")[:400])
        sys.exit(1)
    return r

run(["git", "fetch", "origin"])
base = run(["git", "rev-parse", "origin/main"]).stdout.decode().strip()
print("base", base)

tmp = tempfile.mktemp(prefix="idx_w120seat_")
env = os.environ.copy()
env["GIT_INDEX_FILE"] = tmp
run(["git", "read-tree", base], env=env)
run(["git", "add", "--", SEAT], env=env)
tree = run(["git", "write-tree"], env=env).stdout.decode().strip()
print("tree", tree)
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
p = run(["git", "push", "origin", f"{commit}:refs/heads/main"], check=False)
out = (p.stdout + p.stderr).decode("utf-8", "replace")
print("push rc", p.returncode, "|", out.strip()[:300])
if p.returncode != 0:
    sys.exit(2)
run(["git", "fetch", "origin"])
tip = run(["git", "rev-parse", "origin/main"]).stdout.decode().strip()
print("origin tip after push:", tip, "==", commit, tip == commit)
assert tip == commit, "DELIVERY FAILED"
s = run(["git", "show", f"origin/main:{SEAT}"]).stdout.decode("utf-8", "replace")
assert "W120 seat published=reserved" in s and "A 283_004..285_003" in s
print("SEAT DELIVERED", commit)
os.remove(tmp)
