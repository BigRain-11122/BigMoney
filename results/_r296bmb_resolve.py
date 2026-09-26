# -*- coding: utf-8 -*-
"""r296 bm-b S0 rebase UU resolve (canonical recipes r203/R208/r215/r245/r140/r223).
ours(stage2)=HEAD d480e202 (bm-a autofill tick claim run-0of1, r199 launch-claim + r290 self-commit);
theirs(stage3)=bm-b pre-S0 fold commit (local tick 04:30:01 pool_empty_or_busy).
Single UU = autofill_state.json, classifier GREEN mixed-dict+ledger.
launches = union both blobs -> ts desc cap50 (R215 rolling window) -> ASC write-back (r245);
last_tick = inner-ts compare, take newer whole dict, same-second tie -> HEAD/ours (r140);
CRLF mirror base blob (r223); parse gate before write-back + isinstance dict assert (r185).
"""
import json
import subprocess

P = "results/autofill_state.json"

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("blob fail stage %d %s" % (stage, path))
    return r.stdout

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
union_all = sorted(um.values(), key=lambda r: str(r.get("ts", "")), reverse=True)
dropped = union_all[50:]
merged_launches = sorted(union_all[:50], key=lambda r: str(r.get("ts", "")))  # ASC write-back (r245)
print("launches union %d|%d -> union=%d cap50=%d dropped_oldest=%d" % (
    len(ol), len(tl), len(union_all), len(merged_launches), len(dropped)))
if dropped:
    print("dropped ts range (must be oldest): %s .. %s" % (
        dropped[-1].get("ts"), dropped[0].get("ts")))
    assert str(dropped[0].get("ts", "")) <= str(merged_launches[0].get("ts", "")), "cap must drop oldest only"
# zero-loss gate: every kept entry is in A or B
ka = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in merged_launches}
ba = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in ol + tl}
assert ka <= ba, "kept entries must all come from union"

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
print("autofill_state written crlf=%s last_tick dict ok, parse-verified" % crlf)
