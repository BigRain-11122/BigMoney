"""r484 bm-c S2: fleet task tickets status scan (regenerable, read-only)."""
import json
import glob
import os

OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r484bmc_s02_tasks_out.txt"
lines = []
files = sorted(glob.glob(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\tasks\*.json"))
lines.append(f"total_tickets={len(files)}")
for f in files:
    try:
        with open(f, encoding="utf-8") as fh:
            t = json.load(fh)
    except Exception as e:
        lines.append(f"{os.path.basename(f)} PARSE_FAIL {e}")
        continue
    st = t.get("status")
    if st in ("open", "claimed", "in_progress"):
        lines.append(f"{os.path.basename(f)} status={st} claimed_by={t.get('claimed_by')} title={t.get('title','')[:80]}")
with open(OUT, "w", encoding="utf-8", newline="") as fh:
    fh.write("\n".join(lines))
print("PROBE_DONE")
