# -*- coding: utf-8 -*-
# r431 bm-c: D-06 post-split increment sweep batch
# (4 pits -> pit-spawn x2 / pit-git x1 / pit-tooling x1; 1 flow-sink r628 -> archive 202610.md)
# T-2026-10-02-144(c) · r418 migrate precedent (logical-line CRLF law) · r399/r420 sweep format
# Zero-loss law: verbatim line migration, machine-move, all assertions must PASS before any write.
import hashlib, json, sys

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
CODELY = REPO + r'\CODELY.md'
ARCHIVE = REPO + r'\research\memory-archive\202610.md'
ROUND_TAG = 'r431 bm-c'

PITS = {
    'research/pit-spawn.md': [
        ('r422', '- [2026-10-03 16:3x r422 bm-c]'),
        ('r426', '- [2026-10-03 20:1x r426 bm-c]'),
    ],
    'research/pit-git.md': [
        ('r423', '- [2026-10-03 18:0x r423 bm-c]'),
    ],
    'research/pit-tooling.md': [
        ('r629', '- [2026-10-03 19:0x r629 bm-b]'),
    ],
}
FLOW = ('r628', '- [2026-10-03 19:1x r628 bm-b]')

PTR_EXT = [
    ('- 域指针·D-20261002-06 首拆件',
     '；r431 bm-c 增量回扫 1 条（10-03 18:0x r423 merge 窗三连坑——origin 残留 marker 全仓扫+porcelain UU 全量扫+push 前三 fetch 复核）已入件（件内对账行为准）'),
    ('- 域指针·D-20261002-06 spawn/tooling 域拆件',
     '；r431 bm-c 增量回扫 2 条（r422 三代执行体连环斩首收养律/r426 多子进程链驱动器禁经 CreateNoWindow 包装器点火律）已入件（件内对账行为准）'),
    ('- 域指针·D-20261002-06 census/tooling 域拆件',
     '；r431 bm-c 增量回扫 1 条（r629 rehearsal/harness 镜像=调用点守卫复刻律）已入件（件内对账行为准）'),
]

COLD_PTR = ('- 冷层指针（r431 整编·T-144(c) 流水下沉腿·r444 范式）：r628 bm-b §4 跳位语义钉死行 bm-b 面回执'
            '（selftest 9/9 实跑流水行）——全文 verbatim=research/memory-archive/202610.md'
            '『热冷整编 2026-10-03 r431 bm-c 窗批』节。')

ARCH_NOTE = ('（T-144(c) 流水下沉腿·r444 范式·行级零丢失校验；r628 bm-b §4 跳位语义钉死行 bm-b 面回执流水行自 CODELY.md 热层'
             ' verbatim 迁入；同窗域增量回扫 4 条分域入件（pit-spawn×2：r422/r426·pit-git×1：r423·pit-tooling×1：r629）·各件对账行为准）')

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

clines, ctrailing, cold_b = load_logical(CODELY)

# --- 1) locate the 5 hot-layer entries (unique head-prefix match) ---
found = {}
for lst in PITS.values():
    for key, prefix in lst:
        hits = [i for i, ln in enumerate(clines) if ln.lstrip(' ').startswith(prefix)]
        if len(hits) != 1:
            print('FAIL locate %s hits=%d' % (key, len(hits)))
            sys.exit(2)
        found[key] = (hits[0], clines[hits[0]].lstrip(' '))
key, prefix = FLOW
hits = [i for i, ln in enumerate(clines) if ln.lstrip(' ').startswith(prefix)]
if len(hits) != 1:
    print('FAIL locate %s hits=%d' % (key, len(hits)))
    sys.exit(2)
found[key] = (hits[0], clines[hits[0]].lstrip(' '))
for k in found:
    print('LOC %s -> %s' % (k, found[k][1][:44]))

# --- 2) pointer-line extensions (idempotency + endswith guard) ---
ext_added = 0
for ptr_prefix, note in PTR_EXT:
    phits = [i for i, ln in enumerate(clines) if ln.startswith(ptr_prefix)]
    if len(phits) != 1:
        print('FAIL locate ptr-line %s hits=%d' % (ptr_prefix[:30], len(phits)))
        sys.exit(2)
    i = phits[0]
    if 'r431 bm-c 增量回扫' in clines[i]:
        print('FAIL idempotency: r431 note already in ptr line')
        sys.exit(2)
    if not clines[i].endswith('。'):
        print('FAIL ptr line does not end with 。: %s' % clines[i][-40:])
        sys.exit(2)
    clines[i] = clines[i][:-1] + note + '。'
    ext_added += len(note.encode('utf-8'))

# --- 3) remove the 5 entries ---
drop = set(found[k][0] for k in found)
removed_total = sum(len(clines[i].encode('utf-8')) + 2 for i in drop)  # CRLF face
new_clines = [ln for i, ln in enumerate(clines) if i not in drop]

# --- 4) cold-pointer line after last '- 冷层指针' line ---
cphits = [i for i, ln in enumerate(new_clines) if ln.startswith('- 冷层指针')]
if not cphits:
    print('FAIL no 冷层指针 anchor line')
    sys.exit(2)
new_clines.insert(cphits[-1] + 1, COLD_PTR)
cold_added = len(COLD_PTR.encode('utf-8')) + 2

# --- 5) CODELY byte accounting ---
new_codely_text = '\r\n'.join(new_clines) + ('\r\n' if ctrailing else '')
new_codely_b = len(new_codely_text.encode('utf-8'))
delta = cold_b - new_codely_b
expect_delta = removed_total - ext_added - cold_added
print('CODELY %d -> %d (delta=%d expect=%d removed=%d ext=%d cold=%d)'
      % (cold_b, new_codely_b, delta, expect_delta, removed_total, ext_added, cold_added))
if delta != expect_delta:
    print('FAIL CODELY byte-accounting')
    sys.exit(2)
if '\r\r\n' in new_codely_text:
    print('FAIL CODELY CRLF-corruption')
    sys.exit(2)
for k in found:
    if found[k][1] in new_clines:
        print('FAIL source-residue %s' % k)
        sys.exit(2)

# --- 6) pit-file transforms (anti-dup -> sweep line -> tail append -> assertions) ---
SWEEP = ('> 增量回扫行（%s·T-2026-10-02-144(c)·D-06 post-split 增量批次）：热层条目 %d 条 verbatim 追加'
         '（10-03 批·%s）·追加核 %d B（LF blob 面·md5=%s）·零丢失断言 PASS'
         '（逐行 verbatim 在场+源件 CODELY.md 零残留·机械迁移非手抄·r399/r420 范式同源）。')

results = {}
pit_texts = {}
for path, entries in PITS.items():
    fp = REPO + '\\' + path
    dl, dtrailing, dpre_b = load_logical(fp)
    moved = [found[k][1] for k, _ in entries]
    for k, _ in entries:
        if sum(1 for ln in dl if ln == found[k][1]):
            print('FAIL anti-dup: %s already in %s' % (k, path))
            sys.exit(2)
    lf_core = sum(len(e.encode('utf-8')) + 1 for e in moved)
    core_md5 = hashlib.md5(('\n'.join(moved) + '\n').encode('utf-8')).hexdigest()
    names = '、'.join('[' + e.split(']')[0].lstrip('- ').strip() + ']' for e in moved)
    sweep_line = SWEEP % (ROUND_TAG, len(moved), names, lf_core, core_md5)
    last_gt = max(i for i, ln in enumerate(dl) if ln.startswith('>'))
    dl.insert(last_gt + 1, sweep_line)
    while dl and dl[-1] == '':
        dl.pop()
    dl.append('')
    dl.extend(moved)
    new_dtext = '\r\n'.join(dl) + ('\r\n' if dtrailing else '')
    ndl = new_dtext.split('\r\n')
    for e in moved:
        if e not in ndl:
            print('FAIL verbatim-present %s' % path)
            sys.exit(2)
    if '\r\r\n' in new_dtext:
        print('FAIL CRLF-corruption %s' % path)
        sys.exit(2)
    lf_blob_md5 = hashlib.md5(new_dtext.replace('\r\n', '\n').encode('utf-8')).hexdigest()
    results[path] = dict(pre_bytes_disk=dpre_b, post_bytes_disk=len(new_dtext.encode('utf-8')),
                         entries=len(moved), lf_core_added=lf_core, core_md5=core_md5,
                         lf_blob_md5=lf_blob_md5, codely_removed_disk=sum(len(e.encode('utf-8')) + 2 for e in moved))
    pit_texts[path] = new_dtext
    print('PLAN %s +%d (%d->%d diskB, core-md5=%s)' % (path, len(moved), dpre_b, results[path]['post_bytes_disk'], core_md5))

# --- 7) archive flow-sink ---
al, atrailing, apre_b = load_logical(ARCHIVE)
if sum(1 for ln in al if ln == found['r628'][1]):
    print('FAIL anti-dup: r628 already in archive')
    sys.exit(2)
while al and al[-1] == '':
    al.pop()
al.append('')
al.append('## 热冷整编 2026-10-03 r431 bm-c 窗批')
al.append('')
al.append(ARCH_NOTE)
al.append('')
al.append(found['r628'][1])
new_atext = '\r\n'.join(al) + ('\r\n' if atrailing else '')
if found['r628'][1] not in new_atext.split('\r\n'):
    print('FAIL archive verbatim-present')
    sys.exit(2)
if '\r\r\n' in new_atext:
    print('FAIL archive CRLF-corruption')
    sys.exit(2)
archive_added = len(new_atext.encode('utf-8')) - apre_b
print('PLAN archive %d -> %d diskB (+%d)' % (apre_b, len(new_atext.encode('utf-8')), archive_added))

# --- all green: write ---
for path, txt in pit_texts.items():
    open(REPO + '\\' + path, 'wb').write(txt.encode('utf-8'))
    print('WROTE %s' % path)
open(ARCHIVE, 'wb').write(new_atext.encode('utf-8'))
print('WROTE archive 202610.md')
save_logical(CODELY, new_clines, ctrailing)
print('WROTE CODELY.md %d -> %d' % (cold_b, new_codely_b))

receipt = dict(round=ROUND_TAG, ticket='T-2026-10-02-144(c)', batch='D-06 post-split increment sweep + flow-sink',
               pits=results,
               flow_sink=dict(target='research/memory-archive/202610.md', entry='r628 bm-b §4 receipt',
                              added_bytes_disk=archive_added,
                              cold_ptr_line=COLD_PTR[:60] + '...'),
               codely=dict(pre_bytes=cold_b, post_bytes=new_codely_b, removed_line_bytes_disk=removed_total,
                           ptr_ext_added_bytes=ext_added, cold_ptr_added_bytes=cold_added),
               law='verbatim line migration, machine-move, all assertions PASS before write')
open(REPO + r'\results\_r431bmc_pit_sweep.json', 'w', encoding='utf-8').write(json.dumps(receipt, ensure_ascii=False, indent=1))
print('RECEIPT WRITTEN results/_r431bmc_pit_sweep.json')
