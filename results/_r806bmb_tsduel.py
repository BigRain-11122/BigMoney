import subprocess, json, re, sys, io

files = subprocess.run(['git','diff','--name-only','--diff-filter=U'],capture_output=True,text=True).stdout.split()
print('UU files:', files)

def ts_of(b):
    try:
        j = json.loads(b.decode('utf-8', errors='replace'))
    except Exception:
        m = re.search(rb'"(?:ts|updated|generated_at|asof)"\s*:\s*"([^"]+)"', b)
        return m.group(1).decode() if m else 'NO-JSON'
    if isinstance(j, dict):
        for k in ('ts','updated','generated_at','asof','generated','last_action','now'):
            v = j.get(k)
            if isinstance(v, str):
                return v
    return 'NO-TS'

for f in files:
    ours = subprocess.run(['git','show',':2:'+f],capture_output=True).stdout
    theirs = subprocess.run(['git','show',':3:'+f],capture_output=True).stdout
    print(f, '| origin-side:', ts_of(ours), '| ours-side:', ts_of(theirs))
