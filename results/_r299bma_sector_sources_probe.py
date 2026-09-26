"""R299 bm-a sector-taxonomy reachability probe (queue #4 sector-leader face).

Facts-only reachability check (R99: zero strategy runs). Sources tried in
order; each face is disclosed in the probe JSON regardless of pass/fail:
  A) ak.stock_board_industry_name_ths / cons_ths   (THS industry boards)
  B) ak.stock_board_industry_name_em / cons_em     (EM industry boards)
  C) ak.sw_index_first_info                        (SW level-1, sina-side)
"""
import json
import time
import traceback

import akshare as ak

OUT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\_r299bma_sector_sources_probe.json"
res = {"kind": "reachability probe, facts only", "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
       "akshare": ak.__version__ if hasattr(ak, "__version__") else "?"}

# A) THS industry boards
try:
    t0 = time.time()
    name_df = ak.stock_board_industry_name_ths()
    res["A_ths_name"] = {"ok": True, "n_boards": int(len(name_df)),
                          "cols": list(name_df.columns), "elapsed_s": round(time.time() - t0, 1),
                          "head": name_df.head(3).to_dict("records")}
    try:
        sym0 = str(name_df.iloc[0, 0])
        cons = ak.stock_board_industry_cons_ths(symbol=sym0)
        res["A_ths_cons_sample"] = {"ok": True, "symbol": sym0, "n": int(len(cons)),
                                     "cols": list(cons.columns),
                                     "head": cons.head(3).to_dict("records")}
    except Exception as e:
        res["A_ths_cons_sample"] = {"ok": False, "err": f"{type(e).__name__}: {e}"[:300]}
except Exception as e:
    res["A_ths_name"] = {"ok": False, "err": f"{type(e).__name__}: {e}"[:300]}

# B) EM industry boards
try:
    t0 = time.time()
    em = ak.stock_board_industry_name_em()
    res["B_em_name"] = {"ok": True, "n_boards": int(len(em)),
                         "cols": list(em.columns), "elapsed_s": round(time.time() - t0, 1)}
    try:
        sym0 = str(em.iloc[0, 1])
        cons = ak.stock_board_industry_cons_em(symbol=sym0)
        res["B_em_cons_sample"] = {"ok": True, "symbol": sym0, "n": int(len(cons)),
                                    "cols": list(cons.columns)}
    except Exception as e:
        res["B_em_cons_sample"] = {"ok": False, "err": f"{type(e).__name__}: {e}"[:300]}
except Exception as e:
    res["B_em_name"] = {"ok": False, "err": f"{type(e).__name__}: {e}"[:300]}

# C) SW level-1
try:
    t0 = time.time()
    sw = ak.sw_index_first_info()
    res["C_sw_l1"] = {"ok": True, "n": int(len(sw)), "cols": list(sw.columns),
                       "elapsed_s": round(time.time() - t0, 1)}
except Exception as e:
    res["C_sw_l1"] = {"ok": False, "err": f"{type(e).__name__}: {e}"[:300],
                       "tb": traceback.format_exc()[-200:]}

json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps(res, ensure_ascii=False, indent=1, default=str)[:3000])
