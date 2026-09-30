# r462 bm-b CODELY hot-cold reorg (D-20260924-01 / O-20260927-0230 <=10KB hard line)
# Migrate r269 + r459 pit-law rows verbatim to archive 202609.md; replace with single
# combined cold-pointer line; then append r462 new pitlaw; verify zero-loss + size.
import io, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"

src = open(CODELY, encoding="utf-8").read()
lines = src.splitlines(keepends=True)

# 1. locate the two rows (full-line, startswith match)
keys = ["- [2026-09-30 r269 bm-c] ", "- [2026-09-30 r459 bm-b] "]
migrated = []
kept = []
for ln in lines:
    if any(ln.startswith(k) for k in keys):
        migrated.append(ln)
    else:
        kept.append(ln)
assert len(migrated) == 2, f"expected 2 rows, got {len(migrated)}"

# 2. append verbatim to archive under a new section
arch = open(ARCHIVE, encoding="utf-8").read()
section = "\n## 热冷整编 2026-09-30 r462 bm-b 窗批\n\n" + "".join(migrated)
if not arch.endswith("\n"):
    arch += "\n"
arch += section + "\n（热冷整编零丢失校验：本节两行与迁移前 CODELY.md 热层逐字节恒等；整编者=bm-b r462 S4 水位律当窗动作·r462 stash-pop UU 坑律=新坑律留热层。）\n"
open(ARCHIVE, "w", encoding="utf-8", newline="").write(arch)

# 3. rebuild CODELY: insert single combined pointer line where first migrated row was,
#    then append the new r462 pitlaw at end.
pointer = ("- 冷层指针（r462 合并·指针合并归档 r444 范式）：r269 泊位反重复双洞坑+r459 嵌套账本块"
           "扫描器盲区坑两条全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r462 bm-b 窗批』节。\n")
# find index of first migrated row in original order
first_idx = next(i for i, ln in enumerate(lines) if any(ln.startswith(k) for k in keys))
kept2 = []
inserted = False
for ln in lines:
    if any(ln.startswith(k) for k in keys):
        if not inserted:
            kept2.append(pointer)
            inserted = True
        continue
    kept2.append(ln)

new_law = ("- [2026-09-30 r462 bm-b] stash-pop UU 变体坑（S0 轮首脏处理序·_r462bmb_stash_pop_marks_union.py 承载）：轮首工作树含当日 marks 日账（盘中道 tick 产物）+本机 runtime 件时，stash→pull FF→pop 三段中 **pop 段也会撞 UU**（stash 侧面 vs 刚拉 origin 同窗双写面，非 rebase 冲突=不在「转只读禁解」范围）；正解=bigmoney-conflict-resolve append-log union 配方（:2/:3 双 blob 行级 union·按 ts 排序·json.loads 逐行验证后写回·git add 清标→stash drop）。坑点=pop 输出容易被误读为 pull 冲突而误转只读轮；判别=rebase 状态面 vs stash@{N} 存在与 Unmerged paths 并存=pop 未完成态。\n")

out = "".join(kept2) + new_law
open(CODELY, "w", encoding="utf-8", newline="").write(out)

# 4. zero-loss verification: migrated rows byte-identical in archive; CODELY keeps all
#    other lines untouched (multiset compare); size check.
arch_new = open(ARCHIVE, encoding="utf-8").read()
ok_arch = all(m in arch_new for m in migrated)
src_rows = [l for l in lines if l not in migrated]
out_lines = out.splitlines(keepends=True)
# every original kept line must still be present (multiset)
from collections import Counter
c_src, c_out = Counter(src_rows), Counter(out_lines)
missing = c_src - c_out
extra = c_out - c_src
size = len(out.encode("utf-8"))
print("archive_verbatim_ok:", ok_arch)
print("missing_lines:", sum(missing.values()), "delta_new:", sum(extra.values()))
print("codely_bytes:", size, "under_10KB:", size <= 10240)
assert ok_arch and sum(missing.values()) == 0 and size <= 10240
print("REORG OK")
