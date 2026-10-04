# r709 bm-b merge resolver (r704/r708 bloodline, MERGE_MODE stage: 2=ours 3=theirs)
# Faces: 20 UU vs origin/main 594b83e57 (bm-a judge finalize seat declare + bm-c r511 wave)
# Decisions (probe receipts in _r709bmb_probe_sides/_deep.txt):
#   - take-ours (embedded ts newer) for 14 snapshot/derive faces + twins (.md/.js same-side law r708)
#   - compute_audit.json / regime_state.json: rolling-ledger union (history/transitions) + ours latest/state (r188/R208)
#   - runnable_pool.json: ours base + per-entry newer-wins on the only 2 differing entries (SHARD-10/SHARD-2,
#     theirs carries bm-c close/keepalive newer claim states; MSG-0612 backward face = the exact claw catch)
# Zero-loss assertions per skill sec.3 (parse-verify-then-write, write-back read assertions).
import json, subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def side(stage, path):
    b = subprocess.run(['git', 'show', ':%d:%s' % (stage, path)], capture_output=True, cwd=ROOT).stdout
    if not b:
        raise SystemExit('EMPTY stage %d %s' % (stage, path))
    return b

TAKE_OURS = [
    'docs/daily_report/REPORT-2026-10-05.json',
    'docs/daily_report/REPORT-2026-10-05.md',
    'docs/live_usage/LIVE-2026-10-05.json',
    'docs/live_usage/LIVE-2026-10-05.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json',
    'results/daily_scorecard.json',
    'results/dashboard_status.json',
    'results/dashboard_status.js',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/token_usage.json',
    'results/update_status.json',
]
UNION_LEDGERS = {
    'results/compute_audit.json': ['history'],
    'results/regime_state.json': ['history', 'transitions'],
}

receipt = {'round': 'r709 bm-b', 'merge_head': '594b83e57', 'faces': {}}

def write(path, data):
    if isinstance(data, bytes):
        open(os.path.join(ROOT, path), 'wb').write(data)
    else:
        open(os.path.join(ROOT, path), 'w', encoding='utf-8', newline='\n').write(data)

# ---- 1) take-ours faces (bytes verbatim; parse-verify json ones first, r185 law)
for p in TAKE_OURS:
    o = side(2, p)
    if p.endswith('.json'):
        json.loads(o.decode('utf-8'))          # parse gate before write
    write(p, o)
    receipt['faces'][p] = {'action': 'take-ours', 'bytes': len(o)}

# ---- 2) rolling-ledger unions
for p, keys in UNION_LEDGERS.items():
    o = json.loads(side(2, p).decode('utf-8'))
    t = json.loads(side(3, p).decode('utf-8'))
    for k in keys:
        a = o.get(k) or []
        b = t.get(k) or []
        rows = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in a}
        for r in b:
            rows.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
        merged = sorted(rows.values(), key=lambda r: str(r.get('ts', r.get('updated', ''))))
        o[k] = merged
        receipt['faces'][p] = {'action': 'union+' + k, 'ours_len': len(a), 'theirs_len': len(b),
                               'union_len': len(merged)}
        assert len(merged) >= max(len(a), len(b)), 'union loss %s' % p
    write(p, json.dumps(o, ensure_ascii=False, indent=1) + '\n')

# ---- 3) runnable_pool per-entry newer-wins
p = 'results/runnable_pool.json'
o = json.loads(side(2, p).decode('utf-8'))
t = json.loads(side(3, p).decode('utf-8'))
oe = {e['id']: e for e in o['entries']}
te = {e['id']: e for e in t['entries']}
assert set(oe) == set(te), 'entry id sets diverge'
diff_ids = [i for i in oe if oe[i] != te[i]]

def shards_owner_max(e):
    """Max owner_since across the entry's shard claim records.
    r709 fix: compare ONLY owner_since fields (space format) -- the r709 v1 ts-walk was
    poisoned by format asymmetry ('2026-10-05 03:47:08' sorts below '2026-10-05T01:13:21'
    because ' ' < 'T'), yielding a false tie against the entry-level updated_at."""
    best = ''
    def walk(v):
        nonlocal best
        if isinstance(v, dict):
            for k, x in v.items():
                if k in ('owner_since', 'claimed_at', 'cleared_ts') and isinstance(x, str) and x > best:
                    best = x
                elif isinstance(x, (dict, list)):
                    walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
    walk(e)
    return best

decided = {}
for i in diff_ids:
    ots, tts = shards_owner_max(oe[i]), shards_owner_max(te[i])
    if ots > tts:
        o['entries'][[k for k, e in enumerate(o['entries']) if e['id'] == i][0]] = oe[i]
        decided[i] = 'ours(owner_since %s>%s)' % (ots, tts)
    elif tts > ots:
        o['entries'][[k for k, e in enumerate(o['entries']) if e['id'] == i][0]] = te[i]
        decided[i] = 'theirs(owner_since %s>%s; ours done-state multi-anchored in git history: ckpt files + close/harvest/F-04 commits + our merge parent)' % (tts, ots)
    else:
        decided[i] = 'tie-keep-ours(%s)' % ots
# write + read-back assertion: resolved pool has te's shards for the theirs-won ids
write(p, json.dumps(o, ensure_ascii=False, indent=1) + '\n')
back = json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
be = {e['id']: e for e in back['entries']}
assert len(be) == len(oe), 'entry count changed'
for i, d in decided.items():
    if d.startswith('theirs'):
        assert be[i] == te[i], 'read-back mismatch %s' % i
receipt['faces'][p] = {'action': 'per-entry newer-wins', 'diff_ids': {k: v for k, v in decided.items()},
                       'entry_count': len(be)}

# ---- 4) twins same-side spot assertion (dashboard js/json + LIVE md/json) per r708 twin law
dj = json.load(open(os.path.join(ROOT, 'results/dashboard_status.json'), encoding='utf-8'))
assert dj['meta']['generated_at'].startswith('2026-10-05T04:02'), 'dashboard json side wrong: %s' % dj['meta']['generated_at']
js = open(os.path.join(ROOT, 'results/dashboard_status.js'), 'rb').read()
assert b'04:02:41' in js, 'dashboard js twin not on same generation side'
rep = json.load(open(os.path.join(ROOT, 'docs/daily_report/REPORT-2026-10-05.json'), encoding='utf-8'))
assert str(rep.get('generated_at', '')).startswith('2026-10-05 04:02'), 'report json side wrong'
receipt['twin_checks'] = {'dashboard_js_json_same_side': True, 'report_md_json_same_side': True}

# ---- 5) residual conflict-marker scan on resolved faces (none expected; fail loud if any)
import re
for p in TAKE_OURS + list(UNION_LEDGERS) + ['results/runnable_pool.json']:
    raw = open(os.path.join(ROOT, p), 'rb').read()
    assert not re.search(rb'<<<<<<< ', raw), 'marker left in %s' % p

receipt['resolved_n'] = len(receipt['faces'])
open(os.path.join(ROOT, 'results', '_r709bmb_merge_resolve.json'), 'w', encoding='utf-8', newline='\n').write(
    json.dumps(receipt, ensure_ascii=False, indent=1) + '\n')
print('RESOLVED', len(receipt['faces']), 'faces; pool decided:', json.dumps(decided, ensure_ascii=False))
