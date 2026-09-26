import glob
import json
import re

bad = []
files = glob.glob("results/post_review/*.json")
for f in files:
    try:
        d = json.load(open(f, encoding="utf-8-sig"))
    except Exception:
        bad.append((f, "unparseable"))
        continue
    s = json.dumps(d)
    if re.search(r'"verdict"\s*:\s*"?[X\u2717]', s):
        bad.append((f, "verdict-X"))
print("post_review files:", len(files), "| verdict-X hits:", bad[:5])
