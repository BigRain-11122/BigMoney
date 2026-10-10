# -*- coding: utf-8 -*-
# r839 bm-c: pit-protocol.md sub-split ceremony (D-20261002-06 cap debt)
# TREASURE_PROTECTION_LAW s2 migration ceremony, 3 pieces:
#   1) prescan rc already recorded (rc3 HIT = fail-closed face, D-06 authorized channel)
#   2) registry movement row (appended here)
#   3) zero-loss verbatim assertion (receipt)
import hashlib, json, sys, time

MAIN = 'research/pit-protocol.md'
LANE = 'research/pit-protocol-lane.md'
CODELY = 'CODELY.md'
REG = 'knowledge/TREASURE_REGISTRY.md'
RECEIPT = 'results/_r839bmc_pit_protocol_lanesplit.json'

def rd(p):
    return open(p, 'rb').read()

def assert_eq(a, b, what):
    if a != b:
        print('FATAL mismatch:', what, a, b)
        sys.exit(2)

# ---------- load ----------
mb = rd(MAIN)
lb = rd(LANE)
pre_main = len(mb)
pre_lane = len(lb)
assert_eq(mb.count(b'\n') - mb.count(b'\r\n'), 0, 'main must be pure CRLF')
assert_eq(lb.count(b'\n') - lb.count(b'\r\n'), 0, 'lane must be pure CRLF')

mt = mb.decode('utf-8')
m_lines = mt.split('\r\n')

ENTRY_PREFIXES = [
    '- [2026-10-02 01:1x r529 bm-b]',
    '- [2026-10-02 16:4x r583 bm-b]',
    '- [2026-10-04 04:0x r645 bm-b]',
]

def entry_slices(lines, prefixes):
    idx = [i for i, l in enumerate(lines) if l.startswith('- [2026')]
    out = []
    for p in prefixes:
        hits = [i for i in idx if lines[i].startswith(p)]
        assert_eq(len(hits), 1, 'entry prefix must hit exactly once: ' + p)
        k = idx.index(hits[0])
        end = idx[k + 1] if k + 1 < len(idx) else len(lines)
        # slice = entry line .. line before next entry (includes trailing blank separator)
        sl = lines[hits[0]:end]
        out.append((hits[0], end, sl))
    # non-overlapping & ordered
    pos = [s[0] for s in out]
    assert_eq(pos, sorted(pos), 'slices ordered')
    return out

slices = entry_slices(m_lines, ENTRY_PREFIXES)
moved_blocks = []
moved_bytes = 0
for st, en, sl in slices:
    block = '\r\n'.join(sl)
    # block ends WITHOUT trailing CRLF when it is last-line-of-file; rejoin convention:
    # keep the block text; bytes counted as sum(line)+2 per line (LF blob space + CRLF)
    blk_bytes = sum(len(x.encode('utf-8')) + 2 for x in sl)
    moved_blocks.append(sl)
    moved_bytes += blk_bytes
    # separator sanity: after entry line there must be a blank or next entry start
    assert_eq(sl[0].startswith('- [2026'), True, 'slice starts with entry')
assert_eq(moved_bytes, 824 + 696 + 514, 'moved bytes must equal measured 2034')

# ---------- remove from main (reverse order to keep indices) ----------
for st, en, sl in sorted(slices, key=lambda s: -s[0]):
    del m_lines[st:en]

# ---------- header routing edit ----------
HDR_RM = '猝死诊断与轮号取号/心跳与 state 簿记写入/'
HDR_ADD = 'state 轮号停滞诊断/猝死会话处置/心跳与 state 簿记写入机械/尾部写回自证→改读 pit-protocol-lane.md。'
hdr_hits = [i for i, l in enumerate(m_lines) if l.startswith('> 执法面：')]
assert_eq(len(hdr_hits), 1, 'one header enforcement line')
hi = hdr_hits[0]
assert_eq(m_lines[hi].count(HDR_RM), 1, 'header remove-target present once')
assert_eq(m_lines[hi].endswith('→改读 pit-protocol-judge.md。'), True, 'header tail anchor')
m_lines[hi] = m_lines[hi].replace(HDR_RM, '', 1)
m_lines[hi] = m_lines[hi] + HDR_ADD
hdr_delta = -len(HDR_RM.encode('utf-8')) + len(HDR_ADD.encode('utf-8'))

new_mt = '\r\n'.join(m_lines)
new_mb = new_mt.encode('utf-8')
post_main = len(new_mb)

# byte identity equation
assert_eq(pre_main - moved_bytes + hdr_delta, post_main, 'byte identity equation')
assert_eq(post_main <= 30720, True, 'post_main <= 30720 cap')
assert_eq(pre_main > 30720, True, 'pre_main was over cap')

# ---------- verbatim assertion: moved cores present in new lane text ----------
lane_t = lb.decode('utf-8')
l_lines = lane_t.split('\r\n')
assert_eq(lane_t.endswith('\r\n'), True, 'lane ends with CRLF')
# lane tail: drop trailing empty strings caused by split on trailing CRLF
while l_lines and l_lines[-1] == '':
    l_lines.pop()
# append blocks with blank separator: each block already = [entry, ''] ; last block's trailing '' optional
for bi, sl in enumerate(moved_blocks):
    if bi > 0:
        pass
    for x in sl:
        l_lines.append(x)
    # ensure blank separator after each appended entry
    if l_lines[-1] != '':
        l_lines.append('')
new_lane_t = '\r\n'.join(l_lines) + '\r\n'
new_lane_b = new_lane_t.encode('utf-8')
post_lane = len(new_lane_b)

# verbatim-in-target assertions (each entry core byte-present in new lane)
for st, en, sl in slices:
    core = sl[0].encode('utf-8')
    assert_eq(new_lane_b.count(core), 1, 'verbatim core in lane: ' + sl[0][:40])

moved_md5 = hashlib.md5('\r\n'.join('\r\n'.join(sl) for sl in moved_blocks).encode('utf-8')).hexdigest()

# ---------- write main + lane ----------
open(MAIN, 'wb').write(new_mb)
open(LANE, 'wb').write(new_lane_b)

# ---------- CODELY.md pointer row update ----------
cb = rd(CODELY)
pre_codely = len(cb)
TAIL_ANCHOR = 'prereg 闸/finalize/judged 消费动作前改读 pit-protocol-judge.md。'
ct = cb.decode('utf-8')
assert_eq(ct.count(TAIL_ANCHOR), 1, 'codely protocol row tail anchor unique')
PTR_ADD = ('；r839 bm-c 增量回扫迁移仪式（2026-10-10·主件 31,433B>30,720B 越帽触发·r859 增量欠账）：'
           'r529/r583/r645 state 簿记族 3 条 2,034B verbatim 迁 pit-protocol-lane.md'
           '（state 轮号停滞诊断/心跳簿记写入/尾部写回自证动作前改读该件）'
           '·主件 %dB 恒等 <=30KB·receipt=%s' % (post_main, RECEIPT))
ct2 = ct.replace(TAIL_ANCHOR, TAIL_ANCHOR + PTR_ADD, 1)
cb2 = ct2.encode('utf-8')
open(CODELY, 'wb').write(cb2)
post_codely = len(cb2)
assert_eq(post_codely <= 30720, True, 'codely <= cap')

# ---------- registry movement row ----------
rb = rd(REG)
pre_reg = len(rb)
assert_eq(rb.endswith(b'\r\n'), True, 'registry ends with CRLF')
REG_ROW = ('- 2026-10-10 21:2x bm-c r839 域件 sub-split 迁移仪式（D-20261002-06 域件 <=30KB 再平衡·r838 欠账承接·r791/r836 仪式同款）：'
           'pit-protocol.md 31,433B>30,720B 越帽（r859 bma 10-08 增量致）——集团拆件令 D-20261002-06 授权'
           '×TREASURE_PROTECTION_LAW §2 迁移仪式三件齐：'
           '①prescan 留痕（treasure_guard prescan rc3 命中 pit-protocol.md/pit-protocol-lane.md/CODELY.md/登记册=fail-closed 面·D-06 授权通道）'
           '②出入记录=本行 '
           '③零丢失断言：r529/r583/r645 state 簿记族 3 条 2,034B verbatim 迁 pit-protocol-lane.md'
           '（主件头部执法面同步改道 lane 件·主件 31,433→%dB 恒等 <=30KB·receipt=%s）。' % (post_main, RECEIPT))
rb2 = rb + REG_ROW.encode('utf-8') + b'\r\n'
open(REG, 'wb').write(rb2)
post_reg = len(rb2)

# ---------- receipt ----------
receipt = {
    "ts": time.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
    "round": "r839 bm-c",
    "action": "pit-protocol.md sub-split (state-ledger family entries -> pit-protocol-lane.md)",
    "trigger": "pre_main 31433B > 30720B cap (r859 bma 10-08 increment debt, disclosed r838)",
    "prescan_rc": 3,
    "prescan_note": "treasure_guard prescan rc3 HIT on pit-protocol.md/pit-protocol-lane.md/CODELY.md/TREASURE_REGISTRY.md = fail-closed face; D-20261002-06 authorized channel; r441 intersection ruling: zero-loss verbatim migration is non-deletion class",
    "moved_refs": [
        "2026-10-02 01:1x r529 bm-b",
        "2026-10-02 16:4x r583 bm-b",
        "2026-10-04 04:0x r645 bm-b"
    ],
    "moved_bytes": moved_bytes,
    "header_delta_bytes": hdr_delta,
    "pre_main_bytes": pre_main,
    "post_main_bytes": post_main,
    "post_main_le_cap_30720": post_main <= 30720,
    "pre_lane_bytes": pre_lane,
    "post_lane_bytes": post_lane,
    "post_lane_le_cap_30720": post_lane <= 30720,
    "moved_md5": moved_md5,
    "child_contains_moved_verbatim": True,
    "byte_identity": "%d - %d + %d = %d" % (pre_main, moved_bytes, hdr_delta, post_main),
    "codely_ptr_row": {"pre": pre_codely, "post": post_codely, "le_cap": post_codely <= 30720},
    "registry_row": {"pre": pre_reg, "post": post_reg},
}
open(RECEIPT, 'w', encoding='utf-8', newline='\n').write(json.dumps(receipt, ensure_ascii=False, indent=1))
print('CEREMONY OK')
print('byte_identity:', receipt["byte_identity"])
print('post_main:', post_main, 'post_lane:', post_lane, 'post_codely:', post_codely, 'post_reg:', post_reg)
