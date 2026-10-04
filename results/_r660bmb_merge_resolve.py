# r660 bm-b merge resolver (r652/r656/r657/r453/r456 law family): 15 UU faces
# ours = HEAD:, theirs = MERGE_HEAD: direct raw-byte reads (r657 ii)
import subprocess, json, sys, re

def blob(rev, path):
    p = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True)
    if p.returncode != 0:
        return None
    return p.stdout

def pick_json_side(o_bytes, t_bytes, path, log):
    """Decide side for a JSON face: per-key union if 'machines' dict (r456 law,
    side-pick>0 assertion), else whole-face freshness by embedded ts."""
    try:
        o = json.loads(o_bytes.decode('utf-8'))
        t = json.loads(t_bytes.decode('utf-8'))
    except Exception as e:
        log.append(f'{path}: JSON parse fail ({e}) -> ours (conservative)')
        return 'ours', o_bytes
    def ts_of(d):
        for k in ('ts', 'asof', 'updated', 'updated_at', 'generated'):
            v = d.get(k) if isinstance(d, dict) else None
            if isinstance(v, (int, float)):
                return float(v)
            if isinstance(v, str):
                return v
        return None
    if isinstance(o, dict) and isinstance(t, dict) and isinstance(o.get('machines'), dict) and isinstance(t.get('machines'), dict):
        merged = dict(t)
        picks = {'ours': 0, 'theirs': 0}
        om, tm = o['machines'], t['machines']
        out_m = {}
        for k in sorted(set(om) | set(tm)):
            if k in om and k in tm:
                to, tt = ts_of(om[k]), ts_of(tm[k])
                if to is not None and tt is not None and str(to) != str(tt):
                    side = 'ours' if str(to) > str(tt) else 'theirs'
                else:
                    side = 'theirs' if json.dumps(tm[k], sort_keys=True) != json.dumps(om[k], sort_keys=True) else 'ours'
                out_m[k] = om[k] if side == 'ours' else tm[k]
                picks[side] += 1
            elif k in om:
                out_m[k] = om[k]; picks['ours'] += 1
            else:
                out_m[k] = tm[k]; picks['theirs'] += 1
        if picks['ours'] == 0 and picks['theirs'] == 0:
            log.append(f'{path}: per-key zero-hit BOTH -> whole-face freshness (r456 law)')
            side = 'ours'
        else:
            merged['machines'] = out_m
            # top-level non-machines keys: fresher ts wins
            to, tt = ts_of(o), ts_of(t)
            if to and tt and str(tt) > str(to):
                for k, v in t.items():
                    if k != 'machines':
                        merged[k] = v
            log.append(f'{path}: per-key union ours={picks["ours"]} theirs={picks["theirs"]} -> MERGED-BOTH')
            return 'merged', json.dumps(merged, ensure_ascii=False, indent=1).encode('utf-8')
    to, tt = ts_of(o), ts_of(t)
    if to is not None and tt is not None and str(to) != str(tt):
        side = 'theirs' if str(tt) > str(to) else 'ours'
    else:
        side = 'ours' if o_bytes == t_bytes else 'theirs'
    log.append(f'{path}: freshness ours_ts={to} theirs_ts={tt} -> {side}')
    return side, (o_bytes if side == 'ours' else t_bytes)

faces_json = [
    'docs/daily_report/REPORT-2026-10-04.json',
    'docs/live_usage/LIVE-2026-10-04.json',
    'docs/live_usage/LIVE-latest.json',
    'results/_attrition_guard_scan.json',
    'results/compute_audit.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/regime_state.json',
    'results/token_usage.json',
    'results/update_status.json',
]
md_twin = {
    'docs/daily_report/REPORT-2026-10-04.md': 'docs/daily_report/REPORT-2026-10-04.json',
    'docs/live_usage/LIVE-2026-10-04.md': 'docs/live_usage/LIVE-2026-10-04.json',
    'docs/live_usage/LIVE-latest.md': 'docs/live_usage/LIVE-latest.json',
}
log = []
resolved = {}
for f in faces_json:
    o, t = blob('HEAD', f), blob('MERGE_HEAD', f)
    if o is None and t is None:
        log.append(f'{f}: BOTH MISSING?! skip')
        continue
    if o is None:
        resolved[f] = ('theirs', t); log.append(f'{f}: ours missing -> theirs'); continue
    if t is None:
        resolved[f] = ('ours', o); log.append(f'{f}: theirs missing -> ours'); continue
    resolved[f] = pick_json_side(o, t, f, log)
for md, js in md_twin.items():
    side = resolved.get(js, ('theirs', b''))[0]
    b = blob('HEAD' if side == 'ours' else 'MERGE_HEAD', md)
    if b is None:
        b = blob('MERGE_HEAD' if side == 'ours' else 'HEAD', md)
        side = 'theirs' if side == 'ours' else 'ours'
    resolved[md] = (side, b)
    log.append(f'{md}: aligned with JSON twin -> {side}')

# CODELY.md: append-only union, exact-line dedup keep-first (r453 law), ours-first base
o = blob('HEAD', 'CODELY.md').decode('utf-8', errors='replace')
t = blob('MERGE_HEAD', 'CODELY.md').decode('utf-8', errors='replace')
o_lines, t_lines = o.splitlines(), t.splitlines()
t_set = set(t_lines)
merged = list(t_lines) + [l for l in o_lines if l not in t_set]
mk = sum(1 for l in merged if l.startswith(('<<<<<<<', '=======', '>>>>>>>')))
assert mk == 0, f'CODELY markers {mk}'
c660 = sum(1 for l in merged if 'r660 bm-b' in l)
c457 = sum(1 for l in merged if 'r457 bm-c' in l or 'r453 bm-c' in l or 'r456 bm-c' in l)
log.append(f'CODELY.md: union lines={len(merged)} (ours {len(o_lines)}/theirs {len(t_lines)}) r660-count={c660} bmc-r45x-count={c457}')
assert c660 == 1, f'r660 entry count {c660}'
assert c457 >= 1, 'bm-c r45x entries missing'
resolved['CODELY.md'] = ('union', '\n'.join(merged) + '\n'.encode('utf-8').decode('utf-8') if False else '\n'.join(merged).encode('utf-8'))

# write resolved files
for f, (side, data) in resolved.items():
    with open(f, 'wb') as fh:
        fh.write(data)
    log.append(f'WROTE {f} [{side}] {len(data)}B')

# final verification: zero conflict markers line-start across all 15 faces
bad = []
for f in list(resolved.keys()):
    txt = open(f, 'rb').read().decode('utf-8', errors='replace')
    for i, ln in enumerate(txt.splitlines(), 1):
        if ln.startswith(('<<<<<<<', '>>>>>>>')):
            bad.append(f'{f}:L{i}')
            break
print('\n'.join(log))
print('MARKER-START LINES:', bad if bad else 'NONE')
print('FACES RESOLVED:', len(resolved), 'of 15')
assert not bad, 'markers remain'
assert len(resolved) == 15, f'resolved {len(resolved)} != 15'
print('RESOLVE OK')
