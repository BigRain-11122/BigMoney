# -*- coding: utf-8 -*-
# r636 bm-b pit-git direct-write append (post-split convention)
import hashlib

entry = ("- [2026-10-03 22:3x r636 bm-b] pre-push 爪删除集两分法+churn-absorb 前 D 项属主核验律（r519/r530 phantom-D 族 pre-push 通道新变体·同窗两连拦实弹）："
 "①**轮中 origin 前移→爪删除集假阳性**——长活轮窗内对侧推新 commit 后 push，爪按「push tip vs 本机 fetch 基座」算删除集，把对侧窗内**新增件**（实弹 _r432bmc_s6_log.txt=bm-c r432 同窗新增）报成「D no owner evidence」拦 push；判别法=git cat-file -e origin/main:<path> 有 + git log origin/main..HEAD -- <path> 空 + 本机 tip 无该件=假删除面（对侧新增非本机删），正法=竞速窗吸收 daemon churn 后 pull --rebase 集成新 tip 再推（勿走 --no-verify 逃生口·勿删真件）；"
 "②**轮首脏面吸收 commit 会把工作树未提交的外件删除吞进链**——轮首 git status 的 D 项（死会话遗产删除·实弹 _r635bmb_yield_patch.py）在 churn-absorb add -A 时照吞，链过 pre-commit 却在 pre-push 爪炸（audit.machine 无属主证据）；正法=吸收前逐 D 项验属（本机件方可随吞·外件/无证据件先 restore 归档不删律收口）；爪报文勿盲信=两类拦截面各自对症。")
acct = ("> 直写行（r636 bm-b·post-split convention direct-write）：+1 条（pre-push 爪删除集两分法+吸收前 D 项属主核验——同窗两连拦实弹·轮中 origin 前移假删除面=rebase 集成对症非逃生口·死会话 D 项吸收前验属）·追加核 {n} B（LF blob 面·md5={md5}）·尾部整行追加·件内对账行为准。")

blob = (entry + "\n").encode("utf-8")
n = len(blob)
md5 = hashlib.md5(blob).hexdigest()
acct_line = acct.format(n=n, md5=md5) + "\n"

with open("research/pit-git.md", "a", encoding="utf-8", newline="\n") as f:
    f.write("\n" + entry + "\n" + acct_line)
print("pit-git entry appended:", n, "bytes md5", md5)

# round report addendum (push-phase record)
rrline = ("2026-10-03T22:3x+08:00 | R636 bm-b POST-ROUND ADDENDUM (push \u9636\u6bb5\u4e24\u8fde\u62e6\u6536\u53e3\u5b9e\u5f55) | "
 "\u63a8\u9001\u9636\u6bb5\u4e24\u8fde\u62e6\uff1a\u2460\u8f6e\u4e2d origin \u524d\u79fb\uff0840967c498=bm-c r432 \u540c\u7a97\u65b0\u589e _r432bmc_s6_log.txt\uff09\u2192pre-push \u722a\u5220\u9664\u96c6\u5047\u9633\u6027\u62e6\u975e FF\uff08\u6b63\u6cd5\u5224\u522b\u540e\u7ade\u901f\u7a97\u5438\u6536 pre3+pull --rebase\uff09\uff1b"
 "\u2461rebase \u4e2d\u6bb5 14 UU\uff08\u5168\u4e3a\u786e\u5b9a\u6027 derive/status \u9762\u53d6 origin \u4fa7=r630 \u5f8b\uff09+\u62d2\u7edd\u7eed\u6001\uff08\u4e09\u8bc1\u5168\u51c0\u4ecd\u62d2\u300cYou must edit all merge conflicts\u300d=r427 bm-c \u5df2\u5f55\u5751\uff09\u2192\u6309 r630 \u5f8b\u9a8c\u5438\u6536\u540e\u624b\u5de5 commit -F .git/rebase-merge/message\uff08375d2a9e2\uff09+--skip \u6536\u53e3\uff08r643 bm-a \u5df2\u5f55 commit-F+skip \u8f7b\u91cd\u53d8\u4f53\uff09\uff1b"
 "\u2462\u722a\u4e8c\u62e6=\u8f6e\u9996\u5438\u6536 commit \u541e\u4e86\u5de5\u4f5c\u6811\u672a\u63d0\u4ea4\u7684 r635 \u6b7b\u4f1a\u8bdd\u5de5\u5177\u4ef6\u5220\u9664\uff08_r635bmb_yield_patch.py \u65e0\u5c5e\u4e3b\u8bc1\u636e\uff09\u2192\u6309\u6e05\u7406\u5f8b\u5f52\u6863\u4e0d\u5220\u6062\u590d\u539f\u4ef6\u63a8\u8fc7\uff08pre4 commit\uff09\uff1b\u4e24\u65b0\u9762\u5df2\u76f4\u5199 research/pit-git.md\uff08\u5220\u9664\u96c6\u4e24\u5206\u6cd5+\u5438\u6536\u524d D \u9879\u5c5e\u4e3b\u6838\u9a8c\u5f8b\uff09\u00b7\u96f6 --no-verify \u4f7f\u7528\u00b7\u672a\u7528\u9003\u751f\u53e3\u3002\u9001\u8fbe\u81ea\u8bc1\uff1aLOCAL==origin/main==358e1540d\uff08\u672c addendum+pit \u4ef6 rider commit \u540e\u518d\u81ea\u8bc1\uff09\n")
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(rrline)
print("round report addendum appended")
