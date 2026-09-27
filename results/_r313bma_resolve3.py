# -*- coding: utf-8 -*-
"""R313 resolver round 2: autofill_state mixed-dict+ledger union + token_usage take-new."""
import json, os, subprocess

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    return r.stdout

for p in ["results/autofill_state.json", "results/token_usage.json"]:
    for side, st in (("ours", 2), ("theirs", 3)):
        b = blob(st, p)
        d = json.loads(b.decode("utf-8"))
        info = {"keys": sorted(d.keys())}
        if "launches" in d:
            info["launches_len"] = len(d["launches"])
            ts = [l.get("ts") if isinstance(l, dict) else type(l).__name__ for l in d["launches"]]
            info["launch_first_ts"] = ts[0] if ts else None
            info["launch_last_ts"] = ts[-1] if ts else None
            info["sample_keys"] = sorted(d["launches"][0].keys()) if d["launches"] and isinstance(d["launches"][0], dict) else None
        if "last_tick" in d:
            lt = d["last_tick"]
            info["last_tick_type"] = type(lt).__name__
            info["last_tick_ts"] = lt.get("ts") if isinstance(lt, dict) else str(lt)[:80]
        info["generated"] = d.get("generated")
        info["updated"] = d.get("updated")
        info["crlf"] = b"\r\n" in b[:1500]
        print(p, side, json.dumps(info, ensure_ascii=False)[:400])
