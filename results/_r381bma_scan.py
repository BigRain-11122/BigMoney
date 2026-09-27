import json, glob, io, os

out = io.open(r'results\_r381bma_tmp2.txt', 'w', encoding='utf-8')
for p in sorted(glob.glob('fleet/tasks/*.json')):
    d = json.load(open(p, encoding='utf-8'))
    st = d.get('status')
    own = d.get('claimed_by', '')
    if st in ('open', 'claimed', 'in_progress'):
        t = d.get('title', d.get('subject', ''))[:100]
        out.write('%s | %s | %s | %s\n' % (p, st, own, t))
out.write('=== council seats ===\n')
cand = r'C:\Users\sjs20\Desktop\FluxGroup\cph4\council.md'
if os.path.exists(cand):
    with io.open(cand, encoding='utf-8') as f:
        txt = f.read()
    out.write(txt[:4000])
else:
    out.write('council.md NOT FOUND at %s\n' % cand)
out.close()
print('done')
