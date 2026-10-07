import subprocess, json, re

def sb(rel, st):
    return subprocess.run(['git', 'show', ':%d:%s' % (st, rel)], capture_output=True).stdout

TS = re.compile(r'20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}')

def dmax(o, best=None):
    if isinstance(o, dict):
        for v in o.values():
            best = dmax(v, best)
    elif isinstance(o, list):
        for v in o:
            best = dmax(v, best)
    elif isinstance(o, str) and TS.match(o):
        if best is None or o > best:
            best = o
    return best

for rel in ['results/dashboard_status.json', 'results/scorecard_v1.json',
            'results/strategy_scorecard.json', 'results/lhb_update_status.json']:
    o2, o3 = sb(rel, 2), sb(rel, 3)
    t2 = dmax(json.loads(o2.decode('utf-8', errors='replace'))) if o2 else None
    t3 = dmax(json.loads(o3.decode('utf-8', errors='replace'))) if o3 else None
    w = ':3:' if (t3 and (not t2 or t3 > t2)) else ':2:'
    print(rel, '| :2:', t2, '| :3:', t3, '| winner:', w)

rel = 'results/dashboard_status.js'
o2, o3 = sb(rel, 2), sb(rel, 3)


def jts(b):
    m = re.search(rb'"generated[^"]*"[^"]*"([^"]+)"', b)
    if not m:
        m = re.search(rb'generated[\'": ]+([0-9T: -]+)', b)
    return m.group(1).decode(errors='replace') if m else None

print(rel, '| :2:', jts(o2), '| :3:', jts(o3))
