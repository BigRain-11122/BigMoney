import subprocess, json, hashlib, os

GRP = r"K:\Fluxgroup\FluxGroup"
BM = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def show(path):
    return subprocess.run(["git", "-C", GRP, "show", "origin/main:" + path], capture_output=True).stdout.decode("utf-8", "replace")

dec = show("docs/decisions.md")
lines = dec.splitlines()

# find 派工通告板 block
board_start = None
for i, l in enumerate(lines):
    if "派工通告板" in l:
        board_start = i
        break

out = {}
if board_start is not None:
    # take 60 lines from board start (the board is usually near the tail)
    out["board_lines"] = lines[board_start:board_start + 80]
else:
    out["board_lines"] = ["NO-BOARD-MARKER"]

# find last 40 lines with D-2026 patterns to see recent decisions
dec_rows = [l for l in lines if l.startswith("| D-2026") or "D-20261014" in l or "D-20261013" in l]
out["recent_d_rows"] = dec_rows[-25:] if len(dec_rows) > 25 else dec_rows

# orders.md CEO physical-items zone
orders = show("docs/orders.md")
olines = orders.splitlines()
# locate physical-items section markers
phys_idx = None
for i, l in enumerate(olines):
    if ("物理" in l and ("件" in l or "区" in l)) or "待办" in l or "CEO" in l and "区" in l:
        phys_idx = i
        break
# fallback: just dump lines with recent dates or unchecked boxes
recent = [l for l in olines if ("2026-10-14" in l or "2026-10-13" in l or "2026-10-12" in l)]
out["orders_recent"] = recent[-40:] if len(recent) > 40 else recent
out["orders_phys_zone"] = olines[phys_idx:phys_idx + 40] if phys_idx is not None else ["NO-MARKER"]

print(json.dumps(out, ensure_ascii=False, indent=1))
open(os.path.join(BM, "results", "_r984bmc_s05_consume.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
