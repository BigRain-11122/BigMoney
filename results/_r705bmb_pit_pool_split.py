# -*- coding: utf-8 -*-
# r705 bm-b: D-06 batch-3 -- pit-pool.md two-way sub-split (D-20261002-06 domain-file <=30KB rebalance)
# Ceremony: r439/r441/r703 verbatim-migration family (prescan rc3 acknowledged hit + registry
# in/out row appended separately + zero-loss byte accounting + per-entry sha16 receipt).
# Host EOL = LF (asserted). Known variant-5 bullet-less entries (r598 in E16, r608/r605 in E18)
# migrate verbatim inside their host blobs -- zero information loss, no 2B normalization.
import io, json, hashlib

SRC = 'research/pit-pool.md'
NEW = 'research/pit-pool-edit.md'
RECEIPT = 'results/_r705bmb_pit_pool_split_receipt.json'

# Explicit E-number -> target mapping (verified by hand against titles).
# A = pit-pool.md keep: claim/flip semantics, visibility, takeover, double-burn, parked governance,
#     supply starvation reading.
# B = pit-pool-edit.md new: pool-file byte editing & write-paths, settle, conflict basis, flip
#     execution surgery, burn process mechanics, ignition gates (host_gates/fuse keepblock).
A_KEEP = [2, 3, 4, 5, 7, 9, 10, 11, 15, 16, 17, 19, 20, 23, 25, 26, 37, 38, 45, 46]
B_EDIT = [1, 6, 8, 12, 13, 14, 18, 21, 22, 24, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
          39, 40, 41, 42, 43, 44]

ENTRIES_SUM = 48301
A_SUM = 21852
B_SUM = 26449


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def parse():
    raw = open(SRC, 'rb').read()
    assert b'\r' not in raw, 'host EOL must be pure LF'
    txt = raw.decode('utf-8')
    lines = txt.split('\n')
    starts = [i for i, l in enumerate(lines) if l.startswith('- [')]
    assert len(starts) == 46, 'expected 46 entries, got %d' % len(starts)
    entries = []
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else len(lines)
        entries.append('\n'.join(lines[s:e]))
    preface_lines = lines[:starts[0]]
    recon = '\n'.join(preface_lines + entries)
    assert recon.encode('utf-8') == raw, 'byte-identity reconstruction failed'
    return raw, lines, preface_lines, entries


def build_preface_a(preface_lines, totals):
    rows = list(preface_lines)
    out = []
    for r in rows:
        if r.startswith('> 执法面：'):
            out.append('> 执法面：池认领/翻面（烧+翻原子·entry+shards 双层）/harvest 对账/供给与饥饿判定/WM 红牌定性/停泊治理与裁定链/认领可见性与接管——上述动作前必读本件；池文件（runnable_pool.json）字节级编辑与写入路径/settle/翻面执行手术/烧录进程机械/点火闸（host_gates/fuse keepblock）→改读 pit-pool-edit.md。')
        else:
            out.append(r)
    acc = ('> 字节对账行（D-06 batch-3 拆件·2026-10-05 r705 bm-b·零丢失断言）：拆前本件 %dB（46 条·条目字节和 %dB）'
           '→拆后本件 %dB（20 条·条目 %dB）+pit-pool-edit.md %dB（26 条·条目 %dB）；'
           '两件条目字节和恒等 %dB·逐条 verbatim 迁移非手抄（变体⑤ bullet-less 三条 r598/r608/r605 随宿主 blob 原样迁移零信息损失）·'
           'receipt=results/_r705bmb_pit_pool_split_receipt.json（r703 范式同源）。'
           % (totals['src'], ENTRIES_SUM, totals['a_file'], A_SUM, totals['b_file'], B_SUM, ENTRIES_SUM))
    insert_at = len(out)
    while insert_at > 0 and out[insert_at - 1] == '':
        insert_at -= 1
    out.insert(insert_at, acc)
    return out


PREFACE_B_HEAD = [
    '# pit-pool-edit —— 池文件编辑与烧录执行机械坑律正典（D-20261002-06 域分件·pit-pool sub-split batch-3）',
    '',
    '> 来源：research/pit-pool.md verbatim 迁出（2026-10-05 r705 bm-b·D-20261002-06 域件 ≤30KB 再平衡·收口窗 10-07）。',
    '> 执法面：池文件（runnable_pool.json）字节级编辑与写入路径（整文件重写禁律/文本级定点手术/roundtrip 恒等探针/EOL 与 indent 探测/needle 锚定/尾逗号/登记 id 镜像）、settle 写路（origin-tip 身份断言/sync_face 调用面）、池面冲突解与基底选择、reland/重落窗律、翻面执行与补翻手术（lane-mirror 检查域/守卫分档/孤儿击杀）、烧录进程机械（worker 池/IPC 粒度）、点火闸（host_gates/crash fuse 落闸/keepblock 时序与版本键）——上述动作前必读本件（认领/翻面语义/可见性/接管/停泊治理→pit-pool.md）。',
]

ACC_B = ('> 字节对账行（零丢失断言）：自 pit-pool.md verbatim 迁出 26 条·条目字节和 %dB==源件同条目字节和（LF blob 面·逐字节恒等）·'
         '机械迁移非手抄（变体⑤ bullet-less 三条 r598/r608/r605 随宿主 blob 原样迁移）·'
         'receipt=results/_r705bmb_pit_pool_split_receipt.json（r703 范式同源）。' % B_SUM)


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
    for n in B_EDIT:
        mapping[n] = 'B'
    assert sorted(mapping) == list(range(1, 47)), 'mapping must cover 1..46 exactly once'

    ent_bytes = [len(e.encode('utf-8')) for e in entries]
    assert sum(ent_bytes) == ENTRIES_SUM, 'entries byte sum mismatch: %d' % sum(ent_bytes)

    a_entries = [entries[i] for i in range(46) if mapping[i + 1] == 'A']
    b_entries = [entries[i] for i in range(46) if mapping[i + 1] == 'B']
    a_sum = sum(len(e.encode('utf-8')) for e in a_entries)
    b_sum = sum(len(e.encode('utf-8')) for e in b_entries)
    assert (a_sum, b_sum) == (A_SUM, B_SUM), 'family sums mismatch: %r' % ((a_sum, b_sum),)

    # variant-5 bullet-less probe: host blobs carrying >1 '[2026-' date tag
    bulletless_hosts = []
    for i, e in enumerate(entries):
        if e.count('[2026-') > 1:
            bulletless_hosts.append(i + 1)
    assert bulletless_hosts == [16, 18], 'bullet-less host probe mismatch: %r' % bulletless_hosts

    # fixed-point totals (preface rows contain the totals themselves)
    totals = {'src': len(raw), 'a_file': 0, 'b_file': 0}
    for _ in range(3):
        pa = build_preface_a(preface_lines, totals)
        a_text = assemble(pa, a_entries, True)      # E46 (source tail) lands in A
        pb = PREFACE_B_HEAD + [ACC_B, '']
        b_text = assemble(pb, b_entries, False)
        new_totals = {'src': len(raw),
                      'a_file': len(a_text.encode('utf-8')),
                      'b_file': len(b_text.encode('utf-8'))}
        if new_totals == totals:
            break
        totals = new_totals
    assert totals['a_file'] <= 30720 and totals['b_file'] <= 30720, \
        '30KB bound violated: %r' % totals

    # zero-loss: every original entry byte-string present exactly once across the two targets
    all_bytes = a_text.encode('utf-8') + b'\x00' + b_text.encode('utf-8')
    for i, e in enumerate(entries):
        b = e.encode('utf-8')
        assert all_bytes.count(b) >= 1, 'entry E%02d lost' % (i + 1)
        tgt = (a_text if mapping[i + 1] == 'A' else b_text).encode('utf-8')
        assert tgt.count(b) == 1, 'entry E%02d not verbatim-unique in target' % (i + 1)
        other = (b_text if mapping[i + 1] == 'A' else a_text).encode('utf-8')
        assert b not in other, 'entry E%02d leaked into non-target' % (i + 1)

    # write outputs
    io.open(SRC, 'w', encoding='utf-8', newline='').write(a_text)
    io.open(NEW, 'w', encoding='utf-8', newline='').write(b_text)

    receipt = {
        'op': 'D-20261002-06 domain-file <=30KB rebalance batch-3: pit-pool two-way sub-split',
        'round': 'r705 bm-b', 'ts': '2026-10-05',
        'mechanism': 'r439/r441/r703 verbatim migration ceremony; prescan rc3 acknowledged hit '
                     '(research/ family, non-delete migration under D-20261002-06 mandate); '
                     'registry in/out row appended; TREASURE_PROTECTION_LAW s2',
        'src_before_bytes': len(raw), 'src_before_entries': 46, 'entries_bytes_sum': ENTRIES_SUM,
        'files': {
            'research/pit-pool.md': {'entries': 20, 'entries_bytes': a_sum, 'file_bytes': totals['a_file'],
                                    'face': 'claim/flip semantics, visibility, takeover, double-burn, parked governance, supply reading'},
            'research/pit-pool-edit.md': {'entries': 26, 'entries_bytes': b_sum, 'file_bytes': totals['b_file'],
                                          'face': 'pool-file byte editing & write-paths, settle, conflict basis, reland windows, flip execution surgery, burn process mechanics, ignition gates'},
        },
        'variant5_bulletless': {'hosts': [16, 18], 'entries': ['r598 (in E16)', 'r608 (in E18)', 'r605 (in E18)'],
                                'handling': 'verbatim inside host blobs, zero info loss, no 2B normalization'},
        'entries': [
            {'e': i + 1, 'target': mapping[i + 1], 'bytes': ent_bytes[i], 'sha16': sha16(entries[i].encode('utf-8'))}
            for i in range(46)
        ],
        'verify': {
            'byte_identity_reconstruction': 'PASS',
            'entries_sum_partition': 'PASS (%d == %d+%d)' % (ENTRIES_SUM, a_sum, b_sum),
            'verbatim_unique_in_target_46': 'PASS',
            'no_leak_across_targets_46': 'PASS',
            'thirty_kb_bound_both': 'PASS',
            'bulletless_host_probe': 'PASS (E16/E18 as expected)',
            'eol': 'LF preserved (asserted no CR in source; outputs LF)',
        },
    }
    io.open(RECEIPT, 'w', encoding='utf-8').write(json.dumps(receipt, ensure_ascii=False, indent=1))
    print('SPLIT OK: A=%dB B=%dB (src was %dB)' % (totals['a_file'], totals['b_file'], len(raw)))


if __name__ == '__main__':
    main()
