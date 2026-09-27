# r328 bm-a: CODELY.md over-line in-window archival (十六批) per ≤10KB hard law
import io, os

LIVE = "CODELY.md"
ARCH = "research/memory-archive/202609.md"

live = io.open(LIVE, encoding="utf-8").read()
arch = io.open(ARCH, encoding="utf-8").read()

# the 3 oldest live entries (pre-14:00 window) -- matched by their leading stamps
STAMPS = [
    "- [2026-09-27 13:3x r83 bm-c]",
    "- [2026-09-27 13:5x r327 bm-b]",
    "- [2026-09-27 13:4x r326 bm-a]",
]
lines = live.splitlines()
removed, kept = [], []
for ln in lines:
    if any(ln.startswith(s) for s in STAMPS):
        removed.append(ln)
    else:
        kept.append(ln)
assert len(removed) == 3, "expected exactly 3 entries, got %d" % len(removed)

# verbatim append to archive as 十六批 (行级零丢失)
sec = "十六批外迁（r328 bm-a·rebase 撞窗水位律当窗整编）"
assert sec not in arch, "batch section already exists"
crlf_arch = "\r\n" in arch
block = "\n\n## 坑律归档 2026-09-27——%s\n\n" % sec + "\n\n".join(removed) + "\n"
arch2 = arch if arch.endswith("\n") else arch + "\n"
arch2 += block
with io.open(ARCH, "w", encoding="utf-8", newline="") as f:
    f.write(arch2)

# remove from live + update pointer line (batch enumeration)
live2 = "\n".join(kept) + ("\n" if live.endswith("\n") else "")
old_ptr_tail = "（r85 勘注：两机同窗各编一批『十五批』——bm-a r327 面=四~十四批索引折叠归档、r84 bm-c 面=r321/r323/r82/r325 条目外迁，归档侧两『十五批』节并存零覆盖；后续新批自十六批起编。）"
new_ptr_tail = old_ptr_tail + "十六批外迁（r328 bm-a·rebase 撞窗水位律当窗整编）：r83 配方表覆盖面核对/r327bmb town.html 面板同步/r326bma pandas asi8 单位坑=归档十六批节·行级零丢失。"
assert old_ptr_tail in live2
live2 = live2.replace(old_ptr_tail, new_ptr_tail)
with io.open(LIVE, "w", encoding="utf-8", newline="") as f:
    f.write(live2)

# verify: zero loss (removed lines present in archive byte-for-byte), size under line
arch_now = io.open(ARCH, encoding="utf-8").read()
for ln in removed:
    assert ln in arch_now, "archived line missing: %s" % ln[:60]
    assert ln not in live2, "live still contains: %s" % ln[:60]
sz = os.path.getsize(LIVE)
print("archived 3 entries verbatim; live size now:", sz, "(limit 10240)",
      "OK" if sz <= 10240 else "STILL OVER")
