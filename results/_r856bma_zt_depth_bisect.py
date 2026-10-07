"""r856 bm-a: EM zt-pool depth bisect (read-only). 2022/2020/2018 all
returned 0 rows; find the actual depth boundary."""
import json
import time

import pandas as pd
import akshare as ak

ev = {"ts": pd.Timestamp.now().isoformat(timespec="seconds"),
      "lane": "bm-a r856 bisect", "probes": [], "rc": 0}
for day in ("20250106", "20240102", "20230103", "20220601", "20230103"):
    if any(p["day"] == day for p in ev["probes"]):
        continue
    t0 = time.time()
    try:
        df = ak.stock_zt_pool_em(date=day)
        face = {"day": day, "rows": int(0 if df is None else len(df)),
                "elapsed_s": round(time.time() - t0, 1)}
    except Exception as ex:
        face = {"day": day, "error": f"{type(ex).__name__}: {str(ex)[:100]}"}
        ev["rc"] = 2
    ev["probes"].append(face)
    print(json.dumps(face, ensure_ascii=False), flush=True)
    time.sleep(2.5)

with open("results/_r856bma_zt_depth_bisect.json", "w", encoding="utf-8") as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)
print("bisect rc=", ev["rc"], flush=True)
