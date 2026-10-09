# r812 bm-b cold-pointer merge + D-19 pit direct-write (D-20261002-06 main<=30KB leg)
# Pattern: r444/r779/r800 cold-ptr merge + r747 direct-write precedent.
# prescan rc3 recorded (registry hits on all 3 faces; zero-loss verbatim migration, not a sweep).
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
ARCH = os.path.join(ROOT, "research", "memory-archive", "202610.md")
D19 = os.path.join(ROOT, "research", "pit-protocol-d19.md")
RECEIPT = os.path.join(ROOT, "results", "_r812bmb_coldptr_merge.json")

NEEDLES = [
    "- 域指针·r592 bm-c CODELY 主件回弹续压批 batch-2",
    "- 域指针·r639 bm-c CODELY 主件回弹续压批 batch-3",
    "- 域指针·r644 bm-c D-06 收口残余裁定批",
    "- 域指针·r651 bm-c D-06 mini-split 批",
    "- 域指针·r654 bm-c 增量回扫批",
    "域指针·r666 bm-c（2026-10-07 09:2x）",  # variant-5 bullet-less row (known form, kept as-is)
    "- 域指针·r667 bm-c（2026-10-07 09:5x）",
    "- 域指针·r670 bm-c 增量批",
    "- 域指针·r672 bm-c 增量批",
    "- 域指针·r679 bm-c 增量批",
]

MERGED_LINE = (
    "- 冷层指针（r812 合并·指针合并归档 r444/r779/r800 范式·D-20261002-06 主件 ≤30KB 判据腿）："
    "r592/r639/r644/r651/r654/r666/r667/r670/r672/r679 十条冷层指针行——"
    "原十行全文 verbatim=archive 202610.md『热冷整编 2026-10-10 r812 bm-b 窗批』节"
    "（receipt=results/_r812bmb_coldptr_merge.json）；各所指正文另在 archive 202609.md/202610.md "
    "对应『窗批』节与各 pit-* 域件；坑律本体全部在 pit-* 域件与正典件，指针行仅导航用。"
)

D19_LESSON = (
    "- [2026-10-10 03:3x r812 bm-b] **D-19 水印写侧拼接缺陷坑（r810 幻影族第三面）**："
    "r811「治愈」自身带毒——存储 DEC 水印 a3ea37bd7c856e4b649f52b77212c57a2abe3776 =真 SHA-1 前 8 hex"
    "（a3ea37bd）+r810 幻影（b148d0ad…）承袭 32-hex 尾拼接成串（两尾逐字恒等）；治愈轮只验证了 8-hex 前缀"
    "（「current origin DEC hash a3ea37bd == r809 read2 hash」）未在写入时换全串——python 全串真值"
    "=a3ea37bd70fd5acc83bcf51939874cffd59f1811（r812 字节安全复算），内容零变化实证=末触 00:55<r811 读时 "
    "02:10·origin/main 6a7c4f5 双窗恒等·ORD 水印 e286f842 字节恒等匹配。r812 治愈=全串复算+全串替换+读侧全串恒等断言。"
    "How to apply：水印写一律单源 python 全串直出（print 全 40-hex 原样复制，禁手拼禁两源合成）；治愈验证必须"
    "全串恒等，前缀匹配≠内容未变的判据基础；治愈带毒时整串换入而非换头。"
)


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    main_b = open(MAIN, "rb").read()
    main_before = len(main_b)
    text = main_b.decode("utf-8")
    lines = text.split("\n")
    # locate needle lines (index, content-without-eol)
    found = {}  # needle -> (idx, content)
    for needle in NEEDLES:
        hits = [i for i, l in enumerate(lines) if l.startswith(needle)]
        if len(hits) != 1:
            print("FATAL needle %r hits=%d" % (needle[:24], len(hits)))
            return 2
        found[needle] = hits[0]
    order = sorted(found.items(), key=lambda kv: kv[1])
    blocks = []
    for needle, idx in order:
        content = lines[idx]
        blocks.append((needle, content.encode("utf-8")))
    # archive append (EOL: match archive dominant)
    arch_b = open(ARCH, "rb").read()
    eol = "\r\n" if arch_b.count(b"\r\n") > arch_b.count(b"\n") - arch_b.count(b"\r\n") else "\n"
    arch_text = arch_b.decode("utf-8")
    if not arch_text.endswith(eol):
        arch_text += eol
    section = "## 热冷整编 2026-10-10 r812 bm-b 窗批" + eol + eol
    body = eol.join([blk.decode("utf-8") for _, blk in blocks]) + eol
    arch_text_new = arch_text + section + body
    # verify verbatim-in-target per block
    for needle, blk in blocks:
        if blk.decode("utf-8") not in arch_text_new:
            print("FATAL verbatim miss:", needle[:24])
            return 2
    arch_new = arch_text_new.encode("utf-8")
    # main rebuild: drop needle lines, insert merged line at first removed index
    drop_idx = set(found.values())
    first = min(drop_idx)
    new_lines = []
    for i, l in enumerate(lines):
        if i == first:
            new_lines.append(MERGED_LINE)
        if i in drop_idx:
            continue
        new_lines.append(l)
    main_new = "\n".join(new_lines).encode("utf-8")
    if len(main_new) > 30720:
        print("FATAL main still over cap:", len(main_new))
        return 2
    # D-19 direct-write append
    d19_b = open(D19, "rb").read()
    d19_eol = b"\r\n" if d19_b.count(b"\r\n") > d19_b.count(b"\n") - d19_b.count(b"\r\n") else b"\n"
    if not d19_b.endswith(d19_eol):
        d19_b += d19_eol
    d19_new = d19_b + D19_LESSON.encode("utf-8") + d19_eol
    if D19_LESSON not in d19_new.decode("utf-8"):
        print("FATAL d19 verbatim miss")
        return 2
    if len(d19_new) > 30720:
        print("FATAL d19 over cap:", len(d19_new))
        return 2
    # write all
    open(MAIN, "wb").write(main_new)
    open(ARCH, "wb").write(arch_new)
    open(D19, "wb").write(d19_new)
    receipt = {
        "round": 812, "machine": "bm-b",
        "pattern": "r444/r779/r800 cold-ptr merge + r747 direct-write",
        "prescan": "treasure_guard prescan rc3 recorded (registry hits CODELY.md/archive-202610/pit-protocol-d19; zero-loss verbatim migration, not a sweep/delete)",
        "migrated": [
            {"needle": n[:40], "bytes": len(b), "sha16": sha16(b)}
            for n, b in blocks
        ],
        "merged_line_sha16": sha16(MERGED_LINE.encode("utf-8")),
        "main_bytes_before": main_before,
        "main_bytes_after": len(main_new),
        "archive_bytes_before": len(arch_b),
        "archive_bytes_after": len(arch_new),
        "d19_lesson_bytes": len(D19_LESSON.encode("utf-8")),
        "d19_lesson_sha16": sha16(D19_LESSON.encode("utf-8")),
        "d19_bytes_after": len(d19_new),
        "assertions": {
            "per_block_verbatim_in_target": True,
            "main_le_30720": len(main_new) <= 30720,
            "domain_le_30720": len(d19_new) <= 30720,
            "zero_loss": True,
        },
        "ts": "2026-10-10T03:3x+08:00",
    }
    open(RECEIPT, "w", encoding="utf-8").write(
        json.dumps(receipt, ensure_ascii=False, indent=1) + "\n")
    print("OK main %d->%d archive %d->%d d19 ->%d receipt=%s" % (
        main_before, len(main_new), len(arch_b), len(arch_new),
        len(d19_new), RECEIPT))
    for n, b in blocks:
        print("  row %d B sha16=%s :: %s" % (len(b), sha16(b), n[:36]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
