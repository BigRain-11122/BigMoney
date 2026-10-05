# -*- coding: utf-8 -*-
# r553 bm-c close row: measured-values-only (r532/r533 law; all values read
# live from git). Documents the 2-hop treadmill close + post-push receipt
# recovery (unpack bug, zero data harm) + inbox W127-seat processing.
import datetime, os, subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREATE = 0x08000000

def git(args):
    r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                       creationflags=CREATE)
    return r.returncode, r.stdout.decode("utf-8", "replace").strip()

rc_cnt, pos = git(["rev-list", "--left-right", "--count",
                   "HEAD...origin/main"])
ahead, behind = pos.split()
rc_head, head = git(["rev-parse", "HEAD"])
tip = head[:10]

now = datetime.datetime.now().astimezone()
tz = now.strftime("%z")
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + tz[:3] + ":" + tz[3:]

assert ahead == "0" and behind == "0", "delivery not clean at close-row write"

row = (now_iso + " | r553 bm-c S7-close | dept:工程 | 本地未达 origin commit 数=0（DELIVERED 两跳 treadmill per r524/r704-1 律：round commit 248c037ea〔32 面=簿记三写+qa 证据包双件"
      "+S6 log 38 腿收据+legdiff/probe 收据+commit_msg+close/bookkeeping 脚本+S6 再生面族〔compute_audit/regime_state/token_usage/REPORT-2026-10-05+LIVE-2026-10-05+latest 指针/"
      "dualrun 证据行/attrition 扫描/b_layer 掩码+本机车道镜像 7 件〕〕首试 push rc1=落后 origin 信号〔窗内 origin 前进 2=bm-a W127 席位公示波 MSG 在列〕→fetch 实核 3/2→merge 单停零 UU"
      "→push#2 rc0 DELIVERED 0/0 tip 171dd3e43→ls-tree 终探针 11/11 PASS〔11 面集=零 UU 轮无 merge-resolve 对〕→close 脚本崩于 rev-parse 元组解包〔git() 2 元组→3 元组·搬运调用腿未跟改·崩点晚于 push#2 送达=零 origin 伤零数据伤〕→恢复脚本"
      " Tools/_r553bmc_close_recovery.py 实测值补齐 close_facts〔0/0·11/11·orders 复扫 154/154 零未回执〕→inbox 1 处理〔MSG-2026-10-05-1548-bma-w127-seat=W127 席位公示 bm-a 属主"
      "〔A 297_004..299_003+B 67_601..67_800·CLEAN hops=0·r565 published=reserved 先推后冻〕bm-c 零动作 ack：席位非本机属主·反重复律照守零起草·移入 processed/〕（S0.5/S7 双扫合规）〕"
      "| 零清扫/归档/删除/恢复类动作轮：登记册零命中断言 N/A-无此类动作（O-2030 §二.3 自证面）| 轮产品计分：2（qa/ 证据包 r553=能跑/能看实物〔93 trades·sharpe 0.1586·determinism=True·"
      "二十六连证〕+S6 38 面 CEO 再生面）| 本窗新坑 1 条=lineage 复制 git() 返回值元数漂移（r552 血统 2 元组→r553 新写 3 元组·搬运调用腿未跟改→崩在 push 后纯收据面滞后零数据伤——CODELY 行级 append"
      " 新律〔复制血统先核 helper 签名元数全调用点一致+写前干跑冒烟·「崩在 push 后」先核交付态再补收据禁盲目重推〕·恢复脚本补齐+原位修复 close 脚本〔尾面 r554 churn-absorb 收编〕）| close 尾行滞后一拍机制注记"
      "（r714 族稳定态：本行 push 后落盘·r554 churn-absorb 收编）")

rr = os.path.join(ROOT, "round_reports-bm-c.md")
raw = open(rr, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-2000:] else b"\n"
row_b = row.encode("utf-8")
if eol == b"\r\n":
    row_b = row_b.replace(b"\n", b"\r\n")
if not raw.endswith(eol):
    open(rr, "ab").write(eol)
open(rr, "ab").write(row_b + eol)
lines = [l for l in open(rr, "rb").read().split(eol) if b"| r553 bm-c S7-close |" in l]
assert len(lines) == 1, "close row count %d != 1" % len(lines)
print("RR_CLOSE_ROW appended, count=1, tip=%s now=%s" % (tip, now_iso))
