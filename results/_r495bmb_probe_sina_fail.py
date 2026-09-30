# r495 bm-b: probe sina qfq daily for 3 failed-tail symbols (transient vs persistent)
import json, time, warnings
warnings.filterwarnings("ignore")
import akshare as ak

fails = ["688002", "688220", "688625"]
for code in fails:
    sym = "sh" + code
    t0 = time.time()
    try:
        df = ak.stock_zh_a_daily(symbol=sym, adjust="qfq")
        n = 0 if df is None else len(df)
        tail = "" if df is None else str(df.iloc[-1].get("date", "?"))
        print("OK %s rows=%d tail=%s elapsed=%.1fs" % (code, n, tail, time.time() - t0))
    except Exception as e:
        print("FAIL %s %s: %s elapsed=%.1fs" % (code, type(e).__name__, str(e)[:120], time.time() - t0))
