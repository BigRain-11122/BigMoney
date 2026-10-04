import json
import pandas as pd
from collections import Counter

raw = open('results/theme_ring/theme_events_v03_algorithmic.json', 'rb').read()
d = json.loads(raw.decode('utf-8', errors='replace'))
eps = d['episodes']
print('n_episodes:', len(eps))

cls = Counter(e['persistence_class'] for e in eps)
print('class dist:', dict(cls))

years = Counter(e['ignition_date'][:4] for e in eps)
print('ignition year dist:', dict(sorted(years.items())))

nw = Counter(e['n_waves'] for e in eps)
print('n_waves dist (top):', dict(sorted(nw.items())[:8]))

fam = [e for e in eps if e['famous16_proxy']]
print('\nfamous14 episodes by code:')
byc = Counter(e['code'] for e in fam)
print(dict(byc))

print('\nanchor matches detail:')
for m in d['ceo_anchor_matches']:
    tag = 'HIT' if m['detected_within_pm30td'] else 'miss'
    near = m['nearest_detected']
    print(f"  [{tag}] {m['id']} anchor={m['ceo_anchor']} nearest={near['detected_date']} abs_delta={near['abs_delta_days']}d" if near else f"  [{tag}] {m['id']} anchor={m['ceo_anchor']} no episodes on proxy")

# HIT detail: which episodes matched within +-30td
for m in d['ceo_anchor_matches']:
    if m['detected_within_pm30td']:
        code = m['proxy']
        near = [e for e in eps if e['code'] == code
                and abs((pd.Timestamp(e['ignition_date']) - pd.Timestamp(m['ceo_anchor'])).days) <= 30]
        for e in near:
            print(f"  HIT-detail: {m['id']} <- {e['code']} {e['ignition_date']} ret={e['ret_ign_to_peak']} dur={e['dur_to_peak_td']}")

# top-10 by ret_ign_to_peak (eyeball sanity, names)
top = sorted(eps, key=lambda e: -(e['ret_ign_to_peak'] or 0))[:10]
print('\ntop-10 ret_ign_to_peak:')
for e in top:
    print(f"  {e['code']} {e['name'][:14]:14s} {e['ignition_date']} ret={e['ret_ign_to_peak']:.2f} dur={e['dur_to_peak_td']} cls={e['persistence_class']}")

# window truncation disclosure
short_win = [e for e in eps if e['window_bars'] < 751]
print('\nepisodes with truncated window (<751 bars):', len(short_win), '/', len(eps))

# index_tracker tag coverage
tagged = Counter(str(e['index_tracker_tag']) for e in eps)
print('index_tracker_tag dist:', dict(tagged))
