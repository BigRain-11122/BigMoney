"""r468 bm-c D-20261002-06 reconciliation evidence: byte sizes + md5 of all
research/pit-*.md domain-split files + main/line CODELY.md sizes.
File-out per r446 law; zero console CJK print."""
import hashlib
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
LINE = r"K:\Fluxgroup\FluxGroup\quant"
OUT = os.path.join(REPO, "results", "_r468bmc_d0206_recon.txt")


def main():
    lines = []
    pit_dir = os.path.join(REPO, "research")
    total = 0
    names = sorted(f for f in os.listdir(pit_dir) if f.startswith("pit") and f.endswith(".md"))
    for n in names:
        p = os.path.join(pit_dir, n)
        b = open(p, "rb").read()
        total += len(b)
        lines.append(f"{n} {len(b)}B md5={hashlib.md5(b).hexdigest()}")
    lines.append(f"TOTAL_PIT {len(names)} files {total}B")
    for label, p in [("MAIN_CODELY", os.path.join(REPO, "CODELY.md")),
                     ("LINE_CODELY", os.path.join(LINE, "CODELY.md"))]:
        b = open(p, "rb").read()
        lines.append(f"{label} {len(b)}B md5={hashlib.md5(b).hexdigest()}")
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))
    print("RECON_DONE files", len(names), "main_bytes",
          [l.split()[1] for l in lines if l.startswith("MAIN_CODELY")][0])


if __name__ == "__main__":
    main()
