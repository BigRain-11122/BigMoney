"""r382 bm-b rebase-storm probe: dump both-side ts fields for all 14 UU faces (r159 law: ts decides, not :2:/:3: labels)."""
import subprocess, json

FILES = [
    'CODELY.md',
    'docs/daily_report/REPORT-2026-09-28.json',
    'docs/daily_report/REPORT-2026-09-28.md',
    'results/compute_audit.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/regime_state.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/token_usage.json',
    'results/update_status.json',
]

def side(path, n):
    b = subprocess.run(['git', 'show', ':%d:%s' % (n, path)], capture_output=True).stdout
    return b

for p in FILES:
    s2, s3 = side(p, 2), side(p, 3)
    print('=' * 8, p, 'bytes :2:=%d :3:=%d' % (len(s2), len(s3)))
    if p.endswith('.md'):
        # text faces: show head/tail lines count
        l2 = s2.decode('utf-8', 'replace').splitlines()
        l3 = s3.decode('utf-8', 'replace').splitlines()
        print('  :2: lines=%d first=%r last=%r' % (len(l2), l2[0][:60] if l2 else '', l2[-1][:80] if l2 else ''))
        print('  :3: lines=%d first=%r last=%r' % (len(l3), l3[0][:60] if l3 else '', l3[-1][:80] if l3 else ''))
        only3 = [x for x in l3 if x not in l2]
        print('  lines only in :3: (=mine-new): %d' % len(only3))
        for x in only3[:3]:
            print('    +', x[:110])
        only2 = [x for x in l2 if x not in l3]
        print('  lines only in :2: (=origin-new): %d' % len(only2))
        for x in only2[:3]:
            print('    -', x[:110])
    else:
        for tag, b in ((':2:', s2), (':3:', s3)):
            try:
                d = json.loads(b.decode('utf-8'))
                if isinstance(d, dict):
                    tsf = {k: d[k] for k in d if isinstance(d.get(k), str) and ('ts' in k.lower() or 'generated' in k.lower() or 'updated' in k.lower() or 'as_of' in k.lower())}
                    hist = {k: len(d[k]) for k in d if isinstance(d.get(k), list) and ('history' in k.lower() or 'launches' in k.lower() or 'transitions' in k.lower())}
                    print('  %s ts=%s ledger=%s' % (tag, tsf or '-', hist or '-'))
                else:
                    print('  %s type=%s' % (tag, type(d).__name__))
            except Exception as e:
                txt = b.decode('utf-8', 'replace')
                print('  %s NON-JSON: %s | head=%r' % (tag, e, txt[:90]))
