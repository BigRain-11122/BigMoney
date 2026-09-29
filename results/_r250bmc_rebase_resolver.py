# r250 bm-c: rebase conflict resolver v2 -- per-file ts later-yields (storm law r443/r446/dc4cb1679)
# ours(stage2)=origin incl bm-b orphan dead-tick sweep (witness ts 03:25:18); theirs(stage3)=r249-tail sweep (03:26-03:28)
# unions: compute_audit history by (ts,machine); token_usage machines. Clean-blob reconstruction per r452 law.
import io, sys, subprocess, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def blob(stage, path):
    return subprocess.run(['git', 'show', ':%d:%s' % (stage, path)], capture_output=True).stdout.decode('utf-8')

def best_ts(obj):
    for k in ('generated', 'ts', 'generated_at', 'updated', 'updated_at', 'asof', 'cutoff_ts', 'last_run'):
        v = obj.get(k) if isinstance(obj, dict) else None
        if isinstance(v, str) and len(v) >= 10:
            return v
    return None

def md_ts(text):
    m = re.findall(r'2026-09-30[ T]\d{2}:\d{2}:\d{2}', text)
    return max(m) if m else None

SIMPLE = [
    'docs/daily_report/REPORT-2026-09-30.json', 'docs/daily_report/REPORT-2026-09-30.md',
    'docs/live_usage/LIVE-2026-09-30.json', 'docs/live_usage/LIVE-2026-09-30.md',
    'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json', 'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json', 'results/lhb_update_status.json',
    'results/regime_state.json', 'results/update_status.json',
]
for p in SIMPLE:
    b2, b3 = blob(2, p), blob(3, p)
    if p.endswith('.json'):
        j2, j3 = json.loads(b2), json.loads(b3)
        t2, t3 = best_ts(j2), best_ts(j3)
    else:
        t2, t3 = md_ts(b2), md_ts(b3)
    pick, side = (b3, 'theirs(r249-tail)') if (t3 or '') >= (t2 or '') else (b2, 'ours(origin/bm-b)')
    if p.endswith('.json'):
        json.loads(pick)
    open(p, 'wb').write(pick.encode('utf-8'))
    print('%s: ours_ts=%s theirs_ts=%s -> %s' % (p, t2, t3, side))

# compute_audit.json: history union by (ts, machine); top-level = later ts side
o, t = json.loads(blob(2, 'results/compute_audit.json')), json.loads(blob(3, 'results/compute_audit.json'))
merged_hist = None
for key in ('history', 'runs', 'samples'):
    if isinstance(o.get(key), list) and isinstance(t.get(key), list):
        seen, merged = set(), []
        for rec in o[key] + t[key]:
            k = (rec.get('ts'), rec.get('machine'))
            if k in seen:
                continue
            seen.add(k)
            merged.append(rec)
        merged.sort(key=lambda r: str(r.get('ts')))
        merged_hist = (key, merged)
        break
base = o if (best_ts(o) or '') >= (best_ts(t) or '') else t
if merged_hist:
    base[merged_hist[0]] = merged_hist[1]
    print('compute_audit union %s: %d entries (base=%s)' % (merged_hist[0], len(merged_hist[1]), 'ours' if base is o else 'theirs'))
else:
    print('compute_audit: no history list -- keys %s' % list(o.keys())[:10])
open('results/compute_audit.json', 'wb').write(json.dumps(base, ensure_ascii=False, indent=2).encode('utf-8'))

# token_usage.json: machines union, top-level fields from later side
o, t = json.loads(blob(2, 'results/token_usage.json')), json.loads(blob(3, 'results/token_usage.json'))
base = o if (best_ts(o) or '') >= (best_ts(t) or '') else t
other = t if base is o else o
if isinstance(base.get('machines'), dict) and isinstance(other.get('machines'), dict):
    for k, v in other['machines'].items():
        base['machines'].setdefault(k, v)
    print('token_usage machines union: %d machines' % len(base['machines']))
for k, v in other.items():
    if k != 'machines' and k not in base:
        base[k] = v
open('results/token_usage.json', 'wb').write(json.dumps(base, ensure_ascii=False, indent=2).encode('utf-8'))
print('RESOLVER DONE')
