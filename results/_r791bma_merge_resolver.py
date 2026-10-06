# r791 merge-window face resolver (r609/r611/r756/r782 laws: per-face ts newer-wins, host-ours for bm-a single-writer, union for CODELY append-only)
import subprocess, re, json, sys, datetime

def stage(rev, path):
    r = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode('utf-8', errors='replace')

TS_RE = re.compile(r'(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})(?:[.,]\d+)?(?:\+08:00|\+0800)?')

def max_ts(text):
    best = None
    for m in TS_RE.finditer(text):
        try:
            dt = datetime.datetime(int(m[1]), int(m[2]), int(m[3]), int(m[4]), int(m[5]), int(m[6]))
        except ValueError:
            continue
        if best is None or dt > best:
            best = dt
    return best

HOST_OURS = [
    'results/dashboard_status.json', 'results/dashboard_status.js',
    'results/strategy_scorecard.json', 'results/scorecard_v1.json',
]
TS_FACES = [
    'docs/daily_report/REPORT-2026-10-06.json', 'docs/daily_report/REPORT-2026-10-06.md',
    'docs/live_usage/LIVE-2026-10-06.json', 'docs/live_usage/LIVE-2026-10-06.md',
    'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json', 'results/compute_audit.json',
    'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
    'results/lhb_update_status.json', 'results/regime_state.json',
    'results/token_usage.json', 'results/update_status.json',
]

def resolve(path, mode):
    ours = stage(':2', path)
    theirs = stage(':3', path)
    if ours is None or theirs is None:
        return ('MISSING', None)
    if mode == 'ours':
        winner, side = ours, 'ours'
    elif mode == 'ts':
        ot, tt = max_ts(ours), max_ts(theirs)
        if ot is None or tt is None:
            winner, side = (ours if ot is not None else theirs), ('ours' if ot is not None else 'theirs')
        elif ot >= tt:
            winner, side = ours, 'ours'
        else:
            winner, side = theirs, 'theirs'
    elif mode == 'union':
        base = stage(':1', path)
        bl = base.splitlines() if base else []
        ol = ours.splitlines()
        tl = theirs.splitlines()
        # lines beyond base on each side (append-only ledger)
        def newlines(side_lines):
            out = []
            for l in side_lines:
                if l in bl and l not in out:
                    # skip base lines: first occurrence semantics — approximate: drop lines present in base
                    continue
                out.append(l)
            return out
        on = [l for l in ol if l not in bl]
        tn = [l for l in tl if l not in bl]
        winner = '\n'.join(bl + on + tn) + '\n'
        side = f'union(ours+{len(on)},theirs+{len(tn)})'
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(winner)
    return (side, max_ts(winner) if mode == 'ts' else None)

results = []
for p in HOST_OURS:
    results.append((p, 'ours', *resolve(p, 'ours')))
for p in TS_FACES:
    results.append((p, 'ts', *resolve(p, 'ts')))
results.append(('CODELY.md', 'union', *resolve('CODELY.md', 'union')))

for r in results:
    print(r)
