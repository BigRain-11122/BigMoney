"""r856 bm-a: EM zt-pool API historical depth probe (read-only, 3 calls).
De-risks the S5-01 adaptation replay pilot design (as-collected history
window). Evidence -> results/_r856bma_zt_depth_probe.json"""
import json
import time

import pandas as pd
import akshare as ak

ev = {"ts": pd.Timestamp.now().isoformat(timespec="seconds"),
      "lane": "bm-a r856", "probes": [], "rc": 0}
for day in ("20220104", "20200102", "20180102"):
    t0 = time.time()
    try:
        df = ak.stock_zt_pool_em(date=day)
        face = {"day": day, "rows": int(0 if df is None else len(df)),
                "elapsed_s": round(time.time() - t0, 1)}
        if face["rows"]:
            face["max_ladder"] = int(pd.to_numeric(
                df["连板数"], errors="coerce").max())
    except Exception as ex:
        face = {"day": day, "error": f"{type(ex).__name__}: {str(ex)[:100]}"}
        ev["rc"] = 2
    ev["probes"].append(face)
    print(json.dumps(face, ensure_ascii=False), flush=True)
    time.sleep(2.5)

with open("results/_r856bma_zt_depth_probe.json", "w", encoding="utf-8") as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)
print("depth probe rc=", ev["rc"], flush=True)
