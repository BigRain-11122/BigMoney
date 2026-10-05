# r540 bm-c: parse WM verdict + key faces from S6 log
import json
p = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r540bmc_s6_log.txt"
for line in open(p, encoding="utf-8"):
    line = line.strip()
    if '"verdict"' in line and line.startswith("{"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        v = d.get("verdict")
        if v:
            print("WM verdict=%s | board_open=%s bandit=%s" % (
                v, d.get("board_open_tasks"), d.get("bandit_open")))
