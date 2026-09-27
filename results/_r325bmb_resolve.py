# -*- coding: utf-8 -*-
"""r325 bm-b push-collision resolver (18 UU vs bm-a r325 + bm-c r82 same-window S6 mirror batch).
Recipes per bigmoney-conflict-resolve classifier (12 auto + 6 UNKNOWN hand-adjudicated same-day-regen family):
- CODELY.md: memory-union with overlapping 13th-batch archival (bm-c archived r312+r320PS; mine archived r312+r320x2 superset)
- archive 202609.md: append-union both batch sections
- autofill_state: launches key-union cap50 asc + last_tick inner-ts take-new
- compute_audit: history ts-key union w/ content-identity verify (r322) + latest take-new deep ts
- regime_state: history asof-union + top take-new by updated
- 11 measurement faces: take-:3: (mine probed newer) whole bytes; daily twins same-side coherent
"""
import subprocess, json, io, sys

def blob_bytes(rev, path):
    return subprocess.run(['git', 'show', rev + ':' + path], capture_output=True).stdout

def blob(rev, path):
    return blob_bytes(rev, path).decode('utf-8')

def detect_fmt(raw_bytes):
    txt = raw_bytes.decode('utf-8')
    crlf = '\r\n' in txt
    indent = 0
    for line in txt.splitlines():
        s = line[:len(line) - len(line.lstrip())]
        if s:
            indent = len(s)
            break
    trailing_nl = txt.endswith('\n')
    return crlf, indent, trailing_nl

receipt = []

def w(path, data_bytes):
    io.open(path, 'wb').write(data_bytes)

def resolve_take_mine(path, why):
    b3 = blob_bytes(':3', path)
    w(path, b3)
    receipt.append((path, 'take-:3 whole bytes', why))
    return b3

# ---------- 1) measurement snapshot family: take-:3 (all probed newer) ----------
TAKE3 = {
    'results/dashboard_status.json': 'meta.generated_at 13:15:38 > 13:15:27',
    'results/dashboard_status.js': 'js-wrapper whole-bytes winner mine (meta.generated_at 13:15:38 > 13:15:27) R209',
    'results/fundamental_b_layer_filter.json': 'updated 13:15:30 > 13:15:10',
    'results/futures_update_status.json': 'ts 13:15:26 > 13:14:46',
    'results/heat_update_status.json': 'updated 13:15:25 > 13:14:46',
    'results/lhb_update_status.json': 'updated 13:15:25 > 13:14:45',
    'results/update_status.json': 'updated 13:15:05 > 13:14:11',
    'results/prospect_promotion/_summary.json': 'generated 13:15:32+08:00 > 13:15:22+08:00',
    'results/scorecard_v1.json': 'generated 13:15:09 > 13:14:24',
    'results/strategy_scorecard.json': 'generated 13:15:19 > 13:14:30',
    'docs/daily_report/REPORT-2026-09-27.json': 'generated_at 13:15:36 > 13:15:26',
    'docs/daily_report/REPORT-2026-09-27.md': 'md twin same-side coherent with json (take-:3)',
}
for p, why in TAKE3.items():
    resolve_take_mine(p, why)

# token_usage: key-set equality assert then take-:3 (newer top)
t2 = json.loads(blob(':2', 'results/token_usage.json'))
t3 = json.loads(blob(':3', 'results/token_usage.json'))
assert set(t2.get('machines', {})) == set(t3.get('machines', {})) == {'bm-a', 'bm-c', '-bm-a', '-bm-c', 'default'}, 'machines key drift'
resolve_take_mine('results/token_usage.json', 'machines key-set 5|5 equal -> take-:3 newer top (r324 key-union family)')

# ---------- 2) autofill_state.json: mixed-dict+ledger ----------
p = 'results/autofill_state.json'
a2 = json.loads(blob(':2', p)); a3 = json.loads(blob(':3', p))
raw2 = blob_bytes(':2', p)
crlf, indent, tnl = detect_fmt(raw2)
L2 = a2.get('launches', []); L3 = a3.get('launches', [])
key = lambda e: (e.get('ts'), e.get('machine'), e.get('entry'), e.get('shard'), e.get('pid'))
seen = {}
for e in L2 + L3:  # HEAD face priority for identical keys
    k = key(e)
    if k not in seen:
        seen[k] = e
merged = sorted(seen.values(), key=lambda e: e.get('ts') or '')
cap = 50
kept = merged[-cap:] if len(merged) > cap else merged
kept = sorted(kept, key=lambda e: e.get('ts') or '')  # r245: write-back asc
lt2, lt3 = a2.get('last_tick') or {}, a3.get('last_tick') or {}
assert isinstance(lt2, dict) and isinstance(lt3, dict)
last_tick = lt2 if (lt2.get('ts') or '') >= (lt3.get('ts') or '') else lt3  # inner-ts compare, tie->HEAD(:2)
fin = dict(a3)  # take-:3 shell
fin['launches'] = kept
fin['last_tick'] = last_tick
out = json.dumps(fin, ensure_ascii=False, indent=indent or 1)
if tnl:
    out += '\n'
if crlf:
    out = out.replace('\n', '\r\n')
w(p, out.encode('utf-8'))
json.loads(io.open(p, encoding='utf-8-sig').read())  # reparse
assert isinstance(json.load(io.open(p, encoding='utf-8-sig'))['last_tick'], dict)
receipt.append((p, 'launches union %d+%d->%d cap%d asc + last_tick take-inner-newer(%s)' % (len(L2), len(L3), len(kept), cap, last_tick.get('ts')), 'r317/r140/r245'))

# ---------- 3) compute_audit.json: rolling-ledger ----------
p = 'results/compute_audit.json'
a2 = json.loads(blob(':2', p)); a3 = json.loads(blob(':3', p))
H2 = a2.get('history', []); H3 = a3.get('history', [])
byk2 = {h['ts']: h for h in H2}; byk3 = {h['ts']: h for h in H3}
collisions = set(byk2) & set(byk3)
diffs = [k for k in collisions if json.dumps(byk2[k], sort_keys=True) != json.dumps(byk3[k], sort_keys=True)]
assert not diffs, ('content-diff collisions need composite key', diffs[:3])  # r322 law
union = dict(byk2); union.update(byk3)
hist = sorted(union.values(), key=lambda h: h['ts'])
assert len(hist) == len(set(byk2) | set(byk3)), 'zero-loss assertion'  # r319 canon
lat2, lat3 = a2.get('latest') or {}, a3.get('latest') or {}
latest = lat3 if (lat3.get('ts') or '') > (lat2.get('ts') or '') else lat2
fin = dict(a3)
fin['history'] = hist
fin['latest'] = latest
raw2 = blob_bytes(':2', p)
crlf, indent, tnl = detect_fmt(raw2)
out = json.dumps(fin, ensure_ascii=False, indent=indent or 1)
if tnl: out += '\n'
if crlf: out = out.replace('\n', '\r\n')
w(p, out.encode('utf-8'))
json.loads(io.open(p, encoding='utf-8-sig').read())
receipt.append((p, 'history ts-key union %d+%d->%d (collisions %d content-identical r322) + latest take-newer(%s)' % (len(H2), len(H3), len(hist), len(collisions), latest.get('ts')), 'r188/R208/r322'))

# ---------- 4) regime_state.json: rolling-ledger ----------
p = 'results/regime_state.json'
a2 = json.loads(blob(':2', p)); a3 = json.loads(blob(':3', p))
H2 = a2.get('history', []); H3 = a3.get('history', [])
byk2 = {h['asof']: h for h in H2}; byk3 = {h['asof']: h for h in H3}
collisions = set(byk2) & set(byk3)
diffs = [k for k in collisions if json.dumps(byk2[k], sort_keys=True) != json.dumps(byk3[k], sort_keys=True)]
assert not diffs, ('regime asof content-diff', diffs)
union = dict(byk2); union.update(byk3)
hist = sorted(union.values(), key=lambda h: h['asof'])
assert len(hist) == len(set(byk2) | set(byk3))
fin = a3 if (a3.get('updated') or '') >= (a2.get('updated') or '') else a2  # top take-new by updated
fin['history'] = hist
raw2 = blob_bytes(':2', p)
crlf, indent, tnl = detect_fmt(raw2)
out = json.dumps(fin, ensure_ascii=False, indent=indent or 1)
if tnl: out += '\n'
if crlf: out = out.replace('\n', '\r\n')
w(p, out.encode('utf-8'))
json.loads(io.open(p, encoding='utf-8-sig').read())
receipt.append((p, 'history asof-union %d+%d->%d + top take-new(updated %s)' % (len(H2), len(H3), len(hist), fin.get('updated')), 'r319 key-probe + R208'))

# ---------- 5) CODELY.md: memory-union with overlapping 13th-batch archival ----------
p = 'CODELY.md'
c2 = blob(':2', p); c3 = blob(':3', p)
assert c2 == c2.strip('\ufeff') and '\r\n' not in c2, 'CODELY face format drift'
lines2 = c2.splitlines(True)
# remove r320 bm-a entry (bm-c face kept it; my archive face subsumes it -- entry preserved verbatim in archive union)
r320_key = '- [2026-09-27 12:1x r320 bm-a]'
hits = [l for l in lines2 if l.startswith(r320_key)]
assert len(hits) == 1, ('r320bm-a presence', len(hits))
lines2 = [l for l in lines2 if not l.startswith(r320_key)]
txt = ''.join(lines2)
# my index line + entry from :3:
my_idx = None; my_entry = None
for l in c3.splitlines(True):
    if l.startswith('十三批外迁（r325 bm-b'):
        my_idx = l
    if l.startswith('- [2026-09-27 13:2x r325 bm-b]'):
        my_entry = l
assert my_idx and my_entry, 'my faces not found in :3'
anchor = next(l for l in lines2 if l.startswith('十三批外迁（r82 bm-c'))
txt = txt.replace(anchor, anchor + my_idx, 1)
if not txt.endswith('\n'):
    txt += '\n'
txt += my_entry
w(p, txt.encode('utf-8'))
v = io.open(p, encoding='utf-8').read()
assert '[2026-09-27 13:1x r82 bm-c]' in v and '[2026-09-27 13:2x r325 bm-b]' in v
assert '十三批外迁（r82 bm-c' in v and '十三批外迁（r325 bm-b' in v
assert '- [2026-09-27 10:4x r312 bm-a]' not in v and '- [2026-09-27 12:1x r320 bm-b]' not in v and '- [2026-09-27 12:1x r320 bm-a]' not in v
sz = len(v.encode('utf-8'))
assert sz <= 10240, ('CODELY size', sz)
receipt.append((p, 'memory-union: origin face + r320bm-a subsume-remove (verbatim in archive) + my 13th-batch idx + my r325 entry; %dB' % sz, 'R208/r212 + overlapping-archival manual'))

# ---------- 6) archive 202609.md: append-union both 13th-batch sections ----------
p = 'research/memory-archive/202609.md'
a2t = blob(':2', p); a3t = blob(':3', p)
assert '\r\n' not in a2t and '\r\n' not in a3t
marker = '## 十三批外迁（r325 bm-b'
i = a3t.find(marker)
assert i > 0, 'my section not found'
my_sec = a3t[i - 1:] if a3t[i - 1] == '\n' else a3t[i:]
if not my_sec.endswith('\n'):
    my_sec += '\n'
fin = a2t
if not fin.endswith('\n'):
    fin += '\n'
fin += my_sec
w(p, fin.encode('utf-8'))
v = io.open(p, encoding='utf-8').read()
assert v.count('十三批外迁') == 2 and v.count('（r82 bm-c') == 1 and v.count('（r325 bm-b') == 1, 'both 13th sections present'
assert '- [2026-09-27 10:4x r312 bm-a]' in v and '- [2026-09-27 12:1x r320 bm-b]' in v and '- [2026-09-27 12:1x r320 bm-a]' in v, 'moved entries preserved'
receipt.append((p, 'append-union both 13th-batch sections (r82 bm-c + r325 bm-b), entries verbatim x-dup honest record', 'append-only zero-loss'))

# ---------- board ----------
print('RESOLVER RECEIPT %d/%d' % (len(receipt), 18))
for p, act, law in receipt:
    print('  %s | %s | %s' % (p, act, law))
