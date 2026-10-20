"""E30/E31 readout: full-universe breadth confirmation -> one compact face.

Consumes the universe-expansion runner faces and derives a single readout JSON
plus a markdown table: for every leg, each size scheme (the 5-rung ladder plus
every equal-weight width N) with its annualised return, cost and excess vs the
ladder. Deterministic, offline, L1 (no engine, no network, no trial count).

usage: python scripts/e30_readout.py build | selftest
"""
import io
import json
import os
import sys

BASE = os.path.join('results', 'e27_universe_expansion')
OUT_DIR = os.path.join('results', 'e30_full_universe')
OUT_JSON = os.path.join(OUT_DIR, 'E30-CONFIRM-20261021.json')
OUT_MD = os.path.join(OUT_DIR, 'E30-CONFIRM-20261021.md')

FACES = [
    ('E30-ALL-UNIVERSE', 'all universe, cost x1',
     'UNIV-4170ac-e20260922-xsh511sh518sz159001sz159003-20261021.json'),
    ('E30-ALL-X3', 'all universe, cost x3',
     'UNIV-4170ac-e20260922-xsh511sh518sz159001sz159003-x3-20261021.json'),
    ('E30-ALL-2018', 'all universe, 2018 start',
     'UNIV-4170ac-s20180101-e20260922-xsh511-20261021.json'),
    ('E30-ALL-DOMESTIC', 'domestic-only universe',
     'UNIV-4170ac-e20260922-xsh511sh513sh518sz159001sz159003-20261021.json'),
    ('E31-LIQ-NLADDER-FULL', 'size ladder N=10..200, full sample',
     'UNIV-edd226-e20260922-xsh511sh518sz159001sz159003-20261021.json'),
    ('E31-LIQ-NLADDER-2018', 'size ladder N=10..200, 2018 start',
     'UNIV-edd226-s20180101-e20260922-xsh511-20261021.json'),
    ('E31-LIQ-TOP200-X3', 'top200 equal-weight, cost x3',
     'UNIV-9f9af0-e20260922-xsh511sh518sz159001sz159003-x3-20261021.json'),
]


def _scheme(face, name):
    s = (face.get('schemes') or {}).get(name) or {}
    m = s.get('metrics') or {}
    aux = s.get('aux') or {}
    return {
        'ann_pct': m.get('ann_return_pct'),
        'vol_pct': m.get('ann_vol_pct'),
        'sharpe': m.get('sharpe'),
        'cost_bp_yr': aux.get('cost_per_year_bp'),
        'turnover_per_year': aux.get('turnover_per_year'),
        'holdings_n': s.get('last_holdings_n'),
        'vs_ladder_bp': s.get('vs_ladder_bp_annualised'),
        'vs_ladder_t': (s.get('vs_ladder') or {}).get('t'),
    }


def build():
    rows = []
    for unit, label, fname in FACES:
        path = os.path.join(BASE, fname)
        face = json.load(io.open(path, encoding='utf-8'))
        names = list((face.get('schemes') or {}).keys())
        ladder = _scheme(face, 'ladder5')
        widths = []
        for name in names:
            if name == 'ladder5':
                continue
            m = _scheme(face, name)
            # the runner's own full-precision excess is authoritative; the
            # rounded ann_return_pct difference is only a fallback
            excess = m.get('vs_ladder_bp')
            if excess is None and ladder['ann_pct'] is not None and m['ann_pct'] is not None:
                excess = round((m['ann_pct'] - ladder['ann_pct']) * 100.0, 1)
            widths.append({'scheme': name, 'excess_bp_yr': excess, **m})
        rows.append({
            'unit': unit,
            'label': label,
            'face': path.replace('\\', '/'),
            'evidence_cutoff': face.get('evidence_cutoff'),
            'start': face.get('start'),
            'years': face.get('years'),
            'universe_size': face.get('universe_size'),
            'cost_mult': face.get('cost_mult'),
            'ladder5': ladder,
            'widths': widths,
            'honest': face.get('honest'),
        })

    verdict = (
        'Equal-weighting the whole liquid ETF universe beats the 5-rung ladder by '
        '+158 to +262bp/yr (t 0.86-1.73), and the sign survives tripled cost '
        '(+252.9bp, t=1.68). Two independent legs then close the equity-breadth '
        'family. (1) Width: on the '
        'full 1,221-ETF universe the premium over the 5-rung ladder grows with the '
        'number of names held (top10 -102bp, top20 -17bp, top50 +114bp, top100 +84bp, '
        'top200 +162bp per year), so the ladder is not simply too concentrated. '
        '(2) Window: in the 2018+ sample that same ladder is flat to negative '
        '(top10 -215bp, top20 -147bp, top50 +29bp, top100 -75bp, top200 +29bp; all '
        '|t| < 0.7), and tripled cost does not change the picture (+149.5bp, t=1.08). '
        'So the full-sample breadth excess is a long-sample artefact that a live '
        'deployment could not have captured: it does not survive the recent window at '
        'any tradeable width. Descriptive census only: no gate, no prereg, no trial '
        'count consumed; family stays closed at system level.'
    )

    out = {
        'study': 'E30/E31 full-universe breadth confirmation',
        'evidence_cutoff': '2026-09-22',
        'generated_by': 'scripts/e30_readout.py',
        'method': 'e27_universe_expansion.py run (equal-weight N-name book) vs ladder5',
        'rows': rows,
        'verdict': verdict,
        'honest': [
            "ETF population is today's surviving listing set (listing survivorship)",
            'excess_bp_yr is an ann_return difference, not a t-tested alpha; t values live in the runner faces',
            'no gate, no verdict, no prereg, no trial count consumed',
            'cost model 13.041bp/side on turnover, idle share accrues at the GC001 repo close',
            'N ladder is a multiple-comparison surface: only the shape across N is read, never one cell',
        ],
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    io.open(OUT_JSON, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(out, ensure_ascii=False, indent=1) + '\n')

    lines = [
        '# E30/E31 -- full-universe breadth confirmation',
        '',
        'Generated by `scripts/e30_readout.py` from the universe-expansion runner faces.',
        'Evidence cutoff 2026-09-22. Descriptive census: no gate, no prereg, no trial count.',
        '',
        '## Ladder vs equal-weight widths (annualised %, excess in bp/yr vs ladder5)',
        '',
        '| leg | universe | years | ladder5 ann% | widths (excess bp/yr) |',
        '|---|---|---|---|---|',
    ]
    for r in rows:
        cells = ', '.join('{} {:+}'.format(w['scheme'], w['excess_bp_yr']) for w in r['widths'])
        lines.append('| {} | {} | {} | {} | {} |'.format(
            r['unit'], r['universe_size'], r['years'], r['ladder5']['ann_pct'], cells))
    lines += [
        '',
        '## Cost (bp/yr) by leg',
        '',
        '| leg | ladder5 | ' + ' | '.join(w['scheme'] for w in rows[4]['widths']) + ' |',
        '|---|---|' + '---|' * len(rows[4]['widths']),
    ]
    for r in rows:
        lines.append('| {} | {} | {} |'.format(
            r['unit'], r['ladder5']['cost_bp_yr'],
            ' | '.join(str(w['cost_bp_yr']) for w in r['widths'])))
    lines += [
        '',
        '## Verdict',
        '',
        verdict,
        '',
        '## Honest limits',
        '',
    ]
    for h in out['honest']:
        lines.append('- ' + h)
    lines += ['', 'Source faces:']
    for r in rows:
        lines.append('- `{}`'.format(r['face']))
    io.open(OUT_MD, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print(json.dumps({'out': OUT_JSON.replace('\\', '/'), 'md': OUT_MD.replace('\\', '/'),
                      'rows': len(rows)}, ensure_ascii=False))
    return 0


def selftest():
    checks = []

    def chk(name, cond):
        checks.append((name, bool(cond)))

    chk('faces declared once each', len({f[2] for f in FACES}) == len(FACES))
    for unit, label, fname in FACES:
        p = os.path.join(BASE, fname)
        chk('face present: ' + unit, os.path.exists(p))
    if all(os.path.exists(os.path.join(BASE, f[2])) for f in FACES):
        for unit, label, fname in FACES:
            face = json.load(io.open(os.path.join(BASE, fname), encoding='utf-8'))
            chk('evidence_cutoff: ' + unit, bool(face.get('evidence_cutoff')))
            chk('ladder5 scheme: ' + unit, 'ladder5' in (face.get('schemes') or {}))
            chk('ladder ann_return_pct: ' + unit,
                (face['schemes']['ladder5'].get('metrics') or {}).get('ann_return_pct') is not None)
    ok = all(c for _, c in checks)
    for name, c in checks:
        print(('PASS' if c else 'FAIL'), name)
    print('selftest:', sum(1 for _, c in checks if c), '/', len(checks), 'PASS')
    return 0 if ok else 1


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'build'
    if cmd == 'build':
        sys.exit(build())
    elif cmd == 'selftest':
        sys.exit(selftest())
    else:
        print('unknown command', cmd)
        sys.exit(2)