# -*- coding: utf-8 -*-
"""_r447bma_codely_hotcold.py -- S4 hot-cold archival (CODELY.md 10,606B over
the <=10KB hard line, O-20260927-0230-bm-a group order: same-window, line-level
zero-loss). Migrates three least-active- face entries verbatim to
research/memory-archive/202609.md, leaves pointer lines, appends the new r447
pit entry. Byte-accounted, fail-closed asserts throughout."""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"
HARD_LINE = 10240

MIGRATE_PREFIXES = [
    "- [2026-09-29 17:2x r229 bm-c] LHB 源改史实录",
    "- [2026-09-29 19:5x r235 bm-c] core48 日线源分层定谳",
    "- [2026-09-29 20:1x r237 bm-c] 波级泊位窗先例",
]

POINTER_LINE = (
    "- 冷层指针：r229 LHB 源改史+r235 core48 源分层+r237 波级泊位窗先例三律全文 verbatim="
    "archive 202609.md『热冷整编 2026-09-29 r447 bm-a 窗批』节（r440 bm-b 批曾热留=操作面活跃·"
    "本批水位 10,606B 复超线当窗即办·r237 先例已由 DECISION_CHAIN §四.7 法面+W12 draft 头部双载）。"
)

NEW_ENTRY = (
    "- [2026-09-29 22:2x r447 bm-a] dict-of-Series 构帧对齐全 NaN 坑（W12 RSQR 探针实弹·"
    "零静默损=fail-closed 断言拦截）：pd.DataFrame({列: Series…}, index=新 RangeIndex) 构造时 "
    "dict 值为带索引 Series→pandas 按 Series 自有索引对齐到给定 index=全 NaN 静默重索引（不报错）；"
    "date-indexed 面板列（load_core 族）喂 RangeIndex 帧的逐 bar 因子机（alpha158_factors 类）即全 NaN 下游。"
    "正法=构帧前 .to_numpy() 剥索引（或统一日期索引）。How to apply：凡从 date-indexed 面板列构造 "
    "RangeIndex 帧喂因子库必先 to_numpy；探针/runner 见全 NaN 面第一嫌疑=构帧对齐非数据腐坏"
    "（本例 core48 腿 0/48 成员即此坑·锚面 CSV 列路径无 Series 索引不受影响）。"
    "指针=results/_r447bma_rsqr_w12_probe.py 修点+facts core48_rsqr20_open_rate 48/48。"
)

ARCHIVE_SECTION_HEADER = (
    "## 热冷整编 2026-09-29 r447 bm-a 窗批（CODELY.md 10,606B 超 ≤10KB 硬线当窗即办·行级零丢失迁移"
    "·三律迁档——r229/r235 曾热留两批后本批让位水位律·r237 先例已由法面+W12 draft 双载）"
)

KEEP_HOT_NOTE = (
    "判定留热面：r442 双坑律（W12 runner 构建 nan-safe+ledger 键面即用）+r236 GBK reconfigure"
    "（W12 runner 入口律）+r445 dual-nulls rebind+r441 撞带活复验（W12 冻结面即用）+r446 账本对账"
    "+r440 撞批三查律+r444 fork-point+r240 tick 接续律热留（当前操作面活跃）。"
    "校验=被删行文本逐字在本档在位（脚本 assert）·水位回线。"
)


def main() -> int:
    src = open(CODELY, encoding="utf-8").read()
    arc = open(ARCHIVE, encoding="utf-8").read()
    src_b0, arc_b0 = len(src.encode("utf-8")), len(arc.encode("utf-8"))

    lines = src.splitlines()
    # locate the three migration entries (exact single occurrence each)
    found = {}
    for i, ln in enumerate(lines):
        for p in MIGRATE_PREFIXES:
            if ln.startswith(p):
                assert p not in found, f"duplicate entry for {p[:30]}"
                found[p] = (i, ln)
    missing = [p for p in MIGRATE_PREFIXES if p not in found]
    assert not missing, f"missing entries: {missing}"

    migrated = [found[p][1] for p in MIGRATE_PREFIXES]

    # append archive section: header + verbatim lines + keep-hot note
    arc_new = arc.rstrip("\n") + "\n\n" + ARCHIVE_SECTION_HEADER + "\n\n" \
        + "\n".join(migrated) + "\n\n" + KEEP_HOT_NOTE + "\n"
    # zero-loss assert: each migrated line byte-identical in the new archive
    for ln in migrated:
        assert ln in arc_new, "archived line not verbatim in archive"

    # rebuild CODELY: drop migrated lines, insert pointer after the Reference
    # section's existing 冷层指针 line, append new pit entry at file end
    out = []
    ref_ptr_inserted = False
    for ln in lines:
        if any(ln is found[p][1] for p in MIGRATE_PREFIXES):
            continue
        out.append(ln)
        if ln.startswith("- 冷层指针：流水型条目按") and not ref_ptr_inserted:
            out.append(POINTER_LINE)
            ref_ptr_inserted = True
    assert ref_ptr_inserted, "Reference 冷层指针 anchor line not found"
    # remove trailing blank normalization then append new entry
    while out and out[-1].strip() == "":
        out.pop()
    out.append(NEW_ENTRY)
    src_new = "\n".join(out) + "\n"

    # byte accounting + hard-line check
    migrated_b = sum(len(ln.encode("utf-8")) + 1 for ln in migrated)
    src_b1 = len(src_new.encode("utf-8"))
    arc_b1 = len(arc_new.encode("utf-8"))
    print(f"CODELY: {src_b0} -> {src_b1} B (migrated out {migrated_b}B, "
          f"pointer+new-entry in {src_b1 - (src_b0 - migrated_b)}B)")
    print(f"ARCHIVE: {arc_b0} -> {arc_b1} B (delta +{arc_b1 - arc_b0}B, "
          f"header+notes {arc_b1 - arc_b0 - migrated_b}B)")
    assert src_b1 < HARD_LINE, f"CODELY {src_b1}B still over hard line {HARD_LINE}"

    open(CODELY, "w", encoding="utf-8", newline="").write(src_new)
    open(ARCHIVE, "w", encoding="utf-8", newline="").write(arc_new)

    # post-write verification: re-read, assert migrated lines absent from
    # CODELY and present verbatim in archive; new entry present
    src_chk = open(CODELY, encoding="utf-8").read()
    arc_chk = open(ARCHIVE, encoding="utf-8").read()
    for ln in migrated:
        assert ln not in src_chk, "migrated line still in CODELY"
        assert ln in arc_chk, "migrated line not in archive after write"
    assert NEW_ENTRY in src_chk and POINTER_LINE in src_chk
    assert len(src_chk.encode("utf-8")) == src_b1
    print("zero-loss verification PASS; hard line", HARD_LINE, "OK;",
          "final", len(src_chk.encode("utf-8")), "B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
