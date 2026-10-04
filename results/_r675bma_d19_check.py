"""r675 bm-a D-19 decisions.md 新鲜读探针（r660 subprocess 原字节律+r458 per-key 口径律）"""
import hashlib, json, subprocess, sys

K = "K:\\Fluxgroup\\FluxGroup"
if not __import__("os").path.isdir(K):
    # D-20261004-02③ fallback: 临时 sparse clone 直读 origin blob（r631 bm-b 配方）
    import tempfile, os
    K = os.path.join(tempfile.gettempdir(), "fluxgroup_d19_sparse")
    if not os.path.isdir(K + os.sep + ".git"):
        r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none",
                            "--sparse", "https://github.com/BigRain-11122/FluxGroup.git", K],
                           capture_output=True)
        if r.returncode != 0:
            print("CLONE_ERR:", r.stderr.decode("utf-8", "replace")[:300]); sys.exit(2)
    subprocess.run(["git", "-C", K, "sparse-checkout", "set", "--skip-checks",
                   "docs/decisions.md", "docs/orders.md"], capture_output=True)

st = json.load(open("state-bm-a.json", encoding="utf-8"))
local_sha = st.get("last_decisions_sha", "")

def git(*args, cwd=None):
    r = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True)
    if r.returncode != 0:
        return None, r.stderr.decode("utf-8", "replace")
    return r.stdout, None

if not local_sha:
    print("NO_LOCAL_WATERMARK")
    sys.exit(0)

_, err = git("-C", K, "fetch", "origin")
if err:
    print("FETCH_ERR:", err[:200]); sys.exit(2)

raw, err = git("-C", K, "show", "origin/main:docs/decisions.md")
if raw is None:
    print("SHOW_ERR:", err[:200]); sys.exit(2)

origin_sha = hashlib.sha256(raw).hexdigest().upper()
match = origin_sha == local_sha.upper()
print(f"local_watermark={local_sha}")
print(f"origin_sha256 = {origin_sha}")
print("VERDICT:", "MATCH" if match else "CHANGED")

# orders.md 同律
raw_o, err_o = git("-C", K, "show", "origin/main:docs/orders.md")
if raw_o is not None:
    print("orders_sha256 =", hashlib.sha256(raw_o).hexdigest().upper()[:16], "(physical-件区 CEO 待办)")
    txt = raw_o.decode("utf-8", "replace")
    lines = [l for l in txt.splitlines() if ("BigMoney" in l or "quant" in l) and ("CEO" in l.upper() or "待" in l)]
    print("orders_his_lines=", len(lines))
    for l in lines[-8:]:
        print("  ORD:", l[:160])
if not match:
    txt = raw.decode("utf-8", "replace")
    st_lines = txt.splitlines()
    print("--- decisions tail 30 lines ---")
    for l in st_lines[-30:]:
        print("  ", l[:200])
