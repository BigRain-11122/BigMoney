# R330 bm-a push-collision resolver (18-UU batch, vs bm-b r330 same-window S6+5x double-commit)
# Recipes per bigmoney-conflict-resolve SKILL.md canon:
#  - HANDOVER.md: anchor-insert (R210) -- origin first-comer keeps 最近核对 slot, latecomer entry
#    inserted before the previous-check anchor; tail rows union both (append-ledger-md, R208).
#    EOL: origin side normalized whole file to LF -> final written uniform LF.
#  - autofill_state.json: mixed-dict+ledger (r203/R208/r215/r220/r245/r322/r83) --
#    launches composite-key union dedup-first (field-set additive merge), ts asc re-sort, cap 50
#    newest; last_tick whole-dict by inner ts (tie->HEAD=origin); EOL/indent mirror BASE blob (:1:).
#  - compute_audit.json / regime_state.json: rolling-ledger -- history union by key, latest/state
#    take-new by deep-ts probe (D-09); EOL mirror BASE.
#  - x2_watch_log.jsonl: append-log line union zero-loss (r188).
#  - snapshot + 6 UNKNOWN faces: manual adjudication = per-round regenerated measurement faces
#    (R322 "25 measurement faces" family) -> take-new by deep-ts probe; all MINE newer (15:00 vs
#    14:54); EOL mirror BASE.
# During rebase: :2 = origin (bm-b), :3 = this commit (bm-a). HEAD = origin.
import subprocess, json, io, sys

def blob(rev, path):
    r = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def eol_of(b):
    if b is None:
        return '\n'
    i = b.find(b'\n')
    if i > 0 and b[i-1:i] == b'\r':
        return '\r\n'
    return '\n'

def indent_of(b):
    if b is None:
        return 1
    for line in b.split(b'\n'):
        s = line.decode('utf-8', errors='replace')
        if s.startswith(' ') and len(s.strip()) > 0:
            return len(s) - len(s.lstrip(' '))
    return 1

def trailing_nl(b):
    return b is not None and b.endswith(b'\n')

def write_json(path, obj, base_b):
    eol = eol_of(base_b)
    ind = indent_of(base_b)
    txt = json.dumps(obj, ensure_ascii=False, indent=ind)
    if trailing_nl(base_b):
        txt += '\n'
    data = txt.replace('\n', eol) if eol == '\r\n' else txt
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(data)
    json.loads(io.open(path, encoding='utf-8-sig').read())  # parse-verify (r185)

def deep_ts(d, keys):
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return None
    return d

report = {}

# ---------------------------------------------------------------- 1. HANDOVER.md
path = 'research/HANDOVER.md'
raw = io.open(path, encoding='utf-8', errors='replace', newline='').read()
if '<<<<<<<' not in raw:
    # idempotent re-entry: first resolver run already landed this block before
    # crashing on the ':N:' stage-syntax bug in autofill; verify + skip
    assert '最近核对=bm-b round 330' in raw and '上一次最近核对=bm-a round 330' in raw
    assert raw.count('round 330 bm-a（5x 核对本轮）') == 1 and raw.count('round 330 bm-b（5x 核对本轮）') == 1
    report['HANDOVER'] = 'anchor-insert ok (landed by first pass, verified on re-entry): their entry keeps slot, my entry before bm-b-325 anchor, tail rows union, LF uniform'
else:
    lines = raw.split('\n')
    assert lines[0].startswith('<<<<<<<') and lines[236].startswith('======='), 'marker layout'
    their = [l[:-1] if l.endswith('\r') else l for l in lines[1:236]]
    mine = [l[:-1] if l.endswith('\r') else l for l in lines[237:472]]
    PREFIX = '> 本文件由循环每 5 轮核对更新一次（mandate 已写明）。最近核对='
    SEP = '；上一次最近核对='
    th, my = their[3], mine[3]
    assert th.startswith(PREFIX) and my.startswith(PREFIX), 'header prefix'
    i_th, i_my = th.find(SEP), my.find(SEP)
    assert i_th > 0 and i_my > 0, 'sep present'
    their_entry, my_entry = th[len(PREFIX):i_th], my[len(PREFIX):i_my]
    rest_th, rest_my = th[i_th + len(SEP):], my[i_my + len(SEP):]
    assert rest_th == rest_my, 'demoted chains diverge -- manual adjudication required'
    assert rest_th.startswith('bm-b round 325'), 'rest chain head'
    final_header = PREFIX + their_entry + SEP + my_entry + SEP + rest_th
    # body: identical outside header; tail rows union (theirs 14:5x then mine 15:1x)
    body_ident = sum(1 for a, b in zip(their[:3] + their[4:234], mine[:3] + mine[4:234]) if a != b)
    assert body_ident == 0, 'unexpected body divergence'
    out = their[:3] + [final_header] + their[4:235] + [mine[234]]
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write('\n'.join(out) + '\n')
    chk = io.open(path, encoding='utf-8', newline='').read()
    assert '最近核对=bm-b round 330' in chk and chk.count('round 330 bm-a（5x 核对本轮）') == 1
    assert '上一次最近核对=bm-a round 330' in chk
    report['HANDOVER'] = f'anchor-insert ok: their_entry {len(their_entry)}B + my_entry {len(my_entry)}B before bm-b-325 anchor; tail rows union (bm-b r330 + bm-a R330); LF uniform'

# ---------------------------------------------------------------- 2. autofill_state.json
path = 'results/autofill_state.json'
b_base, b_or, b_mine = blob(':1', path), blob(':2', path), blob(':3', path)
d_or, d_mine = json.loads(b_or.decode('utf-8-sig')), json.loads(b_mine.decode('utf-8-sig'))
CK = ('ts', 'machine', 'pid', 'runner_sha256', 'entry', 'shard')
un = {}
collisions = 0
for e in d_or['launches'] + d_mine['launches']:
    k = tuple(e.get(c) for c in CK)
    if k in un:
        collisions += 1
        a = un[k]
        common_divergent = any(
            key in a and key in e and a[key] != e[key] for key in a if key != 'owner_since')
        if common_divergent:
            print('FATAL: true divergence on composite key', k)
            sys.exit(2)
        merged = dict(a)
        merged.update({kk: vv for kk, vv in e.items() if kk not in merged})
        merged.update({kk: vv for kk, vv in a.items()})
        un[k] = merged  # field-union, additive only (r322)
    else:
        un[k] = e
launches = sorted(un.values(), key=lambda x: str(x.get('ts', '')))
if len(launches) > 50:
    launches = launches[-50:]
launches = sorted(launches, key=lambda x: str(x.get('ts', '')))  # asc write-back (r245)
lt_or, lt_mine = d_or['last_tick'], d_mine['last_tick']
ts_or, ts_mine = str(lt_or.get('ts', '')), str(lt_mine.get('ts', ''))
last_tick = lt_or if ts_or >= ts_mine else lt_mine  # tie -> HEAD(origin) r140
assert isinstance(last_tick, dict)
res = {'launches': launches, 'last_tick': last_tick}
write_json(path, res, b_base)
report['autofill_state'] = f"union {len(d_or['launches'])}|{len(d_mine['launches'])} -> {len(launches)} (collisions {collisions} field-union-merged), last_tick {'origin' if last_tick is lt_or else 'mine'} {ts_or if last_tick is lt_or else ts_mine}, EOL mirror base"

# ---------------------------------------------------------------- 3. compute_audit.json
path = 'results/compute_audit.json'
b_base, b_or, b_mine = blob(':1', path), blob(':2', path), blob(':3', path)
d_or, d_mine = json.loads(b_or.decode('utf-8-sig')), json.loads(b_mine.decode('utf-8-sig'))
h = {}
for e in d_or['history'] + d_mine['history']:
    k = (str(e.get('ts', '')), str(e.get('machine', '')))
    if k in h:
        if h[k] != e:
            print('FATAL: compute_audit history key collision with divergent content', k)
            sys.exit(2)
    else:
        h[k] = e
history = sorted(h.values(), key=lambda x: str(x.get('ts', '')))
latest = d_mine['latest'] if str(d_mine['latest'].get('ts', '')) >= str(d_or['latest'].get('ts', '')) else d_or['latest']
write_json(path, {'latest': latest, 'history': history}, b_base)
report['compute_audit'] = f"history union {len(d_or['history'])}|{len(d_mine['history'])} -> {len(history)} (keyset collisions content-identical-verified), latest {'mine' if latest is d_mine['latest'] else 'origin'}"

# ---------------------------------------------------------------- 4. regime_state.json
path = 'results/regime_state.json'
b_base, b_or, b_mine = blob(':1', path), blob(':2', path), blob(':3', path)
d_or, d_mine = json.loads(b_or.decode('utf-8-sig')), json.loads(b_mine.decode('utf-8-sig'))
res = dict(d_mine if str(d_mine.get('updated', '')) >= str(d_or.get('updated', '')) else d_or)
hist = {}
for e in d_or.get('history', []) + d_mine.get('history', []):
    k = str(e.get('asof', e.get('ts', '')))
    hist.setdefault(k, e)
res['history'] = sorted(hist.values(), key=lambda x: str(x.get('asof', x.get('ts', ''))))
tr = {}
for e in d_or.get('transitions', []) + d_mine.get('transitions', []):
    tr[str(e)] = e
res['transitions'] = list(tr.values())
write_json(path, res, b_base)
report['regime_state'] = f"state take-new, history union -> {len(res['history'])}, transitions union -> {len(res['transitions'])}"

# ---------------------------------------------------------------- 5. x2_watch_log.jsonl
path = 'results/x2_watch_log.jsonl'
b_or, b_mine = blob(':2', path), blob(':3', path)
lo, lm = b_or.decode('utf-8-sig').splitlines(), b_mine.decode('utf-8-sig').splitlines()
seen, out = set(), []
for l in lo + lm:
    if l and l not in seen:
        seen.add(l)
        out.append(l)
with io.open(path, 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(out) + '\n')
report['x2_watch_log'] = f'line union {len(lo)}|{len(lm)} -> {len(out)}'

# ------------------------------------------------- 6. snapshots + UNKNOWN faces
SNAP = {
    'results/dashboard_status.json': ('meta', 'generated_at'),
    'results/fundamental_b_layer_filter.json': ('updated',),
    'results/futures_update_status.json': ('ts',),
    'results/heat_update_status.json': ('updated',),
    'results/lhb_update_status.json': ('updated',),
    'results/token_usage.json': ('generated',),
    'results/update_status.json': ('updated',),
    'results/daily_scorecard.json': ('traders', 'forward_guard', 'as_of'),  # deep probe: [0] handled in ts_of
    'results/prospect_paper/_summary.json': ('generated',),
    'results/prospect_promotion/_summary.json': ('generated',),
    'results/scorecard_v1.json': ('generated',),
    'results/strategy_scorecard.json': ('generated',),
    'results/t35_open_fill_verify.json': ('ts',),
}
for path, probe in SNAP.items():
    b_base, b_or, b_mine = blob(':1', path), blob(':2', path), blob(':3', path)
    d_or, d_mine = json.loads(b_or.decode('utf-8-sig')), json.loads(b_mine.decode('utf-8-sig'))
    def ts_of(d):
        cur = d
        for k in probe:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            elif isinstance(cur, list) and cur:
                cur = cur[0].get(k) if isinstance(cur[0], dict) else None
            else:
                return None
        return str(cur) if cur is not None else None
    t_or, t_mine = ts_of(d_or), ts_of(d_mine)
    assert t_or and t_mine, f'{path}: ts probe failed'
    winner = d_mine if t_mine >= t_or else d_or
    write_json(path, winner, b_base if b_base is not None else b_or)
    report[path] = f"take-{'mine' if winner is d_mine else 'origin'} ({t_mine if winner is d_mine else t_or} >= {t_or if winner is d_mine else t_mine})"

print(json.dumps(report, ensure_ascii=False, indent=1))
print('ALL RESOLVED')
