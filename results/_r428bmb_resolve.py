# -*- coding: utf-8 -*-
# r428 bm-b push-rejection rebase resolver, revision 2 (canon: bigmoney-conflict-resolve skill)
# stages: :1: base, :2: ours = origin/main (bm-c r220 S6 catch-up + its own CODELY waterline reorg),
#         :3: theirs = replayed bm-b r428 commit
# faces:
#   CODELY.md            manual memory-union: origin skeleton wins (first-lander per fleet/README.md sec.4);
#                        my parallel pointer line dropped (subsumed: both sides independently migrated the SAME two
#                        entries to archive; origin carries two per-entry pointer lines); my pit-law entry KEPT,
#                        renumbered 108->109 (same-window batch-number collision with bm-c r220's own 108 stash law),
#                        AND mechanism-corrected in-place before canonization: transport was proven FAITHFUL by
#                        in-round probe (clean Chinese via python -c cmdline arrived byte-identical), the real root
#                        cause was generation-side reproduction of console-displayed mojibake strings.
#   archive 202609.md    append-only tail union: base + origin tail + my tail (prefix-assert both sides).
#   compute_audit.json   rolling-ledger union + latest take-new, trim 201 steady-state cap (r188/R208).
#   regime_state.json    rolling union history/transitions + state take-new deep-ts.
#   x2_watch_log.jsonl   append-log line-level union zero-loss (r188/r217).
#   14 snapshot faces    take-new via hardened deep-ts probe (r311/r319/r100/R350; staged blobs only).
#   6 twin faces         byte-copy SAME side as json probe winner (r329).
import io, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
MOJIBAKE_MARKERS = ['绛栫暐', '鐮旂┒', '婕忔枟', '鏂板悜', '涔嬮棿']  # display-face garble of 策略/研究/漏斗/方向/之间

def raw(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    assert r.returncode == 0, (stage, path, r.stderr[:200])
    return r.stdout

def deep_ts(obj, best=''):
    if isinstance(obj, dict):
        for k, v in obj.items():
            kn = str(k).replace('_', '').replace('-', '').lower()
            if isinstance(v, str) and TS_RE.match(v) and any(p in kn for p in ('generated', 'updated', 'ts', 'asof', 'date')):
                if v > best: best = v
            elif isinstance(v, (dict, list)):
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for it in obj:
            best = deep_ts(it, best)
    return best

def take_newer(path):
    b2, b3 = raw('2', path), raw('3', path)
    t2 = deep_ts(json.loads(b2.decode('utf-8')))
    t3 = deep_ts(json.loads(b3.decode('utf-8')))
    if not t2 and not t3:
        raise SystemExit(f'{path}: no ts probe either side, refuse blind pick')
    winner, side = ('2', b2) if t2 >= t3 else ('3', b3)   # r140 tie -> HEAD (:2:)
    with io.open(path, 'wb') as f:
        f.write(side)
    print(f'[take-new:{path}] :2:ts={t2!r} :3:ts={t3!r} -> :{winner}: ({len(side)}B)')
    return winner

def byte_copy(path, winner):
    side = raw('2', path) if winner == '2' else raw('3', path)
    with io.open(path, 'wb') as f:
        f.write(side)
    print(f'[twin-copy:{path}] from :{winner}: ({len(side)}B)')

def patch(entry, old, new):
    assert old in entry, f'patch source missing: {old[:40]}...'
    return entry.replace(old, new)

# ---------- 1) CODELY.md manual memory-union ----------
P_C = 'CODELY.md'
base_c, origin_c, mine_c = raw('1', P_C), raw('2', P_C), raw('3', P_C)
base_lines = base_c.decode('utf-8').split('\n')
mine_lines = mine_c.decode('utf-8').split('\n')
origin_text = origin_c.decode('utf-8')
my_added = [l for l in mine_lines if l not in set(base_lines)]
entry_lines = [l for l in my_added if l.startswith('- [2026-09-29 14:0x r428 bm-b]')]
assert len(entry_lines) == 1, ('my entry not uniquely found', len(entry_lines))
entry = entry_lines[0]
# mechanism correction before canonization (in-round probe falsified the transport-mangle diagnosis)
entry = patch(entry, '（PS→python -c 中文参数双编码损坏律·控制面非 UTF-8 通道禁直传中文）',
                   '（显示面乱码上下文污染律·命令行管道实测保真·禁复读乱码串入产出）')
entry = patch(entry, 'run_shell_command 经 PowerShell 向 python -c 内联传中文=命令行按控制台码页（GBK）误解码 UTF-8 源文→python 收 mojibake 字符再按 UTF-8 写盘=文件内双编码垃圾',
                   '原诊断=命令行 GBK 误解码——同窗探针翻案：干净中文经 python -c 原样到达=管道保真；真根因=生成面复读控制台显示面乱码串（GBK 控制台读 UTF-8 件产 mojibake 入上下文→新产出内嵌同串）')
entry = patch(entry, '处置=中文产文一律走 write_file 通道（临时件+python 文件对文件二进制复制·命令行参数限 ASCII）',
                   '处置=产出文本前自查上下文显示面乱码串勿复读；关键中文面走 write_file 通道')
# renumber 108 -> 109 (same-window collision with bm-c r220's own 108; commit-time order, later yields)
entry = patch(entry, '坑律一百零八批', '坑律一百零九批')
entry = entry.rstrip('。') + '。（注：原起草 108 批与 bm-c r220 同窗撞号，按 fleet/README.md §4 后到让号改 109。）'
if not origin_text.endswith('\n'):
    origin_text += '\n'
union_c = origin_text + entry + '\n'
ub = union_c.encode('utf-8')
# garble guards: my entry deliberately QUOTES the r428 marker once (evidence string); no other mojibake allowed
assert union_c.count('鎴戞柟') == 1, f'mojibake marker count {union_c.count("鎴戞柟")} != 1'
for m in MOJIBAKE_MARKERS:
    assert m not in union_c, f'contamination marker present: {m}'
assert union_c.count('坑律一百零八批') == 1, 'origin 108 law must appear exactly once'
assert union_c.count('坑律一百零九批') == 1, 'my renumbered 109 law must appear exactly once'
assert len(ub) <= 10000, f'water-line breach {len(ub)}'
with io.open(P_C, 'wb') as f:
    f.write(ub)
print(f'[codely-union] base {len(base_c)}B origin {len(origin_c)}B mine {len(mine_c)}B -> union {len(ub)}B '
      f'(origin skeleton + my entry renumbered 109 + mechanism-corrected; my parallel pointer dropped, subsumed by origin 2-pointer face)')

# ---------- 2) archive 202609.md append-only tail union ----------
P_A = 'research/memory-archive/202609.md'
base_a, origin_a, mine_a = raw('1', P_A), raw('2', P_A), raw('3', P_A)
assert origin_a.startswith(base_a), 'origin not append-only (manual review needed)'
assert mine_a.startswith(base_a), 'mine not append-only (manual review needed)'
my_tail = mine_a[len(base_a):]
assert my_tail.startswith(b'## '), 'my tail must be a new section'
union_a = origin_a + my_tail
with io.open(P_A, 'wb') as f:
    f.write(union_a)
lost = [l for l in origin_a.split(b'\n') if l.strip() and l not in union_a.split(b'\n')]
lost += [l for l in mine_a.split(b'\n') if l.strip() and l not in union_a.split(b'\n')]
assert not lost, f'archive zero-loss FAIL: {lost[:3]}'
print(f'[archive-union] base {len(base_a)}B origin {len(origin_a)}B mine {len(mine_a)}B -> union {len(union_a)}B (both tails kept, zero-loss verified)')

# ---------- 3) compute_audit.json rolling union ----------
P_AUD = 'results/compute_audit.json'
a2, a3 = json.loads(raw('2', P_AUD).decode('utf-8')), json.loads(raw('3', P_AUD).decode('utf-8'))
k = lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False)
u = {k(r): r for r in a2['history']}
for r in a3['history']:
    u[k(r)] = r
rows = sorted(u.values(), key=lambda r: r.get('ts', ''))
trim = rows[-201:]
lt2, lt3 = a2['latest'], a3['latest']
latest = lt3 if str(lt3.get('ts', '')) >= str(lt2.get('ts', '')) else lt2
aud_out = {'latest': latest, 'history': trim}
json.loads(json.dumps(aud_out, ensure_ascii=False))
tmp = P_AUD + '.tmp_r428bmb'
with io.open(tmp, 'w', encoding='utf-8', newline='') as f:
    json.dump(aud_out, f, ensure_ascii=False, indent=2)
    f.write('\n')
os.replace(tmp, P_AUD)
print(f'[audit-union] rows union={len(rows)} -> trim {len(trim)}, latest.ts={latest.get("ts")} (zero-loss union then cap)')

# ---------- 4) regime_state.json rolling union ----------
P_R = 'results/regime_state.json'
r2, r3 = json.loads(raw('2', P_R).decode('utf-8')), json.loads(raw('3', P_R).decode('utf-8'))
out = dict(r2)
for lk in ('history', 'transitions'):
    if lk in r2 and lk in r3 and isinstance(r2[lk], list) and isinstance(r3[lk], list):
        uu = {k(r): r for r in r2[lk]}
        for r in r3[lk]:
            uu[k(r)] = r
        out[lk] = sorted(uu.values(), key=lambda r: str(deep_ts(r) or r))
t2, t3 = deep_ts(r2), deep_ts(r3)
if t3 > t2:
    for kk, vv in r3.items():
        if kk not in ('history', 'transitions'):
            out[kk] = vv
json.loads(json.dumps(out, ensure_ascii=False))
tmp = P_R + '.tmp_r428bmb'
with io.open(tmp, 'w', encoding='utf-8', newline='') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
    f.write('\n')
os.replace(tmp, P_R)
print(f'[regime-union] state take-new by deep-ts (:2:={t2!r} :3:={t3!r}); history={len(out.get("history", []))} transitions={len(out.get("transitions", []))}')

# ---------- 5) x2_watch_log.jsonl line union ----------
P_X = 'results/x2_watch_log.jsonl'
x2, x3 = raw('2', P_X), raw('3', P_X)
seen, merged = set(), []
for line in (x2.split(b'\n') + x3.split(b'\n')):
    if line.strip() and line not in seen:
        seen.add(line); merged.append(line)
union_x = b'\n'.join(merged) + b'\n'
for line in merged:
    json.loads(line.decode('utf-8'))
with io.open(P_X, 'wb') as f:
    f.write(union_x)
n2 = len([l for l in x2.split(b'\n') if l.strip()]); n3 = len([l for l in x3.split(b'\n') if l.strip()])
print(f'[x2-union] :2: {n2} + :3: {n3} -> {len(merged)} lines zero-loss')

# ---------- 6) snapshot take-new faces ----------
for p in ('results/fundamental_b_layer_filter.json', 'results/prospect_paper/_summary.json',
          'results/t35_open_fill_verify.json', 'results/token_usage.json', 'results/update_status.json',
          'results/lhb_update_status.json',
          'results/paper/COMPOSITE-CE-01_paper.json', 'results/paper/COMPOSITE-CE-02_paper.json',
          'results/paper/DROUGHT-CE-01_paper.json', 'results/paper/ENGULF-CE-01_paper.json',
          'results/paper/NEEDLE-DE-01_paper.json', 'results/paper/VOLATILITY-CE-01_paper.json',
          'results/paper_export/export-2026-09-28.json', 'results/paper_export/latest.json'):
    take_newer(p)

# ---------- 7) twin faces ----------
w = take_newer('docs/daily_report/REPORT-2026-09-29.json')
byte_copy('docs/daily_report/REPORT-2026-09-29.md', w)
w2 = take_newer('docs/live_usage/LIVE-2026-09-29.json')
byte_copy('docs/live_usage/LIVE-2026-09-29.md', w2)
byte_copy('docs/live_usage/LIVE-latest.json', w2)
byte_copy('docs/live_usage/LIVE-latest.md', w2)

# ---------- 8) parse-verify every written json (r185) + final canaries ----------
for p in (P_AUD, P_R, 'results/fundamental_b_layer_filter.json', 'results/prospect_paper/_summary.json',
          'results/t35_open_fill_verify.json', 'results/token_usage.json', 'results/update_status.json',
          'results/lhb_update_status.json', 'docs/daily_report/REPORT-2026-09-29.json',
          'docs/live_usage/LIVE-2026-09-29.json', 'docs/live_usage/LIVE-latest.json',
          'results/paper/COMPOSITE-CE-01_paper.json', 'results/paper/COMPOSITE-CE-02_paper.json',
          'results/paper/DROUGHT-CE-01_paper.json', 'results/paper/ENGULF-CE-01_paper.json',
          'results/paper/NEEDLE-DE-01_paper.json', 'results/paper/VOLATILITY-CE-01_paper.json',
          'results/paper_export/export-2026-09-28.json', 'results/paper_export/latest.json'):
    json.loads(io.open(p, encoding='utf-8').read())
CODELY_ = io.open(P_C, encoding='utf-8').read()
assert '坑律一百零九批' in CODELY_ and '坑律一百零八批' in CODELY_
assert '管道保真' in CODELY_  # corrected mechanism present
io.open(P_A, encoding='utf-8').read()
print('[verify] all written faces parse-verified; CODELY dual-batch present; corrected mechanism in tree')
print('resolver r428 bm-b rev2: 25 faces resolved (1 codely manual union + 1 archive tail union + 2 rolling + 1 jsonl + 14 snapshot + 6 twin-copies)')
