# D-06 post-split increment sweep, r625 bm-b (2026-10-03).
# Migrate 6 hot-layer pit entries from root CODELY.md (CRLF disk face) into
# domain pit files (LF disk face), byte-surgical, verbatim, zero-loss
# accounting (r399/r420 paradigm). ASCII-only console output (GBK console law).
import hashlib, json

ROOT = 'CODELY.md'


def U(s):
    return s.encode('utf-8')


PLAN = [
    (U('- [2026-10-03 14:2x r618 bm-b] croc'), 'research/pit-spawn.md', 'r618-croc'),
    (U('- [2026-10-03 14:2x r618 bm-b] 工具'), 'research/pit-ps.md', 'r618-tool'),
    (U('- [2026-10-03 15:0x r619 bm-b]'), 'research/pit-git.md', 'r619-quit'),
    (U('- [2026-10-03 15:1x r620 bm-b]'), 'research/pit-git.md', 'r620-churn'),
    (U('- [2026-10-03 15:33x r621 bm-b]'), 'research/pit-git.md', 'r621-tip'),
    (U('- [2026-10-03 16:4x r624 bm-b]'), 'research/pit-git.md', 'r624-pick'),
]

# Accounting line appended at each target file tail (LF face).
ACC = {
    'research/pit-git.md':
        '> 增量回扫行（r625 bm-b·D-06 post-split 增量批次）：热层条目 4 条 verbatim 追加（10-03 15:0x~16:4x 批·r619 断头 rebase 收口 quit 门行归属探针律+r620 churn-absorb 轮号前置读律+r621 多环陈旧 tip 合并收敛律+r624 rebase 停 pick 重放覆盖在飞 daemon 追加行坑）·追加核 {core_bytes}B（LF blob 面·md5={core_md5}）·零丢失断言 PASS（逐行 verbatim 在场+源件 CODELY.md 零残留·机械迁移非手抄·r399/r420 范式同源）。',
    'research/pit-ps.md':
        '> 增量回扫行（r625 bm-b·D-06 post-split 增量批次）：热层条目 1 条 verbatim 追加（10-03 14:2x·r618 工具签名漂移与 D-19 通道备胎两条——Invoke-SilentExe -Args/-ArgString 签名崩/ssh.github.com 双连击重置 https blobless fallback/PS 管道哈希假值 python 直取）·追加核 {core_bytes}B（LF blob 面·md5={core_md5}）·零丢失断言 PASS（逐行 verbatim 在场+源件 CODELY.md 零残留·机械迁移非手抄·r399/r420 范式同源）；水位注记：append 后 {size}B（越 10KB 硬线·结构性近线态与 pit-git 同族，阈值重锚=集团/GM 裁定面，勿为字节数归档在役律 r504）。',
    'research/pit-spawn.md':
        '> 增量回扫行（r625 bm-b·D-06 post-split 增量批次）：热层条目 1 条 verbatim 追加（10-03 14:2x·r618 croc「could not secure channel」=relay 垃圾字节面非版本失配——双端同版 PAKE 崩·版本假说死亡·T-156 send3/send4 双实弹）·追加核 {core_bytes}B（LF blob 面·md5={core_md5}）·零丢失断言 PASS（逐行 verbatim 在场+源件 CODELY.md 零残留·机械迁移非手抄·r399/r420 范式同源）。',
}

# Root pointer-line clauses: appended in place of each line's trailing full stop.
PTR_NEEDLE = {
    U('- 域指针·D-20261002-06 首拆件'):
        U('；r625 bm-b 增量回扫 4 条（r619 断头 rebase quit 门行归属探针律/r620 churn-absorb 轮号前置读律/r621 多环陈旧 tip 合并收敛律/r624 rebase pick 重放覆盖坑）已入件（件内对账行为准）'),
    U('- 域指针·D-20261002-06 PS 域拆件'):
        U('；r625 bm-b 增量回扫 1 条（r618 工具签名漂移+D-19 通道备胎复合条）已入件（件内对账行为准）'),
    U('- 域指针·D-20261002-06 spawn/tooling 域拆件'):
        U('；r625 bm-b 增量回扫 1 条（r618 croc secure channel=relay 垃圾字节面·双端同版仍 PAKE 崩·版本假说死亡）已入件（件内对账行为准）'),
}
FULLSTOP = U('。')


def build_acc(tgt, core):
    tpl = ACC[tgt]
    t = tpl.replace('{core_bytes}', str(len(core))).replace(
        '{core_md5}', hashlib.md5(core).hexdigest())
    if '{size}' in t:
        size = 0
        for _ in range(3):  # fixed-point on digit count
            acc_b = U(t.replace('{size}', str(size)))
            size = ORIG_SIZE[tgt] + len(core) + len(acc_b)
        acc_b = U(t.replace('{size}', str(size)))
        assert size == ORIG_SIZE[tgt] + len(core) + len(acc_b), 'size fixed-point failed'
        return acc_b
    return U(t)


ORIG_SIZE = {}

def main():
    root_b = open(ROOT, 'rb').read()
    root_before = len(root_b)
    parts = root_b.split(b'\r\n')
    n_term = len(parts) - 1
    removed_idx, moved = [], []
    for needle, target, tag in PLAN:
        hits = [i for i, p in enumerate(parts) if p.startswith(needle)]
        assert len(hits) == 1, 'needle count!=1 for %s: %d' % (tag, len(hits))
        i = hits[0]
        assert i not in removed_idx, 'dup line for %s' % tag
        removed_idx.append(i)
        moved.append({'tag': tag, 'target': target, 'idx': i,
                      'text': parts[i], 'had_crlf': i < n_term})
    ptr_new = {}
    ptr_added = 0
    for pn, clause in PTR_NEEDLE.items():
        hits = [i for i, p in enumerate(parts) if p.startswith(pn)]
        assert len(hits) == 1, 'ptr needle count!=1: %d' % len(hits)
        i = hits[0]
        assert parts[i].endswith(FULLSTOP), 'ptr line lacks trailing full stop'
        new_line = parts[i][:-len(FULLSTOP)] + clause + FULLSTOP
        ptr_new[i] = new_line
        ptr_added += len(new_line) - len(parts[i])
        parts[i] = new_line
    for i in sorted(removed_idx, reverse=True):
        del parts[i]
    root_new = b'\r\n'.join(parts)
    removed_total = sum(len(m['text']) + (2 if m['had_crlf'] else 0) for m in moved)
    cores = {}
    for m in moved:
        cores.setdefault(m['target'], []).append(m['text'] + b'\n')
    receipt = {'round': 'r625 bm-b', 'purpose': 'D-06 post-split increment sweep',
               'root_before_bytes': root_before, 'root_after_bytes': len(root_new),
               'root_removed_bytes': removed_total, 'root_ptr_added_bytes': ptr_added,
               'targets': {}, 'entries': []}
    for tgt, chunks in cores.items():
        tb = open(tgt, 'rb').read()
        ORIG_SIZE[tgt] = len(tb)
        assert tb.endswith(b'\n'), 'target lacks trailing LF: %s' % tgt
        assert tb.count(b'\r') == 0, 'target has CR before append'
        core = b''.join(chunks)
        acc_b = build_acc(tgt, core)
        new_tb = tb + core + acc_b
        assert new_tb.count(b'\r') == 0, 'lone CR introduced'
        for m in moved:
            if m['target'] == tgt:
                assert m['text'] in new_tb, 'verbatim missing after append'
        open(tgt, 'wb').write(new_tb)
        receipt['targets'][tgt] = {
            'before_bytes': len(tb), 'after_bytes': len(new_tb),
            'core_bytes': len(core), 'core_md5_lf': hashlib.md5(core).hexdigest(),
            'acc_bytes': len(acc_b),
            'entries': [m['tag'] for m in moved if m['target'] == tgt]}
    receipt['entries'] = [
        {'tag': m['tag'], 'target': m['target'], 'line_bytes': len(m['text']),
         'had_crlf': m['had_crlf']} for m in moved]
    open(ROOT, 'wb').write(root_new)
    rb2 = open(ROOT, 'rb').read()
    for needle, tgt, tag in PLAN:
        assert rb2.count(needle) == 0, 'residue bytes %s' % tag
    assert rb2.count(b'\n') == rb2.count(b'\r\n'), 'root lone LF leaked'
    assert rb2.count(b'\r') == rb2.count(b'\r\n'), 'root lone CR leaked'
    expect_after = root_before - removed_total + ptr_added
    assert len(rb2) == expect_after, 'root size identity: %d != %d' % (len(rb2), expect_after)
    for tgt, info in receipt['targets'].items():
        tb2 = open(tgt, 'rb').read()
        assert tb2.count(b'\r') == 0, 'target CR leaked: %s' % tgt
        assert len(tb2) == info['after_bytes'], 'target size identity: %s' % tgt
    receipt['zero_loss'] = 'PASS'
    json.dump(receipt, open('results/_r625bmb_d06_sweep_receipt.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('SWEEP_OK entries=%d root %d->%d (-removed %d +ptr %d)' % (
        len(moved), root_before, len(rb2), removed_total, ptr_added))
    for tgt, info in receipt['targets'].items():
        print('  %s: %d->%d core=%dB acc=%dB md5=%s' % (
            tgt.encode('ascii'), info['before_bytes'], info['after_bytes'],
            info['core_bytes'], info['acc_bytes'], info['core_md5_lf']))


if __name__ == '__main__':
    main()
