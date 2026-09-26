# -*- coding: utf-8 -*-
"""R258 bm-a: slice-D artifact inspection (read-only, digest input)."""
import io
import json

d = json.load(io.open("results/t73_s2/factor_history.json", encoding="utf-8"))
for k in ("size/h10", "vol20/h10", "vol60/h10"):
    f = d["faces"][k]
    print(k, "gates:", f["gates"],
          "| oos ir:", f["blocks"]["oos"].get("ic_ir"),
          "| is ir:", f["blocks"]["is"].get("ic_ir"),
          "| oos n:", f["blocks"]["oos"].get("n_periods"),
          "| is n:", f["blocks"]["is"].get("n_periods"))
print("cap sanity:", json.dumps(d["panel"]["cap_sanity_last_bar"], ensure_ascii=False))
print("corr size vs vol60:", d["ic_series_corr_size_vs_vol60"])
print("--- era table h10 (ic_mean / ir / n) ---")
for sig, eras in d["era_table_h10"].items():
    for e, b in eras.items():
        if b:
            print("%-6s %-10s ic=%+.4f ir=%+.3f n=%s"
                  % (sig, e, b.get("ic_mean", float("nan")),
                     b.get("ic_ir", float("nan")), b.get("n_periods")))
        else:
            print("%-6s %-10s SKIP" % (sig, e))
print("--- dividend eras ---")
for e, b in d["dividend"]["era_table"].items():
    if b:
        print("%-18s ann510880=%+.4f ann510300=%+.4f excess=%+.4f bars=%s"
              % (e, b["ann_510880"], b["ann_510300"], b["excess_ann"], b["bars"]))
    else:
        print(e, "SKIP")
print("trials:", d["trials_N"], "elapsed:", d["elapsed_s"])
print("panel:", {k: v for k, v in d["panel"].items() if k != "cap_sanity_last_bar"})
