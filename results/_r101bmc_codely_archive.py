# -*- coding: utf-8 -*-
"""r101 bm-c: CODELY.md S4 append + water-mark hot/cold reorg (27th batch).

Post-append size would cross the 10KB hard line (group order O-20260927-0230;
r310 precedent: 10125B = over). Fold the 8 redundant batch-pointer rows (their
verbatims already live in archive 202609.md per their own pointer text) into the
archive as 27th batch + one index line, then append the new r101 pitlaw.
Line-level zero-loss: every moved line must be byte-content-identical in archive.
"""
import io, os, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CODELY = os.path.join(REPO, "CODELY.md")
ARCHIVE = os.path.join(REPO, "research", "memory-archive", "202609.md")

NEW_ENTRY_PREFIX = "- [2026-09-27 20:3x r101 bm-c] 坑律：树重建后 lane-local gitignored 数据面盘点缺位"
NEW_ENTRY = (
    "- [2026-09-27 20:3x r101 bm-c] 坑律：树重建后 lane-local gitignored 数据面盘点缺位"
    "（U196 统一根重建实弹：fund_premium snapshots 原始快照序列随旧树退役尽失——backfill-nav 只重建 "
    "nav/dividends/panel 派生面、原始采集面无重建腿，磁盘 snapshots=0 与 status last_fetch 成功互矛；"
    "派生面 panel 完整+交易日采集自愈重续序列，原始证据面成结构性缺口）；"
    "正典=树重建后 lane owner 必盘点 gitignored 本地目录族（原始采集面 vs 派生面分核），"
    "采集器 selftest 不覆盖盘上历史在位性。"
)

# 5 signatures -> 8 rows (r334 x2, r335 x2, r341, r91, r339, r340)
ARCHIVE_KEYS = [
    "[2026-09-27 17:3x r334 bm-b] 坑律（二十六批外迁·指针）",
    "[2026-09-27 17:5x r335 bm-b] 坑律（二十六批外迁·指针）",
    "[2026-09-27 17:5x r341 bm-a] 坑律（二十六批外迁·指针）",
    "[2026-09-27 17:2x r91 bm-c] 坑律（二十三批外迁·指针）",
    "[2026-09-27 17:4x r339 bm-a] 坑律（二十三批外迁·指针）",
    "[2026-09-27 17:5x r340 bm-a] 坑律（二十四批外迁·指针）",
    "[2026-09-27 17:3x r334 bm-b] 坑律（二十三批外迁·指针）",
    "[2026-09-27 17:5x r335 bm-b] 坑律（二十五批外迁·指针）",
]
INDEX_LINE = (
    "- 二十七批外迁（r101 bm-c·2026-09-27·水位律当窗整编·指针行二次折叠·行级零丢失）："
    "r91 S0 stash-pop 定侧源、r334 rolling-ledger dedup 面实时间键（二十三/二十六批双记）、"
    "r335 tick add/stash 不受 r201 护栏（二十五/二十六批双记）、r339 blob 尾态字节拼接、"
    "r340 round_no %5 义务撞窗漏做、r341 stale-takeover 双证并取——8 指针行原样外迁="
    "archive 202609.md『坑律归档 2026-09-27 二十七批』节（所指 verbatim 皆在对应批节在位）。"
)
BATCH_HEADER = "## 坑律归档 2026-09-27 二十七批（r101 bm-c·水位律当窗整编·指针行二次折叠·行级零丢失）"


def eol_of(raw: bytes) -> str:
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    return "\r\n" if crlf >= lf else "\n"


def main():
    raw = io.open(CODELY, "rb").read()
    c_eol = eol_of(raw)
    text = raw.decode("utf-8")
    lines = text.splitlines(keepends=True)
    moved, kept, first_moved_idx = [], [], None
    for i, ln in enumerate(lines):
        if any(k in ln for k in ARCHIVE_KEYS):
            if first_moved_idx is None:
                first_moved_idx = i
            moved.append(ln)
        else:
            kept.append(ln)
    assert len(moved) == 8, f"expected 8 moved rows, got {len(moved)}"
    assert first_moved_idx is not None

    # insert index line at first moved-row position; append new entry at EOF
    out_lines = kept[:first_moved_idx] + [INDEX_LINE + c_eol] + kept[first_moved_idx:]
    if not out_lines[-1].endswith(("\n", "\r")):
        out_lines[-1] += c_eol
    out_lines.append(NEW_ENTRY + c_eol)
    new_text = "".join(out_lines)
    assert NEW_ENTRY_PREFIX in new_text and INDEX_LINE[:20] in new_text

    araw = io.open(ARCHIVE, "rb").read()
    a_eol = eol_of(araw)
    atext = araw.decode("utf-8")
    if not atext.endswith(("\n", "\r")):
        atext += a_eol
    # archive moved lines: preserve content bytes, normalize EOL to archive style
    block = BATCH_HEADER + a_eol
    for ln in moved:
        content = ln.rstrip("\r\n")
        block += content + a_eol
    new_archive = atext + block + a_eol

    # zero-loss verify: every moved line content must exist in new archive
    for ln in moved:
        assert ln.rstrip("\r\n") in new_archive, "moved line missing in archive: " + ln[:60]

    io.open(CODELY, "w", encoding="utf-8", newline="").write(new_text)
    io.open(ARCHIVE, "a", encoding="utf-8", newline="").write(block + a_eol)

    size = os.path.getsize(CODELY)
    moved_bytes = sum(len(l.encode("utf-8")) for l in moved)
    print(f"OK moved={len(moved)} rows ({moved_bytes}B) -> archive 27th batch")
    print(f"CODELY.md new size = {size}B (hard line <=10000)")
    print("verdict:", "GREEN" if size <= 10000 else "RED — over line")
    return 0 if size <= 10000 else 1


if __name__ == "__main__":
    sys.exit(main())
