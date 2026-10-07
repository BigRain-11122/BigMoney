# r840 bm-a rebase UU resolver -- 18-face S6 regen set, r773 per-face ts empirical law
# Policy per face family:
#   ts-simple (freshest wins, ours newer verified 20:03-05 vs 19:56-58):
#     docs/daily_report/REPORT-*.{json,md}, docs/live_usage/LIVE-*.{json,md},
#     results/{_attrition_guard_scan,fundamental_b_layer_filter,futures_update_status,
#              lhb_update_status,scorecard_v1,strategy_scorecard,update_status}.json
#   host-ownership (r378 single-writer guard host=bm-a -> ours):
#     results/dashboard_status.{json,js}
#   union/dual faces:
#     results/compute_audit.json   -> history ts-key union, latest=newer (r773)
#     results/regime_state.json    -> base=newer, history asof-union (r773)
#     results/token_usage.json     -> append ledger -> union by round key
import json, subprocess, sys, io

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f'git show :{stage}:{path} rc={r.returncode}: {r.stderr[:200]}')
    return r.stdout.decode('utf-8', errors='replace')

def jblob(stage, path):
    return json.loads(blob(stage, path))

TS_KEYS = ('generated', 'ts', 'updated', 'asof')

def face_ts(d):
    for k in TS_KEYS:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return ''

SIMPLE = [
    'docs/daily_report/REPORT-2026-10-07.json',
    'docs/daily_report/REPORT-2026-10-07.md',
    'docs/live_usage/LIVE-2026-10-07.json',
    'docs/live_usage/LIVE-2026-10-07.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/update_status.json',
]
HOST_OURS = ['results/dashboard_status.json', 'results/dashboard_status.js']

verdicts = {}

for p in SIMPLE:
    o, t = blob(2, p), blob(3, p)
    try:
        oj, tj = json.loads(o), json.loads(t)
        ov, tv = face_ts(oj), face_ts(tj)
    except json.JSONDecodeError:
        ov, tv = '', ''
    if ov and tv:
        win = 'ours' if ov >= tv else 'theirs'
    else:
        win = 'ours'  # unverifiable ts -> ours side of this rebase (our commit being replayed)
    data = o if win == 'ours' else t
    verdicts[p] = f'{win} (ours={ov!r} theirs={tv!r})'
    with open(p, 'w', encoding='utf-8', newline='') as fh:
        fh.write(data)

for p in HOST_OURS:
    o, t = blob(2, p), blob(3, p)
    verdicts[p] = f'ours-host (r378 host=bm-a; ts ours={face_ts(json.loads(o)) if p.endswith("json") else "js"} theirs={face_ts(json.loads(t)) if p.endswith("json") else "js"})'
    with open(p, 'w', encoding='utf-8', newline='') as fh:
        fh.write(o)

# compute_audit.json -- latest=newer, history ts-key union zero-loss
p = 'results/compute_audit.json'
o, t = jblob(2, p), jblob(3, p)
ov, tv = face_ts(o.get('latest', o)), face_ts(t.get('latest', t))
base = o if ov >= tv else t
oh = o.get('history', []); th = t.get('history', [])
seen = {}
for e in oh + th:
    k = e.get('ts') or e.get('generated')
    if k not in seen or str(k) >= str(seen[k].get('ts') or ''):
        seen[k] = e
merged_hist = sorted(seen.values(), key=lambda e: str(e.get('ts') or ''))
if isinstance(base, dict) and 'history' in base:
    base['history'] = merged_hist
verdicts[p] = f'base={"ours" if ov>=tv else "theirs"}({ov} vs {tv}); history union {len(oh)}+{len(th)}->{len(merged_hist)} (dup-key newer-wins)'
with open(p, 'w', encoding='utf-8', newline='') as fh:
    json.dump(base, fh, ensure_ascii=False, indent=2)

# regime_state.json -- base=newer, history asof-union
p = 'results/regime_state.json'
o, t = jblob(2, p), jblob(3, p)
ov, tv = face_ts(o), face_ts(t)
base = o if ov >= tv else t
oh = o.get('history', []); th = t.get('history', [])
seen = {}
for e in oh + th:
    k = e.get('asof') or e.get('ts')
    if k not in seen:
        seen[k] = e
merged = sorted(seen.values(), key=lambda e: str(e.get('asof') or e.get('ts') or ''))
if 'history' in base:
    base['history'] = merged
verdicts[p] = f'base={"ours" if ov>=tv else "theirs"}({ov} vs {tv}); history asof-union {len(oh)}+{len(th)}->{len(merged)} (first-seen per asof)'
with open(p, 'w', encoding='utf-8', newline='') as fh:
    json.dump(base, fh, ensure_ascii=False, indent=2)

# token_usage.json -- append ledger union by round key
p = 'results/token_usage.json'
o, t = jblob(2, p), jblob(3, p)
print('token_usage OURS keys:', list(o.keys()))
print('token_usage THEIRS keys:', list(t.keys()))
for k, v in o.items():
    if isinstance(v, list):
        print(f'  ours list {k}: n={len(v)} sample0={str(v[0])[:140] if v else ""}')
    else:
        print(f'  ours {k}: {str(v)[:80]}')
for k, v in t.items():
    if isinstance(v, list):
        print(f'  theirs list {k}: n={len(v)} sample0={str(v[0])[:140] if v else ""}')
verdicts[p] = 'INSPECT-FIRST (printed structure; union pending)'

for k, v in verdicts.items():
    print(f'{k}: {v}')
print('RESOLVED-SO-FAR ok')
