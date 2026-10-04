"""r463 bm-c D-19 group-tree watermarks (decisions SHA-256 + group orders SHA-1,
per-key caliber per r458 law). Copy of r462 probe, round-numbered per r461 law.
Raw-blob git-show bytes, zero PS pipeline. File-out, zero console CJK print."""
import subprocess
import hashlib

GROUP = r"K:\Fluxgroup\FluxGroup"
DEC_SHA256 = "EB14B510D304A1D0A30175447CF9360D6BAB6DC20972CEEBCE35D47EF8935BFA"
ORD_SHA1 = "68947C178D21814FBB5B20C3497F1DC28D42D50C"
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r463bmc_d19_group_out.txt"


def run(args):
    return subprocess.run(
        args, capture_output=True, cwd=GROUP,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def main():
    lines = []
    r = run(["git", "fetch", "origin"])
    if r.returncode != 0:
        lines.append(f"FETCH_RC {r.returncode} {r.stderr.decode('utf-8', 'replace')[:200]}")
    r = run(["git", "show", "origin/main:docs/decisions.md"])
    if r.returncode != 0:
        lines.append("DECISIONS_READ_FAIL")
    else:
        d = hashlib.sha256(r.stdout).hexdigest().upper()
        lines.append("DECISIONS_MATCH" if d == DEC_SHA256 else f"DECISIONS_CHANGED {d}")
    r = run(["git", "show", "origin/main:docs/orders.md"])
    if r.returncode != 0:
        lines.append("ORDERS_READ_FAIL")
    else:
        raw = r.stdout
        o = hashlib.sha1(raw).hexdigest().upper()
        if o == ORD_SHA1:
            lines.append(f"GROUP_ORDERS_MATCH {o}")
        else:
            lines.append(f"GROUP_ORDERS_CHANGED {o}")
            text = raw.decode("utf-8", "replace")
            olines = text.splitlines()
            hit = False
            for i, ln in enumerate(olines):
                if "CEO" in ln and ("待办" in ln or "物理" in ln):
                    hit = True
                    lines.append("--- CEO pending physical-items area ---")
                    lines.extend(olines[i:i + 40])
                    break
            if not hit:
                lines.append("(no CEO-pending marker; tail 40 lines)")
                lines.extend(olines[-40:])
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))
    print("PROBE_DONE_WROTE", OUT)


if __name__ == "__main__":
    main()
