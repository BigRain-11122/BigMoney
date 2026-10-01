import json, re

d = json.load(open("results/perpetual_faces/n1_w43_results.json", encoding="utf-8"))
npc = d["null_pool_cumulative"]
print("npc.canon:", {k: round(v, 6) if isinstance(v, float) else v for k, v in npc["canon"].items()})
print("npc.pre_w43:", {k: (round(v, 6) if isinstance(v, float) else v) for k, v in npc.get("pre_w43_cumulative", npc.get("pre_w44_cumulative", {})).items()})
print("npc.w43_only:", {k: (round(v, 6) if isinstance(v, float) else v) for k, v in npc.get("w43_only", {}).items()})
print("npc.merged:", {k: (round(v, 6) if isinstance(v, float) else v) for k, v in npc["merged"].items()})
for k in npc:
    if k.startswith("mu_delta"):
        print(k, npc[k])
print("skill_line_v2_k_lift:", d["skill_line_v2_k_lift"])
fams = d.get("families", {})
for fk, fv in fams.items():
    if isinstance(fv, dict):
        print("family", fk, ":", {k: vv for k, vv in fv.items() if not isinstance(vv, (dict, list))})

# anchors for the W45 freeze edits (post-yield state)
src = open("scripts/perpetual_faces.py", encoding="utf-8").read()
m = re.search(r"\n(\s*44: \{.*?\"engine_owner\": \"bm-a\"\},)\n(\s*})", src, re.S)
print("--- A anchor ---"); print(repr(m.group(1)) if m else "NOT FOUND"); print(repr(m.group(2)) if m else "")
src2 = open("scripts/perpetual_faces_n1.py", encoding="utf-8").read()
m2 = re.search(r"(44: \{.*?\"engine_owner\": \"bm-a\"\},\n)(\s+})", src2, re.S)
print("--- B closing ---"); print(repr(m2.group(2)) if m2 else "NOT FOUND")
j = src2.find("W44 prior-wave set must derive")
print("--- C tail ---"); print(repr(src2[j:j+200]) if j != -1 else "NOT FOUND")
k = src2.find("r553 bm-a] ")
print("--- D desc tail ---"); print(repr(src2[k:k+60]) if k != -1 else "NOT FOUND")
canon = open("research/PERPETUAL_FACES.md", encoding="utf-8").read()
rows = [l for l in canon.splitlines() if l.startswith("- N1 ") and "131_004..133_003" in l and "44_201..44_400" in l]
print("--- E anchor row found:", len(rows) == 1)
# W45+ warning text in bm-a's W44 row
i = canon.find("W45+")
print("--- W44 row W45+ warning:", canon[i:i+260] if i != -1 else "NOT FOUND")
