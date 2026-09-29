import json

d = json.load(open('results/innovation_quota/ICU-MA-TIMING-P1.json', encoding='utf-8'))
out = []
for name in ('ICU-N5', 'ICU-N120', 'ICU-N15'):
    c = d['cells'][name]
    out.append(name + ' cell keys: ' + ', '.join(sorted(c.keys())))
for name in ('ICU-N5', 'ICU-N120', 'ICU-N15'):
    c = d['cells'][name]
    keep = {k: c[k] for k in c if any(t in k.lower() for t in
            ('maxdd', 'max_dd', 'dsr', 'g2', 'ann', 'turnover', 'rounds', 'flip', 'raw_side', 'transition'))}
    out.append(name + ': ' + json.dumps(keep, ensure_ascii=False)[:600])
out.append('d6 keys: ' + ', '.join(d['d6'].keys()))
out.append('d6 cell faces: ' + json.dumps({k: v for k, v in d['d6'].items() if k not in ('members', 'near_neighbor_warning', 'reject_line')}, ensure_ascii=False)[:700])
out.append('gates ICU-N120 keys: ' + ', '.join(d['gates']['ICU-N120'].keys()))
g2 = {n: d['gates'][n].get('g2_registration_v2', d['gates'][n].get('g2')) for n in ('ICU-N5', 'ICU-N120', 'ICU-N15')}
out.append('g2 faces: ' + json.dumps(g2, ensure_ascii=False)[:500])
out.append('extreme cells full: ' + json.dumps(d['extreme_day_face']['cells'], ensure_ascii=False))
out.append('legs_face: ' + json.dumps(d['legs_face'], ensure_ascii=False)[:600])
out.append('warmup_law: ' + json.dumps(d['warmup_law'], ensure_ascii=False)[:300])
out.append('anchor_faces: ' + json.dumps(d['anchor_faces'], ensure_ascii=False)[:400])
open('results/_r250bmc_w5_faces.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written', len(out), 'lines')
