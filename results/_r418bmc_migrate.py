# -*- coding: utf-8 -*-
# r418 bm-c: D-06 pre-split survivors batch-1 migration (7 entries -> 3 domain files)
# T-2026-10-02-144(c) · r373/r380/r387 split precedent · r410/r411 incremental-sweep format
# Zero-loss law: verbatim line migration, machine-move (no hand-copy), all assertions
# must PASS before any disk write. Disk face = CRLF everywhere; accounting core = LF.
# v2: uniform logical-line handling (split->rstrip CR->operate->join CRLF). v1 had
# join('\r\n') over split('\n') lines already carrying \r = \r\r\n whole-file face
# corruption (r289/r500 family), rolled back via git checkout before this rewrite.
import hashlib, json, sys

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
CODELY = REPO + r'\CODELY.md'

BATCH = {
    'research/pit-pool.md': [
        ('r489', '- [2026-10-01 r489 bm-b] 池翻面双层坑'),
        ('r511', '- [2026-10-01 11:2x r511 bm-a] pool worker initializer'),
        ('r327', '- [2026-10-01 18:1x r327 bm-c] 亚百毫秒单元池化 IPC'),
    ],
    'research/pit-engine.md': [
        ('r307', '- [2026-10-01 09:3x r307 bm-c] 常供面波带尾律算术撞值跳位'),
        ('r494', '- [2026-10-01 05:5x r494 bm-b] 波次 runner 复制粘贴键漂移坑'),
    ],
    'research/pit-git.md': [
        ('r294a', '- [2026-10-01 r294 bm-c] append-only 台账 union 合并去重域坑'),
        ('r294b', '- [2026-10-01 r294 bm-c] 共享树 amend 撞劫坑'),
    ],
}

ROUND_TAG = 'r418 bm-c'

def load_logical(path):
    raw = open(path, 'rb').read()
    text = raw.decode('utf-8')
    trailing = text.endswith('\r\n')
    lines = [ln.rstrip('\r') for ln in text.split('\n')]
    if trailing and lines and lines[-1] == '':
        lines.pop()
    return lines, trailing, len(raw)

def save_logical(path, lines, trailing):
    text = '\r\n'.join(lines) + ('\r\n' if trailing else '')
    open(path, 'wb').write(text.encode('utf-8'))
    return len(text.encode('utf-8'))

# --- load CODELY ---
clines, ctrailing, cold_b = load_logical(CODELY)

# --- locate target lines (unique head-prefix match after lstrip) ---
found = {}
for lst in BATCH.values():
    for key, prefix in lst:
        hits = [i for i, ln in enumerate(clines) if ln.lstrip(' ').startswith(prefix)]
        if len(hits) != 1:
            print('FAIL locate %s hits=%d' % (key, len(hits)))
            sys.exit(2)
        found[key] = (hits[0], clines[hits[0]].lstrip(' '))

# --- plan ---
plan = {}
for path, entries in BATCH.items():
    moved = [found[k][1] for k, _ in entries]
    lf_core = sum(len(e.encode('utf-8')) + 1 for e in moved)
    codely_removed = sum(len(clines[found[k][0]].encode('utf-8')) + 2 for k, _ in entries)  # +CRLF
    plan[path] = dict(moved=moved, lf_core=lf_core, codely_removed=codely_removed)

# --- CODELY removal ---
drop = set(found[k][0] for k in found)
new_clines = [ln for i, ln in enumerate(clines) if i not in drop]
new_codely_b = len(('\r\n'.join(new_clines) + ('\r\n' if ctrailing else '')).encode('utf-8'))

# --- domain transforms + assertions ---
SWEEP = '> 增量回扫行（%s·T-2026-10-02-144(c)·D-06 pre-split survivors 批次一）：热层条目 %d 条 verbatim 追加（pre-split 存留条·%s）·追加核 %d B（LF blob 面）·零丢失断言 PASS（逐行 verbatim 在场+源件零残留·机械迁移非手抄·r399 范式同源；整行迁移）'

results = {}
for path, info in plan.items():
    fp = REPO + '\\' + path
    dl, dtrailing, dpre_b = load_logical(fp)
    # head block: insert sweep line after last '>' line
    last_gt = max(i for i, ln in enumerate(dl) if ln.startswith('>'))
    names = '、'.join('[' + e.split(']')[0].lstrip('- ').strip() + ']' for e in info['moved'])
    dl.insert(last_gt + 1, SWEEP % (ROUND_TAG, len(info['moved']), names, info['lf_core']))
    # tail: strip trailing blanks, add one blank separator, then entries
    while dl and dl[-1] == '':
        dl.pop()
    dl.append('')
    dl.extend(info['moved'])
    new_dtext = '\r\n'.join(dl) + ('\r\n' if dtrailing else '')
    ndl = new_dtext.split('\r\n')
    # assertion 1: verbatim present as full logical line
    for e in info['moved']:
        assert e in ndl, 'verbatim-present FAIL %s' % path
    # assertion 2: zero residue in new CODELY
    for e in info['moved']:
        assert e not in new_clines, 'source-residue FAIL %s' % path
    # assertion 3: no \r\r\n corruption anywhere
    assert '\r\r\n' not in new_dtext, 'CRLF-corruption FAIL %s' % path
    lf_blob_md5 = hashlib.md5(new_dtext.replace('\r\n', '\n').encode('utf-8')).hexdigest()
    results[path] = dict(pre_bytes_disk=dpre_b, post_bytes_disk=len(new_dtext.encode('utf-8')),
                         lf_core_added=info['lf_core'], codely_removed_disk=info['codely_removed'],
                         entries=len(info['moved']), lf_blob_md5=lf_blob_md5)
    info['new_text'] = new_dtext

# CODELY byte accounting check
removed_total = sum(i['codely_removed'] for i in plan.values())
moved_lf_total = sum(i['lf_core'] for i in plan.values())
delta = cold_b - new_codely_b
print('CODELY %d -> %d (delta=%d, removed_line_bytes=%d, moved_lf_core=%d)' % (cold_b, new_codely_b, delta, removed_total, moved_lf_total))
assert delta == removed_total, 'CODELY byte-accounting FAIL (delta=%d expected=%d)' % (delta, removed_total)
assert '\r\r\n' not in '\r\n'.join(new_clines), 'CODELY CRLF-corruption FAIL'

# --- all green: write ---
for path, info in plan.items():
    open(REPO + '\\' + path, 'wb').write(info['new_text'].encode('utf-8'))
    print('WROTE %s (+%d, %d->%d diskB, lf-md5=%s)' % (path, results[path]['entries'], results[path]['pre_bytes_disk'], results[path]['post_bytes_disk'], results[path]['lf_blob_md5']))
save_logical(CODELY, new_clines, ctrailing)
print('WROTE CODELY.md %d -> %d' % (cold_b, new_codely_b))

receipt = dict(round=ROUND_TAG, ticket='T-2026-10-02-144(c)', batch='D-06 pre-split survivors batch-1',
               entries_total=7, domains=results,
               codely=dict(pre_bytes=cold_b, post_bytes=new_codely_b, removed_line_bytes_disk=removed_total, moved_lf_core=moved_lf_total),
               law='verbatim line migration, machine-move, all assertions PASS before write')
open(REPO + r'\results\_r418bmc_survivors_batch1.json', 'w', encoding='utf-8').write(json.dumps(receipt, ensure_ascii=False, indent=1))
print('RECEIPT WRITTEN')
