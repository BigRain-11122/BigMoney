# r695 bm-a: pool + crash fuse diagnosis for CONTEST-YTD-P1-RC (16 refusals live red face)
import json, subprocess, glob, os

# 1) pool entries overview
pool = json.loads(open(r'results\runnable_pool.json', 'rb').read().decode('utf-8'))
entries = pool.get('entries', [])
print('== pool entries:', len(entries))
for e in entries:
    st = e.get('status'); key = e.get('key') or e.get('id')
    print(f"  {key} | status={st} | owner={e.get('owner')} | since={e.get('owner_since')}")

# 2) fuse record
fuse = json.loads(open(r'results\crash_fuse.json', 'rb').read().decode('utf-8'))
sig = fuse.get('sigs', {}).get('scripts/contest_ytd_legs.py|revcensus')
print('== fuse sig:', json.dumps(sig, ensure_ascii=False))

# 3) find contest crash logs / products
hits = []
for pat in [r'results\**\*contest*', r'logs\**\*contest*']:
    hits += glob.glob(pat, recursive=True)
hits += [p for p in glob.glob(r'results\*.json') if 'contest' in p.lower()]
print('== contest files on disk:')
for h in sorted(set(hits))[:20]:
    print('  ', h, os.path.getsize(h), 'bytes', 'mtime', __import__('datetime').datetime.fromtimestamp(os.path.getmtime(h)).strftime('%H:%M:%S'))

# 4) last 30 lines of any contest runner log found
for h in sorted(set(hits)):
    if h.endswith('.log') or h.endswith('.txt'):
        try:
            tail = open(h, 'rb').read().decode('utf-8', errors='replace').strip().splitlines()[-12:]
            print(f'== tail {h}:')
            for ln in tail:
                print('   ', ln[:240])
        except Exception as ex:
            print('read fail', h, ex)
print('PROBE_OK')
