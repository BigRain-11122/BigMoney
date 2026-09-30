import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

j = json.load(open(r"results/trial_labor_w13/w13_judge.json", encoding="utf-8"))
def walk(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "total" or k == "n_trials":
                print("judge", p + "/" + k, "=", v)
            walk(v, p + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o[:50]):
            walk(v, p + f"[{i}]")
walk(j)

att = json.load(open(r"results/gate_attrition.json", encoding="utf-8"))
ents = att["entries"]
print("attrition entries:", len(ents), "| last entry keys:", list(ents[-1].keys()) if ents else None)
print("last entry:", json.dumps({k: v for k, v in ents[-1].items() if not isinstance(v, (dict, list))}, ensure_ascii=False)[:400])
hist = att["history"]
print("history tail:", json.dumps(hist[-1], ensure_ascii=False)[:300] if hist else None)
