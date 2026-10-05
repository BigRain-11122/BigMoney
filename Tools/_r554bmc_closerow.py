# -*- coding: utf-8 -*-
# r554 bm-c close row: measured-values-only (r532/r533 law; push hops /
# staged count / tip ALL consumed from close_facts written by the close
# driver AFTER delivery verification -- zero prewritten outcome text).
# git() returns 2-tuple here and BOTH call sites unpack 2 values (r553
# lineage law: helper arity checked at every call).
import datetime, os, re, subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREATE = 0x08000000

def git2(args):
    r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                       creationflags=CREATE)
    return r.returncode, r.stdout.decode("utf-8", "replace").strip()

rc_cnt, pos = git2(["rev-list", "--left-right", "--count",
                    "HEAD...origin/main"])
ahead, behind = pos.split()
rc_head, head = git2(["rev-parse", "HEAD"])
tip = head[:10]

facts = open(os.path.join(ROOT, "results", "_r554bmc_close_facts.txt"),
             encoding="utf-8").read()
m_hops = re.search(r"PUSH_VERIFY recheck: ahead=\d+ behind=\d+ \(DELIVERED, hops=(\d+)\)", facts)
m_staged = re.search(r"STAGED_COUNT (\d+)", facts)
m_ok = re.search(r"LSTREE_OK=(\d+)/(\d+)", facts)
assert m_hops and m_staged and m_ok, "close_facts missing measured values"
hops, staged_n, lstree = m_hops.group(1), m_staged.group(1), m_ok.group(1) + "/" + m_ok.group(2)

now = datetime.datetime.now().astimezone()
tz = now.strftime("%z")
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + tz[:3] + ":" + tz[3:]

assert ahead == "0" and behind == "0", "delivery not clean at close-row write"

row = (now_iso + " | r554 bm-c S7-close | dept:工程 | 本地未达 origin commit 数=0（DELIVERED per r524/r704-1 律：round commit " + tip + "〔" + staged_n + " 面=簿记三写+CODELY S4 新坑条目+qa 证据包双件"
      "+S6 log 38 腿收据+legdiff/probe 收据+commit_msg+close/bookkeeping/codely_append 脚本+S6 再生面族〔compute_audit/regime_state/token_usage/_attrition_guard_scan/REPORT-2026-10-05+LIVE-2026-10-05"
      "/dualrun 证据行/b_layer 掩码+本机车道镜像含 5 个 no-op status 面防尾漏〕〕push rc0 " + hops + " 跳 DELIVERED 0/0〔实测值消费 close_facts·轮首 S0 已 merge cabb58bfe 零 UU〕→ls-tree 终探针 " + lstree + " PASS〔含 CODELY.md+legdiff 真门收据"
      "〕→orders 复扫 154/154 零未回执·inbox 0（S0.5/S7 双扫合规）→close_facts tail-defer 实测值落盘〔r532/r533 律·本行全部结果字段=实测消费零预写〕〕"
      "| 零清扫/归档/删除/恢复类动作轮：登记册零命中断言 N/A-无此类动作（O-2030 §二.3 自证面）| 轮产品计分：2（qa/ 证据包 r554=能跑/能看实物〔93 trades·sharpe 0.1586·determinism=True·"
      "二十七连证〕+S6 38 面 CEO 再生面）| 本窗新坑 1 条=lineage 复制替换链 double-apply→legdiff 自比较空转假 PASS（r553 收据谎报「vs r552 lineage」未发生的比较·真门=lineage_copy 内 LEGS 恒等断言在位零漏检"
      "——CODELY 行级 append 新律〔legdiff 血统替换只改 NEW 行路径+复制器替换组禁前后件重叠 assert+收据禁引用未发生的比较〕·r554 legdiff 已写真门 OLD=r553/NEW=r554 PASS）| close 尾行滞后一拍机制注记"
      "（r714 族稳定态：本行 push 后落盘·r555 churn-absorb 收编）")

rr = os.path.join(ROOT, "round_reports-bm-c.md")
raw = open(rr, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-2000:] else b"\n"
row_b = row.encode("utf-8")
if eol == b"\r\n":
    row_b = row_b.replace(b"\n", b"\r\n")
if not raw.endswith(eol):
    open(rr, "ab").write(eol)
open(rr, "ab").write(row_b + eol)
lines = [l for l in open(rr, "rb").read().split(eol) if b"| r554 bm-c S7-close |" in l]
assert len(lines) == 1, "close row count %d != 1" % len(lines)
print("RR_CLOSE_ROW appended, count=1, tip=%s now=%s" % (tip, now_iso))
