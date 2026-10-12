import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
d = json.load(open(r"results\_r925bmc_w221_replay_blocks.json", encoding="utf-8"))
def walk(o, pre=""):
    if isinstance(o, dict):
        for k in list(o.keys())[:40]:
            v = o[k]
            if isinstance(v, (dict, list)):
                print(pre + k, "=>", type(v).__name__, len(v))
                walk(v, pre + "  ")
            else:
                s = str(v)
                print(pre + k, "=", s[:100])
walk(d)
