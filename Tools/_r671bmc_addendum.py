# -*- coding: utf-8 -*-
"""r671 bm-c addendum row append (push-race closeout disclosure, r669
addendum precedent): claw phantom-deletion window + rebase resolution +
delivery verified + concurrent tick session observation."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
ROW = (
 "2026-10-07T11:23:00+08:00 | r671 addendum | dept:工程 | push-race 收口留痕：①首推 11:14 被双闸拦=pre-push 爪 behind-signal 幻影删除面"
 "（origin 同窗前进=bm-a r819 postscript 43cef3eb3 含 W172 shards+r819 脚本·我树落后新 tip 非真删除·r524/r704 律原文场景·零 --no-verify）"
 "②pull --rebase 落新 tip 撞 18-UU 同日 regen 面=per-face 裁决器〔15 面 local ts-newer wins〔本机 S6 链 11:08-11:11 晚于 bm-a 11:05-11:07〕+"
 "3 面 bm-a 宿主单写者 origin-wins〔dashboard_status.json/.js+strategy_scorecard+scorecard_v1·r758/r378 律〕·显式 stage 提取防 rebase ours/theirs 反转坑〕"
 "③rebase --continue 假拒绝〔r758 态机粘滞律〕=手落 commit+rebase --quit+branch -f main 1369802ed 重挂治愈④推送成功 43cef3eb3..07210dce3"
 "〔3 commit：heal 39b077c48+close 1369802ed+tail 07210dce3〕⑤送达自证：fetch 后 rev-list 0/0+origin cat-file 收据在位 rc0"
 "⑥双执行体观察：循环 tick 会话（codely.exe PID 8604·10:55:02 起）与本交互会话并行同仓 28min+·其零 commit 零台账行"
 "〔S5 rerun-guard count==0 断言将拒其重复 r671 行=守卫自纠·按让路律 commit 时间序本会话为先不击杀·watchdog/下一 tick 自愈〕"
 "⑦本地未达 origin commit 数=0（推送后 fetch+rev-list+ls-tree 三探针实测）"
)

raw = open(LEDGER, "rb").read()
assert raw.endswith(b"\r\n") or raw.endswith(b"\n"), "tail EOL gate"
guard = "r671 addendum".encode("utf-8")
assert raw.count(guard) == 0, "rerun guard"
eol = b"\r\n" if raw.count(b"\r\n") >= 10 else b"\n"
sep = b"" if raw.endswith(eol) else eol
new = raw + sep + ROW.encode("utf-8") + eol
open(LEDGER, "wb").write(new)
post = open(LEDGER, "rb").read()
assert post.count(guard) == 1, "post-verify count==1"
print("addendum row appended; ledger now", len(post), "B")
