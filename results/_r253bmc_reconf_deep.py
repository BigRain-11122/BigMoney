#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r253 bm-c: dump ours/theirs for CODELY.md, archive, compute_audit history faces."""
import json, subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    return r.stdout.decode("utf-8")

# --- compute_audit history compare ---
o = json.loads(blob(2, "results/compute_audit.json"))
t = json.loads(blob(3, "results/compute_audit.json"))
oh, th = o.get("history", []), t.get("history", [])
print("compute_audit history ours=%d theirs=%d" % (len(oh), len(th)))
okeys = {json.dumps(h, sort_keys=True) for h in oh}
tkeys = {json.dumps(h, sort_keys=True) for h in th}
only_t = [h for h in th if json.dumps(h, sort_keys=True) not in okeys]
only_o = [h for h in oh if json.dumps(h, sort_keys=True) not in tkeys]
print("  entries only-in-theirs=%d only-in-ours=%d" % (len(only_t), len(only_o)))
for h in only_t[:6]:
    print("  T+", json.dumps({k: h.get(k) for k in ("ts", "host", "verdict", "py_cpu_pct")}, ensure_ascii=False))
for h in only_o[:6]:
    print("  O+", json.dumps({k: h.get(k) for k in ("ts", "host", "verdict", "py_cpu_pct")}, ensure_ascii=False))
print("  ours.latest.ts=%s theirs.latest.ts=%s" % (o.get("latest", {}).get("ts"), t.get("latest", {}).get("ts")))

# --- CODELY.md section-level compare ---
co = blob(2, "CODELY.md"); ct = blob(3, "CODELY.md")
lo, lt = co.splitlines(), ct.splitlines()
so, st = set(lo), set(lt)
print("\nCODELY.md ours=%d lines theirs=%d lines" % (len(lo), len(lt)))
print("--- lines only-in-theirs (mine r252 additions) ---")
for line in lt:
    if line not in so and line.strip():
        print("T| " + line[:150])
print("--- lines only-in-ours (origin r446 additions) ---")
for line in lo:
    if line not in st and line.strip():
        print("O| " + line[:150])

# --- archive 202609.md compare ---
ao = blob(2, "research/memory-archive/202609.md"); at = blob(3, "research/memory-archive/202609.md")
alo, alt = ao.splitlines(), at.splitlines()
aso, ast = set(alo), set(alt)
print("\narchive202609 ours=%d lines theirs=%d lines" % (len(alo), len(alt)))
onlyt = [l for l in alt if l not in aso and l.strip()]
onlyo = [l for l in alo if l not in ast and l.strip()]
print("only-in-theirs=%d only-in-ours=%d" % (len(onlyt), len(onlyo)))
for l in onlyt[:20]:
    print("T| " + l[:160])
for l in onlyo[:20]:
    print("O| " + l[:160])
