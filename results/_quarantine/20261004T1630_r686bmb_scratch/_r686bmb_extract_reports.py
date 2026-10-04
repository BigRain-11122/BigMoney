"""r686 bm-b: extract r676-r679 round report header lines for HANDOVER entry."""
import io
import re

txt = open("logs/iteration-loop/round_reports.md", "rb").read().decode(
    "utf-8", "replace")
pats = [r"\| r67[6-9] \(", r"\| r68[0] \("]
lines = []
for m in re.finditer(r"^.*\| r67[6-9] \(bm-b\).*$|^\s*-\s*2026-10-04.*r67[6-9].*$",
                     txt, re.M):
    lines.append(m.group(0)[:620])
open("results/_r686bmb_r676_679.txt", "w", encoding="utf-8").write(
    "\n\n".join(lines))
print("lines:", len(lines))
