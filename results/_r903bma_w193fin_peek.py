# -*- coding: utf-8 -*-
import json
r = json.load(open(r"results/perpetual_faces/n1_w193_results.json",
                  encoding="utf-8"))
print("A p99:", r["families"]["A_random_engine_exit"].get("full_sharpe_p99"))
print("w193_only sigma:", r["null_pool_cumulative"]["w193_only"]["sigma"])
print("audit:", json.dumps(r.get("audit", {}), ensure_ascii=False)[:400])
print("top keys:", list(r.keys()))
print("evidence_cutoff:", r.get("evidence_cutoff"))
print("cutoff_meta:", "cutoff_meta" in r)
sg = r.get("science_gates", {})
print("sg keys:", list(sg.keys()))
print("ledger:", json.dumps(sg.get("ledger", {}), ensure_ascii=False)[:400])
