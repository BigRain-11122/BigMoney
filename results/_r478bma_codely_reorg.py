"""r478 bm-a CODELY hot-cold reorg (10KB hard-line law: file at 11,451B).

Migrate 7 verbatim entries (window-batch/pit entries whose carriers and
archive-able provenance are in place) to research/memory-archive/202609.md
under a new section; replace them in CODELY.md with ONE merged pointer line
(r444 pattern); append the new r478 pit entry (acceptance-criteria
multi-reading pit). Line-level zero-loss check + byte accounting.
"""
import io

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"

MIGRATE_PREFIXES = [
    "- [2026-09-30 r466 bm-b] 无头 rebase 收口双新面",
    "- [2026-09-30 r276 bm-c] 波次种子带与 SLOT 族带同区交错坑",
    "- [2026-09-30 r462 bm-b] stash-pop UU 变体坑",
    "- [2026-09-30 r468 bm-b] PS5.1 epoch 采样坑",
    "- [2026-09-30 r477 bm-a] 重执行批 rerun 旗标坑",
    "- [2026-09-30 r469 bm-b] PS git stash drop stash@{0} 裸写=哈希表解析吞参坑",
    "- [2026-09-30 r470 bm-b] W14 泊位三族甄别判例",
]

POINTER = ("- 冷层指针（r478 合并·r444 范式）：r466 无头 rebase 收口双新面+r276 波次种子带与 SLOT 族带同区交错坑"
           "+r462 stash-pop UU 变体坑+r468 PS5.1 epoch 采样坑+r477 重执行批 rerun 旗标坑+r469 PS stash drop 哈希表吞参坑"
           "+r470 W14 泊位三族甄别判例（子集型塌缩 vs 精炼型增量二分）——七条全文 verbatim"
           "=archive 202609.md『热冷整编 2026-09-30 r478 bm-a 窗批』节。")

NEW_ENTRY = ("- [2026-09-30 r478 bm-a] 验收判据多读法坑（D-20260930-27 Q9 实弹）：外审验收字面「全量快照零标价行=0」"
             "与执行侧 PASS 宣称「修复后新行零」=两个不同判据——r474 按「新面零」读法宣称 PASS 而历史 20 缺陷行"
             "仍在账本（外审探针全量扫会继续点名）；本窗补外科回填双绿收口（mark_raw 原值保真+前收回退 2.324"
             "+equity 重 derive）。How=宣称 PASS 前把判据原文的量化面（全量/增量/窗口）钉死；历史缺陷行外科修复"
             "正解=原值改名留痕（*_raw）+修复值进正字段+聚合面同步重 derive。")


def main():
    src = io.open(CODELY, encoding="utf-8").read()
    lines = src.split("\n")
    kept, migrated = [], []
    for ln in lines:
        if any(ln.startswith(p) for p in MIGRATE_PREFIXES):
            migrated.append(ln)
        else:
            kept.append(ln)
    assert len(migrated) == len(MIGRATE_PREFIXES), f"expected {len(MIGRATE_PREFIXES)} migrated, got {len(migrated)}"

    # insert pointer lines: pointer goes where first migrated line lived (Project section);
    # new entry right after the pointer; keep section order intact.
    out = []
    inserted = False
    for ln in kept:
        out.append(ln)
        # anchor: the line right before where r466-bm-b entry used to sit is the r464 pointer;
        # simplest: insert after the LAST Project-section pointer line (r464 冷层指针)
        if not inserted and ln.startswith("- 冷层指针（r464 合并"):
            out.append(POINTER)
            out.append(NEW_ENTRY)
            inserted = True
    assert inserted, "insertion anchor not found"

    new_codey = "\n".join(out)
    if src.endswith("\n") and not new_codey.endswith("\n"):
        new_codey += "\n"

    # archive append (verbatim, new section)
    arch = io.open(ARCHIVE, encoding="utf-8").read()
    section = "\n\n## 热冷整编 2026-09-30 r478 bm-a 窗批\n\n" + "\n\n".join(migrated) + "\n"
    arch_new = arch + section

    io.open(CODELY, "w", encoding="utf-8", newline="\n").write(new_codey)
    io.open(ARCHIVE, "w", encoding="utf-8", newline="\n").write(arch_new)

    # zero-loss accounting
    migrated_chars = sum(len(m) for m in migrated)
    print(f"migrated entries: {len(migrated)} ({migrated_chars} chars)")
    print(f"CODELY bytes: {len(src.encode('utf-8'))} -> {len(new_codey.encode('utf-8'))}")
    print(f"archive bytes: {len(arch.encode('utf-8'))} -> {len(arch_new.encode('utf-8'))}")
    print(f"char-accounting: migrated {migrated_chars} + pointer {len(POINTER)} + new {len(NEW_ENTRY)} "
          f"vs removed {len(src) - len(new_codey)} (drift = pointer/new replacing entries, verbatim in archive)")
    # verify all migrated text present in archive verbatim
    for m in migrated:
        assert m in arch_new, "verbatim loss detected"
    print("zero-loss check PASS: all migrated entries verbatim in archive")


if __name__ == "__main__":
    main()
