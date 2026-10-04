"""r457 bm-c pool probe: runnable_pool.json real structure + FUND trio NULLS owner state."""
import json

with open(r"results\runnable_pool.json", encoding="utf-8-sig") as fh:
    d = json.load(fh)
print("TYPE", type(d).__name__)
if isinstance(d, dict):
    for k, v in d.items():
        kind = type(v).__name__
        n = len(v) if hasattr(v, "__len__") else "-"
        print("KEY %s (%s, len=%s)" % (k, kind, n))
        if isinstance(v, list):
            for it in v[:6]:
                if isinstance(it, dict):
                    print("   ", json.dumps({kk: it.get(kk) for kk in
                          ("id", "name", "status", "owner", "owner_since", "shard", "lane") if kk in it},
                          ensure_ascii=False)[:220])
        elif isinstance(v, dict):
            for kk, vv in list(v.items())[:6]:
                if isinstance(vv, dict):
                    print("   ", kk, "->", json.dumps({x: vv.get(x) for x in
                          ("status", "owner", "owner_since", "claimed_by") if x in vv},
                          ensure_ascii=False)[:200])
                else:
                    print("   ", kk, "->", str(vv)[:120])
