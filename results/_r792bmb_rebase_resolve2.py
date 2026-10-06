# r792 bm-b S0 rebase resolver part 2 (pick 6: lane live faces)
# p1d_gates.json -> snapshot take-new by ts; face/state_bm-b.json -> daemon live-wins stage3 (local live face);
# history_bm-b.jsonl -> line-level union zero loss (r188/r217).
import subprocess, json, re

TS_RE = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]')

def blob(st, path):
    r = subprocess.run(['git', 'show', ':%d:%s' % (st, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('git show rc=%d' % r.returncode)
    return r.stdout

def deep_max_ts(obj, best=''):
    if isinstance(obj, dict):
        for v in obj.values():
            best = deep_max_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_max_ts(v, best)
    elif isinstance(obj, str) and TS_RE.match(obj) and obj > best:
        best = obj
    return best

receipt = {}

# p1d_gates.json: snapshot take-new by deep ts probe
p = 'results/p1d_gates.json'
b2, b3 = blob(2, p), blob(3, p)
t2, t3 = deep_max_ts(json.loads(b2)), deep_max_ts(json.loads(b3))
winner, side = (b3, 'stage3-mine') if t3 > t2 else (b2, 'stage2-origin')
open(p, 'wb').write(winner)
json.loads(open(p, 'rb').read())
receipt[p] = {'class': 'snapshot', 'ts2': t2, 'ts3': t3, 'took': side}

# saturation bm-b daemon live faces: live-wins = stage3 (local daemon newest)
for p in ('results/saturation_engine/face_bm-b.json', 'results/saturation_engine/state_bm-b.json'):
    b3 = blob(3, p)
    open(p, 'wb').write(b3)
    json.loads(open(p, 'rb').read())
    receipt[p] = {'class': 'daemon-live-face', 'took': 'stage3-mine (live-wins r620 law)',
                  'ts': deep_max_ts(json.loads(b3))}

# history_bm-b.jsonl: line-level union zero loss
p = 'results/saturation_engine/history_bm-b.jsonl'
l2 = blob(2, p).decode('utf-8').splitlines()
l3 = blob(3, p).decode('utf-8').splitlines()
seen, merged = set(), []
for ln in l2 + l3:
    if ln not in seen:
        seen.add(ln)
        merged.append(ln)
eol = '\r\n' if blob(3, p).count(b'\r\n') else '\n'
open(p, 'wb').write(eol.join(merged).encode('utf-8'))
assert len(merged) == len(set(l2) | set(l3)), 'union zero-loss failed'
receipt[p] = {'class': 'append-log', 'union_lines': len(merged), 's2_lines': len(l2), 's3_lines': len(l3)}

with open('results/_r792bmb_rebase_resolve2.json', 'w') as f:
    json.dump(receipt, f, indent=1, ensure_ascii=False)
print('RESOLVED part2:', len(receipt), 'faces')
for k, v in receipt.items():
    print(' ', k, '->', v)
