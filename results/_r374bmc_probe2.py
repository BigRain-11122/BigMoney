# -*- coding: utf-8 -*-
"""r374 bm-c probe 2: summary single-line anchor (r581 law) + W94 sec.5 keys."""
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

n1 = open(os.path.join(REPO, "scripts", "perpetual_faces_n1.py"), "rb").read().decode("utf-8")
print("== SUMMARY ANCHOR (single-line literal, r581 law) ==")
for needle in ('"W98 row, r582 bm-a] "', '"W97 row, r581 bm-b] "'):
    print("needle:", needle, "count:", n1.count(needle))
k = n1.find('"W98 row, r582 bm-a] "')
print(repr(n1[k - 140:k + 120]))

w94 = json.load(open(os.path.join(REPO, "results", "perpetual_faces",
                                 "n1_w94_results.json"), encoding="utf-8"))
print("== null_pool_cumulative ==")
print(json.dumps(w94.get("null_pool_cumulative"), ensure_ascii=False)[:1200])
print("== skill_line_v2_k_lift ==")
print(json.dumps(w94.get("skill_line_v2_k_lift"), ensure_ascii=False)[:600])
print("== families A summary ==")
fa = w94["families"]["A_random_engine_exit"]
print({kk: fa.get(kk) for kk in ("n", "full_sharpe_mu", "full_sharpe_p95",
                                 "full_sharpe_p99") if kk in fa})
print("== families B summary ==")
fb = w94["families"].get("B_random_exit")
if fb:
    print({kk: fb.get(kk) for kk in ("n", "full_sharpe_mu", "full_sharpe_p95") if kk in fb})
else:
    print("B keys:", [kk for kk in fa if kk.startswith("full")][:8], "| families keys:", list(w94["families"].keys()))
print("== shards_consumed / audit head ==")
print(json.dumps(w94.get("shards_consumed"), ensure_ascii=False)[:200])
print(json.dumps(w94.get("audit"), ensure_ascii=False)[:300])
