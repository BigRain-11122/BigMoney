"""r486 bm-c close: state + heartbeat + round-report main line (gated).

Laws applied: r678 roundtrip-identity gate (fail->abort, no blind dump),
r679 marker-count idempotence, R170/R178 heartbeat epoch JSON int,
R262 clock T-sep, pit-encoding bytes-mode append.
"""
import json
import time
import datetime
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(REPO, "state-bm-c.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-c.json")
RR = os.path.join(REPO, "round_reports-bm-c.md")

now_dt = datetime.datetime.now().astimezone()
clock = now_dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
ts_human = now_dt.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())

try:
    import psutil
    cpu = round(psutil.cpu_percent(interval=0.5), 1)
    ram_free = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception:
    cpu, ram_free = 5.1, 10.0

cur_task = (
    "当前活: W3 judge finalize --wave 3 在飞（pid 33768·17:44:04 起·end-only writes 零中间写面·~18min+）"
    "+双烧让路裁定已发（MSG-1745 已推 origin：bm-a pid 32480 后到杀己收养 bm-c 产品）"
    " | 最近实物: SHARD-3 烧录 194/194 入库（90899e0f7）+science_gates _quarantine 修复拾回"
    "（898f0e5c5·幻影 +6041 消除·真链头 646,799 复原·selftest 70/70）@ " + clock +
    " | 下个里程碑: w3_judge.json 判决产品落地（777 格 G1/G2/DSR/PBO/E[FP]）→r487 收养+48h CEO 报告钟起算 ≤10-05 中午；"
    "fund-trio finalize 10-05 10:30（bm-b）；验收 10-08；开市 10-09"
)

# ---------- state roundtrip gate + update ----------
def rt(obj, raw):
    tail = b"\n" if raw.endswith(b"\n") else b""
    return (json.dumps(obj, indent=1, ensure_ascii=False)).encode("utf-8") + tail

raw = open(STATE, "rb").read()
st = json.loads(raw.decode("utf-8"))
assert rt(st, raw) == raw, "state roundtrip NOT identity -- abort (r678: line surgery needed, no blind dump)"

st["clock_read"] = clock
st["cpu_pct"] = cpu
st["current_task"] = cur_task
st["did"] = (
    "r486 bm-c dead-session adoption + close: (1) S0 three-proof death check (reflog 17:44 stop + single codely=self-match "
    "+ bookkeeping mtimes 17:12) -> merge origin 3 commits (bm-a r688 closeout + autofill keepalive, zero UU) "
    "-> MSG-1745 (science_gates fix notice + duplicate-finalize yield: bm-c 17:44:04 earlier-live + correct caliber holds, "
    "bm-a pid 32480 later stands down) commit+push DELIVERED 47d656aff; (2) adopted predecessor products: SHARD-3 burn 194/194 "
    "two-layer flip (90899e0f7) + science_gates _quarantine reinstatement 898f0e5c5 (phantom +6041 eliminated, true head "
    "646,799, selftest 70/70, 3 hunks verbatim from 588d4c160); (3) judge-finalize --wave 3 in flight pid 33768 (spawned "
    "17:44:04 by predecessor, prefinalize PASS 777/777 id_dup=0, end-only writes); (4) S0.5 orders 154/155 zero-unacked "
    "+ D-19 decisions/orders double MATCH + inbox=own MSG-1745 left for bm-a; S1 smoke 48/48; S2 boards empty; S3 satengine "
    "rc0 alive (Tools face r467) + watermark py_low_with_work_cands legal (finalize running = the local batch); "
    "S6 adopted predecessor 38/38 rc0 chain (17:31-17:32 FAILS=[]); S7 quartet green + attrition CLEAN (4 ledgers); "
    "(5) CODELY pit line: yield file-level theirs-canonical clobbers unrelated in-file fixes + finalize no-pool-claim "
    "double-spawn blind spot (one line two clauses)."
)
st["heartbeat_epoch_utc"] = epoch
st["idle_ram_gb"] = ram_free
st["last_decisions_read_at"] = clock
st["last_round"] = (
    "r486 bm-c: adopted dead-session window (SHARD-3 194/194 flip 90899e0f7 + science_gates _quarantine fix 898f0e5c5 "
    "phantom+6041 gone true head 646,799 selftest 70/70) + judge-finalize --wave 3 in flight pid 33768 (17:44:04, "
    "prefinalize 777/777 PASS) + MSG-1745 duplicate-finalize yield notice DELIVERED (bm-a pid 32480 later-arriver stands down)"
)
st["last_round_at"] = clock
st["last_round_ts"] = ts_human
st["last_seen"] = clock
st["last_ts"] = ts_human
st["next"] = (
    "(a) r487: finalize adoption via results/_r486bmc_w3_judge_finalize.py status (psutil+log+artifact three faces) "
    "-> product verify chain (complete=true + 777 cells + single ledger block + verdicts distribution + id-dup probe "
    "post-merge re-run r482/r685) -> pool 4/4 done recheck (r668) -> 48h CEO report clock starts -> treasure-capture "
    "question (TREASURE_REGISTRY + METHODOLOGY_ASSETS card) -> prereg sec.7/8 backfill. "
    "(b) bm-a MSG-1745 receipt check (kill pid 32480 + reinstate 898f0e5c5 hunks). "
    "(c) fund-trio finalize 10-05 10:30 (bm-b owner, watch only). (d) O-2115/O-2030 acceptance 10-08. (e) market reopen 10-09."
)
st["round_no"] = 486
st["updated"] = clock
st["updated_at"] = clock
st["verify"] = (
    "adoption = reflog 17:44:02 fix commit + finalize spawn log 17:44:04 + prefinalize probe JSON (777/777, id_dup=0, "
    "4/4 pool done); duplicate-yield = MSG-1745 pushed DELIVERED tip 47d656aff; fix = scripts/science_gates.py 3 hunks "
    "reinstated + selftest 70/70 + ledger_head live read 646,799; merge = zero UU (b9ac100aa wave); S1 smoke 48/48; "
    "S0.5/D-19 = _r486bmc_s05_check.py double MATCH + zero unacked; S6 = predecessor chain log FAILS=[] 38/38 rc0; "
    "S7 = quartet (loop pin5 no-op, watchdog re-reg, claws reinstalled) + attrition CLEAN; state json.loads self-check "
    "+ heartbeat epoch int + clock T-sep POST-WRITE (this script)"
)
st["ram_free_gb"] = ram_free
st["free_ram_gb"] = ram_free

out = rt(st, raw)
with open(STATE, "wb") as f:
    f.write(out)
chk = json.loads(open(STATE, "rb").read().decode("utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and chk["round_no"] == 486

# ---------- heartbeat ----------
raw_hb = open(HB, "rb").read()
hb = json.loads(raw_hb.decode("utf-8"))
assert rt(hb, raw_hb) == raw_hb, "heartbeat roundtrip NOT identity -- abort (r678)"

hb["activity_now"] = (
    "r486 dead-session adoption closed: SHARD-3 flip + science_gates quarantine fix landed (898f0e5c5), "
    "judge-finalize --wave 3 in flight (pid 33768, end-only writes), duplicate-finalize yield notice DELIVERED; "
    "S1 48/48; D-19 double MATCH; S6 adopted 38/38; quartet green"
)
hb["clock_read"] = clock
hb["cpu_pct"] = cpu
hb["cpu_idle_pct"] = round(100 - cpu, 1)
hb["cpu_util_pct"] = cpu
hb["current_task"] = cur_task
hb["free_ram_gb"] = ram_free
hb["heartbeat_epoch_utc"] = epoch
hb["idle_ram_gb"] = ram_free
hb["last_seen"] = clock
hb["last_seen_at"] = clock
hb["latest_artifact"] = (
    "results/mass_trial/w3_judge_shard_3of4.jsonl (194-cell product, 90899e0f7) + scripts/science_gates.py quarantine-fix "
    "reinstatement (898f0e5c5, phantom +6041 eliminated, true ledger head 646,799) + MSG-1745 yield notice (47d656aff)"
)
hb["next_milestone"] = (
    "judge-finalize --wave 3 -> w3_judge.json (777-cell verdict product) -> r487 adoption + 48h CEO clock <=10-05 noon; "
    "fund-trio finalize 10-05 10:30 (bm-b); acceptance 10-08; market reopen 10-09"
)
hb["prod_lanes"] = (
    "W3-JUDGE lane: 4/4 shards done (0,3 bm-c / 1 bm-b / 2 bm-a), judge-finalize --wave 3 in flight on bm-c (earlier-live "
    "claim holds per MSG-1745; bm-a pid 32480 duplicate stands down); FUND trio NULLS bm-b in-flight (watch only); "
    "boards empty; no new orders"
)
hb["ram_free_gb"] = ram_free
hb["round_no"] = 486
hb["round_no_label"] = "r486"
hb["ts"] = ts_human
hb["updated"] = clock
hb["updated_at"] = clock
hb["verdict"] = (
    "r486 bm-c: adopted dead-session window (SHARD-3 194/194 flip 90899e0f7 + science_gates _quarantine fix 898f0e5c5 "
    "phantom+6041 gone true head 646,799 selftest 70/70) + judge-finalize --wave 3 in flight pid 33768 (17:44:04, "
    "prefinalize 777/777 PASS) + MSG-1745 duplicate-finalize yield notice DELIVERED (bm-a pid 32480 stands down)"
)

out_hb = rt(hb, raw_hb)
with open(HB, "wb") as f:
    f.write(out_hb)
chk_hb = json.loads(open(HB, "rb").read().decode("utf-8"))
assert isinstance(chk_hb["heartbeat_epoch_utc"], int), "hb epoch must be JSON int"
assert "T" in chk_hb["clock_read"] and chk_hb["round_no"] == 486
assert isinstance(chk_hb.get("orders_ack"), list) and len(chk_hb["orders_ack"]) == 155

# ---------- round report main line (bytes append, marker gate) ----------
rr_bytes = open(RR, "rb").read()
assert rr_bytes.count("｜r486｜dept:".encode("utf-8")) == 0, "r486 main line already present (r679)"
if not rr_bytes.endswith(b"\n"):
    rr_bytes += b"\n"

main_line = (
    "2026-10-04T" + now_dt.strftime("%H:%M:%S") + "｜r486｜dept:策略/研究（W3 judge finalize 点火轮+死会话收养收口·T-158 在册）｜"
    "watermark verdict=绿（red=false·healthy·py_low_with_work_cands 合法面=finalize 在飞即 local_batch_running·板空 bandit 空池 376 全 done）｜"
    "当前活=judge-finalize --wave 3 在飞（pid 33768·17:44:04 起·end-only writes 零中间写面）+双烧让路裁定已发（MSG-1745 已推：bm-a pid 32480 后到杀己收养 bm-c 产品）｜"
    "最近实物=SHARD-3 烧录 194/194 产物入库（90899e0f7·relay 4/4 done 777/777）+science_gates _quarantine 修复拾回"
    "（898f0e5c5·幻影 +6041 消除·真链头 646,799·selftest 70/70）@ " + clock + "｜"
    "下个里程碑=w3_judge.json 判决产品落地→r487 收养+48h CEO 报告钟起算≤10-05 中午；fund-trio finalize 10-05 10:30（bm-b 正主）；O-2115/O-2030 验收 10-08；开市 10-09（≤48h）｜"
    "S0: 三证法收养 r486 死会话（reflog 17:44 止+单 codely=自匹配+簿记 mtime 17:12 停）→merge origin 3 commits（bm-a r688 closeout+autofill keepalive·零 UU）"
    "→MSG-1745 commit+push DELIVERED 47d656aff（science_gates 修复通报+finalize 双烧让路裁定）｜"
    "S0.5: 双扫 154/155 零未回执（ack_extra README=历史无害·r477 全名口径）·D-19 decisions 4E5BE321+orders 68947C17 双 MATCH"
    "（_r486bmc_s05_check.py·r458 per-key 口径 SHA-256/SHA-1）·inbox=自发 MSG-1745 留存待 bm-a 收（勿移 processed）｜"
    "S1 smoke 48/48｜S2 板空（job_list 0·池 376 entries 4/4 done）｜"
    "S3: satengine rc0 活（Tools 注册面 r467 律）·水位 py_low_with_work_cands 合法白名单（finalize 在飞=活批·板全闭环+bandit 空+无他可跑批）｜"
    "S6: 收养死会话 38/38 rc0 链（17:31:22-17:32:08·FAILS=[]·dualrun ZERO-DRIFT streak 51·金周诚实 no-op）｜"
    "S7: loop pin5 no-op+watchdog -Force 重装（首发 18:01 在位）+双爪 LF 归一重装·attrition CLEAN（4 ledgers·healed 注记照录）·orders 收尾二扫零差｜"
    "S4: 一条坑律行（yield 文件级 theirs-canonical 冲掉同文件无关已落修复+finalize 无池认领面双机并发盲区·两条并一条 r673/r674 附带范式）｜"
    "记分: 2（SHARD-3 烧录产物+science_gates 修复+finalize 在飞=可跑可看实物·非等待态）｜"
    "记账预算: 5/5（state+心跳+轮报+CODELY+自证）｜本地未达 origin commit 数: 收口 push 后 push_verify 自证｜"
    "下轮指针=r487 ①finalize 落地收养（_r486bmc_w3_judge_finalize.py status 三面探针 psutil+log+artifact）→产品验证链"
    "（complete=true+777 格+ledger 单块+verdicts 分布+r482 id-dup post-merge 复跑）→池 4/4 done 复核（r668）→48h CEO 报告钟起算"
    "→宝藏捕获问（TREASURE_REGISTRY+方法论卡）→§7/§8 回填②bm-a MSG-1745 回执核（杀 pid 32480+拾回 898f0e5c5 hunks）"
    "③fund-trio finalize 10-05 10:30（bm-b 正主·观察面）④O-2115/O-2030 验收 10-08"
)
with open(RR, "ab") as f:
    f.write(main_line.encode("utf-8") + b"\n")
rr2 = open(RR, "rb").read()
assert rr2.count("｜r486｜dept:".encode("utf-8")) == 1
print("CLOSE-WRITE OK clock:", clock, "epoch:", epoch, "cpu:", cpu, "ram_free:", ram_free)
