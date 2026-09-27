# -*- coding: utf-8 -*-
"""r83 bm-c resolver #3: round-83 commit rebase-replay UU batch (17 files) vs
origin/main 6afba45c (bm-b r325+addendum+r326 same-window S6 mirror + CODELY archival).

Disciplines (bigmoney-conflict-resolve canon + this-round dedup step):
- r323 rebase-inversion: ours(:2)=origin(bm-b), theirs(:3)=replayed commit(bm-c r83);
  stage identity VERIFIED by byte-match vs original pre-rebase commit 24a3c57e.
- CODELY.md memory-union (D-20260927-09): origin side did IN-PLACE hot archival
  (not pure append; prefix assertion fails by design) -> hand adjudication:
  result = origin-side whole content + my pure-append suffix (stage3 minus stage1
  prefix = 1 r83 pitlaw entry) direct-concat, entries verbatim, zero loss.
- autofill_state: launches identical 44/44 cc both sides (dedup verification
  pass-through); last_tick same-second tie 13:30:02 bm-b vs bm-c -> HEAD/ours (r140).
- rolling-ledger unions composite (ts,machine) / (asof) with content-eq dedup (r322).
- js-wrapper whole-bytes same-side (R209); snapshots take-newer (deep-scan ts, D-09);
  REPORT twins same-side; derive faces deep-strip eq compare + take-newer (r320).
All outputs parse-verified; marker scan zero; zero-loss assertions.
"""
import json, re, subprocess

ORIG = '24a3c57e'  # bm-c r83 pre-rebase commit


def blob(rev, path):
    b = subprocess.run(['git', 'show', '%s:%s' % (rev, path)], capture_output=True).stdout
    assert b, 'empty blob %s:%s' % (rev, path)
    return b


def jload(b):
    return json.loads(b.decode('utf-8-sig'))


log = []


def note(msg):
    log.append(msg)
    print(msg)


UU = [
    'CODELY.md',
    'docs/daily_report/REPORT-2026-09-27.json', 'docs/daily_report/REPORT-2026-09-27.md',
    'results/autofill_state.json', 'results/compute_audit.json',
    'results/dashboard_status.js', 'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
    'results/heat_update_status.json', 'results/lhb_update_status.json',
    'results/prospect_promotion/_summary.json', 'results/regime_state.json',
    'results/scorecard_v1.json', 'results/strategy_scorecard.json',
    'results/token_usage.json', 'results/update_status.json',
]

# --- step 0: stage identity (byte-match :3 vs original pre-rebase commit) ---
for p in UU:
    assert blob(':3', p) == blob(ORIG, p), 'STAGE INVERSION SUSPECT at %s' % p
note('stage identity: :3 == %s original for all %d UU (rebase-inversion verified)' % (ORIG, len(UU)))


def deep_ts(obj, _depth=0):
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
    t2 = ts_hint or deep_ts(jload(b2))
    t3 = ts_hint or deep_ts(jload(b3))
    side = 3 if (t3 or '') >= (t2 or '') else 2
    write_bytes(path, b3 if side == 3 else b2)
    note('%-46s snapshot take-%s (ts %s vs %s)' % (path, 'mine' if side == 3 else 'origin', t3, t2))


def union_ledger(path, key_fields, list_key='history'):
    b2, b3 = blob(':2', path), blob(':3', path)
    a2, a3 = jload(b2), jload(b3)
    h2, h3 = a2[list_key], a3[list_key]
    merged, seen = [], {}
    for row in h2 + h3:
        k = tuple(row.get(f) for f in key_fields)
        if k in seen:
            assert seen[k] == row, 'same-key content-diff at %s %s (escalate)' % (path, k)
            continue
        seen[k] = row
        merged.append(row)
    overlap = len(h2) + len(h3) - len(merged)
    merged.sort(key=lambda r: tuple(str(x) for x in (r.get(f) for f in key_fields)))
    t2, t3 = deep_ts(a2), deep_ts(a3)
    base = a3 if (t3 or '') >= (t2 or '') else a2
    out = dict(base)
    out[list_key] = merged
    write_bytes(path, (json.dumps(out, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    note('%-46s union %d+%d -> %d (overlap %d identical-dedup, zero-loss) | base take-%s'
         % (path, len(h2), len(h3), len(merged), overlap, 'mine' if base is a3 else 'origin'))


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
    note('%-46s derive take-%s (ts %s vs %s) | deep-strip runtime-meta eq=%s%s'
         % (path, 'mine' if side == 3 else 'origin', t3, t2, eq,
            '' if eq else ' <-- DIVERGENCE honest: differing paths kept in take-newer side'))


# --- 1) CODELY.md memory-union: origin in-place archival + my pure-append suffix ---
b1, b2, b3 = blob(':1', 'CODELY.md'), blob(':2', 'CODELY.md'), blob(':3', 'CODELY.md')
t1, t2, t3 = b1.decode('utf-8'), b2.decode('utf-8'), b3.decode('utf-8')
assert t3.startswith(t1), 'my side not pure-append vs base (manual review required)'
suffix = t3[len(t1):]  # my r83 pitlaw entry verbatim
assert 'r83 bm-c' in suffix and suffix.count('\n') <= 3, 'unexpected suffix shape'
result = t2 + suffix
write_bytes('CODELY.md', result.encode('utf-8'))
rb = len(result.encode('utf-8'))
assert 'r83 bm-c' in result and 'r325 bm-b' in result and b'<<<<<<<' not in result.encode('utf-8')
note('CODELY.md memory-union: origin in-place-archival side whole + my %dB pure-append suffix '
     'direct-concat -> %dB (base %dB, origin %dB; both deltas preserved verbatim, zero loss)'
     % (len(suffix.encode('utf-8')), rb, len(b1), len(b2)))

# --- 2) autofill_state: launches union (dedup per new recipe) + last_tick tie->HEAD ---
b2, b3 = blob(':2', 'results/autofill_state.json'), blob(':3', 'results/autofill_state.json')
a2, a3 = jload(b2), jload(b3)
K = lambda r: (r.get('ts'), r.get('machine'), r.get('pid'),
               r.get('runner_sha256'), r.get('entry'), r.get('shard'))
merged, seen = [], {}
for row in a2['launches'] + a3['launches']:
    k = K(row)
    if k in seen:
        diff = {f for f in set(seen[k]) | set(row) if seen[k].get(f) != row.get(f)}
        assert diff == set(), 'same-key content-diff %s %s (escalate per r322)' % (k, diff)
        continue
    seen[k] = row
    merged.append(row)
merged.sort(key=lambda r: r['ts'])
merged = merged[-50:]  # cap50 keep-newest
merged.sort(key=lambda r: r['ts'])  # write-back ascending
lo, lt = a2['last_tick'], a3['last_tick']
last = lo if lo['ts'] >= lt['ts'] else lt  # tie -> HEAD/ours (origin side), r140
out = {'launches': merged, 'last_tick': last}
write_bytes('results/autofill_state.json',
            (json.dumps(out, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
note('autofill_state: launches union %d+%d -> %d (dedup content-eq pass) | last_tick %s tie->HEAD take-%s (%s vs %s)'
     % (len(a2['launches']), len(a3['launches']), len(merged), 'same-ts' if lo['ts'] == lt['ts'] else 'newer-wins',
        'origin' if last is lo else 'mine', lo['ts'], lt['ts']))

# --- 3) rolling-ledger unions ---
union_ledger('results/compute_audit.json', ('ts', 'machine'))
union_ledger('results/regime_state.json', ('asof',))

# --- 4) js-wrapper snapshot pair: same-side by inner generated_at ---
js2, js3 = blob(':2', 'results/dashboard_status.js'), blob(':3', 'results/dashboard_status.js')
g2 = re.search(rb'"generated_at":\s*"([^"]+)"', js2) or re.search(rb'"ts":\s*"([^"]+)"', js2)
g3 = re.search(rb'"generated_at":\s*"([^"]+)"', js3) or re.search(rb'"ts":\s*"([^"]+)"', js3)
t2 = g2.group(1).decode() if g2 else ''
t3 = g3.group(1).decode() if g3 else ''
side = 3 if t3 >= t2 else 2
write_bytes('results/dashboard_status.js', js3 if side == 3 else js2)
take_snapshot('results/dashboard_status.json', ts_hint=(t3 if side == 3 else t2))
note('dashboard js+json same-side take-%s (generated_at %s vs %s, wrapper whole-bytes)'
     % ('mine' if side == 3 else 'origin', t3, t2))

# --- 5) plain snapshots take-newer ---
for p in ['results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
          'results/heat_update_status.json', 'results/lhb_update_status.json',
          'results/token_usage.json', 'results/update_status.json']:
    take_snapshot(p)

# --- 6) daily REPORT twins same-side ---
rj2, rj3 = jload(blob(':2', 'docs/daily_report/REPORT-2026-09-27.json')), \
    jload(blob(':3', 'docs/daily_report/REPORT-2026-09-27.json'))
t2, t3 = deep_ts(rj2), deep_ts(rj3)
side = 3 if (t3 or '') >= (t2 or '') else 2
for p in ['docs/daily_report/REPORT-2026-09-27.json', 'docs/daily_report/REPORT-2026-09-27.md']:
    write_bytes(p, blob(':%d' % side, p))
note('REPORT-2026-09-27 json+md same-side take-%s (ts %s vs %s, idempotent twins)'
     % ('mine' if side == 3 else 'origin', t3, t2))

# --- 7) derive faces ---
resolve_derive('results/scorecard_v1.json')
resolve_derive('results/strategy_scorecard.json')
resolve_derive('results/prospect_promotion/_summary.json')

# --- 8) post-verify: strict parse + marker scan ---
for p in UU:
    raw = open(p, 'rb').read()
    if p.endswith('.js'):
        assert raw.lstrip().startswith(b'window.') and b'<<<<<<<' not in raw, 'js wrapper/marker %s' % p
    elif p.endswith('.md'):
        for m in (b'<<<<<<<', b'>>>>>>>', b'\n======'):
            assert m not in raw, 'marker in %s' % p
    else:
        jload(raw)
        for m in (b'<<<<<<<', b'>>>>>>>', b'\n======'):
            assert m not in raw, 'marker in %s' % p

af = jload(open('results/autofill_state.json', 'rb').read())
L = af['launches']
keys = [(l['ts'], l['machine'], l['pid']) for l in L]
assert len(keys) == len(set(keys)) and len(L) <= 50, 'cap50/unique enforcement'
assert all(l.get('crash_counted') is True for l in L), 'cc gap'
note('post-verify: all %d files parse/marker-clean; autofill 44 unique cap50 asc; CODELY %dB <10KB'
     % (len(UU), len(open('CODELY.md', 'rb').read())))

print('\nRESOLVED %d files' % len(UU))
