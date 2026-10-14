"""r1001 bm-a: locate all W2..W241 sites in the frozen W242 template (console-safe)."""
import subprocess

r = subprocess.run(['git', 'log', '--diff-filter=A', '--format=%H', '--',
                    'research/PERPETUAL_N1_W242_PREREG.md'], capture_output=True)
tpl_sha = r.stdout.decode().strip().splitlines()[0]
tpl = subprocess.run(['git', 'show', tpl_sha + ':research/PERPETUAL_N1_W242_PREREG.md'],
                    capture_output=True).stdout.decode('utf-8')
lines = []
for needle in ('W2..W241', 'W1..W241', 'v2..W241', 'W5..W241', 'W136..W241',
               '239 行', '238 行', '本机 bm-c 实例', '_w242bma', '19:5x', '17:3x',
               'engine_owner==bm-a 123', '950,135', '945,189', 'n1_w240_results.json'):
    pos = -1
    hits = []
    while True:
        pos = tpl.find(needle, pos + 1)
        if pos < 0:
            break
        ln = tpl.count('\n', 0, pos) + 1
        hits.append((ln, tpl[max(0, pos - 50):pos + len(needle) + 30].replace('\n', ' ~ ')))
    lines.append('== %s : %d hits' % (needle, len(hits)))
    for ln, ctx in hits:
        lines.append('   L%d: %s' % (ln, ctx))
with open('results/_r1001bma_tplsites.txt', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))
print('written results/_r1001bma_tplsites.txt lines=%d' % len(lines))
