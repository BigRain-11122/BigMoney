# -*- coding: utf-8 -*-
"""r698 bm-a N2-W15 SCREEN entries probe (read-only)."""
import json, io

out = io.StringIO()
with open("results/runnable_pool.json", encoding="utf-8-sig") as fh:
    pool = json.load(fh)

entries = pool.get("entries", [])
print("POOL entries=%d" % len(entries), file=out)
screen = [e for e in entries if str(e.get("id", "")).startswith("PERPETUAL-N2-W15-SHARD")]
print("SCREEN entries=%d" % len(screen), file=out)
if screen:
    e0 = screen[0]
    for k, v in e0.items():
        if k == "shards":
            for s in v:
                print("  shard:", json.dumps(s, ensure_ascii=False)[:300], file=out)
        else:
            print("  %s: %s" % (k, str(v)[:300]), file=out)
    print(file=out)
    # shard status across all 12
    for e in screen:
        for s in e.get("shards", []):
            print("  %-28s owner=%-6s status=%s" % (e.get("id"), s.get("owner"), s.get("status")), file=out)

with open("results/_r698bma_screen_probe.txt", "w", encoding="utf-8", newline="") as fh:
    fh.write(out.getvalue())
print(out.getvalue())
