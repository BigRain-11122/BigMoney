# r615 bm-b push-collision resolver (bigmoney-conflict-resolve skill canonical recipes)
# 19 UU: CODELY.md memory-union (prefix-assert + concat) | compute_audit + regime_state rolling-ledger union |
# rest = same-day idempotent regen snapshots -> take-origin (newer close, commit-time-order cede) incl. attrition scan.
import subprocess, json, sys

def blob(rev, path):
    return subprocess.run(['git', 'show', '%s:%s' % (rev, path)], capture_output=True).stdout

ours_rev, theirs_rev = 'HEAD', 'MERGE_HEAD'   # within an unfinished merge, sides are HEAD vs MERGE_HEAD

# --- 1) CODELY.md: memory-union, manual adjudication (prefix-identity failed on theirs = in-place edits) ---
# theirs in-place edits = bm-c r411 domain-pointer rescans + L56 bullet fix + MIGRATED entry removals
# (r619 -> pit-pool.md, r410 -> pit-protocol.md, zero-loss confirmed in their pointer-line reconciliation).
# ours = pure tail append of 3 r614 bm-b entries. Correct merge = theirs + our tail suffix.
p = 'CODELY.md'
base = blob(':1', p); ours = blob(':2', p); theirs = blob(':3', p)
assert base and ours and theirs, 'missing stage blobs for ' + p
assert ours.startswith(base), 'CODELY ours prefix-identity FAIL (in-place edit)'
suffix = ours[len(base):].lstrip(b'\r\n').decode('utf-8')
assert suffix.startswith('- [2026-10-03'), 'ours-suffix unexpected shape: %r' % suffix[:60]
body = theirs if theirs.endswith(b'\n') else theirs + b'\n'
merged = body + b'\n' + suffix.encode('utf-8')
if not merged.endswith(b'\n'):
    merged += b'\n'
open(p, 'wb').write(merged)
n_ours = len([l for l in suffix.splitlines() if l.strip()])
print('CODELY.md manual union: theirs(base-edited)=%dB + ours-tail %d entries -> %dB (bm-c migrated r619/r410 preserved in pit files per their reconciliation)' %
      (len(theirs), n_ours, len(merged)))

# --- 2) compute_audit.json: rolling-ledger union on history + take-new fields (r188/R208) ---
p = 'results/compute_audit.json'
o = json.loads(blob(':2', p)); t = json.loads(blob(':3', p))
h_o = o.get('history', []); h_t = t.get('history', [])
seen, union = set(), []
for row in h_o + h_t:
    key = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key)
        union.append(row)
res = dict(t)  # take-new snapshot fields = origin side (newer close)
res['history'] = union
open(p, 'w', encoding='utf-8', newline='').write(json.dumps(res, ensure_ascii=False, indent=1))
print('compute_audit: history |A|=%d |B|=%d -> union=%d (dedup identity=whole-row)' % (len(h_o), len(h_t), len(union)))

# --- 3) regime_state.json: rolling-ledger union on transitions/history + take-new state (R208) ---
p = 'results/regime_state.json'
o = json.loads(blob(':2', p)); t = json.loads(blob(':3', p))
res = dict(t)
for k in ('transitions', 'history'):
    a = o.get(k) or []; b = t.get(k) or []
    if isinstance(a, list) and isinstance(b, list):
        seen, union = set(), []
        for row in a + b:
            key = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if key not in seen:
                seen.add(key); union.append(row)
        res[k] = union
        print('regime_state[%s]: |A|=%d |B|=%d -> union=%d' % (k, len(a), len(b), len(union)))
open(p, 'w', encoding='utf-8', newline='').write(json.dumps(res, ensure_ascii=False, indent=1))

# --- 4) snapshot regen faces: take-origin whole bytes (newer close per commit-time-order) ---
snapshots = [
    'docs/daily_report/REPORT-2026-10-03.json', 'docs/daily_report/REPORT-2026-10-03.md',
    'docs/live_usage/LIVE-2026-10-03.json', 'docs/live_usage/LIVE-2026-10-03.md',
    'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
    'results/dashboard_status.js', 'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
    'results/lhb_update_status.json', 'results/scorecard_v1.json',
    'results/strategy_scorecard.json', 'results/token_usage.json', 'results/update_status.json',
    'results/_attrition_guard_scan.json',  # UNKNOWN->manual: per-run evidence snapshot, take-new (origin newer close)
]
for p in snapshots:
    b = blob(':3', p)
    open(p, 'wb').write(b)
    print('take-origin:', p, len(b), 'B')

# --- 5) parse-verify every resolved JSON before add (r185 law) ---
check = [x for x in snapshots if x.endswith('.json')] + ['results/compute_audit.json', 'results/regime_state.json']
for p in check:
    json.load(open(p, encoding='utf-8'))
print('parse-verify PASS: %d json files' % len(check))
print('RESOLVER DONE')
