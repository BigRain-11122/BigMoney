"""r486 bm-c S4: append one pit line to CODELY.md (marker-count gate per r679).

Two lessons from this round window (yield-clobber main + finalize-seat
concurrency as the same line's attached clause, r673/r674 precedent):
1. r687 file-level theirs-canonical yield merge clobbered the unrelated
   in-file r685 science_gates _quarantine fix -> phantom +6041 re-entered
   ledger_head (652,840 vs true 646,799); r486 reinstated 3 hunks verbatim
   (898f0e5c5), selftest 70/70, true head restored.
2. Wave-level judge-finalize has no pool claim face -> two machines spawned
   the same-wave finalize blind (bm-c 17:44:04 vs bm-a r688 ~17:5x re-spawn);
   resolved by live-spawn time-order (later yields, end-only writes kill is
   clean per r426) + MSG seat notice. Law: fetch-scan others' spawn markers
   before finalize spawn + MSG seat notice immediately.
"""
line = (
    "- [2026-10-04 18:0x r486 bm-c] 让路合并文件级 theirs-canonical 冲掉同文件无关已落修复坑"
    "（r687 yield a6fc0132d 把 r685 science_gates _quarantine 扫描排除〔588d4c160〕一并回退"
    "=隔离区两件 bogus W3 summary 幻影 +6041 回流链头 652,840 vs 真链头 646,799〔w3_screen §7 块内算术 641,985+4,814 恒等复核〕；"
    "r486 拾回 898f0e5c5 三 hunk 逐字+各附 reinstated 注记+selftest 70/70 含隔离腿+真链头活读复原。"
    "律=yield 取整文件 theirs 前必做 hunk 级分离（yield 判据面限本争议 hunk）或 yield 后立即复核同文件内无关在册修复在位性——commit 时间序让路律的副作用面首例）。"
    "附带=wave 级 finalize 无池认领面=双机并发盲区（bm-c 17:44:04 spawn〔真链头 caliber 在树〕与 bm-a r688 ~17:5x re-spawn 同 wave 并发盲撞，"
    "幸 MSG-1745 先落让后到者杀己收养先到产品；律=finalize spawn 前必 fetch 查他机轮报/spawn 件在飞标记+spawn 即发 MSG 席位公示，"
    "撞并发按活 spawn 时间序后到让路——cmd_judge_finalize end-only writes 中途击杀零半写面〔r426 谱系法〕，先到产品=canonical，"
    "后到已落本地件按 batch-id keep-first 去重〔r482 律〕勿双块入链）。\n"
)
p = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md"
b = open(p, "rb").read()
assert b.count(b"[2026-10-04 18:0x r486 bm-c]") == 0, "marker already present (r679 idempotence)"
if not b.endswith(b"\n"):
    b += b"\n"
open(p, "ab").write(line.encode("utf-8"))
nb = open(p, "rb").read()
assert nb.count(b"[2026-10-04 18:0x r486 bm-c]") == 1, "append not unique"
print("CODELY appended, size:", len(nb))
