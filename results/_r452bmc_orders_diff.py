"""r452 bm-c S0.5 group docs/orders.md change-diff probe (regenerable, read-only).

Fixes hash-method mismatch from _r452bmc_d19_check.py: stored last_orders_sha is
SHA-1 of raw blob bytes. Computes SHA-1, compares to stored value, and if changed
extracts the last-touch commit diff for docs/orders.md.
"""
import subprocess
import hashlib

GROUP = r"K:\Fluxgroup\FluxGroup"
ORD_SHA1 = "68947C178D21814FBB5B20C3497F1DC28D42D50C"


def run(args):
    return subprocess.run(
        args, capture_output=True, cwd=GROUP,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def main():
    r = run(["git", "show", "origin/main:docs/orders.md"])
    raw = r.stdout
    sha1 = hashlib.sha1(raw).hexdigest().upper()
    if sha1 == ORD_SHA1:
        print("ORDERS_SHA1_MATCH", sha1)
        return
    print("ORDERS_SHA1_CHANGED", sha1)
    # find last commits touching docs/orders.md
    r = run(["git", "log", "origin/main", "--format=%h|%ci|%s", "-6", "--", "docs/orders.md"])
    log_lines = r.stdout.decode("utf-8", "replace").strip().splitlines()
    print("RECENT_TOUCH_COMMITS:")
    for ln in log_lines:
        print(" ", ln)
    if len(log_lines) >= 2:
        old = log_lines[1].split("|")[0]
        new = log_lines[0].split("|")[0]
        r = run(["git", "diff", f"{old}..{new}", "--", "docs/orders.md"])
        print("--- DIFF old..new ---")
        print(r.stdout.decode("utf-8", "replace")[:6000])
    print("PROBE_DONE")


if __name__ == "__main__":
    main()
