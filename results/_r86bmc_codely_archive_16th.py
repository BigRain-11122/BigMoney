# -*- coding: utf-8 -*-
"""r86 bm-c: CODELY.md in-window hot-cold archival (16th batch) + r86 pitlaw append.

Trigger: append r86 pitlaw would exceed 10KB hard line (9769B + ~730B
> 10240B) -> per O-20260927-0230-bm-a group order + D-20260925-01(4):
migrate in-window, don't wait for month-end.

Migrate (verbatim, oldest 3 by time, zero loss):
  - r83 bm-c  union-SKILL recipe sync law   (797B)
  - r327 bm-b org_chart/town.html law       (752B)
  - r326 bm-a pandas asi8 unit law          (870B)
Destination: research/memory-archive/202609.md, new section
"## 十六批外迁（r86 bm-c·2026-09-27·水位律当窗整编·行级零丢失）"
(CRLF host style preserved).

Then append new r86 pitlaw entry (LF host style) to CODELY.md and add
a one-line 16th-batch index note. Asserts: migrated bytes present in
archive verbatim; entries gone from CODELY.md; final size < 10240B;
archive/CODELY line-ending + BOM state unchanged.
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
ARCHIVE = os.path.join(ROOT, "research", "memory-archive", "202609.md")

ENTRY_PREFIXES = [
    "- [2026-09-27 13:3x r83 bm-c] 坑律：",
    "- [2026-09-27 13:5x r327 bm-b] 坑律：",
    "- [2026-09-27 13:4x r326 bm-a] 坑律：",
]

NEW_ENTRY = (
    "- [2026-09-27 15:0x r86 bm-c] 坑律：**根迁移/仓重建后必须同轮盘点机器本地数据面"
    "——gitignored data/* 车道资产不随 clone 复活，旧树删除=不可逆灭失**——r86 实弹："
    "bm-c 09-27 统一根重建（旧树 K:\\金钱牛马 已删·machine.json note 载明）后 "
    "data/fund_premium/（T-16 NAV 全史 48/48+dividends+panel 76,025 行 retained 资产）"
    "整面灭失无人察觉；status 镜像 nav 块仍陈声称 done 48/48 而盘上 0 件=镜像-盘面分歧"
    "（幸 gate 子命令读盘=诚实 fail-closed 无静腐）。正典=①根迁移/重建轮=车道 owner "
    "同轮逐面盘点 .gitignore 机器本地 faces（heat|ext_slots|moneyflow|sina_mf|"
    "astock_daily|fund_premium|ths_ggzjl|ah_panel|bond_w3a）盘上存在性；②镜像 status "
    "的 done 块必须可由盘上事实再 derive（disk 块设计对·陈 done 无再 derive=缺口）；"
    "③恢复=网络重拉（backfill checkpoint 面）+纯本地重建（panel builder）优先勿等需求方撞缺。"
    "指针=results/_r86bmc_fund_premium_data_loss.py/.json+backfill-nav PID 12828。"
)

INDEX_NOTE = (
    "- 十六批外迁（r86 bm-c·2026-09-27·水位律当窗整编）：r83 union 配方律/r327bmb "
    "org_chart 面板律/r326bma pandas asi8 律三条目外迁=归档十六批节·行级零丢失。"
)

ARCHIVE_SECTION_HEADER = (
    "## 十六批外迁（r86 bm-c·2026-09-27·水位律当窗整编·行级零丢失）"
)


def main():
    with io.open(CODELY, "r", encoding="utf-8", newline="") as f:
        raw = f.read()
    assert "\r\n" not in raw, "CODELY.md expected LF host style"
    lines = raw.split("\n")

    migrated, kept = [], []
    for ln in lines:
        if any(ln.startswith(p) for p in ENTRY_PREFIXES):
            migrated.append(ln)
        else:
            kept.append(ln)
    assert len(migrated) == 3, f"expected 3 migrated lines, got {len(migrated)}"

    # append new entry + index note
    out_lines = []
    inserted_note = False
    for ln in kept:
        out_lines.append(ln)
        if "后续新批自十六批起编" in ln:
            out_lines.append(INDEX_NOTE)
            inserted_note = True
    assert inserted_note, "anchor line for index note not found"
    # new pitlaw entry at file end (before trailing '' from final \n)
    assert out_lines[-1] == "", "expected trailing newline structure"
    out_lines[-1] = NEW_ENTRY
    out_lines.append("")
    new_codely = "\n".join(out_lines)
    assert new_codely.encode("utf-8")[
        :3] != b"\xef\xbb\xbf", "no BOM expected"
    size = len(new_codely.encode("utf-8"))
    assert size < 10240, f"CODELY.md still over 10KB hard line: {size}B"

    # archive append (CRLF host style)
    with io.open(ARCHIVE, "r", encoding="utf-8", newline="") as f:
        arch_raw = f.read()
    assert "\n" not in arch_raw.replace(
        "\r\n", ""), "archive expected pure CRLF host style"
    assert arch_raw.endswith("\r\n"), "archive must end with newline"
    section = ARCHIVE_SECTION_HEADER + "\r\n" + "\r\n".join(migrated) + "\r\n"
    assert all("\r\n" not in m and "\n" not in m for m in migrated)
    new_arch = arch_raw + section
    # zero-loss check: every migrated line verbatim inside archive
    for m in migrated:
        assert (m + "\r\n") in new_arch, "verbatim migration check failed"

    with io.open(ARCHIVE, "w", encoding="utf-8", newline="") as f:
        f.write(new_arch)
    with io.open(CODELY, "w", encoding="utf-8", newline="") as f:
        f.write(new_codely)

    # post-write verification
    with io.open(CODELY, "rb") as f:
        cb = f.read()
    with io.open(ARCHIVE, "rb") as f:
        ab = f.read()
    checks = {
        "codely_size": len(cb),
        "codely_under_10kb": len(cb) < 10240,
        "codely_no_bom": cb[:3] != b"\xef\xbb\xbf",
        "codely_lf_only": cb.count(b"\r\n") == 0,
        "migrated_gone_from_codely": all(
            (m.encode("utf-8") + b"\n") not in cb for m in migrated),
        "migrated_in_archive_verbatim": all(
            (m.encode("utf-8") + b"\r\n") in ab for m in migrated),
        "new_entry_present": NEW_ENTRY.encode("utf-8") in cb,
        "index_note_present": INDEX_NOTE.encode("utf-8") in cb,
        "archive_no_bom": ab[:3] != b"\xef\xbb\xbf",
        "archive_ends_newline": ab.endswith(b"\r\n"),
    }
    ok = all(checks.values())
    for k, v in checks.items():
        print(f"{'PASS' if v else 'FAIL'}  {k}")
    print("archived section bytes:", len(section.encode("utf-8")))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
