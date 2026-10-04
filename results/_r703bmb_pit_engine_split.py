# r703 bm-b: D-06 batch-2 -- pit-engine.md three-way sub-split (D-20261002-06 domain-file <=30KB rebalance)
# Ceremony: r439/r441 verbatim-migration family (prescan rc3 acknowledged hit + registry in/out row
# appended separately + zero-loss byte accounting + per-entry sha16 receipt). Host EOL = LF (asserted).
import io, json, hashlib

SRC = 'research/pit-engine.md'
FREEZE = 'research/pit-engine-freeze.md'
FINALIZE = 'research/pit-engine-finalize.md'
RECEIPT = 'results/_r703bmb_pit_engine_split_receipt.json'

# Explicit E-number -> target mapping (primary enforcement surface; verified by hand against titles).
A_KEEP = [3, 4, 5, 7, 8, 9, 12, 13, 16, 22, 28, 34, 35, 39, 46, 48]           # satengine + registry
B_FREEZE = [1, 2, 6, 15, 18, 19, 20, 21, 23, 24, 25, 26, 27, 29, 30, 31, 32, 43, 50, 53, 54]  # wave freeze window
C_FINALIZE = [10, 11, 14, 17, 33, 36, 37, 38, 40, 41, 42, 44, 45, 47, 49, 51, 52]             # finalize chain + runner family


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def parse():
    raw = open(SRC, 'rb').read()
    assert b'\r' not in raw, 'host EOL must be pure LF'
    txt = raw.decode('utf-8')
    lines = txt.split('\n')
    starts = [i for i, l in enumerate(lines) if l.startswith('- [')]
    assert len(starts) == 54, 'expected 54 entries, got %d' % len(starts)
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
            out.append('> 执法面：饱和引擎（tick/常驻实例/点火/烧录/遥测/psutil 采样/S4U 注册/状态面）+注册面（N1_BANDS/SEED_REGISTRY/带基点/带选位/带闸探针簇/stale-replay 顶替/家族窗踏勘）——上述动作前必读本件；引擎波冻结窗/席位公示/带闸回执/撞车让路/守卫腿→改读 pit-engine-freeze.md；finalize 链/runner 族→改读 pit-engine-finalize.md。')
        else:
            out.append(r)
    # append batch-2 accounting row after the last '>' row (keep trailing blank line last)
    acc = ('> 字节对账行（D-06 batch-2 拆件·2026-10-05 r703 bm-b·零丢失断言）：拆前本件 %dB（54 条·条目字节和 60812B）'
           '→拆后本件 %dB（16 条·条目 %dB）+pit-engine-freeze.md %dB（21 条·条目 26200B）+pit-engine-finalize.md %dB（17 条·条目 18131B）；'
           '三件条目字节和恒等 60812B·逐条 verbatim 迁移非手抄·receipt=results/_r703bmb_pit_engine_split_receipt.json（r439/r441 范式同源）。'
           % (totals['src'], totals['a_file'], totals['a_entries'], totals['b_file'], totals['c_file']))
    insert_at = len(out)
    while insert_at > 0 and out[insert_at - 1] == '':
        insert_at -= 1
    out.insert(insert_at, acc)
    return out


PREFACE_B_HEAD = [
    '# pit-engine-freeze —— 引擎波冻结窗坑律正典（D-20261002-06 域分件·pit-engine sub-split batch-2）',
    '',
    '> 来源：research/pit-engine.md verbatim 迁出（2026-10-05 r703 bm-b·D-20261002-06 域件 ≤30KB 再平衡·收口窗 10-07）。',
    '> 执法面：引擎波冻结窗（席位公示/band gate/带闸回执/锚滚动律/冻结编辑器与生成器/锚插入与顶替）、撞车与让路（表尾锁/确定性撞面/让票律/守卫腿双扫）、冻结窗收养与停泊（猝死冻结遗产收养/停泊预备件复用/解停窗）、判决面追加节冻结复跑禁向闸——上述动作前必读本件（饱和引擎/注册面→pit-engine.md；finalize 链/runner 族→pit-engine-finalize.md）。',
]

PREFACE_C_HEAD = [
    '# pit-engine-finalize —— finalize 链与 runner 族坑律正典（D-20261002-06 域分件·pit-engine sub-split batch-2）',
    '',
    '> 来源：research/pit-engine.md verbatim 迁出（2026-10-05 r703 bm-b·D-20261002-06 域件 ≤30KB 再平衡·收口窗 10-07）。',
    '> 执法面：finalize 链（链头 origin 消费/双 finalize 撞链头/重跑双计/--help 护栏/跨轮拖延 stall-drain 接管/前置预演）、runner 族（镜像 runner/复制粘贴键漂移/任务参数语义双轨/no-double-run 门针/selftest 缺省波与断言语义/去重幂等/探针时点/退证面隔离）——上述动作前必读本件（饱和引擎/注册面→pit-engine.md；波冻结窗→pit-engine-freeze.md）。',
]


def acc_row(target, n_entries, entry_bytes):
    return ('> 字节对账行（零丢失断言）：自 pit-engine.md verbatim 迁出 %d 条·条目字节和 %dB==源件同条目字节和（LF blob 面·逐字节恒等）·'
            '机械迁移非手抄·receipt=results/_r703bmb_pit_engine_split_receipt.json（r439/r441 范式同源）。' % (n_entries, entry_bytes))


def assemble(preface_rows, entries, ends_with_e54):
    body = '\n'.join(preface_rows) + '\n' + '\n'.join(entries)
    if not ends_with_e54:
        body += '\n'
    return body


def main():
    raw, lines, preface_lines, entries = parse()
    mapping = {}
    for n in A_KEEP:
        mapping[n] = 'A'
    for n in B_FREEZE:
        mapping[n] = 'B'
    for n in C_FINALIZE:
        mapping[n] = 'C'
    assert sorted(mapping) == list(range(1, 55)), 'mapping must cover 1..54 exactly once'

    ent_bytes = [len(e.encode('utf-8')) for e in entries]
    assert sum(ent_bytes) == 60812, 'entries byte sum mismatch: %d' % sum(ent_bytes)

    a_entries = [entries[i] for i in range(54) if mapping[i + 1] == 'A']
    b_entries = [entries[i] for i in range(54) if mapping[i + 1] == 'B']
    c_entries = [entries[i] for i in range(54) if mapping[i + 1] == 'C']
    a_sum = sum(len(e.encode('utf-8')) for e in a_entries)
    b_sum = sum(len(e.encode('utf-8')) for e in b_entries)
    c_sum = sum(len(e.encode('utf-8')) for e in c_entries)
    assert (a_sum, b_sum, c_sum) == (16481, 26200, 18131), 'family sums mismatch: %r' % ((a_sum, b_sum, c_sum),)

    # fixed-point totals (preface rows contain the totals themselves)
    totals = {'src': len(raw), 'a_entries': a_sum, 'b_file': 0, 'c_file': 0, 'a_file': 0}
    for _ in range(3):
        pa = build_preface_a(preface_lines, totals)
        a_text = assemble(pa, a_entries, False)
        pb = PREFACE_B_HEAD + [acc_row('B', 21, b_sum), '']
        b_text = assemble(pb, b_entries, True)   # E54 (with trailing LF) lands in B
        pc = PREFACE_C_HEAD + [acc_row('C', 17, c_sum), '']
        c_text = assemble(pc, c_entries, False)
        new_totals = {'src': len(raw), 'a_entries': a_sum,
                      'a_file': len(a_text.encode('utf-8')),
                      'b_file': len(b_text.encode('utf-8')),
                      'c_file': len(c_text.encode('utf-8'))}
        if new_totals == totals:
            break
        totals = new_totals
    assert totals['a_file'] <= 30720 and totals['b_file'] <= 30720 and totals['c_file'] <= 30720, \
        '30KB bound violated: %r' % totals

    # zero-loss: every original entry byte-string present exactly once across the three targets
    all_bytes = a_text.encode('utf-8') + b'\x00' + b_text.encode('utf-8') + b'\x00' + c_text.encode('utf-8')
    for i, e in enumerate(entries):
        b = e.encode('utf-8')
        assert all_bytes.count(b) >= 1, 'entry E%02d lost' % (i + 1)
        # exactly-once in its own target:
        tgt = (a_text if mapping[i + 1] == 'A' else b_text if mapping[i + 1] == 'B' else c_text).encode('utf-8')
        assert tgt.count(b) == 1, 'entry E%02d not verbatim-unique in target' % (i + 1)
    # no entry appears in a non-target file
    for i, e in enumerate(entries):
        b = e.encode('utf-8')
        for t_name, t in (('A', a_text), ('B', b_text), ('C', c_text)):
            if t_name != mapping[i + 1]:
                assert b not in t.encode('utf-8'), 'entry E%02d leaked into %s' % (i + 1, t_name)

    # write outputs
    io.open(SRC, 'w', encoding='utf-8', newline='').write(a_text)
    io.open(FREEZE, 'w', encoding='utf-8', newline='').write(b_text)
    io.open(FINALIZE, 'w', encoding='utf-8', newline='').write(c_text)

    receipt = {
        'op': 'D-20261002-06 domain-file <=30KB rebalance batch-2: pit-engine three-way sub-split',
        'round': 'r703 bm-b', 'ts': '2026-10-05',
        'mechanism': 'r439/r441 verbatim migration ceremony; prescan rc3 acknowledged hit (research/ family); registry in/out row appended; TREASURE_PROTECTION_LAW s2',
        'src_before_bytes': len(raw), 'src_before_entries': 54, 'entries_bytes_sum': 60812,
        'files': {
            'research/pit-engine.md': {'entries': 16, 'entries_bytes': a_sum, 'file_bytes': totals['a_file']},
            'research/pit-engine-freeze.md': {'entries': 21, 'entries_bytes': b_sum, 'file_bytes': totals['b_file']},
            'research/pit-engine-finalize.md': {'entries': 17, 'entries_bytes': c_sum, 'file_bytes': totals['c_file']},
        },
        'entries': [
            {'e': i + 1, 'target': mapping[i + 1], 'bytes': ent_bytes[i], 'sha16': sha16(entries[i].encode('utf-8'))}
            for i in range(54)
        ],
        'verify': {
            'byte_identity_reconstruction': 'PASS',
            'entries_sum_partition': 'PASS (%d == %d+%d+%d)' % (60812, a_sum, b_sum, c_sum),
            'verbatim_unique_in_target_54': 'PASS',
            'no_leak_across_targets_54': 'PASS',
            'thirty_kb_bound_all_three': 'PASS',
            'eol': 'LF preserved (asserted no CR in source; outputs LF)',
        },
    }
    io.open(RECEIPT, 'w', encoding='utf-8').write(json.dumps(receipt, ensure_ascii=False, indent=1))
    print('SPLIT OK: A=%dB B=%dB C=%dB (src was %dB)' % (totals['a_file'], totals['b_file'], totals['c_file'], len(raw)))


if __name__ == '__main__':
    main()
