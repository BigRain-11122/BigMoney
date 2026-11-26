"""Round 2123 bm-c: is the uncommitted generation stable enough to publish?

Reads `git status --porcelain`, buckets each modified path by mtime age relative
to now. A generation still being written shows files touched within minutes; a
finished one shows everything older than the last chain run.
"""
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

out = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, encoding="utf-8").stdout
files = []
for line in out.splitlines():
    if len(line) < 4:
        continue
    path = line[3:].strip().strip('"')
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    files.append(path)

now = time.time()
buckets = {}
newest = 0.0
newest_path = ""
missing = 0
for p in files:
    try:
        age = now - os.path.getmtime(p)
    except OSError:
        missing += 1
        continue
    if age > newest:
        newest, newest_path = age, p
    key = "<1h" if age < 3600 else ("1-6h" if age < 21600 else ("6-24h" if age < 86400 else ">24h"))
    buckets[key] = buckets.get(key, 0) + 1

print("dirty_files=%d missing=%d buckets=%s" % (len(files), missing, buckets))
print("newest_age_min=%.1f newest=%s" % (newest / 60.0, newest_path))
