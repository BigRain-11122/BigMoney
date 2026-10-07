import json, subprocess, sys

UU = subprocess.run(['git','diff','--name-only','--diff-filter=U'],capture_output=True,text=True).stdout.split()
RT_KEYS = {'generated','generated_at','elapsed_sec','ts','asof','runtime_meta','last_run','updated','clock','now'}
results = {}
for f in UU:
    try:
        ours = subprocess.run(['git','show',f':2:{f}'],capture_output=True).stdout.decode('utf-8',errors='replace')
        theirs = subprocess.run(['git','show',f':3:{f}'],capture_output=True).stdout.decode('utf-8',errors='replace')
        try:
            o, t = json.loads(ours), json.loads(theirs)
            o2 = {k:v for k,v in o.items() if k not in RT_KEYS}
            t2 = {k:v for k,v in t.items() if k not in RT_KEYS}
            payload_same = (o2 == t2)
            diff_keys = sorted({k for k in set(o2)|set(t2) if o2.get(k)!=t2.get(k)})
        except Exception as e:
            payload_same = None; diff_keys = [f'non-json: {e}']
        results[f] = {'payload_same':payload_same,'diff_keys':diff_keys[:12],
                      'ours_bytes':len(ours),'theirs_bytes':len(theirs)}
    except Exception as e:
        results[f] = {'error':str(e)}
print(json.dumps(results,ensure_ascii=False,indent=1))
