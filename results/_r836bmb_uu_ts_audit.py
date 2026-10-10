import json, subprocess, sys
out = subprocess.run(['git','ls-files','-u'], capture_output=True, text=True).stdout
stages = {}
for line in out.splitlines():
    parts = line.split('\t')
    mode, sha, stage = parts[0].split()
    stages.setdefault(parts[1], {})[int(stage)] = sha

def blob_text(sha):
    return subprocess.run(['git','cat-file','-p',sha], capture_output=True, text=True, errors='replace').stdout

def ts_of(txt):
    try:
        j = json.loads(txt)
    except Exception:
        return None
    best = None
    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and any(t in k.lower() for t in ('ts','time','date','asof','generated','updated','epoch')) and len(v) >= 8:
                    if best is None or v > best: best = v
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(j)
    return best

for path, st in sorted(stages.items()):
    t2, t3 = ts_of(blob_text(st.get(2,''))), ts_of(blob_text(st.get(3,'')))
    if t2 and t3:
        winner = 'STAGE2(origin)' if t2 >= t3 else 'STAGE3(pick)'
    elif t2: winner = 'STAGE2(origin)'
    elif t3: winner = 'STAGE3(pick)'
    else: winner = 'NO-TS'
    print(f"{path}\tS2={t2}\tS3={t3}\t=> {winner}")
