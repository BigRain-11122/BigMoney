# r1074bm-a S0 UU resolver: results/watermark_red.json newer-wins (r1028 family)
import re, sys, json
P = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\watermark_red.json'
raw = open(P, encoding='utf-8').read()
m = re.search(r'<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>> ', raw, re.S)
if not m:
    print('NO_CONFLICT_BLOCK'); sys.exit(0)
ours, theirs = m.group(1), m.group(2)
def ts_of(side):
    hits = re.findall(r'"(?:ts|probe_ts|asof|updated)"\s*:\s*"([^"]+)"', side)
    return hits[0] if hits else ''
o_t, t_t = ts_of(ours), ts_of(theirs)
print('OURS_TS:', o_t, '| THEIRS_TS:', t_t)
# newer-wins; tie or missing -> take ours (local fresh derive, r1072 take-stash precedent)
winner = 'ours' if o_t >= t_t else 'theirs'
print('WINNER:', winner)
resolved = ours if winner == 'ours' else theirs
new_raw = raw[:m.start()] + resolved + raw[m.end():]
# strip any residual conflict markers elsewhere (must be zero for this file)
assert '<<<<<<<' not in new_raw and '>>>>>>>' not in new_raw and '=======' not in new_raw, 'RESIDUAL_MARKERS'
json.loads(new_raw)  # validate whole file is legal JSON
open(P, 'w', encoding='utf-8', newline='').write(new_raw)
print('RESOLVED_OK bytes:', len(new_raw))
