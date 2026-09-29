# r448 bm-a CODELY waterline operation: append r448 pit law + migrate r441 entry verbatim to archive (line-level zero-loss verified)
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
ARCHIVE = os.path.join(ROOT, "research", "memory-archive", "202609.md")
HARD_LINE = 10240  # 10KB

R441_PREFIX = "- [2026-09-29 21:1x r441 bm-b]"
POINTER = ("-冷层指针：r441 泊位种子撞带竞态活处理律全文 verbatim=archive 202609.md"
           "『热冷整编 2026-09-29 r448 bm-a 窗批』节（法面双载=T-123 spec+W12 draft ⑤收编清单）。")
NEW_ENTRY = (
    "- [2026-09-29 22:5x r448 bm-a] 账本外写者吞行坑+对账律机械化（r442 族四犯面）：r446 修复后 75 行面在 21:23-21:40 窗被外部写者"
    "（多写者 stale 覆写：风暴窗/云同步镜像任一）静默打回 71 行旧版，r447 pre-pull 吸收 commit 盲扫入树=A10-A13 四行二度蒸发；"
    "「轮报告宣称修复」≠「修复在树上」——吸收脏树 commit 前必须跑账本 tripwire。正法=①blob union 重建（r446 律·"
    "results/_r448bma_attrition_restore.py）②机械化=scripts/attrition_ledger_guard.py（work⊇HEAD+历史单调不减·"
    "exit 1=ACTIVE LOSS 禁 commit·adjudicated 白名单=bm-b r295 CN_TREND 去重禁回填）③已接线 Tools/iteration_prompt.txt"
    " S7 提交纪律前=全机常设。指针=results/_attrition_guard_scan.json。"
)

lines = io.open(CODELY, encoding="utf-8").read().splitlines(keepends=True)
r441_idx = [i for i, ln in enumerate(lines) if ln.startswith(R441_PREFIX)]
assert len(r441_idx) == 1, f"r441 line found x{len(r441_idx)}"
r441_line = lines[r441_idx[0]]
assert r441_line.endswith("\n"), "r441 line lacks newline"

# 1) archive the r441 line verbatim
arch = io.open(ARCHIVE, encoding="utf-8", mode="a", newline="")
arch.write("\n## 热冷整编 2026-09-29 r448 bm-a 窗批（CODELY.md 9,991B+新坑律行预超 ≤10KB 硬线·r441 条 verbatim 迁入·行级零丢失校验）\n\n")
arch.write(r441_line)
arch.close()

# 2) swap pointer line in place of the migrated entry
lines[r441_idx[0]] = POINTER + "\n"

# 3) append the new r448 entry at file end
if not lines[-1].endswith("\n"):
    lines[-1] += "\n"
lines.append(NEW_ENTRY + "\n")

out = "".join(lines)
with io.open(CODELY, "w", encoding="utf-8", newline="") as fh:
    fh.write(out)

# verification
new_codely = io.open(CODELY, encoding="utf-8").read()
assert r441_line in new_codely, "FATAL: migrated line still in CODELY"
arch_tail = io.open(ARCHIVE, encoding="utf-8").read()
assert r441_line in arch_tail, "FATAL: migrated line NOT verbatim in archive (zero-loss violated)"
size = os.path.getsize(CODELY)
print(f"CODELY size: {size}B (hard line {HARD_LINE}) {'OK under line' if size <= HARD_LINE else 'OVER LINE -- must re-arch in-window'}")
assert size <= HARD_LINE, "waterline violation"
print("zero-loss: r441 verbatim archived + absent from hot; pointer + new r448 entry landed")
