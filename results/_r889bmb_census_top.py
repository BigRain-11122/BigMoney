import json

d = json.load(open('results/alphagen_rg/CENSUS-2026-10-09.json', encoding='utf-8'))
fs = d['census']['formulas']
top = sorted(fs, key=lambda f: -abs(f['h1']['ic_ir']))[:8]
for f in top:
    h = f['h1']
    print("idx=%3d depth=%d absICIR=%.4f ic_mean=%+.4f pos=%.3f n=%d formula=%s" % (
        f['idx'], f['depth'], abs(h['ic_ir']), h['ic_mean'], h['ic_pos_pct'], h['n_periods'], f['formula']))
print('---verdict:', json.dumps(d.get('verdict', {}), ensure_ascii=False)[:500])
print('---descriptive:', json.dumps(d.get('descriptive', {}), ensure_ascii=False)[:400])
