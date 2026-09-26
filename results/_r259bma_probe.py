# -*- coding: utf-8 -*-
"""R259 bm-a probe: slice-E descriptive faces for digest (read-only)."""
import io
import json

d = json.load(io.open("results/t73_s2/style_rotation.json", encoding="utf-8-sig"))
art = d["descriptive"]
names = art["leg_names"]
print("== yearly best/worst (CAGR%) ==")
for y, row in sorted(art["yearly"].items(), key=lambda kv: int(kv[0])):
    legs = row["legs"]
    if row.get("best"):
        print(f"{y}: best={names[row['best']]} {legs[row['best']]*100:+.1f}% "
              f"worst={names[row['worst']]} {legs[row['worst']]*100:+.1f}% "
              f"K={row['k_present']}")
    else:
        print(f"{y}: K={row.get('k_present')} no-call")
print("winner repeats:", art["winner_repeat_transitions"], "/",
      art["n_year_transitions"])
print()
print("== era rel_vs_base (cum multiple, top-4) ==")
for era, row in art["era_table"].items():
    rel = row.get("_rel_vs_base", {})
    items = sorted(rel.items(), key=lambda kv: -kv[1])
    print(era, " | ".join(f"{names[k]}:{v:.3f}" for k, v in items[:4]))
print()
print("== era CAGR per leg ==")
for era, row in art["era_table"].items():
    cells = {names[k]: v["cagr"] for k, v in row.items()
             if k != "_rel_vs_base" and isinstance(v, dict)}
    print(era, {k: f"{v*100:+.1f}%" for k, v in cells.items()})
print()
print("== faces detail ==")
for fn, f in d["faces"].items():
    print(fn, "is:", f["blocks"]["is"], "oos:", f["blocks"]["oos"])
    print("   nulls:", f["null_p95_abs"], "months:", f["months"])
print()
print("ledger:", d["trials_ledger"])
print("panel:", d["panel"]["fund_events_flagged"], "events flagged;",
      d["panel"]["union_days"], "union days")
