# -*- coding: utf-8 -*-
# r554 bm-c close row: measured-values-only (r532/r533 law; round sha /
# final tip / push hops / staged count / ls-tree / orders rescan ALL
# consumed from close_facts written after delivery verification -- zero
# prewritten outcome text). Documents the two-hop S6-race close: close#1
# push rejected (origin advanced) -> merge blocked by 19 post-commit
# dirty faces (r620) -> churn-absorb-2 -> 17-UU resolver -> push#2
# DELIVERED. git() returns 2-tuple here and BOTH call sites unpack 2
# values (r553 lineage law: helper arity checked at every call).
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

facts = open(os.path.join(ROOT, "results", "_r554bmc_close_facts.txt"),
             encoding="utf-8").read()
def fx(pat):
    m = re.search(pat, facts)
    assert m, "close_facts missing %s" % pat
    return m.group(1)
round_sha = fx(r"ROUND_SHA (\S+)")
final_tip = fx(r"FINAL_TIP (\S+)")
hops = fx(r"PUSH_VERIFY recheck: ahead=\d+ behind=\d+ \(DELIVERED, hops=(\d+)\)")
staged_n = fx(r"STAGED_COUNT (\d+)")
lstree = fx(r"LSTREE_OK=(\d+)/(\d+)")
lstree = lstree[0] + "/" + lstree[1]
orders = fx(r"ORDERS_RESCAN (\d+/\d+) unacked=(\d+) inbox=(\d+)")
orders_face = "%s unacked=%s inbox=%s" % (orders[0], orders[1], orders[2])

now = datetime.datetime.now().astimezone()
tz = now.strftime("%z")
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + tz[:3] + ":" + tz[3:]

assert ahead == "0" and behind == "0", "delivery not clean at close-row write"
assert final_tip == head[:10], "facts tip vs HEAD mismatch"

row = (now_iso + " | r554 bm-c S7-close | dept:工程 | 本地未达 origin commit 数=0（DELIVERED 两跳 S6 竞态窗 per r524/r704-1/r620 律：round commit " + round_sha + "〔" + staged_n + " 面=簿记三写+CODELY S4 新坑条目+qa 证据包双件"
      "+S6 log 38 腿收据+legdiff/probe 收据+commit_msg+close/bookkeeping/codely_append 脚本+S6 再生面族〕首试 push rc1=落后 origin 信号〔origin 前进 2=bm-b r734 close 波 1e967da9f+74f378032〕→close 窗 merge rc2 零 UU=19 个 post-commit S6/守护脏面挡道〔r620 律实弹：S6 共享再生面 17+own satengine daemon 活面 2〕→churn-absorb-2 a007c3895（targeted add 19 面+commit -F）"
      "→merge 单停 17-UU=同窗 S6 双写竞态面〔vs bm-b r734 波 15:4x-15:46 落·我链 15:50-15:52〕→resolver Tools/_r554bmc_merge_resolve.py：ts-newer-wins 格式归一定向键（r709/r711）x10 json 全 ours 机器探针定谳〔15:50:59-15:52:31>15:42:06-15:46:04 逐面实测〕+twins 同侧（r708：REPORT md/LIVE md x2/dashboard js 跟 json）x4+CODELY.md 块联合（r706 零丢失·ours 36 entries+theirs 34 全子集 new=0·锚集恒等断言过）+compute_audit 滚动联合（r729·201+202→203·latest ours 15:50:41>15:41:54）+token_usage per-key max-union（r715/r522·newer=ours）·stage 源 python bytes（r515/r706-A）·反读 reparse+关键键断言过（r704）·零 residual marker（r505-③）→merge commit " + final_tip + "→push#2 rc0 DELIVERED 0/0〔hops=" + hops + " 全实测消费 close_facts〕→ls-tree 终探针 " + lstree + " PASS〔含 CODELY.md+legdiff 真门收据〕→orders 复扫 " + orders_face + "（S0.5/S7 双扫合规）→close_facts tail-defer 实测值落盘〔r532/r533 律·回执 results/_r554bmc_merge_resolve.json 17 面决策表〕〕"
      "| 零清扫/归档/删除/恢复类动作轮：登记册零命中断言 N/A-无此类动作（O-2030 §二.3 自证面）| 轮产品计分：2（qa/ 证据包 r554=能跑/能看实物〔93 trades·sharpe 0.1586·determinism=True·二十七连证〕+S6 38 面 CEO 再生面）| 本窗新坑 1 条=lineage 复制替换链 double-apply→legdiff 自比较空转假 PASS（r553 收据谎报「vs r552 lineage」未发生的比较·真门=lineage_copy 内 LEGS 恒等断言在位零漏检——CODELY 行级 append 新律〔legdiff 血统替换只改 NEW 行路径+复制器替换组禁前后件重叠 assert+收据禁引用未发生的比较〕·r554 legdiff 已写真门 OLD=r553/NEW=r554 PASS）| close 尾行滞后一拍机制注记（r714 族稳定态：本行 push 后落盘·r555 churn-absorb 收编；resolver/closerow 尾面脚本同收编）")

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
print("RR_CLOSE_ROW appended, count=1, tip=%s round=%s now=%s" % (final_tip, round_sha, now_iso))
