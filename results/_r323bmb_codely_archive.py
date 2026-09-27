# -*- coding: utf-8 -*-
"""r323 bm-b: CODELY.md S4 append + water-mark hot/cold reorg (12th batch).

Post-append size would cross the 10KB hard line (group order O-20260927-0230):
append new r323 pitlaw -> archive oldest hot entries (r317/r318/r319 bm-b)
verbatim to research/memory-archive/202609.md -> add batch index line to
Reference section -> strict re-verify + multiset zero-loss check.
"""
import io, os, sys, json

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"
CODELY = os.path.join(REPO, "CODELY.md")
ARCHIVE = os.path.join(REPO, "research", "memory-archive", "202609.md")

NEW_ENTRY = (
    "- [2026-09-27 12:5x r323 bm-b] 坑律：**GBK 污染修复必须全量扫生产者当窗写入面——只修冲突集单件=同病残留**"
    "——r320 bm-a 修 HANDOVER GBK 段（rebase 冲突集内件）后，同窗生产者（bm-b r320 两提交 54 件面）的 "
    "round_reports.md r320 行 GBK 3381B 漏扫残留 5h，r323 轮首 strict 读者实撞 UnicodeDecodeError；"
    "正典=①污染修复扫描面=生产者提交 `git show --stat` 全量件单逐 strict UTF-8 验（禁只扫冲突集）"
    "②坏区 strict gbk→UTF-8 无损转码+全文件重验+邻行在场断言+行数不变"
    "③正式件追加一律 `io.open(...,encoding='utf-8')` 禁裸 open()/PS Add-Content（zh-CN locale=GBK 生产源）。"
    "指针=results/_r323bmb_gbk_sweep.py+round_reports r323 行。"
)

ARCHIVE_KEYS = ["[2026-09-27 11:3x r317 bm-b]", "[2026-09-27 11:4x r318 bm-b]", "[2026-09-27 12:0x r319 bm-b]"]
INDEX_LINE = (
    "十二批外迁（r323 bm-b·水位律当窗整编）：r317 autostash stage-union/r318 方案A git 转移通道双暗面/"
    "r319 union 去重键实存=归档十二批节·行级零丢失。"
)
BATCH_HEADER = "## 十二批迁移（r323 bm-b·2026-09-27 水位律当窗整编·行级零丢失）"

def main():
    t = io.open(CODELY, encoding="utf-8").read()
    lines = t.splitlines(keepends=True)
    moved, kept = [], []
    for ln in lines:
        if any(k in ln for k in ARCHIVE_KEYS):
            moved.append(ln)
        else:
            kept.append(ln)
    assert len(moved) == 3, "expected exactly 3 archive targets, got %d" % len(moved)

    new_text = "".join(kept).rstrip("\n") + "\n" + NEW_ENTRY + "\n"
    # insert batch index line right after the 十一批 index line in Reference section
    idx_anchor = None
    for i, ln in enumerate(kept):
        if ln.startswith("十一批外迁"):
            idx_anchor = i
            break
    assert idx_anchor is not None, "十一批 anchor not found"
    out_lines = new_text.splitlines(keepends=True)
    pos = next(i for i, ln in enumerate(out_lines) if ln.startswith("十一批外迁"))
    out_lines.insert(pos + 1, INDEX_LINE + "\n")
    final = "".join(out_lines)

    # append batch to archive (verbatim moved lines)
    a = io.open(ARCHIVE, encoding="utf-8").read()
    arch_new = a.rstrip("\n") + "\n\n" + BATCH_HEADER + "\n" + "".join(moved).rstrip("\n") + "\n"

    io.open(CODELY, "w", encoding="utf-8", newline="").write(final)
    io.open(ARCHIVE, "w", encoding="utf-8", newline="").write(arch_new)

    # verification: strict re-read, size, zero-loss multiset
    c2 = io.open(CODELY, encoding="utf-8").read()
    a2 = io.open(ARCHIVE, encoding="utf-8").read()
    v = {
        "codely_size": os.path.getsize(CODELY),
        "codely_under_10kb": os.path.getsize(CODELY) <= 10240,
        "archive_size": os.path.getsize(ARCHIVE),
        "new_entry_present": NEW_ENTRY[:60] in c2,
        "moved_gone_from_hot": all(k not in c2 for k in ARCHIVE_KEYS),
        "moved_in_archive": all(k in a2 for k in ARCHIVE_KEYS),
        "multiset_zero_loss": sorted(ln.strip() for ln in moved) == sorted(
            ln.strip() for ln in a2.splitlines() if any(k in ln for k in ARCHIVE_KEYS)),
        "index_line_present": INDEX_LINE[:12] in c2,
        "batch_header_present": BATCH_HEADER[:6] in a2,
        "verbatim_bytes": sum(len(ln.encode("utf-8")) for ln in moved),
    }
    v["verdict"] = "PASS" if all(x for k, x in v.items() if isinstance(x, bool)) else "FAIL"
    print(json.dumps(v, ensure_ascii=False, indent=1))
    sys.exit(0 if v["verdict"] == "PASS" else 2)

if __name__ == "__main__":
    main()
