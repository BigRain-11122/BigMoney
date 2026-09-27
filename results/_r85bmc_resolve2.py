# -*- coding: utf-8 -*-
"""r85 bm-c resolve2: SECOND same-window collision batch (r327 law: same recipe, no
method change). Replays da760c1f (r85 round commit) onto 46efedad (bm-b r329+addendum).
ours=:2:=HEAD(46efedad, bm-b S6 14:24-14:25), theirs=:3:=da760c1f (bm-c r85 S6
14:29-14:31, NEWER -> take-mine for ts-ordered snapshots), base=:1:=c5d480ac.
"""
import io, json, subprocess

def blob(n, path):
    r = subprocess.run(['git', 'show', f':{n}:{path}'], capture_output=True)
    assert r.returncode == 0, f'blob :{n}:{path} rc={r.returncode}'
    return r.stdout

def dig(d, path):
    for k in path.split('.'):
        d = d[int(k)] if k.isdigit() else d[k]
    return d

# ---------- A) 25 take-MINE files (mine newer face, byte-faithful :3:) ----------
TAKE_MINE = [
    'docs/daily_report/REPORT-2026-09-27.json', 'docs/daily_report/REPORT-2026-09-27.md',
    'results/daily_scorecard.json', 'results/dashboard_status.js', 'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
    'results/heat_update_status.json', 'results/lhb_update_status.json',
    'results/paper/COMPOSITE-CE-01_paper.json', 'results/paper/COMPOSITE-CE-02_paper.json',
    'results/paper/DROUGHT-CE-01_paper.json', 'results/paper/ENGULF-CE-01_paper.json',
    'results/paper/NEEDLE-DE-01_paper.json', 'results/paper/VOLATILITY-CE-01_paper.json',
    'results/paper_export/export-2026-09-24.json', 'results/paper_export/latest.json',
    'results/prospect_paper/_summary.json', 'results/prospect_promotion/_summary.json',
    'results/regime_state.json', 'results/scorecard_v1.json',
    'results/strategy_scorecard.json', 'results/t35_open_fill_verify.json',
    'results/token_usage.json', 'results/update_status.json',
]
TSKEYS = {
    'docs/daily_report/REPORT-2026-09-27.json': 'generated_at',
    'results/daily_scorecard.json': 'traders.0.forward_guard.as_of',
    'results/fundamental_b_layer_filter.json': 'updated',
    'results/futures_update_status.json': 'ts',
    'results/heat_update_status.json': 'updated',
    'results/lhb_update_status.json': 'updated',
    'results/paper/COMPOSITE-CE-01_paper.json': 'updated',
    'results/paper/COMPOSITE-CE-02_paper.json': 'updated',
    'results/paper/DROUGHT-CE-01_paper.json': 'updated',
    'results/paper/ENGULF-CE-01_paper.json': 'updated',
    'results/paper/NEEDLE-DE-01_paper.json': 'updated',
    'results/paper/VOLATILITY-CE-01_paper.json': 'updated',
    'results/paper_export/export-2026-09-24.json': 'generated_from_state_updated',
    'results/paper_export/latest.json': 'generated_from_state_updated',
    'results/prospect_paper/_summary.json': 'generated',
    'results/prospect_promotion/_summary.json': 'generated',
    'results/regime_state.json': 'updated',
    'results/scorecard_v1.json': 'generated',
    'results/strategy_scorecard.json': 'generated',
    'results/t35_open_fill_verify.json': 'ts',
    'results/token_usage.json': 'generated',
    'results/update_status.json': 'updated',
}
for f in TAKE_MINE:
    ob, tb = blob('2', f), blob('3', f)
    if f in TSKEYS:
        o, t = json.loads(ob), json.loads(tb)
        assert dig(t, TSKEYS[f]) > dig(o, TSKEYS[f]), f'{f}: mine NOT newer'
    if f.endswith(('.json', '.js')):
        txt = tb.decode('utf-8')
        if f.endswith('.js'):
            assert txt.lstrip().startswith('window.DASH_DATA'), f'{f}: wrapper stripped'
            json.loads(txt.strip()[len('window.DASH_DATA'):].strip().lstrip('=').rstrip(';'))
        else:
            json.loads(txt)
    open(f, 'wb').write(tb)
print(f"A) take-mine x{len(TAKE_MINE)} byte-faithful ({len(TSKEYS)} ts assertions)")

# ---------- B) autofill: launches composite-key union + last_tick take-mine ----------
o = json.loads(blob('2', 'results/autofill_state.json'))
t = json.loads(blob('3', 'results/autofill_state.json'))
K = lambda r: (r.get('ts'), r.get('machine'), r.get('pid'),
               r.get('runner_sha256'), r.get('entry'), r.get('shard'))
ok = {K(r): r for r in o['launches']}
tk = {K(r): r for r in t['launches']}
assert len(ok) == len(o['launches']) and len(tk) == len(t['launches']), 'in-side dup'
bad = [k for k in set(ok) & set(tk) if ok[k] != tk[k]]
assert not bad, f'same-key divergence (r322 flag-law): {bad[:2]}'
merged = dict(ok); merged.update(tk)          # shared identical, ours has +1 (bm-b 14:20:02)
assert len(merged) == 45, f'union {len(merged)} != 45'
assert t['last_tick']['ts'] > o['last_tick']['ts'], 'last_tick not newer'
out = dict(t)
out['launches'] = sorted(merged.values(), key=lambda r: r['ts'])  # append-order face
out['last_tick'] = t['last_tick']
# producer format: mirror base face (CRLF); verify indent round-trip first
base = blob('1', 'results/autofill_state.json')
crlf = base.count(b'\r\n') > 0
btxt = base.decode('utf-8').replace('\r\n', '\n')
assert json.dumps(json.loads(btxt), ensure_ascii=False, indent=1) == btxt, \
    'autofill producer face != indent1 no-trailing-newline round-trip'
io.open('results/autofill_state.json', 'w', encoding='utf-8',
        newline='\r\n' if crlf else '\n').write(
    json.dumps(out, ensure_ascii=False, indent=1))
d = json.loads(io.open('results/autofill_state.json', encoding='utf-8').read())
assert len(d['launches']) == 45 and d['last_tick']['ts'] == '2026-09-27 14:30:01'
print(f"B) autofill: launches union {len(ok)}|{len(tk)}->45 zero-loss (overlap "
      f"{len(set(ok) & set(tk))} identical, ours-only 1 absorbed), last_tick take-mine "
      f"bm-c 14:30:01 > bm-b 14:20:02, face CRLF={crlf} indent1 round-trip verified")

# ---------- C) compute_audit: history union + latest take-mine ----------
o = json.loads(blob('2', 'results/compute_audit.json'))
t = json.loads(blob('3', 'results/compute_audit.json'))
K = lambda e: (e.get('ts'), e.get('machine'))
ko = {K(e): e for e in o['history']}
kt = {K(e): e for e in t['history']}
assert len(ko) == len(o['history']) and len(kt) == len(t['history']), 'in-side dup'
bad = [k for k in set(ko) & set(kt) if ko[k] != kt[k]]
assert not bad, f'same-key divergence (r322 flag-law) {bad[:2]}'
merged = dict(ko); merged.update(kt)
hist = sorted(merged.values(), key=lambda e: e['ts'])
assert 'ts' in o['latest'] and 'ts' in t['latest'], 'r319 probe-existence'
assert t['latest']['ts'] > o['latest']['ts'], 'audit latest not newer'
out = dict(t); out['history'] = hist; out['latest'] = t['latest']
bb = blob('1', 'results/compute_audit.json')
assert bb.count(b'\r\n') == 0 and bb.split(b'\n')[1].startswith(b' "'), 'base LF indent1'
io.open('results/compute_audit.json', 'w', encoding='utf-8', newline='\n').write(
    json.dumps(out, ensure_ascii=False, indent=1) + '\n')
d = json.loads(io.open('results/compute_audit.json', encoding='utf-8').read())
assert len(d['history']) == len(merged) and d['latest']['ts'] == '2026-09-27 14:29:28'
print(f"C) compute_audit: history union {len(o['history'])}|{len(t['history'])}->"
      f"{len(hist)} zero-loss, latest take-mine 14:29:28 (base LF indent1 mirrored)")

# ---------- D) x2_watch_log: line-level union ----------
ol = blob('2', 'results/x2_watch_log.jsonl').decode('utf-8').splitlines()
tl = blob('3', 'results/x2_watch_log.jsonl').decode('utf-8').splitlines()
seen, union = set(), []
for line in ol + tl:
    if line.strip() and line not in seen:
        seen.add(line); union.append(line)
union.sort(key=lambda l: json.loads(l).get('ts', ''))
assert len(union) == len(set(ol) | set(tl)), 'union count mismatch'
io.open('results/x2_watch_log.jsonl', 'w', encoding='utf-8', newline='\n').write(
    '\n'.join(union) + '\n')
print(f"D) x2_watch_log: line union {len(set(ol))}|{len(set(tl))}->{len(union)} "
      f"(ours-only {len(set(ol) - set(tl))}, mine-only {len(set(tl) - set(ol))}) zero-loss")

# ---------- E) CODELY: memory-union direct-concat (both sides pure-append) ----------
b, ob, tb = blob('1', 'CODELY.md'), blob('2', 'CODELY.md'), blob('3', 'CODELY.md')
assert ob.startswith(b) and tb.startswith(b), 'prefix assertion (r212)'
a_suf, c_suf = ob[len(b):], tb[len(b):]
union = b + a_suf + c_suf
assert len(union) == len(b) + len(a_suf) + len(c_suf)
union.decode('utf-8')
assert len(union) < 10240, f'CODELY {len(union)}B over 10KB'
open('CODELY.md', 'wb').write(union)
txt = union.decode('utf-8')
assert 'r329 bm-b' in txt and 'r85 bm-c] 坑律' in txt, 'both sides entries missing'
print(f"E) CODELY: memory-union concat {len(b)}+{len(a_suf)}(bm-b r329 x2 entries)+"
      f"{len(c_suf)}(r85 rolling-window)={len(union)}B (<10KB), entries verbatim")

print('RESOLVE2 COMPLETE -- 29 UU: 25 take-mine + autofill/audit unions + x2 union + CODELY concat')
