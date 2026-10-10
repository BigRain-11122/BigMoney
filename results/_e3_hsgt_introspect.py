"""E3 P3-queue head: northbound (HSGT) data source reachability probe.

Zero-network introspection pass (R109 discipline: introspect before any request).
Writes results/_e3_hsgt_introspect.json.
"""
import inspect
import json
import re

import akshare as ak

TARGETS = [
    "stock_hsgt_fund_flow_summary_em",
    "stock_hsgt_fund_min_em",
    "stock_hsgt_hist_em",
    "stock_hsgt_individual_em",
    "stock_hsgt_board_rank_em",
    "stock_hsgt_hold_stock_em",
    "stock_hsgt_stock_statistics_em",
    "stock_hsgt_institution_statistics_em",
]

out = {}
for t in TARGETS:
    try:
        fn = getattr(ak, t)
    except AttributeError:
        out[t] = {"present": False}
        continue
    src = inspect.getsource(fn)
    doc = (fn.__doc__ or "").strip().replace("\n", " / ")
    urls = re.findall(r"https?://[^\\s'\"]+", src)
    params = list(inspect.signature(fn).parameters)
    out[t] = {
        "present": True,
        "doc": doc[:220],
        "urls": urls[:3],
        "params": params,
    }

with open("results/_e3_hsgt_introspect.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
for k, v in out.items():
    print("=====", k)
    print("  doc:", v.get("doc", "")[:130])
    print("  url:", v.get("urls"))
    print("  params:", v.get("params"))
