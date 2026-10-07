import subprocess, json, re

files = subprocess.run(['git','diff','--name-only','--diff-filter=U'],capture_output=True,text=True).stdout.split()
print('UU count:', len(files))

def side(stage, f):
    return subprocess.run(['git','show',stage+':'+f],capture_output=True).stdout

for f in files:
    o = side(':2:', f)
    t = side(':3:', f)
    info = []
    for tag, b in (('H',o),('P',t)):
        if f.endswith('.jsonl'):
            lines = [ln for ln in b.decode('utf-8',errors='replace').splitlines() if ln.strip()]
            info.append(tag+':rows=%d' % len(lines))
            if lines:
                try:
                    j = json.loads(lines[-1])
                    info.append(tag+':last=' + json.dumps({k: j[k] for k in list(j)[:4]}, ensure_ascii=False)[:120])
                except Exception:
                    info.append(tag+':lastRAW=' + lines[-1][:100])
        else:
            try:
                j = json.loads(b.decode('utf-8',errors='replace'))
                tsv = None
                def find_ts(d, depth=0):
                    if depth > 3: return None
                    if isinstance(d, dict):
                        for k in ('ts','updated','generated_at','asof','generated','now','report_ts','report_date'):
                            if isinstance(d.get(k), str):
                                return k+'='+d[k]
                        for v in d.values():
                            r = find_ts(v, depth+1)
                            if r: return r
                    return None
                tsv = find_ts(j)
                info.append(tag+':json ts='+str(tsv)+' keys='+str(list(j)[:8]))
            except Exception:
                txt = b.decode('utf-8',errors='replace')
                m = re.search(r'(ts|updated|generated_at|asof)[":\s]+([0-9T:\-\. +]+)', txt[:3000])
                info.append(tag+':text ts='+(m.group(2) if m else 'NONE')[:40])
    print(f, ' || '.join(info))
