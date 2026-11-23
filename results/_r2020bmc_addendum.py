"""Append the r2020 addendum row: delivery receipt + the r2019 never-landed finding."""
import io

ROW = (
    "| 2026-11-24 02:5x | r2020 **addendum**（送达核验 + 一处必须说清的发现） | commit **f19ef1eae5** "
    "已推 origin/main（a0508443a4..f19ef1eae5），fetch 后 **AHEAD=0 / BEHIND=0**，`git ls-tree -r origin/main` "
    "**十件 blob 全在位**（本轮六件 scripts/two_book_blend.py / results/two_book_blend.json / "
    "research/TWO_BOOK_BLEND.md / 负控 results/_r2020bmc_blend_negative.py / 收口 _r2020bmc_round_report.py 与 "
    "_r2020bmc_hb_fields.json，`_r[0-9]*` 走 `git add -f` 既有惯例；**外加 r2019 四件**，见下）→ "
    "**本地未达 origin commit 数=0**。**发现（本轮实弹·交付核对律第二次咬人）**：提交前查 `git ls-tree -r "
    "origin/main` 时发现 **r2019 的四件从未上链**——scripts/astock_veto_smooth_rank.py、"
    "results/astock_veto_smooth_rank.json、research/ASTOCK_VETO_SMOOTH_RANK.md、"
    "results/_r2019bmc_smooth_rank_negative.py 只在本地 index 里 staged 着，而当时 HEAD 仍是 round 2018 的 "
    "簿记 commit（a0508443a4）；r2019 那行只写到「本地未达 origin commit 数＝推送后复核」就停了，**没有 addendum**。"
    "这正是 r1939 判例族（「pushed by loop 类断言必须 fetch 后以 reflog+ls-tree 实证」）的又一实锚："
    "跑过、写过、staged 过，都不等于上链。**处置**：不丢弃、也不盲带——先跑它们自己的门复核完整性"
    "（`astock_veto_smooth_rank.py check` **rc0**，slices=77 / anchor ok=True / K=2,3 SMOOTHING_COSTS、"
    "K=4 SMOOTHING_NOT_SEPARABLE；负控 **34/34 PASS**），确认不是半成品，再原样代投，内容零改动，"
    "commit message 单列一节说明来由。**教训一句**：轮次的「已推」结论只能由 origin 回答，不能由本地 "
    "index 或上一份报告回答；顺带说明为何要保留 staged——按 r1907「暂存即活」，若本窗做 `git add -A` 之外的"
    "任何索引清理，这四件就静默丢了。记账：本行 1 处（轮报告 addendum）。|\n"
)

path = "fleet/round_reports-bm-c.md"
with io.open(path, "rb") as f:
    raw = f.read()
need_nl = raw and not raw.endswith(b"\n")
with io.open(path, "a", encoding="utf-8", newline="") as f:
    if need_nl:
        f.write("\n")
    f.write(ROW)
print("appended %d chars; need_nl=%s" % (len(ROW), need_nl))
