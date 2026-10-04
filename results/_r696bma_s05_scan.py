"""r696 bm-a: orders dual-scan (r477 full-name same-form) + D-19 dual-key."""
import hashlib, json, os, subprocess, glob

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
out = {}

# --- 1) orders ack diff: both sides full filenames ---
orders_dir = os.path.join(ROOT, "fleet", "orders")
disk = {f for f in os.listdir(orders_dir) if f.startswith("O-") and f.endswith(".md")}
hb = json.load(open(os.path.join(ROOT, "fleet", "machines", "bm-a.json"),
                   encoding="utf-8"))
acked = {a for a in hb.get("orders_ack", []) if isinstance(a, str) and a.endswith(".md")}
unacked = sorted(disk - acked)
extra = sorted(acked - disk)
out["orders"] = {"disk_count": len(disk), "ack_count": len(acked),
                 "unacked": unacked, "ack_extra": extra}

# --- 2) D-19 dual-key via state watermarks (per-key hash family) ---
st = json.load(open(os.path.join(ROOT, "state-bm-a.json"), encoding="utf-8"))
def sha_bytes(b, algo):
    h = hashlib.new(algo)
    h.update(b)
    return h.hexdigest()

def group_blob(path):
    # group tree via real-path fetch + show (r660 subprocess raw-bytes law)
    gp = r"C:\Users\sjs20\Desktop\FluxGroup\FluxGroup"
    if not os.path.isdir(gp):
        # S4U fallback (D-20261004-02(3)): sparse clone direct origin
        # blob read -- ssh first (r677), https fallback, unique tempdir.
        import tempfile, shutil
        urls = ["git@github.com:BigRain-11122/FluxGroup.git",
                "https://github.com/BigRain-11122/FluxGroup.git"]
        for url in urls:
            td = tempfile.mkdtemp(prefix="d19_")
            try:
                r = subprocess.run(
                    ["git", "clone", "--depth", "1", "--filter=blob:none",
                     "--sparse", url, td], capture_output=True, timeout=120)
                if r.returncode != 0:
                    continue
                r2 = subprocess.run(
                    ["git", "-C", td, "sparse-checkout", "set", "--skip-checks",
                     path], capture_output=True, timeout=60)
                if r2.returncode != 0:
                    continue
                s = subprocess.run(["git", "-C", td, "show",
                                    "origin/main:" + path], capture_output=True)
                if s.returncode != 0:
                    continue
                return s.stdout, None
            except Exception as ex:
                continue
            finally:
                shutil.rmtree(td, ignore_errors=True)
        return None, "sparse-clone fallback failed (both URLs)"
    r = subprocess.run(["git", "-C", gp, "fetch", "origin"],
                       capture_output=True)
    if r.returncode != 0:
        return None, "fetch fail: " + r.stderr.decode("utf-8", "replace")[:120]
    s = subprocess.run(["git", "-C", gp, "show", "origin/main:" + path],
                       capture_output=True)
    if s.returncode != 0:
        return None, "show fail: " + s.stderr.decode("utf-8", "replace")[:120]
    return s.stdout, None

def method_for(val):
    v = (val or "").strip().lower()
    return "sha1" if len(v) == 40 else "sha256"

res = {}
for path, state_key in (("docs/decisions.md", "last_decisions_sha"),
                       ("docs/orders.md", "last_orders_sha")):
    raw, err = group_blob(path)
    if raw is None:
        res[path] = {"error": err}
        continue
    want = st.get(state_key, "")
    algo = method_for(want)
    got = sha_bytes(raw, algo)
    res[path] = {"algo": algo, "match": got == want.upper(),
                 "stored": want[:16] + "...", "computed": got[:16] + "..."}
out["d19"] = res

with open(os.path.join(ROOT, "results", "_r696bma_s05_scan.json"), "w",
          encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1)[:1800])
