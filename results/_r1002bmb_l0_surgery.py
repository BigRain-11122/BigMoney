# -*- coding: utf-8 -*-
"""r1002 bm-b: L0 pollution clean (CEO order 2026-10-18 00:2x piece-3) + identity tuple.
Moves 25 other-machine-domain / superseded-dupe entries verbatim -> topic files,
inserts bm-b identity tuple as first User entry, regenerates [memory-gate] index counts.
Zero-loss assertions enforced; CRLF/BOM preserved; mtime-guard style single write."""
import os, sys, datetime

L0 = r"C:\Users\Administrator\.codely-cli\CODELY.md"
TOPICS = r"C:\Users\Administrator\memory\topics"
SECTIONS = ("User", "Feedback", "Project", "Reference")

# (unique first-line prefix, target topic file)
MOVES = [
    ("- [2026-10-02 19:09:53] [2026-10-10 01:0x 勘正·union 串机事故修复] 机队硬件档", "hardware-procurement.md"),
    ("- [2026-10-16 16:29:55] [2026-10-16 16:3x] [MV 产线长期法·CEO 机制问责令", "mv-production.md"),
    ("- [2026-10-08 14:40:05] CEO 深研先行律+过目双闸（2026-10-08 MV 令三连申斥后立·BigStream 内容产线长期硬门·原话「研究透了", "mv-production.md"),
    ("- [2026-10-08 19:55:52] [2026-10-08] bm-a 弹窗根治终态", "tool-pitfalls.md"),
    ("- [2026-10-09 11:43:00] [2026-10-09 12:0x] [2026-10-09] CEO 角色设计裁决", "mv-production.md"),
    ("- [2026-10-09 13:18:15] [2026-10-09 12:5x] [2026-10-09] CEO 男主定谳令", "mv-production.md"),
    ("- [2026-10-09 15:29:28] [2026-10-09 17:0x] [2026-10-09 15:2x] CEO 男主脸四连令定谳", "mv-production.md"),
    ("- [2026-10-09 16:20:42] [2026-10-09 17:2x] [2026-10-09 16:4x] CEO 男主路线定谳+双主设计追加令", "mv-production.md"),
    ("- [2026-10-09 16:59:12] [2026-10-09 17:5x] CEO 角色设计第二簇令", "mv-production.md"),
    ("- [2026-10-09 17:11:20] [2026-10-09 17:5x] [2026-10-09 16:4x-17:4x] CEO 男主角色系列裁决", "mv-production.md"),
    ("- [2026-10-09 18:02:10] [2026-10-09 18:0x] [2026-10-09 17:3x-17:5x] CEO mv0001 角色面七连令+保留清单", "mv-production.md"),
    ("- [2026-10-02 19:09:53] 本机（C 机）定位", "hardware-procurement.md"),
    ("- [2026-10-09 22:02:07] [2026-10-09 22:2x] CEO mv0001 30秒MV 生产裁决簇", "mv-production.md"),
    ("- [2026-10-09 23:19:41] [2026-10-09 23:0x] [2026-10-09 22:4x-23:0x] CEO mv0001 30秒片三连批后创作工作流定谳", "mv-production.md"),
    ("- [2026-10-02 19:09:53] [2026-10-10 00:3x 实测修正] 本机（C 机/bm-a）定位", "hardware-procurement.md"),
    ("- [2026-10-08 14:40:05] [2026-10-10 修订] CEO 深研先行律+过目双闸", "mv-production.md"),
    ("- [2026-10-09 16:59+17:11 并档] [2026-10-09 17:5x] CEO 男主角色系列裁决（mv0001·两簇令合并", "mv-production.md"),
    ("- [2026-10-10 18:16:36] [2026-10-10] CEO 常设授权令（原话「决策委员会替我去决策那些堆积的事情，只有物理件等我来有空弄」·O-20261010-1800）：①一切积压/新增决策件=决策委员会 T1 代决+7 天否决窗", "governance-council.md"),
    ("- [2026-10-13 22:19:24] CEO 机队 CPU 常设开放令（2026-10-13 22:1x 原话", "fleet-dispatcher.md"),
    ("- [2026-10-17 12:22:15] - [2026-10-17 12:2x] 坑录（V5 追加 4 镜重烧交付窗·bm-c）", "mv-production.md"),
    ("- [2026-10-09 19:01:16] [2026-10-09 19:0x] O-20261009-1746 MiniMax-H3 装机测试令收口态（bm-a 视角", "mv-production.md"),
    ("- [2026-10-09 19:33:18] [2026-10-09 19:3x] mv0001「画面+歌」端到端装配管线首验", "mv-production.md"),
    ("- [2026-10-06 23:1x r798 bm-a] **CEO 用机让路律触发词", "fleet-dispatcher.md"),
    ("- [2026-10-14 13:15:39] [2026-10-14 13:2x] CEO 常设工作律（原话「github上面有现成的工具", "governance-council.md"),
    ("- [2026-10-13 22:19:24] CEO 机队 CPU 常设开放令（22:1x 原话", "fleet-dispatcher.md"),
]

IDENTITY = ("- [2026-10-18 bm-b 身份元组] L0 归属=bm-b（compute-node·16核/24GB RAM/RTX3070 8G·1200W PSU 满性能·"
            "用户 Administrator）；治理=memory-curator 写入五问门+4h S4U 预算闸 bm-b-MemoryBudgetGate"
            "（执法线 50KB/120 条·预警 35KB/80 条·Tools/memory-budget-gate.py）+主题路由 ~/memory/topics/；"
            "他机域内容按主题路由出 L0·本条= bm-b 专属身份锚（禁联合回灌禁他机覆写；CEO 令 2026-10-18 00:2x·"
            "R-20261018-memory-control-01）")

raw = open(L0, "rb").read()
bom = raw.startswith(b"\xef\xbb\xbf")
text = raw.decode("utf-8-sig")
crlf = "\r\n" in text
norm = text.replace("\r\n", "\n")
lines = norm.split("\n")

# split: header (before first '### ') + section entries
entries = []  # [sec, text]
header = []
sec = None
pend = None
for ln in lines:
    if ln.startswith("### ") and ln[4:].strip() in SECTIONS:
        if pend: entries.append(pend)
        pend = None
        sec = ln[4:].strip()
        continue
    if sec is None:
        header.append(ln)
        continue
    if ln.startswith("- ["):
        if pend: entries.append(pend)
        pend = [sec, ln]
    elif pend is not None:
        pend[1] += "\n" + ln
    # blank lines between sections fall into pend of previous entry (tail) - matches gate parse
if pend: entries.append(pend)

assert len(entries) == 102, "entry count drift: %d" % len(entries)

# match moves
move_map = {}   # idx -> topic
for i, (s, txt) in enumerate(entries):
    for pref, topic in MOVES:
        if txt.startswith(pref):
            assert i not in move_map, "dup match %d" % i
            move_map[i] = topic
missing = [p for p, _ in MOVES if not any(e[1].startswith(p) for e in entries)]
assert not missing, "unmatched prefixes: %r" % missing[:3]
assert len(move_map) == len(MOVES), "matched %d != %d" % (len(move_map), len(MOVES))

# append moved verbatim to topics
os.makedirs(TOPICS, exist_ok=True)
for i, topic in sorted(move_map.items()):
    with open(os.path.join(TOPICS, topic), "a", encoding="utf-8", newline="\n") as f:
        f.write("\n" + entries[i][1].strip() + "\n")

# build keep list + identity tuple as first User entry
out_entries = []
inserted = False
for i, (s, txt) in enumerate(entries):
    if i in move_map:
        continue
    if s == "User" and not inserted:
        out_entries.append([s, IDENTITY])
        inserted = True
    out_entries.append([s, txt])
assert inserted, "identity tuple not inserted"
assert len(out_entries) == 102 - len(MOVES) + 1

# regenerate [memory-gate] index entry counts
counts = {}
for fn in sorted(os.listdir(TOPICS)):
    if fn.endswith(".md"):
        with open(os.path.join(TOPICS, fn), encoding="utf-8") as f:
            counts[fn] = sum(1 for l in f if l.startswith("- ["))
fixed = []
for s, txt in out_entries:
    if txt.startswith("- [memory-gate]"):
        head = txt.split("\n")[0]
        fixed.append([s, head + "\n" + "".join("- %s（%d 条）=%s\\%s\n" % (fn, c, TOPICS, fn) for fn, c in counts.items())])
    else:
        fixed.append([s, txt])

# rebuild
out = ["\n".join(header) if header and any(h.strip() for h in header) else ""]
for s in SECTIONS:
    out.append("### " + s)
    for sec2, txt in fixed:
        if sec2 == s:
            out.append(txt)
    out.append("")
new_text = "\n".join(out).lstrip("\n")
if not new_text.endswith("\n"):
    new_text += "\n"
if crlf:
    new_text = new_text.replace("\n", "\r\n")
nb = (b"\xef\xbb\xbf" if bom else b"") + new_text.encode("utf-8")

# zero-loss verify: every kept entry text present in new_text; every moved first-line in topic file
for s, txt in fixed:
    assert txt in new_text.replace("\r\n", "\n"), "lost entry: " + txt[:60]
for i, topic in move_map.items():
    fl = entries[i][1].split("\n")[0]
    assert fl in open(os.path.join(TOPICS, topic), encoding="utf-8").read(), "topic missing moved entry"

open(L0, "wb").write(nb)
print("L0-SURGERY bytes=%d->%d entries=102->%d moved=%d topics=%s" % (len(raw), len(nb), len(fixed), len(MOVES), sorted(set(move_map.values()))))
print("IDENTITY-INSERTED; index topics=%d" % len(counts))
