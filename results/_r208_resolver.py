"""R208 rebase conflict resolver (r161/r185/r188/r201/r203 family recipe).

11 UU files, all dual-machine same-window S6 shared-state conflicts.
Rules:
- snapshot status files: take side with newer ts/updated/generated field (whole side)
- autofill_state.json: launches union (identity dedupe, ts sort, cap 50 rolling);
  last_tick take-newer by internal ts, same-second tie -> HEAD (r140/r193 precedent)
- token_usage.json: take newer generated side whole
Verify-parse BEFORE write-back (r185). No git add inside this script.
"""
import io, json

PREFIX_JS = 'window.DASH_DATA = '

def sides(f):
    t = io.open(f, encoding='utf-8').read()
    lines = t.split('\n')
    head_lines, ours_lines = [], []
    state = 'common'
    for ln in lines:
        if ln.startswith('<<<<<<<'): state = 'head'; continue
        if ln.startswith('======='): state = 'ours'; continue
        if ln.startswith('>>>>>>>'): state = 'common'; continue
        if state == 'head': head_lines.append(ln); continue
        if state == 'ours': ours_lines.append(ln); continue
        head_lines.append(ln); ours_lines.append(ln)
    return '\n'.join(head_lines), '\n'.join(ours_lines)

def parse(f, txt):
    if f.endswith('.js'):
        i = txt.find(PREFIX_JS)
        assert i >= 0, f + ': no DASH_DATA prefix'
        txt = txt[i + len(PREFIX_JS):].strip().rstrip(';')
    return json.loads(txt)

def ts_of(d):
    for k in ('ts', 'updated', 'generated', 'now'):
        if k in d:
            return d[k]
    return ''

resolved, skipped = [], []

def resolve_snapshot(f, prefer='ours'):
    h, o = sides(f)
    hj, oj = parse(f, h), parse(f, o)
    th, to = ts_of(hj), ts_of(oj)
    # tie -> keep HEAD (older writer wins only on exact tie per r140; here prefer newer)
    pick = hj if th > to else (oj if to > th else (hj if prefer == 'head' else oj))
    src = 'head' if pick is hj else 'ours'
    io.open(f, 'w', encoding='utf-8', newline='\n').write(json.dumps(pick, ensure_ascii=False, indent=2) + '\n')
    back = json.load(io.open(f, encoding='utf-8'))
    assert back == pick, f + ': write-back mismatch'
    resolved.append('%s -> %s (ts %s vs %s)' % (f, src, th, to))

def resolve_autofill():
    f = 'results/autofill_state.json'
    h, o = sides(f)
    hj, oj = json.loads(h), json.loads(o)
    # launches union: identity dedupe by canonical json, ts sort, cap 50 rolling
    seen = {}
    for e in hj['launches'] + oj['launches']:
        seen[json.dumps(e, ensure_ascii=False, sort_keys=True)] = e
    merged = sorted(seen.values(), key=lambda e: e.get('ts', ''))
    n_union = len(merged)
    merged = merged[-50:]  # rolling cap 50 (oldest dropped)
    # last_tick: take-newer by internal ts; same-second tie -> HEAD (r140/r193)
    lt_h, lt_o = hj['last_tick'], oj['last_tick']
    if lt_o.get('ts', '') > lt_h.get('ts', ''):
        lt = lt_o; src = 'ours'
    else:
        lt = lt_h; src = 'head(tie-or-older-ours)'
    assert isinstance(lt, dict), 'last_tick must stay dict (r203)'
    out = {
        'launches': merged,
        'last_tick': lt,
        'rebase_union_note': 'r208 rebase union (bm-a): launches %d+%d -> %d unique -> cap 50 rolling (oldest dropped); last_tick take-newer, same-second tie -> HEAD = %s' % (
            len(hj['launches']), len(oj['launches']), n_union, src),
    }
    io.open(f, 'w', encoding='utf-8', newline='\n').write(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    back = json.load(io.open(f, encoding='utf-8'))
    assert isinstance(back['last_tick'], dict) and len(back['launches']) <= 50
    assert back['launches'] == merged and back['last_tick'] == lt
    resolved.append('%s -> union %d unique cap50; last_tick %s from %s' % (f, n_union, lt.get('ts'), src))

def resolve_token_usage():
    f = 'results/token_usage.json'
    h, o = sides(f)
    hj, oj = json.loads(h), json.loads(o)
    th, to = hj['generated'], oj['generated']
    pick = hj if th > to else oj
    src = 'head' if pick is hj else 'ours'
    io.open(f, 'w', encoding='utf-8', newline='\n').write(json.dumps(pick, ensure_ascii=False, indent=2) + '\n')
    back = json.load(io.open(f, encoding='utf-8'))
    assert back == pick
    resolved.append('%s -> %s (generated %s vs %s)' % (f, src, th, to))

for f in [
    'results/compute_audit.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/heat_update_status.json',
    'results/lhb_update_status.json',
    'results/regime_state.json',
    'results/update_status.json',
]:
    resolve_snapshot(f, prefer='ours')

resolve_autofill()
resolve_token_usage()

for r in resolved:
    print('OK', r)
print('resolved:', len(resolved), '| skipped:', len(skipped))
