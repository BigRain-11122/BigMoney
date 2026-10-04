"""r470 bm-c S2: fleet task-board scan (open tickets + recent claims).
Round-numbered copy of _r469bmc_s2_board.py per r461 law."""
import json
import os

TASKS = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\tasks"
out = []
for name in sorted(os.listdir(TASKS)):
    if not name.endswith(".json"):
        continue
    try:
        with open(os.path.join(TASKS, name), encoding="utf-8-sig") as fh:
            t = json.load(fh)
    except (OSError, ValueError):
        continue
    status = t.get("status", "")
    if status in ("open", "claimed", "in_progress"):
        out.append({
            "file": name,
            "id": t.get("id", t.get("ticket", "")),
            "status": status,
            "claimed_by": t.get("claimed_by", ""),
            "subject": (t.get("subject") or t.get("title") or "")[:80],
        })
with open(
    r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r470bmc_s2_board.json",
    "w", encoding="utf-8", newline="\n",
) as fh:
    json.dump({"open_or_claimed": out, "count": len(out)}, fh, indent=1)
print("OPEN_OR_CLAIMED=" + str(len(out)))
for e in out:
    print(e["file"] + " | " + e["status"] + " | " + e["claimed_by"] + " | " + e["subject"])
