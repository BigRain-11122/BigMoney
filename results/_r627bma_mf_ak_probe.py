# r627 bm-a: akshare-path probe - does ak.stock_individual_fund_flow work right now?
import json, time, datetime, traceback
EVID = {"ts": datetime.datetime.now().isoformat(timespec="seconds"), "calls": []}
def call(name, fn):
    t0 = time.time()
    try:
        r = fn()
        EVID["calls"].append({"name": name, "ok": True, "elapsed_s": round(time.time()-t0, 2),
                              "rows": len(r) if r is not None and hasattr(r, "__len__") else "?"})
    except Exception as e:
        EVID["calls"].append({"name": name, "ok": False, "elapsed_s": round(time.time()-t0, 2),
                              "err": type(e).__name__ + ": " + str(e)[:200]})
    print(EVID["calls"][-1])

import akshare as ak
EVID["akshare_version"] = getattr(ak, "__version__", "?")
print("akshare", EVID["akshare_version"])

call("ak_fflow_000151_sz", lambda: ak.stock_individual_fund_flow(stock="000151", market="sz"))
time.sleep(2.5)
call("ak_fflow_000153_sz", lambda: ak.stock_individual_fund_flow(stock="000153", market="sz"))
time.sleep(2.5)
call("ak_fflow_000155_sz", lambda: ak.stock_individual_fund_flow(stock="000155", market="sz"))

json.dump(EVID, open("results/_r627bma_mf_ak_probe.json", "w", encoding="utf-8"), indent=1)
