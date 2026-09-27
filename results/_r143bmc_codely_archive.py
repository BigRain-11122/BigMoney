# results/_r143bmc_codely_archive.py -- batch-33 hot/cold archival (bm-c r143)
# CODELY.md union 10,385B > 10KB hard line -> migrate two oldest hot entries
# (r363 bm-b / r386 bm-a) VERBATIM to research/memory-archive/202609.md,
# leave one cold-layer pointer line. Binary faces throughout (r209/r389
# line-ending law: read/write 'rb'/'wb', never text-mode newline munging).
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CP = os.path.join(ROOT, "CODELY.md")
AP = os.path.join(ROOT, "research", "memory-archive", "202609.md")

raw = open(CP, "rb").read()
lines = raw.split(b"\n")            # keep per-line bytes; endings re-joined verbatim

# locate entry blocks: line starting with b"- [" ... up to (excluding) the
# blank separator line before the next b"- [" or section header
def entry_blocks(lines):
    blocks = []          # list of (start_idx, end_idx_exclusive)
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].startswith(b"- ["):
            j = i + 1
            while j < n and not lines[j].startswith(b"- [") \
                    and not lines[j].startswith(b"##") \
                    and not lines[j].startswith(b"###"):
                j += 1
            blocks.append((i, j))
            i = j
        else:
            i += 1
    return blocks

blocks = entry_blocks(lines)


def block_text(b):
    s, e = b
    return b"\n".join(lines[s:e])


marks = {}
for b in blocks:
    t = block_text(b)
    if t.startswith(b"- [2026-09-28 06:4x r363 bm-b]"):
        marks["r363"] = b
    elif t.startswith(b"- [2026-09-28 06:3x r386 bm-a]"):
        marks["r386"] = b
assert len(marks) == 2, f"expected 2 migration targets, found {sorted(marks)}"

migrated = [block_text(marks["r363"]), block_text(marks["r386"])]

# remove blocks from lines (descending start order), including the trailing
# blank separator line that follows each block
remove = set()
for b in (marks["r363"], marks["r386"]):
    s, e = b
    for k in range(s, e):
        remove.add(k)
    if e < len(lines) and lines[e] == b"":
        remove.add(e)
new_lines = [ln for k, ln in enumerate(lines) if k not in remove]

# insert pointer line right after the batch-32 pointer line
pointer = (b"\xe5\x86\xb7\xe5\xb1\x82\xe6\x8c\x87\xe9\x92\x88\xef\xbc\x9a"
           b"\xe5\x9d\x91\xe5\xbe\x8b\xe6\xad\xa3\xe5\x85\xb8 2026-09-28 "
           b"\xe4\xb8\x89\xe5\x8d\x81\xe4\xb8\x89\xe6\x89\xb9\xef\xbc\x88r143 bm-c "
           b"\xe7\xaa\x97\xc2\xb7\xe6\xb0\xb4\xe4\xbd\x8d\xe5\xbe\x8b\xe5\xbd\x93\xe7\xaa\x97"
           b"\xe6\x95\xb4\xe7\xbc\x96\xef\xbc\x9aCODELY union 10,385B \xe8\xb6\x85 "
           b"\xe2\x89\xa410KB \xe7\xa1\xac\xe7\xba\xbf\xef\xbc\x89\xef\xbc\x9ar363 "
           b"\xe7\x9c\x9f\xe6\x95\xb0\xe6\x8d\xae\xe9\xa6\x96\xe8\xb7\x91\xe8\xbf\x9e\xe7\x8e\xaf"
           b"\xe6\x92\x9e\xe6\x8e\xa2\xe9\x92\x88\xe8\xbf\xad\xe4\xbb\xa3\xe5\xbe\x8b / r386 "
           b"hermetic fixture \xe6\x97\xb6\xe9\x97\xb4\xe6\x8e\xa8\xe8\xbf\x9b\xe9\x9d\xa2"
           b"\xe9\x9b\xb6\xe8\xa6\x86\xe7\x9b\x96 \xe4\xb8\xa4\xe6\x9d\xa1\xe5\x85\xa8\xe6\x96\x87 "
           b"verbatim=archive 202609.md\xe3\x80\x8e\xe5\x9d\x91\xe5\xbe\x8b\xe5\xbd\x92"
           b"\xe6\xa1\xa3 2026-09-28 \xe4\xb8\x89\xe5\x8d\x81\xe4\xb8\x89\xe6\x89\xb9"
           b"\xe3\x80\x8f\xe8\x8a\x82\xef\xbc\x88\xe8\xa1\x8c\xe7\xba\xa7\xe9\x9b\xb6\xe4\xb8\xa2"
           b"\xe5\xa4\xb1\xe6\xa0\xa1\xe9\xaa\x8c\xef\xbc\x89\xe3\x80\x82")
idx32 = next(k for k, ln in enumerate(new_lines)
             if ln.startswith(b"\xe5\x86\xb7\xe5\xb1\x82\xe6\x8c\x87\xe9\x92\x88")
             and b"\xe4\xb8\x89\xe5\x8d\x81\xe4\xba\x8c\xe6\x89\xb9" in ln)
new_lines.insert(idx32 + 1, b"" if new_lines[idx32 + 1] != b"" else new_lines[idx32 + 1])
# simpler: just insert pointer after idx32 (before whatever follows)
new_lines = new_lines[:idx32 + 1] + [pointer] + new_lines[idx32 + 1:]
# ensure a blank line separates pointer from following hot entry
if new_lines[idx32 + 2] != b"":
    new_lines = new_lines[:idx32 + 2] + [b""] + new_lines[idx32 + 2:]

new_codely = b"\n".join(new_lines)
# zero-loss gate: every migrated line present verbatim in archive payload
arch_raw = open(AP, "rb").read()
header = ("\n## 坑律归档 2026-09-28 三十三批（r143 bm-c 窗·水位律当窗整编："
          "CODELY union 10,385B 超 ≤10KB 硬线）\n").encode("utf-8")
payload = migrated[0] + b"\n\n" + migrated[1] + b"\n"
footer = ("\n> 迁移记录：三十三批=两条件（r363 真数据首跑连环撞探针迭代律/"
          "r386 hermetic fixture 时间推进面零覆盖）自 CODELY.md 热层 verbatim 外迁"
          "（行级零丢失校验）；热层留三十三批指针行，检索按日期段。\n").encode("utf-8")
for ln in (migrated[0].split(b"\n") + migrated[1].split(b"\n")):
    if ln and ln not in payload:
        raise SystemExit("internal: payload self-check failed")
assert b"<<<<<<<" not in new_codely and b">>>>>>>" not in new_codely
open(CP, "wb").write(new_codely)
open(AP, "ab").write(header + b"\n" + payload + footer)

# verify: size gate + line-level zero loss (each archived line byte-present)
size = os.path.getsize(CP)
arch_new = open(AP, "rb").read()
loss = 0
for blk in migrated:
    for ln in blk.split(b"\n"):
        if ln and ln not in arch_new:
            loss += 1
print(f"CODELY.md -> {size}B (<=10240: {size <= 10240})")
print(f"archive appended {len(header)+len(payload)+len(footer)}B; "
      f"line-loss count: {loss}")
assert size <= 10240 and loss == 0
