# -*- coding: utf-8 -*-
"""r305 bm-c rebase canon-resolver (r498 AA law + r294 union domain + r298 blob rebuild).
Resolves the 12 unmerged paths of interrupted rebase (pick 5a8049da0 onto 1be030382).
Writes resolution evidence to results/_r305bmc_resolve_evidence.json
"""
import subprocess, json, hashlib, sys, collections

def blob(stage, path):
    return subprocess.check_output(['git', 'show', f':{stage}:{path}'])

def write_bytes(path, data):
    with open(path, 'wb') as f:
        f.write(data)

ENVELOPE_KEYS = {'updated', 'ts', 'generated', 'state_updated',
                 'generated_from_state_updated', 'regime_guard', 'forward_guard',
                 'asof', 'as_of', 'delta_vs_prev'}

def strip_env(o):
    if isinstance(o, dict):
        return {k: strip_env(v) for k, v in o.items() if k not in ENVELOPE_KEYS}
    if isinstance(o, list):
        return [strip_env(x) for x in o]
    return o

ev = {'resolved': {}, 'failed': {}}

# ---- 1) AA-twin JSON files: assert payload identity outside envelope -> take stage2 raw ----
aa_files = [
    'results/paper/COMPOSITE-CE-01_paper.json',
    'results/paper/COMPOSITE-CE-02_paper.json',
    'results/paper/DROUGHT-CE-01_paper.json',
    'results/paper/ENGULF-CE-01_paper.json',
    'results/paper/NEEDLE-DE-01_paper.json',
    'results/paper/VOLATILITY-CE-01_paper.json',
    'results/paper_export/export-2026-09-30.json',
    'results/paper_export/latest.json',
    'results/t35_open_fill_verify.json',
    'results/token_usage.json',
]
for p in aa_files:
    b2, b3 = blob(2, p), blob(3, p)
    if b2 == b3:
        write_bytes(p, b2); ev['resolved'][p] = 'identical->stage2'; continue
    try:
        j2 = json.loads(b2.decode('utf-8')); j3 = json.loads(b3.decode('utf-8'))
        ok = strip_env(j2) == strip_env(j3)
    except Exception as e:
        ok = False; ev['failed'][p] = f'json_err {e}'; continue
    if ok:
        write_bytes(p, b2)
        # capture origin-side regime_guard mode for evidence
        rg = j2.get('regime_guard', {})
        ev['resolved'][p] = {'action': 'AA-assert-pass->origin(:2:)',
                             'origin_regime_mode': rg.get('mode') if isinstance(rg, dict) else None}
    else:
        ev['failed'][p] = 'AA-assert-FAIL: payload differs outside envelope -> escalated, no blind side-take'

# ---- 2) x2_watch_log.jsonl: conflict-region union (r294: multiset diff, tail-append theirs-only) ----
p = 'results/x2_watch_log.jsonl'
b1, b2, b3 = blob(1, p), blob(2, p), blob(3, p)
def lines_of(b):
    txt = b.decode('utf-8')
    ls = txt.split('\r\n') if '\r\n' in txt else txt.split('\n')
    while ls and ls[-1] == '': ls.pop()
    return ls
L1, L2, L3 = lines_of(b1), lines_of(b2), lines_of(b3)
c1, c2, c3 = collections.Counter(L1), collections.Counter(L2), collections.Counter(L3)
only3 = list((c3 - c2).elements())
only2 = list((c2 - c3).elements())
base_covered = not (c1 - c2) and not (c1 - c3)
if base_covered and len(only3) == 6 and len(only2) == 6:
    eol = '\r\n' if b'\r\n' in b2[:400] else '\n'
    merged = b2
    if not merged.endswith(b'\n'): merged += eol.encode()
    for l in only3:
        merged += (l + eol).encode()
    write_bytes(p, merged)
    ev['resolved'][p] = {'action': 'union-tail-append', 'common': sum((c2 & c3).values()),
                          'ours_only': len(only2), 'theirs_only': len(only3),
                          'final_lines': len(L2) + len(only3)}
else:
    ev['failed'][p] = f'union guard FAIL: base_covered={base_covered} only2={len(only2)} only3={len(only3)}'

# ---- 3) CODELY.md: single-region union -> stage2 bytes + stage3-only line appended ----
p = 'CODELY.md'
b1, b2, b3 = blob(1, p), blob(2, p), blob(3, p)
def lines_keepends(b):
    return b.decode('utf-8').splitlines(True)
L1, L2, L3 = lines_keepends(b1), lines_keepends(b2), lines_keepends(b3)
c1, c2, c3 = collections.Counter(x.rstrip('\r\n') for x in L1), collections.Counter(x.rstrip('\r\n') for x in L2), collections.Counter(x.rstrip('\r\n') for x in L3)
only3 = list((c3 - c2).elements())
only2 = list((c2 - c3).elements())
if len(only3) == 1 and len(only2) == 1 and not (c1 - c2) and not (c1 - c3):
    eol = '\r\n' if b2[:400].find(b'\r\n') >= 0 else '\n'
    merged = b2
    if not merged.endswith(b'\n'): merged += eol.encode()
    merged += (only3[0] + eol).encode()
    write_bytes(p, merged)
    ev['resolved'][p] = {'action': 'union-append', 'base': len(L1), 's2': len(L2), 's3': len(L3), 'final': len(L2) + 1}
else:
    ev['failed'][p] = f'CODELY union guard FAIL: only2={len(only2)} only3={len(only3)}'

# ---- verify: no conflict markers remain anywhere ----
import re
marker_files = []
for p_ in list(ev['resolved']) :
    try:
        t = open(p_, 'rb').read()
        if b'<<<<<<<' in t or b'>>>>>>>' in t or b'|||||||' in t:
            marker_files.append(p_)
    except Exception:
        pass
ev['marker_check_clean'] = not marker_files
ev['marker_files'] = marker_files

json.dump(ev, open('results/_r305bmc_resolve_evidence.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(ev, ensure_ascii=False, indent=1))
