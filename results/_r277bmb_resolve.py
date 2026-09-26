# -*- coding: utf-8 -*-
# r277 bm-b S0 stash-pop conflict resolver: results/autofill_state.json
# Recipe (bigmoney-conflict-resolve skill, mixed-dict+ledger, r203/R208/r215/r220/r245):
#   launches = union -> ts desc -> cap 50 -> re-sort ts ASCENDING (r245: producer=append order,
#              desc write-back = whole-column flip pseudo-diff inherited by producer tick)
#   last_tick = compare internal ts, WHOLE-dict assignment (no str() compare), assert isinstance dict
#   Format mirror: probe base blob (HEAD) for indent/EOL/trailing-newline/ensure_ascii; write with
#              newline translation mode. Parse-verify before add (r185).
# Sides: :2: ours = HEAD after pull (bm-a r274 wrap face, last_tick 22:40:01)
#        :3: theirs = stashed local watchdog face (bm-b, last_tick 22:50:01, newer)
import json
import subprocess
import sys

PATH = "results/autofill_state.json"


def blob(rev):
    r = subprocess.run(["git", "show", rev + ":" + PATH], capture_output=True)
    if r.returncode != 0:
        print("FATAL: cannot read", rev)
        sys.exit(2)
    return r.stdout


raw_ours = blob(":2")   # HEAD (pulled origin face)
raw_theirs = blob(":3")  # stashed local face
A = json.loads(raw_ours)
B = json.loads(raw_theirs)

# --- launches: union by full-record identity ---
def ident(rec):
    return json.dumps(rec, sort_keys=True, ensure_ascii=False)

seen = {}
for rec in A.get("launches", []) + B.get("launches", []):
    seen[ident(rec)] = rec
union = list(seen.values())
union.sort(key=lambda l: l.get("ts", ""), reverse=True)  # ts desc -> keep newest 50
union = union[:50]
union.sort(key=lambda l: l.get("ts", ""))  # r245: re-sort ascending before write-back
n_union = len(union)
print("launches: ours=%d theirs=%d union=%d (cap50 -> %d)" % (
    len(A.get("launches", [])), len(B.get("launches", [])), len(seen), n_union))

# --- last_tick: newer internal ts wins, whole dict ---
lt_a, lt_b = A.get("last_tick"), B.get("last_tick")
assert isinstance(lt_a, dict) and isinstance(lt_b, dict), "last_tick not dict on a side"
ts_a = lt_a.get("ts", "")
ts_b = lt_b.get("ts", "")
last_tick = lt_b if ts_b >= ts_a else lt_a
assert isinstance(last_tick, dict), "last_tick resolution not dict"
print("last_tick: ours ts=%s theirs ts=%s -> took %s" % (ts_a, ts_b, ts_b if ts_b >= ts_a else ts_a))

out = {"launches": union, "last_tick": last_tick}

# --- format mirror from base blob (HEAD face) ---
bom = raw_ours.startswith(b"\xef\xbb\xbf")
crlf = b"\r\n" in raw_ours
indent = 1
for line in raw_ours.split(b"\n")[1:2]:
    indent = len(line) - len(line.lstrip(b" "))
    if not indent:
        indent = 1
trailing_nl = raw_ours.endswith(b"\n")
try:
    raw_ours.decode("ascii")
    ensure_ascii_safe = True
except UnicodeDecodeError:
    ensure_ascii_safe = False
print("format: bom=%s crlf=%s indent=%d trailing_nl=%s ensure_ascii=%s" % (
    bom, crlf, indent, trailing_nl, ensure_ascii_safe))

txt = json.dumps(out, indent=indent, ensure_ascii=True)
data = txt.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
if crlf:
    data = data.replace(b"\n", b"\r\n")
if trailing_nl:
    if not data.endswith(b"\r\n" if crlf else b"\n"):
        data += b"\r\n" if crlf else b"\n"

with open(PATH, "wb") as f:
    f.write(data)

# --- parse-verify + zero-loss (r185) ---
back = json.loads(open(PATH, "rb").read().decode("utf-8-sig" if bom else "utf-8"))
assert len(back["launches"]) == n_union, "launch count drift"
assert isinstance(back["last_tick"], dict), "last_tick not dict after write"
assert ident(back["last_tick"]) == ident(last_tick), "last_tick drift"
for rec in union:
    assert ident(rec) in {ident(r) for r in back["launches"]}, "record lost"
print("VERIFIED: %d launches, last_tick dict intact, zero-loss OK" % n_union)
