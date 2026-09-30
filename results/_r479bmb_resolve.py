# r479 bm-b rebase-conflict resolver (skill bigmoney-conflict-resolve recipes)
# Laws: r188/R208/R209/R212/R216/r220/r312 -- classify-first, union ledgers,
# take-new snapshots by ts, pool = canonical merge_runnable_pool laws,
# zero-loss validation, bytes reads (no shell redirect).
# Unknown-classified file (results/_attrition_guard_scan.json) manually
# adjudicated = per-scan evidence snapshot -> take-new by ts (regenerated
# each scan, next round rewrites anyway).
import datetime
import json
import subprocess
import sys

sys.path.insert(0, 'scripts')
import merge_lane_views as m  # noqa: E402  (r479 fixed version: owner_since-null law)


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
        win = a if ta >= tb else b
        side = 'stage2' if ta > tb else 'stage3'
    else:
        win, side = b, 'stage3(fallback)'
    open(path, 'wb').write(win)
    json.loads(open(path, 'rb').read().decode('utf-8'))
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
            out[k] = merged
        else:
            pick = va if va is not None else vb
            if isinstance(va, dict) and isinstance(vb, dict):
                ta, tb = ts_of(va), ts_of(vb)
                pick = va if (ta or 0) >= (tb or 0) else vb
            out[k] = pick
    open(path, 'w', encoding='utf-8').write(
        json.dumps(out, ensure_ascii=False, indent=1))
    json.loads(open(path, encoding='utf-8').read())
    return 'union+take-new'


def memory_union(path):
    a = blob(2, path).decode('utf-8').splitlines(keepends=True)
    b = blob(3, path).decode('utf-8').splitlines(keepends=True)
    # merge-base prefix-identity assertion per D-20260927-09 classifier recipe:
    # find common prefix, then direct-concat both suffixes (NO line dedupe
    # across sides -- dedupe collapses structure; identical-line overlap
    # removed only within the shared prefix assumption).
    n = 0
    for la, lb in zip(a, b):
        if la != lb:
            break
        n += 1
    if n == 0:
        # no common prefix -- fall back to line-union with dedupe (defensive)
        seen = set(a)
        merged = list(a) + [ln for ln in b if ln not in seen]
        return f'line-union-fallback {len(a)}+{len(b)}->{len(merged)}'
    merged = a[:n] + a[n:] + b[n:]
    open(path, 'w', encoding='utf-8', newline='').writelines(merged)
    return f'prefix-concat {len(a)}+{len(b)} base={n} ->{len(merged)}'


def pool_union(path):
    a, b = blob(2, path), blob(3, path)
    ja = json.loads(a.decode('utf-8'))
    jb = json.loads(b.decode('utf-8'))
    merged, notes = m.merge_runnable_pool(
        [('stage2-ours', ja), ('stage3-theirs', jb)])
    blob_txt = json.dumps(merged, ensure_ascii=False, indent=1)
    json.loads(blob_txt)  # validate before write-back
    open(path, 'w', encoding='utf-8', newline='').write(blob_txt + '\n')
    # zero-loss assertions: done shards survive, defer markers survive
    ids = {e.get('id'): e for e in merged.get('entries', [])}
    for eid, want in (('P2NULL-KLIFT-K2200-S0', 'done'),
                      ('P2NULL-KLIFT-K2200-S1', 'done'),
                      ('P2NULL-KLIFT-K2200-S2', 'done')):
        e = ids.get(eid)
        assert e is not None, f'{eid} lost in pool union'
        st = [s.get('status') for s in e.get('shards', [])]
        assert want in st, f'{eid} shard done lost: {st}'
    for eid in ('EXCLUSION-MARGINAL-P1-RUN',
                'CROSS-START-ROBUSTNESS-P1-FACEB-RUN'):
        e = ids.get(eid)
        assert e is not None and e.get('status') == 'waiting' and \
            e.get('defer_note'), f'{eid} defer-marker lost'
    return f'pool-entry-union laws (done-absorb+defer-marker survived); {len(notes)} notes'


report = []
# 1) memory-union (prefix-concat per classifier recipe)
report.append(('CODELY.md', memory_union('CODELY.md')))
# 2) rolling ledgers
for p in ('results/compute_audit.json', 'results/regime_state.json'):
    report.append((p, union_ledger(p)))
# 3) canonical pool union via merge_lane_views laws
report.append(('results/runnable_pool.json', pool_union('results/runnable_pool.json')))
# 4) snapshots take-new
for p in ('results/futures_update_status.json', 'results/lhb_update_status.json',
          'results/update_status.json', 'results/token_usage.json',
          'results/_attrition_guard_scan.json'):
    report.append((p, take_new_json(p)))
# 5) same-day regen twin families (md follows json side)
for jp, tp in (('docs/daily_report/REPORT-2026-09-30.json',
                'docs/daily_report/REPORT-2026-09-30.md'),
               ('docs/live_usage/LIVE-2026-09-30.json',
                'docs/live_usage/LIVE-2026-09-30.md'),
               ('docs/live_usage/LIVE-latest.json',
                'docs/live_usage/LIVE-latest.md')):
    report.append((jp, take_new_text_pair(jp, tp)))

for path, verdict in report:
    print(f'{verdict:44s} {path}')

paths = [p for p, _ in report] + [
    'docs/daily_report/REPORT-2026-09-30.md',
    'docs/live_usage/LIVE-2026-09-30.md',
    'docs/live_usage/LIVE-latest.md']
subprocess.run(['git', 'add', '--'] + paths, check=True)
print('RESOLVED_AND_STAGED', len(paths), 'files')
