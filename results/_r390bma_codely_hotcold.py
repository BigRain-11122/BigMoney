# -*- coding: utf-8 -*-
"""r390 bm-a CODELY.md hot-cold archive (batch 34).

Watermark law: new pit-law append would push the hot layer past the
<=10KB hard line -> same-window hot-cold edit (勿等月, r384/r385
precedent).  Binary-face read/write preserves the CRLF working-tree
lineage (r389 pit-law: git ls-files --eol i/lf w/crlf verified).

Migrates the two OLDEST hot entries (r141/r142 bm-c, 2026-09-28 06:5x)
verbatim to research/memory-archive/202609.md batch-34 section, keeps
a hot-layer pointer line, appends the new r390 pit-law entry.
"""
import io
import sys

HOT = "CODELY.md"
ARC = "research/memory-archive/202609.md"

NEW_ENTRY = (
    "- [2026-09-28 07:3x r390 bm-a] 坑律：**行插入类 replace 的 old_string "
    "必须锚定整行（或带完整上下行）——拿既有行的行首片段当锚插入新行=新文本"
    "与残尾同线缝合、原行首被吞**（r390 实弹：HANDOVER 5x 行插入用 bm-b r365 "
    "行首短片段当锚→replace 后我的新行+bm-b 行残尾缝成一行 5,278B、总行数不增"
    "=读页难觉；git diff --stat 权威核验=1 insertion 0 deletions 证非外科，接缝"
    "拆分回植行首修复+行首前缀枚举复验）。How to apply：①行插入 new_string=新行"
    "完整+锚行完整原文，old_string=锚行完整原文（勿用行首片段）；②长文件改动后"
    "行数/接缝疑差以 git diff 为权威（splitlines 计数/分页读均可骗）；③修复后必跑"
    "结构核验（行首前缀枚举+锚行首尾恒等+diff --stat 外科数字）。指针="
    "round_reports-bm-a R390+git diff research/HANDOVER.md 1 insertion。"
)

MIGRATE_PREFIXES = (
    "- [2026-09-28 06:5x r141 bm-c] 坑律：",
    "- [2026-09-28 06:5x r142 bm-c] 坑律：",
)


def read_crlf(path):
    with open(path, "rb") as fh:
        return fh.read().decode("utf-8")


def write_crlf(path, text):
    # normalize to CRLF on the wire (working-tree lineage w/crlf)
    text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    with open(path, "wb") as fh:
        fh.write(text.encode("utf-8"))


hot = read_crlf(HOT)
arc = read_crlf(ARC)

# 1) append the new r390 entry at the very end
sep = "\n\n" if not hot.rstrip("\r\n").endswith("\n") else "\n"
hot_new = hot.rstrip("\r\n") + "\r\n\r\n" + NEW_ENTRY + "\r\n"
post_append = len(hot_new.encode("utf-8"))
print(f"post-append hot size: {post_append}B (hard line 10,240B) "
      f"-> over={post_append > 10240}")

# 2) extract the two oldest entries verbatim (entry = one line, blank-line
#    separated in this file)
hot_lines = hot_new.split("\r\n")
migrated = []
kept = []
for ln in hot_lines:
    if any(ln.startswith(p) for p in MIGRATE_PREFIXES):
        migrated.append(ln)
    else:
        kept.append(ln)
assert len(migrated) == 2, f"expected 2 migration entries, got {len(migrated)}"
# trailing blanks collapse: rebuild without double blanks at EOF
while kept and kept[-1] == "":
    kept.pop()
hot_final = "\r\n".join(kept) + "\r\n"

# 3) pointer line inserted right after the batch-33 pointer line
PTR = (
    f"冷层指针：坑律正典 2026-09-28 三十四批（r390 bm-a 窗·水位律当窗整编："
    f"新坑律 append 后 {post_append}B 超 ≤10KB 硬线）：r141 CLI 分发表零参调用"
    f"+池分片键唯一 / r142 crash-fuse 25min 静默死盲窗 两条全文 verbatim="
    f"archive 202609.md『坑律归档 2026-09-28 三十四批』节（行级零丢失校验）。"
)
idx = max(i for i, ln in enumerate(kept)
          if ln.startswith("冷层指针：坑律正典 2026-09-28 三十三批"))
kept.insert(idx + 1, PTR)
hot_final = "\r\n".join(kept) + "\r\n"

# 4) archive section (verbatim lines + migration record)
SECTION = (
    "\r\n\r\n## 坑律归档 2026-09-28 三十四批（r390 bm-a 窗·水位律当窗整编："
    "新坑律 append 后超 ≤10KB 硬线）\r\n\r\n"
    + migrated[0] + "\r\n\r\n"
    + migrated[1] + "\r\n\r\n"
    + "> 迁移记录（三十四批=两条坑律 r141 CLI 子命令分发表零参调用+池分片键"
    "跨条目唯一、r142 crash-fuse FUSE_CONFIRM_MIN 静默死盲窗，自 CODELY.md "
    "热层 verbatim 迁移〔行级零丢失校验〕；热层含三十四批指针行〔归档侧"
    "迁移史留痕〕。\r\n"
)
arc_new = arc.rstrip("\r\n") + "\r\n" + SECTION.lstrip("\r\n")

# 5) verifications
fail = []
for m in migrated:
    if m not in arc_new:
        fail.append(f"archive missing entry: {m[:60]}")
    if any(ln == m for ln in hot_final.split("\r\n")):
        fail.append(f"hot still contains entry: {m[:60]}")
for m in migrated:
    for probe in ("How to apply", "指针="):
        if probe not in arc_new:
            fail.append(f"archive entry truncated (missing {probe})")
hot_size = len(hot_final.encode("utf-8"))
if hot_size > 10240:
    fail.append(f"hot {hot_size}B > 10,240B hard line")
# hot structural anchors intact
for anchor in ("### User", "### Feedback", "### Project", "### Reference",
               NEW_ENTRY[:40]):
    if anchor not in hot_final:
        fail.append(f"hot missing anchor: {anchor}")
# pointer present exactly once
if hot_final.count(PTR[:30]) != 1:
    fail.append("pointer line count != 1")
if "三十四批" not in arc_new:
    fail.append("archive missing batch-34 header")

if fail:
    for f in fail:
        print("FAIL:", f)
    sys.exit(1)

write_crlf(HOT, hot_final)
write_crlf(ARC, arc_new)
print(f"hot final: {hot_size}B <= 10,240B OK; migrated 2 entries verbatim; "
      f"archive +{len(SECTION.encode('utf-8'))}B; containment PASS")
