# r789 bm-b: D-06 CODELY.md main-file incremental re-sweep (r441/r703/r783 migration ritual)
# 3 newest pit entries verbatim-migrated to domain pit files; byte-exact accounting; receipt JSON.
import hashlib, json, os, glob

def rb(p):
    with open(p, 'rb') as f:
        return f.read()

def wb(p, b):
    with open(p, 'wb') as f:
        f.write(b)

def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]

ENTRIES = [
    (b'- [2026-10-06 21:3x r640 bm-c]', 'r640_qa_roundlabel_race', 'research/pit-protocol-lane.md'),
    (b'- [2026-10-06 23:4x r642 bm-c]', 'r642_autostash_pop_dead', 'research/pit-git-resolver.md'),
    (b'- [2026-10-06 23:5x r787 bm-b]', 'r787_rebase_continue_fake', 'research/pit-git-resolver.md'),
]

main_p = 'CODELY.md'
main_before = rb(main_p)
size_before = len(main_before)

# 1) extract exact line bytes (no LF) + remove from main
lines = main_before.split(b'\n')
# file ends with LF -> last element is b'' ; keep structure: rejoin with b'\n'
removed = {}
kept = []
for ln in lines:
    hit = None
    for pref, key, tgt in ENTRIES:
        if ln.startswith(pref):
            assert key not in removed, 'dup entry prefix ' + key
            removed[key] = (ln, tgt)
            hit = key
            break
    if hit is None:
        kept.append(ln)
    else:
        print('removed:', hit, len(ln), 'B')
assert len(removed) == 3, 'must remove exactly 3 entries, got %d' % len(removed)

# ptr row appended at end of main (after final row, before terminal LF)
PTR = ('- 域指针·r789 bm-b 增量回扫批（D-20261002-06 主件 ≤30KB 判据腿·2026-10-07 r789 bm-b·迁移仪式 r441/r703/r783 同款）：'
       '主件回弹增量坑律 3 条 verbatim 迁出——r640 QA 分离跑手轮标竞态坑（qa_ignite×close.py state 进位·close 前必 qa_poll 序）'
       '→pit-protocol-lane.md〔state 簿记/竞态族·QA 证据包收口动作前改读〕'
       '+r642 pull --rebase autostash pop 冲突致死+接管收口配方（净树零 autostash 根治律）'
       '→pit-git-resolver.md〔S0 脏窗/resolver 族〕'
       '+r787 rebase --continue 假冲突报×车道活面加窗坑（add+continue 原子化律）'
       '→pit-git-resolver.md〔S0 rebase continue 面〕'
       '——逐条字节+sha16 对账=receipt results/_r789bmb_codely_increment.json'
       '（零丢失断言=逐块 bytes in target verbatim+主件保留面恒等式+主件 ≤30KB+全域件 ≤30KB·登记册出入记录行同步 append）；'
       '新坑律仍先入本件后回扫。').encode('utf-8')
kept.append(PTR)
main_after = b'\n'.join(kept)
size_after = len(main_after)

# byte equation: before - (3 entries + their 3 LFs) + (ptr row + its LF) == after
eq_expect = size_before - sum(len(e[0]) + 1 for e in removed.values()) + len(PTR) + 1
assert size_after == eq_expect, 'byte equation broken: %d != %d' % (size_after, eq_expect)

# 2) append entries verbatim to targets (each target must end with exactly one LF)
for pref, key, tgt in ENTRIES:
    ebytes, tgt = removed[key]
    t = rb(tgt)
    assert t.endswith(b'\n') and not t.endswith(b'\n\n'), 'target tail malformed: ' + tgt
    assert t.count(ebytes) == 0, 'entry already in target: ' + key
    wb(tgt, t + ebytes + b'\n')
    t2 = rb(tgt)
    assert t2.count(ebytes) == 1, 'verbatim x1 fail: ' + key
    print('appended %s -> %s (%d B, sha16 %s, file %d B)' % (key, tgt, len(ebytes), sha16(ebytes), len(t2)))

wb(main_p, main_after)

# 3) assertions
assert size_after <= 30720, 'main still over 30720: %d' % size_after
pit_sizes = {p: os.path.getsize(p) for p in glob.glob('research/pit-*.md')}
over = {p: s for p, s in pit_sizes.items() if s > 30720}
assert not over, 'pit files over 30720: %r' % over
main_now = rb(main_p)
for mk in (b'\n<<<<<<<', b'\n>>>>>>>', b'\n======='):
    assert mk not in main_now, 'conflict marker in main: %r' % mk

receipt = {
    'ritual': 'r441/r703/r783 migration ritual (r789 bm-b, prescan rc3 x4 logged)',
    'entries': {},
    'asserts': [
        'main %d -> %d B (<=30720)' % (size_before, size_after),
        'byte equation exact (3 entries + LFs out, 1 ptr row + LF in)',
        'each entry verbatim x1 in target, sha16-anchored',
        'all %d pit-*.md <= 30720B' % len(pit_sizes),
        'marker scan clean on main',
    ],
    'sizes': {'main_before': size_before, 'main_after': size_after},
    'pit_files': len(pit_sizes),
    'registry_line_appended': True,
}
for pref, key, tgt in ENTRIES:
    ebytes, t = removed[key]
    receipt['entries'][key] = {
        'target': t.replace('\\', '/'),
        'bytes': len(ebytes),
        'sha16': sha16(ebytes),
        'target_bytes_after': os.path.getsize(t),
    }
wb('results/_r789bmb_codely_increment.json', json.dumps(receipt, ensure_ascii=False, indent=1).encode('utf-8') + b'\n')

# 4) registry in-out record row (TREASURE_REGISTRY.md append)
row = ('- 2026-10-07 00:4x bm-b r789 D-06 主件回弹增量回扫迁移仪式（D-20261002-06 主件 ≤30KB 判据腿·顺延窗 10-09 00:00 per D-20261007-01③·'
       'r441/r703/r783 仪式同款）：prescan 实弹 rc3 命中 research/pit-protocol-lane.md+pit-git-resolver.md+CODELY.md+knowledge/TREASURE_REGISTRY.md'
       '（research/ 全族+登记册类 fail-closed 面）——集团拆件令 D-20261002-06 授权 TREASURE_PROTECTION_LAW §2 迁移仪式三件齐：'
       '①prescan rc3 留痕（本行）②出入记录本行 ③零丢失断言：CODELY.md 主件 %d→%dB 回线'
       '（3 条增量坑律 verbatim 迁出非手抄：r640 QA 轮标竞态坑→pit-protocol-lane.md〔%dB·sha16 %s〕'
       '+r642 autostash pop 冲突坑→pit-git-resolver.md〔%dB·sha16 %s〕'
       '+r787 rebase continue 假冲突坑→pit-git-resolver.md〔%dB·sha16 %s〕·逐条字节对账+主件保留面恒等+全域件 ≤30KB）；'
       'receipt=results/_r789bmb_codely_increment.json。') % (
    size_before, size_after,
    receipt['entries']['r640_qa_roundlabel_race']['bytes'], receipt['entries']['r640_qa_roundlabel_race']['sha16'],
    receipt['entries']['r642_autostash_pop_dead']['bytes'], receipt['entries']['r642_autostash_pop_dead']['sha16'],
    receipt['entries']['r787_rebase_continue_fake']['bytes'], receipt['entries']['r787_rebase_continue_fake']['sha16'],
)
reg_p = 'knowledge/TREASURE_REGISTRY.md'
reg = rb(reg_p)
assert reg.endswith(b'\n') and not reg.endswith(b'\n\n'), 'registry tail malformed'
wb(reg_p, reg + row.encode('utf-8') + b'\n')
print('registry row appended (%d B)' % len(row.encode('utf-8')))
print('DONE main %d -> %d B; receipt written' % (size_before, size_after))
