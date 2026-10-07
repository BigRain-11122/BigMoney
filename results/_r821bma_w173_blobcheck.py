import sys
import json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = json.load(open("results/_r820bma_w173_probe_receipt.json", encoding="utf-8"))
print(json.dumps(p["legs"]["leg1"], ensure_ascii=False, indent=1))
t = open("results/_r820bma_w173_probe.py", encoding="utf-8").read()
for i, line in enumerate(t.splitlines(), 1):
    if "THIRTY" in line or "staircase" in line:
        print(i, line.strip()[:160])
