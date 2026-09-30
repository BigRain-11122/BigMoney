# r478 bm-b rebase-conflict resolver (skill bigmoney-conflict-resolve recipes)
# Laws: r188/R208/R209/R212/R216/r220 -- classify-first, union ledgers, take-new
# snapshots by ts, zero-loss validation, bytes reads (no shell redirect).
import json, subprocess, sys, os

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def ts_of(obj):
    if not isinstance(obj, dict):
        return None
    for k in ('ts', 'updated', 'generated', 'now', 'updated_at', 'written_at',
              'scan_ts', 'ts_iso', 'generated_at', 'last_scan_ts', 'asof'):
        v = obj.get(k)
        if isinstance(v, (int, float)) and v > 1e9:
            return float(v)
        if isinstance(v, str):
            try:
                import datetime
                t = datetime.datetime.fromisoformat(v.replace('Z', '+00:00'))
                return t.timestamp()
            except Exception:
                continue
    return None

def take_new_json(path):
    a, b = blob(2, path), blob(3, path)
    ja, jb = json.loads(a.decode('utf-8')), json.loads(b.decode('utf-8'))
    ta, tb = ts_of(ja), ts_of(jb)
    if ta is not None and tb is not None:
        win = a if ta >= tb else b   # tie -> stage3 (ours-later per r140 HEAD-tie spirit at rebase stop = take newer; equal ts take replay side)
        side = 'stage2' if (ta > tb) else 'stage3'
    else:
        win, side = b, 'stage3(fallback)'
    open(path, 'wb').write(win)
    json.loads(open(path, 'rb').read().decode('utf-8'))  # validate
    return side

def take_new_text_pair(json_path, text_path):
    side = take_new_json(json_path)
    stage = 2 if side.startswith('stage2') else 3
    r = blob(stage, text_path)
    if r is None:
        r = blob(3 if stage == 2 else 2, text_path)
    open(text_path, 'wb').write(r)
    return f'{side}(md-twin stage{stage})'

def union_ledger(path):
    a, b = blob(2, path), blob(3, path)
    ja, jb = json.loads(a.decode('utf-8')), json.loads(b.decode('utf-8'))
    out = {}
    for k in set(ja) | set(jb):
        va, vb = ja.get(k), jb.get(k)
        if isinstance(va, list) and isinstance(vb, list):
            seen, merged = set(), []
            for row in va + vb:
                key = json.dumps(row, ensure_ascii=False, sort_keys=True)
                if key not in seen:
                    seen.add(key)
                    merged.append(row)
            out[k] = merged          # zero-loss union, |A u B|
        else:
            pick = va if va is not None else vb
            if isinstance(va, dict) and isinstance(vb, dict):
                ta, tb = ts_of(va), ts_of(vb)
                pick = va if (ta or 0) >= (tb or 0) else vb
            out[k] = pick            # state fields: newer ts wins
    open(path, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1))
    json.loads(open(path, encoding='utf-8').read())
    return 'union+take-new'

def memory_union(path):
    a = blob(2, path).decode('utf-8').splitlines(keepends=True)
    b = blob(3, path).decode('utf-8').splitlines(keepends=True)
    seen = set(a)
    merged = list(a) + [ln for ln in b if ln not in seen]   # keep both sides verbatim, dedupe identical
    open(path, 'w', encoding='utf-8', newline='').writelines(merged)
    return f'line-union {len(a)}+{len(b)}->{len(merged)}'

aggr = [f'results/aggr_paper/AGGR-{n}_paper.json' for n in (
    'BARBELL', 'CONC-TOP2', 'FULLCE-C80', 'FULLCE', 'GREEN-MAX', 'GREEN-TOP2',
    'MOM', 'NOCASH', 'OFFENSE-FULL', 'OFFENSE', 'REG3', 'REGIME', 'TOP2-60',
    'TOP2-80', 'TOP2-C80', 'TOP2-C95', 'TOP2-MON', 'TOP2-WK', 'TOP3-GRAD', 'TOP3')]

report = []
# 1) memory-union
report.append(('CODELY.md', memory_union('CODELY.md')))
# 2) rolling ledgers
for p in ('results/compute_audit.json', 'results/regime_state.json'):
    report.append((p, union_ledger(p)))
# 3) classified snapshots
for p in ('results/fundamental_b_layer_filter.json', 'results/lhb_update_status.json',
          'results/update_status.json', 'results/token_usage.json',
          'results/_attrition_guard_scan.json'):
    report.append((p, take_new_json(p)))
# 4) manually-classified same-day regenerated snapshot families (take-new, md follows json twin)
for p in aggr:
    report.append((p, take_new_json(p)))
for jp, tp in (('docs/daily_report/REPORT-2026-09-30.json', 'docs/daily_report/REPORT-2026-09-30.md'),
               ('docs/live_usage/LIVE-2026-09-30.json', 'docs/live_usage/LIVE-2026-09-30.md'),
               ('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'),
               ('results/market_clock/call_latest.json', 'results/market_clock/CALL-2026-09-30.md')):
    report.append((jp, take_new_text_pair(jp, tp)))

for path, verdict in report:
    print(f'{verdict:28s} {path}')

# add all resolved
paths = [p for p, _ in report] + ['docs/daily_report/REPORT-2026-09-30.md',
           'docs/live_usage/LIVE-2026-09-30.md', 'docs/live_usage/LIVE-latest.md',
           'results/market_clock/CALL-2026-09-30.md']
subprocess.run(['git', 'add', '--'] + paths, check=True)
print('RESOLVED_AND_STAGED', len(paths), 'files')
