# -*- coding: utf-8 -*-
"""r680 bm-c: full dump of token_usage machines sub-face diff mine vs merged."""
import json
import subprocess

def show(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)], capture_output=True)
    return json.loads(r.stdout.decode("utf-8-sig"))

mine = show("c09013750", "results/token_usage.json")["machines"]
merged = json.load(open("results/token_usage.json", encoding="utf-8-sig"))["machines"]
print("mine keys:", sorted(mine.keys()))
print("merged keys:", sorted(merged.keys()))
for k in sorted(set(mine) | set(merged)):
    a, b = mine.get(k), merged.get(k)
    if a != b:
        print("--- key %r differs" % k)
        if isinstance(a, dict) and isinstance(b, dict):
            for kk in sorted(set(a) | set(b)):
                if a.get(kk) != b.get(kk):
                    print("    %s: mine=%r" % (kk, a.get(kk)))
                    print("    %s: merged=%r" % (kk, b.get(kk)))
        else:
            print("    mine=%r" % (a,))
            print("    merged=%r" % (b,))
