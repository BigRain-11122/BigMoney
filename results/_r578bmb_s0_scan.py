"""r578 bm-b S0.5+S0.6 pre-surgery scan: orders diff + D-19 decisions/orders watermark.

Runs BEFORE the estate carry commit so CEO orders are visible before any surgery.
Read-only except the temp partial clone dir under %TEMP% (r481 recipe).
"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP_REMOTE = "git@github.com:BigRain-11122/FluxGroup.git"
CLONE_DIR = os.path.join(os.environ.get("TEMP", "."), "fg-dec-bmb")


def sh(args, cwd=None, check=True):
    p = subprocess.run(args, cwd=cwd, capture_output=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"{args} rc={p.returncode} stderr={p.stderr[:400]!r}")
    return p


def main():
    # --- S0.5 orders full-set diff (R13: programmatic, no timestamp filter) ---
    orders_dir = os.path.join(ROOT, "fleet", "orders")
    on_disk = sorted(
        f for f in os.listdir(orders_dir) if f.startswith("O-") and f.endswith(".md")
    )
    with open(os.path.join(ROOT, "fleet", "machines", "bm-b.json"), "rb") as f:
        hb = json.loads(f.read().decode("utf-8"))
    acked = set(hb.get("orders_ack", []))
    unacked = [f for f in on_disk if f not in acked]
    print(f"ORDERS on_disk={len(on_disk)} acked={len(acked)} UNACKED={unacked}")

    # --- D-19 fresh read: temp partial clone, raw-bytes SHA (r292/r503 laws) ---
    if not os.path.isdir(os.path.join(CLONE_DIR, ".git")):
        sh(["git", "clone", "--depth", "1", "--filter=blob:none", "--no-checkout",
            GROUP_REMOTE, CLONE_DIR])
    sh(["git", "fetch", "origin"], cwd=CLONE_DIR)
    dec = sh(["git", "show", "origin/main:docs/decisions.md"], cwd=CLONE_DIR).stdout
    orders_md = sh(["git", "show", "origin/main:docs/orders.md"], cwd=CLONE_DIR).stdout
    dec_sha = hashlib.sha256(dec).hexdigest().upper()
    with open(os.path.join(ROOT, "state.json"), "rb") as f:
        st = json.loads(f.read().decode("utf-8"))
    prev = str(st.get("last_decisions_sha", "")).upper()
    print(f"D19 decisions_sha={dec_sha[:16]}.. prev={prev[:16]}.. "
          f"{'MATCH-unchanged' if dec_sha == prev else 'CHANGED'}")
    if dec_sha != prev:
        new_rows = [ln for ln in dec.decode('utf-8', 'replace').splitlines()
                    if ln.strip().startswith('- [') and 'D-2026' in ln]
        print("D19 tail decision rows (last 12):")
        for ln in new_rows[-12:]:
            print("  " + ln[:220])
    # CEO physical-items area in group orders.md: show rows mentioning bigmoney/quant
    olines = orders_md.decode('utf-8', 'replace').splitlines()
    hits = [ln for ln in olines if ('bigmoney' in ln.lower() or 'quant' in ln.lower()
                                    or 'BigMoney' in ln)]
    print(f"D19 group_orders.md bigmoney/quant rows={len(hits)} (last 8):")
    for ln in hits[-8:]:
        print("  " + ln[:220])
    return 0


if __name__ == "__main__":
    sys.exit(main())
