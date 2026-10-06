# -*- coding: utf-8 -*-
# r650 bm-c: quick pool/trio watch probe (read-only)
import json, re
POOL = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\runnable_pool.json"
p = json.load(open(POOL, encoding="utf-8-sig"))
print("pool keys:", list(p.keys())[:20])
s = json.dumps(p, ensure_ascii=False)
print("len bytes:", len(s))
for m in re.finditer(r'"([^"]*(?:fund|trio|yjbb|xjll|zcfz)[^"]*)"', s, re.I):
    print("match:", m.group(1))
