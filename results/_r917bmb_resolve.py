# r917 resolver: 2 UU faces from rebase replay (c7c8d8746 onto b3d66545c origin)
# 1. _r686bmb_d19_check.json     -> ts-newer-wins (my probe evidence snapshot 23:04 vs origin absorbed copy)
# 2. _r686bmb_orders_fresh.md    -> ts-newer-wins by embedded date (r967 pattern verbatim)
# Both = bm-b owned regen-class probe faces; default prefer :3: (replay = latest session write).
import json, subprocess, re

GIT = r"C:\Program Files\Git\cmd\git.exe"

def blob(rev):
    r = subprocess.run([GIT, "show", rev], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show {rev} rc={r.returncode}: {r.stderr[:200]}")
    if len(r.stdout) < 100:
        raise RuntimeError(f"git show {rev} returned {len(r.stdout)}B (<100) = missing stage, refusing write (r710 law)")
    return r.stdout

def scan_ts(data):
    try:
        d = json.loads(data.decode("utf-8"))
    except Exception as e:
        return None, f"JSONDecodeFail:{e}"
    for k in ("scanned_at", "ts", "timestamp", "generated_at", "read_at"):
        if k in d:
            return d[k], None
    return None, "no-ts-key:" + ",".join(list(d.keys())[:8])

path = "results/_r686bmb_d19_check.json"
b2 = blob(f":2:{path}")  # base side = origin (replayed-onto)
b3 = blob(f":3:{path}")  # replay side = mine (c7c8d8746)
t2, e2 = scan_ts(b2)
t3, e3 = scan_ts(b3)
winner = ":3:"
if t2 and t3 and str(t2) > str(t3):
    winner = ":2:"
data = b3 if winner == ":3:" else b2
with open(path, "wb") as f:
    f.write(data)
# r609 law: re-read + reparse self-verify
chk = open(path, "rb").read()
assert chk == data, "write-back mismatch"
if winner == ":3:":
    json.loads(chk.decode("utf-8"))
print(f"{path}: base={t2 or e2} mine={t3 or e3} -> {winner} ({len(data)}B) reparse-OK")

path = "results/_r686bmb_orders_fresh.md"
b2 = blob(f":2:{path}").decode("utf-8", "replace")
b3 = blob(f":3:{path}").decode("utf-8", "replace")

def find_date(s):
    m = re.findall(r"2026-\d{2}-\d{2}[T ]\d{2}:\d{2}", s)
    return m[0] if m else None

d2, d3 = find_date(b2), find_date(b3)
winner = ":3:"
if d2 and d3 and d2 > d3:
    winner = ":2:"
data = (b3 if winner == ":3:" else b2).encode("utf-8")
with open(path, "wb") as f:
    f.write(data)
chk = open(path, "rb").read()
assert chk == data, "write-back mismatch"
assert b"<<<<<<<" not in chk and b"=======" not in chk and b">>>>>>>" not in chk, "marker residue"
print(f"{path}: base_date={d2} mine_date={d3} -> {winner} ({len(data)}B) marker-scan-clean")
print("RESOLVE-DONE")
