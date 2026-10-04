# -*- coding: utf-8 -*-
"""r677 bm-a: token_usage three-way inspection (local vs origin blob, r466 law)."""
import json, subprocess

def load_local():
    return json.load(open("results/token_usage.json", encoding="utf-8"))

def load_origin():
    p = subprocess.run(["git", "show", "origin/main:results/token_usage.json"],
                       capture_output=True)
    return json.loads(p.stdout.decode("utf-8"))

loc = load_local()
org = load_origin()
print("local top keys:", sorted(loc.keys()))
print("origin top keys:", sorted(org.keys()))
for k in sorted(set(loc) | set(org)):
    lv, ov = loc.get(k), org.get(k)
    if isinstance(lv, dict) and isinstance(ov, dict):
        mk = sorted(set(lv) | set(ov))
        print(f"[{k}] dict keys:", mk)
        for m in mk:
            a, b = lv.get(m), ov.get(m)
            if isinstance(a, dict) and isinstance(b, dict):
                ta = a.get("ts") or a.get("updated_at") or "?"
                tb = b.get("ts") or b.get("updated_at") or "?"
            else:
                ta = tb = "-"
            same = "SAME" if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True) else "DIFF"
            print(f"   {m}: mine ts={ta} origin ts={tb} {same}")
    else:
        same = "SAME" if json.dumps(lv, sort_keys=True) == json.dumps(ov, sort_keys=True) else "DIFF"
        print(f"[{k}] {same} mine={json.dumps(lv)[:90]} origin={json.dumps(ov)[:90]}")
