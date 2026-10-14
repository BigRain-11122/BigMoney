"""r997: direct ak.fund_etf_hist_sina probe - what does the wrapper return now?"""
import sys, os, json, datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import akshare as ak
    df = ak.fund_etf_hist_sina(symbol="sh510300")
    tail = df.tail(4)[["date", "close"]].astype(str).values.tolist()
    out = {"ok": True, "akshare_version": ak.__version__, "n": len(df), "tail": tail}
except Exception as e:
    out = {"ok": False, "err": f"{type(e).__name__}: {e}"[:300]}
out["ts"] = datetime.datetime.now().isoformat(timespec="seconds")
open(r"results\_r997bma_akshare_probe.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps(out, ensure_ascii=False)[:500])
