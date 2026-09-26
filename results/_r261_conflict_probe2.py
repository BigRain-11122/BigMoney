import subprocess, json, re

def blob(rev, path):
    out = subprocess.run(['git', 'show', '%s:%s' % (rev, path)], capture_output=True)
    return out.stdout

for p in ['results/dashboard_status.json', 'results/daily_scorecard.json']:
    for rev in [':2', ':3']:
        o = json.loads(blob(rev, p).decode('utf-8-sig'))
        print(p, rev, 'top keys:', list(o.keys())[:12])
        for k in ('meta', 'stamp', 'info', 'header'):
            if isinstance(o.get(k), dict):
                print('  ', k, '->', {kk: str(vv)[:26] for kk, vv in list(o[k].items())[:5]})

pj = 'results/dashboard_status.js'
pat = re.compile(r'"generated_at":\s*"([^"]+)"')
for rev in [':2', ':3']:
    s = blob(rev, pj).decode('utf-8-sig')
    m = pat.search(s)
    print('js', rev, 'generated_at:', m.group(1) if m else None)

ph = 'results/daily_scorecard.html'
mgen = re.compile(r'[Gg]enerated[^:]*:\s*"?([^"<\n]{8,30})')
mdate = re.compile(r'(20\d\d-\d\d-\d\d[T ][\d:]+)')
for rev in [':2', ':3']:
    s = blob(rev, ph).decode('utf-8-sig')
    a = mgen.search(s)
    b = mdate.search(s[:800])
    print('html', rev, 'gen:', a.group(1).strip() if a else None, '| first-ts:', b.group(1) if b else None)
