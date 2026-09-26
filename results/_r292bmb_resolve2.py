# -*- coding: utf-8 -*-
"""r292 bm-b autofill_state stash-pop resolve (mixed-dict+ledger recipe r203/R208/r245).
ours(stage2)=HEAD merged face (bm-a tick 03:20:01); theirs(stage3)=stashed bm-b local tick dirt.
"""
import json
import subprocess

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("blob fail")
    return r.stdout

P = "results/autofill_state.json"
o_raw = blob(2, P)
t_raw = blob(3, P)
base_raw = blob(1, P)
o = json.loads(o_raw.decode("utf-8-sig"))
t = json.loads(t_raw.decode("utf-8-sig"))

# launches: union by identity -> ts desc cap50 -> re-sort ts ASC (r245 write-order law)
ol = o.get("launches", [])
tl = t.get("launches", [])
um = {}
for r in ol + tl:
    key = json.dumps(r, sort_keys=True, ensure_ascii=False)
    um.setdefault(key, r)
merged_launches = sorted(um.values(), key=lambda r: str(r.get("ts", "")), reverse=True)[:50]
merged_launches = sorted(merged_launches, key=lambda r: str(r.get("ts", "")))  # ASC on write-back
print("launches union %d|%d -> %d (cap50)" % (len(ol), len(tl), len(merged_launches)))

# last_tick: dict-internal ts compare, tie -> HEAD(ours) (r140)
merged = dict(o)
lo, lt = o.get("last_tick"), t.get("last_tick")
if isinstance(lo, dict) and isinstance(lt, dict):
    to, tt = str(lo.get("ts", "")), str(lt.get("ts", ""))
    if tt > to:
        merged["last_tick"] = lt
        pick = "theirs(bm-b %s > ours %s)" % (tt, to)
    elif tt == to:
        merged["last_tick"] = lo
        pick = "tie->HEAD(ours) %s" % (to)
    else:
        merged["last_tick"] = lo
        pick = "ours(bm-a %s >= theirs %s)" % (to, tt)
else:
    pick = "last_tick non-dict faces -> keep ours"
print("last_tick:", pick)
merged["launches"] = merged_launches

# newline mirror of base blob (CRLF producer r223/r234: detect, write with translation)
crlf = b"\r\n" in base_raw
nl = "\r\n" if crlf else "\n"
payload = json.dumps(merged, ensure_ascii=False, indent=1)
with open(P, "w", encoding="utf-8", newline="") as f:
    f.write(payload.replace("\n", nl))
chk = json.loads(open(P, encoding="utf-8-sig").read())
assert isinstance(chk.get("last_tick"), dict), "last_tick must stay dict"
assert chk["launches"] == merged_launches
print("written crlf=%s last_tick dict ok" % crlf)
