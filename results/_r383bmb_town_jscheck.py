# -*- coding: utf-8 -*-
# r383 bm-b: extract <script> block(s) from town.html for node --check diagnostics
import re, sys, os, subprocess

def extract_src(text, out):
    m = re.search(r"<script>(.*?)</script>", text, re.S)
    js = m.group(1)
    open(out, "w", encoding="utf-8", newline="\n").write(js)
    return js.count("\n") + 1

tmp = os.environ.get("TEMP", ".")
head = subprocess.run(["git", "show", "HEAD:town.html"], capture_output=True).stdout.decode("utf-8")
for name, text in [("head", head), ("cur", open("town.html", encoding="utf-8").read())]:
    out = os.path.join(tmp, "town_%s.js" % name)
    n = extract_src(text, out)
    r = subprocess.run(["node", "--check", out], capture_output=True, text=True)
    print(name, "| lines", n, "| node --check exit", r.returncode)
    if r.returncode != 0:
        print(r.stderr[:600])
