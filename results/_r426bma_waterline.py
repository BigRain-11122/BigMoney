# r426 bm-a CODELY waterline reorg (hot >10,000B line -> same-window hot-cold per O-20260927-0230)
# Moves: hot pit entries batch-100 (r424) + batch-101 (r211 bm-c) verbatim -> archive 202609.md;
#        8 adjacent cold pointer lines (batches 81-96) merged per r173 precedent (verbatim to archive, one merged line in hot);
#        appends new hot entry batch-102 (S0 rebase queue diagnosis + linear-rebase merge-commit-drop hazard).
# Binary-mode IO, explicit CRLF, no native \r in string literals (r425 byte-truncation pit).
# Verification: every moved line found verbatim in archive text; hot size <10,000B; line-count accounting.
import io, sys

CRLF = b"\r\n"

def read_bytes(p):
    with open(p, "rb") as f:
        return f.read()

HOT = "CODELY.md"
ARC = "research/memory-archive/202609.md"

hot_b = read_bytes(HOT)
assert CRLF in hot_b and hot_b.count(b"\n") == hot_b.count(b"\r\n"), "hot file not pure CRLF"
hot_text = hot_b.decode("utf-8")
lines = hot_text.split("\r\n")
assert lines[-1] == "", "expected trailing newline"
lines = lines[:-1]
orig_count = len(lines)
orig_size = len(hot_b)

# --- identify lines by unique prefixes ---
P_HOT100 = "- [2026-09-29 10:2x r424 bm-a] 坑律一百批"
P_HOT101 = "- [2026-09-29 10:5x r211 bm-c] 坑律一百零一批"
PTR_PREFIXES = [
    "冷层指针：坑律正典 2026-09-29 八十一/八十二/八十三批",
    "冷层指针：坑律正典 2026-09-29 八十四/八十五/八十六批",
    "冷层指针：坑律正典 2026-09-29 八十七/八十八批",
    "冷层指针：坑律正典 2026-09-29 九十/八十九批",
    "冷层指针：坑律正典 2026-09-29 八十八批（r412 bm-b",
    "冷层指针：坑律正典 2026-09-29 八十九批（r413 bm-b",
    "冷层指针：坑律正典 2026-09-29 九十五批三连",
    "冷层指针：坑律正典 2026-09-29 九十六批",
]

def find_one(prefix):
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, f"prefix not unique/found: {prefix!r} hits={hits}"
    return hits[0]

i_hot100 = find_one(P_HOT100)
i_hot101 = find_one(P_HOT101)
i_ptrs = [find_one(p) for p in PTR_PREFIXES]
assert i_hot100 < i_hot101
moved_hot = [lines[i_hot100], lines[i_hot101]]
moved_ptrs = [lines[i] for i in i_ptrs]

# --- new content ---
NEW_HOT102 = (
    "- [2026-09-29 11:5x r426 bm-a] 坑律一百零二批（S0 rebase 队列构成诊断律·线性 rebase 静默丢弃未推 merge commit 坑）："
    "S0 pull --rebase 撞头先诊断队列再动手——本例「Rebasing (1/1)」唯一件=陈旧 r425 原始件 f9890dfde（message 自述 da44b8b11 LANDED=内容已在远端），"
    "真正待保的未推 r426 merge commit 2f7b3e1a 被线性 rebase 静默排除（merge commit 不入重放队列=簿记从分支面蒸发）。"
    "正解序：①git status 读队列构成+message 自查落地面；②merge-base --is-ancestor <声称已落 sha> origin/main 验真；"
    "③0 件已解时 abort 合法（r220 律只护已解工）；④r419 单次 merge-back 收口（6 UU=5 ALL_FACES merge_lane_views resolve+1 append-log multiset union，"
    "一百批 merge 语境直用律实弹再证·reconcile 14 面 13 ZERO-DRIFT+1 RETIRED-SHARED 合法）；⑤push 拒=再单 merge 不 rebase-replay（pit-93 两步式）。"
    "How to apply：S0 rebase 撞头先看队列件数与件名，「件=自称已落地的旧原始件」=abort+单 merge 信号；本地有未推 merge commit 一律禁 rebase-replay。"
)
PTR_ARCHIVED = (
    "冷层指针：坑律正典 2026-09-29 一百批（r424 bm-a·merge 语境 resolve 直用律）+一百零一批（r211 bm-c·池 done-flip 双面闭合律）"
    "全文 verbatim=archive 202609.md『坑律归档 2026-09-29 r426 bm-a 窗批』节（r426 bm-a 窗水位律当窗整编·行级零丢失校验）。"
)
MERGED_PTR = (
    "冷层指针（09-29 r426 bm-a 水位整编·r173 范式合并行·八行 verbatim 迁 archive 202609.md『指针合并归档 2026-09-29 r426 bm-a 窗批』节·零删改）："
    "坑律正典 2026-09-29 八十一~九十六批全段（八十一/八十二/八十三 r410 bm-b 窗批·八十四/八十五/八十六 r201 bm-c 窗批·八十七/八十八 r416-cont bm-a 窗批二·"
    "九十/八十九+T-116 回执+九十四/九十一/九十二/九十三 r415 bm-b 窗批·八十八 r412 bm-b+r202 bm-c V3-TOURNAMENT 收割回执 r413 bm-b 窗批·"
    "八十九 r413 bm-b+r203 bm-c T-116 s3 flip 回执 r204 bm-c 窗批·九十五批三连 r422 bm-a 窗批·九十六批 r208 bm-c 窗批）全文 verbatim=archive 对应各节。"
)

# --- build new hot lines ---
remove = {i_hot100, i_hot101} | set(i_ptrs)
new_lines = []
ptr_new_done = False
merged_done = False
for idx, l in enumerate(lines):
    if idx in remove:
        if idx == i_hot100:
            new_lines.append(NEW_HOT102)  # hot entry replaces archived pair (Project section)
        elif idx == i_ptrs[0]:
            new_lines.append(MERGED_PTR)   # merged pointer replaces 8-line block
        continue
    new_lines.append(l)
    if l == "### Reference" and not ptr_new_done:
        new_lines.append(PTR_ARCHIVED)     # newest archive pointer at top of Reference
        ptr_new_done = True

# fix: merged pointer position -- i_ptrs[0] was L16 which sits AFTER the r407 merged line; keep order as built (first-occurrence replacement preserves position)
assert ptr_new_done, "### Reference anchor not found"
new_count = len(new_lines)
new_hot_b = ("\r\n".join(new_lines) + "\r\n").encode("utf-8")

# --- archive append (verbatim section) ---
arc_b = read_bytes(ARC)
assert arc_b.endswith(b"\r\n") or arc_b.endswith(b"\n"), "archive must end with newline"
nl = b"\r\n" if arc_b.endswith(b"\r\n") else b"\n"
sec = []
sec.append("## 坑律归档 2026-09-29 r426 bm-a 窗批（水位律当窗整编：CODELY 热层 batch-102 append 时 10,168B 已超 10,000B 硬线→一百批/一百零一批 r211 两热条 verbatim 迁此+八指针行 r173 范式合并；行级零丢失校验）")
sec.append(moved_hot[0])
sec.append(moved_hot[1])
sec.append("（以上两条 hot CODELY.md 2026-09-29 r426 迁移窗原样 verbatim；热层去后指针行；零删改零重排。）")
sec.append("")
sec.append("### 指针合并归档 2026-09-29 r426 bm-a 窗批（八行 verbatim 迁此·热层换一行合并行）")
sec.extend(moved_ptrs)
sec.append("（以上八行指针 r426 bm-a 合并窗原样 verbatim；热层合并为一行；零删改。）")
arc_append = ("\r\n".join(sec) + "\r\n").encode("utf-8")

# --- verification BEFORE write ---
arc_text_probe = arc_append.decode("utf-8")
for l in moved_hot + moved_ptrs:
    assert l in arc_text_probe, f"moved line not verbatim in archive append: {l[:60]!r}"
hot_text_new = new_hot_b.decode("utf-8")
for l in moved_hot + moved_ptrs:
    assert l not in hot_text_new, f"moved line still present in hot: {l[:60]!r}"
assert NEW_HOT102 in hot_text_new and PTR_ARCHIVED in hot_text_new and MERGED_PTR in hot_text_new
assert orig_count - len(remove) + 3 == new_count, f"line accounting: {orig_count}-{len(remove)}+3 != {new_count}"

with open(HOT, "wb") as f:
    f.write(new_hot_b)
with open(ARC, "ab") as f:
    f.write(arc_append)

print(f"hot: {orig_size}B/{orig_count}L -> {len(new_hot_b)}B/{new_count}L (removed {len(remove)} lines, +3 new)")
print(f"archive: +{len(arc_append)}B section (2 hot entries + 8 pointers verbatim)")
assert len(new_hot_b) < 10000, f"still over 10,000B line: {len(new_hot_b)}"
print(f"WATERLINE OK: hot {len(new_hot_b)}B < 10,000B line; zero-loss verified {2+8}/10 verbatim in archive")
