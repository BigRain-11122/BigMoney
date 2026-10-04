# -*- coding: utf-8 -*-
# r706 bm-b: D-06 batch-3 -- pit-protocol.md three-way sub-split (D-20261002-06 domain-file <=30KB rebalance)
# Ceremony: r439/r441/r703/r705 verbatim-migration family (prescan rc3 acknowledged hit + registry
# in/out row appended separately + zero-loss byte accounting + per-entry sha16 receipt).
# Host EOL = LF (asserted). Variant-6 fused inline entry (r460 inside E46 host blob, r410 law)
# migrates verbatim inside its host blob -- zero information loss.
import io, json, hashlib

SRC = 'research/pit-protocol.md'
NEW_D19 = 'research/pit-protocol-d19.md'
NEW_J = 'research/pit-protocol-judge.md'
RECEIPT = 'results/_r706bmb_pit_protocol_split_receipt.json'

# A = pit-protocol.md keep: round-protocol core (orders scan, S0 restore, claims/yield,
#     adoption, session-death numbering, heartbeat/state bookkeeping, shared append-only
#     memory union + canonical char face, lane_io single-writer guards, inbox).
# D19 = pit-protocol-d19.md: D-19 decision/orders watermark consumption + content-addressing
#     (sha case/caliber/base/git-show raw bytes/channel) + watermark probes (py_watermark
#     ticket scan, post_review REPORT face, false-alarm repro-first law).
# J = pit-protocol-judge.md: prereg admission gates (banned_direction, placeholder anchors,
#     exit-axis declaration/neutralization), finalize accounting + AA assertions, judged
#     declared-axis (dead letters/ghost twins), E1 legs, assertion-tolerance faces.
A_KEEP = [1, 4, 6, 9, 10, 12, 16, 19, 20, 22, 24, 25, 30, 32, 33, 34, 35, 36, 37, 38,
          41, 42, 43, 47, 48, 49, 51, 53]
D19 = [3, 11, 17, 18, 21, 28, 39, 40, 44, 45, 46, 50, 52]
J = [2, 5, 7, 8, 13, 14, 15, 23, 26, 27, 29, 31]

N = 53
ENTRIES_SUM = 46837
A_SUM = 23678
D19_SUM = 11004
J_SUM = 12155


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def parse():
    raw = open(SRC, 'rb').read()
    assert b'\r' not in raw, 'host EOL must be pure LF'
    txt = raw.decode('utf-8')
    lines = txt.split('\n')
    starts = [i for i, l in enumerate(lines) if l.startswith('- [')]
    assert len(starts) == N, 'expected %d entries, got %d' % (N, len(starts))
    entries = []
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else len(lines)
        entries.append('\n'.join(lines[s:e]))
    preface_lines = lines[:starts[0]]
    recon = '\n'.join(preface_lines + entries)
    assert recon.encode('utf-8') == raw, 'byte-identity reconstruction failed'
    return raw, lines, preface_lines, entries


def build_preface_a(preface_lines, totals):
    out = []
    for r in preface_lines:
        if r.startswith('> 执法面：'):
            out.append('> 执法面：S0.5 令扫与 orders 差集（排序窗/计数口径/条目形态）/S0 恢复 restore 分类与集成净路/跨机宣称 git 实证面/票认领让路与开票查收/收养（半成品·工具集·悬空引用）核验/猝死诊断与轮号取号/心跳与 state 簿记写入/共享 append-only 记忆 union 与正典机读字符面/lane_io 单机执笔守卫/inbox 声明——上述动作前必读本件；D-19 决策/orders 水位消费与水位探针→改读 pit-protocol-d19.md；prereg 起草与准入闸（banned_direction·占位锚·出场轴）/finalize 记账与 AA 断言/judged 批声明轴与 E1 对账→改读 pit-protocol-judge.md。')
        else:
            out.append(r)
    acc = ('> 字节对账行（D-06 batch-3 拆件·2026-10-05 r706 bm-b·零丢失断言）：拆前本件 50756B（53 条·条目字节和 %dB）'
           '→拆后本件 %dB（28 条·条目 %dB）+pit-protocol-d19.md %dB（13 条·条目 %dB）+pit-protocol-judge.md %dB（12 条·条目 %dB）；'
           '三件条目字节和恒等 %dB·逐条 verbatim 迁移非手抄（变体⑥ 行内融合两条：r294 前导空格 bullet 形随宿主 E38·r460 无换行内联形随宿主 E46·原样迁移零信息损失）·'
           'receipt=results/_r706bmb_pit_protocol_split_receipt.json（r703/r705 范式同源）。'
           % (ENTRIES_SUM, totals['a_file'], A_SUM, totals['d19_file'], D19_SUM,
              totals['j_file'], J_SUM, ENTRIES_SUM))
    insert_at = len(out)
    while insert_at > 0 and out[insert_at - 1] == '':
        insert_at -= 1
    out.insert(insert_at, acc)
    return out


PREFACE_D19 = [
    '# pit-protocol-d19 —— D-19 决策水位与水位探针坑律正典（D-20261002-06 域分件·pit-protocol sub-split batch-3）',
    '',
    '> 来源：research/pit-protocol.md verbatim 迁出（2026-10-05 r706 bm-b·D-20261002-06 域件 ≤30KB 再平衡·收口窗 10-07）。',
    '> 执法面：D-19 决策/orders 水位消费（回执与水位键同轮原子落地/SHA 大小写归一与键口径自证/内容寻址基座 git show 原字节律/sparse-clone 通道 ssh 先+mkdtemp/集团树路由与 S4U 无树 fallback/共享决策面回归观察 push-race）/水位探针（py_watermark 票扫描 claimed 排除/post_review 判定读 REPORT 面/探针假警先复现证伪）——上述动作前必读本件（轮协议核心/收养/票让路/state 簿记→pit-protocol.md；prereg 闸/finalize/judged→pit-protocol-judge.md）。',
    '> 字节对账行（零丢失断言）：自 pit-protocol.md verbatim 迁出 13 条·条目字节和 %dB==源件同条目字节和（LF blob 面·逐字节恒等）·机械迁移非手抄（变体⑥ 行内融合不涉本件）·receipt=results/_r706bmb_pit_protocol_split_receipt.json（r703/r705 范式同源）。' % D19_SUM,
    '',
]

PREFACE_J = [
    '# pit-protocol-judge —— prereg 准入与判决面坑律正典（D-20261002-06 域分件·pit-protocol sub-split batch-3）',
    '',
    '> 来源：research/pit-protocol.md verbatim 迁出（2026-10-05 r706 bm-b·D-20261002-06 域件 ≤30KB 再平衡·收口窗 10-07）。',
    '> 执法面：prereg 起草与准入闸（banned_direction §0.5 例外合同/占位锚两态守卫/波冻结 copy-adapt 源件回填态三件套/出场轴显式声明与非股票族缺省栈禁令/出场中和 ExitPatch 通道）、finalize 记账与 AA 断言（append_ledger 返回块持久化序/幻影记账甄别/汇总件浮点尾差三层判据）、judged 批声明轴（参数轴死信/幽灵孪生诊断签名/真分化证据三件套守卫）与 E1 三腿对账（as-burned 重放/出口中和/无引擎独立腿·断板日语义）、判据断言容差面（普查书写变体保守判律/published-vs-curves 消费双约定）——上述动作前必读本件（轮协议核心→pit-protocol.md；D-19 水位→pit-protocol-d19.md）。',
    '> 字节对账行（零丢失断言）：自 pit-protocol.md verbatim 迁出 12 条·条目字节和 %dB==源件同条目字节和（LF blob 面·逐字节恒等）·机械迁移非手抄（变体⑥ 行内融合不涉本件）·receipt=results/_r706bmb_pit_protocol_split_receipt.json（r703/r705 范式同源）。' % J_SUM,
    '',
]


def assemble(preface_rows, entries, carries_source_tail):
    body = '\n'.join(preface_rows) + '\n' + '\n'.join(entries)
    if not carries_source_tail:
        body += '\n'
    return body


def main():
    raw, lines, preface_lines, entries = parse()
    mapping = {}
    for n in A_KEEP:
        mapping[n] = 'A'
    for n in D19:
        mapping[n] = 'D19'
    for n in J:
        mapping[n] = 'J'
    assert sorted(mapping) == list(range(1, N + 1)), 'mapping must cover 1..%d exactly once' % N

    ent_bytes = [len(e.encode('utf-8')) for e in entries]
    assert sum(ent_bytes) == ENTRIES_SUM, 'entries byte sum mismatch: %d' % sum(ent_bytes)

    a_entries = [entries[i] for i in range(N) if mapping[i + 1] == 'A']
    d19_entries = [entries[i] for i in range(N) if mapping[i + 1] == 'D19']
    j_entries = [entries[i] for i in range(N) if mapping[i + 1] == 'J']
    a_sum = sum(len(e.encode('utf-8')) for e in a_entries)
    d19_sum = sum(len(e.encode('utf-8')) for e in d19_entries)
    j_sum = sum(len(e.encode('utf-8')) for e in j_entries)
    assert (a_sum, d19_sum, j_sum) == (A_SUM, D19_SUM, J_SUM), \
        'family sums mismatch: %r' % ((a_sum, d19_sum, j_sum),)

    # variant-6 fused inline probe: host blobs carrying >1 '[2026-' date tag inline.
    # E46 carries r460 fused inline (no newline); E38 carries r294 fused with a
    # leading-space bullet form (line starts ' - [', not counted as entry start).
    # Both fused passengers (r460 PS-pipeline / r294 lane_io ladder) are same-family
    # with their hosts -> fusion migrates whole, zero info loss (r410 law).
    fused_hosts = []
    for i, e in enumerate(entries):
        if e.count('[2026-') > 1:
            fused_hosts.append(i + 1)
    assert fused_hosts == [38, 46], 'fused host probe mismatch: %r' % fused_hosts
    assert 'r460 bm-c' in entries[45], 'E46 must carry the r460 fused inline entry'
    assert 'r294 bm-c' in entries[37], 'E38 must carry the r294 fused leading-space entry'

    # fixed-point totals (A accounting row contains the three file sizes themselves)
    totals = {'src': len(raw), 'a_file': 0, 'd19_file': 0, 'j_file': 0}
    for _ in range(4):
        pa = build_preface_a(preface_lines, totals)
        a_text = assemble(pa, a_entries, True)          # E53 (source tail) lands in A
        d19_text = assemble(PREFACE_D19, d19_entries, False)
        j_text = assemble(PREFACE_J, j_entries, False)
        new_totals = {'src': len(raw),
                      'a_file': len(a_text.encode('utf-8')),
                      'd19_file': len(d19_text.encode('utf-8')),
                      'j_file': len(j_text.encode('utf-8'))}
        if new_totals == totals:
            break
        totals = new_totals
    assert totals['a_file'] <= 30720 and totals['d19_file'] <= 30720 and totals['j_file'] <= 30720, \
        '30KB bound violated: %r' % totals

    # zero-loss: every original entry byte-string present exactly once, in its target only
    all_bytes = (a_text.encode('utf-8') + b'\x00' + d19_text.encode('utf-8')
                 + b'\x00' + j_text.encode('utf-8'))
    for i, e in enumerate(entries):
        b = e.encode('utf-8')
        assert all_bytes.count(b) >= 1, 'entry E%02d lost' % (i + 1)
        tgt = {'A': a_text, 'D19': d19_text, 'J': j_text}[mapping[i + 1]].encode('utf-8')
        assert tgt.count(b) == 1, 'entry E%02d not verbatim-unique in target' % (i + 1)
        for other_name, other in (('A', a_text), ('D19', d19_text), ('J', j_text)):
            if other_name != mapping[i + 1]:
                assert b not in other.encode('utf-8'), \
                    'entry E%02d leaked into non-target %s' % (i + 1, other_name)

    # write outputs
    io.open(SRC, 'w', encoding='utf-8', newline='').write(a_text)
    io.open(NEW_D19, 'w', encoding='utf-8', newline='').write(d19_text)
    io.open(NEW_J, 'w', encoding='utf-8', newline='').write(j_text)

    receipt = {
        'op': 'D-20261002-06 domain-file <=30KB rebalance batch-3: pit-protocol three-way sub-split',
        'round': 'r706 bm-b', 'ts': '2026-10-05',
        'mechanism': 'r439/r441/r703/r705 verbatim migration ceremony; prescan rc3 acknowledged hit '
                     '(research/ family, non-delete migration under D-20261002-06 mandate); '
                     'registry in/out row appended; TREASURE_PROTECTION_LAW s2',
        'src_before_bytes': len(raw), 'src_before_entries': N, 'entries_bytes_sum': ENTRIES_SUM,
        'files': {
            'research/pit-protocol.md': {'entries': 28, 'entries_bytes': a_sum, 'file_bytes': totals['a_file'],
                                         'face': 'round-protocol core: orders scan, S0 restore classification, claims/yield, adoption, session-death numbering, heartbeat/state bookkeeping, shared append-only memory union + canonical char face, lane_io guards, inbox'},
            'research/pit-protocol-d19.md': {'entries': 13, 'entries_bytes': d19_sum, 'file_bytes': totals['d19_file'],
                                             'face': 'D-19 decision/orders watermark consumption + content-addressing + watermark probes'},
            'research/pit-protocol-judge.md': {'entries': 12, 'entries_bytes': j_sum, 'file_bytes': totals['j_file'],
                                               'face': 'prereg admission gates, exit-axis declaration, finalize accounting + AA assertions, judged declared-axis, E1 legs, assertion tolerances'},
        },
        'variant6_fused_inline': {'hosts': [38, 46],
                                  'entries': ['r294 bm-c (lane_io stale-takeover ladder, leading-space bullet form, host E38)',
                                              'r460 bm-c (PS Select-Object -First truncation kill, inline no-newline form, host E46)'],
                                  'handling': 'verbatim inside host blobs (r410 inline-fusion law), zero info loss'},
        'entries': [
            {'e': i + 1, 'target': mapping[i + 1], 'bytes': ent_bytes[i],
             'sha16': sha16(entries[i].encode('utf-8'))}
            for i in range(N)
        ],
        'verify': {
            'byte_identity_reconstruction': 'PASS',
            'entries_sum_partition': 'PASS (%d == %d+%d+%d)' % (ENTRIES_SUM, a_sum, d19_sum, j_sum),
            'verbatim_unique_in_target_53': 'PASS',
            'no_leak_across_targets_53': 'PASS',
            'thirty_kb_bound_all_three': 'PASS',
            'fused_host_probe': 'PASS (E38 carries r294 leading-space + E46 carries r460 inline)',
            'eol': 'LF preserved (asserted no CR in source; outputs LF)',
        },
    }
    io.open(RECEIPT, 'w', encoding='utf-8').write(json.dumps(receipt, ensure_ascii=False, indent=1))
    print('SPLIT OK: A=%dB D19=%dB J=%dB (src was %dB)' % (
        totals['a_file'], totals['d19_file'], totals['j_file'], len(raw)))


if __name__ == '__main__':
    main()
