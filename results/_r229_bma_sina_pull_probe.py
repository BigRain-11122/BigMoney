# r229 bm-a probe: T-72 s2 first-pull progress read (machine-prefixed per R221 collision law)
import json, glob, os, re, time

src = open('scripts/update_sina_mf.py', encoding='utf-8-sig').read()
cands = sorted(set(re.findall(r'"([^"]*(?:checkpoint|progress)[^"]*\.json)"', src)))
print('script-declared state files:', cands)

for f in cands:
    if os.path.exists(f):
        d = json.load(open(f, encoding='utf-8'))
        s = json.dumps(d, ensure_ascii=False)
        print('---', f, os.path.getsize(f), 'bytes mtime', time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(f))))
        print(s[:700])

# also scan loose results/sina_mf* files
for f in glob.glob('results/sina_mf*'):
    print('LOOSE', f, os.path.getsize(f), 'bytes mtime', time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(f))))
for f in glob.glob('data/sina_mf*'):
    if os.path.isdir(f):
        print('DIR', f, len(os.listdir(f)), 'entries; newest 3:')
        entries = [(os.path.getmtime(os.path.join(f, x)), x) for x in os.listdir(f)]
        for mt, x in sorted(entries)[-3:]:
            print('   ', x, time.strftime('%H:%M:%S', time.localtime(mt)))
    else:
        print('FILE', f, os.path.getsize(f))
