import json, io, os
RB = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def load(n):
    return json.load(io.open(os.path.join(RB, n), encoding="utf-8"))

for n in [r"results\fund_h_unlock_eval.json",
          r"results\fund_history_status.json",
          r"results\mass_trial\w2_judge.json"]:
    try:
        d = load(n)
        ks = sorted(d.keys()) if isinstance(d, dict) else None
        print("==", n, "keys:", (ks[:16] if ks else type(d).__name__))
    except Exception as e:
        print("==", n, "ERR", repr(e)[:120])

d = load(r"results\fund_h_unlock_eval.json")
print("UNLOCK_EVAL:", json.dumps(d, ensure_ascii=False)[:1000])

d2 = load(r"results\mass_trial\w2_judge.json")
print("W2_HEAD:", json.dumps({k: d2[k] for k in list(d2)[:12] if not isinstance(d2[k], (list, dict)) or len(json.dumps(d2[k])) < 200}, ensure_ascii=False)[:800])

# PIT audit face hunt
for root, dirs, files in os.walk(os.path.join(RB, "results")):
    for f in files:
        if "pit" in f.lower() and f.endswith(".json"):
            print("PIT_FILE:", os.path.join(root, f).replace(RB + "\\", ""))
