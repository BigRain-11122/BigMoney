# r783 bm-b D-06 migration -- completion leg (main already written by v4; finish registry + receipt + final verify)
import json, hashlib, os

os.chdir(r'C:\Fluxgroup\FluxGroup\quant\bigmoney')
MAIN = 'CODELY.md'
LINE_LIMIT = 30720
REG = 'knowledge/TREASURE_REGISTRY.md'
ANCHORS = {'r782_worksnap': ('research/pit-git-resolver.md', '- [2026-10-06 21:3x r782 bm-b] **worksnap 同名互覆'),
           'r639_lineage_stepper': ('research/pit-lineage-legdiff.md', '- [2026-10-06 20:5x r639 bm-c] **血统机械步进')}
PTR_HEAD = '- 域指针·r783 bm-b 增量回扫批'

def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]

receipt = {'ritual': 'r441/r703 migration ritual (completion leg after v4 main-write)', 'entries': {}, 'asserts': [], 'sizes': {}}

# --- main final state ---
main_raw = open(MAIN, 'rb').read()
main_txt = main_raw.decode('utf-8')
receipt['sizes']['main_before'] = 31854
receipt['sizes']['main_after'] = len(main_raw)
assert len(main_raw) <= LINE_LIMIT, 'main over line: %d' % len(main_raw)
assert main_txt.count(PTR_HEAD) == 1, 'pointer row missing/dup in main'
for key, (tgt, anchor) in ANCHORS.items():
    assert anchor not in main_txt, 'entry still in main: %s' % key
receipt['asserts'].append('main %d -> %d B (<=30720), ptr row x1, both entries removed' % (receipt['sizes']['main_before'], len(main_raw)))

# --- marker scan: MAIN only (domain pit files legitimately quote markers in law text) ---
for m in (b'<<<<<<< ', b'>>>>>>> ', b'||||||| '):
    assert m not in main_raw, 'conflict marker %r in main' % m
receipt['asserts'].append('marker scan clean on main (domain pit files exempt: they document markers verbatim)')

# --- domain files: verbatim x1 + under line ---
for key, (tgt, anchor) in ANCHORS.items():
    traw = open(tgt, 'rb').read()
    eb = anchor.encode('utf-8')  # anchor is the entry-line prefix; verify full line via line-start match
    lines_t = traw.decode('utf-8').splitlines()
    full = [ln for ln in lines_t if ln.startswith(anchor)]
    assert len(full) == 1, 'entry count != 1 in %s: %d' % (tgt, len(full))
    entry_b = full[0].encode('utf-8')
    assert len(traw) <= LINE_LIMIT, 'target over line: %s %d' % (tgt, len(traw))
    receipt['entries'][key] = {'target': tgt, 'bytes': len(entry_b), 'sha16': sha16(entry_b), 'target_bytes_after': len(traw)}
    receipt['asserts'].append('%s verbatim x1 in %s (%d B, sha16 %s, file %d B)' % (key, tgt, len(entry_b), sha16(entry_b), len(traw)))

# --- all-domain sweep ---
pit = [f for f in os.listdir('research') if f.startswith('pit-') and f.endswith('.md')]
over = [(f, os.path.getsize(os.path.join('research', f))) for f in pit if os.path.getsize(os.path.join('research', f)) > LINE_LIMIT]
assert not over, 'domain files over line: %r' % over
receipt['asserts'].append('all %d pit-*.md <= 30720B' % len(pit))
receipt['pit_files'] = len(pit)

# --- registry in/out record line (append-only, skip if present) ---
reg_line = ('- 2026-10-06 21:2x bm-b r783 D-06 主件回弹增量回扫迁移仪式（D-20261002-06 主件 ≤30KB 判据腿·r441/r703 仪式同款）：'
            'prescan 实弹 rc3 命中 research/pit-git-resolver.md+pit-lineage-legdiff.md（research/ 全族 fail-closed 面）——'
            '集团拆件令 D-20261002-06（主件+域件 ≤30KB·收口窗 10-07 12:00）授权 TREASURE_PROTECTION_LAW §2 迁移仪式三件齐：'
            '①prescan rc3 留痕（本行）②出入记录本行 ③零丢失断言：CODELY.md 主件 %d→%d 回线（2 条增量坑律 verbatim 迁出非手抄：'
            'r782 worksnap 三连坑→pit-git-resolver.md〔%dB·sha16 %s〕+r639 血统机械步进坑→pit-lineage-legdiff.md〔%dB·sha16 %s〕·'
            '逐条 bytes-in-target verbatim x1 验证·主件结构恒等（原行集-2 条目-1 空行+指针行+尾 EOL 愈合）·'
            'receipt=results/_r783bmb_codely_increment.json）；域件面=纯加性 append 零删除·在册路径保留非删除·CODELY.md 指针行随批新增。') % (
    receipt['sizes']['main_before'], receipt['sizes']['main_after'],
    receipt['entries']['r782_worksnap']['bytes'], receipt['entries']['r782_worksnap']['sha16'],
    receipt['entries']['r639_lineage_stepper']['bytes'], receipt['entries']['r639_lineage_stepper']['sha16'])
rraw = open(REG, 'rb').read()
if reg_line.encode('utf-8') not in rraw:
    txt = rraw.decode('utf-8')
    eol = '\r\n' if '\r\n' in txt[:200000] else '\n'
    blob = rraw
    if rraw and not (rraw.endswith(b'\n') or rraw.endswith(b'\r')):
        blob += eol.encode('utf-8')
    blob += reg_line.encode('utf-8') + eol.encode('utf-8')
    open(REG, 'wb').write(blob)
    receipt['registry_line_appended'] = True
else:
    receipt['registry_line_appended'] = 'already'

json.dump(receipt, open('results/_r783bmb_codely_increment.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({'sizes': receipt['sizes'], 'entries': receipt['entries'], 'asserts': receipt['asserts'], 'registry': receipt['registry_line_appended']}, ensure_ascii=False, indent=1))
print('MIGRATION-COMPLETE')
