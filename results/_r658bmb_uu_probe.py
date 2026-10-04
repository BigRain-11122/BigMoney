import subprocess, json, os

def gv(rev, path):
    r = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True)
    return r.stdout if r.returncode == 0 else None

stopped = subprocess.run(['git', 'rev-parse', 'REBASE_HEAD'], capture_output=True).stdout.decode().strip()
head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True).stdout.decode().strip()
print('HEAD(onto/origin side):', head)
print('REBASE_HEAD(mine side):', stopped)

UU = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def jload(b):
    try:
        return json.loads(b.decode('utf-8'))
    except Exception:
        return None

for p in UU:
    a = gv(head, p)   # origin side
    b = gv(stopped, p)  # mine side
    ja, jb = jload(a) if a else None, jload(b) if b else None
    ta = (ja or {}).get('ts') or (ja or {}).get('generated') or (ja or {}).get('updated_at') if isinstance(ja, dict) else None
    tb = (jb or {}).get('ts') or (jb or {}).get('generated') or (jb or {}).get('updated_at') if isinstance(jb, dict) else None
    same = (a == b)
    print(f"{p}\n  origin_side ts={ta} mine_side ts={tb} bytes_equal={same} len_o={len(a) if a else 0} len_m={len(b) if b else 0}")
    if isinstance(ja, dict): print('  origin keys:', list(ja)[:10])
    if isinstance(jb, dict): print('  mine keys:', list(jb)[:10])
