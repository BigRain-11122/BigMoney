# -*- coding: utf-8 -*-
# r707 bm-b: D-06 batch-3 final -- pit-git-surgery.md two-way sub-split (D-20261002-06 domain-file <=30KB rebalance)
# Ceremony: r439/r441/r703/r705/r706/r707-netpath verbatim-migration family (prescan rc3
# acknowledged hit + registry in/out row appended separately + zero-loss byte accounting
# + per-entry sha16 receipt). Host EOL = LF (asserted). No fused hosts (probe asserted).
import io, json, hashlib

SRC = 'research/pit-git-surgery.md'
NEW = 'research/pit-git-surgery-guard.md'
RECEIPT = 'results/_r707bmb_pit_surgery_split_receipt.json'

# A = pit-git-surgery.md keep: surgical CAS direct-injection mechanics family -- temp-index
#     payload/staging, commit-tree message source, diff-index --cached asserts, update-ref +
#     checkout Already-on, push remote-name, surgical payload fork-point derive, post-op
#     realign M-face classification (prefix-driver/raw hash-object/autocrlf), stale-face
#     probes, reland loops (un-FF-reland/facet restore/origin-verbatim live fetch),
#     hash-object filters + update-index flags, ls-tree column/manifest, byte surgery
#     (EOL marker probe/orphan CR suppression/union dedup + superseded-variant containment).
# B = pit-git-surgery-guard.md: yield/closeout tree guards + deletion-set self-proof family --
#     r519 phantom-D sweep disease full spectrum, yield window order laws (ownership verify ->
#     twin delete -> detach), rebase-band reservation exhaust scan, same-anchor dual-add
#     constructive merge, deletion-set asserts + D-phantom discrimination + owner-gate
#     priority + D-face zeroing + pre-push claw deletion-set bipartition + whitelist
#     interaction + bad-object misblock.
A_KEEP = [3, 7, 14, 15, 19, 20, 22, 23, 24, 26, 28, 29, 32, 35, 36, 37, 38, 39, 41, 42, 43, 44]
B = [1, 2, 4, 5, 6, 8, 9, 10, 11, 12, 13, 16, 17, 18, 21, 25, 27, 30, 31, 33, 34, 40]

N = 44
ENTRIES_SUM = 43567
A_SUM = 19786
B_SUM = 23781


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def parse():
    raw = open(SRC, 'rb').read()
    assert b'\r' not in raw, 'host EOL must be pure LF'
    txt = raw.decode('utf-8')
    lines = txt.split('\n')
    starts = [i for i, l in enumerate(lines) if l.lstrip().startswith('- [')]
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
        if r.startswith('# pit-git-surgery '):
            out.append('# pit-git-surgery —— 外科推送 CAS 直投机械坑律正典（D-20261002-06 域分件·pit-git sub-split batch-1·外科机械核·r707 二段拆件）')
        elif r.startswith('> 执法面：'):
            out.append('> 执法面：外科 CAS 直投机械族——temp-index payload 与删除 staging/commit-tree message 源盲取/diff-index --cached 断言腿/push remote 名与 fork 点 payload derive/update-ref 后 checkout 零动作/术后 realign M 面分类（前缀驱动·raw hash-object·autocrlf 滤镜）/术后陈旧面定性探针与 file-move 伪影/reland 环（撤-FF-重落·分面恢复·origin-verbatim 执行时点实取）/hash-object --no-filters 与 update-index --cacheinfo 旗/ls-tree 列位与文件清点/字节手术（冲突标记 EOL 形态实探·孤 CR 抑制·union 手术 dedup 与被取代变体子串遏制）——外科推送与字节手术动作前必读本件；让路/closeout 树卫与删除集自证族→改读 pit-git-surgery-guard.md。')
        else:
            out.append(r)
    acc = ('> 字节对账行（D-06 batch-3 二段拆件·2026-10-05 r707 bm-b·零丢失断言）：拆前本件 45114B（44 条·条目字节和 %dB）'
           '→拆后本件 %dB（22 条·条目 %dB）+pit-git-surgery-guard.md %dB（22 条·条目 %dB）；'
           '两件条目字节和恒等 %dB·逐条 verbatim 迁移非手抄（融合探针零命中）·'
           'receipt=results/_r707bmb_pit_surgery_split_receipt.json（r703/r705/r706/r707-netpath 范式同源）。'
           % (ENTRIES_SUM, totals['a_file'], A_SUM, totals['b_file'], B_SUM, ENTRIES_SUM))
    insert_at = len(out)
    while insert_at > 0 and out[insert_at - 1] == '':
        insert_at -= 1
    out.insert(insert_at, acc)
    return out


PREFACE_B = [
    '# pit-git-surgery-guard —— 让路/closeout 树卫与删除集自证坑律正典（D-20261002-06 域分件·pit-git-surgery sub-split·r707 二段拆件）',
    '',
    '> 来源：research/pit-git-surgery.md verbatim 迁出（2026-10-05 r707 bm-b·D-20261002-06 域件 ≤30KB 再平衡·收口窗 10-07）。',
    '> 执法面：让路/closeout 树卫与删除集自证族——r519 phantom-D 扫树病全谱（整树面回退已推件·跨机误删与单写者簿记回退·closeout 扫树病各犯·外科标签不免疫·重父 stale tree·reset --soft stale index·外科 rebroadcast stale 基）/让路窗序律（验属 audit.machine→删孪生→detach·重基带位预留面穷尽扫描·同锚双加构式合并·验属×树变交割窗·stale-index phantom-D 伪影）/删除集自证与判别（D 伪影判别三断言·分面属主门优先于 blob 新近度·D 面未清零 add -A 吞删除·pre-push 爪删除集两分法与 inbox 白名单互作用与 bad-object 误拦·churn-absorb 前 D 项属主核验）——让路/closeout/pre-push 删除集动作前必读本件；外科 CAS 直投机械族→pit-git-surgery.md。',
    '> 字节对账行（零丢失断言）：自 pit-git-surgery.md verbatim 迁出 22 条·条目字节和 %dB==源件同条目字节和（LF blob 面·逐字节恒等）·机械迁移非手抄·receipt=results/_r707bmb_pit_surgery_split_receipt.json（r703/r705/r706/r707-netpath 范式同源）。' % B_SUM,
    '',
]


def assemble(preface_rows, entries):
    return '\n'.join(preface_rows) + '\n' + '\n'.join(entries) + '\n'


def main():
    raw, lines, preface_lines, entries = parse()
    mapping = {}
    for n in A_KEEP:
        mapping[n] = 'A'
    for n in B:
        mapping[n] = 'B'
    assert sorted(mapping) == list(range(1, N + 1)), 'mapping must cover 1..%d exactly once' % N

    ent_bytes = [len(e.encode('utf-8')) for e in entries]
    assert sum(ent_bytes) == ENTRIES_SUM, 'entries byte sum mismatch: %d' % sum(ent_bytes)

    a_entries = [entries[i] for i in range(N) if mapping[i + 1] == 'A']
    b_entries = [entries[i] for i in range(N) if mapping[i + 1] == 'B']
    a_sum = sum(len(e.encode('utf-8')) for e in a_entries)
    b_sum = sum(len(e.encode('utf-8')) for e in b_entries)
    assert (a_sum, b_sum) == (A_SUM, B_SUM), 'family sums mismatch: %r' % ((a_sum, b_sum),)

    # fused-inline probe: this host carries no fused passengers
    fused_hosts = [i + 1 for i, e in enumerate(entries) if e.count('[2026-') > 1]
    assert fused_hosts == [], 'unexpected fused hosts: %r' % fused_hosts

    # fixed-point totals (A accounting row carries both file sizes)
    totals = {'a_file': 0, 'b_file': 0}
    for _ in range(4):
        pa = build_preface_a(preface_lines, totals)
        a_text = assemble(pa, a_entries)
        b_text = assemble(PREFACE_B, b_entries)
        new_totals = {'a_file': len(a_text.encode('utf-8')),
                      'b_file': len(b_text.encode('utf-8'))}
        if new_totals == totals:
            break
        totals = new_totals
    assert totals['a_file'] <= 30720 and totals['b_file'] <= 30720, \
        '30KB bound violated: %r' % totals

    # zero-loss: every original entry byte-string present exactly once, in its target only
    for i, e in enumerate(entries):
        b = e.encode('utf-8')
        tgt = {'A': a_text, 'B': b_text}[mapping[i + 1]].encode('utf-8')
        assert tgt.count(b) == 1, 'entry E%02d not verbatim-unique in target' % (i + 1)
        other = {'A': b_text, 'B': a_text}[mapping[i + 1]].encode('utf-8')
        assert b not in other, 'entry E%02d leaked into non-target' % (i + 1)

    io.open(SRC, 'w', encoding='utf-8', newline='').write(a_text)
    io.open(NEW, 'w', encoding='utf-8', newline='').write(b_text)

    receipt = {
        'op': 'D-20261002-06 domain-file <=30KB rebalance batch-3 final: pit-git-surgery two-way sub-split',
        'round': 'r707 bm-b', 'ts': '2026-10-05',
        'mechanism': 'r439/r441/r703/r705/r706/r707-netpath verbatim migration ceremony; prescan rc3 '
                     'acknowledged hit (research/pit-git-surgery.md registered, non-delete migration '
                     'under D-20261002-06 mandate, closeout 10-07 12:00); registry in/out row appended; '
                     'TREASURE_PROTECTION_LAW s2',
        'src_before_bytes': len(raw), 'src_before_entries': N, 'entries_bytes_sum': ENTRIES_SUM,
        'files': {
            'research/pit-git-surgery.md': {'entries': 22, 'entries_bytes': a_sum, 'file_bytes': totals['a_file'],
                                            'face': 'surgical CAS direct-injection mechanics: temp-index, commit-tree, diff-index asserts, update-ref, push remote-name, fork-point payload, post-op realign classification, reland loops, hash-object filters, ls-tree columns, byte surgery'},
            'research/pit-git-surgery-guard.md': {'entries': 22, 'entries_bytes': b_sum, 'file_bytes': totals['b_file'],
                                                  'face': 'yield/closeout tree guards + deletion-set self-proof: r519 phantom-D spectrum, yield window order laws, ownership gates, D-phantom discrimination, pre-push claw deletion-set faces'},
        },
        'fused_inline_hosts': {'hosts': [], 'handling': 'probe zero hits'},
        'entries': [
            {'e': i + 1, 'target': mapping[i + 1], 'bytes': ent_bytes[i],
             'sha16': sha16(entries[i].encode('utf-8'))}
            for i in range(N)
        ],
        'verify': {
            'byte_identity_reconstruction': 'PASS',
            'entries_sum_partition': 'PASS (%d == %d+%d)' % (ENTRIES_SUM, a_sum, b_sum),
            'verbatim_unique_in_target_44': 'PASS',
            'no_leak_across_targets_44': 'PASS',
            'thirty_kb_bound_both': 'PASS',
            'fused_host_probe': 'PASS (zero fused hosts)',
            'eol': 'LF preserved (asserted no CR in source; outputs LF)',
        },
    }
    io.open(RECEIPT, 'w', encoding='utf-8').write(json.dumps(receipt, ensure_ascii=False, indent=1))
    print('SPLIT OK: A=%dB B=%dB (src was %dB)' % (totals['a_file'], totals['b_file'], len(raw)))


if __name__ == '__main__':
    main()
