# -*- coding: utf-8 -*-
# r662 debug: why rolling_union got zero side-picks on compute_audit.json
import json, subprocess, io, re

def gb(rev, path):
    p = subprocess.run(["git", "show", "%s:%s" % (rev, path)], capture_output=True)
    return json.loads(p.stdout.decode("utf-8-sig", "replace"))

for f in ("results/compute_audit.json", "results/regime_state.json"):
    jh = gb("HEAD", f); jt = gb("MERGE_HEAD", f)
    print("==", f)
    for tag, j in (("HEAD", jh), ("THEIRS", jt)):
        keys = {k: (len(v) if isinstance(v, list) else type(v).__name__) for k, v in j.items()}
        print(" ", tag, keys)
    # compare list-key sets
    for k in jh:
        if isinstance(jh[k], list) and isinstance(jt.get(k), list):
            sh = set(json.dumps(e, sort_keys=True) for e in jh[k])
            st = set(json.dumps(e, sort_keys=True) for e in jt[k])
            print("  list key", k, "| HEAD-only:", len(sh - st), "| THEIRS-only:", len(st - sh), "| common:", len(sh & st))
    # scalar diff sample
    diffs = [k for k in jh if not isinstance(jh[k], list) and json.dumps(jh.get(k), sort_keys=True) != json.dumps(jt.get(k), sort_keys=True)]
    print("  scalar-diff keys:", diffs[:12])
