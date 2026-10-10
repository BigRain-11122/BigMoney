"""r827 bm-b E7 source probe: ETF universe+liquidity enumeration sources reachability.

Bounded single-call probe per source (E1/E3 two-source discipline):
  A) ak.fund_etf_spot_em      (EM push2 - universe + name + today amount)
  B) ak.fund_etf_category_sina (sina list - universe + name)
Writes no shared state; stdout-only facts. Exit 0 if >=1 source alive, else 2.
"""
import json
import sys
import time

t0 = time.time()
facts = {"probe": "e7_etf_list_sources", "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00")}

# --- A) EM spot
try:
    import akshare as ak
    df = ak.fund_etf_spot_em()
    facts["em_spot"] = {
        "ok": True, "rows": int(len(df)),
        "cols": list(df.columns)[:14],
        "sample": df.head(2).to_dict("records"),
    }
except Exception as e:
    facts["em_spot"] = {"ok": False, "err": repr(e)[:200]}

# --- B) sina category list
try:
    import akshare as ak
    df2 = ak.fund_etf_category_sina(symbol="ETF基金")
    facts["sina_list"] = {
        "ok": True, "rows": int(len(df2)),
        "cols": list(df2.columns)[:12],
        "sample": df2.head(2).to_dict("records"),
    }
except Exception as e:
    facts["sina_list"] = {"ok": False, "err": repr(e)[:200]}

alive = sum(1 for k in ("em_spot", "sina_list") if facts.get(k, {}).get("ok"))
facts["alive_sources"] = alive
facts["elapsed_sec"] = round(time.time() - t0, 1)
print(json.dumps(facts, ensure_ascii=False, default=str)[:2400])
sys.exit(0 if alive >= 1 else 2)
