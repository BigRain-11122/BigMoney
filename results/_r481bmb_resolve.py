# r481 bm-b rebase-collision resolver (vs bm-c r291 same-window) per bigmoney-conflict-resolve skill
# Classes: CODELY=memory-union(+dual-reorg dedup, all dropped rows verbatim-archived), archive=append-section union,
# compute_audit=rolling-ledger union+latest take-new, regime_state=rolling-ledger union+state take-new,
# 8 snapshots/same-day-faces=take-new (theirs=bm-b 22:38-22:41 all newer than bm-c 22:33-22:35, verified in recon).
import subprocess, json, hashlib, sys

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        sys.exit(f'blob read fail {stage} {path}: {r.stderr[:200]}')
    return r.stdout

def eol_of_bytes(b):
    crlf = b.count(b'\r\n'); lf = b.count(b'\n') - crlf
    return '\r\n' if crlf >= lf else '\n'

def write_bytes(path, data):
    open(path, 'wb').write(data)

report = []

# ---------- 1. archive 202609.md: ours + theirs-only tail section (my r481 section) ----------
AR = 'research/memory-archive/202609.md'
ar_o, ar_t = blob(2, AR), blob(3, AR)
ar_eol = eol_of_bytes(ar_o)
o_lines = ar_o.decode('utf-8').replace('\r\n', '\n').split('\n')
t_lines = ar_t.decode('utf-8').replace('\r\n', '\n').split('\n')
o_set = set(o_lines)
t_only = [l for l in t_lines if l not in o_set]
# my r481 section = trailing block from its title onward in theirs
title481 = '## 热冷整编 2026-09-30 r481 bm-b 窗批'
idx = next((i for i, l in enumerate(t_lines) if l.startswith(title481)), None)
assert idx is not None, 'r481 section title not found in theirs archive'
t_section = t_lines[idx:]
merged_ar = list(o_lines)
if merged_ar and merged_ar[-1] != '':
    merged_ar.append('')
merged_ar += t_section
while merged_ar and merged_ar[-1] == '':
    merged_ar.pop()
merged_ar.append('')
# resolver note section: rows dropped from CODELY union that were NOT already in any archive section
resolver_rows = []  # filled after CODELY step; appended below
ar_text = '\n'.join(merged_ar)
if ar_eol == '\r\n':
    ar_text = ar_text.replace('\n', '\r\n')
write_bytes(AR, ar_text.encode('utf-8'))
report.append(f'archive: union ours({len(ar_o)}B)+theirs-only section {len(t_section)} lines -> {len(open(AR,"rb").read())}B')

# ---------- 2. CODELY.md: union with dual-reorg dedup ----------
CO = 'CODELY.md'
co_o, co_t = blob(2, CO), blob(3, CO)
co_eol = eol_of_bytes(co_o)
o = co_o.decode('utf-8').replace('\r\n', '\n').split('\n')
t = co_t.decode('utf-8').replace('\r\n', '\n').split('\n')
o_set, t_set = set(o), set(t)
t_only = [l for l in t if l not in o_set]
o_only = [l for l in o if l not in t_set]

# rows to drop from union (redundant pointers covered by the single r481 merged pointer; receipt=流水型)
drop_prefixes = [
    '- 冷层指针（r475 合并',                                   # covered verbatim in archive r481 bm-b section
    '- 冷层指针（r291 合并·r444 范式）：r472 冻结探针事实消费三坑+r473',   # bm-c merged (a) -> archive in resolver section
    '- 冷层指针（r291 合并·指针合并归档 r444 范式）：r282 bm-c SSH',       # bm-c merged (c) -> archive in resolver section
    '- [2026-09-30 r492 bm-a] O-20260930-2054 机队 CPU 效率确保令已回执执行',  # receipt; verbatim in archive r481 bm-b section
]
dropped = [l for l in o if any(l.startswith(p) for p in drop_prefixes)]
dropped_not_archived = [l for l in dropped if (l not in set(o_lines) and l not in set(t_lines))]
# my r481 pit + merged pointer rows (keep verbatim)
my_new = [l for l in t_only if l.startswith('- [2026-09-30 22:4x r481 bm-b]') or l.startswith('- 冷层指针（r481 合并')]
assert len(my_new) == 2, f'expected 2 bm-b new rows, got {len(my_new)}'
# bm-c r291 pit law row (keep in place)
their_pit = [l for l in o_only if l.startswith('- [2026-09-30 r291 bm-c] 正典引用字符面坑')]
assert len(their_pit) == 1, 'bm-c r291 pit row not found'

# build union: ours minus dropped, then append my 2 rows at end (Project tail)
final = [l for l in o if l not in dropped]
# strip trailing blanks, append my rows
while final and final[-1] == '':
    final.pop()
final += my_new
final.append('')

# zero-loss assert: every dropped line must exist verbatim in archive file OR be archived by resolver now
ar_now = set(open(AR, encoding='utf-8').read().replace('\r\n', '\n').split('\n'))
dropped_not_archived = [l for l in dropped if l not in ar_now]

# second-pass hardline cut if needed: pointer-ize r290 (full text -> resolver note, r444 pointer-merge law)
co_text_tmp = '\n'.join(final)
size_tmp = len((co_text_tmp.replace('\n', '\r\n') if co_eol == '\r\n' else co_text_tmp).encode('utf-8'))
pointerized = []
if size_tmp > 10240:
    r290_rows = [l for l in final if l.startswith('- [2026-09-30 r290 bm-c] 集团决策面盲读坑')]
    assert len(r290_rows) == 1, 'r290 row not found for pointer-ize'
    ptr290 = '- [2026-09-30 r290 bm-c] 集团决策面盲读坑+D-19 新鲜读律接线（指针条·全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r481 bm-b rebase-resolver 注记』节）'
    final = [ptr290 if l == r290_rows[0] else l for l in final]
    pointerized = r290_rows
    assert ptr290 not in ar_now

# resolver note append (dropped + pointerized rows, verbatim)
to_archive = dropped_not_archived + pointerized
if to_archive:
    note_title = '## 热冷整编 2026-09-30 r481 bm-b rebase-resolver 注记（CODELY union 去冗/指针化行 verbatim 收口）'
    block = [note_title, ''] + to_archive + ['']
    with open(AR, 'ab') as f:
        f.write(('\r\n'.join(block) if ar_eol == '\r\n' else '\n'.join(block)).encode('utf-8'))
    ar_now = set(open(AR, encoding='utf-8').read().replace('\r\n', '\n').split('\n'))

lost = [l for l in dropped + pointerized if l not in ar_now]
assert not lost, f'ZERO-LOSS FAIL: {len(lost)} rows lost'

co_text = '\n'.join(final)
if co_eol == '\r\n':
    co_text = co_text.replace('\n', '\r\n')
co_bytes = co_text.encode('utf-8')
write_bytes(CO, co_bytes)
size = len(co_bytes)
report.append(f'CODELY: union={size}B dropped={len(dropped)} pointerized={len(pointerized)} archived_now={len(to_archive)} hardline={"PASS" if size<=10240 else "FAIL"}')
assert size <= 10240, f'CODELY {size}B > 10240 hardline'

# ---------- 3. compute_audit.json: history union + latest take-new ----------
CA = 'results/compute_audit.json'
cao = json.loads(blob(2, CA)); cat = json.loads(blob(3, CA))
def rowhash(x):
    return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()
seen = {}
hist = []
for row in cao.get('history', []) + cat.get('history', []):
    h = rowhash(row)
    if h not in seen:
        seen[h] = True
        hist.append(row)
hist.sort(key=lambda r: str(r.get('ts', '')))
latest = cat.get('latest') if str(cat.get('latest', {}).get('ts', '')) >= str(cao.get('latest', {}).get('ts', '')) else cao.get('latest')
ca_merged = {'latest': latest, 'history': hist}
e = eol_of_bytes(blob(2, CA))
s = json.dumps(ca_merged, ensure_ascii=False, indent=1)
if e == '\r\n': s = s.replace('\n', '\r\n')
write_bytes(CA, s.encode('utf-8'))
json.loads(open(CA, encoding='utf-8').read())
report.append(f'compute_audit: history {len(cao["history"])}+{len(cat["history"])} -> union {len(hist)} rows; latest ts={latest.get("ts")}')

# ---------- 4. regime_state.json: ledger union + state take-new ----------
RS = 'results/regime_state.json'
rso = json.loads(blob(2, RS)); rst = json.loads(blob(3, RS))
merged = dict(rso)  # start from ours (older), overlay theirs (newer) for state fields
for k, v in rst.items():
    if k in ('transitions', 'history'):
        seen2 = {}
        comb = []
        for row in rso.get(k, []) + rst.get(k, []):
            h = rowhash(row)
            if h not in seen2:
                seen2[h] = True
                comb.append(row)
        comb.sort(key=lambda r: str(r.get('ts') or r.get('date') or ''))
        merged[k] = comb
    else:
        merged[k] = v  # theirs newer (22:38 vs 22:33) for all scalar fields
e = eol_of_bytes(blob(2, RS))
s = json.dumps(merged, ensure_ascii=False, indent=1)
if e == '\r\n': s = s.replace('\n', '\r\n')
write_bytes(RS, s.encode('utf-8'))
json.loads(open(RS, encoding='utf-8').read())
report.append(f'regime_state: transitions union {len(merged["transitions"])} rows, history union {len(merged["history"])} rows, updated={merged["updated"]} (take-new theirs)')

# ---------- 5. snapshots + same-day faces: take theirs (bm-b newer, recon-verified) ----------
TAKE_THEIRS = [
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/update_status.json',
    'results/token_usage.json',
    'results/fundamental_b_layer_filter.json',
    'results/_attrition_guard_scan.json',
    'docs/daily_report/REPORT-2026-09-30.json',
    'docs/daily_report/REPORT-2026-09-30.md',
    'docs/live_usage/LIVE-2026-09-30.json',
    'docs/live_usage/LIVE-2026-09-30.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
]
for p in TAKE_THEIRS:
    b = blob(3, p)
    write_bytes(p, b)
    if p.endswith('.json'):
        json.loads(b)
    report.append(f'{p}: take theirs ({len(b)}B)')

open('results/_r481bmb_resolve_report.txt', 'w', encoding='utf-8').write('\n'.join(report))
print('RESOLVER OK')
for r in report:
    print(' -', r.encode('ascii', 'backslashreplace').decode('ascii'))
