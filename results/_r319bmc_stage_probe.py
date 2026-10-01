import subprocess, json
def st(n):
    r = subprocess.run(['git', 'show', ':%d:results/p2cal_ext/n1_w9/shard-0-of-12.json' % n],
                       capture_output=True)
    return json.loads(r.stdout)
a, b = st(2), st(3)
def which(d):
    s = json.dumps(d, ensure_ascii=False)
    hits = [m for m in ('bm-c', 'bm-b', 'bm-a') if m in s]
    return hits or ['?']
print('stage2 machine-ish:', which(a), '| stage3:', which(b))
print('stage2 top keys:', sorted(a.keys()))
print('stage3 top keys:', sorted(b.keys()))
for k in sorted(set(a) | set(b)):
    if a.get(k) != b.get(k):
        sa = json.dumps(a.get(k), ensure_ascii=False)[:150]
        sb = json.dumps(b.get(k), ensure_ascii=False)[:150]
        print('DIFF key=%s' % k)
        print('  :2: %s' % sa)
        print('  :3: %s' % sb)
