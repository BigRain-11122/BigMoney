# r447 bm-b rebase wedge resolver (21 UU files, same-window multi-machine S6 collision)
# Law: bigmoney-conflict-resolve SKILL.md -- classify first (classifier exit 2 = manual per-file
# adjudication done below via embedded ts comparison, per R208/R216 take-new / r188 union).
# ours(:2) = origin/main post bm-c r254 e87cb4f3b; theirs(:3) = bm-b round 447 commit.
# Raw-bytes take-side for snapshots (preserve producer format); union for rolling ledgers.
import subprocess, json, sys, io

def blob(p, n):
    r = subprocess.run(['git', 'show', f':{n}:{p}'], capture_output=True)
    if r.returncode != 0:
        sys.exit(f'FATAL blob read fail {p} stage {n}: {r.stderr.decode(errors="replace")}')
    return r.stdout

TS_KEYS = ['generated_at', 'generated', 'ts', 'updated_at', 'updated', 'written_at']

def ts_of(d):
    for k in TS_KEYS:
        if isinstance(d, dict) and k in d:
            return str(d[k])
    if isinstance(d, dict) and isinstance(d.get('meta'), dict) and 'generated_at' in d['meta']:
        return str(d['meta']['generated_at'])
    return None

def parse(b):
    return json.loads(b.decode('utf-8'))

VERDICTS = {}

def take_new(path):
    a, c = parse(blob(path, 2)), parse(blob(path, 3))
    ta, tc = ts_of(a), ts_of(c)
    if ta is None or tc is None:
        sys.exit(f'FATAL no ts face {path}: ours={ta} theirs={tc}')
    win = 3 if tc > ta else 2
    VERDICTS[path] = ('take-new', 'theirs' if win == 3 else 'ours', ta, tc)
    with open(path, 'wb') as f:
        f.write(blob(path, win))

def take_side_raw(path, side):
    VERDICTS[path] = ('take-side', side, '-', '-')
    with open(path, 'wb') as f:
        f.write(blob(path, 3 if side == 'theirs' else 2))

# --- snapshots: take-new by embedded ts ---
for p in [
    'results/_attrition_guard_scan.json',
    'results/token_usage.json',
    'results/prospect_promotion/_summary.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/update_status.json',
    'docs/daily_report/REPORT-2026-09-30.json',
    'docs/live_usage/LIVE-2026-09-30.json',
    'docs/live_usage/LIVE-latest.json',
]:
    take_new(p)

# --- md twins + js wrapper: same side as their json twin ---
for md, twin in [
    ('docs/daily_report/REPORT-2026-09-30.md', 'docs/daily_report/REPORT-2026-09-30.json'),
    ('docs/live_usage/LIVE-2026-09-30.md', 'docs/live_usage/LIVE-2026-09-30.json'),
    ('docs/live_usage/LIVE-latest.md', 'docs/live_usage/LIVE-latest.json'),
    ('results/dashboard_status.js', 'results/dashboard_status.json'),
]:
    take_side_raw(md, VERDICTS[twin][1])

# --- origin-newer faces (bm-c 05:49 bar-family vs bm-b dead-session 05:44) ---
for p in ['results/prospect_paper/_summary.json', 'results/t35_open_fill_verify.json']:
    take_new(p)

# --- rolling ledger: compute_audit.json -- history union + latest take-new ---
p = 'results/compute_audit.json'
a, c = parse(blob(p, 2)), parse(blob(p, 3))
seen, merged = set(), []
for row in list(a['history']) + list(c['history']):
    k = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if k not in seen:
        seen.add(k)
        merged.append(row)
def hts(r):
    return r.get('ts') or r.get('generated') or ''
merged.sort(key=lambda r: hts(r))
la, lc = a['latest'], c['latest']
latest = lc if ts_of(lc) > ts_of(la) else la
res = {'latest': latest, 'history': merged}
out = json.dumps(res, ensure_ascii=False, indent=2) + '\n'
with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(out)
VERDICTS[p] = ('union-history', f'rows {len(a["history"])}+{len(c["history"])}->{len(merged)}', ts_of(la), ts_of(lc))

# --- rolling ledger: regime_state.json -- transitions/history union + state take-new ---
p = 'results/regime_state.json'
a, c = parse(blob(p, 2)), parse(blob(p, 3))
base = c if ts_of(c) > ts_of(a) else a  # newest whole state face
other = a if base is c else c
for key in ('transitions', 'history'):
    seen = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in base.get(key, [])}
    extra = [r for r in other.get(key, []) if json.dumps(r, sort_keys=True, ensure_ascii=False) not in seen]
    if extra:
        base[key] = sorted(base.get(key, []) + extra, key=lambda r: str(r.get('ts') or r.get('asof') or r.get('date') or ''))
out = json.dumps(base, ensure_ascii=False, indent=2)
with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(out)
VERDICTS[p] = ('union-ledger+take-new', f'transitions {len(base.get("transitions", []))} history {len(base.get("history", []))}', ts_of(a), ts_of(c))

# --- verify before add (r185 law) ---
for path in VERDICTS:
    raw = open(path, 'rb').read()
    if path.endswith('.json'):
        parse(raw)
    elif path.endswith('.js'):
        assert b'window.' in raw[:200], f'js wrapper lost: {path}'
    else:
        assert b'<<<<<<<' not in raw and b'>>>>>>>' not in raw, f'md markers: {path}'
subprocess.run(['git', 'add'] + list(VERDICTS.keys()), check=True)
for path, v in VERDICTS.items():
    print(f'{path}: {v[0]} winner={v[1]} ours_ts={v[2]} theirs_ts={v[3]}')
print(f'RESOLVED {len(VERDICTS)} files, all verified, staged')
