# -*- coding: utf-8 -*-
"""R287 bm-a: CODELY.md <=10KB hot-cold refile per group order O-20260927-0230-bm-a.

Byte-exact move: all 坑律 entries (everything after the 冷层指针 line) go to
research/memory-archive/202609.md (D-20260924-01 mechanism, line-level zero-loss),
CODELY.md keeps header + User 元律 + 冷层指针 + new archive pointer lines.
"""
import io, os, sys

CODELY = "CODELY.md"
ARCHIVE = os.path.join("research", "memory-archive", "202609.md")

raw = open(CODELY, "rb").read()
lines = raw.split(b"\n")
# locate the 冷层指针 line (the last line of the keep-part)
COLD_MARK = "- \u51b7\u5c42\u6307\u9488".encode("utf-8")  # 冷层指针
cold_idx = None
for i, ln in enumerate(lines):
    if ln.startswith(COLD_MARK):
        cold_idx = i
if cold_idx is None:
    sys.exit("FATAL: 冷层指针 anchor line not found")

keep_bytes = b"\n".join(lines[: cold_idx + 1])
move_bytes = b"\n".join(lines[cold_idx + 1:])
# strip pure blank lead-ins from the move block but keep them counted (they are separators)
n_entries = sum(1 for ln in lines[cold_idx + 1:] if ln.strip().startswith(b"-"))

# archive append: probe trailing newline first (R281 law)
arc_raw = open(ARCHIVE, "rb").read()
sep = b"" if (not arc_raw or arc_raw.endswith(b"\n")) else b"\n"
header = (
    "\n## 坑律归档 2026-09-27（集团令 O-20260927-0230-bm-a·CODELY ≤10KB 热冷整编·行级零丢失·自 CODELY.md Reference 节原样外迁）\n\n"
).encode("utf-8")
with open(ARCHIVE, "wb") as f:
    f.write(arc_raw + sep + header + move_bytes)

new_ref = (
    "\n\n- 坑律正典全量归档（2026-09-27 集团令 O-20260927-0230-bm-a·CODELY ≤10KB 整编）：全部坑律条目已外迁 research/memory-archive/202609.md『坑律归档 2026-09-27』节（行级零丢失·全量留 git·检索按条目内『指针=』字段定位）；新坑律仍先入本件，**≤10KB 硬线**——append 后超线=当窗即办热冷整编勿等月（水位律自 >50KB 重锚·集团令优先）。\n"
    "- 集团令台账：fleet/orders/O-20260927-0230-bm-a.md（集团 orders.md L45 承接·CODELY ≤10KB·已执行·判据=字节落线）；根 CODELY.md ≤20KB 为 @HQ 面。\n"
).encode("utf-8")
with open(CODELY, "wb") as f:
    f.write(keep_bytes + new_ref)

# verify
c2 = open(CODELY, "rb").read()
a2 = open(ARCHIVE, "rb").read()
checks = {
    "codely_bytes": len(c2),
    "codely_le_10kb": len(c2) <= 10240,
    "archive_delta_eq_move": len(a2) - len(arc_raw) - len(sep) - len(header) == len(move_bytes),
    "moved_entries": n_entries,
    "moved_bytes": len(move_bytes),
    "sections_present": all(s.encode() in c2 for s in ["### User", "### Feedback", "### Project", "### Reference"]),
    "cold_pointer_kept": "\u51b7\u5c42\u6307\u9488".encode("utf-8") in c2,
    "user_yuanlv_kept": "\u5b9e\u6218\u51fa\u771f\u77e5".encode("utf-8") in c2,
}
print(checks)
ok = all(v for k, v in checks.items() if isinstance(v, bool))
print("ALL_OK" if ok else "FAIL")
sys.exit(0 if ok else 1)
