# r406 bm-b: CODELY.md append batch-80 + hot-cold consolidation (watermark law, in-window)
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CP = "CODELY.md"
AP = "research/memory-archive/202609.md"

# markers of the six dated entries to archive (batches 74-79)
MARKS = [
    "- [2026-09-29 02:2x] r403 bm-b 坑律七十四批",
    "- [2026-09-29 02:4x] r193 bm-c 坑律七十五批",
    "- [2026-09-29 02:44] r404 bm-b 坑律七十六批",
    "- [2026-09-29 03:1x] r410 bm-a 坑律七十七批",
    "- [2026-09-29 03:1x] r194 bm-c 坑律七十八批",
    "- [2026-09-29 03:19] r411 bm-a 坑律七十九批",
]
NEW80 = open("results/_r406bmb_codely_line.txt", encoding="utf-8").read().rstrip("\n")

lines = open(CP, encoding="utf-8").read().splitlines()
assert not any("\ufffd" in l for l in lines), "existing CODELY has replacement char?"

# 1) locate the six dated entries
idx = {}
for m in MARKS:
    hits = [i for i, l in enumerate(lines) if l.startswith(m)]
    assert len(hits) == 1, f"marker {m[:40]}... hits={hits}"
    idx[m] = hits[0]
moved = [lines[idx[m]] for m in MARKS]
first = min(idx.values())

# 2) append batch-80 line right after the last dated entry (hot layer)
lines.insert(max(idx.values()) + 1, NEW80)

# 3) build pointer line, replace the six entries + keep 80 in place? No: watermark law
#    requires in-window consolidation; 80 goes to archive TOO (whole hot tail this window).
POINTER = (
    "冷层指针：坑律正典 2026-09-29 七十四~八十批（r403 bm-b 七十四批 CPU-delta 探针律死会话归因/r193 bm-c 七十五批集团令面移动断链·义务定义交棒律/"
    "r404 bm-b 七十六批 resolver take-NEW 公式方向坑·t3>t2 修正/r410 bm-a 七十七批 T-116 迁移窗 lane 镜像滞后假阳性·共享面权威律/"
    "r194 bm-c 七十八批 llama-bench 均值列坑+跨服字段域/r411 bm-a 七十九批指针写≠执行律/r406 bm-b 八十批 CJK 命令通道写面腐蚀坑·文件面写盘律"
    "·水位律当窗整编）全文 verbatim=archive 202609.md『坑律归档 2026-09-29 r406 bm-b 窗批』节（行级零丢失校验）。"
)
# remove the seven dated entries (six + newly inserted 80), insert pointer at first position
drop = set(idx.values()) | {max(idx.values()) + 1}  # 80 was inserted after max
kept = [l for i, l in enumerate(lines) if i not in drop]
pos = first  # first dated-entry position in the ORIGINAL list; after removals the pointer goes here
# recompute: number of removed lines before `first` is 0 (all dated entries are >= first)
kept.insert(first, POINTER)
text = "\n".join(kept) + "\n"
assert "\ufffd" not in text, "pointer/new text has replacement char"
open(CP, "w", encoding="utf-8", newline="").write(text)

# 4) archive section: verbatim seven entries + zero-loss footer
section_lines = ["", "## 坑律归档 2026-09-29 r406 bm-b 窗批", ""]
for m in MARKS:
    section_lines.append(lines[idx[m]])  # original entries (pre-removal snapshot)
section_lines.append(NEW80)
section_lines.append("")
section_lines.append("〔r406 bm-b 窗行级零丢失校验：以上七条（七十四~八十批）自 CODELY.md 热层 verbatim 迁移，条目内容零删零改动。〕")
arch_text = open(AP, encoding="utf-8").read()
open(AP, "w", encoding="utf-8", newline="").write(arch_text + "\n".join(section_lines) + "\n")

# 5) verify: each of the 7 entries verbatim present in archive; CODELY < 10KB; no dup
arch = open(AP, encoding="utf-8").read()
for m in MARKS:
    assert lines[idx[m]] in arch, f"verbatim missing: {m[:30]}"
assert NEW80 in arch, "batch-80 verbatim missing in archive"
assert sum(1 for _ in [l for l in kept if l.startswith(NEW80[:30])]) == 0, "80 still hot"
sz = os.path.getsize(CP)
print(f"CODELY.md {sz}B (<=10240: {sz <= 10240}); archived 7 entries verbatim-verified; pointer inserted at line {first}")
