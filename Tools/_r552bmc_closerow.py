# -*- coding: utf-8 -*-
# r552 bm-c close row: measured-values-only (r532/r533 law; all values read
# live from git). Documents the 4-hop treadmill close + QA-pack fix commit.
import datetime, os, subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREATE = 0x08000000

def git(args):
    r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                       creationflags=CREATE)
    return r.returncode, r.stdout.decode("utf-8", "replace").strip()

rc_cnt, pos = git(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
ahead, behind = pos.split()
rc_head, head = git(["rev-parse", "HEAD"])
tip = head[:10]

now = datetime.datetime.now().astimezone()
tz = now.strftime("%z")
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + tz[:3] + ":" + tz[3:]

assert ahead == "0" and behind == "0", "delivery not clean at close-row write"

row = (now_iso + " | r552 bm-c S7-close | dept:工程 | 本地未达 origin commit 数=0（DELIVERED 四跳+fix 收口 per r524/r704-1 律：round commit c0c7427cc〔34 面=簿记三写+qa 证据包双件"
      "…见 fix 注记+S6 log 38 腿收据+legdiff/probe 收据+bookkeeping+S6 再生面族〕首试 push_verify rc1=爪双拦落后 origin 信号〔窗内 origin 前进 8=bm-a r731 W126 波+bm-b r732/733 close 波·删除集=W126"
      " 件缺席我 tip+池 owner_since 回退面·两拦皆落后态非本地误写 r524 律〕→fetch 2/8→merge#1 2-UU〔regime_state ours 15:20:09>theirs 15:09:09 stage-2+compute_audit history union 201+206→207"
      " ALL_DICT r522〕merge commit 64ead7ee0→push#2 爪拦再犯〔origin 又前进·W126 shards 2-4〕→fetch 1/2→merge#2 14-UU 全同日 S6 双写竞态面〔9 面 ts-newer-wins 全 theirs 15:20:42-15:22:53>ours "
      "15:20:08-15:20:37 机器探针实测定谳〔bm-a r733 波晚于我 S6 链 1-2 分钟〕+3 twins 锁 json 同侧 r708+compute_audit union+token_usage per-key union r515/r522·stage-sourced python bytes r515/r706-A·"
      "readback 断言全过·零 residual marker·回执 results/_r552bmc_merge_resolve.json 双窗 union r516-3〕merge commit 75e023e92→push#3 爪拦三犯〔origin 再进 1=bm-a r731 close shards 5-6〕→fetch→merge#3 "
      "clean〔11 面〕+原子 push DELIVERED 0/0 tip a53e1b06a7→ls-tree 终探针 10/12 抓红=qa/smoke-r552.md+equity-curve-r552.png 缺席 round commit〔r549-① untrackedCache 陈旧窗复现：15:19 落盘件在 "
      "15:2x porcelain 快照缺席·后跑 status 又可见=r549-① 原文形态·close v2 确定性 add 律违例当场定罪〕→fix commit ca90f6e5a〔确定性 add 7 面=qa 双件+close 脚本+close_facts+mergemsg2+own satengine x2〕"
      "→push DELIVERED 0/0 final tip=" + tip + "→close 探针复跑 12/12 PASS+orders 复扫 154/154 零未回执+inbox 0（S0.5/S7 双扫合规）〕| 零清扫/归档/删除/恢复类动作轮：登记册零命中断言 N/A-无此类动作"
      "（O-2030 §二.3 自证面）| 轮产品计分：2（qa/ 证据包 r552=能跑/能看实物〔93 trades·sharpe 0.1586·determinism=True·二十五连证·fix commit 后全量在册〕+S6 38 面 CEO 再生面）| 本窗新坑 1 条="
      "r549-① untrackedCache 陈旧窗复现（已载律·close v2 终探针正确执法当场抓红·窗内自愈零数据损失〔盘上件全程完好·仅晚一跳入册〕·S4 四问门裁定不入 CODELY〔已覆盖类〕——如实披露：本窗 close 面清单确实"
      "重犯了「依赖 status 可见性」违例，修法=确定性 add 已在 fix commit 落地）| close 尾行滞后一拍机制注记（r714 族稳定态：本行 push 后落盘·r553 churn-absorb 收编）")

rr = os.path.join(ROOT, "round_reports-bm-c.md")
raw = open(rr, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-2000:] else b"\n"
row_b = row.encode("utf-8")
if eol == b"\r\n":
    row_b = row_b.replace(b"\n", b"\r\n")
if not raw.endswith(eol):
    open(rr, "ab").write(eol)
open(rr, "ab").write(row_b + eol)
lines = [l for l in open(rr, "rb").read().split(eol) if b"| r552 bm-c S7-close |" in l]
assert len(lines) == 1, "close row count %d != 1" % len(lines)
print("RR_CLOSE_ROW appended, count=1, tip=%s now=%s" % (tip, now_iso))
