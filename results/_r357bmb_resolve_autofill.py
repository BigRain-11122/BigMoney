"""r357 bm-b: resolve 1-UU autofill_state.json per r373 law (full-row union, zero-loss).

HEAD (stage2, origin/main) vs OURS (stage3, afbec4b1):
- launches: identity-less event rows -> union both sides, dedupe exact rows, keep order (HEAD rows first, then OURS-only rows)
- last_tick: NOT a same-second tie (ours 03:30:02 > head 03:20:01) -> newer wins (ours)
"""
import subprocess, json

def load(stage):
    raw = subprocess.run(['git', 'show', f':{stage}:results/autofill_state.json'],
                         capture_output=True).stdout.decode('utf-8')
    return json.loads(raw)

h = load(2)
o = load(3)

# union launches: dedupe by full-row canonical json (identity-less events, r373 law)
seen = set()
merged = []
for row in h.get('launches', []) + o.get('launches', []):
    key = json.dumps(row, ensure_ascii=False, sort_keys=True)
    if key not in seen:
        seen.add(key)
        merged.append(row)

lt_h, lt_o = h.get('last_tick'), o.get('last_tick')
ts_h = lt_h.get('ts') if isinstance(lt_h, dict) else ''
ts_o = lt_o.get('ts') if isinstance(lt_o, dict) else ''
if ts_h == ts_o:
    last_tick = lt_h  # same-second tie -> HEAD (r373 law)
    pick = 'HEAD(tie)'
else:
    last_tick = lt_o if ts_o > ts_h else lt_h  # newer ts wins
    pick = 'OURS' if ts_o > ts_h else 'HEAD'

out = {'last_tick': last_tick, 'launches': merged}
with open('results/autofill_state.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

# self-verify: reparses, counts, zero-loss assertion
reparsed = json.load(open('results/autofill_state.json', encoding='utf-8'))
n_h, n_o, n_m = len(h.get('launches', [])), len(o.get('launches', [])), len(reparsed['launches'])
assert n_m >= max(n_h, n_o), 'union must be superset of each side (zero-loss)'
print(f"resolve OK: launches {n_h} HEAD + {n_o} OURS -> {n_m} union (dup dropped {n_h+n_o-n_m})")
print(f"last_tick pick={pick}: {json.dumps(reparsed['last_tick'], ensure_ascii=False)[:160]}")
