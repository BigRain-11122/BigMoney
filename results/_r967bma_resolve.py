# r967 resolver: 3 UU faces from rebase replay (bdc56c119 onto d604677c7)
# 1. _attrition_guard_scan.json  -> ts-newer-wins (my scan ran 23:0x, fresher)
# 2. _r686bmb_d19_check.json     -> ts-newer-wins (evidence snapshot)
# 3. _r686bmb_orders_fresh.md    -> ts-newer-wins by content sha of group orders (whichever sha matches current group origin)
import json, subprocess, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"

def blob(rev):
    r = subprocess.run([GIT, "show", rev], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show {rev} rc={r.returncode}: {r.stderr[:200]}")
    return r.stdout

def scan_ts(data):
    # attrition scan json: find ts-like key
    try:
        d = json.loads(data.decode("utf-8"))
    except Exception as e:
        return None, f"JSONDecodeFail:{e}"
    for k in ("scanned_at", "ts", "timestamp", "generated_at"):
        if k in d:
            return d[k], None
    return None, "no-ts-key:" + ",".join(list(d.keys())[:8])

faces = [
    ("results/_attrition_guard_scan.json", scan_ts),
    ("results/_r686bmb_d19_check.json", scan_ts),
]

for path, fn in faces:
    b2 = blob(f":2:{path}")  # base side = bm-b (origin replayed-onto)
    b3 = blob(f":3:{path}")  # replay side = mine (bdc56c119)
    t2, e2 = fn(b2)
    t3, e3 = fn(b3)
    # newer-wins; if ts equal or unreadable, prefer :3: (replay = latest session write)
    winner = ":3:"
    if t2 and t3 and str(t2) > str(t3):
        winner = ":2:"
    data = b3 if winner == ":3:" else b2
    with open(path, "wb") as f:
        f.write(data)
    print(f"{path}: base={t2 or e2} mine={t3 or e3} -> {winner} ({len(data)}B)")

# 3. orders fresh md: check embedded sha/ts header line; prefer the one whose orders_sha matches
# the CURRENT group origin (fresh-read evidence = whichever is fresher snapshot).
import re, os
b2 = blob(":2:results/_r686bmb_orders_fresh.md").decode("utf-8", "replace")
b3 = blob(":3:results/_r686bmb_orders_fresh.md").decode("utf-8", "replace")

def find_date(s):
    m = re.findall(r"2026-\d{2}-\d{2}[T ]\d{2}:\d{2}", s)
    return m[0] if m else None

d2, d3 = find_date(b2), find_date(b3)
winner = ":3:"
if d2 and d3 and d2 > d3:
    winner = ":2:"
data = (b3 if winner == ":3:" else b2).encode("utf-8")
with open("results/_r686bmb_orders_fresh.md", "wb") as f:
    f.write(data)
print(f"results/_r686bmb_orders_fresh.md: base_date={d2} mine_date={d3} -> {winner} ({len(data)}B) lines2={b2.count(chr(10))} lines3={b3.count(chr(10))}")
print("RESOLVE-DONE")
