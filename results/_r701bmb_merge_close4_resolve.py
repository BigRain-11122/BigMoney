# r701 merge close-4 generic resolver: UU set auto-recipes (jsonl=union, ledger keys union, snapshot=ts-new, text=ts regex)
import json, re, subprocess, io
def stage(i,p): return subprocess.run(["git","show",f":{i}:{p}"],capture_output=True).stdout
uu = subprocess.run(["git","diff","--name-only","--diff-filter=U"],capture_output=True,text=True).stdout.split()
TS_KEYS=("ts","generated","updated","as_of","asof","scan_ts","last_scan","generated_at","updated_at","evidence_cutoff","cutoff","date","last_run","time")
def pick(obj,d=0,best=""):
    if d>4: return best
    if isinstance(obj,dict):
        for k,v in obj.items():
            if isinstance(v,str) and k.lower() in TS_KEYS and re.match(r"2026-\d\d-\d\d",v):
                if v>best: best=v
            else: best=pick(v,d+1,best)
    elif isinstance(obj,list):
        for it in obj[:60]: best=pick(it,d+1,best)
    return best
LED={"results/compute_audit.json":("history","launches"),"results/regime_state.json":("launches","transitions","history")}
for p in uu:
    o,t=stage(2,p),stage(3,p)
    if p.endswith(".jsonl"):  # append-log line union
        ol,tl=o.decode("utf-8","replace").splitlines(),t.decode("utf-8","replace").splitlines()
        merged=[];seen=set()
        for l in ol+tl:
            if l not in seen: seen.add(l);merged.append(l)
        out=("\n".join(merged)+"\n").encode("utf-8")
        note=f"jsonl union {len(ol)}+{len(tl)}->{len(merged)}"
    elif p in LED:  # ledger union + state take-new
        od,td=json.loads(o),json.loads(t)
        for key in LED[p]:
            a,b=od.get(key,[]),td.get(key,[]);s=set();m=[]
            for e in a+b:
                sig=json.dumps(e,sort_keys=True,ensure_ascii=False)
                if sig not in s: s.add(sig);m.append(e)
            m.sort(key=lambda e: pick(e) or ""); od[key]=m
        for k in td:
            if k not in LED[p]: od[k]=td[k]
        out=(json.dumps(od,ensure_ascii=False,indent=1)+"\n").encode(); note="ledger union "+",".join(f"{k}:{len(od[k])}" for k in LED[p])
    elif p.endswith(".json"):
        try: o_ts,t_ts=pick(json.loads(o)),pick(json.loads(t))
        except Exception: o_ts=t_ts=""
        side=3 if t_ts>=o_ts else 2; out=(t if side==3 else o); json.loads(out); note=f"snapshot ours={o_ts or 'NOTS'} theirs={t_ts or 'NOTS'} -> {'theirs' if side==3 else 'ours'}"
    else:  # .md/.js text: ts regex pick side whole bytes
        o_ts=str(max(re.findall(r"2026-10-0\d[T ]\d\d:\d\d:\d\d",o.decode("utf-8","replace")) or [""]))
        t_ts=str(max(re.findall(r"2026-10-0\d[T ]\d\d:\d\d:\d\d",t.decode("utf-8","replace")) or [""]))
        side=3 if t_ts>=o_ts else 2; out=(t if side==3 else o); note=f"text ours={o_ts} theirs={t_ts} -> {'theirs' if side==3 else 'ours'}"
    io.open(p,"wb").write(out)
    print(f"{p:50s} {note}")
print("CLOSE4 RESOLVED",len(uu))
