# -*- coding: utf-8 -*-
# r656 bm-c S6 key-face digest probe (read-only)
import re, json
R = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
txt = open(R + r"\results\_r656bmc_s6_log.txt", encoding="utf-8-sig").read()

m = re.search(r"\[pool_dualrun\].*", txt)
print(m.group(0) if m else "no dualrun line")

for l in txt.splitlines():
    if '"audit_version"' in l and l.lstrip().startswith('{"ts"'):
        a = json.loads(l.strip())
        keys = {k: v for k, v in a.items() if "flag" in str(k).lower() or k in ("blind_run", "zombie", "gpu_violation")}
        print("audit: cpu", a.get("cpu_total_pct"), "py", a.get("py_cpu_pct"), "| flag-ish keys:", keys)
        break

m = re.search(r'"verdict":\s*"(\w+)"', txt)
print("py_watermark verdict:", m.group(1) if m else "?")

for tag in ("update_daily", "token_meter", "daily_report", "ceo_live_usage", "live_paper"):
    m = re.search(r"=== %s rc=0 [^\n]*\n(.*?)\n" % tag, txt, re.S)
    if m:
        tl = [l for l in m.group(1).splitlines() if l.strip()][-2:]
        print(tag, "tail:", " / ".join(x[:110] for x in tl))
