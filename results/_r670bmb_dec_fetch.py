# r670 bm-b: fetch current group decisions.md for consumption (changed watermark)
import subprocess, sys, tempfile, shutil, os

URL = "https://github.com/BigRain-11122/FluxGroup.git"
OUTDUMP = os.path.join(tempfile.gettempdir(), "fg_decisions_r670.md")

def run(args, cwd=None):
    p = subprocess.run(args, capture_output=True, cwd=cwd)
    return p.returncode, p.stdout, p.stderr

tmp = tempfile.mkdtemp(prefix="fgd19r-")
try:
    rc, so, se = run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", URL, tmp])
    if rc != 0:
        print("CLONE_FAIL", se.decode("utf-8", "replace")[:300]); sys.exit(2)
    rc, so, se = run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks", "docs/decisions.md"])
    if rc != 0:
        print("SPARSE_FAIL", se.decode("utf-8", "replace")[:300]); sys.exit(2)
    rc, so, se = run(["git", "-C", tmp, "show", "origin/main:docs/decisions.md"])
    if rc != 0:
        print("SHOW_FAIL", se.decode("utf-8", "replace")[:300]); sys.exit(2)
    open(OUTDUMP, "wb").write(so)
    print("DUMP_OK", OUTDUMP, len(so), "bytes")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
