"""r856 bm-a: EM zt-pool depth bisect round 4 (read-only). Boundary is
inside 2026-09; pin it: 09-07 / 09-14 / 09-21."""
import json
import time

import pandas as pd
import akshare as ak

ev = {"ts": pd.Timestamp.now().isoformat(timespec="seconds"),
      "lane": "bm-a r856 bisect4", "probes": [], "rc": 0}
for day in ("20260907", "20260914", "20260921"):
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

with open("results/_r856bma_zt_depth_bisect4.json", "w", encoding="utf-8") as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)
print("bisect4 rc=", ev["rc"], flush=True)
