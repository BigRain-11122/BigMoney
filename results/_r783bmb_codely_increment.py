# r783 bm-b D-06 main-file rebound incremental re-scan (migration ritual per r441/r703/r707) -- idempotent v2
import json, hashlib, os

os.chdir(r'C:\Fluxgroup\FluxGroup\quant\bigmoney')
MAIN = 'CODELY.md'
TARGETS = {'r782_worksnap': ('research/pit-git-resolver.md', '- [2026-10-06 21:3x r782 bm-b] **worksnap 同名互覆', True),
           'r639_lineage_stepper': ('research/pit-lineage-legdiff.md', '- [2026-10-06 20:5x r639 bm-c] **血统机械步进', False)}
LINE_LIMIT = 30720
REG = 'knowledge/TREASURE_REGISTRY.md'
receipt = {'ritual': 'r441/r703 migration ritual: prescan rc3 (hits recorded) + registry line + zero-loss battery + receipt',
           'entries': {}, 'asserts': [], 'sizes': {}, 'idempotent_skips': []}

def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]

def eol_of(raw):
    return '\r\n' if '\r\n' in raw.decode('utf-8', 'replace')[:200000] else '\n'

main_raw = open(MAIN, 'rb').read()
receipt['sizes']['main_before'] = len(main_raw)
main_txt = main_raw.decode('utf-8')
main_eol = eol_of(main_raw)
eol_b = main_eol.encode('utf-8')
lines = main_txt.split(main_eol)

# --- extract the 2 entry lines (unique anchors) ---
blocks = {}
for key, (tgt, anchor, drop_blank_after) in TARGETS.items():
    hits = [i for i, ln in enumerate(lines) if ln.startswith(anchor)]
    assert len(hits) == 1, 'anchor not unique for %s: %d hits' % (key, len(hits))
    blocks[key] = {'idx': hits[0], 'entry': lines[hits[0]], 'target': tgt, 'drop_blank': drop_blank_after}
    receipt['entries'][key] = {'target': tgt, 'bytes': len(lines[hits[0]].encode('utf-8')), 'sha16': sha16(lines[hits[0]].encode('utf-8'))}

# remove from main (highest idx first); r782 also drops its following blank (restores pre-insert topology)
drop = set()
for key in sorted(blocks, key=lambda k: -blocks[k]['idx']):
    b = blocks[key]
    drop.add(b['idx'])
    if b['drop_blank'] and b['idx'] + 1 < len(lines) and lines[b['idx'] + 1] == '':
        drop.add(b['idx'] + 1)
kept = [ln for i, ln in enumerate(lines) if i not in drop]

# pointer row: insert before trailing '' element (file-end hygiene), else append
ptr = ('- 域指针·r783 bm-b 增量回扫批（D-20261002-06 主件 ≤30KB 判据腿·2026-10-06 r783 bm-b·迁移仪式 r441/r703 同款）：'
       '主件回弹增量坑律 2 条 verbatim 迁出——r782 worksnap 三连坑（S0 脏窗 worksnap 路径限定/checkout 竞态/guard RESTORE_FORBIDDEN 证据类）→pit-git-resolver.md'
       '〔S0 merge resolver 族·S0 脏窗处理动作前改读〕+r639 血统机械步进 \\b 假界坑（r6NN 步进器 (?!\d) 形+修表全跑+compile 门）→pit-lineage-legdiff.md'
       '〔needle 步进器族·代际步进动作前改读〕——逐条字节+sha16 对账=receipt results/_r783bmb_codely_increment.json'
       '（零丢失断言=逐块 bytes in target verbatim+主件保留面恒等式+主件 ≤30KB+全域件 ≤30KB·登记册出入记录行同步 append）；新坑律仍先入本件后回扫。')
if kept and kept[-1] == '':
    kept.insert(len(kept) - 1, ptr)
else:
    kept.append(ptr)
new_main_txt = main_eol.join(kept)
final_eol_added = False
if not new_main_txt.endswith(main_eol):
    new_main_txt += main_eol
    final_eol_added = True
new_main = new_main_txt.encode('utf-8')
receipt['sizes']['main_after'] = len(new_main)
receipt['final_eol_heal'] = final_eol_added
assert len(new_main) <= LINE_LIMIT, 'main still over line: %d' % len(new_main)

# --- structural identity (arithmetic-free): exact line-list equality ---
kept_lines = [ln for i, ln in enumerate(lines) if i not in drop]
new_lines = new_main_txt.split(main_eol)
expected_lines = kept_lines + [ptr] + ([''] if final_eol_added else [])
assert new_lines == expected_lines, 'structural identity failed: %d vs %d lines' % (len(new_lines), len(expected_lines))
for key, b in blocks.items():
    assert b['entry'] not in new_lines, 'dropped entry still present: %s' % key
    assert b['entry'] in main_txt, 'sanity: entry was in original'
receipt['asserts'].append('structural identity: new == (original - %d dropped lines) + ptr + final-eol(%s); dropped entries x0 in new' % (len(drop), final_eol_added))

# --- append verbatim to domain files (idempotent: skip if already present) ---
for key, b in blocks.items():
    tgt = b['target']
    traw = open(tgt, 'rb').read()
    eb = b['entry'].encode('utf-8')
    if eb in traw:
        receipt['idempotent_skips'].append(tgt)
    else:
        teol = eol_of(traw).encode('utf-8')
        blob = traw
        if traw and not (traw.endswith(b'\n') or traw.endswith(b'\r')):
            blob += teol
        blob += eb + teol
        open(tgt, 'wb').write(blob)
    check = open(tgt, 'rb').read()
    assert check.count(eb) == 1, 'verbatim count != 1 in %s (got %d)' % (tgt, check.count(eb))
    assert len(check) <= LINE_LIMIT, 'target over line: %s %d' % (tgt, len(check))
    receipt['entries'][key]['target_bytes_after'] = len(check)
    receipt['asserts'].append('%s verbatim x1 in %s (bytes %d, sha16 %s, file %d B)' % (key, tgt, receipt['entries'][key]['bytes'], receipt['entries'][key]['sha16'], len(check)))

# write main
open(MAIN, 'wb').write(new_main)

# --- all-domain size sweep ---
pit = [f for f in os.listdir('research') if f.startswith('pit-') and f.endswith('.md')]
over = [(f, os.path.getsize(os.path.join('research', f))) for f in pit if os.path.getsize(os.path.join('research', f)) > LINE_LIMIT]
assert not over, 'domain files over line: %r' % over
receipt['asserts'].append('all %d pit-*.md <= 30720B' % len(pit))

# --- conflict marker scan on touched files ---
for p in [MAIN] + [b['target'] for b in blocks.values()]:
    raw = open(p, 'rb').read()
    for m in (b'<<<<<<< ', b'>>>>>>> ', b'||||||| '):
        assert m not in raw, 'conflict marker %r in %s' % (m, p)
receipt['asserts'].append('marker scan clean on 3 touched files')

# --- registry in/out record line (append-only) ---
reg_line = ('- 2026-10-06 21:2x bm-b r783 D-06 主件回弹增量回扫迁移仪式（D-20261002-06 主件 ≤30KB 判据腿·r441/r703 仪式同款）：'
            'prescan 实弹 rc3 命中 research/pit-git-resolver.md+pit-lineage-legdiff.md（research/ 全族 fail-closed 面）——'
            '集团拆件令 D-20261002-06（主件+域件 ≤30KB·收口窗 10-07 12:00）授权 TREASURE_PROTECTION_LAW §2 迁移仪式三件齐：'
            '①prescan rc3 留痕（本行）②出入记录本行 ③零丢失断言：CODELY.md 主件 %d→%d 回线（2 条增量坑律 verbatim 迁出非手抄：'
            'r782 worksnap 三连坑→pit-git-resolver.md〔%dB·sha16 %s〕+r639 血统机械步进坑→pit-lineage-legdiff.md〔%dB·sha16 %s〕·'
            '逐条 bytes-in-target verbatim x1 验证·主件保留面字节恒等式·receipt=results/_r783bmb_codely_increment.json）；'
            '域件面=纯加性 append 零删除·在册路径保留非删除·CODELY.md 指针行随批新增。') % (
    receipt['sizes']['main_before'], receipt['sizes']['main_after'],
    receipt['entries']['r782_worksnap']['bytes'], receipt['entries']['r782_worksnap']['sha16'],
    receipt['entries']['r639_lineage_stepper']['bytes'], receipt['entries']['r639_lineage_stepper']['sha16'])
rraw = open(REG, 'rb').read()
if reg_line.encode('utf-8') not in rraw:
    reol = eol_of(rraw).encode('utf-8')
    rblob = rraw
    if rraw and not (rraw.endswith(b'\n') or rraw.endswith(b'\r')):
        rblob += reol
    rblob += reg_line.encode('utf-8') + reol
    open(REG, 'wb').write(rblob)
receipt['registry_line_appended'] = True

json.dump(receipt, open('results/_r783bmb_codely_increment.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({'sizes': receipt['sizes'], 'entries': {k: {'bytes': v['bytes'], 'sha16': v['sha16'], 'target': v['target'], 'target_bytes_after': v.get('target_bytes_after')} for k, v in receipt['entries'].items()}, 'asserts': receipt['asserts'], 'idempotent_skips': receipt['idempotent_skips']}, ensure_ascii=False, indent=1))
print('MIGRATION-OK')
