import json, subprocess, re

def blob(path):
    r = subprocess.run(['git', 'show', f'origin/main:{path}'],
                       capture_output=True)
    assert r.returncode == 0, r.stderr.decode()[:200]
    return r.stdout  # bytes

for path in ['results/runnable_pool.bm-b.json', 'results/runnable_pool.bm-c.json']:
    b = blob(path)
    txt = b.decode('utf-8')
    print('===', path, 'bytes', len(b), 'CRLF', b.count(b'\r\n'))
    for m in re.finditer(r'"key": "(fund-value-p1-[^"]*)"', txt):
        seg = txt[m.end():m.end() + 300]
        own = re.search(r'"owner": "([^"]*)"', seg)
        since = re.search(r'"owner_since": "([^"]*)"', seg)
        print(' ', m.group(1)[:44], '| owner', own.group(1) if own else None,
              '| since', since.group(1) if since else None)
        if 'FUND-VALUE' in txt[max(0, m.start()-500):m.start()]:
            pass
