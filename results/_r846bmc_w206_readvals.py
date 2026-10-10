# -*- coding: utf-8 -*-
# r846 bm-c: read n1_w206_results.json exact values for §7 backfill + §5 four pre-keys check
import io, json, re
d = json.load(io.open('results/perpetual_faces/n1_w206_results.json', encoding='utf-8'))
out = {}
out['top_keys'] = list(d.keys())
sg = d.get('science_gates') or {}
out['ledger'] = sg.get('ledger') or d.get('trials_ledger')
for k in ('merged', 'w_only', 'wave_only', 'pool', 'skill_line', 'skill_line_v2', 'audit', 'bands', 'stats', 'summary'):
    if k in d:
        v = d[k]
        out[k] = v if not isinstance(v, dict) else {kk: v[kk] for kk in list(v)[:24]}
io.open('results/_r846bmc_w206_results_dump.txt', 'w', encoding='utf-8').write(
    json.dumps(out, ensure_ascii=False, indent=1, default=str))
print('written; top keys:', out['top_keys'][:20])
print('ledger:', out['ledger'])
# prereg §5 four pre-keys text
t = io.open('research/PERPETUAL_N1_W206_PREREG.md', encoding='utf-8').read()
heads = [(m.start(), m.group(0)) for m in re.finditer(r'^## .+$', t, re.M)]
sec5 = ''
for i, (pos, h) in enumerate(heads):
    if '5' in h and ('预' in h or '键' in h):
        end = heads[i + 1][0] if i + 1 < len(heads) else len(t)
        sec5 = t[pos:end]
        break
io.open('results/_r846bmc_w206_sec5_extract.txt', 'w', encoding='utf-8').write(sec5)
print('sec5 bytes:', len(sec5))
