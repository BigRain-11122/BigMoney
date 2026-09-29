# -*- coding: utf-8 -*-
"""r245 bm-c hot-cold archival -- waterline trim (r449 dedupe-first law applied).
CODELY.md = 10,932B (LF-accounted) > <=10,240B hard line (r244-declared P0).
Dedupe scan catch: User-section meta-law (CEO 实战出真知) IS verbatim-in-archive but
carries deliberate hot-restore annotation (R156: User 节元律不随批归档) -> EXCLUDED from
mechanical drop; true dedupe = 0. Age-migrate 2 cold candidates whose law faces are
tool/codified-carried: r449 storm-union resurrection law (mechanism = _r449bma_codely_dedupe.py
standing tool, applied by this very reorg) + r440 batch-collision three-check law
(procedural S3 checklist, no new-batch drafting face this window; W4 already frozen).
Pit-laws needed by this round's W4 runner build (r236 GBK / r445 seed-base / r450
fail-closed guard) stay hot. Byte-accounted, fail-closed, line-level zero-loss."""
import sys, io

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"
HARD = 10240

MIGRATE_PREFIXES = [
    "- [2026-09-29 18:2x r440 bm-a] 撞批三查律",
    "- [2026-09-29 23:5x r449 bm-a] 风暴 union 合并复活已归档热层条目坑",
]

POINTER = (
    "- 冷层指针：r440 撞批三查律+r449 风暴 union 复活去重律全文 verbatim="
    "archive 202609.md『热冷整编 2026-09-30 r245 bm-c 窗批』节。"
)

ARCH_HEADER = (
    "## 热冷整编 2026-09-30 r245 bm-c 窗批（水位整编·行级零丢失·dedupe 先行扫描=0 真重复"
    "〔User 节实战出真知条虽 verbatim 在档但自带 R156 热恢复注记+User 节元律不随批归档=有意热留"
    "禁机械删〕·冷迁 2 条=机制已工具/清单承载）"
)


def main() -> int:
    src = open(CODELY, encoding="utf-8").read()
    arc = open(ARCHIVE, encoding="utf-8").read()
    src_b0, arc_b0 = len(src.encode("utf-8")), len(arc.encode("utf-8"))
    lines = src.splitlines()

    # dedupe-first: entries verbatim-in-archive, excluding deliberate hot-restores
    HOT_KEEP_DESPITE_ARCHIVE = [
        "- [2026-09-24 16:07:32] CEO 最高判据宣言",  # User-section meta-law, R156 hot-restore
    ]
    dedup = [ln for ln in lines
             if (ln.startswith("- [") or ln.startswith("### [2026"))
             and ln in arc
             and not any(ln.startswith(p) for p in HOT_KEEP_DESPITE_ARCHIVE)]
    assert not dedup, f"unexpected archive-duplicates: {dedup}"
    print("dedupe scan: 0 true duplicates (1 deliberate hot-restore excluded)")

    out, migrated = [], []
    for ln in lines:
        if any(ln.startswith(p) for p in MIGRATE_PREFIXES):
            migrated.append(ln)
            continue
        out.append(ln)
    assert len(migrated) == len(MIGRATE_PREFIXES), f"migrate miss: {len(migrated)}"

    # pointer line replaces migrated entries, anchored after the standing 坑律正典 header block
    ptr_anchors = [i for i, ln in enumerate(out)
                   if ln.startswith("- 冷层指针：r433 同门换用法反向证伪律")]
    assert ptr_anchors, "anchor pointer line not found"
    out.insert(ptr_anchors[0] + 1, POINTER)

    while out and out[-1].strip() == "":
        out.pop()
    src_new = "\n".join(out) + "\n"
    src_b1 = len(src_new.encode("utf-8"))

    arc_new = (arc.rstrip("\n") + "\n\n" + ARCH_HEADER + "\n\n"
               + "\n".join(migrated) + "\n")
    for ln in migrated:
        assert ln in arc_new

    print(f"age-migrated {len(migrated)} entries:")
    for ln in migrated:
        print("   -", ln[:78])
    print(f"CODELY: {src_b0} -> {src_b1} B (hard line {HARD})")
    assert src_b1 < HARD, f"still over hard line: {src_b1}"

    open(CODELY, "w", encoding="utf-8", newline="").write(src_new)
    open(ARCHIVE, "w", encoding="utf-8", newline="").write(arc_new)

    chk, achk = open(CODELY, encoding="utf-8").read(), open(ARCHIVE, encoding="utf-8").read()
    for ln in migrated:
        assert ln not in chk, "dropped line still hot"
        assert ln in achk, "dropped line not verbatim in archive"
    # line-level zero-loss: every non-migrated original line survives verbatim
    kept = [ln for ln in lines if ln not in migrated]
    for ln in kept:
        assert ln in chk, f"kept line lost: {ln[:60]}"
    assert POINTER in chk
    assert len(chk.encode("utf-8")) == src_b1
    # User meta-law still hot
    assert any(ln.startswith(HOT_KEEP_DESPITE_ARCHIVE[0]) for ln in chk.splitlines())
    print(f"zero-loss verify PASS; ARCHIVE {arc_b0} -> {len(achk.encode('utf-8'))} B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
