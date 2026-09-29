# -*- coding: utf-8 -*-
"""r452 bm-a hot-cold archival -- dedupe-against-archive first (r449 law), then
oldest-first age migration until <=10,240B hard line. Byte-accounted, fail-closed.
Adds the r452 pit entry (criterion-field semantic drift vs wiring window).
Mechanism verbatim-reused from results/_r447bma_codely_hotcold.py + _r449bma_codely_dedupe.py."""
import sys, io

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"
HARD = 10240

NEW_ENTRY = (
    "- [2026-09-30 01:5x r452 bm-a] 判据字段语义漂移=接线窗未走预声明配套预注册坑（science_audit C6 第二场实弹·六误报定谳）："
    "§9(c) 09-24 冻结读 paper 块 mode 字串=生效模式；T-21 v3 接线窗把 mode 改为请求信道记录（env enforce=S6 链明文动作）"
    "+active/enforced 三计数器承载生效面——判据与接线语义错配，且 §9 末行预声明的「enforce 接线落地时=新预注册追加判据」"
    "在接线窗从未执行，月度审计第二场才浮出 6 误报（state 件 mode 恒 shadow→10-01 起将月月复现）。"
    "正法=消费侧走 §8 变更协议修订（research/SCIENCE_AUDIT_S9C_AMEND_PREREG.md·GM 署名·否决窗至 10-07·"
    "判据改读 active+计数器实际干预面+补 §9 预声明响应腿=不弱反强），禁改生产侧 mode 记录（请求信道透明面更全）。"
    "How to apply：任何 wiring 落地改变既有冻结判据所读字段的语义时，接线窗同轮必查判据件预声明配套节并同步追加预注册，"
    "防月度审计窗才浮出的误报风暴。"
)

# oldest-first migration candidates (exact prefixes; asserted single-occurrence)
MIGRATE_PREFIXES = [
    "- [2026-09-29 18:2x r440 bm-a] 撞批三查律",
    "- [2026-09-29 20:0x r236 bm-c] GBK 控制台吞链 runner 坑",
    "- [2026-09-29 20:2x r444 bm-a] fork-point 过时基点重放坑",
]

ARCHIVE_SECTION_HEADER = "## 热冷整编 2026-09-30 r452 bm-a 窗批（超线 10,959B 当窗即办·dedupe 先行律）"
POINTER_LINE = (
    "- 冷层指针：r440 撞批三查律+r236 GBK 控制台吞链+r444 fork-point 过时基点重放三律全文 verbatim="
    "archive 202609.md『热冷整编 2026-09-30 r452 bm-a 窗批』节（操作面活跃度=S3 选批三查/runner 入口 reconfigure 惯例/"
    "rebase 风暴窗三步——法面由 iteration_prompt S3+r444 步骤文承载，热层指针在位即可发现）。"
)


def main() -> int:
    src = open(CODELY, encoding="utf-8").read()
    arc = open(ARCHIVE, encoding="utf-8").read()
    src_b0, arc_b0 = len(src.encode("utf-8")), len(arc.encode("utf-8"))
    print(f"CODELY in: {src_b0}B (hard line {HARD})")

    lines = src.splitlines()

    # --- r449 law step 1: dedupe scan -- any hot entry verbatim already in archive?
    dupes = [ln for ln in lines if ln.startswith("- [2026-") and ln in arc]
    print(f"dedupe scan: {len(dupes)} hot entries verbatim-in-archive")
    for ln in dupes:
        print("  DUPE:", ln[:60])

    # --- locate migration entries (exact single occurrence each)
    found = {}
    for i, ln in enumerate(lines):
        for p in MIGRATE_PREFIXES:
            if ln.startswith(p):
                assert p not in found, f"duplicate entry for {p[:30]}"
                found[p] = (i, ln)
    missing = [p for p in MIGRATE_PREFIXES if p not in found]
    assert not missing, f"missing entries: {missing}"

    migrated = [found[p][1] for p in MIGRATE_PREFIXES]

    # --- archive append: header + verbatim lines (zero-loss assert)
    arc_new = arc.rstrip("\n") + "\n\n" + ARCHIVE_SECTION_HEADER + "\n\n" \
        + "\n".join(migrated) + "\n"
    for ln in migrated:
        assert ln in arc_new, "archived line not verbatim in archive"

    # --- rebuild CODELY: drop migrated, insert pointer at Reference anchor, append new entry
    out, ref_ptr_inserted = [], False
    for ln in lines:
        if any(ln is found[p][1] for p in MIGRATE_PREFIXES):
            continue
        out.append(ln)
        if ln.startswith("- 冷层指针：流水型条目按") and not ref_ptr_inserted:
            out.append(POINTER_LINE)
            ref_ptr_inserted = True
    assert ref_ptr_inserted, "Reference 冷层指针 anchor line not found"
    while out and out[-1].strip() == "":
        out.pop()
    out.append(NEW_ENTRY)
    src_new = "\n".join(out) + "\n"

    migrated_b = sum(len(ln.encode("utf-8")) + 1 for ln in migrated)
    src_b1 = len(src_new.encode("utf-8"))
    arc_b1 = len(arc_new.encode("utf-8"))
    print(f"CODELY: {src_b0} -> {src_b1} B (migrated out {migrated_b}B; pointer+new-entry net "
          f"{src_b1 - (src_b0 - migrated_b):+d}B)")
    print(f"ARCHIVE: {arc_b0} -> {arc_b1} B (delta +{arc_b1 - arc_b0}B)")

    # line-level zero-loss: every dropped hot line exists verbatim in archive
    for ln in migrated:
        assert ln in arc_new
    # hard-line check
    if src_b1 > HARD:
        print(f"FAIL: still over hard line ({src_b1} > {HARD}) -- more migration needed")
        return 2

    open(CODELY, "w", encoding="utf-8", newline="\n").write(src_new)
    open(ARCHIVE, "w", encoding="utf-8", newline="\n").write(arc_new)

    chk = open(CODELY, encoding="utf-8").read()
    chk_arc = open(ARCHIVE, encoding="utf-8").read()
    assert NEW_ENTRY in chk, "new entry missing after write"
    for ln in migrated:
        assert ln in chk_arc, "archive lost a migrated line"
        assert ln not in chk, "migrated line still hot"
    print(f"OK: CODELY now {len(chk.encode('utf-8'))}B <= {HARD}; "
          f"archive {len(chk_arc.encode('utf-8'))}B; zero-loss verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
