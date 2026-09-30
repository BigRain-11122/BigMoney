# r258 bm-c: next-berth eligibility scan (r446 dual-face order + r448 three-key-face law)
# Purpose: mechanical anti-duplication scan of zoo A/B-layer candidate families
#          NOT already judged / berth-declared / gate-parked, to pick the next
#          INNOVATION-QUOTA berth row for bm-c (supply floor ready=0<3 standing breach).
# Key faces per family (r448): family name UNION zooNN_* alias UNION known consumer batch ids.
import json
import os
import re
import time

FAMILIES = {
    'zoo81_slope_r2_rotation': [r'slope_r2', r'slope-r2', r'SLOPE-R2', r'rsqr', r'zoo81'],
    'zoo82_dual_momentum_etf': [r'dual_momentum', r'dual-momentum', r'DUAL-MOMENTUM', r'zoo82'],
    'zoo83_gem_ashare': [r'gem_ashare', r'gem-ashare', r'GEM-ASHARE', r'zoo83'],
    'zoo84_crowding_vote': [r'crowding_vote', r'crowding-vote', r'CROWDING-VOTE', r'zoo84'],
    'zoo90_alligator_timing': [r'alligator', r'zoo90'],
    'zoo79_micro_cap': [r'micro_cap', r'micro-cap', r'MICRO-CAP', r'zoo79'],
    'zoo93_disposition_cgo': [r'disposition', r'\bcgo\b', r'zoo93'],
    'zoo94_lhb_inst_dist': [r'lhb_inst', r'LHB-INST', r'zoo94'],
    'zoo95_index_higher_mom': [r'higher_mom', r'higher-mom', r'HIGHER-MOM', r'zoo95'],
}

SCAN_DIRS = ['results', 'research', 'Tools', 'fleet']
SKIP_DIRS = {'__pycache__', '.git', 'node_modules'}
TEXT_EXT = ('.md', '.json', '.jsonl', '.py', '.txt', '.csv', '.js', '.html', '.ps1')

# classification weight: which hit faces constitute a prior judgment/consumption mark
VERDICT_FACE = re.compile(r'innovation_quota|TRIAL_LABOR_W\d+|PREREG|verdict|judged|p1e_partial|digests', re.I)


def scan():
    compiled = {fam: [re.compile(p, re.I) for p in pats] for fam, pats in FAMILIES.items()}
    hits = {fam: {} for fam in FAMILIES}
    files_scanned = 0
    for top in SCAN_DIRS:
        for root, dirs, files in os.walk(top):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in files:
                if not fn.endswith(TEXT_EXT):
                    continue
                if fn.endswith('.npy'):
                    continue
                path = os.path.join(root, fn)
                try:
                    with open(path, encoding='utf-8', errors='ignore') as fh:
                        text = fh.read()
                except OSError:
                    continue
                files_scanned += 1
                for fam, pats in compiled.items():
                    for pat in pats:
                        if pat.search(text):
                            hits[fam].setdefault(path, {'pats': []})['pats'].append(pat.pattern)
                            break
    return hits, files_scanned


def classify(path):
    if 'p1e_partial' in path:
        return 'burned-partial (P-1e IC face)'
    if re.search(r'innovation_quota', path, re.I):
        return 'innovation-quota face (verdict/berth/prereg)'
    if re.search(r'TRIAL_LABOR_W\d+_PREREG', path):
        return 'trial-labor wave prereg (consumption face)'
    if 'digests' in path:
        return 'digest (evidence card, not a verdict)'
    if 'ASTYLE_ZOO' in path:
        return 'zoo registry itself'
    if 'catalog' in path.lower() or 'fill_ladder' in path:
        return 'catalog face'
    return 'other mention'


def main():
    ts = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
    hits, n = scan()
    out = {
        'artifact': 'next-berth eligibility scan (mechanical anti-dup three-key-face)',
        'machine': 'bm-c', 'round': 258, 'ts': ts,
        'law_refs': ['r446 dual-face order (results face first)', 'r448 three-key-face law (family U zooNN alias U consumer batch)',
                     'supply floor ready=0<3 standing breach (O-1614 sec.1)'],
        'scan_scope': SCAN_DIRS, 'files_scanned': n,
        'candidates': {},
    }
    for fam in FAMILIES:
        fh = hits[fam]
        verdict_faces = [p for p in fh if re.search(r'innovation_quota|p1e_partial|TRIAL_LABOR_W\d+_PREREG', p, re.I)]
        other = [p for p in fh if p not in verdict_faces]
        out['candidates'][fam] = {
            'n_hit_files': len(fh),
            'verdict_face_files': sorted(verdict_faces)[:12],
            'other_hit_files_sample': sorted(other)[:10],
            'classes': sorted({classify(p) for p in fh}),
        }
    with open('results/_r258bmc_zoo_eligibility_scan.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    # console-safe digest
    for fam, d in out['candidates'].items():
        vf = d['verdict_face_files']
        print(fam, '| hit_files:', d['n_hit_files'], '| VERDICT-FACE hits:', len(vf))
        for p in vf[:6]:
            print('   *', p)


if __name__ == '__main__':
    main()
