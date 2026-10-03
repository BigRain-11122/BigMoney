"""r450 bm-c S7-supplement append: post-push-race claw double-block + merge receipt."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rr_path = os.path.join(ROOT, "round_reports-bm-c.md")
raw = open(rr_path, "rb").read()
assert raw.endswith(b"\n"), "round report must end with newline"
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
LINE = (
    "2026-10-04T07:2x+08:00	| r450 bm-c S7-supplement	| closeout push 首推被 pre-push 爪正确双拦（①删除集含 bm-b r654 在途新件 _r654bmb_* x6「no owner evidence」=本地 behind 型非漂移·②共享池 owner_since 07:14:12→07:04:12 backward=r648 正例本地 behind 型陈旧面）→正解 merge 收尾：git merge origin/main 撞 19 UU（同日幂等再生态双机 S6 竞写族·daily_scorecard.{html,json} 干净自动并）→r449 配方逐面解（receipt results/_r450bmc_merge_resolve.py：UU 集完备断言 19/19 全分类零未知面；17 再生面 take-new-by-ts 全 ours 诚实比较 07:09-07:11>bm-b 07:06-07:08；regime_state asof 2026-09-30 双侧同值 tie 确定性取 ours；compute_audit 跨机 union 201+201→202；token_usage per-machine union 5/5 ours）→zero-marker 19 面+JSON reparse PASS→merge c1c716855→push 过爪（删除集空+池 owner_since=origin 新值 07:14:12 保真）→push_verify DELIVERED tip 双侧恒等 c1c716855 ahead==0/behind==0。本地未达 origin commit 数=0（push_verify 实证）。冲突池面=runnable_pool/crash_fuse 零冲突零重放（S0 reland 环律前置断言过）。爪双拦首证=治理面 live-fire 正例（防了 behind 型整树推送吞 bm-b r654 件+池 claim 回退双事故）。"
)
with open(rr_path, "ab") as fh:
    fh.write(LINE.encode("utf-8") + eol)
chk = open(rr_path, "rb").read().decode("utf-8", errors="strict").splitlines()
assert "r450 bm-c S7-supplement" in chk[-1], "rr supplement tail"
print("SUPPLEMENT-OK lines=%d" % len(chk))
