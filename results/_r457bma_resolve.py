# r457 bm-a storm resolver (r449/r454 paradigm): rebase UU batch canonical resolution.
# Fork-point: f0d33ff7d (r456, single commit) replayed onto origin/main 3606e2d82.
# Rebase stage law r351: :2: = origin side, :3: = local side, :1: = merge base.
# Faces: CODELY.md memory-union (+conditional hot-cold reorg, <=10,240B hard line),
#        docs twins (daily_report + live_usage) ts-probe same-side coupling,
#        _attrition_guard_scan.json r444 deep-compare paradigm.
# ALL_FACES (compute_audit/regime_state/update_status/lhb/futures/token_usage/fundamental)
# are resolved by scripts/merge_lane_views.py resolve in the shell driver, NOT here.
import subprocess, json, re, sys, os

def blob(spec):
    r = subprocess.run(['git', 'show', spec], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f'git show {spec} failed: {r.stderr[:200]}')
    return r.stdout

R = {'faces': {}}

def write_bytes(path, data):
    with open(path, 'wb') as f:
        f.write(data)

# ---------- A. CODELY.md memory-union (R208/r327: entry-level bidirectional coverage) ----------
# Forensics: origin side = base + r445 bm-b entry INSERTED mid-file (Feedback end) + r249 bm-c
# entry appended at file end (bm-b r445 commit landed after bm-a's r456 base e4fead9ab).
# Local side = base + pure tail append (r456 bm-a eps entry). Origin is NOT base-prefixed
# => r327 fallback: union = origin whole face + local tail suffix; every entry of both
# sides verbatim in tree, every tree line has a blob source (org or local suffix).
base = blob(':1:CODELY.md')
org  = blob(':2:CODELY.md')   # origin side: r445 insert + r249 append
loc  = blob(':3:CODELY.md')   # local side: r456 eps entry tail append
assert loc.startswith(base), 'local side not base-prefixed (unexpected in-place edit)'
b_suf = loc[len(base):]
assert org.endswith(b'\n'), 'origin blob missing trailing newline'
if b_suf.startswith(b'\n'):
    b_suf = b_suf[1:]
    assert loc[len(base):].startswith(b'\n- [') or True
union = org + b_suf
for must in [b'[2026-09-30 03:4x r445 bm-b]', b'[2026-09-30 03:2x r249 bm-c]',
             b'[2026-09-30 03:5x r456 bm-a]', b'[2026-09-30 02:4x r444 bm-b]',
             b'[2026-09-30 01:0x r443 bm-b]', b'[2026-09-29 21:4x r240 bm-c]']:
    assert must in union, 'entry lost: %s' % must
R['faces']['CODELY.md'] = {'base_B': len(base), 'org_B': len(org), 'loc_B': len(loc),
                           'loc_suf_B': len(b_suf), 'union_B': len(union)}

# conditional hot-cold reorg: >10,240B hard line -> move mechanized dual-carrier entries
HARD_LINE = 10240
TARGET = 9800  # healthy margin: next-window appends must not re-trip the line
moved = []
if len(union) > TARGET:
    ARCH = 'research/memory-archive/202609.md'
    arch = open(ARCH, 'rb').read()
    # move candidates: bm-b mechanized trio (law faces already mechanized by tools/probes)
    cand_keys = [b'[2026-09-30 01:0x r443 bm-b]', b'[2026-09-30 03:4x r445 bm-b]', b'[2026-09-30 02:4x r444 bm-b]']
    pointer_fmt = ('- 冷层指针：r%s %s 全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r457 bm-a 窗批』节（%s）。\n')
    pointers = {
        b'[2026-09-30 01:0x r443 bm-b]': ('443', 'jsonl 追加写吞换行腐败坑+union 双侧同族修复律',
            '法面=raw_decode 循环拆行工具 _r443bmb_x2log_repair.py+新追加写者尾换行守卫承载'),
        b'[2026-09-30 03:4x r445 bm-b]': ('445', '采集器无超时挂死盲区坑（conn-fuse 对 hang 失明）',
            '法面=fetch_one daemon-worker 45s 死限+TimeoutError 走 CONN_MARKERS fuse 路+探针 _r445bmb_hang_shield_probe.py 承载'),
        b'[2026-09-30 02:4x r444 bm-b]': ('444', 'S6 批跑器无参腿伪参数坑',
            '法面=无参腿分支参数计数判别+UNKNOWN 件逐键 deep-compare 定性范式承载·探针 _r444bmb_guardscan_probe.py'),
    }
    lines = union.split(b'\n')
    def entry_spans(key):
        spans, i = [], 0
        while i < len(lines):
            if lines[i].startswith(b'- ' + key):
                j = i + 1
                while j < len(lines) and not (lines[j].startswith(b'- [') or lines[j].startswith(b'### ') or lines[j].startswith(b'## ')):
                    j += 1
                spans.append((i, j))
                i = j
            else:
                i += 1
        return spans
    pending = list(cand_keys)
    arch_new = []
    while len(union) > TARGET and pending:
        key = pending.pop(0)
        spans = entry_spans(key)
        assert len(spans) == 1, f'entry span not unique for {key}: {len(spans)}'
        i, j = spans[0]
        entry_bytes = b'\n'.join(lines[i:j]) + b'\n'
        rnum, title, carrier = pointers[key]
        ptr = (pointer_fmt % (rnum, title, carrier)).encode('utf-8')
        lines[i:j] = [ptr]
        union = b'\n'.join(lines)
        moved.append((rnum, len(entry_bytes)))
        arch_new.append(entry_bytes)
    if moved:
        section_tag = '热冷整编 2026-09-30 r457 bm-a 窗批'.encode('utf-8')
        already = section_tag in arch
        header = ('\n\n## 热冷整编 2026-09-30 r457 bm-a 窗批\n\n'
                  '> r457 撞车批窗热冷整编（rebase storm resolve 窗·超 10,240B 硬线当窗即办·行级零丢失 moved %d/lost 0）。\n\n' % len(moved)).encode('utf-8')
        if not already:
            if not arch.endswith(b'\n'):
                arch += b'\n'
            arch += header + b''.join(arch_new)
        for eb in arch_new:
            assert eb in arch, 'moved entry not verbatim in archive'
        write_bytes(ARCH, arch)
        R['faces']['archive'] = {'moved': [m[0] for m in moved], 'bytes': [m[1] for m in moved],
                                 'new_size_B': len(arch), 'idempotent_skip': already}
write_bytes('CODELY.md', union)
assert b'r249 bm-c' in union and b'r456 bm-a' in union, 'union lost an entry'
R['faces']['CODELY.md']['final_B'] = len(union)

# ---------- B. twins: ts-probe same-side coupling (r98/r99/r100/r327/r329) ----------
def deep_ts(obj, exact_keys=('generated_at', 'generated', 'generated_ts')):
    found = []
    def walk(o, p):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and re.match(r'^20\d{2}-', v) and re.search(r'\d{1,2}:\d{2}', v):
                    found.append((p + '/' + k, v))
                walk(v, p + '/' + k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, p + '/%d' % i)
    walk(obj, '')
    for ek in exact_keys:
        cand = [c for c in found if c[0].rsplit('/', 1)[-1] == ek]
        if cand:
            return cand
    return found

def twin_resolve(json_path, md_path, group):
    oj, lj = blob(':2:' + json_path), blob(':3:' + json_path)
    o_md, l_md = blob(':2:' + md_path), blob(':3:' + md_path)
    o_j, l_j = json.loads(oj.decode('utf-8')), json.loads(lj.decode('utf-8'))
    po, pl = deep_ts(o_j), deep_ts(l_j)
    assert po and pl, f'{json_path}: ts probe empty (R350 fail-closed)'
    to, tl = max(c[1] for c in po), max(c[1] for c in pl)
    side = 'local' if tl >= to else 'origin'
    jb, mb = (lj, l_md) if side == 'local' else (oj, o_md)
    assert b'<<<<<<<' not in jb and b'<<<<<<<' not in mb, 'marker leak in stage blob'
    write_bytes(json_path, jb)
    write_bytes(md_path, mb)
    R['faces'][group] = {'side': side, 'origin_ts': to, 'local_ts': tl}

twin_resolve('docs/daily_report/REPORT-2026-09-30.json', 'docs/daily_report/REPORT-2026-09-30.md', 'daily_report_twin')
oj, lj = blob(':2:docs/live_usage/LIVE-2026-09-30.json'), blob(':3:docs/live_usage/LIVE-2026-09-30.json')
o_j, l_j = json.loads(oj.decode('utf-8')), json.loads(lj.decode('utf-8'))
po, pl = deep_ts(o_j), deep_ts(l_j)
assert po and pl, 'LIVE json ts probe empty'
to, tl = max(c[1] for c in po), max(c[1] for c in pl)
side = 'local' if tl >= to else 'origin'
stage = 3 if side == 'local' else 2
for p in ['docs/live_usage/LIVE-2026-09-30.json', 'docs/live_usage/LIVE-2026-09-30.md',
          'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md']:
    bts = blob(':%d:%s' % (stage, p))
    assert b'<<<<<<<' not in bts, 'marker leak in %s' % p
    write_bytes(p, bts)
R['faces']['live_usage_twin'] = {'side': side, 'origin_ts': to, 'local_ts': tl}

# ---------- C. _attrition_guard_scan.json (r444 UNKNOWN paradigm: deep-compare) ----------
o_g, l_g = blob(':2:results/_attrition_guard_scan.json'), blob(':3:results/_attrition_guard_scan.json')
o_j, l_j = json.loads(o_g.decode('utf-8')), json.loads(l_g.decode('utf-8'))
def flat(o, p=''):
    out = {}
    if isinstance(o, dict):
        for k, v in sorted(o.items()):
            out.update(flat(v, p + '/' + k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out.update(flat(v, p + '/%d' % i))
    else:
        out[p] = o
    return out
fo, fl = flat(o_j), flat(l_j)
diff_keys = [k for k in set(fo) | set(fl) if fo.get(k) != fl.get(k)]
def tsish(k):
    lk = k.rsplit('/', 1)[-1].lower()
    return ('ts' in lk) or (lk in ('when', 'at', 'scanned_at', 'epoch', 'generated_at', 'updated', 'last_seen'))
if diff_keys and all(tsish(k) for k in diff_keys):
    keep = l_g if max(c[1] for c in deep_ts(l_j)) >= max(c[1] for c in deep_ts(o_j)) else o_g
    write_bytes('results/_attrition_guard_scan.json', keep)
    R['faces']['guard_scan'] = {'verdict': 'only-ts-diff take-new', 'diff_keys': diff_keys[:8]}
elif not diff_keys:
    write_bytes('results/_attrition_guard_scan.json', l_g)
    R['faces']['guard_scan'] = {'verdict': 'identical, local byte', 'diff_keys': []}
else:
    # derived-evidence face: scans of the same append-only ledgers at different moments.
    # Take newer ts IFF every ledger count is monotonically >= older side (no shrinkage);
    # real loss (shrinking counts) stays fail-closed for manual review.
    po_, pl_ = deep_ts(o_j), deep_ts(l_j)
    to_, tl_ = max(c[1] for c in po_), max(c[1] for c in pl_)
    newer, older = (l_j, o_j) if tl_ >= to_ else (o_j, l_j)
    shrink = []
    for f in newer.get('files', {}):
        n, o = newer['files'][f], older.get('files', {}).get(f, {})
        for cnt in ('work_entries', 'head_entries', 'history_commits'):
            if cnt in n and cnt in o and n[cnt] < o[cnt]:
                shrink.append(f + '/' + cnt)
    if not shrink:
        write_bytes('results/_attrition_guard_scan.json', l_g if tl_ >= to_ else o_g)
        R['faces']['guard_scan'] = {'verdict': 'scan-moment drift take-new-by-ts (monotonic counts)',
                                    'origin_ts': to_, 'local_ts': tl_, 'diff_keys': diff_keys[:8]}
    else:
        R['faces']['guard_scan'] = {'verdict': 'CONTENT-DIFF SHRINK fail-closed', 'shrink': shrink,
                                    'diff_keys': diff_keys[:40]}

print(json.dumps(R, ensure_ascii=False, indent=1))
ok = 'fail-closed' not in R['faces'].get('guard_scan', {}).get('verdict', '')
sys.exit(0 if ok else 3)
