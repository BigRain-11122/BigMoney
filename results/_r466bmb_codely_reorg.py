# r466 bm-b CODELY.md hot-cold reorg v2: archive r461 + r473 x2 verbatim, pointers in place, <=10000B hard line
import io

p_codely = "CODELY.md"
p_archive = "research/memory-archive/202609.md"
src = io.open(p_codely, "r", encoding="utf-8").read()

MOVES = [
    ("- [2026-09-30 r461 bm-b] rebase",
     "- 冷层指针（r466 合并·r444 范式）：r461 rebase 重放撞车双向坑（方向禁按 rebase 常识·逐件 ts 探针定方向·union=行数回归唯一恢复面·lane_io 守卫旧 commit 照写归分类器）全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r466 bm-b 窗批』节。"),
    ("- [2026-09-30 r473 bm-a] 盘中标记零价静默蒸发坑",
     "- 冷层指针（r466 合并·r444 范式）：r473 bm-a 盘中标记零价静默蒸发坑（价 0 双义+「行在」≠「价真」两判据合一·P0；How=mark/估值路径过「价真=值>0」回退链+断言禁写盘·selftest S7-S9 承载）全文 verbatim=archive 同节。"),
    ("- [2026-09-30 r473 bm-a] 断头 rebase 诊断序",
     "- 冷层指针（r466 合并·r444 范式）：r473 bm-a 断头 rebase 诊断序（脏树+pull 拒先 git reflog 分辨真脏树 vs 中断重放态伪装脏树·正序=重放态当 commit 消费收口→再 pull --rebase）全文 verbatim=archive 同节。"),
]
R466_ENTRY = ("- [2026-09-30 r466 bm-b] 无头 rebase 收口双新面（D-20260925-01 侧支律配套·_r466bmb_resolve.py 承载）："
"①rebase --continue 撞「Terminal is dumb, but EDITOR unset」=无头会话无编辑器，正解=git -c core.editor=true rebase --continue"
"（惰性编辑器吞开屏复用原 commit message，勿手敲 -m 重打）；②UU 探针 raw 正则带捕获组时 findall 只回组内容不回全匹配"
"（md/js 面探针打印 ':55' 伪 ts 定不了向）——raw 探针一律 finditer+group(0)，md/js 方向裁决让孪生 json 探针代言（r98 孪生同侧律）；"
"③push 两拒（重试额度尽）后按 D-20260925-01③ 推 origin machine/<id>-r<N> 侧支收轮，下轮 S0 pull --rebase 自然合并"
"（本地 main 已含侧支 lineage），落地后侧支冗余可删。")

lines = src.split("\n")
moved = []
for i, l in enumerate(lines):
    for mark, ptr in MOVES:
        if l.startswith(mark):
            assert l not in moved
            moved.append(l)
            lines[i] = ptr
            break
assert len(moved) == 3, f"expected 3 moves, got {len(moved)}"

ref_idx = lines.index("### Reference")
lines.insert(ref_idx, R466_ENTRY)
lines.insert(ref_idx + 1, "")
new_src = "\n".join(lines)

arch = io.open(p_archive, "r", encoding="utf-8").read()
SECTION = "## 热冷整编 2026-09-30 r466 bm-b 窗批"
if SECTION not in arch:
    arch = arch.rstrip("\n") + "\n\n" + SECTION + "\n\n" + "\n\n".join(moved) + "\n"
else:
    # idempotent: append only entries not yet present in the section
    for e in moved:
        if e not in arch:
            arch = arch.rstrip("\n") + "\n" + e + "\n"
io.open(p_archive, "w", encoding="utf-8", newline="\n").write(arch)

arch2 = io.open(p_archive, "r", encoding="utf-8").read()
for e in moved:
    assert e in arch2, f"ZERO-LOSS FAIL: not verbatim in archive: {e[:60]}"
    assert e not in new_src, f"full entry still in CODELY.md: {e[:60]}"
assert R466_ENTRY in new_src
nb = len(new_src.encode("utf-8"))
print(f"CODELY.md {len(src.encode('utf-8'))}B -> {nb}B (hard line 10000B)")
assert nb <= 10000, f"still over hard line: {nb}"
io.open(p_codely, "w", encoding="utf-8", newline="\n").write(new_src)
print("reorg v2 OK: 3 entries verbatim->archive zero-loss PASS, r466 appended, 3 pointers in place")
