# -*- coding: utf-8 -*-
"""r385 bm-b S4: append new lesson (worker-tree liveness probe) to CODELY.md,
then waterline law: append pushes file over the <=10KB hard line ->
same-window hot-cold reorg batch 50: move r381 + r162 verbatim entries to
research/memory-archive/202609.md (verbatim, line-level zero-loss verified),
leave single pointer line. Byte style: pure LF, no BOM, trailing newline
(probed pre-write per r381 byte-style law)."""
import io
import sys

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"
HARD = 10240

NEW_ENTRY = (
    "- [2026-09-28 13:2 r385 bm-b] 坑律：**multiprocessing runner 活度定谳必探 "
    "worker 树——父进程 CPU 0-delta+小 WS=协调态常态非停滞**（r385 实弹：census "
    "W2B 终段 checkpoint 20min 未刷+父 pid 28820 单探针判 cpu-idle-suspect，树探="
    "3/4 spawn worker ~100% CPU 活烧+1 worker 分片排空=尾相常态；单看父 pid 差点"
    "误诊停滞违 no-kill 律）。判序=Win32_Process 按 ParentProcessId 枚举子 "
    "worker，20s 双采样 cpu delta，任一 worker 增量>0.5s=活烧零动作。How to "
    "apply：census/MASS/judge 族任何 spawn 池 runner 停滞嫌疑先树探后定谳；"
    "父 idle+checkpoint 停刷双陈旧面与 r382 陈旧崩迹同判序族。指针=results/"
    "_r385bmb_census_probe.py + _r385bmb_census_tree.py。"
)

MOVE_PREFIXES = [
    "- [2026-09-28 12:4 r381 bm-b] 坑律：",
    "- [2026-09-28 12:4 r162 bm-c] 坑律：",
]

POINTER = (
    "冷层指针：坑律正典 2026-09-28 五十批（r385 bm-b 窗·水位律当窗整编：r385 "
    "新坑律 append 后超 ≤10KB 硬线）：r381 池文件字节风格 / r162 开波四件套裁定"
    "链双门 两条全文 verbatim=archive 202609.md『坑律归档 2026-09-28 五十批』节"
    "（行级零丢失校验）。"
)

SECTION_HEADER = (
    "坑律归档 2026-09-28 五十批（r385 bm-b 窗·水位律当窗整编：r385 新坑律 "
    "append 后超 ≤10KB 硬线）："
)


def main():
    c = io.open(CODELY, encoding="utf-8").read()
    assert c.endswith("\n") and "\r\n" not in c, "CODELY byte style drifted"
    assert NEW_ENTRY.split("]")[0] not in c, "r385 entry already present"
    lines = c.split("\n")
    # append new entry after the r383 entry (last verbatim entry line)
    idx = max(i for i, l in enumerate(lines) if l.startswith("- [2026-09-28"))
    lines.insert(idx + 1, NEW_ENTRY)
    c2 = "\n".join(lines)
    size_after_append = len(c2.encode("utf-8"))
    print(f"after append: {size_after_append}B "
          f"({'OVER' if size_after_append > HARD else 'under'} {HARD} hard line)")
    if size_after_append <= HARD:
        io.open(CODELY, "w", encoding="utf-8", newline="\n").write(c2)
        print("no reorg needed")
        return 0
    # --- reorg batch 50 ---
    lines = c2.split("\n")
    moved = []
    for pref in MOVE_PREFIXES:
        hits = [i for i, l in enumerate(lines) if l.startswith(pref)]
        assert len(hits) == 1, f"prefix not unique/found: {pref} -> {hits}"
        moved.append(lines[hits[0]])
    # archive append: blank + section header + blank + entries verbatim
    a = io.open(ARCHIVE, encoding="utf-8").read()
    assert a.endswith("\n") and "\r\n" not in a, "archive byte style drifted"
    block = ("\n" if not a.endswith("\n\n") else "") + SECTION_HEADER + "\n\n" \
        + "\n".join(moved) + "\n"
    io.open(ARCHIVE, "w", encoding="utf-8", newline="\n").write(a + block)
    # CODELY: drop moved entries, insert pointer after the 49th-batch pointer
    lines = [l for l in lines if l not in moved]
    p49 = max(i for i, l in enumerate(lines) if "四十九批" in l)
    lines.insert(p49 + 1, POINTER)
    c3 = "\n".join(lines)
    assert c3.endswith("\n")
    io.open(CODELY, "w", encoding="utf-8", newline="\n").write(c3)
    # --- verification ---
    a2 = io.open(ARCHIVE, encoding="utf-8").read()
    c4 = io.open(CODELY, encoding="utf-8").read()
    for m in moved:
        assert m in a2, "moved line LOST in archive"
        assert m not in c4, "moved line still in CODELY"
    assert a2.count(SECTION_HEADER) == 1
    assert NEW_ENTRY in c4 and POINTER in c4
    assert "\r\n" not in c4 and c4.endswith("\n")
    assert "\r\n" not in a2 and a2.endswith("\n")
    sz = len(c4.encode("utf-8"))
    print(f"reorg done: moved {len(moved)} entries verbatim; "
          f"CODELY now {sz}B ({'OK' if sz <= HARD else 'STILL OVER'} <= {HARD}); "
          f"archive +{len(block.encode('utf-8'))}B")
    return 0 if sz <= HARD else 1


if __name__ == "__main__":
    sys.exit(main())
