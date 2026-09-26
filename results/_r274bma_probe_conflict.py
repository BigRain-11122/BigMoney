# -*- coding: utf-8 -*-
import subprocess, json, re
def blob(stage, p):
    return subprocess.run(['git', 'show', f':{stage}:{p}'], capture_output=True).stdout

def tsmax(d):
    best = None
    def walk(x):
        nonlocal best
        if isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
        elif isinstance(x, str):
            m = re.search(r'2026-09-2[0-9][ T][0-9:.]+', x)
            if m:
                s = m.group(0).replace('T', ' ')[:19]
                if best is None or s > best: best = s
    walk(d)
    return best

o = blob(2, 'results/dashboard_status.js').decode('utf-8')
t = blob(3, 'results/dashboard_status.js').decode('utf-8')
mo = re.search(r'generated.{0,4}(.{19,20})', o)
mt = re.search(r'generated.{0,4}(.{19,20})', t)
print('js ours gen:', mo.group(1) if mo else None, '| theirs gen:', mt.group(1) if mt else None)

do = json.loads(blob(2, 'results/dashboard_status.json').decode('utf-8'))
dt = json.loads(blob(3, 'results/dashboard_status.json').decode('utf-8'))
print('json ours ts:', tsmax(do), '| theirs ts:', tsmax(dt))

co = blob(2, 'CODELY.md').decode('utf-8')
ct = blob(3, 'CODELY.md').decode('utf-8')
ol = set(co.splitlines()); tl = set(ct.splitlines())
print('CODELY theirs-only lines:', len(tl - ol), 'ours-only:', len(ol - tl))
for l in (tl - ol):
    print('  theirs-only:', l[:90])
for l in list(ol - tl)[:6]:
    print('  ours-only:', l[:90])
print('ours ends crlf:', co.endswith('\r\n'), 'theirs ends crlf:', ct.endswith('\r\n'))
