# r785 bm-b: fetch group-repo CEO-yield-law kit + order O-20261006-2110 via sparse clone (r631 recipe).
import subprocess, tempfile, shutil, os, json, glob

URLS = ["git@github.com:BigRain-11122/FluxGroup.git",
        "https://github.com/BigRain-11122/FluxGroup.git"]
PATHS = ["fleet/orders/", "cph4/fleet/machine-state-kit/", "resource-chain.md"]

d = tempfile.mkdtemp(prefix="kitfetch_")
try:
    ok = False
    for url in URLS:
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)
        r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none",
                            "--sparse", url, d], capture_output=True, text=True, timeout=180)
        if r.returncode == 0:
            ok = True
            break
    if not ok:
        print(json.dumps({"status": "CLONE_FAIL", "err": r.stderr[-400:]}))
        raise SystemExit(2)
    subprocess.run(["git", "-C", d, "sparse-checkout", "set", "--skip-checks"] + PATHS,
                   capture_output=True, timeout=120)
    # locate order file
    hits = glob.glob(os.path.join(d, "fleet", "orders", "*2110*"))
    out = {"status": "OK", "order_files": [], "kit_files": []}
    for h in hits:
        rel = os.path.relpath(h, d).replace(os.sep, "/")
        dst = os.path.join("results", "_r785bmb_grp_" + os.path.basename(h))
        shutil.copyfile(h, dst)
        out["order_files"].append(rel)
    kitdir = os.path.join(d, "cph4", "fleet", "machine-state-kit")
    for root, _, files in os.walk(kitdir):
        for f in files:
            src = os.path.join(root, f)
            rel = os.path.relpath(src, kitdir)
            dst = os.path.join("results", "_r785bmb_kit_" + rel.replace(os.sep, "_"))
            shutil.copyfile(src, dst)
            out["kit_files"].append(rel.replace(os.sep, "/"))
    rc = os.path.join(d, "resource-chain.md")
    if os.path.exists(rc):
        shutil.copyfile(rc, "results/_r785bmb_grp_resource-chain.md")
        out["resource_chain"] = True
    print(json.dumps(out, ensure_ascii=False))
finally:
    shutil.rmtree(d, ignore_errors=True)
