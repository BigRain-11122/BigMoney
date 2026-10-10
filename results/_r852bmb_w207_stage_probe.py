# -*- coding: utf-8 -*-
# r852 bm-b staging probe: verify W207 splice anchors in current files + seat MSG location
import io, glob

n1 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
pf = io.open('scripts/perpetual_faces.py', encoding='utf-8').read()
CRLF = '\r\n'

anchors = [
    ('n1 cfg_close', '                       ' + CRLF + 'PREREG = WAVE_CONFIGS[2]["prereg"]'),
    ('n1 t141_marker', '    # --- T-141 s2 lane face'),
    ('n1 print_t141', '          "+ T-141 s2 '),
    ('n1 PRE_first', '"pre-run; design = frozen v1 null calibration verbatim, "'),
    ('n1 par_marker', '        # registered row parity (r307 pinned constants, recent estate)'),
    ('n1 W205 block hdr', '    # --- W205 materializer face'),
    ('n1 W204-row-leg start', '        assert pf.N1_BANDS[204] == {'),
    ('pf W205-owner close ctx', '         "engine_owner": "bm-a"},' + CRLF + '}' + CRLF + '# v1 + ext(wave-1) in-use bands'),
]
for name, needle in anchors:
    print(name, '->', n1.count(needle) if needle.startswith('    #') or 'WAVE' in needle or needle.startswith('        #') or needle.startswith('"') or needle.startswith('          ') else pf.count(needle))

# precise per-file checks
print('n1 cfg_close count:', n1.count(anchors[0][1]))
print('n1 t141 count:', n1.count(anchors[1][1]))
print('n1 print_t141 count:', n1.count(anchors[2][1]))
print('n1 PRE_first count:', n1.count(anchors[3][1]))
print('n1 par_marker count:', n1.count(anchors[4][1]))
print('n1 W205 block count:', n1.count(anchors[5][1]))
print('n1 W206 block count:', n1.count('    # --- W206 materializer face'))
print('n1 204-row-leg count:', n1.count(anchors[6][1]))
print('pf W205-owner-close count:', pf.count(anchors[7][1]))
print('pf W206-row present:', pf.count('206: {"a"'))
print('pf W205-row present:', pf.count('205: {"a"'))

# estate extraction dry-check from W205 block: marker -> first 204-row-leg line
i = n1.find(anchors[5][1])
j = n1.find('    # --- T-141 s2 lane face', i)
blk = n1[i:j]
k = blk.find(anchors[4][1])
leg204 = blk.find(anchors[6][1])
estate = blk[k:leg204]
import re
waves = re.findall(r'assert pf\.N1_BANDS\[(\d+)\]', estate)
print('W205-block estate: asserts=', estate.count('assert pf.N1_BANDS['), 'waves=', (waves[0], waves[-1]) if waves else None, 'n_uniq=', len(set(waves)), 'endswith_CRLF=', estate.endswith(CRLF))
print('estate wave set == 138..187:', sorted(set(int(w) for w in waves)) == list(range(138, 188)))

# seat MSG location
for f in glob.glob('fleet/inbox/*.md') + glob.glob('fleet/inbox/processed/*.md'):
    if 'w207' in f.lower():
        print('seat MSG:', f)
