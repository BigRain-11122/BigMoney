import subprocess, json, io, re, os

def side(stage, f, retries=5):
    for i in range(retries):
        r = subprocess.run(['git','show',stage+':'+f],capture_output=True)
        if r.returncode == 0:
            return r.stdout
        import time; time.sleep(0.6)
    raise RuntimeError('git show %s%s failed: %s' % (stage, f, r.stderr[:200]))

def find_ts(obj, depth=0):
    if depth > 4 or not isinstance(obj, dict):
        return None
    for k in ('ts','updated','generated_at','asof','generated','now','report_ts','time'):
        v = obj.get(k)
        if isinstance(v, str):
            return v
    for v in obj.values():
        r = find_ts(v, depth+1)
        if r:
            return r
    return None

log = []

def resolve_regen(f):
    """regen face: ts-duel H vs P; tie/none -> P (literal pick-4 blob)."""
    h = side(':2:', f); p = side(':3:', f)
    try:
        hj = json.loads(h.decode('utf-8',errors='replace'))
        pj = json.loads(p.decode('utf-8',errors='replace'))
        th, tp = find_ts(hj), find_ts(pj)
    except Exception:
        th = tp = None
    if th and tp and th > tp:
        data, winner = h, 'H'
    elif th and tp and th < tp:
        data, winner = p, 'P'
    else:
        data, winner = p, 'P-tie-or-nots'
    with io.open(f,'wb') as fh:
        fh.write(data)
    log.append('%s -> %s (H ts=%s P ts=%s, %dB)' % (f, winner, th, tp, len(data)))

def resolve_jsonl_union(f):
    """append-only jsonl: union H+P rows + clean worktree tail rows (post-marker daemon appends)."""
    h = side(':2:', f).decode('utf-8', errors='replace')
    p = side(':3:', f).decode('utf-8', errors='replace')
    def rows(txt):
        out = []
        for ln in txt.splitlines():
            s = ln.strip()
            if not s or s.startswith('<<<<<<<') or s.startswith('=======') or s.startswith('>>>>>>>'):
                continue
            out.append(s)
        return out
    hr, pr = rows(h), rows(p)
    seen = set(); union = []
    for r in hr + pr:
        if r not in seen:
            seen.add(r); union.append(r)
    tail_new = 0
    if os.path.exists(f):
        wt = io.open(f, encoding='utf-8', errors='replace').read()
        for r in rows(wt):
            if r not in seen:
                seen.add(r); union.append(r); tail_new += 1
    with io.open(f,'w',encoding='utf-8',newline='\n') as fh:
        fh.write('\n'.join(union) + ('\n' if union else ''))
    log.append('%s -> UNION H=%d P=%d -> %d rows (worktree tail +%d)' % (f, len(hr), len(pr), len(union), tail_new))

def resolve_live_or_duel(f):
    """bm-b-owned live face: worktree if marker-free (daemon rewrote = live-wins), else P."""
    wt_clean = False
    if os.path.exists(f):
        raw = io.open(f, encoding='utf-8', errors='replace').read()
        if '<<<<<<<' not in raw and '>>>>>>>' not in raw:
            try:
                json.loads(raw); wt_clean = True
            except Exception:
                pass
    if wt_clean:
        log.append('%s -> WORKTREE-LIVE (daemon rewrote, marker-free)' % f)
        return
    resolve_regen(f)
    log[-1] = log[-1] + ' [fallback: worktree had markers]'

def resolve_keyed(f):
    """machine/latest-keyed json: adaptive per-key merge."""
    h = json.loads(side(':2:', f).decode('utf-8',errors='replace'))
    p = json.loads(side(':3:', f).decode('utf-8',errors='replace'))
    keys_h = {k for k in h if not isinstance(h[k], (list, dict))}
    # token_usage-like: latest+history
    if all(k in h for k in ('history',)) and any(k in h for k in ('latest','total')):
        merged = {}
        th, tp = find_ts(h), find_ts(p)
        base = h if (th or '') >= (tp or '') else p
        merged.update(base)
        hh, ph = h.get('history', []), p.get('history', [])
        seen = set(); rows = []
        for r in hh + ph:
            key = json.dumps(r, sort_keys=True, ensure_ascii=False) if not isinstance(r, str) else r
            if key in seen:
                continue
            seen.add(key); rows.append(r)
        try:
            rows.sort(key=lambda r: (r.get('ts','') if isinstance(r, dict) else str(r)))
        except Exception:
            pass
        merged['history'] = rows
        with io.open(f,'w',encoding='utf-8',newline='\n') as fh:
            json.dump(merged, fh, ensure_ascii=False, indent=1)
        log.append('%s -> latest-duel base=%s + history union %d+%d->%d' % (f, 'H' if base is h else 'P', len(hh), len(ph), len(rows)))
        return
    # generic per-key: same key both sides -> ts-duel; else union
    merged = {}
    for k in set(h) | set(p):
        if k in h and k in p:
            th, tp = find_ts(h[k]), find_ts(p[k])
            merged[k] = h[k] if (th or '') >= (tp or '') else p[k]
        else:
            merged[k] = h.get(k, p.get(k))
    with io.open(f,'w',encoding='utf-8',newline='\n') as fh:
        json.dump(merged, fh, ensure_ascii=False, indent=1)
    log.append('%s -> per-key merge (%d keys)' % (f, len(merged)))

# --- dispatch ---
regen = ['docs/daily_report/REPORT-2026-10-07.json','docs/daily_report/REPORT-2026-10-07.md',
         'docs/live_usage/LIVE-2026-10-07.json','docs/live_usage/LIVE-2026-10-07.md',
         'docs/live_usage/LIVE-latest.json','docs/live_usage/LIVE-latest.md',
         'results/dashboard_status.js','results/dashboard_status.json',
         'results/fundamental_b_layer_filter.json']
for f in regen:
    resolve_regen(f)

resolve_jsonl_union('results/fund_divlowvol_p1/nulls.jsonl')
resolve_jsonl_union('results/saturation_engine/history_bm-b.jsonl')
resolve_live_or_duel('results/saturation_engine/face_bm-b.json')
resolve_live_or_duel('results/saturation_engine/state_bm-b.json')
resolve_keyed('results/p1d_gates.json')
resolve_keyed('results/token_usage.json')

print('\n'.join(log))
print('RESOLVE-DONE')
