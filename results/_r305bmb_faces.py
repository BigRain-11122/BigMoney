# -*- coding: utf-8 -*-
"""r305 bm-b faces probe: compute_audit flag face + autofill tick + runnable_pool
open-entry face, for the round report honest naming (O-1810 / WM probe section 4)."""
import io
import json


def load(p):
    return json.load(io.open(p, encoding="utf-8-sig"))


a = load("results/compute_audit.json")
print("AUDIT top keys:", sorted(a.keys()))
for k in sorted(a.keys()):
    if "flag" in k.lower() or k in ("ts", "verdict", "audit_version", "version"):
        v = a[k]
        print("AUDIT %s = %s" % (k, json.dumps(v, ensure_ascii=False)[:300] if not isinstance(v, str) else v))
h = a.get("history") or []
if h:
    last = h[-1]
    face = {k: last.get(k) for k in last if "flag" in k.lower() or k in ("ts", "verdict")}
    print("AUDIT hist_last n=%d face=%s" % (len(h), json.dumps(face, ensure_ascii=False)[:400]))

s = load("results/autofill_state.json")
print("AUTOFILL:", json.dumps(s, ensure_ascii=False)[:500])

p = load("results/runnable_pool.json")
if isinstance(p, dict):
    print("POOL top keys:", list(p.keys())[:12])
    for k, v in p.items():
        if isinstance(v, list):
            print("POOL %s n=%d" % (k, len(v)))
            for e in v[:8]:
                if isinstance(e, dict):
                    face = {kk: e.get(kk) for kk in
                            ("batch_id", "id", "status", "owner", "claimed_by",
                             "lane", "workers_plan", "ticket") if kk in e}
                    print("  entry:", json.dumps(face, ensure_ascii=False)[:220])
        elif isinstance(v, dict):
            print("POOL %s dict n=%d" % (k, len(v)))
            for ek, ev in list(v.items())[:8]:
                if isinstance(ev, dict):
                    face = {kk: ev.get(kk) for kk in
                            ("status", "owner", "claimed_by", "lane") if kk in ev}
                    print("  %s: %s" % (ek, json.dumps(face, ensure_ascii=False)[:200]))
