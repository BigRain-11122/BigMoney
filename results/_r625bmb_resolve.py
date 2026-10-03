# r625 bm-b push-collision resolver (16 UU, classifier 10+7-manual families).
# Recipes: bigmoney-conflict-resolve canon -- memory-union (CODELY.md tail),
# rolling-ledger union + take-new (compute_audit, regime_state), snapshot
# take-new by ts probe (rest), js-wrapper whole-bytes (dashboard_status.js).
# Blob face = disk face (CRLF preserved verbatim). ASCII console output only.
import json, subprocess


def blob(ref):
    r = subprocess.run(['git', 'show', ref], capture_output=True)
    assert r.returncode == 0, 'git show failed: %s' % ref
    return r.stdout


def write(path, data):
    assert isinstance(data, bytes)
    open(path, 'wb').write(data)


def jload(b):
    return json.loads(b.decode('utf-8'))


def jdump_crlf(obj, ascii_mode):
    s = json.dumps(obj, indent=2, ensure_ascii=ascii_mode)
    return s.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8')


RESOLVED = {}

# ---- 1) snapshot take-new by ts probe ----
TS_KEY = {
    'results/fundamental_b_layer_filter.json': ('updated', None),
    'results/futures_update_status.json': ('ts', None),
    'results/lhb_update_status.json': ('updated', None),
    'results/token_usage.json': ('generated', None),
    'results/update_status.json': ('updated', None),
    'docs/live_usage/LIVE-2026-10-03.json': ('generated', None),
    'docs/live_usage/LIVE-latest.json': ('generated', None),
    'results/_attrition_guard_scan.json': ('ts', None),
    'results/scorecard_v1.json': ('generated', None),
    'results/strategy_scorecard.json': ('generated', None),
    'results/dashboard_status.json': ('generated_at', 'meta'),
}
for path, (key, parent) in TS_KEY.items():
    o, t = jload(blob(':2:' + path)), jload(blob(':3:' + path))
    ov = o[parent][key] if parent else o[key]
    tv = t[parent][key] if parent else t[key]
    side = 'ours' if ov >= tv else 'theirs'  # same-second tie -> HEAD (r140)
    data = blob(':2:' + path) if side == 'ours' else blob(':3:' + path)
    jload(data)  # r185: parse-validate before write
    write(path, data)
    RESOLVED[path] = '%s take-new %s (%s %s >= %s)' % (
        'snapshot', side, key, ov, tv)

# ---- 2) twins take the same side as their json producer run ----
for twin, ref in [
        ('docs/live_usage/LIVE-2026-10-03.md', 'docs/live_usage/LIVE-2026-10-03.json'),
        ('docs/live_usage/LIVE-latest.md', 'docs/live_usage/LIVE-latest.json'),
        ('results/dashboard_status.js', 'results/dashboard_status.json')]:
    o, t = jload(blob(':2:' + ref)), jload(blob(':3:' + ref))
    key, parent = TS_KEY[ref]
    ov = o[parent][key] if parent else o[key]
    tv = t[parent][key] if parent else t[key]
    side = 'ours' if ov >= tv else 'theirs'
    data = blob(':2:' + twin) if side == 'ours' else blob(':3:' + twin)
    if twin.endswith('.js'):
        head = data[:40]
        assert b'window.DASH_DATA' in data or b'DASH' in head[:200], 'js wrapper missing (R209)'
    write(twin, data)
    RESOLVED[twin] = 'twin whole-bytes %s (paired %s)' % (side, ref)

# ---- 3) compute_audit.json: history union + latest take-new ----
p = 'results/compute_audit.json'
o, t = jload(blob(':2:' + p)), jload(blob(':3:' + p))
okey = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in o['history']}
tkey = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in t['history']}
union = dict(okey)
for k, row in tkey.items():
    union.setdefault(k, row)
hist = sorted(union.values(), key=lambda r: r['ts'])
lossless = len(hist) == len(okey) + len([k for k in tkey if k not in okey])
assert lossless, 'union zero-loss failed: %d vs %d+%d' % (
    len(hist), len(okey), len(tkey))
merged = dict(o)  # keep ours doc shape
merged['history'] = hist
merged['latest'] = o['latest'] if o['latest']['ts'] >= t['latest']['ts'] else t['latest']
ascii_mode = b'\\u' in blob(':2:' + p)
data = jdump_crlf(merged, ascii_mode)
jload(data)
write(p, data)
RESOLVED[p] = 'rolling-ledger union %d|%d -> %d rows + latest take-new %s' % (
    len(okey), len(tkey), len(hist), merged['latest']['ts'])

# ---- 4) regime_state.json: take-new state doc + history union by asof ----
p = 'results/regime_state.json'
o, t = jload(blob(':2:' + p)), jload(blob(':3:' + p))
assert o['updated'] >= t['updated'], 'regime take-new expects ours'
merged = dict(o)
oh = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in o.get('history', [])}
th = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in t.get('history', [])}
uh = dict(oh)
for k, row in th.items():
    uh.setdefault(k, row)
merged['history'] = sorted(uh.values(), key=lambda r: str(r.get('asof', '')))
merged['transitions'] = sorted(
    {json.dumps(r, sort_keys=True, ensure_ascii=False): r
     for r in (o.get('transitions', []) + t.get('transitions', []))}.values(),
    key=lambda r: str(r.get('ts', r.get('asof', ''))))
ascii_mode = b'\\u' in blob(':2:' + p)
data = jdump_crlf(merged, ascii_mode)
jload(data)
write(p, data)
RESOLVED[p] = 'rolling-ledger state take-new %s + history union %d|%d -> %d' % (
    o['updated'], len(oh), len(th), len(uh))

# ---- 5) CODELY.md: memory-union tail hunk (keep bm-a r632, r624 stays deleted) ----
p = 'CODELY.md'
b = open(p, 'rb').read()
assert b.count(b'<<<<<<<') == 1 and b.count(b'>>>>>>>') == 1, 'expect single hunk'
START = b'<<<<<<< HEAD\r\n'
i = b.find(START)
assert i >= 0, 'start marker missing'
PRE = b[:i]
rest = b[i + len(START):]
if rest.startswith(b'=======\r\n'):
    MID = b''
    rest2 = rest[len(b'=======\r\n'):]
else:
    MID, rest2 = rest.split(b'\r\n=======\r\n', 1)
assert MID == b'', 'ours side expected empty (r624 deletion), got %d B' % len(MID)
END = b'>>>>>>> origin/main\r\n'
THEIRS, TAIL = rest2.split(END, 1)
NEEDLE624 = b'- [2026-10-03 16:4x r624 bm-b]'
keep = []
for line in THEIRS.split(b'\r\n'):
    if line == b'':
        continue
    if line.startswith(NEEDLE624):
        continue  # my domain-migration deletion stands (verbatim in pit-git.md)
    keep.append(line)
assert keep, 'theirs block must retain bm-a r632 entry'
assert PRE.endswith(b'\r\n'), 'pre must end with CRLF for line integrity'
out = PRE + b'\r\n'.join(keep) + b'\r\n' + TAIL
# guard: no conflict markers, no lone LF, key lines present/absent
assert b'<<<<<<<' not in out and b'>>>>>>>' not in out, 'markers residue'
assert out.count(b'\n') == out.count(b'\r\n'), 'lone LF leaked'
assert b'- [2026-10-03 16:4x r632 bm-a]' in out, 'r632 entry missing'
assert NEEDLE624 not in out, 'r624 residue'
assert out.count(b'r625 bm-b') >= 3, 'ptr clauses missing'
assert b'- [2026-10-03 16:3x r631 bm-a]' in out, 'r631 anchor missing'
write(p, out)
RESOLVED[p] = 'memory-union tail: r624 dropped (migrated), r632 kept'

for k in sorted(RESOLVED):
    print('RESOLVED %s :: %s' % (k.encode('ascii', 'replace').decode('ascii'), RESOLVED[k].encode('ascii', 'replace').decode('ascii')))
print('RESOLVER_OK %d files' % len(RESOLVED))
