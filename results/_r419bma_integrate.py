"""r419 bm-a — CODELY.md water-level integration (水位律当窗整编, <=10KB hard line).

Union landed at 11,362B > 10KB -> collapse the 2026-09-28 dated 冷层指针 index
lines into ONE combined pointer line per r173 precedent (24 old pointer lines
merged to one, batch content zero-deletion). Archive holds all content.
"""
import re

C = "CODELY.md"
text = open(C, encoding="utf-8").read()
lines = text.split("\n")
pat = re.compile(r"冷层指针.*2026-09-28|2026-09-28.*冷层指针")
hits = [i for i, ln in enumerate(lines) if pat.search(ln)]
print(f"collapse targets: {len(hits)} lines, {[len(lines[i].encode('utf-8')) for i in hits]}B")
assert 5 <= len(hits) <= 8, "unexpected collapse set size"
removed = [lines[i] for i in hits]
first = hits[0]
combined = ("冷层指针：坑律归档 2026-09-28 各窗老批指针合并行（r419 bm-a 窗按 r173 范式合并："
            "25~57 批+五十八批+晚窗批·执行记录+坑律补/六十/六十一/六十三批+六十二/六十四/"
            "六十五/六十六批+r397 批三面教训+r398 定谳+r182 回执+六十七/六十八/六十九批+r403 执行记录"
            "+r187 判定回执+国家队接口正面知识）各批全文 verbatim=archive 202609.md 对应"
            "『坑律归档 2026-09-28 <各节>』『坑律归档 2026-09-29 r189/r183 bm-c 窗批』节"
            "（五十九批 G-REPRO 双坑=research/DECISION_CHAIN_V2_PREREG.md a6 append-only 节）——"
            "批内容零删零改动（2026-09-29 r419 bm-a 水位律当窗整编）。")
# verify every collapsed line is a pointer INTO a canonical file
for ln in removed:
    assert ("verbatim=" in ln) or ("archive 202609.md" in ln), f"non-pointer collapsed: {ln[:50]!r}"
new_lines = [combined if i == first else None for i in range(len(lines))]
new_lines = [(combined if i == first else lines[i]) for i in range(len(lines))
             if i not in set(hits) or i == first]
# dedupe consecutive blanks introduced by removals
out, prev_blank = [], False
for ln in new_lines:
    blank = (ln.strip() == "")
    if blank and prev_blank:
        continue
    out.append(ln)
    prev_blank = blank
new = "\n".join(out)
open(C, "w", encoding="utf-8", newline="").write(new)
nb = len(new.encode("utf-8"))
print(f"integrated: {len(text.encode('utf-8'))}B -> {nb}B (<=10KB hard line: {nb <= 10240})")
assert nb <= 10240, "still over hard line"
# content zero-loss: every non-collapsed, non-blank original line still present
kept = set(l for l in lines if l.strip() and l not in removed)
for ln in kept:
    assert ln in new, f"lost: {ln[:50]!r}"
print("kept-lines zero-loss check OK; collapsed pointer lines ->", len(removed))
