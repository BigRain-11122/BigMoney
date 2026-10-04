"""r679 bm-a D-19 新鲜读探针（r660 subprocess 原字节律+r458 per-key 口径律+r678 实径先例）"""
import hashlib, json, os, subprocess, sys

CANDS = [r"C:\Users\sjs20\Desktop\FluxGroup", "K:\\Fluxgroup\\FluxGroup"]
K = next((c for c in CANDS if os.path.isdir(c) and os.path.isdir(os.path.join(c, ".git"))), None)
if K is None:
    # D-20261004-02③ fallback: 临时 sparse clone 直读 origin blob（r631 bm-b 配方）
    import tempfile
    K = os.path.join(tempfile.gettempdir(), "fluxgroup_d19_sparse")
    if not os.path.isdir(K + os.sep + ".git"):
        r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none",
                            "--sparse", "https://github.com/BigRain-11122/FluxGroup.git", K],
                           capture_output=True)
        if r.returncode != 0:
            print("CLONE_ERR:", r.stderr.decode("utf-8", "replace")[:300]); sys.exit(2)
    subprocess.run(["git", "-C", K, "sparse-checkout", "set", "--skip-checks",
                   "docs/decisions.md", "docs/orders.md"], capture_output=True)
print("tree =", K)

st = json.load(open("state-bm-a.json", encoding="utf-8"))

def git(*args):
    r = subprocess.run(["git", "-C", K] + list(args), capture_output=True)
    if r.returncode != 0:
        return None, r.stderr.decode("utf-8", "replace")
    return r.stdout, None

_, err = git("fetch", "origin")
if err:
    print("FETCH_ERR:", err[:200]); sys.exit(2)

verdicts = {}
for key, path in [("last_decisions_sha", "docs/decisions.md"), ("last_orders_sha", "docs/orders.md")]:
    local_sha = st.get(key, "")
    raw, err = git("show", "origin/main:" + path)
    if raw is None:
        print(f"SHOW_ERR[{key}]:", err[:200]); sys.exit(2)
    origin_sha = hashlib.sha256(raw).hexdigest().upper()
    match = bool(local_sha) and origin_sha == local_sha.upper()
    verdicts[key] = match
    print(f"{key}: local={local_sha[:16]} origin={origin_sha[:16]} VERDICT={'MATCH' if match else 'CHANGED'}")
    if not match:
        txt = raw.decode("utf-8", "replace")
        print(f"--- {path} tail 25 lines ---")
        for l in txt.splitlines()[-25:]:
            print("  ", l[:200])

print("OVERALL:", "MATCH_ZERO_ACTION" if all(verdicts.values()) else "CHANGED_CONSUME")
