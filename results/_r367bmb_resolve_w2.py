"""r367 bm-b wave-2: compute_audit history union (ours=origin bm-c r146, theirs=my r366 replay)."""
import subprocess, json
p="results/compute_audit.json"
def blob(s):
    r=subprocess.run(["git","show",":%d:%s"%(s,p)],capture_output=True)
    if r.returncode: raise SystemExit("blob fail")
    return r.stdout
o,t=blob(2),blob(3)
jo,jt=json.loads(o.decode("utf-8")),json.loads(t.decode("utf-8"))
seen,merged=set(),[]
for row in jo.get("history",[])+jt.get("history",[]):
    k=json.dumps(row,sort_keys=True,ensure_ascii=False)
    if k not in seen: seen.add(k); merged.append(row)
merged.sort(key=lambda r:r.get("ts",""))
cap=merged[-200:]
lo,lt=jo.get("latest",{}).get("ts"),jt.get("latest",{}).get("ts")
print("ours hist=%d theirs hist=%d union=%d cap=%d latest ours=%s theirs=%s"%(len(jo["history"]),len(jt["history"]),len(merged),len(cap),lo,lt))
assert lo and (not lt or lo>=lt), "ours latest not newest"
assert len(cap)==len({json.dumps(r,sort_keys=True,ensure_ascii=False) for r in cap})
out=dict(jo); out["history"]=cap
tail=b"\n" if o.endswith(b"}\n") else b""
open(p,"wb").write(json.dumps(out,indent=2,ensure_ascii=False).encode("utf-8")+tail)
json.loads(open(p,encoding="utf-8").read()); assert b"<<<<<<<" not in open(p,"rb").read()
print("compute_audit wave-2 resolved+validated")
