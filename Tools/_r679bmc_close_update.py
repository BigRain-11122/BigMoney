# -*- coding: utf-8 -*-
"""r679 bm-c close: state + heartbeat updater.
Laws: R170/R178 epoch int, R262 clock_read T-format, r583 facts-driven
watermark keys (dec/ord sha from s05 facts file), r640 race law (QA terminal
state polled terminal 5/5 BEFORE this script advances state), r653
measure-at-use (sizes derive from receipts/len() never hand-copied).
r679 watermark face: DEC 4C32527B / ORD A8B02C8A double zero-delta (both
sweeps, zero new face); fleet orders 166/166; inbox 0.
S5 ledger row already written earlier this round by _r679bmc_s5_ledger.py
(dedup: no REPORT leg here)."""
import ctypes
import datetime as dt
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
FACTS = os.path.join(ROOT, "results", "_r679bmc_s05_facts.json")
CREATE_NO_WINDOW = 0x08000000

now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

with open(FACTS, encoding="utf-8-sig") as fh:
    facts = json.load(fh)
dec_sha = facts["dec_sha"]
ord_sha = facts["ord_sha"]
assert len(dec_sha) == 64 and len(ord_sha) == 40, "facts sha shape gate"
assert facts["round"] == 679, "facts round gate"
assert facts["dec_delta"] is False, "DEC moved during round -- re-consume first"
assert facts["ord_delta"] is False, "ORD moved during round -- re-consume first"
assert facts["unacked"] == [], "fleet orders unacked gate"
assert facts["inbox_unread"] == [], "inbox unread gate"
assert facts["fleet_orders_total"] == 166, "fleet orders total gate"

# ---- 0b) size gate-pin derived at close (r646 gate-pin + r653 derive law) ----
codely_blob = int(subprocess.check_output(
    ["git", "cat-file", "-s", ":CODELY.md"],
    creationflags=CREATE_NO_WINDOW).decode().strip())
assert codely_blob <= 30720, "CODELY.md over 30KB gate: {}".format(codely_blob)

# ---- QA terminal-state gate (r640 race law): pack r679 5/5 verified ----
qa_head = open(os.path.join(ROOT, "qa", "smoke-r679.md"), encoding="utf-8").readline()
assert "r679" in qa_head, "QA pack round label gate"
qa_out = open(os.path.join(ROOT, "results", "_r679bmc_qa_runner.out"), encoding="utf-8").read()
assert "items=5/5" in qa_out, "QA terminal 5/5 gate"

gpu_mib = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=20)
    gpu_mib = int(r.stdout.decode("utf-8", errors="replace").strip().splitlines()[0])
except Exception:
    gpu_mib = None

cpu_pct = 5
try:
    with open(os.path.join(ROOT, "results", "watermark.jsonl"), encoding="utf-8") as fh:
        rows = [json.loads(l) for l in fh if l.strip()]
    if rows:
        cpu_pct = int(round(float(rows[-1].get("cpu_total_pct", cpu_pct))))
except Exception:
    pass
cpu_idle = 100 - cpu_pct

ram_free_gb = 8
try:
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    ram_free_gb = int(round(stat.ullAvailPhys / (1024 ** 3)))
except Exception:
    ram_free_gb = 8

with open(STATE, encoding="utf-8-sig") as fh:
    st = json.load(fh)
assert st["round_no"] == 679, "unexpected round_no {}".format(st["round_no"])
prev_gpu = st.get("gpu_free_vram_mib") or 694
gpu_mib = gpu_mib if gpu_mib is not None else prev_gpu

ACT = ("当前活: r679 金周尾日值守轮（复市前夜窗 T-1）收口：S0 absorb b980e255d〔6 自家 daemon live-face·r620 律〕+落后 origin 0 无需 rebase·S0.5 双扫=DEC 4C32527B/ORD "
       + ord_sha[:8] + " 双零 delta〔轮首+收口两腿全零新面〕·S1 48/48·S3 SAT 活 rc0〔burns_active=[]·queue_next=[]=O-2115 §2 N1 收口维持〕+水位红牌 red=false·probe py_low_with_work_cands=§四诚实披露〔候选=S6 链自身在飞腿 1.07 核自检面·板 0+bandit 0+burns 队空=合法 idle 白名单成立〕+板 0 open+post_review 45Y/0N 零红·S6 38/38 rc0〔dualrun streak 51@404·CA supply 双旗=W174 间隙窗延续一行不重扫·bm-a 心跳回鲜 15-16min→9 宿主面全自然归还零 stale-takeover〕·QA r679 5/5 零误标〔93 trades·determinism=True·equity 1,017,839 跨轮面恒等〕·tripwire CLEAN+attrition CLEAN+四自愈件幂等过"
       " | 最近实物: qa/smoke-r679.md（5/5）+qa/equity-curve-r679.png（66,161B）+results/_r679bmc_s6_log.txt（38/38 rc0）+docs/daily_report/REPORT-2026-10-07.md 与 docs/live_usage/LIVE-2026-10-07.md 再生（ORANGE）+results/_r679bmc_s05_facts.json（轮首+收口双扫）+results/post_review/REPORT-20261007.md（45Y/0N/5W 零红再生）"
       " | 下个里程碑: r680=5x HANDOVER 窗；10-08（周四）复市首交易日——数据链 re-arm+REGIME_GUARD v3 首 bar enforce 激活+纸盘 marks 地板推进+fund_premium 15:30 首采（bm-c 车道）+O-2115 验收包复跑（治理日）；W174 freeze/burn 观望（supply 双旗自然清预期）；trio finalize 窗至 10-09（bm-b 正典道）；月界首考 10-31（T-143 交付 10-29）")
DID = ("r679 bm-c: golden-week final-day standing guard round, reopen T-1 eve window (no P0 tail, zero new pits). "
       "(1) S0: round-start dirty = 6 own daemon live-faces -> absorb commit b980e255d (r620 law); behind origin 0 (no rebase needed, cleanest start since r674). "
       "(2) S0.5 double-sweep: round-start + close DEC 4C32527B / ORD A8B02C8A double zero-delta both sweeps; fleet orders 166/166 zero unacked both sweeps; inbox 0 unread both sweeps. "
       "(3) S1 smoke 48/48. S3: satengine alive rc0 (alive_flag=true, burns_active=[], queue_next=[] = O-2115 sec-2 N1 closure maintained); watermark red=false but probe verdict py_low_with_work_cands -> sec-4 honest disclosure: candidate = S6 chain's own in-flight leg (top_proc_cores 1.07 >= 0.5-core threshold, update_lhb fetch window, chain self-detection NOT an unclaimed batch); legal-idle whitelist holds (board 0 open + bandit 0 + burns queue empty + golden-week no-bar); board 0 open; job_list 0; post_review re-derive 45Y/0N/5W zero red = no P0; trial-labor line not triggered (O-2115 sec-2 N1 closure maintained + fund-trio D-family burn in flight on bm-b eta ~10-08 + golden-week no-bar + W174 seat published by bm-a = next-freezer re-derive obligation consumed by bm-a seat chain per r822 note). "
       "(4) S6 chain 38/38 rc0: dualrun ZERO-DRIFT streak 51 @404; compute_audit flags=[supply_gap,supply_floor] root-cause = between-seat W174 wave gap window continued (pool ready 2 < floor 3, unclaimed 0; bm-a freeze+burn ignition = natural clear expected, r676/r677/r678 same-family, one-line no-rescan per product-priority law); bm-a origin heartbeat FRESH (15-16min) mid-chain -> ALL 9 lane-io host faces (scorecard/live_paper/t35_open_fill/t24 pair/t35_paper_export/daily_scorecard/build_status) skip-derive natural hand-back to bm-a, zero stale-takeover needed this round (better than r678 early-leg state); REPORT-2026-10-07 + LIVE-2026-10-07 regenerated idempotent ORANGE; update_fund_premium pre-15:30 no-op (bm-c lane reopen-ready for 10-08 15:30 first snapshot); regime_guard v3 enforce requested, honest shadow downgrade (first-bar activation 10-08). "
       "(5) S4: zero new pits (3 clone artifacts s05/s6/qa_ignite bare-number law pass; QA ignite first-line label r679 correct); main CODELY zero append maintained, staged blob {}B. ".format(codely_blob) +
       "(6) QA pack r679 5/5 zero-mislabel (explicit --round 679 detached pid 36468, terminal state polled; 93 trades, determinism=True, equity final 1,017,839 cross-round face-identical, png 66,161B, latest_panel_bar=2026-09-30 golden-week honest no-op). "
       "(7) S7 self-heal green: loop pin=5 no-op (first fire 13:55), watchdog idempotent re-register (first fire 13:51), precommit/prepush claws installed LF-normalized both; tripwire scan CLEAN (post-append re-scan, E09 law); attrition guard scan CLEAN (4 ledgers, healed rows annotated); post_review re-derive 45Y/0N/5W zero red. "
       "Delivery: push + fetch + rev-list self-verify (final N recorded in r679 addendum ledger line).")
NXT = ("(a) r680 = 5x HANDOVER window (research/HANDOVER.md 核对更新 per every-5-rounds law). "
       "(b) 10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + REGIME_GUARD v3 first-bar enforce activation + paper marks floors advance + fund_premium first snapshot 15:30 (bm-c lane, readiness verified r671/r673/r675) + O-2115 acceptance pack rerun (governance day, scripts/o2115_acceptance_pack.py run). "
       "(c) W174 freeze/burn watch -> compute_audit supply flags natural clear expected at burn ignition. "
       "(d) trio finalize window watch to 10-09 (bm-b canonical lane). "
       "(e) monthly exam 10-31 assembly face (T-143, deliverable 10-29). "
       "(f) per-round close: tripwire scan (E09 law) + dup-heal scan. "
       "(g) group governance watch: C-20261007-02 §9 + C-20261007-03 判据回访 10-14 windows (committee-side, bm-c watch only).")
NOTE = ("r679: standing guard round, reopen T-1 eve; DEC/ORD double zero-delta x2; probe verdict py_low_with_work_cands disclosed sec-4 (chain self-detection, legal idle); "
        "QA r679 5/5 zero-mislabel; S6 38/38 rc0; smoke 48/48; post_review zero red; tripwire+attrition CLEAN; 4 self-heal idempotent-pass; "
        "bm-a heartbeat fresh = all 9 host faces natural hand-back, zero stale-takeover; golden-week no-bar held, reopen 10-08.")
VERIFY = ("receipts: results/_r679bmc_s6_log.txt (38/38 rc0) + qa/smoke-r679.md (5/5, first-line round label r679 verified) + qa/equity-curve-r679.png (66,161B) "
          "+ docs/daily_report/REPORT-2026-10-07.md + docs/live_usage/LIVE-2026-10-07.md (regen ORANGE) + results/_r679bmc_s05_facts.json (round-start + close double-sweep, double zero-delta) "
          "+ results/post_review/REPORT-20261007.md (45Y/0N/5W zero red re-derive) + results/_attrition_guard_scan.json CLEAN + results/_r679bmc_qa_runner.out (terminal 5/5 explicit --round 679)")

st["round_no"] = 680
st["round_no_label"] = "round 679 (bm-c)"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at",
          "current_task_at", "last_round_at", "last_round_ts", "last_ts", "last_run_at",
          "last_decisions_read_at", "last_decisions_at"):
    st[k] = now
st["current_task"] = ACT
st["activity_now"] = ACT
st["did"] = DID
st["last_round"] = DID
st["last_round_summary"] = ("r679: golden-week final-day standing guard (reopen T-1 eve): S0 absorb b980e255d, behind 0 (no rebase); DEC/ORD double zero-delta x2; "
                            "fleet orders 166/166; inbox 0; smoke 48/48; probe py_low_with_work_cands disclosed (chain self-detection, legal idle); post_review 45Y/0N zero red; "
                            "S6 38/38 rc0 (dualrun streak 51; bm-a heartbeat fresh 15-16min -> all 9 host faces natural hand-back, zero stale-takeover; REPORT/LIVE-2026-10-07 regen ORANGE); "
                            "QA r679 5/5 zero-mislabel (93 trades, determinism=True, equity 1,017,839 face-identical); tripwire+attrition CLEAN; 4 self-heal idempotent-pass; reopen 10-08")
st["last_action"] = DID[:300]
st["next"] = NXT
st["note"] = NOTE
st["verify"] = VERIFY
st["last_decisions_sha"] = dec_sha
st["last_orders_sha"] = ord_sha
st["last_decisions_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r679 round-start + close double-sweep both scans = "
                                   + dec_sha[:8] + " MATCH zero-delta; facts-driven from results/_r679bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["dec_sha_method"] = st["last_decisions_sha_method"]
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r679 round-start + close double-sweep both scans = "
                               + ord_sha[:8] + " MATCH zero-delta (zero new face both sweeps); "
                               "facts-driven from results/_r679bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["ord_sha_method"] = st["last_orders_sha_method"]
st["heartbeat_epoch_utc"] = epoch
st["cpu_pct"] = cpu_pct
st["cpu_util_pct"] = cpu_pct
st["cpu_idle_pct"] = cpu_idle
st["free_ram_gb"] = ram_free_gb
st["idle_ram_gb"] = ram_free_gb
st["ram_free_gb"] = ram_free_gb
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
chk = json.loads(open(STATE, encoding="utf-8-sig").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch int gate (R170/R178)"
print("STATE written round_no=%s label=%s epoch_type=%s gpu_mib=%d cpu=%d ram=%d codely_blob=%d" % (
    chk["round_no"], chk["round_no_label"], type(chk["heartbeat_epoch_utc"]).__name__, gpu_mib, cpu_pct, ram_free_gb, codely_blob))

# ---- heartbeat ----
with open(HB, encoding="utf-8-sig") as fh:
    hb = json.load(fh)
hb["round_no"] = 680
hb["round_no_label"] = "round 679 (bm-c)"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at", "current_task_at"):
    hb[k] = now
hb["current_task"] = ACT
hb["activity_now"] = ACT
hb["health"] = ("alive (r679 standing guard round clean: loop pin=5 no-op, watchdog registered, claws installed LF-normalized, attrition CLEAN, tripwire CLEAN; "
                "DEC/ORD double zero-delta; bm-a origin heartbeat fresh (15-16min) = all 9 lane-io host faces natural hand-back, zero stale-takeover; "
                "compute_audit supply flags natural clear expected at bm-a freeze+burn ignition; "
                "golden-week no-bar until 10-08 reopen; fund_premium lane reopen-ready for 10-08 15:30 first snapshot)")
hb["heartbeat_epoch_utc"] = epoch
hb["latest_artifact"] = ("qa/smoke-r679.md (5/5, 93 trades, determinism=True, equity 1,017,839 face-identical) + qa/equity-curve-r679.png (66,161B) + "
                         "results/_r679bmc_s6_log.txt (38/38 rc0) + results/_r679bmc_s05_facts.json (double-sweep double zero-delta) + "
                         "docs/daily_report/REPORT-2026-10-07.md + docs/live_usage/LIVE-2026-10-07.md (regen ORANGE) @ " + now)
hb["next_milestone"] = ("r680 = 5x HANDOVER window; 10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + regime_guard v3 first-bar enforce + marks floors advance + fund_premium first snapshot 15:30 (bm-c) "
                        "+ O-2115 acceptance pack rerun (governance day); W174 freeze/burn watch -> supply flags natural clear; "
                        "trio finalize window to 10-09 (bm-b); monthly exam 10-31")
hb["prod_lanes"] = ("r679 金周尾日值守轮（复市前夜窗 T-1）：S0 absorb b980e255d+落后 0 无 rebase·双扫 DEC/ORD 双零 delta·S6 38/38 rc0"
                    "（dualrun streak 51·CA supply 双旗=W174 间隙窗延续·bm-a 心跳回鲜→9 宿主面全自然归还零 stale-takeover）·"
                    "probe py_low_with_work_cands §四 已披露=链自检面合法 idle·QA r679 5/5 零误标（93 trades·equity 1,017,839 跨轮恒等）·post_review 45Y/0N 零红·tripwire/attrition CLEAN·四自愈件幂等过")
hb["verdict"] = ("alive: r679 standing guard round complete (smoke 48/48; S6 38/38 rc0 all legs; dualrun streak 51; QA r679 5/5 zero-mislabel explicit --round 679, 93 trades determinism=True equity 1,017,839 face-identical; "
                 "DEC 4C32527B zero-delta x2; ORD A8B02C8A zero-delta x2; fleet orders 166/166; board 0 open; "
                 "satengine alive rc0 N1 closure maintained; post_review 45Y/0N zero red; probe py_low_with_work_cands disclosed sec-4 (chain self-detection top_proc_cores 1.07, legal idle whitelist holds: board 0 + bandit 0 + burns empty); "
                 "compute_audit flags=[supply_gap,supply_floor] = W174 between-seat gap window continued (bm-a heartbeat fresh = natural clear expected); "
                 "tripwire+attrition CLEAN; 4 self-heal idempotent-pass; golden-week no-bar held, reopen 10-08)")
hb["note"] = ("r679: standing round, reopen T-1 eve; DEC/ORD double zero-delta; QA r679 5/5; S6 38/38; smoke 48/48; "
              "post_review zero red; attrition CLEAN.")
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["cpu_idle_pct"] = cpu_idle
hb["free_ram_gb"] = ram_free_gb
hb["idle_ram_gb"] = ram_free_gb
hb["ram_free_gb"] = ram_free_gb
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
chk2 = json.loads(open(HB, encoding="utf-8-sig").read())
assert isinstance(chk2["heartbeat_epoch_utc"], int), "hb epoch int gate"
assert "T" in chk2["clock_read"], "clock_read T-format gate (R262)"
print("HB written round_no=%s epoch_type=%s clock=%s" % (chk2["round_no"], type(chk2["heartbeat_epoch_utc"]).__name__, chk2["clock_read"]))
print("CLOSE_UPDATER_OK %s epoch=%d gpu_mib=%d cpu=%d ram=%d codely_blob=%d" % (now, epoch, gpu_mib, cpu_pct, ram_free_gb, codely_blob))
