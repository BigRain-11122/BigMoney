# -*- coding: utf-8 -*-
"""r407 bm-a hot-cold reconsolidation: CODELY.md 11,959B >10KB hard line.
Migrate oldest 3 pitlaw batches (r400 / r189-70 / r191-71) verbatim to
research/memory-archive/202609.md, replace with one pointer line, append
batch-73 (probe-basis verbatim law). Line-level zero-loss verification."""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
ARCHIVE = os.path.join(ROOT, "research", "memory-archive", "202609.md")
CRLF = "\r\n"

targets = [
    "- [2026-09-28 23:4x] r400 bm-b",
    "- [2026-09-29 00:4x] r189 bm-c",
    "- [2026-09-29 01:3x] r191 bm-c",
]

with io.open(CODELY, encoding="utf-8", newline="") as fh:
    raw = fh.read()
lines = raw.split(CRLF)
if lines and lines[-1] == "":
    lines = lines[:-1]

idxs = []
for t in targets:
    hit = [i for i, l in enumerate(lines) if l.startswith(t)]
    assert len(hit) == 1, f"target not unique/absent: {t} -> {hit}"
    idxs.append(hit[0])
assert idxs == sorted(idxs), f"order unexpected: {idxs}"

migrated = [lines[i] for i in idxs]

batch73 = (
    "- [2026-09-29 01:5x] r407 bm-a 坑律七十三批（预注册锚交叉表必须探针基逐字复算·禁复用语法层门函数）："
    "W5 generate 双静默死（r406+r407 两次 autofill launch 均无痕亡·无 checkpoint 无产物）诊断=前台复跑截 stdout："
    "①`_yang_face_full` 对 open 列做 datetime 标签 reindex 时 open 仍持 RangeIndex→全 NaN→na_window==n_bars 健康面板假拒；"
    "②交叉表复用 tl3 `gate_state_series`（min_periods=200 预热窗 gate-closed=既非 bull 亦非 bear）而 r162 探针基是"
    "`map({True:bull,False:bear})` 的 False 腿**把 199 bar 预热窗归入 bear**（bear 天数 1,703=全窗 3,483−1,780）"
    "→red∧bear 812 vs 冻结锚 914（102 bar 差=预热窗内 red 日）。How to apply：预注册锚定的派生统计"
    "（交叉表/条件率/计数锚）一律**按探针代码逐字复算**（探针件=prereg 基准 face 的权威定义），"
    "禁拿语义相近的引擎/语法层函数代算——同一统计量在「预热窗/NaN 窗如何归类」上的差=健康面板必红假拒"
    "（r398 面刻度家族第二次实证）；门锚本身永不改（fail-closed 照旧），修的是复算面不是判线。"
    "另：autofill launch 无 stderr 捕获=烧批死因黑洞，秒死批先前台复跑截输出再谈修复。"
)

pointer = (
    "冷层指针：坑律正典 r400 bm-b（S0 冲突降级轮 playbook·三活实证）+r189 bm-c 七十批（状态行权威律+取模相位值域坑）"
    "+r191 bm-c 七十一批（崩确认窗连发坑·同版本 relaunch 冷却律）全文 verbatim=archive 202609.md"
    "『坑律归档 2026-09-29 r407 bm-a 窗批』节（r407 bm-a 窗水位律当窗整编·行级零丢失校验）。"
)

sec_head = "## 坑律归档 2026-09-29 r407 bm-a 窗批"
sec_note = (
    "（r407 bm-a 窗水位律当窗整编：CODELY.md hot 层 11,959B 超 ≤10KB 硬线；本批新坑律七十三批入册后，"
    "最老三条（r400/r189 七十批/r191 七十一批）verbatim 外迁本节，行级零丢失校验。）"
)

with io.open(ARCHIVE, encoding="utf-8", newline="") as fh:
    arc_raw = fh.read()
arc_lines = arc_raw.split(CRLF)
if arc_lines and arc_lines[-1] == "":
    arc_lines = arc_lines[:-1]
arc_lines += ["", sec_head, sec_note] + migrated + [""]

# replace: first migrated index -> pointer; drop the rest
for k, i in enumerate(sorted(idxs)):
    if k == 0:
        lines[i] = pointer
    else:
        lines[i] = None
lines = [l for l in lines if l is not None]
if lines and lines[-1].startswith("- [2026-09-29 01:5x] r406 bm-a 坑律七十一批补"):
    lines += ["", batch73]
else:
    lines += ["", batch73]

new_codely = CRLF.join(lines) + CRLF
new_archive = CRLF.join(arc_lines) + CRLF
with io.open(CODELY, "w", encoding="utf-8", newline="") as fh:
    fh.write(new_codely)
with io.open(ARCHIVE, "a", encoding="utf-8", newline="") as fh:
    pass  # already rewritten via arc_lines? no -- rewrite below
with io.open(ARCHIVE, "w", encoding="utf-8", newline="") as fh:
    fh.write(new_archive)

# zero-loss verification
chk_codely = io.open(CODELY, encoding="utf-8", newline="").read()
chk_archive = io.open(ARCHIVE, encoding="utf-8", newline="").read()
missing = [t for t in migrated if t not in chk_archive]
dup_hot = [t for t in migrated if t in chk_codely]
sz = os.path.getsize(CODELY)
arc_contains_all = all((t in chk_archive) for t in targets)
print("migrated_lines:", len(migrated))
print("zero_loss_in_archive:", not missing)
print("removed_from_hot:", not dup_hot)
print("new_codely_bytes:", sz)
print("under_10KB:", sz <= 10240)
print("batch73_in_hot:", batch73 in chk_codely)
print("pointer_in_hot:", pointer in chk_codely)
print("archive_contains_targets:", arc_contains_all)
print("archive_bytes:", os.path.getsize(ARCHIVE))
sys.exit(0 if (not missing and not dup_hot and sz <= 10240 and batch73 in chk_codely) else 2)
