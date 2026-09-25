"""r221: append report line to logs/iteration-loop/round_reports.md (bm-b).
PS-redirect encoding hazards (r209) -> python io append, UTF-8 no BOM."""
import io
line = io.open("results/_r221_report_line.txt", encoding="utf-8").read().strip()
with io.open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("appended", len(line), "chars")