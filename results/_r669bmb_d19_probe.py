# r669 S0.5 watermark + orders dual-scan probe (r631 recipe / r458 per-key caliber / r660 subprocess-raw-bytes law)
import subprocess, hashlib, json, os, sys, tempfile, shutil

OUT = r"results\_r669bmb_d19_probe_out.json"
res = {"ts": "2026-10-04", "runner": "r669 bm-b"}

def git_raw_bytes(repo, args, timeout=90):
    p = subprocess.run(["git", "-C", repo] + args, capture_output=True, timeout=timeout)
    if p.returncode != 0:
        return None, p.stderr.decode("utf-8", "replace")[:300]
    return p.stdout, None

def sha_of(data, algo):
    h = hashlib.new(algo)
    h.update(data)
    return h.hexdigest().upper()

# --- locate group tree (K: first, local real paths fallback, temp sparse clone last) ---
group_repo = None
k_path = r"K:\Fluxgroup\FluxGroup"
cand = [k_path, r"C:\Fluxgroup\FluxGroup"]
for c in cand:
    if os.path.isdir(os.path.join(c, ".git")):
        group_repo = c
        res["group_repo_source"] = c
        break
if group_repo is None:
    # temp sparse clone (zero persistent tree)
    tmp = tempfile.mkdtemp(prefix="fg-sparse-")
    p = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                        "https://github.com/BigRain-11122/FluxGroup.git", tmp],
                       capture_output=True, timeout=300)
    if p.returncode == 0:
        subprocess.run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks", "docs/decisions.md", "docs/orders.md"],
                      capture_output=True, timeout=120)
        group_repo = tmp
        res["group_repo_source"] = "temp-sparse-clone"
    else:
        res["group_repo_error"] = p.stderr.decode("utf-8", "replace")[:300]

# --- decisions.md SHA-256 + orders.md SHA-1 from origin blob raw bytes ---
if group_repo:
    subprocess.run(["git", "-C", group_repo, "fetch", "origin"], capture_output=True, timeout=120)
    dec, err = git_raw_bytes(group_repo, ["show", "origin/main:docs/decisions.md"])
    if dec is not None:
        res["decisions_sha256"] = sha_of(dec, "sha256")
    else:
        res["decisions_err"] = err
    grp, err = git_raw_bytes(group_repo, ["show", "origin/main:docs/orders.md"])
    if grp is not None:
        res["group_orders_sha1"] = sha_of(grp, "sha1")
    else:
        res["group_orders_err"] = err
    if res.get("group_repo_source") == "temp-sparse-clone":
        shutil.rmtree(tmp, ignore_errors=True)

# --- fleet orders same-caliber set diff: ls-tree HEAD vs heartbeat orders_ack ---
repo = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
out, err = git_raw_bytes(repo, ["ls-tree", "--name-only", "HEAD", "fleet/orders/"])
disk_orders = set()
if out is not None:
    for line in out.decode("utf-8").splitlines():
        base = os.path.basename(line.strip())
        if base.startswith("O-") and base.endswith(".md"):
            disk_orders.add(base)
with open(os.path.join(repo, "fleet", "machines", "bm-b.json"), "rb") as f:
    hb = json.loads(f.read().decode("utf-8"))
ack = set(hb.get("orders_ack", []))
res["orders_disk_count"] = len(disk_orders)
res["orders_ack_count"] = len(ack)
res["orders_unacked"] = sorted(disk_orders - ack)
res["orders_ack_orphan"] = sorted(ack - disk_orders)

with open(os.path.join(repo, OUT), "wb") as f:
    f.write(json.dumps(res, ensure_ascii=True, indent=1).encode("ascii"))
print("PROBE-DONE")
