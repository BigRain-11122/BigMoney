# r350 bm-c: read W47 finalize artifact summary (authoritative anchor numbers
# for the W50 prereg sec.5 -- fresh-read law, no prose hand-copy).
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
d = json.load(open(r"results/perpetual_faces/n1_w47_results.json", encoding="utf-8"))
skip_top = {"families", "shards", "per_shard", "cells", "nulls", "samples",
            "a_entries", "b_entries", "entries", "raw", "per_start", "runs"}
out = {}
for k, v in d.items():
    if k in skip_top:
        continue
    if isinstance(v, dict):
        # keep only shallow scalars from nested dicts (2 levels deep max)
        shallow = {}
        for k2, v2 in v.items():
            if isinstance(v2, (int, float, str, bool)) or v2 is None:
                shallow[k2] = v2
            elif isinstance(v2, dict) and all(
                    isinstance(x, (int, float, str, bool)) or x is None
                    for x in v2.values()):
                shallow[k2] = v2
        out[k] = shallow
    else:
        out[k] = v
print(json.dumps(out, ensure_ascii=False, indent=1)[:5000])
