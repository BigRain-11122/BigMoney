# -*- coding: utf-8 -*-
# r852 probe4: EOL flip point in git history + LF-face anchor counts
import subprocess

def show(ref):
    r = subprocess.run(['git', 'show', ref], capture_output=True)
    return r.stdout.decode('utf-8', errors='replace')

# recent commits touching n1
r = subprocess.run(['git', 'log', 'origin/main', '--oneline', '-n', '8',
                    '--', 'scripts/perpetual_faces_n1.py'], capture_output=True, text=True, encoding='utf-8')
lines = [l.split(' ', 1) for l in r.stdout.strip().splitlines()]
print('recent n1 commits:')
for sha, msg in lines:
    blob = show(f'{sha}:scripts/perpetual_faces_n1.py')
    crlf = blob.count('\r\n'); lf = blob.count('\n') - crlf
    print(' ', sha[:10], '| CRLF:', crlf, '| LF:', lf, '|', msg[:70])

n1 = open('scripts/perpetual_faces_n1.py', 'rb').read().decode('utf-8')
pf = open('scripts/perpetual_faces.py', 'rb').read().decode('utf-8')
LF = '\n'
print()
print('LF-face anchor counts:')
print('n1 cfg_close:', n1.count('                       }' + LF + 'PREREG = WAVE_CONFIGS[2]["prereg"]'))
print('n1 t141:', n1.count('    # --- T-141 s2 lane face'))
print('n1 print_t141:', n1.count('          "+ T-141 s2 '))
print('pf W205-owner close:', pf.count('         "engine_owner": "bm-a"},' + LF + '}' + LF + '# v1 + ext(wave-1) in-use bands'))
print('n1 PRE_first:', n1.count('"pre-run; design = frozen v1 null calibration verbatim, "'))
print('n1 205-cfg key:', n1.count('"prereg": ("research/PERPETUAL_N1_W205_PREREG.md'))
print('n1 205 a_seed line:', n1.count('"a_seed_base": 465_804'))
print('n1 205 batch line:', n1.count('205: {"batch": "PERPETUAL-N1-W205"'))
