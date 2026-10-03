"""r634 bm-b: run conflict classifier via subprocess (avoid PS UTF-16 redirect),
print per-file form + recipe, then apply canon recipes per SKILL.md table."""
import json
import re
import subprocess
import sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
CLS = (
    r"C:\Fluxgroup\FluxGroup\quant\bigmoney\.codely-cli\skills"
    r"\bigmoney-conflict-resolve\scripts\classify_conflicts.py"
)

p = subprocess.run(
    [sys.executable, CLS], cwd=ROOT, capture_output=True
)
out = p.stdout.decode("utf-8", errors="replace")
m = re.search(r"\{.*\}", out, re.S)
data = json.loads(m.group(0))
entries = data.get("entries", [])
print("N_ENTRIES:", len(entries))
for e in entries:
    print(
        e.get("state"),
        "|",
        e.get("class") or e.get("form") or "UNKNOWN",
        "|",
        e.get("path"),
        "|",
        (e.get("recipe") or "")[:80],
    )
