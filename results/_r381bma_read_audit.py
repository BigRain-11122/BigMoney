import os, re, io

out = io.open(r'results\_r381bma_tmp9.txt', 'w', encoding='utf-8')
FACES = ['compute_audit.json', 'regime_state.json', 'autofill_state.json',
         'runnable_pool.json', 'gate_attrition.json', 'post_review_criteria.json']
# scan production dirs only; skip results/, research/, logs/ archives
SCAN_DIRS = ['scripts', 'monitor', 'live', 'firm', 'Tools', 'config', 'engine', 'tests']
hits = {f: [] for f in FACES}
for d in SCAN_DIRS:
    if not os.path.isdir(d):
        continue
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in ('__pycache__', '.git')]
        for fn in files:
            if not fn.endswith('.py'):
                continue
            p = os.path.join(root, fn)
            try:
                txt = io.open(p, encoding='utf-8', errors='replace').read()
            except Exception:
                continue
            for i, line in enumerate(txt.splitlines(), 1):
                for face in FACES:
                    if face in line:
                        s = line.strip()
                        # classify read vs write vs comment
                        kind = '?'
                        if re.search(r'(open\(.*[\'\"]r|json\.load|read_|load_sources|_lane_view|FACE)', s):
                            kind = 'READ?'
                        if re.search(r'(write_lane|mirror|dump|write_text|atomic_write|write_json|save)', s, re.I):
                            kind = 'WRITE?'
                        hits[face].append('%s L%d [%s]: %s' % (p, i, kind, s[:160]))

for face in FACES:
    out.write('==== %s (%d hits) ====\n' % (face, len(hits[face])))
    for h in hits[face]:
        out.write(h + '\n')
    out.write('\n')
out.close()
print('done')
