# -*- coding: utf-8 -*-
"""r326 bm-a: timestamp-drift correction (actual clock ~13:45, not 14:2x/14:5x).
Renames the W2-A adjudication MSG to its true time (1342), fixes its ts field,
and updates all cross-references (pool entry / ticket / report line)."""
import io
import json
import os

OLD_ID = "MSG-20260927-1425-bm-a"
NEW_ID = "MSG-20260927-1342-bm-a"

# 1. rename + rets the MSG file
old_p = rf"fleet\inbox\{OLD_ID}-w2a-universe-reading.json"
new_p = rf"fleet\inbox\{NEW_ID}-w2a-universe-reading.json"
assert os.path.exists(old_p), old_p
d = json.load(io.open(old_p, encoding="utf-8"))
assert OLD_ID in d["id"], d["id"]
d["id"] = f"{NEW_ID}-w2a-universe-reading"
d["ts"] = "2026-09-27T13:42:00+08:00"
s = json.dumps(d, indent=1, ensure_ascii=False)
json.loads(s)
with io.open(new_p, "w", encoding="utf-8", newline="") as f:
    f.write(s)
os.remove(old_p)
print("MSG renamed ->", new_p)

# 2. pool entry reference
pool_p = r"results\runnable_pool.json"
b = open(pool_p, "rb").read().decode("utf-8")
assert OLD_ID in b
b = b.replace(OLD_ID, NEW_ID)
json.loads(b)
with io.open(pool_p, "w", encoding="utf-8", newline="") as f:
    f.write(b)
print("pool entry ref fixed")

# 3. ticket reference
tk_p = r"fleet\tasks\T-2026-09-26-86-P1.json"
b2 = open(tk_p, "rb").read()
has_bom = b2.startswith(b"\xef\xbb\xbf")
t = b2.decode("utf-8-sig")
assert OLD_ID in t
t = t.replace(OLD_ID, NEW_ID)
json.loads(t)
open(tk_p, "wb").write((b"\xef\xbb\xbf" if has_bom else b"") + t.encode("utf-8"))
print("ticket ref fixed (bom:", has_bom, ")")

# 4. report line: MSG ref + line timestamp
rp = r"logs\iteration-loop\round_reports-bm-a.md"
b3 = open(rp, "rb").read()
assert OLD_ID.encode() in b3 and b"2026-09-27T14:5x:xx" in b3
b3 = b3.replace(OLD_ID.encode(), NEW_ID.encode())
b3 = b3.replace(b"2026-09-27T14:5x:xx+08:00 | R326", b"2026-09-27T13:45:xx+08:00 | R326")
open(rp, "wb").write(b3)
s3 = io.open(rp, encoding="utf-8").read()
assert NEW_ID in s3 and "13:45:xx" in s3 and OLD_ID not in s3
print("report line fixed")

# 5. sweep: no stale OLD_ID anywhere in tracked fleet/results/logs files
import glob
stale = []
for pat in (r"fleet\**\*.json", r"results\*.json", r"logs\**\*.md"):
    for f in glob.glob(pat, recursive=True):
        try:
            if OLD_ID in io.open(f, encoding="utf-8").read():
                stale.append(f)
        except Exception:
            pass
assert not stale, stale
print("zero stale refs; correction complete")
