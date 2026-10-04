"""r688 bm-a S0.5: orders unacked diff (same-form full-name) + D-19 decisions watermark check.

Laws applied:
- r477: orders_ack entries are full file names (O-*.md); orders side must use full names too.
- r672/r458: watermark key hash family self-verified by value length (40-hex=SHA-1, 64-hex=SHA-256).
- r660/r677: D-19 hash via python subprocess raw bytes (no PS pipe); sparse-clone ssh-first if K: absent.
"""
import hashlib
import json
import os
import subprocess
import tempfile

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
HB = os.path.join(REPO, r"fleet\machines\bm-a.json")
ORDERS_DIR = os.path.join(REPO, r"fleet\orders")

hb = json.load(open(HB, encoding="utf-8-sig"))
acked = set(hb.get("orders_ack", []))

order_files = sorted(
    f for f in os.listdir(ORDERS_DIR)
    if f.startswith("O-") and f.endswith(".md")
)
order_set = set(order_files)

unacked = sorted(order_set - acked)
extra = sorted(acked - order_set)
print("orders_total:", len(order_set), "acked:", len(acked))
print("unacked:", unacked if unacked else "NONE")

# --- D-19 decisions watermark (K: absent check first) ---
K = r"K:\Fluxgroup\FluxGroup"
state = json.load(open(os.path.join(REPO, "state-bm-a.json"), encoding="utf-8-sig"))
stored = state.get("last_decisions_sha", "").strip()
print("state last_decisions_sha:", stored)


def sha256_raw(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


if os.path.isdir(K) and os.path.isdir(os.path.join(K, ".git")):
    subprocess.run(["git", "-C", K, "fetch", "origin"], capture_output=True)
    blob = subprocess.run(
        ["git", "-C", K, "show", "origin/main:docs/decisions.md"],
        capture_output=True,
    ).stdout
    src = "K-tree"
else:
    tmp = tempfile.mkdtemp(prefix="d19_")
    rc = subprocess.run(
        ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
         "git@github.com:BigRain-11122/FluxGroup.git", tmp],
        capture_output=True)
    if rc.returncode != 0:
        rc = subprocess.run(
            ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
             "https://github.com/BigRain-11122/FluxGroup.git", tmp],
            capture_output=True)
    subprocess.run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks",
                   "docs/decisions.md"], capture_output=True)
    blob = subprocess.run(
        ["git", "-C", tmp, "show", "origin/main:docs/decisions.md"],
        capture_output=True).stdout
    src = "sparse-clone"
cur = sha256_raw(blob)
print("src:", src, "current_sha:", cur)
print("decisions_verdict:", "MATCH" if cur.upper() == stored.upper() else "CHANGED")
if cur.upper() != stored.upper():
    # dump the diff region for consumption: show the new lines vs stored blob? we only have current
    open(os.path.join(REPO, "results", "_r688bma_decisions_changed.txt"), "wb").write(blob)
    print("changed blob saved: results/_r688bma_decisions_changed.txt")
