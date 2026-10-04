"""r666 bm-a S0.5 D-19 probe: origin-fresh decisions.md/orders.md raw-byte hash + new-line consumption.

Per r660 content-addressing law: hash git-show raw bytes (never disk copies).
Per r446: probe as file (no inline python -c quoting hazards).
"""
import subprocess
import hashlib
import sys

# pit-encoding: GBK console crashes on CJK/emoji print — force utf-8 stdout
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

GROUP = r"C:\Users\sjs20\Desktop\FluxGroup"
STATE_SHA = "eb14b510d304a1d0a30175447cf9360d6bab6dc20972ceebce35d47ef8935bfa"


def show_bytes(path: str) -> bytes:
    out = subprocess.run(
        ["git", "-C", GROUP, "show", f"origin/main:{path}"],
        capture_output=True,
    )
    if out.returncode != 0:
        print(f"SHOW_FAIL {path} rc={out.returncode} {out.stderr[:200]!r}")
        sys.exit(2)
    return out.stdout


def main() -> None:
    dec = show_bytes("docs/decisions.md")
    sha = hashlib.sha256(dec).hexdigest()
    print(f"DECISIONS_SHA={sha}")
    print(f"STATE_SHA_MATCH={sha == STATE_SHA}")
    text = dec.decode("utf-8", errors="replace")
    lines = text.splitlines()
    print(f"DEC_TOTAL_LINES={len(lines)}")
    print("--- decisions tail 45 ---")
    for ln in lines[-45:]:
        print(ln)
    print("--- dispatch board (派工通告板) ---")
    in_board = False
    for ln in lines:
        if "派工通告板" in ln:
            in_board = True
        elif in_board and ln.startswith("## "):
            break
        if in_board:
            print(ln)
    print("--- orders.md lines touching BigMoney/quant/CEO-pending ---")
    orders = show_bytes("docs/orders.md").decode("utf-8", errors="replace")
    for ln in orders.splitlines():
        if "BigMoney" in ln or "quant" in ln or "待CEO" in ln or "CEO 待办" in ln:
            print(ln)


if __name__ == "__main__":
    main()
