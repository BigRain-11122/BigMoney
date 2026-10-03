# r414 bm-c: pool schema dump (fix probe key names, one-shot)
import json

d = json.load(open("K:/Fluxgroup/FluxGroup/quant/bigmoney/results/runnable_pool.json",
                   encoding="utf-8"))
ents = d.get("entries", [])
print("top_keys:", sorted(d.keys()))
print("n_entries:", len(ents))
if ents:
    print("ENTRY0_FULL:", json.dumps(ents[0], ensure_ascii=False)[:700])
    print("ENTRY1_KEYS:", sorted(ents[1].keys()) if len(ents) > 1 else [])
