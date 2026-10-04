"""r668 bm-a: extract watermark/audit verdicts from S6 log."""
import json
import re

d = json.load(open("results/_r668bma_s6_log.txt", encoding="utf-8"))
for leg in d["legs"]:
    if leg["leg"] in ("py_watermark", "compute_audit"):
        m = re.search(r'"verdict": "([a-z_]+)"', leg["tail"])
        print(leg["leg"], "verdict=",
              m.group(1) if m else leg["tail"][:150])
