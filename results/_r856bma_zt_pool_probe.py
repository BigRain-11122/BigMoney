"""r856 bm-a: zt_pool 4-endpoint live shape probe (read-only, zero panel
writes). Source audit per wiring-skill law (single probe before expand).
Evidence -> results/_r856bma_zt_pool_probe.json"""
import json
import time

import pandas as pd
import akshare as ak

EP = {
    "zt":     ("stock_zt_pool_em",        ["代码", "名称", "涨跌幅", "连板数"]),
    "zbgc":   ("stock_zt_pool_zbgc_em",  ["代码", "名称", "涨跌幅"]),
    "dtgc":   ("stock_zt_pool_dtgc_em",   ["代码", "名称", "涨跌幅"]),
    "strong": ("stock_zt_pool_strong_em", ["代码", "名称", "涨跌幅"]),
}
DAY = "20260930"   # last bar-landed trading day (golden week before today)

ev = {"ts": pd.Timestamp.now().isoformat(timespec="seconds"),
      "lane": "bm-a r856", "day": DAY, "endpoints": {}, "rc": 0}
for key, (fn_name, inv) in EP.items():
    t0 = time.time()
    try:
        fn = getattr(ak, fn_name)
        df = fn(date=DAY)
        rows = 0 if df is None else len(df)
        cols = [] if df is None else list(df.columns)
        missing = [c for c in inv if c not in cols] if rows else []
        face = {"rows": int(rows), "cols": cols,
                "invariant_missing": missing,
                "elapsed_s": round(time.time() - t0, 1)}
        if rows:
            face["head2"] = df.head(2).to_dict(orient="records")
            face["ladder_max"] = (int(pd.to_numeric(df["连板数"],
                                   errors="coerce").max())
                                  if "连板数" in cols else None)
        if missing:
            ev["rc"] = max(ev["rc"], 3)
    except Exception as ex:
        face = {"error": f"{type(ex).__name__}: {str(ex)[:120]}"}
        ev["rc"] = max(ev["rc"], 2)
    ev["endpoints"][key] = face
    print(key, json.dumps(face, ensure_ascii=False)[:300], flush=True)
    time.sleep(2.5)

with open("results/_r856bma_zt_pool_probe.json", "w", encoding="utf-8") as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)
print("probe rc=", ev["rc"], "evidence=results/_r856bma_zt_pool_probe.json",
      flush=True)
