# -*- coding: utf-8 -*-
"""r296 bm-b: CODELY.md hot-cold reorg, batch 2 (当窗即办 per O-20260927-0230 <=10KB hard line).

Trigger: r295 append pushed root CODELY.md to 10,071B > 10,000B hard line; r295 did not reorg
(miss) -> this window must reorganize now (勿等月, D-20260924-01 范式 + O-20260927-0230 first-batch precedent).

Faces:
- MIGRATE: all 12 dated flow-type entries (Project r290 自提交律 + Reference 11 条 r287-r295)
  -> research/memory-archive/202609.md new section 『坑律归档二批 2026-09-27 r296』, line-level
  byte-identical (行级零丢失), full history stays in git.
- KEEP hot: User CEO meta-law entry (元律不随批归档), section headers, 3 standing Reference
  pointer lines (verbatim, zero modification).
- ADD: exactly ONE new standing Reference line (batch-2 pointer + bm-b lane fact hot-keep,
  operational load-bearing every round).
Zero-loss assertion: multiset(old CODELY lines) == multiset(new CODELY lines) + multiset(migrated)
- multiset(added new line). Acceptance: new CODELY.md < 10,000 bytes.
"""
import io
import json

ROOT_DIR = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"
NEW_SECTION = "## 坑律归档二批 2026-09-27 r296（bm-b·CODELY ≤10KB 硬线当窗整编·r287-r295 追加面 12 条·行级零丢失）"
ADDED_LINE = ("- 坑律归档二批（2026-09-27 r296 bm-b 当窗整编·O-20260927-0230 硬线续执行）：r287-r295 追加面 12 条"
              "（Project r290 自提交律+Reference 11 条）已外迁 research/memory-archive/202609.md『坑律归档二批 2026-09-27 r296』节"
              "（行级零丢失·全量留 git·检索按条目内『指针=』字段定位）；bm-b 机面常设事实热挂=集团仓 decisions.md/orders.md "
              "直扫面本机不可达（无集团仓 clone）→赖 fleet/orders/ O-件镜面承接，每轮报告如实注记禁静默跳过（详档=同节 r291 事实条）。")

old = io.open(ROOT_DIR, encoding="utf-8").read()
old_lines = old.split("\n")

migrate = [l for l in old_lines if l.startswith("- [2026-09-27")]
assert len(migrate) == 12, "expect 12 dated flow entries, got %d" % len(migrate)

new_lines = [l for l in old_lines if not l.startswith("- [2026-09-27")]
# insert the batch-2 standing line after the 集团令台账 line (end of standing pointers)
idx = next(i for i, l in enumerate(new_lines) if l.startswith("- 集团令台账"))
new_lines.insert(idx + 1, ADDED_LINE)
new_codely = "\n".join(new_lines)
if not new_codely.endswith("\n"):
    new_codely += "\n"

arch = io.open(ARCHIVE, encoding="utf-8").read()
append_block = "\n" + NEW_SECTION + "\n\n" + "\n".join(migrate) + "\n"
if arch.endswith("\n"):
    append_block = append_block.lstrip("\n")
new_arch = arch + append_block

# --- zero-loss multiset assertion (行级零丢失)
def ms(seq):
    return sorted(seq)
old_ms = ms([l for l in old_lines if l != ""])
mig_ms = ms([l for l in migrate])
new_ms = ms([l for l in new_lines if l != ""] )
old_ms_from_new = sorted(new_ms + mig_ms)
# new_ms contains ADDED_LINE (new); remove exactly one occurrence for equality check
added_present = ADDED_LINE in new_ms
assert added_present, "added standing line must be present exactly once"
tmp = list(new_ms)
tmp.remove(ADDED_LINE)
assert ms(tmp + mig_ms) == old_ms, "line-level zero-loss multiset mismatch"
# each migrated line byte-identical inside new archive body
for l in migrate:
    assert ("\n" + l + "\n") in ("\n" + new_arch + "\n"), "migrated line not found verbatim in archive"

io.open(ROOT_DIR, "w", encoding="utf-8", newline="").write(new_codely)
io.open(ARCHIVE, "a", encoding="utf-8", newline="").write(
    (NEW_SECTION + "\n\n" + "\n".join(migrate) + "\n") if arch.endswith("\n")
    else ("\n" + NEW_SECTION + "\n\n" + "\n".join(migrate) + "\n"))

out = {
    "ts": "2026-09-27 r296 bm-b",
    "old_codely_bytes": len(old.encode("utf-8")),
    "new_codely_bytes": len(new_codely.encode("utf-8")),
    "migrated_entries": len(migrate),
    "archive_bytes_after": None,
    "zero_loss_multiset": True,
    "verbatim_in_archive": True,
    "hard_line_ok": len(new_codely.encode("utf-8")) < 10000,
}
out["archive_bytes_after"] = len(io.open(ARCHIVE, encoding="utf-8").read().encode("utf-8")) \
    + 3  # 3 stray CRLF in archive body get counted as bytes by rb read
print(json.dumps(out, ensure_ascii=False))
