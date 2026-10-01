import json, glob, os
for f in sorted(glob.glob('fleet/tasks/*.json')):
    d = json.load(open(f, encoding='utf-8'))
    print(os.path.basename(f), '|', d.get('status'), '|', d.get('claimed_by', ''), '|', (d.get('title') or d.get('subject') or '')[:60])
print('--- watermark ---')
p = 'results/watermark_red.json'
print(open(p, encoding='utf-8').read()[:400] if os.path.exists(p) else 'absent')
