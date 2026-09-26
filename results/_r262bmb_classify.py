# -*- coding: utf-8 -*-
"""R262 bm-b: run conflict classifier, parse first JSON object, dump summary."""
import io
import json
import os
import subprocess

env = dict(os.environ, PYTHONIOENCODING="utf-8")
out = subprocess.run(
    ["python", ".codely-cli/skills/bigmoney-conflict-resolve/scripts/"
     "classify_conflicts.py"],
    capture_output=True, env=env).stdout.decode("utf-8", errors="replace")
d, _ = json.JSONDecoder().raw_decode(out[out.index("{"):])
io.open("results/_r262_classify.json", "w", encoding="utf-8",
        newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
for c in d["classified"]:
    print(c["state"], c["path"], "->", c["class"])
u = d.get("unknown", d.get("unclassified", []))
print("UNKNOWN:", json.dumps(u, ensure_ascii=False, indent=1))
for k, v in d.items():
    if k not in ("classified", "unknown", "unclassified"):
        print(k, ":", str(v)[:200])
