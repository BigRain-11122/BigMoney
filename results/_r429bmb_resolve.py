# -*- coding: utf-8 -*-
# r429 bm-b push-rejection rebase resolver (canon: bigmoney-conflict-resolve skill,
# mirroring _r428bmb_resolve.py rev2 + _r431bma_resolve.py mechanics).
# stages: :1: base, :2: ours = origin/main (bm-a r431 series S6 ~14:0x runs),
#         :3: theirs = replayed bm-b r429 commit (S6 chain 14:26-14:31 runs).
# faces (30 UU): 2 rolling-ledger unions + 1 jsonl line-union + 3 twin pairs
#   (REPORT-2026-09-29, LIVE-2026-09-29, LIVE-latest; json probe decides, md byte-copy
#   same side per r329; live_usage x4 = same-day idempotent regen face per r428 canon)
#   + dashboard json probe with js-wrapper byte-copy coupled (R209) + 22 snapshot take-new
#   via hardened deep-ts probe on STAGED blobs only (r311/r319/r100/R350; R350: TS_RE
#   requires time-of-day, no key-EXCLUDE lists; r140 tie -> HEAD :2:).
import io, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")

def raw(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    assert r.returncode == 0, (stage, path, r.stderr[:200])
    return r.stdout

def deep_ts(obj, best=''):
    if isinstance(obj, dict):
        for k, v in obj.items():
            kn = str(k).replace('_', '').replace('-', '').lower()
            if isinstance(v, str) and TS_RE.match(v) and any(p in kn for p in ('generated', 'updated', 'ts', 'asof', 'date')):
                if v > best: best = v
            elif isinstance(v, (dict, list)):
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for it in obj:
            best = deep_ts(it, best)
    return best

def take_newer(path):
    b2, b3 = raw('2', path), raw('3', path)
    t2 = deep_ts(json.loads(b2.decode('utf-8')))
    t3 = deep_ts(json.loads(b3.decode('utf-8')))
    if not t2 and not t3:
        raise SystemExit(f'{path}: no ts probe either side, refuse blind pick')
    winner, side = ('2', b2) if t2 >= t3 else ('3', b3)   # r140 tie -> HEAD (:2:)
    with io.open(path, 'wb') as f:
        f.write(side)
    print(f'[take-new:{path}] :2:ts={t2!r} :3:ts={t3!r} -> :{winner}: ({len(side)}B)')
    return winner

def byte_copy(path, winner):
    side = raw('2', path) if winner == '2' else raw('3', path)
    with io.open(path, 'wb') as f:
        f.write(side)
    print(f'[twin-copy:{path}] from :{winner}: ({len(side)}B)')

# ---------- 1) compute_audit.json rolling union (r188/R208, cap 201) ----------
P_AUD = 'results/compute_audit.json'
a2, a3 = json.loads(raw('2', P_AUD).decode('utf-8')), json.loads(raw('3', P_AUD).decode('utf-8'))
k = lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False)
u = {k(r): r for r in a2['history']}
for r in a3['history']:
    u[k(r)] = r
rows = sorted(u.values(), key=lambda r: r.get('ts', ''))
trim = rows[-201:]
lt2, lt3 = a2['latest'], a3['latest']
latest = lt3 if str(lt3.get('ts', '')) >= str(lt2.get('ts', '')) else lt2
aud_out = {'latest': latest, 'history': trim}
json.loads(json.dumps(aud_out, ensure_ascii=False))
tmp = P_AUD + '.tmp_r429bmb'
with io.open(tmp, 'w', encoding='utf-8', newline='') as f:
    json.dump(aud_out, f, ensure_ascii=False, indent=2)
    f.write('\n')
os.replace(tmp, P_AUD)
print(f'[audit-union] rows union={len(rows)} -> trim {len(trim)}, latest.ts={latest.get("ts")} (zero-loss union then cap)')

# ---------- 2) regime_state.json rolling union + state take-new ----------
P_R = 'results/regime_state.json'
r2, r3 = json.loads(raw('2', P_R).decode('utf-8')), json.loads(raw('3', P_R).decode('utf-8'))
out = dict(r2)
for lk in ('history', 'transitions'):
    if lk in r2 and lk in r3 and isinstance(r2[lk], list) and isinstance(r3[lk], list):
        uu = {k(r): r for r in r2[lk]}
        for r in r3[lk]:
            uu[k(r)] = r
        out[lk] = sorted(uu.values(), key=lambda r: str(deep_ts(r) or r))
t2, t3 = deep_ts(r2), deep_ts(r3)
if t3 > t2:
    for kk, vv in r3.items():
        if kk not in ('history', 'transitions'):
            out[kk] = vv
json.loads(json.dumps(out, ensure_ascii=False))
tmp = P_R + '.tmp_r429bmb'
with io.open(tmp, 'w', encoding='utf-8', newline='') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
    f.write('\n')
os.replace(tmp, P_R)
print(f'[regime-union] state take-new by deep-ts (:2:={t2!r} :3:={t3!r}); history={len(out.get("history", []))} transitions={len(out.get("transitions", []))}')

# ---------- 3) x2_watch_log.jsonl line union (r188/r217) ----------
P_X = 'results/x2_watch_log.jsonl'
x2, x3 = raw('2', P_X), raw('3', P_X)
seen, merged = set(), []
for line in (x2.split(b'\n') + x3.split(b'\n')):
    if line.strip() and line not in seen:
        seen.add(line); merged.append(line)
union_x = b'\n'.join(merged) + b'\n'
for line in merged:
    json.loads(line.decode('utf-8'))
with io.open(P_X, 'wb') as f:
    f.write(union_x)
n2 = len([l for l in x2.split(b'\n') if l.strip()]); n3 = len([l for l in x3.split(b'\n') if l.strip()])
print(f'[x2-union] :2: {n2} + :3: {n3} -> {len(merged)} lines zero-loss')

# ---------- 4) snapshot take-new faces ----------
for p in ('results/daily_scorecard.json', 'results/fundamental_b_layer_filter.json',
          'results/futures_update_status.json', 'results/lhb_update_status.json',
          'results/prospect_paper/_summary.json', 'results/prospect_promotion/_summary.json',
          'results/scorecard_v1.json', 'results/strategy_scorecard.json',
          'results/t35_open_fill_verify.json', 'results/token_usage.json',
          'results/update_status.json',
          'results/paper/COMPOSITE-CE-01_paper.json', 'results/paper/COMPOSITE-CE-02_paper.json',
          'results/paper/DROUGHT-CE-01_paper.json', 'results/paper/ENGULF-CE-01_paper.json',
          'results/paper/NEEDLE-DE-01_paper.json', 'results/paper/VOLATILITY-CE-01_paper.json',
          'results/paper_export/export-2026-09-28.json', 'results/paper_export/latest.json'):
    take_newer(p)

# ---------- 5) twin faces: json probe decides, md byte-copy same side (r329) ----------
w = take_newer('docs/daily_report/REPORT-2026-09-29.json')
byte_copy('docs/daily_report/REPORT-2026-09-29.md', w)
w2 = take_newer('docs/live_usage/LIVE-2026-09-29.json')
byte_copy('docs/live_usage/LIVE-2026-09-29.md', w2)
byte_copy('docs/live_usage/LIVE-latest.json', w2)
byte_copy('docs/live_usage/LIVE-latest.md', w2)

# ---------- 6) dashboard json probe -> js-wrapper byte-copy coupled (R209) ----------
w3 = take_newer('results/dashboard_status.json')
byte_copy('results/dashboard_status.js', w3)

# ---------- 7) parse-verify every written face (r185) + wrapper canary ----------
verify_list = (P_AUD, P_R,
               'results/daily_scorecard.json', 'results/fundamental_b_layer_filter.json',
               'results/futures_update_status.json', 'results/lhb_update_status.json',
               'results/prospect_paper/_summary.json', 'results/prospect_promotion/_summary.json',
               'results/scorecard_v1.json', 'results/strategy_scorecard.json',
               'results/t35_open_fill_verify.json', 'results/token_usage.json',
               'results/update_status.json',
               'results/paper/COMPOSITE-CE-01_paper.json', 'results/paper/COMPOSITE-CE-02_paper.json',
               'results/paper/DROUGHT-CE-01_paper.json', 'results/paper/ENGULF-CE-01_paper.json',
               'results/paper/NEEDLE-DE-01_paper.json', 'results/paper/VOLATILITY-CE-01_paper.json',
               'results/paper_export/export-2026-09-28.json', 'results/paper_export/latest.json',
               'docs/daily_report/REPORT-2026-09-29.json',
               'docs/live_usage/LIVE-2026-09-29.json', 'docs/live_usage/LIVE-latest.json',
               'results/dashboard_status.json')
for p in verify_list:
    json.loads(io.open(p, encoding='utf-8').read())
js = io.open('results/dashboard_status.js', encoding='utf-8').read()
json.loads(js.split('=', 1)[1].rsplit(';', 1)[0].strip())
print('[verify] all written faces parse-verified; js wrapper intact')
print('resolver r429 bm-b: 30 faces resolved (2 rolling union + 1 jsonl union + 22 snapshot take-new + 5 twin/js coupled copies)')
