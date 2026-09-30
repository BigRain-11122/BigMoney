"""_r455bmb_codely_reorg.py -- hot-cold re-arch tripped by 10KB hard line (r455 S4).

CODELY.md at 9,950B; appending the r455 futures-gate entry would cross the
<=10KB hard line -> same-window re-arch per O-20260927-0230 law.
Moves 3 coldest hot entries verbatim to archive 202609.md, leaves one
pointer line (r444 paradigm), appends the new hot entry, byte-verifies
zero-loss.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"

MOVE_PREFIXES = [
    "- [2026-09-30 r261 bm-c] rebase --continue 幻影拒走坑",
    "- [2026-09-30 r261 bm-c] 判决落地即同窗 done-flip 止损 churn 律",
    "- [2026-09-30 05:5x r254 bm-c] push 假拒绝坑",
]

POINTER = ("- 冷层指针（r455 合并·指针合并归档 r444 范式）：r261 rebase --continue 幻影拒走坑（脏树幻报冲突·正法=ls-files -u 验零→add 脏态件→continue）"
           "+r261 判决落地即同窗 done-flip 止损 churn 律（ready 滞留>20min 撞 r450 守卫·判决观测轮即翻面）"
           "+r254 push 假拒绝坑（reflock 竞态·先 fetch 验 origin 落点再重试禁盲 rebase）三条全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r455 bm-b 窗批』节。\n")

NEW_HOT = ("- [2026-09-30 r455 bm-b] update_futures 门 no-op≠全腿新鲜读坑：local_data_cutoff()=VARIETIES（9 员）MAX 聚合——任一员新鲜即门闭，"
           "单员滞后被掩蔽永不重拉（本窗实读 9/9 员齐 09-29 健康·零事故·掩蔽面=latent）；TS=一次性腿不在 VARIETIES（bm-a T-65 s2 专拉止 09-24·"
           "hold 列≠oi 已由 CTA_WAVE1 冻结件裁定 OHLCV-only）——读期货面板禁以「cutoff covered no-op」推 10/10 新鲜；修面（min 门/逐员 stale-leg 重拉）"
           "=bm-a R48/R51 车道观察件 results/_r455bmb_futures_gate_probe.json 承载。\n")

with open(CODELY, "r", encoding="utf-8") as f:
    lines = f.read().splitlines(keepends=True)

moved, kept = [], []
for ln in lines:
    if any(ln.startswith(p) for p in MOVE_PREFIXES):
        moved.append(ln)
    else:
        kept.append(ln)
assert len(moved) == 3, f"expected 3 move targets, found {len(moved)}"

# insert pointer where the first moved entry lived (scan kept for anchor:
# the two r261 entries sat right after the r261-merge cold pointer line)
idx = next(i for i, ln in enumerate(kept) if ln.startswith("- 冷层指针（r261 合并"))
kept.insert(idx + 1, POINTER)

with open(CODELY, "w", encoding="utf-8", newline="") as f:
    f.writelines(kept)
with open(CODELY, "a", encoding="utf-8", newline="") as f:
    f.write(NEW_HOT)

# archive append: verbatim section + zero-loss footer
section = "\n## 热冷整编 2026-09-30 r455 bm-b 窗批\n\n" + "".join(moved) + "\n（热冷整编零丢失校验：本节三行与迁移前 CODELY.md 热层逐字节恒等；整编者=bm-b r455 S4 水位律当窗动作。\n）\n"
with open(ARCHIVE, "a", encoding="utf-8", newline="") as f:
    f.write(section)

# verify zero-loss: each moved line verbatim in archive
arch = open(ARCHIVE, "r", encoding="utf-8").read()
ok = all(m in arch for m in moved)
size = len(open(CODELY, "r", encoding="utf-8").read().encode("utf-8"))
print("moved:", len(moved), "| zero-loss:", ok, "| CODELY bytes now:", size, "| under-10KB:", size <= 10240)
