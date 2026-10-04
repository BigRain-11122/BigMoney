import json
raw = open('results/theme_ring/theme_events_v03_algorithmic.json', 'rb').read()
d = json.loads(raw.decode('utf-8', errors='replace'))
eps = d['episodes']

# market-wide confound: breadth_at_20 == 1.0 episodes (all 14 famous proxies up)
broad1 = [e for e in eps if e['breadth_at_20'] == 1.0]
print('episodes with breadth==1.0 (market-wide confound):', len(broad1))
from collections import Counter
print('their year dist:', dict(sorted(Counter(e['ignition_date'][:4] for e in broad1).items())))
print('their ignition-day dist (top):', dict(Counter(e['ignition_date'] for e in broad1).most_common(8)))
sub1 = [e for e in eps if e['breadth_at_20'] is not None and e['breadth_at_20'] < 1.0]
print('episodes with breadth<1.0:', len(sub1))
fam_sub = [e for e in sub1 if e['famous16_proxy']]
rest_sub = [e for e in sub1 if not e['famous16_proxy']]
def med(v):
    v = sorted(x for x in v if x is not None)
    return round(v[len(v)//2], 4) if v else None
print('breadth<1 famous median ret:', med([e['ret_ign_to_peak'] for e in fam_sub]), 'n=', len(fam_sub))
print('breadth<1 rest   median ret:', med([e['ret_ign_to_peak'] for e in rest_sub]), 'n=', len(rest_sub))

# names for top rows from CSV
import csv as _csv
with open('results/theme_ring/theme_events_v03_algorithmic.csv', encoding='utf-8') as f:
    rd = list(_csv.DictReader(f))
for r in rd[:0]:
    pass
top_codes = ['sh513310', 'sh562590', 'sh588890', 'sh588290', 'sh588200', 'sz159558', 'sh516300']
seen = set()
for r in rd:
    if r['code'] in top_codes and r['code'] not in seen:
        seen.add(r['code'])
        print(r['code'], '|', r['name'][:20], '|', r['ignition_date'], '| ret', r['ret_ign_to_peak'])
    if len(seen) == len(top_codes):
        break
