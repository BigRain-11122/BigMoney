# -*- coding: utf-8 -*-
"""r306 bm-b: probe 3rd collision (2 UU: autofill_state, runnable_pool).
base=7df7a767 common, ours=b9c22863 (bm-a r301), theirs=d2394875 (bm-b r306)."""
import subprocess, json

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("blob fail %d %s" % (stage, path))
    return r.stdout

# --- runnable_pool ---
P = "results/runnable_pool.json"
o = json.loads(blob(2, P).decode("utf-8-sig"))   # bm-a r301
t = json.loads(blob(3, P).decode("utf-8-sig"))   # bm-b r306
oe = {e["id"]: e for e in o.get("entries", [])}
te = {e["id"]: e for e in t.get("entries", [])}
print("runnable_pool: ours entries=%d theirs entries=%d | ids only-ours=%s only-theirs=%s" % (
    len(oe), len(te), sorted(set(oe) - set(te)), sorted(set(te) - set(oe))))
for eid in sorted(set(oe) | set(te)):
    a, b = oe.get(eid), te.get(eid)
    if a and b and json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
        da = {k: a.get(k) for k in set(a) | set(b) if a.get(k) != b.get(k)}
        print("  DIFF id=%s fields->ours:%s" % (eid, json.dumps(da, ensure_ascii=False)[:300]))
        print("       ours full:", json.dumps(a, ensure_ascii=False)[:400])
        print("       theirs full:", json.dumps(b, ensure_ascii=False)[:400])
for kk in sorted(set(o) | set(t)):
    if kk != "entries" and o.get(kk) != t.get(kk):
        print("  meta %s: ours=%r theirs=%r" % (kk, str(o.get(kk))[:60], str(t.get(kk))[:60]))

# --- autofill_state ---
P = "results/autofill_state.json"
o = json.loads(blob(2, P).decode("utf-8-sig"))
t = json.loads(blob(3, P).decode("utf-8-sig"))
ol, tl = o.get("launches", []), t.get("launches", [])
um = {}
for r in ol + tl:
    um.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
print("autofill: launches ours=%d theirs=%d union=%d" % (len(ol), len(tl), len(um)))
print("  last_tick ours=%s theirs=%s" % (o.get("last_tick", {}).get("ts"), t.get("last_tick", {}).get("ts")))
print("  top-keys equal:", sorted(o) == sorted(t))
print("  ours last launch ts=%s | theirs last launch ts=%s" % (ol[-1].get("ts"), tl[-1].get("ts")))
okeys = {k for k in o if k not in ("launches", "last_tick")}
tkeys = {k for k in t if k not in ("launches", "last_tick")}
for k in sorted(okeys | tkeys):
    if o.get(k) != t.get(k):
        print("  scalar %s: ours=%r theirs=%r" % (k, str(o.get(k))[:60], str(t.get(k))[:60]))
print("PROBE3-DONE")
