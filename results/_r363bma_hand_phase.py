# -*- coding: utf-8 -*-
"""r363 bm-a hand-phase resolver: CODELY.md (memory-union via r327 entry-level law,
prefix-identity failed on both sides = in-place folds) + archive 202609.md (append-log,
prefix-identity HOLDS = pure concat).

CODELY construction = OURS face (origin batch-35 canon by bm-c r113, landed first)
+ my 2 rows renumbered 35->36 (batch-number collision yield per r176 law) with
yield adjudication amendment on the r362 execution row.
Zero-loss verification per r327: every entry line of both faces in (final tree
lines + final archive lines), with disclosed renumber/amend exceptions whose
originals remain verbatim in git history (9ddf5883).

Archive construction = base + ours-suffix + mine-suffix(renumbered 35->36),
byte math asserted.
"""
import io
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
T = os.environ["TEMP"]


def rd(n):
    return open(os.path.join(T, n), "rb").read()


def git(*args, binary=False):
    p = subprocess.run(["git"] + list(args), capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {args[:3]} rc={p.returncode}: {p.stderr[:300]}")
    return p.stdout if binary else p.stdout.decode("utf-8", errors="replace")


def lines_of(b):
    return [ln for ln in b.decode("utf-8").splitlines() if ln.strip()]


# ---------- archive (append-log, prefix-identity holds) ----------
arch_base, arch_ours, arch_mine = rd("r363_archive_base.md"), rd("r363_archive_ours.md"), rd("r363_archive_mine.md")
assert arch_ours.startswith(arch_base), "archive ours prefix broken"
assert arch_mine.startswith(arch_base), "archive mine prefix broken"
suf_ours = arch_ours[len(arch_base):]
suf_mine = arch_mine[len(arch_base):]

old_h = "## 坑律归档 2026-09-27 三十五批（r362 bm-a·CODELY.md 超 10KB 硬线（10,322B）当窗整编·行级零丢失）".encode("utf-8")
new_h = "## 坑律归档 2026-09-27 三十六批（r362 bm-a·CODELY.md 超 10KB 硬线（10,322B）当窗整编·行级零丢失·同窗撞批号让号 r176 律：三十五批号 origin bm-c r113 已占）".encode("utf-8")
old_c = "三十五批记录：上列 20 行=".encode("utf-8")
new_c = "三十六批记录：上列 20 行=".encode("utf-8")
assert suf_mine.count(old_h) == 1, f"header count {suf_mine.count(old_h)}"
assert suf_mine.count(old_c) == 1, f"closing count {suf_mine.count(old_c)}"
assert "三十五批".encode("utf-8") not in suf_mine.replace(old_h, b"@@@").replace(old_c, b"@@@"), "unexpected extra 三十五批 self-refs in mine suffix"
suf_mine_36 = suf_mine.replace(old_h, new_h).replace(old_c, new_c)

arch_new = arch_base + suf_ours + suf_mine_36
io.open("research/memory-archive/202609.md", "wb").write(arch_new)
print(f"archive: base {len(arch_base)} + ours-suffix {len(suf_ours)} + mine-suffix-36 {len(suf_mine_36)} = {len(arch_new)} (byte math {len(arch_base) + len(suf_ours) + len(suf_mine_36) == len(arch_new)})")
# zero-loss: every non-blank line of both suffixes present in final archive
final_arch_lines = set(lines_of(arch_new))
for tag, suf in [("ours", suf_ours), ("mine-36", suf_mine_36)]:
    missing = [ln for ln in lines_of(suf) if ln not in final_arch_lines]
    assert not missing, f"archive suffix {tag} lost lines: {missing[:2]}"
print("archive: suffix line coverage ours+mine-36 OK (zero-loss)")

# ---------- CODELY (memory-union, entry-level r327) ----------
cod_base, cod_ours, cod_mine = rd("r363_codely_base.md"), rd("r363_codely_ours.md"), rd("r363_codely_mine.md")
nl = b"\r\n" if b"\r\n" in cod_ours[:2000] else b"\n"


def row(txt):
    return txt.encode("utf-8").replace(b"\n", nl)


row_batch = "- 三十六批外迁（r362 bm-a·2026-09-27·超线 10,322B>10,000B 当窗整编·行级零丢失·同窗撞批号让号 r176 律：origin 三十四批=bm-b r346+三十五批=bm-c r113 已在位·本批让号取三十六）：meta 行 6+r93/r98/r99/r109/r334×2/r335×2/r341/r91/r339/r340/r342/r110 指针行 14（共 20 行）verbatim=archive 202609.md『坑律归档 2026-09-27 三十六批』节；union 面=origin 侧批次结构（r93~r110 活跃指针保留面·冗余合法零丢失律满足）+本机活跃指针 r344×2/r359/r360/r346。"
row_exec = "- [2026-09-27 23:1x r362 bm-a] 执行记录：CEO 双令 O-2026-09-27-2245（千人试用期大考）+O-2026-09-27-2250（常设律）同轮回执执行——T-94 认领即开跑（900e90eb），MASS_TRIAL_W1 预注册+语法冻结（c638f8cf·R99·seed 20283000），stage-1 初筛 975 候选→166 存活（null p95 0.533<0.60·熊门轴 36.7% vs 9.0%）；push 撞锁发现 bm-b 22:49:09 先占→§4 后到让路（产物=侧支证据·采纳 vs 取代裁决归 owner·分片要约 MSG-2335），ledger +975 计数保持；详指针=research/MASS_TRIAL_W1_PREREG.md+fleet/tasks/T-2026-09-27-94-P1.json yield_note_bm_a+progress_r362。"

cod_new = cod_ours
if not cod_new.endswith(nl):
    cod_new += nl
cod_new += row(row_batch) + nl + row(row_exec) + nl
io.open("CODELY.md", "wb").write(cod_new)
print(f"CODELY: ours {len(cod_ours)} + 2 rows = {len(cod_new)}B (hard line 10,000B: {'OK' if len(cod_new) <= 10000 else 'OVER'})")

# zero-loss verification (r327): every entry line of both faces in final tree or final archive
final_tree_lines = set(lines_of(cod_new))
ours_lines, mine_lines = lines_of(cod_ours), lines_of(cod_mine)
missing_ours = [ln for ln in ours_lines if ln not in final_tree_lines]
assert not missing_ours, f"ours lines lost from tree: {missing_ours[:3]}"
renum_35 = "- 三十五批外迁（r362 bm-a·2026-09-27·超线 10,322B>10,000B 当窗整编·行级零丢失·撞批号核（origin 三十四批=bm-b r346 已在位·本批让号取三十五））：二十七/二十六/二十九/三十/三十一/三十三批 meta 行 6+r93/r98/r99/r109/r334×2/r335×2/r341/r91/r339/r340/r342/r110 指针行 14（共 20 行）verbatim=archive 202609.md『坑律归档 2026-09-27 三十五批』节；保留=User 元律+法行 2+活跃指针 r344×2/r359/r360/r346。"
exec_orig_prefix = "- [2026-09-27 23:1x r362 bm-a] 执行记录："
missing_mine = []
for ln in mine_lines:
    if ln in final_tree_lines or ln in final_arch_lines:
        continue
    if ln == renum_35 or ln.startswith(exec_orig_prefix):
        continue  # disclosed renumber/amend exceptions; originals verbatim in git history 9ddf5883
    missing_mine.append(ln)
assert not missing_mine, f"mine lines lost from tree+archive: {missing_mine[:3]}"
print("CODELY: entry-level coverage ours 100% in tree + mine 100% in tree∪archive (2 disclosed renumber/amend exceptions in git history) OK")
assert len(cod_new) <= 10000, f"CODELY hard line breached: {len(cod_new)}"
print("ALL HAND-PHASE CONSTRUCTION OK")
