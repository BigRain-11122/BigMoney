# -*- coding: utf-8 -*-
"""_r585bma_engine_split.py -- CODELY.md engine-domain split (D-20261002-06, third split).
Mechanical verbatim migration of 33 engine-domain pit entries CODELY.md -> research/pit-engine.md.
Laws: r530 bytes-in/bytes-out, r373 blob-space (LF) accounting + working-tree EOL write,
r335 machine-verification (no hand-copy), zero-loss assertion (entry bytes == net removal).
Idempotent: re-run after successful split detects pit-engine.md and exits 2 (refuse double-split).
"""
import hashlib, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, 'CODELY.md')
PIT = os.path.join(ROOT, 'research', 'pit-engine.md')

# (line_index, must_contain) -- engine-domain entries, verified against r-number anchors
ENGINE_LINES = {
    18: 'r576', 19: 'r374', 69: 'r319', 70: 'r321', 74: 'r523', 75: 'r511',
    77: 'r325', 80: 'r529', 82: 'r330', 83: 'r518', 87: 'r534', 88: 'r535',
    90: 'r521', 91: 'r538', 92: 'r335', 93: 'r522', 94: 'r522', 104: 'r530',
    107: 'r558', 110: 'r560', 111: 'r565', 112: 'r566', 113: 'r566', 114: 'r359',
    115: 'r359', 123: 'r578', 125: 'r370', 127: 'r580', 131: 'r581', 132: 'r581',
    133: 'r580', 135: 'r580', 136: 'r581',
}

POINTER_ROW = ('- 域指针·D-20261002-06 引擎域拆件（2026-10-02 r585 bm-a）：引擎域坑律 33 条'
 '（饱和引擎 tick/常驻双实例/点火遥测/孤儿对账+波冻结席位公示/band gate/五面生成器/锚滚动律/带闸回执'
 '+撞车让路表尾锁/确定性撞面/异带让路+finalize 链头消费/重跑双计/--help 护栏+注册面快照顶替族）'
 '已整域 verbatim 迁出→**research/pit-engine.md**（件内字节对账+md5 行·零丢失断言）'
 '——引擎波冻结/席位公示/带闸回执/finalize/引擎 tick 诊断/注册面（N1_BANDS/SEED_REGISTRY）编辑前必读该件；'
 '余域=数据/协议+流水下沉（D-06 全线收口窗 10-07）。')

def to_blob(b: bytes) -> bytes:
    """blob space = LF (r373 law)"""
    return b.replace(b'\r\n', b'\n')

def main():
    if os.path.exists(PIT):
        print('REFUSE: research/pit-engine.md already exists (double-split guard)')
        return 2
    raw = open(CODELY, 'rb').read()
    crlf = raw.count(b'\r\n'); lf_only = raw.count(b'\n') - crlf
    eol = b'\r\n' if crlf > lf_only else b'\n'
    blob = to_blob(raw)
    lines = blob.decode('utf-8').split('\n')
    # trailing '' from final newline is preserved by split/join semantics below
    pre_bytes = len(blob)
    pre_md5 = hashlib.md5(blob).hexdigest()

    # verify each selected line with its anchor
    picked = []
    for idx, anchor in sorted(ENGINE_LINES.items()):
        ln = lines[idx]
        assert anchor in ln, f'anchor {anchor} not found at line {idx}: {ln[:80]}'
        picked.append((idx, ln))
    assert len(picked) == 33, f'expected 33 entries, got {len(picked)}'

    # zero-loss reconstruction check (order-preserving): removing picked lines + pointer == original
    keep = [ln for i, ln in enumerate(lines) if i not in ENGINE_LINES]
    # insert pointer row after the second existing domain pointer row (git + pool)
    gi = next(i for i, ln in enumerate(keep) if ln.startswith('- 域指针·D-20261002-06 池域拆件'))
    keep.insert(gi + 1, POINTER_ROW)

    # byte accounting in blob space
    entry_bytes = sum(len(ln.encode('utf-8')) + 1 for _, ln in picked)  # +1 trailing LF each
    post_blob = '\n'.join(keep).encode('utf-8')
    post_bytes = len(post_blob)
    pointer_bytes = len(POINTER_ROW.encode('utf-8')) + 1
    assert pre_bytes - post_bytes == entry_bytes - pointer_bytes, \
        f'byte mismatch: pre {pre_bytes} post {post_bytes} entries {entry_bytes} pointer {pointer_bytes}'

    # verbatim zero-loss: original line multiset == kept-minus-pointer + picked (ordered union identity)
    orig_seq = [ln for ln in lines if ln != '']
    keep_no_ptr = [ln for ln in keep if ln != '' and ln != POINTER_ROW]
    picked_seq = [ln for _, ln in picked]
    assert sorted(orig_seq) == sorted(keep_no_ptr + picked_seq), 'zero-loss assertion FAILED'

    header = """# pit-engine —— 引擎域坑律正典（D-20261002-06 域分件·第三拆件）

> 来源：CODELY.md 整域 verbatim 迁出（2026-10-02 r585 bm-a·集团裁定 D-20261002-06「坑律按域分件·轮 prompt 按需局部读」）。
> 执法面：饱和引擎（tick/常驻实例/点火/烧录/遥测/孤儿对账）、引擎波冻结（席位公示/band gate/五面生成器/锚滚动律/带闸回执）、撞车与让路（表尾锁/确定性撞面/异带动刀序）、finalize 链（链头 origin 消费/重跑双计/--help 护栏/selftest 缺省波）、注册面（N1_BANDS/SEED_REGISTRY/整文件快照顶替）——上述动作前必读本件。
> 字节对账行（零丢失断言）：CODELY.md 迁出前 {pre}B（md5={pre_md5}）→迁出后 {post}B（md5={post_md5}·净变化=−{moved}B 迁出+{ptr}B 指针行）；移出 33 条·条目字节和（LF blob 空间·含行尾）={moved}B==主件净删减字节·逐字节恒等零丢失；本件由拆件脚本机械迁移非手抄（r335 机证律同源）。
> 已拆域件：pit-git.md（r369·49 条）；pit-pool.md（r373·16 条）；pit-engine.md（r585·本件 33 条）；余域=数据/协议+流水下沉（D-06 全线收口窗 2026-10-07）。
""".format(pre=pre_bytes, pre_md5=pre_md5, post=post_bytes, post_md5=hashlib.md5(post_blob).hexdigest(),
           moved=entry_bytes, ptr=pointer_bytes)

    body = '\n'.join(ln for _, ln in picked)
    pit_blob = (header + '\n' + body + '\n').encode('utf-8')
    # write working-tree EOL (r373): CRLF if repo working tree convention
    pit_out = pit_blob.replace(b'\n', eol)
    codely_out = post_blob.replace(b'\n', eol)
    open(PIT, 'wb').write(pit_out)
    open(CODELY, 'wb').write(codely_out)
    print(f'SPLIT OK: 33 entries, {entry_bytes}B moved (blob LF space)')
    print(f'CODELY: {pre_bytes} -> {post_bytes} (md5 {pre_md5[:8]} -> {hashlib.md5(post_blob).hexdigest()[:8]})')
    print(f'pit-engine.md: {len(pit_blob)}B blob / {len(pit_out)}B on-disk ({eol!r} EOL)')
    return 0

if __name__ == '__main__':
    sys.exit(main())
