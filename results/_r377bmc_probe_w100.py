# -*- coding: utf-8 -*-
"""r377 bm-c: quick chain-state probe -- W100 finalize result head keys."""
import json

p = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\perpetual_faces\n1_w100_results.json"
d = json.load(open(p, encoding="utf-8"))


def find(obj, keys, path=""):
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            kk = k.lower()
            if isinstance(v, (int, float, str)) and any(t in kk for t in keys):
                hits.append((path + "/" + k, v))
            else:
                hits.extend(find(v, keys, path + "/" + k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:3]):
            hits.extend(find(v, keys, path + f"[{i}]"))
    return hits


for k, v in find(d, ["total", "ledger", "skill", "wave", "void", "k_", "n_"]):
    print(k, "=", v)
