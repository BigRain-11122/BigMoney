# r785 bm-b: list group repo fleet/orders filenames (locate O-20261006-2110 exact name).
import subprocess, tempfile, shutil, json

d = tempfile.mkdtemp(prefix="ols_")
try:
    subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                    "git@github.com:BigRain-11122/FluxGroup.git", d],
                   capture_output=True, text=True, timeout=180)
    out = subprocess.run(["git", "-C", d, "ls-tree", "HEAD", "fleet/orders/", "--name-only"],
                         capture_output=True, text=True).stdout
    lines = [l for l in out.splitlines() if l.strip()]
    hits = [l for l in lines if "10-06" in l or "2110" in l]
    print(json.dumps({"total": len(lines), "oct06_or_2110": hits}, ensure_ascii=False))
finally:
    shutil.rmtree(d, ignore_errors=True)
