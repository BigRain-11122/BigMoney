# r459 bm-a storm resolver (r457 paradigm): rebase UU batch canonical resolution.
# Fork: local r458 (eb0de1814) + autofill tick (38e9e10b0) replayed onto origin/main
# (ffa2eabc5 r446 bm-b W12 SCREEN finalize + 3aa3c8a3b CODELY + ee6832525 autofill claim).
# Rebase stage law r351: :2: = origin side, :3: = local side, :1: = merge base.
# Faces here: archive union (both sides base-prefixed tail appends), CODELY hot-cold
# reorg (auto-merged 10,485B > 10,240B hard line -> move mechanized-carrier entries),
# twins x6 ts-probe same-side, scorecards x2 + dashboard x2 + fundamental take-new
# deep-ts probe (r100/R350 hardened), guard_scan r444 deep-compare monotonic take-new.
# ALL_FACES x6 already resolved by scripts/merge_lane_views.py resolve in the driver.
# IDEMPOTENCY (r457 pit law): archive final content is a PURE FUNCTION of blobs
# (union + reorg section computed then written once) -> re-run byte-identical.
# If a prior run died mid-way: git checkout -- CODELY.md (restore staged face) first.
import subprocess, json, re, sys

def blob(spec):
    r = subprocess.run(['git', 'show', spec], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('git show %s failed: %s' % (spec, r.stderr[:200]))
    return r.stdout

def write_bytes(path, data):
    with open(path, 'wb') as f:
        f.write(data)

R = {'faces': {}}

# ---------- A. archive union: base + local suffix + origin suffix (zero-loss) ----------
ARCH = 'research/memory-archive/202609.md'
b = blob(':1:' + ARCH); o = blob(':2:' + ARCH); l = blob(':3:' + ARCH)
assert o.startswith(b) and l.startswith(b), 'archive side not base-prefixed (in-place edit!)'
loc_suf = l[len(b):]; org_suf = o[len(b):]
union_arch = b + loc_suf + org_suf
for must in ['热冷整编 2026-09-30 r446 bm-b 窗批', '热冷整编 2026-09-30 r458 bm-a 窗批']:
    assert must.encode('utf-8') in union_arch, 'archive union lost section: %s' % must
R['faces']['archive_union'] = {'base_B': len(b), 'org_suf_B': len(org_suf), 'loc_suf_B': len(loc_suf)}

# ---------- B. CODELY.md hot-cold reorg (auto-merged 10,485B > 10,240B hard line) ----------
# Re-run safety (r457 non-idempotent-append pit law): detect prior-move state FIRST via
# pointer presence (NOT via size re-check -- slimmed CODELY would skip the whole block and
# drop the reorg section from the rebuilt archive = silent entry loss).
HARD_LINE, TARGET = 10240, 9800
cod = open('CODELY.md', 'rb').read()
R['faces']['CODELY_premerge_B'] = len(cod)
moved, arch_extra = [], b''
reorg_tag = '热冷整编 2026-09-30 r459 bm-a 窗批'
ptr_fmt = '- 冷层指针：r%s %s 全文 verbatim=archive 202609.md『%s』节（%s）。\n'
pointers = {
    b'[2026-09-30 03:2x r249 bm-c]': ('249', 'pandas to_csv 浮点回读非逐位坑（W5 runner selftest 首跑实弹）',
        '法面=W5 runner selftest derive-then-freeze CSV-readback 锚范式承载'),
    b'[2026-09-30 03:5x r456 bm-a]': ('456', 'a158 冻结面抽位点对账 eps 分母坑（W13 探针首跑实弹）',
        '法面=a158_tsgate_probe 参考式同款 eps 分母+镜像孪生族构造恒等自检承载'),
    b'[2026-09-30 04:2x r457 bm-a]': ('457', '风暴 resolver 非幂等追加坑',
        '法面=resolver 幂等守卫（目标节 tag 探测+纯函数写回）承载'),
}
already = '冷层指针：r249'.encode('utf-8') in cod
if already:
    # prior run of THIS window already moved entries: recover the reorg section verbatim
    # from the working-tree archive (prior run appended it at file end) and re-attach --
    # the blob-derived union alone would silently drop it.
    cur_arch = open(ARCH, 'rb').read()
    tag_b = ('## ' + reorg_tag).encode('utf-8')
    idx = cur_arch.find(tag_b)
    assert idx >= 2 and cur_arch[idx-2:idx] == b'\n\n', 'reorg section not recoverable from working archive'
    arch_extra = cur_arch[idx-2:]
    moved = [rnum for rnum in ('249', '456', '457')
             if ('冷层指针：r%s' % rnum).encode('utf-8') in cod]
    assert moved, 're-run detected but no moved pointers found'
    for key, rnum in [(k, v[0]) for k, v in pointers.items()]:
        if rnum in moved:
            assert (b'- ' + key) in arch_extra, 're-run: moved entry r%s not verbatim in recovered section' % rnum
    R['faces']['CODELY_reorg'] = {'idempotent_recover': True, 'moved': moved}
elif len(cod) > TARGET:
    lines = cod.split(b'\n')
    def entry_spans(key):
        spans, i = [], 0
        while i < len(lines):
            if lines[i].startswith(b'- ' + key):
                j = i + 1
                while j < len(lines) and not (lines[j].startswith(b'- [') or lines[j].startswith(b'### ') or lines[j].startswith(b'## ')):
                    j += 1
                spans.append((i, j)); i = j
            else:
                i += 1
        return spans
    pending = list(pointers.keys()); arch_new = []
    while len(cod) > TARGET and pending:
        key = pending.pop(0)
        spans = entry_spans(key)
        assert len(spans) == 1, 'entry span not unique for %s: %d' % (key, len(spans))
        i, j = spans[0]
        entry_bytes = b'\n'.join(lines[i:j]) + b'\n'
        rnum, title, carrier = pointers[key]
        ptr = (ptr_fmt % (rnum, title, reorg_tag, carrier)).encode('utf-8')
        lines[i:j] = [ptr[:-1]]  # span slice excludes trailing \n split
        cod = b'\n'.join(lines)
        moved.append(rnum)
        arch_new.append(entry_bytes)
    assert moved, 'reorg moved nothing yet CODELY still over target'
    header = ('\n\n## %s\n\n> r459 rebase storm 窗热冷整编（CODELY auto-merge 10,485B 超 10,240B 硬线'
              '当窗即办·行级零丢失 moved %d/lost 0）。\n\n' % (reorg_tag, len(moved))).encode('utf-8')
    arch_extra = header + b''.join(arch_new)
    for eb in arch_new:
        assert eb in arch_extra, 'moved entry not verbatim in reorg section'
    R['faces']['CODELY_reorg'] = {'moved': moved}
for rnum in moved:
    assert ('冷层指针：r%s' % rnum).encode('utf-8') in cod, 'pointer missing for r%s' % rnum
assert len(cod) <= HARD_LINE, 'CODELY still over hard line: %d' % len(cod)
R['faces']['CODELY_reorg']['final_B'] = len(cod)

# write archive ONCE: union + (reorg section if any) -- pure function of blobs+cod
final_arch = union_arch
if arch_extra:
    assert reorg_tag.encode('utf-8') not in union_arch, 'reorg tag already in union blobs'
    if not final_arch.endswith(b'\n'):
        final_arch += b'\n'
    final_arch += arch_extra
write_bytes(ARCH, final_arch)
write_bytes('CODELY.md', cod)
R['faces']['archive_final_B'] = len(final_arch)

# ---------- C. deep-ts probe (r100/R350 hardened: value ^20xx- AND time-of-day) ----------
def deep_ts(obj):
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
    return found

def take_new_json(path, face):
    oj, lj = blob(':2:' + path), blob(':3:' + path)
    o_j, l_j = json.loads(oj.decode('utf-8')), json.loads(lj.decode('utf-8'))
    po, pl = deep_ts(o_j), deep_ts(l_j)
    assert po and pl, '%s: ts probe empty (R350 fail-closed)' % path
    to, tl = max(c[1] for c in po), max(c[1] for c in pl)
    side = 'local' if tl >= to else 'origin'
    keep = lj if side == 'local' else oj
    assert b'<<<<<<<' not in keep, 'marker leak in %s' % path
    write_bytes(path, keep)
    R['faces'][face] = {'side': side, 'origin_ts': to, 'local_ts': tl}
    return side

# ---------- D. twins: same-side coupling (r98/r99/r100/r329) ----------
def twin_resolve(json_path, md_path, group):
    oj, lj = blob(':2:' + json_path), blob(':3:' + json_path)
    o_md, l_md = blob(':2:' + md_path), blob(':3:' + md_path)
    o_j, l_j = json.loads(oj.decode('utf-8')), json.loads(lj.decode('utf-8'))
    po, pl = deep_ts(o_j), deep_ts(l_j)
    assert po and pl, '%s: ts probe empty' % json_path
    to, tl = max(c[1] for c in po), max(c[1] for c in pl)
    side = 'local' if tl >= to else 'origin'
    jb, mb = (lj, l_md) if side == 'local' else (oj, o_md)
    assert b'<<<<<<<' not in jb and b'<<<<<<<' not in mb, 'marker leak in stage blob'
    write_bytes(json_path, jb); write_bytes(md_path, mb)
    R['faces'][group] = {'side': side, 'origin_ts': to, 'local_ts': tl}

twin_resolve('docs/daily_report/REPORT-2026-09-30.json', 'docs/daily_report/REPORT-2026-09-30.md', 'daily_report_twin')
side = take_new_json('docs/live_usage/LIVE-2026-09-30.json', 'live_usage_probe')
stage = 3 if side == 'local' else 2
for p in ['docs/live_usage/LIVE-2026-09-30.json', 'docs/live_usage/LIVE-2026-09-30.md',
          'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md']:
    bts = blob(':%d:%s' % (stage, p))
    assert b'<<<<<<<' not in bts, 'marker leak in %s' % p
    write_bytes(p, bts)
R['faces']['live_usage_twin'] = {'side': side}

# ---------- E. snapshot faces: take-new hardened probe ----------
take_new_json('results/scorecard_v1.json', 'scorecard_v1')
take_new_json('results/strategy_scorecard.json', 'strategy_scorecard')

# dashboard pair: probe .json side, take SAME side whole bytes for .js (R209 wrapper)
side = take_new_json('results/dashboard_status.json', 'dashboard_probe')
stage = 3 if side == 'local' else 2
js = blob(':%d:results/dashboard_status.js' % stage)
assert b'<<<<<<<' not in js and js.lstrip().startswith(b'window.DASH_DATA'), 'js wrapper shape violation'
write_bytes('results/dashboard_status.js', js)
R['faces']['dashboard_pair'] = {'side': side}

take_new_json('results/fundamental_b_layer_filter.json', 'fundamental_b_layer')

# ---------- F. guard_scan (r444 deep-compare + monotonic take-new) ----------
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
po_, pl_ = deep_ts(o_j), deep_ts(l_j)
to_, tl_ = max(c[1] for c in po_), max(c[1] for c in pl_)
newer, older = (l_j, o_j) if tl_ >= to_ else (o_j, l_j)
shrink = []
for f in newer.get('files', {}):
    n, o2 = newer['files'][f], older.get('files', {}).get(f, {})
    for cnt in ('work_entries', 'head_entries', 'history_commits'):
        if cnt in n and cnt in o2 and n[cnt] < o2[cnt]:
            shrink.append(f + '/' + cnt)
if not diff_keys:
    write_bytes('results/_attrition_guard_scan.json', l_g)
    R['faces']['guard_scan'] = {'verdict': 'identical, local byte'}
elif not shrink:
    write_bytes('results/_attrition_guard_scan.json', l_g if tl_ >= to_ else o_g)
    R['faces']['guard_scan'] = {'verdict': 'scan-moment drift take-new-by-ts (monotonic counts)',
                                'origin_ts': to_, 'local_ts': tl_, 'diff_keys': diff_keys[:8]}
elif all(s.split('/')[0] != 'gate_attrition.bm-a.json' for s in shrink) \
        and all(not (f.get('active_loss_keys') or []) for f in newer.get('files', {}).values()) \
        and all(not (f.get('active_loss_keys') or []) for f in older.get('files', {}).values()):
    # cross-tree lane-lag adjudication (r85 禁按行数直判丢失律): shrink confined to OTHER
    # machines' lane ledgers + zero active-loss on both sides = the older scan's tree simply
    # carried a fresher own-lane append (bm-b W12) that the newer pre-rebase tree lacked.
    # Take the side with the LARGER count on the shrinking file (matches post-rebase tree);
    # the S7 fresh scan re-derives everything on the merged tree this same round.
    f0, cnt0 = shrink[0].split('/')
    bigger = 'origin' if o_j['files'][f0][cnt0] >= l_j['files'][f0][cnt0] else 'local'
    write_bytes('results/_attrition_guard_scan.json', o_g if bigger == 'origin' else l_g)
    R['faces']['guard_scan'] = {'verdict': 'cross-tree lane-lag adjudicated take-%s (r85 no-count-verdict law)' % bigger,
                                'shrink': shrink, 'origin_ts': to_, 'local_ts': tl_,
                                'note': 'local scan ran on pre-rebase tree lacking bm-b W12 lane append (arrives via this rebase); both sides active_loss_keys=[]; S7 scan re-derives on merged tree'}
else:
    R['faces']['guard_scan'] = {'verdict': 'CONTENT-DIFF SHRINK fail-closed', 'shrink': shrink,
                                'diff_keys': diff_keys[:40]}

# ---------- G. parse-verify every written json + moved-entry verbatim ----------
MOVED_KEYS = [(b'[2026-09-30 03:2x r249 bm-c]', '249'), (b'[2026-09-30 03:5x r456 bm-a]', '456'),
              (b'[2026-09-30 04:2x r457 bm-a]', '457')]
parse_fail = []
for key, rnum in MOVED_KEYS:
    if rnum in moved:
        assert final_arch.find(b'- ' + key) >= 0, 'moved entry not verbatim in archive: r%s' % rnum
for p in ['docs/daily_report/REPORT-2026-09-30.json', 'docs/live_usage/LIVE-2026-09-30.json',
          'docs/live_usage/LIVE-latest.json', 'results/scorecard_v1.json',
          'results/strategy_scorecard.json', 'results/dashboard_status.json',
          'results/fundamental_b_layer_filter.json', 'results/_attrition_guard_scan.json',
          'results/compute_audit.json', 'results/regime_state.json', 'results/futures_update_status.json',
          'results/lhb_update_status.json', 'results/update_status.json', 'results/token_usage.json']:
    try:
        json.load(open(p, encoding='utf-8'))
    except Exception as e:
        parse_fail.append('%s: %s' % (p, str(e)[:120]))
R['parse_verify'] = 'all-written-json-ok' if not parse_fail else {'FAIL': parse_fail}

print(json.dumps(R, ensure_ascii=False, indent=1))
ok = (not parse_fail) and 'fail-closed' not in R['faces'].get('guard_scan', {}).get('verdict', '')
sys.exit(0 if ok else 3)
