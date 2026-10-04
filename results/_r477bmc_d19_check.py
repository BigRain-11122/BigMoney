"""r471 bm-c S0.5 D-19 probe: group decisions/orders raw-blob hash vs state keys.

Per-key hash calibers (r458 law): decisions=SHA-256, orders=SHA-1.
Raw-blob bytes via python subprocess capture_output (r660 law: no PS pipeline,
no on-disk sparse-clone copies). Output written to file, zero console CJK.
Round-numbered copy of _r470bmc_d19_check.py per r461 law (constants live-read
from state, so only paths/labels differ).
"""
import hashlib
import json
import subprocess
import sys

GROUP = r"K:\Fluxgroup\FluxGroup"
STATE = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json"
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r477bmc_d19_check.json"

CREATE_NO_WINDOW = 0x08000000


def git_show_blob(repo: str, path: str) -> bytes:
    out = subprocess.run(
        ["git", "-C", repo, "show", f"origin/main:{path}"],
        capture_output=True, creationflags=CREATE_NO_WINDOW,
    )
    if out.returncode != 0:
        raise RuntimeError(f"git show failed rc={out.returncode}: {out.stderr[:200]!r}")
    return out.stdout


def main() -> int:
    subprocess.run(
        ["git", "-C", GROUP, "fetch", "origin"],
        capture_output=True, creationflags=CREATE_NO_WINDOW,
    )
    with open(STATE, encoding="utf-8-sig") as fh:
        state = json.load(fh)

    dec_bytes = git_show_blob(GROUP, "docs/decisions.md")
    ord_bytes = git_show_blob(GROUP, "docs/orders.md")
    dec_sha = hashlib.sha256(dec_bytes).hexdigest().upper()
    ord_sha = hashlib.sha1(ord_bytes).hexdigest().upper()

    prev_dec = state.get("last_decisions_sha", "")
    prev_ord = state.get("last_orders_sha", "")
    result = {
        "round": "r477 bm-c",
        "decisions_sha256": dec_sha,
        "decisions_prev": prev_dec,
        "decisions_changed": dec_sha != prev_dec,
        "orders_sha1": ord_sha,
        "orders_prev": prev_ord,
        "orders_changed": ord_sha != prev_ord,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, ensure_ascii=True, indent=1)
    print("DECISIONS_CHANGED=" + str(result["decisions_changed"]))
    print("ORDERS_CHANGED=" + str(result["orders_changed"]))
    print("DEC_SHA=" + dec_sha)
    print("ORD_SHA=" + ord_sha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
