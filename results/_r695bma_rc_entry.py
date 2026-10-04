# r695 bm-a: CONTEST-YTD-P1-RC entry detail + crash log full + prereg locate
import json, glob, os

pool = json.loads(open(r'results\runnable_pool.json', 'rb').read().decode('utf-8'))
for e in pool.get('entries', []):
    if 'RC' in str(e.get('key', '')):
        print('== ENTRY:', json.dumps(e, ensure_ascii=False, indent=1)[:1600])

print('== crash log full:')
print(open(r'logs\autofill_CONTEST-YTD-P1-RC-0OF1.log', 'rb').read().decode('utf-8', errors='replace'))

print('== prereg / spec candidates:')
for pat in [r'research\**\*CONTEST*', r'research\**\*contest*']:
    for h in glob.glob(pat, recursive=True):
        print('  ', h, os.path.getsize(h))

print('== recent MSG mentioning CONTEST:')
for h in sorted(glob.glob(r'fleet\inbox\MSG-*.md') + glob.glob(r'fleet\inbox\processed\MSG-*.md')):
    try:
        txt = open(h, 'rb').read().decode('utf-8', errors='replace')
    except Exception:
        continue
    if 'CONTEST' in txt and os.path.getmtime(h) > 1791000000:  # ~today
        print('  ', h)
print('PROBE_OK')
