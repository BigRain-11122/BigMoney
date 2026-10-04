# r701 bm-b: D-19 new-content read (sparse clone, r677/r700 recipe reuse)
import subprocess, tempfile, shutil, os, sys

URLS = ["git@github.com:BigRain-11122/FluxGroup.git",
        "https://github.com/BigRain-11122/FluxGroup.git"]
out = {}
d = tempfile.mkdtemp(prefix="d19read_")
try:
    ok = False
    for url in URLS:
        r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none",
                             "--sparse", url, d],
                            capture_output=True, text=True, timeout=180)
        if r.returncode == 0:
            ok = True
            break
        shutil.rmtree(d, ignore_errors=True)
        try:
            os.makedirs(d)
        except OSError:
            pass
    if not ok:
        print("CLONE_FAIL")
        sys.exit(2)
    subprocess.run(["git", "-C", d, "sparse-checkout", "set", "--skip-checks",
                    "docs/decisions.md", "docs/orders.md"],
                   capture_output=True, timeout=120)
    for name in ["docs/decisions.md", "docs/orders.md"]:
        p = os.path.join(d, name.replace("/", os.sep))
        try:
            with open(p, "rb") as f:
                b = f.read()
        except OSError:
            b = b""
        w = os.path.join("results", "_r701bmb_" + os.path.basename(name))
        with open(w, "wb") as f:
            f.write(b)
        out[name] = len(b)
    print(out)
finally:
    shutil.rmtree(d, ignore_errors=True)
