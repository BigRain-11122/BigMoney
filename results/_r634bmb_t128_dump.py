"""r634 bm-b: dump T-128 progress field tail to readable txt."""
import json

j = json.load(open(r"fleet/tasks/T-2026-09-30-128-P1.json", encoding="utf-8"))
p = j.get("progress", "")
open(r"results/_r634bmb_t128_progress.txt", "w", encoding="utf-8").write(p)
print("progress chars:", len(p))
print("TAIL:", p[-2200:])
