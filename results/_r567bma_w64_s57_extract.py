import json
d = json.load(open(r"results\perpetual_faces\n1_w64_results.json", encoding="utf-8"))
npc = d["null_pool_cumulative"]
fams = d.get("families") or {}
print("top keys:", list(d.keys()))
print("w64_only:", {k: round(v, 6) if isinstance(v, float) else v
                    for k, v in npc["w64_only"].items()})
print("merged:", {k: round(v, 6) if isinstance(v, float) else v
                  for k, v in npc["merged"].items()})
for k, v in npc.items():
    if k not in ("canon", "pre_w64_cumulative", "w64_only", "merged"):
        print("npc extra:", k, "=", v if not isinstance(v, dict) else
              {kk: (round(vv, 6) if isinstance(vv, float) else vv)
               for kk, vv in list(v.items())[:10]})
sl = d.get("skill_line_v2_k_lift") or {}
print("skill_line:", {k: (round(v, 6) if isinstance(v, float) else v)
                      for k, v in list(sl.items())[:10]})
