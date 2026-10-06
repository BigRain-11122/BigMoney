# r787 bm-b rebase conflict resolver (dead-r786-tail absorb commit replay vs bm-a r798 landed)
# Recipes per bigmoney-conflict-resolve SKILL.md + classify_conflicts.py output.
# ASCII only (PS5.1 encoding law). Stage2=origin/bm-a side, Stage3=ours(bm-b absorb) side.
import json, subprocess, sys, re
from collections import Counter

def side(stage, path):
    r = subprocess.run(['git','show',f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def ts_of(d, keys=('ts','generated_at','generated','updated','last_run','timestamp','asof','cutoff','last_write')):
    best = None
    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for k,v in o.items():
                if k in keys and isinstance(v,(str,int,float)):
                    s=str(v)
                    if best is None or s > best: best = s
                else: walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(d)
    return best or ''

def pick_new_by_ts(path, default_stage=2):
    a, b = side(2,path), side(3,path)
    if a is None: return b
    if b is None: return a
    try:
        da, db = json.loads(a), json.loads(b)
        ta, tb = ts_of(da), ts_of(db)
        return b if tb > ta else a   # tie -> HEAD-side (origin) per r140
    except Exception:
        return a if default_stage==2 else b

LEDGER_UNION = {
  'results/compute_audit.json': ['history','launches','samples'],
  'results/regime_state.json': ['history','transitions','launches'],
}
SNAP_TAKE_NEW = [
  'results/fundamental_b_layer_filter.json','results/futures_update_status.json',
  'results/lhb_update_status.json','results/token_usage.json','results/update_status.json',
  'results/_attrition_guard_scan.json','results/t35_open_fill_verify.json',
  'results/prospect_paper/_summary.json','results/prospect_promotion/_summary.json',
  'docs/daily_report/REPORT-2026-10-06.json','docs/live_usage/LIVE-2026-10-06.json',
  'docs/live_usage/LIVE-latest.json','results/paper/COMPOSITE-CE-01_paper.json',
  'results/paper/COMPOSITE-CE-02_paper.json','results/paper/DROUGHT-CE-01_paper.json',
  'results/paper/ENGULF-CE-01_paper.json','results/paper/NEEDLE-DE-01_paper.json',
  'results/paper/VOLATILITY-CE-01_paper.json','results/paper_export/export-2026-09-30.json',
  'results/paper_export/latest.json',
]
# r378 single-writer host=bm-a faces: origin side is authoritative (his machine owns the pen)
BMA_HOSTED = [
  'results/dashboard_status.json','results/daily_scorecard.json',
  'results/strategy_scorecard.json','results/scorecard_v1.json',
]
MD_TWIN = {  # md follows its json twin side
  'docs/daily_report/REPORT-2026-10-06.md':'docs/daily_report/REPORT-2026-10-06.json',
  'docs/live_usage/LIVE-2026-10-06.md':'docs/live_usage/LIVE-2026-10-06.json',
  'docs/live_usage/LIVE-latest.md':'docs/live_usage/LIVE-latest.json',
}

def union_ledger(path, keys):
    a, b = side(2,path), side(3,path)
    da, db = json.loads(a), json.loads(b)
    out = db if ts_of(db) >= ts_of(da) else da   # state fields: newer wins
    for k in keys:
        la, lb = da.get(k), db.get(k)
        if isinstance(la, list) and isinstance(lb, list):
            seen, merged = Counter(), []
            for row in la + lb:
                key = json.dumps(row, sort_keys=True, ensure_ascii=False)
                seen[key] += 1
                if seen[key] == 1: merged.append(row)
            out[k] = merged
    return json.dumps(out, ensure_ascii=False, indent=1).encode('utf-8')

def union_lines(path):
    a, b = side(2,path), side(3,path)
    la, lb = a.decode('utf-8').splitlines(), b.decode('utf-8').splitlines()
    seen, merged = Counter(), []
    for ln in la + lb:
        seen[ln] += 1
        if seen[ln] == 1: merged.append(ln)
    return ('\n'.join(merged) + ('\n' if (la and la[-1]=='') or (lb and lb[-1]=='') else '')).encode('utf-8')

def memory_union(path):
    a, b = side(2,path), side(3,path)
    la, lb = a.decode('utf-8').splitlines(), b.decode('utf-8').splitlines()
    ca, cb = Counter(la), Counter(lb)
    extra = []
    cb2 = Counter(lb)
    for ln in lb:                     # lines unique to B (ours) in order
        if cb2[ln] > ca.get(ln,0):
            extra.append(ln); cb2[ln]-=1
        else:
            ca[ln]-=1
    if not extra:
        return a
    # group contiguous blocks, insert each before its following anchor present in A
    blocks, cur = [], []
    for i, ln in enumerate(extra):
        cur.append((ln, i))
    # simpler: extra lines are contiguous appends in practice; find insert anchor per block
    out = list(la)
    # anchors: for each extra line, the next B-line after it that exists in A
    used = Counter()
    inserted = []
    # build B index
    for idx, ln in enumerate(extra):
        pass
    # walk B to locate block boundaries via positions in lb
    pos_in_b = {}
    ei = 0
    for j, ln in enumerate(lb):
        if ei < len(extra) and ln == extra[ei]:
            pos_in_b[ei] = j; ei += 1
    # group consecutive extra indices whose lb positions are adjacent
    groups, g = [], []
    prev_j = None
    for ei in sorted(pos_in_b):
        j = pos_in_b[ei]
        if prev_j is not None and j == prev_j + 1: g.append(ei)
        else:
            if g: groups.append(g)
            g = [ei]
        prev_j = j
    if g: groups.append(g)
    for grp in groups:
        first = grp[0]; j = pos_in_b[first]
        # anchor = next line in lb after the block that survives in A
        block_len = len(grp)
        anchor = None
        for k in range(j+block_len, len(lb)):
            if ca.get(lb[k],0) > 0:
                anchor = lb[k]; break
        block = [extra[x] for x in grp]
        if anchor is not None:
            try:
                at = out.index(anchor)
                out[at:at] = block
            except ValueError:
                out.extend(block)
        else:
            out.extend(block)
    return ('\n'.join(out) + ('\n' if la and la[-1]=='' else '')).encode('utf-8')

resolved = {}
resolved['CODELY.md'] = memory_union('CODELY.md')
resolved['results/x2_watch_log.jsonl'] = union_lines('results/x2_watch_log.jsonl')
for p, keys in LEDGER_UNION.items():
    resolved[p] = union_ledger(p, keys)
for p in SNAP_TAKE_NEW:
    resolved[p] = pick_new_by_ts(p)
for p in BMA_HOSTED:
    s = side(2,p) or side(3,p)
    resolved[p] = s
for p in SNAP_TAKE_NEW:
    resolved[p] = pick_new_by_ts(p)
for md, js in MD_TWIN.items():
    # md twin: pick same side as json twin decision (re-decide by ts on json, then take matching md side bytes)
    a, b = side(2,js), side(3,js)
    try:
        ta, tb = ts_of(json.loads(a)), ts_of(json.loads(b))
        win = 3 if tb > ta else 2
    except Exception:
        win = 2
    resolved[md] = side(win, md) or side(2, md)
# dashboard_status.js: js-wrapper-snapshot, single-writer host=bm-a -> take origin whole bytes
resolved['results/dashboard_status.js'] = side(2,'results/dashboard_status.js') or side(3,'results/dashboard_status.js')

report = {}
for p, data in resolved.items():
    if data is None:
        print('MISS', p); sys.exit(2)
    if p.endswith('.json'):
        try: json.loads(data.decode('utf-8'))
        except Exception as e:
            print('JSONFAIL', p, e); sys.exit(2)
    low = data.decode('utf-8', errors='replace')
    for marker in ('<<<<<<<','>>>>>>> '):
        if marker in low:
            print('MARKER', p); sys.exit(2)
    with open(p,'wb') as f:
        f.write(data)
    report[p] = len(data)
print(json.dumps({'resolved': sorted(report), 'bytes': sum(report.values())}))
