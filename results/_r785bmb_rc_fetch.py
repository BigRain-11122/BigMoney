# r785 bm-b: locate + fetch resource-chain.md (CEO-yield law sec.6 full text) from group repo.
import subprocess, tempfile, shutil, os, json

d = tempfile.mkdtemp(prefix="rcfind_")
try:
    subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                    "git@github.com:BigRain-11122/FluxGroup.git", d],
                   capture_output=True, text=True, timeout=180)
    out = subprocess.run(["git", "-C", d, "ls-tree", "-r", "HEAD", "--name-only"],
                         capture_output=True, text=True).stdout
    cands = [l for l in out.splitlines() if "resource-chain" in l.lower()]
    print(json.dumps({"candidates": cands}))
    if cands:
        subprocess.run(["git", "-C", d, "sparse-checkout", "set", "--skip-checks"] + cands,
                       capture_output=True, timeout=120)
        for c in cands:
            p = os.path.join(d, c.replace("/", os.sep))
            if os.path.exists(p):
                dst = "results/_r785bmb_grp_" + os.path.basename(c)
                shutil.copyfile(p, dst)
                print("saved:", dst, os.path.getsize(dst), "bytes")
finally:
    shutil.rmtree(d, ignore_errors=True)
