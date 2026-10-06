# r781 bm-b: trio burn progress probe (Q/D nulls lines + gate states)
import json, os

for name in ["fund_quality_p1", "fund_divlowvol_p1"]:
    p = f"results/{name}/nulls.jsonl"
    if not os.path.exists(p):
        print(name, "MISSING", p)
        continue
    lines = open(p, encoding="utf-8").read().strip().splitlines()
    print(name, "lines=", len(lines))
    if lines:
        print("  tail:", lines[-1][:240])

try:
    g = json.load(open("results/p1d_gates.json", encoding="utf-8"))
    print("p1d_gates:", json.dumps(g, ensure_ascii=False)[:800])
except Exception as e:
    print("p1d_gates ERR", e)

try:
    a = json.load(open("results/autofill_state.bm-b.json", encoding="utf-8"))
    # print compact summary of active/pending batches
    s = json.dumps(a, ensure_ascii=False)
    print("autofill_state bytes=", len(s))
    print("autofill keys:", list(a.keys())[:20])
except Exception as e:
    print("autofill ERR", e)
