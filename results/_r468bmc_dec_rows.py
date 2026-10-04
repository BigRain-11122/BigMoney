"""r468 bm-c D-19 consumption leg: extract group decisions rows touching
D-20261002-02/03/05/06 + D-20261004-02 (BigMoney receipt window face) from
origin/main docs/decisions.md raw blob; compute new SHA-256 watermark.
File-out per r446 law; zero console CJK print."""
import hashlib
import os
import subprocess

GROUP = r"K:\Fluxgroup\FluxGroup"
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = os.path.join(REPO, "results", "_r468bmc_dec_rows.txt")
NEEDLES = ("D-20261002-02", "D-20261002-03", "D-20261002-05",
           "D-20261002-06", "D-20261004-02", "D-20261004-05")


def main():
    r = subprocess.run(["git", "fetch", "origin"], cwd=GROUP, capture_output=True,
                       creationflags=0x08000000)
    r = subprocess.run(["git", "show", "origin/main:docs/decisions.md"], cwd=GROUP,
                       capture_output=True, creationflags=0x08000000)
    lines = []
    if r.returncode != 0:
        lines.append("READ_FAIL " + r.stderr.decode("utf-8", "replace")[:200])
    else:
        raw = r.stdout
        sha = hashlib.sha256(raw).hexdigest().upper()
        lines.append(f"NEW_DECISIONS_SHA256 {sha}")
        text = raw.decode("utf-8", "replace")
        for ln in text.splitlines():
            if any(n in ln for n in NEEDLES):
                lines.append("ROW>> " + ln)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))
    print("DEC_ROWS_DONE sha", lines[0] if lines else "?", "rows", len(lines) - 1)


if __name__ == "__main__":
    main()
