# r669 bm-a D-19 watermark check: decisions (SHA-256) + group orders (SHA-1 per-key caliber, r458 law)
# raw bytes via python subprocess git show (r660 law); zero PS pipeline.
import subprocess, hashlib, json, io, sys, os

CANDIDATES = [
    r"K:\Fluxgroup\FluxGroup",
    r"C:\Users\sjs20\Desktop\FluxGroup",
]

SPARSE_URL = "https://github.com/BigRain-11122/FluxGroup.git"

def pick_repo():
    for p in CANDIDATES:
        if os.path.isdir(p) and os.path.isdir(os.path.join(p, ".git")):
            return p, False
    # sparse-clone fallback (r631 bm-b recipe; zero resident tree)
    tmp = os.path.join(os.environ.get("TEMP", "."), "_r669bma_grp_sparse")
    if not os.path.isdir(tmp):
        subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none",
                        "--sparse", SPARSE_URL, tmp], capture_output=True, timeout=300)
    subprocess.run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks",
                    "docs/decisions.md", "docs/orders.md"], capture_output=True, timeout=120)
    subprocess.run(["git", "-C", tmp, "fetch", "origin"],
                   capture_output=True, timeout=300)
    return tmp, True

def main():
    out = {"repo": None, "decisions_sha256": None, "orders_sha1": None}
    repo, sparse = pick_repo()
    if repo is None:
        out["error"] = "no group tree path available"
        print(json.dumps(out, ensure_ascii=False))
        return 0
    out["sparse_fallback"] = sparse
    subprocess.run(["git", "-C", repo, "fetch", "origin"],
                   capture_output=True, timeout=120)
    # both state keys are 64-hex = SHA-256 caliber (verified by length; r458 per-key law)
    for path, algo, key in (("docs/decisions.md", "sha256", "decisions_sha256"),
                            ("docs/orders.md", "sha256", "orders_sha256")):
        r = subprocess.run(["git", "-C", repo, "show", "origin/main:%s" % path],
                           capture_output=True, timeout=60)
        if r.returncode != 0:
            out[key] = "RC%d" % r.returncode
            continue
        out[key] = hashlib.new(algo, r.stdout).hexdigest()
    out["repo"] = repo
    # compare with state watermark keys
    try:
        st = json.load(io.open(os.path.join(os.path.dirname(__file__), "..", "state-bm-a.json"),
                                encoding="utf-8"))
        out["state_decisions_sha"] = st.get("last_decisions_sha")
        out["state_orders_sha"] = st.get("last_orders_sha")
        out["decisions_match"] = (out["decisions_sha256"] == st.get("last_decisions_sha"))
        out["orders_match"] = (out["orders_sha256"] == st.get("last_orders_sha"))
    except Exception as e:
        out["state_error"] = repr(e)
    with io.open(os.path.join(os.path.dirname(__file__), "_r669bma_d19_check.json"), "w",
                 encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
