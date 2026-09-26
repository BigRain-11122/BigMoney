# -*- coding: utf-8 -*-
"""r293 bm-b S0 stash-pop resolve (canonical recipes r203/R208/r245/r290).
ours(stage2)=HEAD 37487c72 (bm-a push: pool 03:39:00 done-flip + autofill richer last_tick);
theirs(stage3)=stashed bm-b local tick dirt (older intermediate face).
runnable_pool: entry-id sets equal 54/54, only 2 entries differ = ready->done time evolution
(CN-TREND-ETF-P1, CENSUS-FUS-S2-W1, done_at 03:39:00 + result_ref filled on HEAD) =>
stash face strictly older => take ours/HEAD whole-face, zero loss (r290 pool-upstream-base law).
autofill_state: mixed-dict+ledger canonical (launches union cap50 ASC + last_tick inner-ts compare tie->HEAD r140
+ isinstance dict assert + CRLF producer mirror r223).
"""
import json
import subprocess

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("blob fail %s" % path)
    return r.stdout

def write_raw(path, raw):
    with open(path, "wb") as f:
        f.write(raw)

# --- runnable_pool.json: take ours/HEAD whole face (byte-identical, verified parsable)
POOL = "results/runnable_pool.json"
pool_ours = blob(2, POOL)
json.loads(pool_ours.decode("utf-8-sig"))  # parse gate before write-back (r185 law)
write_raw(POOL, pool_ours)
print("runnable_pool: took HEAD whole-face (%d bytes, 54 entries, updated_at 03:39:00)" % len(pool_ours))

# --- autofill_state.json: mixed-dict+ledger canonical
P = "results/autofill_state.json"
o_raw = blob(2, P)
t_raw = blob(3, P)
base_raw = blob(1, P)
o = json.loads(o_raw.decode("utf-8-sig"))
t = json.loads(t_raw.decode("utf-8-sig"))

ol = o.get("launches", [])
tl = t.get("launches", [])
um = {}
for r in ol + tl:
    key = json.dumps(r, sort_keys=True, ensure_ascii=False)
    um.setdefault(key, r)
merged_launches = sorted(um.values(), key=lambda r: str(r.get("ts", "")), reverse=True)[:50]
merged_launches = sorted(merged_launches, key=lambda r: str(r.get("ts", "")))  # ASC write-back (r245)
print("launches union %d|%d -> %d (cap50)" % (len(ol), len(tl), len(merged_launches)))

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
        pick = "ours(HEAD %s >= theirs %s)" % (to, tt)
else:
    pick = "last_tick non-dict faces -> keep ours"
print("last_tick:", pick)
merged["launches"] = merged_launches

crlf = b"\r\n" in base_raw
nl = "\r\n" if crlf else "\n"
payload = json.dumps(merged, ensure_ascii=False, indent=1)
with open(P, "w", encoding="utf-8", newline="") as f:
    f.write(payload.replace("\n", nl))
chk = json.loads(open(P, encoding="utf-8-sig").read())
assert isinstance(chk.get("last_tick"), dict), "last_tick must stay dict"
assert chk["launches"] == merged_launches
print("autofill_state written crlf=%s last_tick dict ok" % crlf)
