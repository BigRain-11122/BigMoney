"""r308 bm-b: CODELY.md kenglu append + same-window hot/cold repack (O-20260927-0230 hard line).

- Append 1 new kenglu (autofill_state transient read-tear class, r308 live-fire).
- 10030B + append > 10KB hard line -> move 2 pure flow-record lines (集团令台账 /
  坑律归档二批) verbatim to research/memory-archive/202609.md '三批' section
  (line-level zero loss); standing laws (≤10KB 硬线律·D-05③ marker-check) stay hot.
- Verify: CODELY <= 10240B; moved lines byte-identical in archive & absent in CODELY.
"""
import json, datetime

CODELY = "CODELY.md"
ARCH = "research/memory-archive/202609.md"
EV = "results/_r308bmb_codely_repack.json"
now = datetime.datetime.now().astimezone().isoformat()

NEW = "- [2026-09-27 07:4x r308 bm-b] 坑律：autofill tick 的「corrupt autofill_state」ABORT 可为**瞬态读撕裂**——tick 读共享态恰逢 git 换文件（rebase/stash-pop/commit 面同名替换）即见半文件，r201 refuse-wipe 正确自愈（07:30:03 ABORT→07:41:58 下 tick 干净 no-op 实证）；正典=控制面修复手术前必先复检当前盘面 json.loads（r308 修复探针 NO_OP_DISK_VALID 零手术落证），连续两 tick 皆红才动刀，禁信 tick 日志单源定性。指针=results/_r308bmb_autofill_state_repair.py+json+logs/autofill.log 07:30:03/07:41:58 行"

MOVE_PREFIXES = ("- 集团令台账：", "- 坑律归档二批")

src = open(CODELY, encoding="utf-8").read()
lines = src.splitlines()
moved = [l for l in lines if any(l.startswith(p) for p in MOVE_PREFIXES)]
assert len(moved) == 2, "expected exactly 2 move lines, got %d" % len(moved)

out_lines = []
inserted = False
for l in lines:
    if any(l.startswith(p) for p in MOVE_PREFIXES):
        continue
    out_lines.append(l)
    if l.strip() == "### Project" and not inserted:
        out_lines.append(NEW)
        inserted = True
assert inserted, "Project section anchor not found"
new_src = "\n".join(out_lines) + "\n"

hdr = "## 坑律归档三批 2026-09-27 r308 bm-b（O-20260927-0230 ≤10KB 硬线续执行·2 流水面外迁·行级零丢失·指针字段检索）"
arch = open(ARCH, encoding="utf-8").read()
if not arch.endswith("\n"):
    arch += "\n"
arch_new = arch + hdr + "\n" + moved[0] + "\n" + moved[1] + "\n"

# zero-loss + size gates
for m in moved:
    assert m in arch_new, "moved line missing verbatim in archive"
    assert m not in new_src, "moved line still in CODELY"
assert NEW in new_src
nb = len(new_src.encode("utf-8"))
assert nb <= 10240, "CODELY still over 10KB: %d" % nb

open(CODELY, "w", encoding="utf-8", newline="\n").write(new_src)
open(ARCH, "a", encoding="utf-8", newline="\n").write(hdr + "\n" + moved[0] + "\n" + moved[1] + "\n")

chk = open(CODELY, encoding="utf-8").read()
ev = {
    "ts": now,
    "codely_bytes_before": len(src.encode("utf-8")),
    "codely_bytes_after": len(chk.encode("utf-8")),
    "codely_lines_before": len(lines),
    "codely_lines_after": len(chk.splitlines()),
    "moved_count": len(moved),
    "moved_prefixes": [m[:28] for m in moved],
    "archive_section": hdr,
    "gates": "CODELY<=10240 PASS; moved verbatim in archive PASS; absent in CODELY PASS; new kenglu present PASS",
}
json.dump(ev, open(EV, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(ev, ensure_ascii=False))
