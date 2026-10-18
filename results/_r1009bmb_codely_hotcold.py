"""r1009 bm-b: CODELY.md hot-cold reorg + new pit entry landing.

Law: O-20260927-0230 header law (<=10KB hard line, same-window reorg on
breach), D-20260924-01 pattern, r1047/r1062 precedents. prescan rc3 =
registry hit, authorized migration face per TREASURE_PROTECTION_LAW s2
(memory/pit-law class, verbatim move + pointer backfill, zero-loss).

Surgery:
  1. Move 4 cold rows verbatim -> research/memory-archive/202610.md new
     section '热冷整编 2026-10-18 r1009 bm-b 窗批' (r1089 d19 single-face
     superseded-by-r1090-in-tool row, r1091 W268 editor row, r1093
     fivekeys row, r1093 autocrlf row).
  2. Backfill 4 compact pointer lines in place (operational essence hot).
  3. Append the r1008 window's new pit entry (rebase-continue
     GHOST-REFUSAL + stash-pop index poison + per-machine-keyed union).
  4. Receipt with before/after sizes, moved-row byte identity, prescan
     verdict (re-run in-script, capture_output per r1045 law).
EOL: detect and preserve (autocrlf smudge face, r1093 law). Pure ASCII
source (repo law); CJK content passes through as UTF-8 bytes untouched.
"""
import hashlib
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(REPO, "CODELY.md")
ARCHIVE = os.path.join(REPO, "research", "memory-archive", "202610.md")
RECEIPT = os.path.join(REPO, "results", "_r1009bmb_codely_hotcold_receipt.json")

MARKERS = [
    "- [2026-10-18 12:4x r1089 bm-c] **d19 水位推进单面写坑",
    "- [2026-10-18 14:1x r1091 bm-c] **W268 编辑器出稿双坑",
    "- [2026-10-18 16:0x r1093 bm-c] **fivekeys 锚精度坑",
    "- [2026-10-18 16:0x r1093 bm-c] **bm-c 仓 core.autocrlf",
]

POINTERS = [
    "- 冷层指针：d19 update --advance 单面写坑已 r1090 焊双面自愈（update 同窗写 state+heartbeat 镜像·本机 r1009 实弹证实 mirrors synced 3）；--receipt 语义坑（=工具运行回执输出路径·误传判断件会被覆写）+手动镜像同步律全文=archive 202610.md『热冷整编 2026-10-18 r1009 bm-b 窗批』节。",
    "- 冷层指针：W268 编辑器出稿双坑（canon 折行断言面 needle 一律拆短+derive gone 清单禁收裸波号 token·须逐一排除本变换自产面·W273+ 编辑器出稿前必读）全文=archive 202610.md『热冷整编 2026-10-18 r1009 bm-b 窗批』节（r1091 bm-c）。",
    "- 冷层指针：fivekeys 锚常数一律从上一波 finalize 产物 JSON 机读全精度值（prereg 文字段 8 位小数舍入面在 1e-9 容差必炸·r587 live-read 律克隆面）全文=archive 202610.md『热冷整编 2026-10-18 r1009 bm-b 窗批』节（r1093 bm-c）。",
    "- 冷层指针：bm-c 仓 core.autocrlf=true smudge 面（盘面 raw 字节 sha/尺寸≠blob 但 norm-eq 恒真·git status 不显脏·冻结面预检比对一律走 git-object 级归一）全文=archive 202610.md『热冷整编 2026-10-18 r1009 bm-b 窗批』节（r1093 bm-c）。",
]

NEW_ROW = (
    "- [2026-10-18 16:4x r1008 bm-b] **rebase-continue 幽灵拒绝死循环+stash-pop 索引毒化+"
    "per-machine 键面 union 三连坑（push 竞速窗实弹）**：①rebase 中途 stash pop 撞 "
    "'could not write index' 毒化索引后，git rebase --continue 进 GHOST-REFUSAL 死循环"
    "（报 'You must edit all merge conflicts' 而 git ls-files --unmerged 恒空）——"
    "正法=r1032 族树手术直通：全解索引 write-tree → commit-tree -p <fetch 后新 tip> "
    "-F msgfile → rebase --quit → update-ref main → reset --mixed（update-ref 前先 "
    "reflog main 核他窗提交·零孤儿才动指针）；②push 重放撞共享 regen 面分两类处置："
    "普通 regen 面=newer-wins 整文件重放，**per-machine 键面（token_usage.json 类）一律 "
    "UNION 保他机行**——机器键无 ts 字段，整文件 newer-wins 会删他机行且必触 pre-push "
    "爪拦截。How to apply：竞速窗 push 重放前先分类面（普通 regen=整文件 vs per-machine "
    "键面=union）；rebase --continue 被拒而 unmerged 恒空=索引毒化，勿再 continue 直接树手术直通。"
)

ARCHIVE_HEADER = (
    "## 热冷整编 2026-10-18 r1009 bm-b 窗批（CODELY.md 9,968B 基线+新坑律 ~790B 预穿 10KB "
    "硬线·O-20260927-0230 当窗即办律·4 行冷迁 verbatim+指针回填·prescan rc3=登记簿命中·"
    "记忆坑律类授权迁移面 TPL §2·r1047/r1062 先例·receipt=results/_r1009bmb_codely_hotcold_receipt.json）"
)


def rd(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def wr(p, s):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def main():
    codely = rd(CODELY)
    arch = rd(ARCHIVE)
    nl_c = "\r\n" if "\r\n" in codely else "\n"
    nl_a = "\r\n" if "\r\n" in arch else "\n"
    before_c = len(codely.encode("utf-8"))
    # marker uniqueness (short-needle count law r1088/r1091)
    for m in MARKERS:
        n = sum(1 for ln in codely.split(nl_c) if ln.startswith(m))
        assert n == 1, "marker count %d != 1: %s" % (n, m[:40])
    lines = codely.split(nl_c)
    moved = []
    out = []
    for ln in lines:
        hit = None
        for i, m in enumerate(MARKERS):
            if ln.startswith(m):
                hit = i
                break
        if hit is None:
            out.append(ln)
        else:
            moved.append((hit, ln))
            out.append(POINTERS[hit])
    assert len(moved) == 4, "expected 4 moved rows, got %d" % len(moved)
    new_codely = nl_c.join(out)
    if not new_codely.endswith(nl_c):
        new_codely += nl_c
    new_codely += NEW_ROW + nl_c
    # archive append (verbatim, file order preserved)
    arch_new = arch
    if not arch_new.endswith(nl_a):
        arch_new += nl_a
    arch_new += ARCHIVE_HEADER + nl_a
    for _, ln in moved:
        arch_new += ln + nl_a
    # zero-loss assertions: each moved row appears verbatim exactly once in
    # the new archive; marker rows absent from new CODELY rows; pointer and
    # new-row presence asserted
    for _, ln in moved:
        assert arch_new.count(ln) == 1, "moved row not verbatim-once in archive"
    for m in MARKERS:
        assert not any(l2.startswith(m) for l2 in new_codely.split(nl_c)), \
            "marker still present: %s" % m[:40]
    for p in POINTERS:
        assert new_codely.count(p) == 1, "pointer missing"
    assert new_codely.count(NEW_ROW) == 1, "new row missing"
    after_c = len(new_codely.encode("utf-8"))
    assert after_c <= 10240, "CODELY.md still over 10KB: %d" % after_c
    wr(CODELY, new_codely)
    wr(ARCHIVE, arch_new)
    # post-write re-read assertions (r504 law)
    c2 = rd(CODELY)
    a2 = rd(ARCHIVE)
    assert c2 == new_codely and a2 == arch_new, "post-write readback mismatch"
    for _, ln in moved:
        assert a2.count(ln) == 1, "post-write archive verbatim broke"
    assert c2.count(NEW_ROW) == 1
    # prescan verdict (capture_output law r1045)
    ps = subprocess.run(
        [sys.executable, os.path.join(REPO, "Tools", "treasure_guard.py"),
         "prescan", "CODELY.md", "research/memory-archive/202610.md"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    receipt = {
        "tool": "r1009_codely_hotcold",
        "machine": "bm-b",
        "before_bytes": before_c,
        "after_bytes": after_c,
        "archive_header": ARCHIVE_HEADER[:40],
        "moved_rows": [
            {"marker": m[:48], "row_bytes": len(ln.encode("utf-8"))}
            for m, (_, ln) in zip(MARKERS, moved)
        ],
        "moved_total_bytes": sum(len(ln.encode("utf-8")) for _, ln in moved),
        "pointer_total_bytes": sum(len(p.encode("utf-8")) for p in POINTERS),
        "new_row_bytes": len(NEW_ROW.encode("utf-8")),
        "zero_loss": True,
        "prescan_rc": ps.returncode,
        "prescan_verdict": (ps.stdout or "")[:200],
        "law": "O-20260927-0230 header law + TPL s2 authorized migration face",
    }
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: receipt[k] for k in
                      ("before_bytes", "after_bytes", "moved_total_bytes",
                       "new_row_bytes", "prescan_rc", "zero_loss")}))


if __name__ == "__main__":
    main()
