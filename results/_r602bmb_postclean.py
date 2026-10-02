# r602 bm-b: post-surgical cleanup per r586 (file-move D+?? twin: blob-identity proof then delete
# untracked leftover), temp artifacts removal, and stage the surgical script receipt.
import subprocess, sys, os, hashlib

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(REPO)

def run(args, check=True):
    p = subprocess.run(args, capture_output=True)
    if check and p.returncode != 0:
        print("FAIL:", args, p.stderr.decode("utf-8", "replace")[:300]); sys.exit(1)
    return p

# 1. r586 blob-identity proof for the moved inbox MSG-0410 (bm-a moved inbox->processed in b3cd4db34)
leftover = os.path.join("fleet", "inbox", "MSG-2026-10-03-0410-bmc-bma.md")
moved = "origin/main:fleet/inbox/processed/MSG-2026-10-03-0410-bmc-bma.md"
if os.path.exists(leftover):
    disk_sha = hashlib.sha256(open(leftover, "rb").read()).hexdigest()
    origin_blob = run(["git", "show", moved]).stdout
    origin_sha = hashlib.sha256(origin_blob).hexdigest()
    print("leftover sha256 :", disk_sha)
    print("origin blob sha256:", origin_sha)
    if disk_sha == origin_sha:
        os.remove(leftover)
        print("BLOB IDENTITY PROVEN -> untracked leftover deleted (r586 zero-loss cleanup)")
    else:
        print("ABORT: blob mismatch, manual adjudication needed"); sys.exit(2)
else:
    print("no leftover present")

# 2. temp artifacts cleanup (untracked, not receipts)
for junk in ("results/_r602bmb_poolheal_td",):
    import shutil
    shutil.rmtree(junk, ignore_errors=True)
    print("removed:", junk)
if os.path.exists("results/_r602bmb_surgical.index"):
    os.remove("results/_r602bmb_surgical.index")
    print("removed: results/_r602bmb_surgical.index")

# 3. stage the surgical script receipt (written after payload build)
run(["git", "add", "--", "results/_r602bmb_surgical.py"])
p = run(["git", "diff", "--cached", "--name-only"])
staged = p.stdout.decode().strip().splitlines()
print("staged:", staged)
assert staged == ["results/_r602bmb_surgical.py"], staged
run(["git", "commit", "-m",
     "round 602 (bm-b): surgical script receipt (_r602bmb_surgical.py, r523/r589 reland executor) + "
     "r586 file-move twin cleanup (inbox MSG-0410 leftover blob-identity proven vs processed/ then deleted) + "
     "heal temp artifacts removed. Follow-up to 716e63164."], check=False)
p = run(["git", "log", "--oneline", "-1"])
print(p.stdout.decode()[:200])
