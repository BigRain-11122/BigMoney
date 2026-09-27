"""r82 bm-c rebase-collision resolver vs bm-b r324+addendum (same-window S6 mirror, 15 UU).

Disciplines (bigmoney-conflict-resolve canon):
- r323 rebase-inversion: during rebase ours(:2)=origin(bm-b), theirs(:3)=replayed commit(bm-c r82);
  stage identity VERIFIED by byte-match against original pre-rebase commit BEFORE any take-side call.
- r322 union-collision content-eq: composite key (ts,machine) for ledger union; identical rows dedupe.
- r319 key-existence probe before compare; D-20260927-09 deep-scan nested ts (top-level miss != absent).
- R209 js-wrapper: whole-bytes take-side, never re-dump.
- daily REPORT twins: same-side take-newer (json+md from one side).
- derive faces: deep-strip runtime metadata, compare, take-newer, report divergence honestly.
- r245 cap50 for autofill launches (post-auto-merge enforcement).
All outputs parse-verified; marker scan zero; zero-loss assertions.
"""
import json
import re
import subprocess
import sys

ORIG = '20491d9e'  # bm-c r82 pre-rebase commit
ME, THEM = 'bm-c r82 (mine)', 'bm-b r324+addendum (origin)'


def blob(rev, path):
    b = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True).stdout
    assert b, 'empty blob %s:%s' % (rev, path)
    return b


def jload(b):
    return json.loads(b.decode('utf-8-sig'))


log = []


def note(msg):
    log.append(msg)
    print(msg)


UU = [
    'docs/daily_report/REPORT-2026-09-27.json', 'docs/daily_report/REPORT-2026-09-27.md',
    'results/compute_audit.json', 'results/dashboard_status.js', 'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
    'results/heat_update_status.json', 'results/lhb_update_status.json',
    'results/prospect_promotion/_summary.json', 'results/regime_state.json',
    'results/scorecard_v1.json', 'results/strategy_scorecard.json',
    'results/token_usage.json', 'results/update_status.json',
]

# --- step 0: rebase-inversion stage identity (byte-match :3 vs original commit) ---
for p in UU:
    assert blob(':3', p) == blob(ORIG, p), 'STAGE INVERSION SUSPECT at %s' % p
note('stage identity: :3 == %s original for all 15 UU (rebase-inversion verified)' % ORIG)

# --- helpers ---


def deep_ts(obj, _depth=0):
    """DEEP-SCAN any ts-ish leaf; return max ISO-ish string found (D-20260927-09)."""
    best = None
    if _depth > 6:
        return best
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and re.fullmatch(r'20\d\d-\d\d-\d\d[T ].*', v):
                if best is None or v > best:
                    best = v
            r = deep_ts(v, _depth + 1)
            if r and (best is None or r > best):
                best = r
    elif isinstance(obj, list):
        for v in obj:
            r = deep_ts(v, _depth + 1)
            if r and (best is None or r > best):
                best = r
    elif isinstance(obj, str) and re.fullmatch(r'20\d\d-\d\d-\d\d[T ].*', obj):
        best = obj
    return best


def write_bytes(path, b):
    with open(path, 'wb') as f:
        f.write(b)


def take_snapshot(path, ts_hint=None):
    b2, b3 = blob(':2', path), blob(':3', path)
    t2, t3 = ts_hint or deep_ts(jload(b2)), ts_hint or deep_ts(jload(b3))
    side = 3 if (t3 or '') >= (t2 or '') else 2
    write_bytes(path, b3 if side == 3 else b2)
    note('%-46s snapshot take-%s (%s ts %s vs %s)' % (path, 'mine' if side == 3 else 'origin',
                                                      'mine' if side == 3 else 'origin', t3, t2))
    return side


def union_ledger(path, key_fields, list_key='history'):
    b2, b3 = blob(':2', path), blob(':3', path)
    a2, a3 = jload(b2), jload(b3)
    h2, h3 = a2[list_key], a3[list_key]
    merged, seen = [], {}
    for row in h2 + h3:
        k = tuple(row.get(f) for f in key_fields)
        if k in seen:
            assert seen[k] == row, 'same-key content-diff at %s %s (needs composite adjudication)' % (path, k)
            continue
        seen[k] = row
        merged.append(row)
    overlap = len(h2) + len(h3) - len(merged)
    merged.sort(key=lambda r: tuple(str(x) for x in (r.get(f) for f in key_fields)))
    t2, t3 = deep_ts(a2), deep_ts(a3)
    base = a3 if (t3 or '') >= (t2 or '') else a2
    out = dict(base)
    out[list_key] = merged
    s = json.dumps(out, ensure_ascii=False, indent=1) + '\n'
    write_bytes(path, s.encode('utf-8'))
    note('%-46s union %d+%d -> %d (overlap %d dedup, zero-loss) | base take-%s (ts %s vs %s)'
         % (path, len(h2), len(h3), len(merged), overlap, 'mine' if base is a3 else 'origin', t3, t2))
    return out


def deep_strip(obj, drop=('generated', 'elapsed_sec', 'generated_at')):
    if isinstance(obj, dict):
        return {k: deep_strip(v, drop) for k, v in obj.items() if k not in drop}
    if isinstance(obj, list):
        return [deep_strip(v, drop) for v in obj]
    return obj


def resolve_derive(path):
    b2, b3 = blob(':2', path), blob(':3', path)
    a2, a3 = jload(b2), jload(b3)
    t2, t3 = deep_ts(a2), deep_ts(a3)
    side = 3 if (t3 or '') >= (t2 or '') else 2
    eq = deep_strip(a2) == deep_strip(a3)
    write_bytes(path, b3 if side == 3 else b2)
    note('%-46s derive take-%s (%s ts %s vs %s) | deep-strip runtime-meta eq=%s%s'
         % (path, 'mine' if side == 3 else 'origin', 'mine' if side == 3 else 'origin', t3, t2, eq,
            '' if eq else ' <-- DIVERGENCE honest: differing paths kept in take-newer side'))


# --- 1) rolling-ledger unions ---
union_ledger('results/compute_audit.json', ('ts', 'machine'))
union_ledger('results/regime_state.json', ('asof',))

# --- 2) js-wrapper snapshot pair: same-side by inner generated_at ---
js2, js3 = blob(':2', 'results/dashboard_status.js'), blob(':3', 'results/dashboard_status.js')
g2 = (re.search(rb'"generated_at":\s*"([^"]+)"', js2) or re.search(rb'"ts":\s*"([^"]+)"', js2))
g3 = (re.search(rb'"generated_at":\s*"([^"]+)"', js3) or re.search(rb'"ts":\s*"([^"]+)"', js3))
t2 = g2.group(1).decode() if g2 else ''
t3 = g3.group(1).decode() if g3 else ''
side = 3 if t3 >= t2 else 2
write_bytes('results/dashboard_status.js', js3 if side == 3 else js2)
take_snapshot('results/dashboard_status.json', ts_hint=(t3 if side == 3 else t2))
note('dashboard js+json same-side take-%s (generated_at %s vs %s, wrapper preserved whole-bytes)'
     % ('mine' if side == 3 else 'origin', t3, t2))

# --- 3) plain snapshots: take-newer by deep-scanned ts ---
for p in ['results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
          'results/heat_update_status.json', 'results/lhb_update_status.json',
          'results/token_usage.json', 'results/update_status.json']:
    take_snapshot(p)

# --- 4) daily REPORT twins: same-side take-newer by json ts ---
rj2, rj3 = jload(blob(':2', 'docs/daily_report/REPORT-2026-09-27.json')), \
    jload(blob(':3', 'docs/daily_report/REPORT-2026-09-27.json'))
t2, t3 = deep_ts(rj2), deep_ts(rj3)
side = 3 if (t3 or '') >= (t2 or '') else 2
for p in ['docs/daily_report/REPORT-2026-09-27.json', 'docs/daily_report/REPORT-2026-09-27.md']:
    write_bytes(p, blob(':%d' % side, p))
note('REPORT-2026-09-27 json+md same-side take-%s (ts %s vs %s, same-day idempotent twins)'
     % ('mine' if side == 3 else 'origin', t3, t2))

# --- 5) derive faces ---
resolve_derive('results/scorecard_v1.json')
resolve_derive('results/strategy_scorecard.json')
resolve_derive('results/prospect_promotion/_summary.json')

# --- 6) post-verify: strict parse + marker scan + autofill cap50 enforcement ---
for p in UU:
    raw = open(p, 'rb').read()
    if p.endswith('.js'):
        assert raw.lstrip().startswith(b'window.') and b'<<<<<<<' not in raw, 'js wrapper/marker %s' % p
    else:
        jload(raw)
        for m in (b'<<<<<<<', b'>>>>>>>', b'^======='.replace(b'^', b'\n=======')):
            assert m not in raw, 'marker in %s' % p

af = jload(open('results/autofill_state.json', 'rb').read())
L = af.get('launches', [])
keys = [(l.get('ts'), l.get('machine'), l.get('entry'), l.get('shard'), l.get('pid')) for l in L]
if len(keys) != len(set(keys)) or len(L) > 50:
    uniq = {}
    for l in L:
        uniq[(l.get('ts'), l.get('machine'), l.get('entry'), l.get('shard'), l.get('pid'))] = l
    keep = sorted(uniq.values(), key=lambda l: str(l.get('ts')))[-50:]
    keep.sort(key=lambda l: str(l.get('ts')))
    af['launches'] = keep
    open('results/autofill_state.json', 'wb').write(
        (json.dumps(af, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    note('autofill_state post-merge enforcement: %d -> %d unique cap50 asc (r245)' % (len(L), len(keep)))
else:
    note('autofill_state auto-merge parse-verified: %d launches, keys unique, <=cap50' % len(L))

# CODELY.md + own round report marker scan (auto-merged faces)
for p in ['CODELY.md', 'logs/iteration-loop/round_reports-bm-c.md', 'research/memory-archive/202609.md']:
    raw = open(p, 'rb').read()
    assert b'<<<<<<<' not in raw and b'>>>>>>>' not in raw, 'marker in %s' % p
note('CODELY.md + round_reports-bm-c.md + archive marker-scan clean')

print('\nRESOLVED %d files; see log above' % len(UU))
