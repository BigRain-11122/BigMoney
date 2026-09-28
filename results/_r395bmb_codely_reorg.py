# r395 bm-b CODELY.md water-line hot/cold reorg (S4 law: append-crosses-10KB -> same-window reorg)
import io, os, sys

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"
CODELY = os.path.join(ROOT, "CODELY.md")
ARCH = os.path.join(ROOT, "research", "memory-archive", "202609.md")

NEW_E1 = "- [2026-09-28 19:58] r395 bm-b 执行记录：O-1755 CEO 工具链令执行+回执 O-20260928-1925-bm-b.md（本机早窗已装面幂等确认+pixel-art-studio SKILL.md 残件修复 33/33·HQ 仓=C:\\Users\\Administrator\\FluxGroup）；O-1716/1750/1925 ack（O-1750=token 常设令：需要即用禁逐次呈请、审计只查浪费）；T-110 bm-b 分片认领+venv 构建 attempt-2 在飞（attempt-1 rqalpha py3.11 无轮→回退 5.6.5 sdist 构建死·改 11 包主装+rqalpha==6.1.1 单试）；W4-JUDGE 461/461 完工实证+双文件 done 翻面（fuse count=翻面滞后假阳）+judge-finalize 脱扣在飞（48h CEO 报告钟待 finalize 起）；SENTIMENT-AXES entry done 翻面（产物 55e4c489 已 commit·fuse 同族假阳）；D-20260928-02/03 司域在树核验（bm-a r366/r388·autofill selftest ALL PASS·零重建）；S6 ~30 腿 rc=0。详情=logs/iteration-loop/round_reports.md R395 行。"
NEW_E2 = "- [2026-09-28 19:58] r395 bm-b 坑律六十二批（fuse 翻面滞后假阳·O-0947 判崩面第三例）：crash-fuse confirm 判据=「runner dead+池 shard status!=done」——runner 已完工产物已落盘、仅轮会话翻面缺位（轮空窗 17:52-19:22 实证）=假阳计崩+同版本拒重跑循环。本窗双实证：W4-JUDGE 461/461（checkpoint 19:03 完工 19:20 计崩）与 SENTIMENT-AXES（17:43 落盘且已 commit·18:10 计崩）。How to apply：轮会话 S3 必扫「本机 owner 分片产物 mtime 新于池 status=waiting」=翻面欠账，验证产物后即翻（双文件律）；fuse count 先验产物再信（r401 JUDGE-GATE 判拒计崩同族=三例定谳成类）；tick 自动翻 done 根治面暂缓=tick 无科学验证权，翻面义务归轮会话。"
POINTER = "冷层指针：2026-09-28 晚窗批（r398-cont/r399/r175/r393/r394/r401 执行记录+坑律补/六十/六十一/六十二批）全文 verbatim=archive 202609.md『坑律归档 2026-09-28 六十~六十二批+晚窗执行记录批』节（r395 bm-b 窗水位律当窗整编·行级零丢失校验）。"
SECTION = "\n## 坑律归档 2026-09-28 六十~六十二批+晚窗执行记录批（r395 bm-b 窗·水位律当窗整编：CODELY.md 9,592B+本窗新坑律 append 即超 ≤10KB 硬线·行级零丢失校验）\n"

with io.open(CODELY, "r", encoding="utf-8") as f:
    lines = f.read().split("\n")
moved = [l for l in lines if l.startswith("- [2026-09-28 ")]
assert len(moved) == 10, f"expected 10 entries to move, got {len(moved)}: {[l[:40] for l in moved]}"
assert all(l in lines for l in moved)
kept = [l for l in lines if not l.startswith("- [2026-09-28 ")]

# append archive section: verbatim moved lines (original order) + 2 new entries
with io.open(ARCH, "a", encoding="utf-8", newline="") as f:
    f.write(SECTION)
    for l in moved:
        f.write(l + "\n")
    f.write(NEW_E1 + "\n")
    f.write(NEW_E2 + "\n")

# rewrite CODELY.md: kept lines + new pointer at end
out = kept[:]
if out and out[-1].strip() != "":
    out.append("")
out.append(POINTER)
with io.open(CODELY, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(out))

# zero-loss verification: every moved byte-line exists verbatim in archive
with io.open(ARCH, "r", encoding="utf-8") as f:
    arch_txt = f.read()
missing = [l for l in moved + [NEW_E1, NEW_E2] if l not in arch_txt]
assert not missing, f"ZERO-LOSS FAIL: {len(missing)} lines missing"
print("ZERO_LOSS_OK moved=", len(moved), "+new=2")
print("CODELY_bytes=", os.path.getsize(CODELY), "ARCH_bytes=", os.path.getsize(ARCH))
