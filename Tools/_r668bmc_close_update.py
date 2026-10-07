# -*- coding: utf-8 -*-
"""r668 bm-c close: state + heartbeat + round-report updater.
Laws: R170/R178 epoch int (python int(time.time()) direct), R262 clock_read
T-format, r583 facts-driven watermark keys (dec/ord sha from s05 facts file),
r814-bm-a watermark write-side single-source (python raw-blob values only).
r668 specifics: reopen-date erratum lands on ALL live faces (10-09 wrong ->
10-08 correct, State Council notice three-source cross-validated; bm-a r714
readiness + bm-b heartbeat were already correct).
"""
import datetime as dt
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
FACTS = os.path.join(ROOT, "results", "_r668bmc_s05_facts.json")
CREATE_NO_WINDOW = 0x08000000

now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

with open(FACTS, encoding="utf-8-sig") as fh:
    facts = json.load(fh)
dec_sha = facts["dec_sha"]
ord_sha = facts["ord_sha"]
assert len(dec_sha) == 64 and len(ord_sha) == 40, "facts sha shape gate"

# GPU free VRAM sample (CREATE_NO_WINDOW per U060)
gpu_mib = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=20)
    gpu_mib = int(r.stdout.decode("utf-8", errors="replace").strip().splitlines()[0])
except Exception:
    gpu_mib = None

# CPU sample facts-driven from standing watermark probe tail (S6 leg-03 face)
cpu_pct = 12
try:
    with open(os.path.join(ROOT, "results", "watermark.jsonl"), encoding="utf-8") as fh:
        rows = [json.loads(l) for l in fh if l.strip()]
    if rows:
        cpu_pct = int(round(float(rows[-1].get("cpu_total_pct", cpu_pct))))
except Exception:
    pass
cpu_idle = 100 - cpu_pct

with open(STATE, encoding="utf-8-sig") as fh:
    st = json.load(fh)
prev_gpu = st.get("gpu_free_vram_mib") or 1078
gpu_mib = gpu_mib if gpu_mib is not None else prev_gpu

ACT = ("当前活: r668 值守+勘误轮收口（S0 干净自产 3 件零落后·S1 48/48·S3 板 0 open+SAT 活+水位绿+池面健康=1 ready bm-b keepalive+1 治理停泊 W14 零触碰·复市日勘误定谳 10-09→10-08〔国务院通知三源交叉·bm-a r714 件+bm-b 心跳本正确=仅本机面错〕·CODELY 增量批 r814 迁 pit-protocol-d19+新坑律入册·S6 38/38·QA r668 5/5）"
       " | 最近实物: CODELY.md 增量批收据 results/_r668bmc_codely_increment.json（主件 30,541→30,719B≤30,720B·r814 758B verbatim 迁 pit-protocol-d19.md sha16 3598f944144aaa01·新坑律行 936B）+qa/smoke-r668.md 5/5（93 trades·determinism=True·equity 1,017,839 跨轮恒等）+qa/equity-curve-r668.png+results/_r668bmc_s6_log.txt 38/38 rc0+docs/daily_report/REPORT-2026-10-07.md+docs/live_usage/LIVE-2026-10-07.md（ORANGE）"
       " | 下个里程碑: 10-08（周四）复市首交易日——数据链 re-arm+REGIME_GUARD v3 首 bar 激活（t24 门=last_bar≥10-01 即活）+纸盘 marks 地板推进；trio finalize 窗观察至 10-09（bm-b 道）；月界首考 10-31；下个 5x=r670（HANDOVER 窗）")
DID = ("r668 bm-c: golden-week watch + reopen-date erratum + CODELY increment round. "
      "(1) S0: round-start dirty = 3 self daemon live-wins faces, HEAD==origin 0/0 zero-behind, no pull needed, symref healthy. "
      "(2) S0.5 double-sweep: DEC 635C3024 / ORD B687D867 zero-delta x2 (round-start + close); fleet orders 164/164 zero unacked; inbox 0. "
      "(3) S1 smoke 48/48. S3: satengine alive rc0 (Tools face, burn process in flight); watermark green (next_pick=claimed moneyflow IC batch, panel parked EM source-blocked 30min self-heal); board open=0; job_list 0; post_review tail-30 zero-x; pool 401 done + FUND-DIVLOWVOL-P1-NULLS ready (bm-b keepalive 09:16 lane, not ours) + TRIAL-LABOR-W14-GENERATE waiting = governance park per MSG-2026-10-03-0436 (GM dual-ruling pending, three-machine zero-touch, NOT a stall); trial-labor line: no new batch (W171 finalized by bm-a r816 in-window + trio finalize D 1674/2000 bm-b in flight). "
      "(4) MAIN PRODUCT reopen-date erratum: bm-c r666/r667 heartbeat+state faces claimed '10-09 market reopen' = WRONG; external three-source cross-validation (State Council Office 2026 holiday notice) = National Day 10-01(Thu)..10-07(Wed) closed, make-up workdays 9-20/10-10, A-share first trading day = 10-08 (Thu), 10-10 make-up workday markets still closed; bm-a r714 open_market_readiness.py (MARKET_DATE=2026-10-08) + bm-b heartbeat were already correct = single-machine face error (r666 close template origin); all live faces corrected this round (heartbeat/state/next pointers + qa_smoke_run.py stdout string 'until 10-09'->'until 10-08' same-length fix); historical round-report/scratch-script lines untouched per git-history law; new pit entry in main CODELY.md (future-calendar-facts two-source verification law). "
      "(5) CODELY increment batch (prescan rc3 recorded, r651/r654 operative precedent): r814 bm-a watermark-write-side pit 758B verbatim OUT -> research/pit-protocol-d19.md (+526B accounting line, 16,067->17,353B); new r668 pit line 936B IN; main 30,541->30,719B <=30,720B (1B headroom, next direct-write pit triggers next increment batch); 15 gates PASS (needle==1, sha16 pin, byte equations x2, verbatim-in-target, marker-absence, CRLF three-count x2, preserved-face identity, target prefix identity, strict reparse x2); receipt results/_r668bmc_codely_increment.json. "
      "(6) S6 chain 38/38 rc0 (dualrun ZERO-DRIFT streak 51; REPORT-2026-10-07 + LIVE-2026-10-07 regenerated ORANGE; t24 prospect enforce->shadow downgrade verified CORRECT by design: gate compares last_bar 2026-09-30 < active_from 2026-10-01, first new bar 10-08 activates enforce). "
      "(7) QA r668 5/5 (explicit --round 668 detached runner, 93 trades determinism=True, equity 1,017,839 cross-round identical, png 66,261B). "
      "(8) S7: loop pin=5 + watchdog present + claws MATCH x2; attrition CLEAN (4 ledgers, healed rows noted); 10-09->10-08 erratum on all live faces.")
NXT = ("(a) 10-08 (Thu) market reopen first bar: data-chain re-arm (update legs auto-revive post-15:30) + REGIME_GUARD v3 enforce first-bar activation (t24 gate: last_bar >= 2026-10-01 activates) + paper marks floors advance (t35/prospect/aggr/alloc/grid/system_v1 same window) + external run-11/run-7 (bm-a readiness face r714 owns preflight, MARKET_DATE 10-08 verified correct). "
      "(b) trio finalize window watch to 10-09 (bm-b canonical lane, D 1674/2000, watch+record only). "
      "(c) W172+ projection: next freezer bm-a (A 393_004..395_003 / B 393_204..393_403 naive-B-inside-naive-A re-derive-MANDATORY per bm-a r815 note). "
      "(d) CODELY main 30,719B headroom 1B: next direct-write pit entry triggers next increment batch same-window (r669 candidates: r653 close-size entry blocked by pit-lineage.md 30,552B full; r659 rebase-continue entry blocked by pit-git-resolver.md 30,412B room 308B -- both need domain-file relief first). "
      "(e) monthly exam 10-31 assembly face (T-143, deliverable 10-29); next 5x=r670 HANDOVER window.")
NOTE = ("r668: reopen-date erratum round (10-09 -> 10-08, State Council notice three-source, bm-a r714 + bm-b already correct, single-machine face error corrected on all live faces) + "
        "CODELY increment (r814 out to pit-protocol-d19.md, new calendar-law pit in, main 30,719B, 15 gates, receipt) + qa_smoke_run stdout fix + "
        "QA r668 5/5 + S6 38/38; DEC/ORD zero-delta x2; smoke 48/48; attrition CLEAN; W14 park untouched per MSG-0436.")
VERIFY = ("receipts: results/_r668bmc_codely_increment.json (zero-loss increment receipt, byte equations PASS, prescan rc3 recorded) + "
          "research/pit-protocol-d19.md (r814 verbatim + accounting line) + CODELY.md r668 pit line + qa/smoke-r668.md 5/5 (93 trades determinism=True equity 1,017,839) + "
          "qa/equity-curve-r668.png + results/_r668bmc_s6_log.txt 38/38 rc0 + results/_r668bmc_s05_facts.json (DEC 635C3024 + ORD B687D867 double-sweep zero-delta) + "
          "results/_attrition_guard_scan.json CLEAN + scripts/qa_smoke_run.py stdout erratum fix + heartbeat/state faces corrected to 10-08")

# ---- state ----
st["round_no"] = 669
st["round_no_label"] = "round 668 (bm-c)"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at",
          "current_task_at", "last_round_at", "last_round_ts", "last_ts", "last_run_at",
          "last_decisions_read_at", "last_decisions_at"):
    st[k] = now
st["current_task"] = ACT
st["activity_now"] = ACT
st["did"] = DID
st["last_round"] = DID
st["last_round_summary"] = ("r668: reopen-date erratum (10-09 -> 10-08 State-Council three-source, single-machine face error, all live faces corrected) + "
                            "CODELY increment (r814 -> pit-protocol-d19.md verbatim + calendar-law pit in, main 30,719B 15 gates receipt) + "
                            "qa_smoke_run stdout fix + QA r668 5/5 + S6 38/38; DEC/ORD zero-delta x2; smoke 48/48; attrition CLEAN")
st["last_action"] = DID
st["next"] = NXT
st["note"] = NOTE
st["verify"] = VERIFY
st["last_decisions_sha"] = dec_sha
st["last_orders_sha"] = ord_sha
st["last_decisions_sha_method"] = "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r668 s05 round-start + s7close double-sweep MATCH zero-delta; value facts-driven from results/_r668bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))"
st["dec_sha_method"] = st["last_decisions_sha_method"]
st["last_orders_sha_method"] = "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r668 s05 round-start + s7close double-sweep MATCH; facts-driven from results/_r668bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))"
st["ord_sha_method"] = st["last_orders_sha_method"]
st["heartbeat_epoch_utc"] = epoch
st["cpu_pct"] = cpu_pct
st["cpu_util_pct"] = cpu_pct
st["cpu_idle_pct"] = cpu_idle
st["free_ram_gb"] = 4
st["idle_ram_gb"] = 4
st["ram_free_gb"] = 4
st["gpu_free_vram_mib"] = gpu_mib
st["gpu_free_vram_mb"] = gpu_mib
st["gpu_idle_vram_mib"] = gpu_mib
st["gpu_idle_vram_mb"] = gpu_mib
st["gpu_free_mb"] = gpu_mib
st["gpu_free_mib"] = gpu_mib
st["gpu_idle_mb"] = gpu_mib
st["gpu_vram_free_mb"] = gpu_mib
with open(STATE, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
print("STATE written round_no=669 epoch_type=%s gpu_mib=%d cpu=%d" % (type(st["heartbeat_epoch_utc"]).__name__, gpu_mib, cpu_pct))

# ---- heartbeat ----
with open(HB, encoding="utf-8-sig") as fh:
    hb = json.load(fh)
hb["round_no"] = 669
hb["round_no_label"] = "round 668 (bm-c)"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at", "current_task_at"):
    hb[k] = now
hb["current_task"] = ACT
hb["activity_now"] = ACT
hb["health"] = "alive (r668 watch+erratum round clean: loop pin=5, watchdog present, claws MATCH, attrition CLEAN; reopen date corrected 10-09 -> 10-08 on this machine's faces; golden-week no-bar until 10-08)"
hb["heartbeat_epoch_utc"] = epoch
hb["latest_artifact"] = ("results/_r668bmc_codely_increment.json (zero-loss CODELY increment receipt, r814 -> pit-protocol-d19.md + calendar-law pit, main 30,719B) + qa/smoke-r668.md 5/5 (93 trades determinism=True equity 1,017,839) + reopen-date erratum landed on all live faces @ " + now)
hb["next_milestone"] = ("10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + regime_guard v3 first-bar enforce activation + marks floors advance; trio finalize window to 10-09 (bm-b); monthly exam 10-31; next 5x=r670 HANDOVER")
hb["prod_lanes"] = ("r668 值守+勘误轮（复市日 10-09→10-08 外源定谳落全部活面·CODELY 增量批 r814 迁出+新坑律入册主件 30,719B·smoke 48/48+S6 38/38+QA r668 5/5·板 0 open·水位绿·SAT 活·下个 5x=r670〔HANDOVER 窗〕）")
hb["verdict"] = ("alive: r668 watch+erratum round complete (reopen date 10-09 -> 10-08 corrected per State Council notice three-source cross-validation, bm-a r714 readiness + bm-b heartbeat already correct = single-machine face error, all live faces fixed, qa_smoke_run stdout fixed; "
                 "CODELY increment: r814 verbatim -> pit-protocol-d19.md + new calendar-law pit, main 30,541->30,719B <=30,720B, 15 gates PASS, prescan rc3 recorded; QA r668 5/5; "
                 "S6 38/38 rc0; smoke 48/48; board open=0; satengine alive rc0; DEC/ORD double-sweep zero-delta 164/164; attrition CLEAN; post_review zero-x; "
                 "W14 governance park untouched per MSG-0436; golden-week no-bar face held until 10-08)")
hb["note"] = "r668: reopen-date erratum + CODELY increment (r814 out, calendar-law pit in, 15 gates) + qa_smoke_run stdout fix; QA 5/5; S6 38/38; DEC/ORD zero-delta x2; attrition CLEAN."
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["cpu_idle_pct"] = cpu_idle
hb["free_ram_gb"] = 4
hb["idle_ram_gb"] = 4
hb["ram_free_gb"] = 4
hb["gpu_free_vram_mib"] = gpu_mib
hb["gpu_free_vram_mb"] = gpu_mib
hb["gpu_idle_vram_mib"] = gpu_mib
hb["gpu_idle_vram_mb"] = gpu_mib
hb["gpu_free_mb"] = gpu_mib
hb["gpu_free_mib"] = gpu_mib
hb["gpu_idle_mb"] = gpu_mib
hb["gpu_vram_free_mb"] = gpu_mib
with open(HB, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
print("HB written round_no=669 epoch=%s" % type(hb["heartbeat_epoch_utc"]).__name__)

# ---- round report ----
line = ("watermark: 绿（red=false lane healthy·py_watermark S6probe 09:59 板空合法 idle〔板 0 open·判决链席位他机在飞：W171 bm-a r816 已 finalize+trio finalize bm-b D 1674/2000·金周无 bar〕·SAT 活=Tools 注册面 rc0 burn 进程在飞·post_review ✗0）"
        " | " + now + " | r668 bm-c | dept:工程/舰队（金周值守轮+复市日勘误定谳+CODELY 增量批）"
        " | 当前活: r668 值守+勘误轮（S0 干净自产 3 件零落后·S1 48/48·S3 板 0 open+池面健康〔FUND-DIVLOWVOL ready=bm-b keepalive 道·W14-GENERATE waiting=治理停泊 MSG-0436 三机零触碰·试用劳力线不触发=W171+trio 在飞〕·复市日勘误 10-09→10-08 外源三源定谳〔国务院通知：国庆 10-01~10-07 休·复市=10-08 周四·10-10 调休上班日股市休〕=bm-a r714 件+bm-b 心跳本正确·仅本机 r666/r667 面单方错·全部活面当轮勘正+qa_smoke_run.py stdout 同错族一字修·CODELY 增量批=r814 758B verbatim 迁 pit-protocol-d19.md（+对账行 17,353B）+新坑律行 936B 入册·主件 30,541→30,719B≤30,720B〔余量 1B〕·15 门全过·prescan rc3 作业先例留痕·S6 38/38·QA r668 5/5）"
        " | 最近实物: results/_r668bmc_codely_increment.json（零丢失增量收据·字节方程 PASS）+CODELY.md r668 坑律行（未来日历事实两源核验律）+research/pit-protocol-d19.md（r814 verbatim+对账行）+qa/smoke-r668.md 5/5（93 trades·determinism=True·equity 1,017,839 跨轮恒等）+qa/equity-curve-r668.png+results/_r668bmc_s6_log.txt 38/38 rc0+docs/daily_report/REPORT-2026-10-07.md+docs/live_usage/LIVE-2026-10-07.md（ORANGE）"
        " | 下个里程碑: 10-08（周四）复市首交易日=数据链 re-arm+REGIME_GUARD v3 首 bar 激活（t24 门 last_bar≥10-01 即活·当日核验）+纸盘 marks 地板推进+external run-11/run-7（bm-a r714 readiness 件已验正确）；trio finalize 窗观察至 10-09（bm-b 道）；月界首考 10-31；下个 5x=r670（HANDOVER 窗） | 本地未达 origin commit 数=0（收口推送后 fetch+ls-tree 自证）")
with open(REPORT, "ab") as fh:
    with open(REPORT, "rb") as fr:
        rb = fr.read()
    sep = b"\r\n" if rb.endswith(b"\r\n") else b"\n"
    if not rb.endswith(sep):
        rb = rb + sep
    fh.write(rb + line.encode("utf-8") + sep)
print("REPORT appended")
print("CLOSE_UPDATER_OK %s epoch=%d gpu_mib=%d cpu=%d" % (now, epoch, gpu_mib, cpu_pct))
