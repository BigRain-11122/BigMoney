# -*- coding: utf-8 -*-
# r707 bm-b: D-06 batch-3 final -- pit-git-netpath.md two-way sub-split (D-20261002-06 domain-file <=30KB rebalance)
# Ceremony: r439/r441/r703/r705/r706 verbatim-migration family (prescan rc3 acknowledged hit
# + registry in/out row appended separately + zero-loss byte accounting + per-entry sha16 receipt).
# Host EOL = LF (asserted). Fused inline hosts E8/E9 (r410 law) migrate verbatim inside
# their host blobs -- E9 -> A (rebase core), E8 -> B (racewin) -- zero information loss.
import io, json, hashlib

SRC = 'research/pit-git-netpath.md'
NEW = 'research/pit-git-racewin.md'
RECEIPT = 'results/_r707bmb_pit_netpath_split_receipt.json'

# A = pit-git-netpath.md keep: rebase netpath core (pull --rebase/autostash long-window,
#     refuse/quitrouted netpath family r305/r501/r507/r613/r427/r433, dead-rebase legacy
#     closeout, live-burn-window daemon interference: hijack/checkout truncation/clean-index
#     double-refuse/mute EDITOR, mid-rebase conflict re-adjudication + diff3 residual asserts).
# B = pit-git-racewin.md: S0/S7 integration windows + push-race closeout family (integration
#     blocking triage, shared-tree backoff, dead-session adoption + CAS integration, pure-FF
#     disposal + origin re-advance, appender dual-head signature, merge stage-mapping swap,
#     union dedup domain + amend hijack, churn-absorb pre-read, stale-tip merge convergence,
#     merge-window triple pits, twin-regen TIE, prealign netpath, staging swallow checkout,
#     guard false-positives, five-race closeout, yield-merge theirs-canonical, daemon tick
#     stale writeback, cross-round scratch script discipline).
A_KEEP = [1, 3, 4, 5, 7, 9, 11, 12, 13, 14, 15, 19, 20, 21, 22, 25, 27, 30, 31, 34, 37]
B = [2, 6, 8, 10, 16, 17, 18, 23, 24, 26, 28, 29, 32, 33, 35, 36, 38, 39, 40, 41, 42, 43]

N = 43
ENTRIES_SUM = 44869
A_SUM = 22663
B_SUM = 22206


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
        if r.startswith('# pit-git-netpath '):
            out.append('# pit-git-netpath —— rebase 净路坑律正典（D-20261002-06 域分件·pit-git sub-split batch-2·rebase 净路核·r707 二段拆件）')
        elif r.startswith('> 执法面：'):
            out.append('> 执法面：pull --rebase 与 autostash 长窗衰变/rebase 假拒绝净路族（r305/r501/r507/r613/r427/r433）/--quit 余 pick 与游离 HEAD/多 refspec 与 cherry-pick 收编超集路由/活烧窗 daemon 干扰（抢道劫持·checkout 截断活写·净索引双拒·哑终端 EDITOR）/死 rebase 遗产收口三律/冲突二次裁决与 diff3 残留断言行首匹配/AA 产品件信封分歧裁定——rebase 净路动作前必读本件；merge/FF/push-race 集成窗与收口窗（集成阻塞分面·共享树退避·纯 FF·merge stage 映射·union 去重域·churn-absorb·预对齐净路·守卫假阳性·让路合并）→改读 pit-git-racewin.md。')
        else:
            out.append(r)
    acc = ('> 字节对账行（D-06 batch-3 二段拆件·2026-10-05 r707 bm-b·零丢失断言）：拆前本件 46328B（43 条·条目字节和 %dB）'
           '→拆后本件 %dB（21 条·条目 %dB）+pit-git-racewin.md %dB（22 条·条目 %dB）；'
           '两件条目字节和恒等 %dB·逐条 verbatim 迁移非手抄（融合宿主 E8/E9 各携 2 日期签·E9 随宿主落本件·E8 随宿主落 racewin·原样迁移零信息损失·r410 律）·'
           'receipt=results/_r707bmb_pit_netpath_split_receipt.json（r703/r705/r706 范式同源）。'
           % (ENTRIES_SUM, totals['a_file'], A_SUM, totals['b_file'], B_SUM, ENTRIES_SUM))
    insert_at = len(out)
    while insert_at > 0 and out[insert_at - 1] == '':
        insert_at -= 1
    out.insert(insert_at, acc)
    return out


PREFACE_B = [
    '# pit-git-racewin —— merge/FF/push-race 集成窗坑律正典（D-20261002-06 域分件·pit-git-netpath sub-split·r707 二段拆件）',
    '',
    '> 来源：research/pit-git-netpath.md verbatim 迁出（2026-10-05 r707 bm-b·D-20261002-06 域件 ≤30KB 再平衡·收口窗 10-07）。',
    '> 执法面：S0/S7 集成窗与 push-race 收口窗——集成三重阻塞分面定性/共享树退避轮正法/猝死会话收编与 CAS 整合法/push 阻塞窗 daemon tick 积压/纯 FF 处置律与 origin 二次前进/appender 批量 commit 双头分叉诊断签名/merge 向 stage 映射交换律（r701(3) 翻面）/union 去重域与 amend 撞劫/churn-absorb 轮号前置读/多环陈旧 tip 合并收敛/merge 窗三连坑与残留 marker 全仓扫/孪生再生面 TIE 陷阱/预对齐窗 staging 吞 checkout/merge 收口守卫假阳性/五连 push-race 收口/让路合并 theirs-canonical/daemon tick×merge worktree 陈旧回写/跨轮 scratch 脚本盲执行——上述动作前必读本件；rebase 净路族（假拒绝净路/--quit/活烧窗干扰/死 rebase 收口）→pit-git-netpath.md。',
    '> 字节对账行（零丢失断言）：自 pit-git-netpath.md verbatim 迁出 22 条·条目字节和 %dB==源件同条目字节和（LF blob 面·逐字节恒等）·机械迁移非手抄（融合宿主 E8 内联乘客随宿主 blob 原样迁移零信息损失·r410 律）·receipt=results/_r707bmb_pit_netpath_split_receipt.json（r703/r705/r706 范式同源）。' % B_SUM,
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

    # fused-inline probe (r706 block-boundary law): hosts carrying >1 '[2026-' tag inline
    fused_hosts = []
    for i, e in enumerate(entries):
        if e.count('[2026-') > 1:
            fused_hosts.append(i + 1)
    assert fused_hosts == [8, 9], 'fused host probe mismatch: %r' % fused_hosts
    assert mapping[8] == 'B' and mapping[9] == 'A', 'fused hosts must not split across targets'

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
        'op': 'D-20261002-06 domain-file <=30KB rebalance batch-3 final: pit-git-netpath two-way sub-split',
        'round': 'r707 bm-b', 'ts': '2026-10-05',
        'mechanism': 'r439/r441/r703/r705/r706 verbatim migration ceremony; prescan rc3 acknowledged hit '
                     '(research/pit-git-netpath.md registered, non-delete migration under D-20261002-06 '
                     'mandate, closeout 10-07 12:00); registry in/out row appended; TREASURE_PROTECTION_LAW s2',
        'src_before_bytes': len(raw), 'src_before_entries': N, 'entries_bytes_sum': ENTRIES_SUM,
        'files': {
            'research/pit-git-netpath.md': {'entries': 21, 'entries_bytes': a_sum, 'file_bytes': totals['a_file'],
                                            'face': 'rebase netpath core: autostash long-window, refuse/quit netpath family, dead-rebase legacy, live-burn daemon interference, conflict re-adjudication + diff3 residual asserts'},
            'research/pit-git-racewin.md': {'entries': 22, 'entries_bytes': b_sum, 'file_bytes': totals['b_file'],
                                            'face': 'S0/S7 integration windows + push-race closeout family: FF disposal, merge stage-mapping, union dedup, churn-absorb, prealign, guard false-positives, yield-merge, stale writeback'},
        },
        'fused_inline_hosts': {'hosts': [8, 9],
                               'handling': 'E9 -> A, E8 -> B; passengers migrate verbatim inside host blobs (r410 law), zero info loss'},
        'entries': [
            {'e': i + 1, 'target': mapping[i + 1], 'bytes': ent_bytes[i],
             'sha16': sha16(entries[i].encode('utf-8'))}
            for i in range(N)
        ],
        'verify': {
            'byte_identity_reconstruction': 'PASS',
            'entries_sum_partition': 'PASS (%d == %d+%d)' % (ENTRIES_SUM, a_sum, b_sum),
            'verbatim_unique_in_target_43': 'PASS',
            'no_leak_across_targets_43': 'PASS',
            'thirty_kb_bound_both': 'PASS',
            'fused_host_probe': 'PASS (hosts 8->B, 9->A, whole-blob migration)',
            'eol': 'LF preserved (asserted no CR in source; outputs LF)',
        },
    }
    io.open(RECEIPT, 'w', encoding='utf-8').write(json.dumps(receipt, ensure_ascii=False, indent=1))
    print('SPLIT OK: A=%dB B=%dB (src was %dB)' % (totals['a_file'], totals['b_file'], len(raw)))


if __name__ == '__main__':
    main()
