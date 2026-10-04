"""r475 bm-c S7-close line append + close commit (resolver evidence + daemon
lane faces) + push_verify. Bytes-mode append per r641 law."""
import datetime
import json
import os
import subprocess

C = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")

now = datetime.datetime.now()
now_iso = now.isoformat(timespec="seconds")

close_line = (
    "2026-10-04T" + now_iso[11:] + "+08:00｜r475 bm-c S7-close｜本地未达 origin commit 数=0"
    "（push_verify DELIVERED 两段：round commit 5b4c8b618〔amend 终版 38 面·pre-commit 爪过〕"
    "+merge #1 14-UU canon 解+merge #2 波收敛〔bm-b r674 wave 8 面零 UU〕·tip "
    "ad45ed590d14f651487adb3e2e7fabbec3585fd1==remote tip·ahead=0/behind=0·零 --no-verify·"
    "零强推·两波 push-race 全净路收敛）｜收口实录：round commit 首推 REJECTED rc1（bm-a r679 "
    "wave 在途：CFO panel completeness probe PASS=FUND piece-4 prereq slice 收口+21-UU canon "
    "resolve）→**心跳字段丢失事故当场抓回**（closeout.py 全新 dict 覆盖 fleet/machines/bm-c.json"
    "=orders_ack 等 23 字段被剥〔staged diff -199 行异常指征〕→HEAD~1 blob 实取恢复 35 字段全保"
    "〔orders_ack=154 项原样+epoch int+clock T-sep 自证〕→amend 未推送私有史合法〔r461 判例〕→"
    "证据件 results/_r475bmc_hb_heal.py）→fetch behind=3→merge origin bm-a r679 wave 撞 14 UU"
    "（porcelain 全量 U 行清点 r657 律①·12 regen ts-newer 双胞胎+compute_audit hist-union+token "
    "r466 per-key union〔side_pick>0 断言〕）→resolver=results/_r475bmc_merge_resolve.py（r474 "
    "血统·UU census 断言+marker 行首扫描+reparse 门+attrition 复扫 CLEAN）→merge commit 首推 "
    "REJECTED rc1（bm-b r674 wave 在途：trio NULLS burn snapshot absorb）→merge #2 零 UU 净落→"
    "push_verify DELIVERED（tip ad45ed590d==remote）｜inbox 处理：本轮 0 新入站件（1 出站自 "
    "MSG-1332 在途待 bm-a/bm-b 消费·S0.5/S7 双复测）零归档动作｜零清扫/归档/删除/恢复类动作轮："
    "登记册零命中断言 N/A-无此类动作（O-2030 §二.3 自证面）｜轮产品计分：5x HANDOVER r475 条目"
    "（增量窗 r471-475·统一链 625,977 live-read）+S6 38/38 log（_r475bmc_s6_log.txt）+fundnulls "
    "watch JSON（V778/Q604/D451·自愈第三轮持续）+14-UU resolver 件+心跳恢复件+S3 探针族+REPORT/"
    "LIVE-2026-10-04 幂等再生=可跑/能看实物面（等待态声明：finalize 窗 10-05 10:30 开·N1 关+trio "
    "bm-b 属主+板空=零新面孔可烧·非空转）\n")

with open(REPORT, "ab") as f:
    f.write(close_line.encode("utf-8"))
with open(REPORT, "rb") as f:
    tail = f.read()
assert b"r475 bm-c S7-close" in tail.splitlines()[-1], "S7-close line append failed"
print("CLOSE_LINE_OK")

def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, creationflags=C, cwd=ROOT)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace"), \
        (p.stderr or b"").decode("utf-8", "replace")

rc, out, err = git("add", "-A")
assert rc == 0, "add fail: " + err[:200]
rc, out, err = git("diff", "--cached", "--stat")
print(out[-500:])
rc, out, err = git("commit", "-m",
                   "r475 bm-c S7-close: two-wave push-race converged DELIVERED (tip ad45ed590d); "
                   "heartbeat field-loss incident caught pre-push (35 fields restored, orders_ack "
                   "154 intact); 14-UU canon resolve; pool self-heal 3rd-round evidence")
assert rc == 0, "close commit fail: " + (out + err)[:300]
print("COMMIT_OK " + out.splitlines()[0] if out else "")

pr = subprocess.run([os.path.join(ROOT, "Tools", "push_verify.py").replace("\\", "\\\\")]
                    if False else ["python", "Tools/push_verify.py"],
                    capture_output=True, creationflags=C, cwd=ROOT)
txt = (pr.stdout or b"").decode("utf-8", "replace")
print("PUSH_VERIFY_RC=" + str(pr.returncode))
print(txt.strip()[-300:])
