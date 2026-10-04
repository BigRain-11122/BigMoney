"""r698 bm-b addendum writer: round-report push-race narrative + CODELY.md
resolver-lineage copy pit law (marker-gated appends, bytes-safe, zero
console CJK). One lesson per the memory entry four-question gate."""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RR = os.path.join(REPO, "logs", "iteration-loop", "round_reports.md")
CM = os.path.join(REPO, "CODELY.md")

ADDENDUM = (
    "2026-10-04T22:5x+08:00 | round 698 addendum (bm-b) | S7 收口双波 "
    "push-race 实录：首推被 pre-push 双爪正确拦截（本地 behind 型=r648 律："
    "origin 在途他机新 commit 含 _r500bmc_* 10 件删除集假象+CONTEST-RC "
    "keepalive 22:32:33>本地基座 22:12:07 owner_since 回退假象）→零 "
    "--no-verify→fetch+merge 三波净路（absorb #2/#3 共 13 lane 面）→"
    "merge#1 32 UU 同窗双 S6 再生面 resolver（r697 血统 "
    "_r698bmb_merge_resolve.py：25 json ts-newer-wins 大多 ours-fresh "
    "22:35:xx + 4 md/js twins 锁 json 侧 + token per-key union theirs=21 + "
    "crash_fuse per-key ours=1 + x2_watch 行 union 2875+6 零丢失 "
    "containment 断言）→推再拒（bm-a r699 同窗双 merge close-3/4 已推）→"
    "merge#2 5 UU（resolver 幂等重跑·x2 union 2881+6=双机 watch 行共存）→"
    "终推 DELIVERED（tip==remote 3e32fa151·ahead=0·behind=0）。新坑律入 "
    "CODELY（resolver twin 分支 TWIN-PENDING 漏写=r499 型·完成度判据=UU "
    "清零勿信脚本自报）。双爬零 --no-verify 零强推。本地未达 origin commit "
    "数=0（push_verify DELIVERED 实证）\n")

LAW = (
    "- [2026-10-04 22:5x r698 bm-b] merge resolver 血统复制 TWIN-PENDING "
    "漏写坑（32 UU 同窗双 S6 收口实弹·r499 型第二犯·fail-closed 当场抓回零 "
    "origin 伤害）：r697 正典 resolver 的 twin 分支先 receipt[path]="
    "'TWIN-PENDING' 再置 data=None；r698 复制改造时标记只赋局部变量、落在 "
    "`if data is not None` 块内→twin 四面 receipt 缺键→第二遍 twin 腿 "
    "`.get()=='TWIN-PENDING'` 恒 False→四面带冲突 marker 留树（脚本自报 "
    "28/32 假完成度）。自愈=幂等重跑（resolver 全量从 HEAD/MERGE_HEAD blob "
    "确定性重导出·marker 断言在位）+ UU 余量复核。律=复制 resolver 血统时 "
    "twin/特殊面分支的 receipt 标记必须先于 data 判写入 receipt 字典；"
    "resolver 跑完的完成判据=git status UU 余量清零，勿信脚本自报计数。"
    "How to apply：复制 merge resolver 先核 twin 分支标记写入位；收口门="
    "porcelain UU==0。\n")


def append(path, text, marker):
    with open(path, "rb") as f:
        blob = f.read()
    txt = blob.decode("utf-8", errors="replace")
    n0 = txt.count(marker)
    assert n0 == 0, "marker %r count %d != 0" % (marker, n0)
    tail_ok = blob.endswith(b"\n") or blob.endswith(b"\r\n")
    with open(path, "a", encoding="utf-8", newline="") as f:
        if not tail_ok:
            f.write("\n")
        f.write(text)
    with open(path, "rb") as f:
        n1 = f.read().decode("utf-8", errors="replace").count(marker)
    assert n1 == 1, "marker %r count %d != 1 after append" % (marker, n1)
    print("APPEND OK %s marker=1" % os.path.basename(path))


append(RR, ADDENDUM, "round 698 addendum (bm-b)")
append(CM, LAW, "r698 bm-b] merge resolver 血统复制 TWIN-PENDING")
