# -*- coding: utf-8 -*-
# r931 probe: pool file EOL/needle format after sync_face settle
for p in ("results/runnable_pool.json", "results/runnable_pool.bm-b.json"):
    b = open(p, "rb").read()
    t = b.decode("utf-8")
    crlf = t.count("\r\n")
    lf_only = t.count("\n") - crlf
    needle = "  }\r\n ],\r\n" if crlf else "  }\n ],\n"
    print(p, "bytes", len(b), "crlf", crlf, "lf_only", lf_only)
    print("  needle_count", t.count(needle), "tail", repr(t[-40:]))
    print("  shard7_id_pos", t.find('"id": "TRIAL-LABOR-W19-SCREEN-SHARD-7"'))
    print("  entries_close_pos", t.find(needle))
