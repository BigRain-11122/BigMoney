# r334 bm-a 18th-batch CODELY hot-cold archival (triggered in-window: 9632B + new r334 pitlaw entry > 10240B hard line)
# Law: O-20260927-0230-bm-a + CODELY ≤10KB 硬线 -- append 后超线=当窗即办热冷整编勿等月.
# Moves (verbatim, zero-loss asserted): r331-bma CRLF entry / r330-bmb ctor-arity entry / r86-bmc data-loss entry -> archive 202609.md 十八批节.
# In-tree: pointer lines replace them; duplicate strict-subset 归档 canon block1 removed (block1 ⊂ block2 asserted before removal).
# New entry appended: r334 future-ts probe poisoning pitlaw (the trigger of this batch).
import io, sys

CODELY = 'CODELY.md'
ARCHIVE = 'research/memory-archive/202609.md'

NEW_ENTRY = '- [2026-09-27 16:0x r334 bm-a] 坑律：**resolver 取侧 ts 探针的「全扫 max-timestamp」启发式会被载荷内未来日期字段毒化——dashboard 载荷带 next-fire「2026-09-28 09:15」（T-91 周一点火计划面）压过两侧一切生成 ts，blanket 扫描两翼同 max→假 tie→r140 tie→HEAD 静默取旧侧**。r334 实弹：27-UU 批 dashboard_status.js/.json 对按 maxts 误判 tie 取 origin，而权威探针 meta.generated_at 实况 origin 15:48:33 < mine 15:53:10=mine 后到，_r334bma_resolve_patch.py 当场纠侧（pair-law 同侧保住零杂交）。正典=①已知生产者探针路径优先（r319 存在性先行），blanket max-ts 只作末路；②必用 blanket 时加未来哨卫（ts > now 一律剔除出取侧比较——计划面字段非生成面）；③pair/twin 同侧断言防杂交不防双错侧——双翼同错侧时断言恒过，正判仍靠探针路径。指针=results/_r334bma_resolve.py+results/_r334bma_resolve_patch.py+round_reports r334 addendum+commit r334。'

MOVE_MARKERS = [
    ('r331-bma-CRLF', '- [2026-09-27 15:3x r331 bm-a] 坑律：**rebase 撞车核验自动合并件（非 UU）'),
    ('r330-bmb-ctor', '- [2026-09-27 14:5x r330 bm-b] 坑律：**移植既有因子 ctor 前必探明返回形'),
    ('r86-bmc-dataloss', '- [2026-09-27 15:0x r86 bm-c] 坑律：**根迁移/仓重建后必须同轮盘点机器本地数据面'),
]
POINTER = {
    'r331-bma-CRLF': '- [2026-09-27 15:3x r331 bm-a] 坑律（十八批外迁·指针）：rebase 撞车核验自动合并件归属侧必先 CRLF 规范化（autocrlf 下 LF-blob 件必假报 HYBRID）/定侧正道=两 commit changed-file 交集（UU 必==交集）——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 十八批』节。',
    'r330-bmb-ctor': '- [2026-09-27 14:5x r330 bm-b] 坑律（十八批外迁·指针）：移植既有因子 ctor 前必探明返回形+真实调用形态探针先行（含崩类复现腿，hermetic 合成面测不到）——全文 verbatim=archive 202609.md 十八批节。',
    'r86-bmc-dataloss': '- [2026-09-27 15:0x r86 bm-c] 坑律（十八批外迁·指针）：根迁移/仓重建后必须同轮盘点机器本地数据面（gitignored data/* 车道资产不随 clone 复活=不可逆灭失；status done 块必须可由盘上事实再 derive）——全文 verbatim=archive 202609.md 十八批节。',
}
BLOCK1_PREFIX = '- 坑律正典全量归档（2026-09-27 集团令 O-20260927-0230-bm-a·CODELY ≤10KB 整编）：全部坑律条目已外迁'

def main():
    src = open(CODELY, encoding='utf-8').read()
    lines = src.split('\n')
    out_lines, moved, seen_block1, seen_block2 = [], {}, 0, 0
    for ln in lines:
        if ln.startswith(BLOCK1_PREFIX):
            seen_block1 += 1
            if seen_block1 == 1:
                block1 = ln  # candidate duplicate; keep aside, drop if block2 superset found
                continue
            else:
                seen_block2 += 1
                block2 = ln
                # strict-subset assertion: block1 content inside block2 (zero-loss dedup)
                assert block1.rstrip() in block2, 'block1 NOT subset of block2 -- abort dedup'
                out_lines.append(ln)  # keep the superset
                continue
        matched = False
        for tag, marker in MOVE_MARKERS:
            if ln.startswith(marker):
                moved[tag] = ln
                out_lines.append(POINTER[tag])
                matched = True
                break
        if not matched:
            out_lines.append(ln)
    assert seen_block1 == 2, f'expected 2 canon blocks, found {seen_block1} -- structure drift, abort'
    assert set(moved) == {t for t, _ in MOVE_MARKERS}, f'move set mismatch: {sorted(moved)}'
    # append new entry after the last Reference line (tail of file, before trailing empties)
    while out_lines and out_lines[-1] == '':
        out_lines.pop()
    out_lines.append(NEW_ENTRY)
    out_lines.append('')
    new_src = '\n'.join(out_lines)

    # archive: append 十八批 section with verbatim entries
    arch = open(ARCHIVE, encoding='utf-8').read()
    sec = '\n## 坑律归档 2026-09-27 十八批（r334 bm-a·CODELY ≤10KB 硬线当窗整编·行级零丢失）\n\n'
    entries = [moved[t] for t, _ in MOVE_MARKERS]
    sec += '\n\n'.join(entries) + '\n'
    new_arch = arch + sec

    # zero-loss assertions: every moved entry verbatim-contained in new archive
    for t, e in moved.items():
        assert e in new_arch, f'{t} not verbatim in archive'
    # byte math + hard line
    nb = len(new_src.encode('utf-8')); ab = len(new_arch.encode('utf-8'))
    sb = len(src.encode('utf-8')); ob = len(arch.encode('utf-8'))
    assert nb <= 10240, f'CODELY still over line: {nb}'
    assert ab >= ob, 'archive shrunk'
    # strict utf-8 round-trip
    assert new_src.encode('utf-8').decode('utf-8') == new_src
    assert new_arch.encode('utf-8').decode('utf-8') == new_arch

    open(CODELY, 'w', encoding='utf-8', newline='').write(new_src)
    open(ARCHIVE, 'a', encoding='utf-8', newline='').write(sec)
    print(f'== 18th-batch archival done ==')
    print(f'moved entries: {sorted(moved)}')
    print(f'duplicate canon block deduped (block1 subset of block2, asserted)')
    print(f'CODELY: {sb}B -> {nb}B (hard line 10240B)')
    print(f'archive: {ob}B -> {ab}B (+{ab-ob}B)')

if __name__ == '__main__':
    main()
