import subprocess

def run(*a):
    return subprocess.run(list(a), capture_output=True).stdout.decode('utf-8', errors='replace')

out = []
for br in ['machine/bm-c-r87', 'machine/bm-c-r88', 'machine/bm-c-r89']:
    ref = 'origin/' + br
    b = run('git', 'show', ref + ':CODELY.md')
    m = open('CODELY.md', encoding='utf-8').read()
    bl = set(l.strip() for l in b.splitlines() if l.strip())
    ml = set(l.strip() for l in m.splitlines() if l.strip())
    missing = sorted(x for x in bl - ml if x.startswith('-'))
    out.append('=== %s CODELY.md missing-in-main %d lines:' % (br, len(missing)))
    for x in missing:
        out.append('  ' + x)
    # also archive journal check
    for f in ['research/memory-archive/202609.md', 'logs/iteration-loop/round_reports-bm-c.md',
              'HQ-FEEDBACK.md', 'fleet/FLEET-OPS.md']:
        try:
            b2 = run('git', 'show', ref + ':' + f)
        except Exception:
            b2 = ''
        if not b2 and f != 'research/memory-archive/202609.md':
            continue
        m2 = open(f, encoding='utf-8').read() if f != '__none__' else ''
        bl2 = set(l.strip() for l in b2.splitlines() if l.strip())
        ml2 = set(l.strip() for l in m2.splitlines() if l.strip())
        miss2 = sorted(x for x in bl2 - ml2 if x.startswith(('- ', '## ', '### ')))
        out.append('--- %s %s : missing %d' % (br, f, len(miss2)))
        for x in miss2[:15]:
            out.append('  MISS: ' + x[:220])

open('results/_r338bma_foldcheck3_out.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written', len(out), 'lines')
