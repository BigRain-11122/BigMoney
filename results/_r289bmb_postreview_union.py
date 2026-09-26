# -*- coding: utf-8 -*-
"""r289: fix post_review.jsonl (line-union, misclassified as snapshot earlier)
+ verify autofill_state claim face after mixed-dict resolve."""
import importlib.util
import json
import re
import subprocess

spec = importlib.util.spec_from_file_location("res", "results/_r289bmb_resolve.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

b2 = m.blob(2, "results/post_review.jsonl")
if b2 is None:
    # stages cleared by earlier git add -- reconstruct from commit refs
    r = subprocess.run(["git", "show", "82e7689c:results/post_review.jsonl"],
                       capture_output=True)
    b2 = r.stdout
    r = subprocess.run(["git", "show", "d06eaeff:results/post_review.jsonl"],
                       capture_output=True)
    b3 = r.stdout
else:
    b3 = m.blob(3, "results/post_review.jsonl")
l2 = [l for l in b2.decode("utf-8-sig").splitlines() if l.strip()]
l3 = [l for l in b3.decode("utf-8-sig").splitlines() if l.strip()]
seen, u = set(), []
for l in l2 + l3:
    if l in seen:
        continue
    seen.add(l)
    u.append(l)

def lts(l):
    mm = re.search(r'"(ts|at|generated)"\s*:\s*"([^"]+)"', l)
    return mm.group(2).replace("T", " ")[:19] if mm else ""

u.sort(key=lts)
eol = b"\r\n" if b2.find(b"\r\n") >= 0 else b"\n"
m.write("results/post_review.jsonl", eol.join(x.encode("utf-8") for x in u) + eol)
print("post_review.jsonl line-union: %d+%d->%d" % (len(l2), len(l3), len(u)))
json.loads(open("results/post_review.jsonl", encoding="utf-8-sig").read().splitlines()[0])
subprocess.run(["git", "add", "--", "results/post_review.jsonl"], capture_output=True)

d = json.load(open("results/autofill_state.json", encoding="utf-8-sig"))
lt = d.get("last_tick", {})
print("autofill last_tick ts:", lt.get("ts"), "machine:", lt.get("machine"))
for l in d.get("launches", [])[-6:]:
    print("  launch:", l.get("ts"), l.get("batch"), l.get("owner"),
          l.get("verdict", ""))
