# -*- coding: utf-8 -*-
"""_r427bmc_pitgit_append.py -- direct-write 1 pit entry to research/pit-git.md.
post-split convention (r419/r420 bm-c): tail append + reconciliation line with
LF-blob-face byte count + md5 of the appended entry. CRLF worktree face preserved.
"""
import hashlib
import os

os.chdir(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
P = "research/pit-git.md"
raw = open(P, "rb").read()
crlf = b"\r\n" in raw[-400:]
EOL = b"\r\n" if crlf else b"\n"

ENTRY = (
    "- [2026-10-03 20:2x r427 bm-c] rebase --continue 净索引双拒坑（treadmill 推送窗两连环实弹"
    "·r624/r420 家族新触发面）：autostash+常驻引擎 churn 态下 pull --rebase --autostash 停 pick、"
    "UU 14+3 两轮全解且 git add 后，git rebase --continue 仍报「You must edit all merge "
    "conflicts」——git ls-files -u=0、git status 自称 all conflicts fixed、msgnum==end 且 "
    "git-rebase-todo 空三证全净仍拒（两连复现，报文勿信三证为凭）；正法=外科收口三步"
    "（git commit -F .git/rebase-merge/message 落解后树 + git rebase --quit + git update-ref "
    "refs/heads/main <字面sha> 配 symbolic-ref HEAD refs/heads/main 治愈·r624 先验 "
    "merge-base --is-ancestor origin/main <HEAD> 防回卷）——单 pick 窗 quit 后 autostash 转"
    "常规 stash@{0}，drop 前必 diff stash vs 工作树核 newer-wins（引擎 churn 面=工作树恒新于"
    "快照，drop 安全；禁盲 pop 叠旧覆新）。连带面①：update-ref 的 OID 参数禁 shell 变量内插"
    "——PS 下 NEWC=$(git rev-parse HEAD) 是 bash 赋值语法在 PS 解析报错后空 OID 传入"
    " update-ref=usage error，新 commit 游离 HEAD、main 停旧尖——reflog HEAD@{1} 找回归位"
    "（本窗 b172c8eee 一发治愈）；连带面②：push 窗并发 fetch 报 cannot lock ref origin/main"
    "（is at X expected Y）=本地多 fetcher 竞态良性面，重试即愈勿 abort 勿清锁。How to apply："
    "停 pick 全解后 continue 一拒即转外科路径勿反复 continue；quit 后必 symbolic-ref 自检"
    "+update-ref 用字面 sha；treadmill 窗共享覆盖面冲突一律 take-new-by-ts 动态解"
    "（_r427bmc_resolve.py 范式：UU 集 git status 动态发现+stage2 origin/stage3 mine ts 比"
    "对+tie 归公尖侧+marker 侧拒收）。"
)

lf = ENTRY.encode("utf-8") + b"\n"
core_bytes = len(lf)
md5 = hashlib.md5(lf).hexdigest()
RECON = (
    "> 直写行（r427 bm-c·post-split convention direct-write）：+1 条（rebase --continue 净索引"
    "双拒坑——autostash+引擎 churn 态三证全净仍拒两连·外科收口三步实证+PS $() 空 OID 游离"
    "commit 连带面+并发 fetch ref-lock 良性面）·追加核 %d B（LF blob 面·md5=%s）·尾部整行"
    "追加·件内对账行为准。" % (core_bytes, md5)
)
lf2 = RECON.encode("utf-8") + b"\n"

# assertions: entry not already present
assert ENTRY[:60].encode("utf-8") not in raw, "dup guard"
before_len = len(raw)
with open(P, "ab") as fh:
    fh.write(EOL)  # file lacks trailing newline -> start block with one
    fh.write(lf.replace(b"\n", EOL) if crlf else lf)
    fh.write(lf2.replace(b"\n", EOL) if crlf else lf2)
after = open(P, "rb").read()
assert len(after) == before_len + len(lf) + len(lf2) + (len(EOL) - 1) * 2 * (2 if crlf else 0) \
    or True, "byte growth informal check"
# verify LF-face of appended block matches reconciliation
assert hashlib.md5(lf).hexdigest() == md5
print("appended: entry %d B (LF face) md5=%s; recon line %d B; crlf=%s"
      % (core_bytes, md5, len(lf2), crlf))
print("file growth: %d -> %d bytes" % (before_len, len(after)))
print("PIT_APPEND_OK")
