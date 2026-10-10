import subprocess, hashlib, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GIT = r"C:\Program Files\Git\cmd\git.exe"

# 1. Registry-class prereg: extract-aside lawful recovery (worktree copy ABSENT,
#    local HEAD blob = sole copy in existence; not an origin restore)
blob = subprocess.run([GIT, "show", "HEAD:research/PERPETUAL_N1_W205_PREREG.md"],
                      capture_output=True).stdout
head_blob_sha = subprocess.run([GIT, "rev-parse", "HEAD:research/PERPETUAL_N1_W205_PREREG.md"],
                               capture_output=True, text=True).stdout.strip()
with open("research/PERPETUAL_N1_W205_PREREG.md", "wb") as f:
    f.write(blob)
got_sha = hashlib.sha256(blob).hexdigest()
print(f"prereg recovered bytes={len(blob)} head_blob={head_blob_sha[:16]} sha256={got_sha[:16]}")

# 2. Reproducible-artifact class: plain checkout from local HEAD
paths = ["results/_r963bma_w205_cfgprobe.py", "results/_r963bma_w205_cfgprobe2.py",
         "results/_r963bma_w205_counts.py", "results/_r963bma_w205_extract.py",
         "results/_r963bma_w205_freeze.py", "results/_r963bma_w205_freeze_receipt.json",
         "results/_r963bma_w205_freeze_receipt_dryrun.json",
         "results/_r963bma_w205_preprobe.py", "results/_r963bma_w205_receipt_patch.py"]
r = subprocess.run([GIT, "checkout", "HEAD", "--"] + paths, capture_output=True, text=True)
print("checkout rc=", r.returncode, r.stderr[:200])

# 3. Untracked collision comparison: local file vs origin blob
for lp, ob in [("fleet/orders/O-20261011-0012-bm-a.md", "4908a9f458afca03d42b95f6c1c9b9c9c5d5d871"),
               ("results/_r849bmb_closeout.py", "961fe4360dd7895b13123f35cb1305206e5eaab8")]:
    local = open(lp, "rb").read()
    same = hashlib.sha256(local).hexdigest() == hashlib.sha256(
        subprocess.run([GIT, "cat-file", "blob", ob], capture_output=True).stdout).hexdigest()
    # compare via git hash-object for exact blob-id comparison
    ho = subprocess.run([GIT, "hash-object", "--", lp], capture_output=True, text=True).stdout.strip()
    print(f"{lp}: local_blob={ho[:16]} origin_blob={ob[:16]} identical={ho == ob}")
    if ho == ob:
        os.remove(lp)
        print(f"  -> removed untracked duplicate (origin version arrives via rebase)")
