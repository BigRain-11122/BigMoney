# -*- coding: utf-8 -*-
"""r239 step-2 pre-resolve inspection: read stage2 (bm-a canonical) versions."""
import subprocess

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"


def s2(path):
    out = subprocess.run(["git", "-C", ROOT, "show", ":2:%s" % path], capture_output=True)
    return out.stdout.decode("utf-8", "replace") if out.returncode == 0 else "<NO STAGE2>"


def s3(path):
    out = subprocess.run(["git", "-C", ROOT, "show", ":3:%s" % path], capture_output=True)
    return out.stdout.decode("utf-8", "replace") if out.returncode == 0 else "<NO STAGE3>"


dr = s2("scripts/daily_report.py")
print("== bm-a daily_report.py: %d bytes ==" % len(dr))
for probe in ("docs/daily_report", "results/daily_report", "OUT_DIR", "startswith(\"_\")", "startswith('_')", "cutoff24", "15:45", "selftest"):
    print("  %-22s %s" % (probe, "PRESENT" if probe in dr else "absent"))
import re
m = re.search(r"OUT_DIR\s*=\s*(.+)", dr)
print("  OUT_DIR line:", m.group(1).strip() if m else "?")
m2 = re.search(r"def cmd_force|force", dr)
print("  has force cmd:", "def cmd_force" in dr)
print("  subcommands:", re.findall(r"mode == \"(\w+)\"", dr))

dec = s2("firm/DECISIONS.md")
print("== bm-a DECISIONS.md: %d bytes, %d D-entries ==" % (len(dec), dec.count("[D-")))
print(dec[-1200:])

mcc = s2("research/MARKET_CLOCK_COMBO.md")
print("== bm-a MARKET_CLOCK_COMBO.md: %d bytes ==" % len(mcc))
for probe in ("ORANGE_COOL", "heat", "热度", "N_eff", "g1_prime_v2", "Arm", "arm", "20d", "fund", "基金", "512480"):
    print("  %-14s %s" % (probe, "PRESENT" if probe in mcc else "absent"))

ip = s2("Tools/iteration_prompt.txt")
print("== iteration_prompt stage2: daily_report legs:", ip.count("daily_report.py"), "| CRLF:", ip.count("\r\n"))

sc = s2("scripts/daily_scorecard.py")
print("== scorecard stage2: has daily-report pointer:", "每日战报" in sc or "daily_report" in sc)

print("== my docs files in stage3/working tree:")
print(s3("docs/daily_report/REPORT-20260926.md")[:80])
