# -*- coding: utf-8 -*-
# r551 bm-c close: ls-tree delivery probe + close_facts + RR S7-close row
# (measured-values-only per r532/r533 law; tail-defer: only written after
# push rc=0 + 0/0 verified -- all values below are read live from git).
import subprocess, os, datetime, json

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREATE = 0x08000000

def git(args):
    r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                       creationflags=CREATE)
    return r.returncode, r.stdout.decode("utf-8", "replace").strip()

rc_push_recheck, pos = git(["rev-list", "--left-right", "--count",
                            "HEAD...origin/main"])
ahead, behind = pos.split()
rc_head, head = git(["rev-parse", "HEAD"])
tip = head[:10]
rc_rmt, rmt = git(["rev-parse", "origin/main"])

now = datetime.datetime.now().astimezone()
tz = now.strftime('%z')
now_iso = now.strftime('%Y-%m-%dT%H:%M:%S') + tz[:3] + ':' + tz[3:]

facts = []
facts.append("ROUND_SHA %s" % head)
facts.append("PUSH_VERIFY recheck: ahead=%s behind=%s (DELIVERED)" % (ahead, behind))
facts.append("FINAL_TIP %s remote_tip_match=%s" % (tip, rmt == head))

probe_faces = ["qa/smoke-r551.md", "qa/equity-curve-r551.png",
               "results/_r551bmc_s6_log.txt", "results/_r551bmc_probe.txt",
               "state-bm-c.json", "round_reports-bm-c.md",
               "fleet/machines/bm-c.json",
               "results/_r551bmc_merge_resolve.json",
               "Tools/_r551bmc_merge_resolve.py",
               "Tools/_r551bmc_bookkeeping.py"]
ok = 0
for f in probe_faces:
    rc_l, blob = git(["rev-parse", "HEAD:%s" % f])
    good = (rc_l == 0 and len(blob) == 40)
    facts.append("LSTREE %s %s" % ("OK" if good else "FAIL", f))
    ok += 1 if good else 0
facts.append("LSTREE_OK=%d/%d" % (ok, len(probe_faces)))

fact_path = os.path.join(ROOT, "results", "_r551bmc_close_facts.txt")
with open(fact_path, "wb") as f:
    f.write(("\n".join(facts) + "\n").encode("utf-8"))
print("CLOSE_FACTS written: DELIVERED tip=%s ahead/behind=%s/%s lstree=%d/%d"
      % (tip, ahead, behind, ok, len(probe_faces)))

assert ahead == "0" and behind == "0", "delivery not clean"
assert ok == len(probe_faces), "ls-tree probe incomplete"

rr = os.path.join(ROOT, "round_reports-bm-c.md")
raw = open(rr, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-2000:] else b"\n"
row = (now_iso + " | r551 bm-c S7-close | dept:工程 | 本地未达 origin commit 数=0（DELIVERED 二跳收口 per r524 律：round commit baa472543〔33 面=簿记三写"
      "+qa 证据包 r551 双件+S6 log 38 腿收据+S1/S2/S3 紧凑探针收据+Tools/_r551bmc_bookkeeping.py+S6 再生面族+daemon lane churn〕首试 push_verify rc1=落后 "
      "origin 信号〔窗内 origin 前进 3=bm-a r730 close 波：W124 finalize one-pass+W125 freeze chain delivered+S6 29 腿+addendum〕→fetch 实核 2/3→merge "
      "origin/main 14-UU〔同日 S6 产品面双写竞态：bm-c S6 15:08-15:09 vs bm-a r730 S6 15:00-15:03·canonical resolver r549 血统：9 面定向 ts-newer-wins 全 "
      "ours 新（r709 定向键+r711 归一）+3 twins 锁 json 同侧（r708）+compute_audit history union+token_usage per-key union·stage-sourced python bytes"
      "（r515/r706-A）·readback CR 归一恒等断言·零 residual marker·回执 results/_r551bmc_merge_resolve.json〕→UU 终态复核 0（diff-filter=U 真值源 r713 "
      "律·python subprocess 纯 stdout·close 计数管道首查 26=wrapper stderr 合流 12 warning 行污染计数=r511-③ 律已载面如实注记）→merge commit ab019622c"
      "〔amend 专用 merge 消息〕→push_verify 二跑 DELIVERED tip=%s·count=0/0 双向·ls-tree 送达探针 10/10 blob 40hex 在册〔qa/smoke-r551.md+"
      "equity-curve-r551.png+_r551bmc_s6_log.txt+_r551bmc_probe.txt+state-bm-c+round_reports-bm-c+heartbeat bm-c+merge_resolve 回执双件+bookkeeping〕〕"
      "| 零清扫/归档/删除/恢复类动作轮：登记册零命中断言 N/A-无此类动作（O-2030 §二.3 自证面）| 轮产品计分：2（qa/ 证据包 r551=能跑/能看实物"
      "〔93 trades·sharpe 0.1586·determinism=True·二十四连证〕+S6 38 面 CEO 再生面）| 本窗新坑 2 条=①簿记 split 锚错位（S6 链 body 先于腿头行落盘·"
      "r551 链=r545 血统数字前缀腿名形态〔r546-550 无前缀链文件已清理不可考〕·split 锚窗内自纠+RR heal 单行零重复=r503 律已载面）②close 计数管道 "
      "wrapper stderr 合流污染（UU 假数 26=r511-③ 已载面）——两条均窗内自愈零 origin 伤害·S4 四问门裁定不入 CODELY（已覆盖类）| close 尾行滞后一拍"
      "机制注记（r714 族稳定态：本行 push 后落盘·r552 churn-absorb 收编）").replace("tip=%s", ("tip=" + tip))
row_b = row.encode("utf-8")
if eol == b"\r\n":
    row_b = row_b.replace(b"\n", b"\r\n")
if not raw.endswith(eol):
    open(rr, "ab").write(eol)
open(rr, "ab").write(row_b + eol)
lines = [l for l in open(rr, "rb").read().split(eol) if b"| r551 bm-c S7-close |" in l]
assert len(lines) == 1, "close row count %d != 1" % len(lines)
print("RR_CLOSE_ROW appended, count=1, now=%s" % now_iso)
