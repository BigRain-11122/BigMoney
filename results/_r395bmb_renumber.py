# r395 bm-b renumber 62->63 (bm-c's 62nd pitlaw hit origin first; prior-occupancy law)
import io, os

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"

def patch(path, pairs):
    with io.open(path, "r", encoding="utf-8") as f:
        t = f.read()
    for old, new in pairs:
        assert old in t, f"NOT FOUND in {path}: {old[:60]}"
        t = t.replace(old, new, 1)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(t)
    print("patched", os.path.basename(path))

patch(os.path.join(ROOT, "research", "memory-archive", "202609.md"), [
    ("## 坑律归档 2026-09-28 六十~六十二批+晚窗执行记录批（r395 bm-b 窗·水位律当窗整编：CODELY.md 9,592B+本窗新坑律 append 即超 ≤10KB 硬线·行级零丢失校验）",
     "## 坑律归档 2026-09-28 晚窗批·执行记录+坑律补/六十/六十一/六十三批（r395 bm-b 窗·水位律当窗整编：CODELY.md 9,592B+本窗新坑律 append 即超 ≤10KB 硬线·行级零丢失校验·本机坑律 62→63 撞号让位=bm-c 62 批先在 origin）"),
    ("r395 bm-b 坑律六十二批（fuse 翻面滞后假阳",
     "r395 bm-b 坑律六十三批（撞号让位改号：本窗原计 62 批·bm-c 同窗 62 批先在 origin·后到让位·fuse 翻面滞后假阳"),
])
patch(os.path.join(ROOT, "CODELY.md"), [
    ("冷层指针：2026-09-28 晚窗批（r398-cont/r399/r175/r393/r394/r401 执行记录+坑律补/六十/六十一/六十二批）全文 verbatim=archive 202609.md『坑律归档 2026-09-28 六十~六十二批+晚窗执行记录批』节（r395 bm-b 窗水位律当窗整编·行级零丢失校验）。",
     "冷层指针：2026-09-28 晚窗批（r398-cont/r399/r175/r393/r394/r401 执行记录+坑律补/六十/六十一/六十三批）全文 verbatim=archive 202609.md『坑律归档 2026-09-28 晚窗批·执行记录+坑律补/六十/六十一/六十三批』节（r395 bm-b 窗水位律当窗整编·行级零丢失校验·本机 62→63 撞号让位=bm-c 62 批先在 origin）。"),
])
patch(os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md"), [
    ("10 条晚窗批+坑律 62 批 verbatim 入 archive 202609.md",
     "10 条晚窗批+坑律 63 批 verbatim 入 archive 202609.md(62 撞号让位=bm-c 62 批先在 origin)"),
])
patch(os.path.join(ROOT, "fleet", "machines", "bm-b.json"), [
    ("62nd pitlaw archived", "63rd pitlaw archived (renumbered: bm-c holds 62nd, prior-occupancy)"),
])
print("RENUMBER_OK")
