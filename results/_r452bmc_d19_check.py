"""r452 bm-c S0.5 D-19 watermark probe (regenerable, read-only).

Raw-blob content-addressing per D-20260930-18/r660 law: hash `git show origin/main:<path>`
raw bytes, never on-disk worktree copies.
"""
import subprocess
import hashlib
import sys

GROUP = r"K:\Fluxgroup\FluxGroup"
DEC_SHA = "EB14B510D304A1D0A30175447CF9360D6BAB6DC20972CEEBCE35D47EF8935BFA"
ORD_SHA = "68947C178D21814FBB5B20C3497F1DC28D42D50C"


def run(args):
    return subprocess.run(
        args, capture_output=True, cwd=GROUP,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def main():
    r = run(["git", "fetch", "origin"])
    if r.returncode != 0:
        print("FETCH_RC", r.returncode, r.stderr.decode("utf-8", "replace")[:200])
    out = {}
    for name, path in (("decisions", "docs/decisions.md"), ("orders", "docs/orders.md")):
        r = run(["git", "show", f"origin/main:{path}"])
        if r.returncode != 0:
            print(f"{name.upper()}_SHOW_RC", r.returncode, r.stderr.decode("utf-8", "replace")[:200])
            continue
        raw = r.stdout
        sha = hashlib.sha256(raw).hexdigest().upper()
        out[name] = sha
    d = out.get("decisions")
    if d is None:
        print("DECISIONS_READ_FAIL")
        sys.exit(2)
    if d == DEC_SHA:
        print("DECISIONS_MATCH", d)
    else:
        print("DECISIONS_CHANGED", d)
        r = run(["git", "show", "origin/main:docs/decisions.md"])
        text = r.stdout.decode("utf-8", "replace")
        lines = text.splitlines()
        for i, ln in enumerate(lines):
            if "派工通告板" in ln:
                print("--- 派工通告板 block ---")
                print("\n".join(lines[i:i + 40]))
                break
    o = out.get("orders")
    if o is None:
        print("ORDERS_READ_FAIL")
        sys.exit(2)
    if o == ORD_SHA:
        print("GROUP_ORDERS_MATCH", o)
    else:
        print("GROUP_ORDERS_CHANGED", o)
        r = run(["git", "show", "origin/main:docs/orders.md"])
        text = r.stdout.decode("utf-8", "replace")
        lines = text.splitlines()
        hit = False
        for i, ln in enumerate(lines):
            if "CEO" in ln and ("待办" in ln or "物理" in ln):
                hit = True
                print("--- CEO pending physical-items area ---")
                print("\n".join(lines[i:i + 30]))
                break
        if not hit:
            print("(no CEO-pending marker found; tail below)")
            print("\n".join(lines[-30:]))
    print("PROBE_DONE")


if __name__ == "__main__":
    main()
