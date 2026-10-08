"""r781 bm-c: pull full compute_audit + py_watermark JSON lines from S6 log."""
import re

LOG = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r781bmc_s6_log.txt"
txt = open(LOG, encoding="utf-8").read()
parts = re.split(r"\n===== (\S+) =====\n", txt)
faces = {}
for i in range(1, len(parts), 2):
    faces[parts[i]] = parts[i + 1]

for w in ("compute_audit", "py_watermark"):
    body = faces.get(w, "")
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("{"):
            import json
            try:
                j = json.loads(line)
            except Exception:
                print(w, "PARSE_FAIL")
                continue
            print("==== %s keys ====" % w)
            print("flags=", j.get("flags"))
            print("verdict=", j.get("verdict"))
            print("load_state=", j.get("load_state"))
            print("pool_starvation_candidate=", j.get("pool_starvation_candidate"))
            print("supply_gap_candidate=", j.get("supply_gap_candidate"))
            print("cap_violation=", j.get("cap_violation_candidate",
                                          j.get("cap_violation")))
            print("window=", j.get("window"))
            print()
