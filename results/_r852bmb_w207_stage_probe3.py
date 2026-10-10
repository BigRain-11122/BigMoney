# -*- coding: utf-8 -*-
# r852 probe3: byte-face (rb) block map around the 204-row-leg + EOL census
import re

raw = open('scripts/perpetual_faces_n1.py', 'rb').read()
t = raw.decode('utf-8')
CRLF = '\r\n'

print('CRLF count:', t.count(CRLF), '| bare LF count:', t.count('\n') - t.count(CRLF))

# block header map (last 6 blocks)
hdrs = [(m.start(), m.group(0)) for m in re.finditer(r'    # --- W\d+ materializer face', t)]
print('total blocks:', len(hdrs))
for pos, h in hdrs[-4:]:
    print('block', h.strip(), 'at', pos)

m204 = t.find('        assert pf.N1_BANDS[204] == {')
print('204-leg at', m204, '| containing block:', [h.strip() for p, h in hdrs if p <= m204][-1])

# W205 block byte-face estate extraction (rb bytes, CRLF face)
i = t.rfind('    # --- W205 materializer face')
j = t.find('    # --- T-141 s2 lane face', i)
blk = t[i:j]
k = blk.find('        # registered row parity (r307 pinned constants, recent estate)')
leg204 = blk.find('        assert pf.N1_BANDS[204] == {')
estate = blk[k:leg204]
waves = re.findall(r'assert pf\.N1_BANDS\[(\d+)\]', estate)
print('W205 estate (byte face): asserts=', estate.count('assert pf.N1_BANDS['),
      'first/last=', (waves[0], waves[-1]), 'n_uniq=', len(set(waves)),
      'endswith CRLF=', estate.endswith(CRLF))
print('sorted estate == 138..187:', sorted(int(w) for w in waves) == list(range(138, 188)))
print('file order ascending:', [int(w) for w in waves] == sorted(int(w) for w in waves))

# which assert is immediately before the 204-leg (byte face)
print('bytes before 204-leg:', repr(blk[leg204-180:leg204]))

# cfg close anchor byte-face
print('cfg_close anchor count (byte):', t.count('                       }' + CRLF + 'PREREG = WAVE_CONFIGS[2]["prereg"]'))

pfr = open('scripts/perpetual_faces.py', 'rb').read().decode('utf-8')
print('pf CRLF count:', pfr.count(CRLF))
print('pf W205-owner close anchor count (byte):',
      pfr.count('         "engine_owner": "bm-a"},' + CRLF + '}' + CRLF + '# v1 + ext(wave-1) in-use bands'))
