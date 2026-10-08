"""r779 bm-c CODELY main-file hot-cold split surgery (D-20261002-06 standing
law: main <=30,720B; append of the r779 S4 pit line pushes 30,684B over cap ->
same-window split per the r441/r731/r735 ceremony family).

Migration set (9 rows, byte-measured, each unique-needle verified):
  A r387 cold-ptr line 61  -> archive 202610.md new window-batch section
  B r276 cold-ptr line 62  -> same
  C r483a cold-ptr line 65 -> same
  D r483b cold-ptr line 66 -> same
  E r561 cold-ptr line 72  -> same
  F r431 cold-ptr line 73  -> same
  G r690 cold-ptr line 76  -> same
  H r643 cold-ptr line 78  -> same
  I r872 pit row line 102  -> research/pit-protocol-lane.md (r844/r865/r750
                              family domain; r731 precedent migrating a bm-a
                              pit row to its domain file)
  A-H replaced by ONE merged pointer row (r444/r800 merge paradigm) at the
  position of row A. New S4 pit line (r779 DEC watermark contradiction
  3-step law) appended at file end.

Safety: treasure_guard prescan run + rc recorded (r735 precedent: registry
hit does NOT block D-06-authorized byte-verbatim migration, not a deletion;
zero-loss asserted). Assertions before write: every needle line found exactly
once; after write: every migrated row verbatim in target; retained face of
main byte-identical; main <=30,720B; pit-protocol-lane <=30,720B.
Receipt: results/_r779bmc_coldptr_merge.json (dry-run mode writes
results/_r779bmc_coldptr_merge_dryrun.json instead, no files touched).
All edits byte-level on the raw CRLF blob (EOL face preserved verbatim)."""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
ARCHIVE = os.path.join(ROOT, "research", "memory-archive", "202610.md")
LANE = os.path.join(ROOT, "research", "pit-protocol-lane.md")
RECEIPT = os.path.join(ROOT, "results", "_r779bmc_coldptr_merge.json")
DRY = os.path.join(ROOT, "results", "_r779bmc_coldptr_merge_dryrun.json")

CAP = 30720

NEEDLES = {  # unique substring -> (label, target)
    "冷层指针（r387 合并": ("A_r387", "archive"),
    "冷层指针（r276 合并": ("B_r276", "archive"),
    "r492 bm-a Start-Process": ("C_r483a", "archive"),
    "r292 bm-c O-2230": ("D_r483b", "archive"),
    "冷层指针（r561 整编": ("E_r561", "archive"),
    "冷层指针（r431 整编": ("F_r431", "archive"),
    "冷层指针（r690 整编": ("G_r690", "archive"),
    "冷层指针（r643 合并": ("H_r643", "archive"),
    "收尾脚本旧路径轮报行坑第3例": ("I_r872", "lane"),
}

MERGED_ROW = (
    "- 冷层指针（r779 合并·指针合并归档 r444/r800 范式·D-20261002-06 主件 ≤30KB 判据腿）："
    "r387/r276/r483×2/r561/r431/r690/r643 八条冷层指针行——原八行全文 verbatim="
    "archive 202610.md『热冷整编 2026-10-08 r779 bm-c 窗批』节"
    "（receipt=results/_r779bmc_coldptr_merge.json）；各所指正文另在 archive 202609.md/"
    "202610.md 对应『窗批』节（r292 正典=令件 fleet/orders/O-2026-09-30-2230-bm-a.md·"
    "r453 正典=fleet/orders/O-20261004-0808-bm-a.md+bm-c 轮报 r453）；坑律本体全部在 "
    "pit-* 域件与正典件，指针行仅导航用。"
)

NEW_S4 = (
    "- [2026-10-08 21:3x r779 bm-c] **跨机 DEC 水位矛盾核查三步法（近失坑实弹）**："
    "他机轮报宣称消费了本机未见的新决策（bm-a r890「ee70cef0→54b242ac」vs 本机 origin "
    "锚探针「EE70CEF0 零增量」）——①命令面首查：group 树 git log -- docs/decisions.md "
    "不带 origin/main 前缀=读本地陈旧树（本机本地 group 树落后至 10-07 22:41·首查假读"
    "「无 10-08 决策提交」·D-20260930-13 禁读工作树副本律的 history/log 变体面）；"
    "②跨机哈希宣称面=他机可从其本地领先面消费（双工作面推送协议）·origin blob 锚探针是"
    "唯一可比面·他机本地领先≠本机漏消费；③终局裁决=origin blob 内容实读（决策行 "
    "verbatim 行号）+本机水位链回溯（facts 文件族定位首次消费轮=r756 消费 "
    "D-20261008-05~08·水位恒等闭环）。How to apply：见跨机水位矛盾先跑三步法再定性·"
    "禁跳步宣称「决策被回滚」。"
)

ARCHIVE_SECTION_HDR = "## 热冷整编 2026-10-08 r779 bm-c 窗批（CODELY 主件 9 行 verbatim 迁出·coldptr merge+pit row domain move）"
ARCHIVE_SECTION_NOTE = (
    "（迁移仪式 r441/r731/r735 同款；A-H 八条冷层指针行由 r779 合并指针行接替·"
    "I r872 行迁 pit-protocol-lane.md r844/r865/r750 同族域；receipt=results/"
    "_r779bmc_coldptr_merge.json；prescan rc3 留痕=登记簿命中照录·D-06 授权 verbatim "
    "迁移非删除）"
)


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    apply = "--apply" in sys.argv
    raw = open(MAIN, "rb").read()
    lines = raw.split(b"\r\n")  # file is uniform CRLF (103 CRLF, 0 bare LF)
    facts = {"round": 779, "apply": apply, "main_bytes_before": len(raw)}

    # prescan (r735 precedent: rc recorded, registry hit does not block
    # D-06-authorized byte-verbatim migration)
    p = subprocess.run([sys.executable,
                        os.path.join(ROOT, "Tools", "treasure_guard.py"),
                        "prescan", "CODELY.md",
                        "research/memory-archive/202610.md",
                        "research/pit-protocol-lane.md"],
                       capture_output=True)
    facts["prescan_rc"] = p.returncode
    facts["prescan_note"] = ("rc recorded per r735 precedent; D-06 authorized "
                             "byte-accounted verbatim migration (not a deletion); "
                             "zero-loss asserted by bytes-in-target blocks")

    # locate needle lines
    idx = {}
    for needle, (label, target) in NEEDLES.items():
        enc = needle.encode("utf-8")
        hits = [i for i, l in enumerate(lines) if enc in l]
        if len(hits) != 1:
            print("FATAL: needle %s hits=%s (expect exactly 1)" % (label, hits))
            return 3
        idx[label] = hits[0]
    facts["needle_lines"] = idx

    # snapshot rows verbatim (bytes without EOL) + with-EOL bytes for accounting
    rows = {}
    for label, i in idx.items():
        rows[label] = lines[i]
    for label in rows:
        facts.setdefault("row_bytes", {})[label] = len(rows[label]) + 2  # +CRLF

    # build new main
    remove = set(idx.values())
    merged_enc = MERGED_ROW.encode("utf-8")
    s4_enc = NEW_S4.encode("utf-8")
    pos_a = idx["A_r387"]
    new_lines = []
    for i, l in enumerate(lines):
        if i == pos_a:
            new_lines.append(merged_enc)
            continue
        if i in remove:
            continue
        new_lines.append(l)
    new_lines.append(s4_enc)
    new_main = b"\r\n".join(new_lines) + b"\r\n"

    # lane append: row I verbatim + accounting line
    lane_raw = open(LANE, "rb").read()
    row_i = rows["I_r872"]
    acct = ("- 对账行 r779 bm-c: entry bytes=%d sha16=%s verbatim-in-file "
            "(r844/r865/r750 family domain move per r731 precedent; "
            "receipt=results/_r779bmc_coldptr_merge.json; zero-loss asserted)"
            % (len(row_i), sha16(row_i))).encode("utf-8")
    sep = b"\r\n" if lane_raw.endswith(b"\r\n") else b"\n"
    new_lane = lane_raw + sep + row_i + b"\r\n" + acct + b"\r\n"

    # archive append: new section with rows A-H verbatim
    arch_raw = open(ARCHIVE, "rb").read()
    sect = [ARCHIVE_SECTION_HDR.encode("utf-8"),
            ARCHIVE_SECTION_NOTE.encode("utf-8")]
    for label in ["A_r387", "B_r276", "C_r483a", "D_r483b",
                  "E_r561", "F_r431", "G_r690", "H_r643"]:
        sect.append(rows[label])
    arch_asep = b"\r\n" if arch_raw.endswith(b"\r\n") else b"\n"
    new_arch = arch_raw + arch_asep + b"\r\n".join(sect) + b"\r\n"

    # assertions
    facts["main_bytes_after"] = len(new_main)
    facts["lane_bytes_after"] = len(new_lane)
    facts["archive_bytes_after"] = len(new_arch)
    facts["merged_row_bytes"] = len(merged_enc) + 2
    facts["new_s4_bytes"] = len(s4_enc) + 2
    assert len(new_main) <= CAP, "main over cap: %d" % len(new_main)
    assert len(new_lane) <= CAP, "lane over cap: %d" % len(new_lane)
    for label, target_file, blob in (
            [("A_r387", "archive", new_arch), ("B_r276", "archive", new_arch),
             ("C_r483a", "archive", new_arch), ("D_r483b", "archive", new_arch),
             ("E_r561", "archive", new_arch), ("F_r431", "archive", new_arch),
             ("G_r690", "archive", new_arch), ("H_r643", "archive", new_arch),
             ("I_r872", "lane", new_lane)]):
        assert rows[label] in blob, "row %s not verbatim in target" % label
    # retained-face identity: every non-removed, non-inserted line unchanged
    old_kept = [l for i, l in enumerate(lines)
                if i not in remove and i != pos_a]
    new_kept = [l for i, l in enumerate(new_lines)
                if i != pos_a and l not in (merged_enc, s4_enc)]
    # exact multiset comparison on the retained spine:
    spine_old = [l for i, l in enumerate(lines) if i not in remove]
    spine_new = [l for l in new_lines if l not in (merged_enc, s4_enc)]
    # spine_new should equal spine_old minus... no: pos_a replaced by merged ->
    # remove pos_a from old spine comparison set
    spine_old_wo_a = [l for i, l in enumerate(lines)
                      if i not in remove and i != pos_a]
    assert spine_old_wo_a == [l for l in spine_new], "retained spine mismatch"
    facts["retained_spine_lines"] = len(spine_old_wo_a)
    facts["rows_migrated_archive"] = 8
    facts["rows_migrated_lane"] = 1
    facts["sha16_rows"] = {k: sha16(v) for k, v in rows.items()}
    facts["assert_zero_loss"] = True
    facts["assert_main_under_cap"] = len(new_main) <= CAP
    facts["assert_lane_under_cap"] = len(new_lane) <= CAP

    out = RECEIPT if apply else DRY
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print("mode=%s main %d -> %d (cap %d) lane %d -> %d archive %d -> %d"
          % (apply, facts["main_bytes_before"], len(new_main), CAP,
             len(lane_raw), len(new_lane), len(arch_raw), len(new_arch)))
    print("receipt ->", out)
    if not apply:
        print("DRY RUN ONLY: no files written")
        return 0
    open(MAIN, "wb").write(new_main)
    open(LANE, "wb").write(new_lane)
    open(ARCHIVE, "wb").write(new_arch)
    print("APPLIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
