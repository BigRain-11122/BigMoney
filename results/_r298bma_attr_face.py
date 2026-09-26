import io
raw = open('results/gate_attrition.json', 'rb').read()
print('BOM:', raw[:3] == b'\xef\xbb\xbf')
print('CRLF:', b'\r\n' in raw, '| LF-only:', raw.count(b'\n') != raw.count(b'\r\n'))
print('ends with newline:', raw[-1:] in (b'\n', b'\r'))
import json
d = json.loads(raw.decode('utf-8-sig'))
print('parses ok; entries n =', len(d['entries']))
# what does the most recent full-45-less row (CN_TREND_ETF_P1, 7 cells) look like key-wise?
r = [e for e in d['entries'] if e['batch'] == 'CN_TREND_ETF_P1'][0]
print('CN_TREND row keys:', list(r.keys()))
print('gates keys:', list((r.get('gates') or {}).keys()))
g = r['gates']
print('gates.g1_pass:', json.dumps(g.get('g1_pass'), ensure_ascii=False)[:200])
print('gates.family_pbo keys:', list((g.get('family_pbo') or {}).keys())[:12])
print('gates has d6_reject?', 'd6_reject' in g)
print(json.dumps(g.get('family_pbo'), ensure_ascii=False)[:300])
