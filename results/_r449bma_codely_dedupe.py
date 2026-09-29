# -*- coding: utf-8 -*-
"""r449 bm-a hot-cold archival -- storm-union resurrection dedupe + waterline trim.
Post-storm CODELY.md = 13,828B (storm union re-inflated hot layer with entries already
verbatim-archived by r447/r448 windows on the lagging sibling copy face).
Law: dedupe-against-archive FIRST (in-archive == true zero-loss to drop), then age-migrate
cold entries only if still over the <=10,240B hard line. Byte-accounted, fail-closed."""
import sys, io

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"
HARD = 10240

NEW_ENTRY = (
    "- [2026-09-29 23:5x r449 bm-a] 风暴 union 合并复活已归档热层条目坑（CODELY 热冷整编×冲突解交互实弹）："
    "memory-union 冲突解的零丢失偏置（origin 侧骨架+双侧条目全保）在对岸滞后面（bm-b 未吸收本机 r447/r448 "
    "整编批的 CODELY 面）上重放时，把已在 archive 的 r229/r235/r237/r441 全文条目整段复活回热层=13.8KB 复超线；"
    "正法=风暴后整编不按年龄选条目，先逐条对照 archive 件查 verbatim 重复（在档即删热层=真零丢失·指针行已在位），"
    "再按水位补迁冷条目。How to apply：凡 memory-union 解冲突后同窗整编，第一步=archive 去重扫描而非「迁最旧」。"
    "指针=results/_r449bma_codely_dedupe.py（r447 hotcold 机制复用+dedupe 前置步）。"
)

# age-migration candidates (only touched if dedupe alone leaves us over the line),
# coldest first; each carries an existing archive-side pointer already or gets one here.
AGE_MIGRATE_PREFIXES = [
    "- [2026-09-29 19:3x r442 bm-a] A10 判据线 NaN 静默退化坑",
    "- [2026-09-29 21:5x r446 bm-a] 声明件-落盘件分离丢账坑",
]

POINTER_AGE = (
    "- 冷层指针：r442 A10 NaN 双坑律（法面已由 attrition 72 行/guard 脚本+preref §7/8 承载）+r446 "
    "账本对账律（已机械化=scripts/attrition_ledger_guard.py r448 遗产 r449 落地）全文 verbatim="
    "archive 202609.md『热冷整编 2026-09-29 r449 bm-a 窗批』节。"
)

ARCH_HEADER = (
    "## 热冷整编 2026-09-29 r449 bm-a 窗批（风暴 union 复活条目去重+水位整编·行级零丢失·"
    "dedupe=archive verbatim 在档即删·r447/r448 指针行沿用）"
)


def is_entry(ln):
    return ln.startswith("- [") or ln.startswith("### [2026")


def main() -> int:
    src = open(CODELY, encoding="utf-8").read()
    arc = open(ARCHIVE, encoding="utf-8").read()
    src_b0, arc_b0 = len(src.encode("utf-8")), len(arc.encode("utf-8"))
    lines = src.splitlines()

    dedup, keep = [], []
    for ln in lines:
        if is_entry(ln) and ln in arc:
            dedup.append(ln)
        else:
            keep.append(ln)
    for ln in dedup:
        assert ln in arc, "dedupe candidate not actually in archive"

    out = list(keep)
    migrated = []
    size = sum(len(ln.encode("utf-8")) + 1 for ln in out)
    if size + len(NEW_ENTRY.encode("utf-8")) + 1 > HARD:
        found = {}
        for i, ln in enumerate(out):
            for p in AGE_MIGRATE_PREFIXES:
                if ln.startswith(p):
                    assert p not in found
                    found[p] = ln
        missing = [p for p in AGE_MIGRATE_PREFIXES if p not in found]
        assert not missing, f"age-migrate entries missing: {missing}"
        migrated = [found[p] for p in AGE_MIGRATE_PREFIXES]
        out2, ptr_in = [], False
        for ln in out:
            if any(ln is m for m in migrated):
                continue
            out2.append(ln)
            if ln.startswith("- 冷层指针：r441 泊位种子撞带") and not ptr_in:
                out2.append(POINTER_AGE)
                ptr_in = True
        assert ptr_in, "r448 r441-pointer anchor line not found for age-pointer insert"
        out = out2
        # archive gets the migrated entries verbatim
        arc_new = arc.rstrip("\n") + "\n\n" + ARCH_HEADER + "\n\n" + "\n".join(migrated) + "\n"
        for ln in migrated:
            assert ln in arc_new
    else:
        arc_new = None

    while out and out[-1].strip() == "":
        out.pop()
    out.append(NEW_ENTRY)
    src_new = "\n".join(out) + "\n"
    src_b1 = len(src_new.encode("utf-8"))
    arc_b1 = len(arc_new.encode("utf-8")) if arc_new else arc_b0

    print(f"dedupe dropped {len(dedup)} archive-duplicate entries:")
    for ln in dedup:
        print("   -", ln[:78])
    if migrated:
        print(f"age-migrated {len(migrated)} entries:")
        for ln in migrated:
            print("   -", ln[:78])
    print(f"CODELY: {src_b0} -> {src_b1} B (hard line {HARD})")
    assert src_b1 < HARD, f"still over hard line: {src_b1}"

    open(CODELY, "w", encoding="utf-8", newline="").write(src_new)
    if arc_new:
        open(ARCHIVE, "w", encoding="utf-8", newline="").write(arc_new)

    chk, achk = open(CODELY, encoding="utf-8").read(), open(ARCHIVE, encoding="utf-8").read()
    for ln in dedup + migrated:
        assert ln not in chk, "dropped line still hot"
        assert ln in achk, "dropped line not verbatim in archive"
    assert NEW_ENTRY in chk
    assert len(chk.encode("utf-8")) == src_b1
    print(f"zero-loss verify PASS; ARCHIVE {arc_b0} -> {arc_b1} B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
