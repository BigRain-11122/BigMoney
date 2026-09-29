import re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
t = open("research/TRIAL_LABOR_W11_PREREG.md", encoding="utf-8").read()
for kw in ("p95", "band", "5.2"):
    for m in re.finditer(kw, t):
        s = max(0, m.start() - 260)
        seg = t[s:m.start() + 260].replace("\n", " | ")
        print(f"[{kw}] ...{seg}...")
        print("-" * 60)
        break  # first hit only per kw
