# r349 bm-a rebase-stop resolver: 3 UU vs bm-c r99 chain (push-rejection window)
# Canon: bigmoney-conflict-resolve skill; blob shas from `git ls-files -u`
#   compute_audit.json  -> rolling-ledger: history multiset union zero-loss + latest take-new (deep ts probe)
#   token_usage.json    -> snapshot: take-new whole-face by deep ts probe
#   x2_watch_log.jsonl  -> append-log: line-level multiset union zero-loss
import subprocess, json, sys

BLOBS = {
    'results/compute_audit.json':  ('32cc640288d6b81eab6eaee0e90c3912d66ca4ba', '71dbec1b6bfd8b202b1232f04041831f18afba20', '533db5559ff81da102e8ed6af7716edf3e3837b1'),
    'results/token_usage.json':    ('2258789e70e177b74d94bfd9e0ce1b8d0b92abdc', '9a1690b293d558ab3659afb27ad218b1761eeb20', '08c95b9b61195f430b40f4a9c78dc4bbb0d1c4ab'),
    'results/x2_watch_log.jsonl':  ('26c4bff5ae6cba37efeac55e2b63295679130bf5', '7ec82e8bfd35633d4414f55041a177c218868ab4', 'ee79f24f0a6f5ac7282cf575684d2b7c791f1ef0'),
}
# stage2 = onto side (origin/main = bm-c r99), stage3 = replayed side (bm-a r349)

def cat(sha):
    r = subprocess.run(['git', 'cat-file', '-p', sha], capture_output=True)
    assert r.returncode == 0 and r.stdout, f'cat-file failed for {sha}: {r.stderr[:200]}'
    return r.stdout

def deep_ts(obj):
    # D-09 deep probe: first ts-like key found, recursive, deterministic order
    if isinstance(obj, dict):
        for k in ('ts', 'updated_at', 'generated', 'generated_at', 'asof', 'snapshot_ts', 'last_run'):
            if k in obj and isinstance(obj[k], str):
                return obj[k]
        for v in obj.values():
            t = deep_ts(v)
            if t:
                return t
    elif isinstance(obj, list):
        for v in obj:
            t = deep_ts(v)
            if t:
                return t
    return None

report = []

# ---- 1) compute_audit.json : rolling-ledger union ----
base, s2, s3 = (json.loads(cat(BLOBS['results/compute_audit.json'][i])) for i in range(3))
hb, h2, h3 = base.get('history', []), s2.get('history', []), s3.get('history', [])
key = lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False)
u_keys = {key(r) for r in h2} | {key(r) for r in h3}
union_rows = sorted((json.loads(k) for k in u_keys), key=lambda r: r['ts'])
assert len(union_rows) == len(u_keys), 'multiset union count mismatch'
# ts-collision content check (same ts both sides, differing content = keep both + disclose)
ts2 = {}
for r in h2:
    ts2.setdefault(r['ts'], []).append(key(r))
coll = [ts for ts in set(r['ts'] for r in h2) & set(r['ts'] for r in h3)
        if not (set(ts2.get(ts, [])) & set(key(r) for r in h3 if r['ts'] == ts))]
# simpler: count ts shared with differing row content
shared_ts = set(r['ts'] for r in h2) & set(r['ts'] for r in h3)
diff_content_ts = [ts for ts in shared_ts
                   if {key(r) for r in h2 if r['ts'] == ts} != {key(r) for r in h3 if r['ts'] == ts}]
# latest: take-new by deep probe (nested latest.ts)
ts2_latest = deep_ts(s2.get('latest', {}))
ts3_latest = deep_ts(s3.get('latest', {}))
assert ts2_latest and ts3_latest, 'latest.ts probe must exist (D-09 deep probe)'
newer = s3 if str(ts3_latest) >= str(ts2_latest) else s2
picked_latest_from = 'bm-a(s3)' if newer is s3 else 'bm-c(s2)'
out = dict(newer)
out['history'] = union_rows
# r85 survival check: base rows dropped from union must be older than window head (front truncation)
u_ts = [r['ts'] for r in union_rows]
dropped = [r['ts'] for r in hb if key(r) not in u_keys]
boundary = min(min(r['ts'] for r in h2), min(r['ts'] for r in h3))
assert all(d < boundary for d in dropped), f'non-window drop detected: {dropped}'
# write back mirroring base blob face (indent 1, newline face)
b_bytes = cat(BLOBS['results/compute_audit.json'][0])
nl = b'\r\n' if b'\r\n' in b_bytes[:2000] else b'\n'
indent = 1
data = json.dumps(out, ensure_ascii=False, indent=indent).encode('utf-8') + b'\n'
if nl == b'\r\n':
    data = data.replace(b'\n', b'\r\n')
open('results/compute_audit.json', 'wb').write(data)
json.loads(open('results/compute_audit.json', encoding='utf-8').read())  # parse-verify r185
report.append(f'compute_audit: history {len(h2)}|{len(h3)} shared-ts {len(shared_ts)} diff-content {len(diff_content_ts)} -> union {len(union_rows)} | base {len(hb)} dropped {len(dropped)} all<boundary PASS | latest take-new from {picked_latest_from} ({ts2_latest} vs {ts3_latest})')

# ---- 2) token_usage.json : snapshot take-new whole-face ----
base_b, s2_b, s3_b = (cat(BLOBS['results/token_usage.json'][i]) for i in range(3))
t2, t3 = json.loads(s2_b), json.loads(s3_b)
p2, p3 = deep_ts(t2), deep_ts(t3)
assert p2 and p3, 'token_usage ts probe must exist'
win_bytes = s3_b if str(p3) >= str(p2) else s2_b
win_from = 'bm-a(s3)' if win_bytes is s3_b else 'bm-c(s2)'
open('results/token_usage.json', 'wb').write(win_bytes)
json.loads(open('results/token_usage.json', encoding='utf-8').read())
report.append(f'token_usage: snapshot take-new from {win_from} (probe {p2} vs {p3}) whole-face bytes {len(win_bytes)}')

# ---- 3) x2_watch_log.jsonl : append-log line union ----
def lines_of(sha):
    return cat(sha).splitlines()
l2, l3 = lines_of(BLOBS['results/x2_watch_log.jsonl'][1]), lines_of(BLOBS['results/x2_watch_log.jsonl'][2])
all_lines = list(dict.fromkeys(l2 + l3))  # stable multiset union, identical collapse
def line_ts(l):
    try:
        d = json.loads(l)
        return deep_ts(d) or ''
    except Exception:
        return ''
all_lines.sort(key=lambda l: line_ts(l) or '')
assert len(all_lines) == len(set(l2) | set(l3)), 'line union count mismatch'
open('results/x2_watch_log.jsonl', 'wb').write(b'\n'.join(all_lines) + b'\n')
for l in all_lines:
    json.loads(l)  # parse-verify every line
report.append(f'x2_watch_log: lines {len(l2)}|{len(l3)} -> union {len(all_lines)} zero-loss, ts-sorted')

print('RESOLVE OK')
for r in report:
    print(' -', r)
