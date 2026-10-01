import json, re

src = open("scripts/perpetual_faces_n1.py", encoding="utf-8").read()
# B anchor: WAVE_CONFIGS closing after 43
m = re.search(r"(43: \{.*?\"engine_owner\": \"bm-c\"\},\n)(\s+})", src, re.S)
print("B anchor found:", bool(m))
if m:
    print("closing text:", repr(m.group(2)))
# D anchor: W43 desc line tail
k = src.find("r346 bm-c] ")
print("D anchor found:", k != -1)
if k != -1:
    print("desc tail:", repr(src[k:k+120]))
# W43 selftest leg tail (C anchor)
j = src.find("W43 prior-wave set must derive")
print("C anchor found:", j != -1)
if j != -1:
    print("C tail:", repr(src[j:j+180]))

# W42 finalize actuals for the W44 prereg sec.5 anchors
d = json.load(open("results/perpetual_faces/n1_w42_results.json", encoding="utf-8"))
print("--- n1_w42_results keys:", sorted(d.keys()))
for k in ("n_eff", "n_values", "ledger_head", "prev_total", "k_lift",
          "mu", "sigma", "merged", "skill_line", "audit", "summary"):
    if k in d:
        print(k, "=", json.dumps(d[k], ensure_ascii=False)[:400])
# W42-only stats may live under a per-wave block
for k, v in d.items():
    if isinstance(v, dict) and ("mu" in v or "sigma" in v):
        print("BLOCK", k, "=", json.dumps({kk: v[kk] for kk in v if not isinstance(v[kk], (dict, list))}, ensure_ascii=False)[:500])
