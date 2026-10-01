import subprocess, re, sys

FILES = [
    'docs/daily_report/REPORT-2026-10-01.json',
    'docs/daily_report/REPORT-2026-10-01.md',
    'docs/live_usage/LIVE-2026-10-01.json',
    'docs/live_usage/LIVE-2026-10-01.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/compute_audit.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/regime_state.json',
    'results/token_usage.json',
    'results/update_status.json',
]

TS_RE = re.compile(r'20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?')

def stage(p, n):
    try:
        return subprocess.check_output(['git', 'show', ':%d:%s' % (n, p)])
    except Exception:
        return b''

def maxts(b):
    s = b.decode('utf-8', errors='replace')
    ts = TS_RE.findall(s)
    if not ts:
        return None
    return max(TS_RE.finditer(s), key=lambda m: m.group(0)).group(0)

for f in FILES:
    o = stage(f, 2)  # ours = origin side
    t = stage(f, 3)  # theirs = my commit side
    to, tt = maxts(o), maxts(t)
    if tt and (not to or tt >= to):
        side = 'theirs'
        subprocess.check_output(['git', 'checkout', '--theirs', f])
    else:
        side = 'ours'
        subprocess.check_output(['git', 'checkout', '--ours', f])
    print('%-52s origin_ts=%s mine_ts=%s -> %s' % (f, to, tt, side))
    subprocess.check_output(['git', 'add', f])
print('resolver done')
