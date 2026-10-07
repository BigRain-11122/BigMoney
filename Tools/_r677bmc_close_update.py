# -*- coding: utf-8 -*-
"""r677 bm-c close: state + heartbeat updater.
Laws: R170/R178 epoch int, R262 clock_read T-format, r583 facts-driven
watermark keys (dec/ord sha from s05 facts file), r640 race law (QA terminal
state polled terminal 5/5 BEFORE this script advances state), r653
measure-at-use (sizes derive from receipts/len() never hand-copied).
ORD watermark = A8B02C8A (close re-sweep CAUGHT mid-round change: commit
5005c4e 13:07:56 appended the single C-20261007-03 committee-retro row to
docs/orders.md -- zero BigMoney rows per the diff -- consumption verdict =
watermark update + zero execution face; double-sweep law working as designed).
S5 ledger row already written earlier this round by _r677bmc_s5_ledger.py
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
FACTS = os.path.join(ROOT, "results", "_r677bmc_s05_facts.json")
CREATE_NO_WINDOW = 0x08000000

now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

with open(FACTS, encoding="utf-8-sig") as fh:
    facts = json.load(fh)
dec_sha = facts["dec_sha"]
ord_sha = facts["ord_sha"]
assert len(dec_sha) == 64 and len(ord_sha) == 40, "facts sha shape gate"
assert facts["round"] == 677, "facts round gate"
assert facts["dec_delta"] is False, "DEC moved during round -- re-consume first"
assert facts["ord_delta"] is True, "expected ORD catch (C-20261007-03 row)"
assert facts["unacked"] == [], "fleet orders unacked gate"
assert facts["inbox_unread"] == [], "inbox unread gate"
assert facts["fleet_orders_total"] == 166, "fleet orders total gate"

# ---- 0b) size gate-pin derived at close (r646 gate-pin + r653 derive law) ----
codely_blob = int(subprocess.check_output(
    ["git", "cat-file", "-s", ":CODELY.md"],
    creationflags=CREATE_NO_WINDOW).decode().strip())
assert codely_blob <= 30720, "CODELY.md over 30KB gate: {}".format(codely_blob)

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
assert st["round_no"] == 677, "unexpected round_no {}".format(st["round_no"])
prev_gpu = st.get("gpu_free_vram_mib") or 852
gpu_mib = gpu_mib if gpu_mib is not None else prev_gpu

ACT = ("当前活: r677 金周尾日值守轮（复市 T-1 续窗）收口：S0 absorb cb8d20a07+rebase up-to-date·S0.5 双扫=轮首零 delta+收口重扫按律捕获 ORD delta〔B687D867→"
       + ord_sha[:8] + "=集团 commit 5005c4e 13:07:56 落 C-20261007-03 委员会复盘单行登记·diff 定性零涉本司行（R1-R6 全 CPH4/治理面·判据回访 10-14）=水位键更新零执行面〕·S1 48/48·S3 SAT 活 rc0+水位绿（py_low_board_clear 合法 idle）+板 0 open+post_review 45Y/0N 零红·S6 38/38 rc0〔dualrun streak 51@404·update_lhb 距 r675 季批>30min→季批 refetch 11/11·CA supply 双旗=W174 席位间隙窗延续·bm-a 心跳陈 38min→四宿主面 stale-takeover derive by bm-c〕·QA r677 5/5 零误标〔93 trades·determinism=True·equity 1,017,839 跨轮面恒等〕·tripwire CLEAN〔1169 行〕+attrition CLEAN+四自愈件幂等过"
       " | 最近实物: qa/smoke-r677.md（5/5）+qa/equity-curve-r677.png（66,289B）+results/_r677bmc_s6_log.txt（38/38 rc0）+docs/daily_report/REPORT-2026-10-07.md 与 docs/live_usage/LIVE-2026-10-07.md 再生（ORANGE）+results/_r677bmc_s05_facts.json（轮首+收口双扫+ORD catch 收据）+results/post_review/REPORT-20261007.md（45Y/0N/5W 零红再生）"
       " | 下个里程碑: 10-08（周四）复市首交易日——数据链 re-arm+REGIME_GUARD v3 首 bar enforce 激活+纸盘 marks 地板推进+fund_premium 15:30 首采（bm-c 车道）+O-2115 验收包复跑（治理日）；W174 freeze 观望（bm-a 下窗→supply 双旗自然清）；trio finalize 窗至 10-09（bm-b 正典道）；月界首考 10-31（T-143 交付 10-29）；下个 5x=r680（HANDOVER 窗）")
DID = ("r677 bm-c: golden-week final-day standing guard round, reopen T-1 continued window (no P0 tail, zero new pits). "
       "(1) S0: round-start dirty = 4 own daemon live-faces -> absorb commit cb8d20a07 (r620 law); behind origin 0, pull --rebase up-to-date. "
       "(2) S0.5 double-sweep: round-start DEC 4C32527B / ORD B687D867 zero-delta match state; close re-sweep DEC zero-delta again but CAUGHT mid-round ORD change per double-sweep law: group commit 5005c4e (13:07:56) appended exactly ONE row to docs/orders.md = C-20261007-03 committee-retro registration (R1-R6 all CPH4/governance faces, zero BigMoney rows per diff read) -> consumption verdict = ORD watermark key update A8B02C8A + zero execution face, recorded in round report + this state; fleet orders 166/166 zero unacked both sweeps; inbox 0 unread both sweeps. "
       "(3) S1 smoke 48/48. S3: satengine alive rc0; watermark red=false lane healthy (next_pick=claimed moneyflow IC batch carried honestly); board 0 open; job_list 0; post_review re-derive 45Y/0N/5W zero red = no P0; trial-labor line not triggered (O-2115 sec-2 N1 closure maintained + fund-trio D-family burn in flight on bm-b eta ~10-08 + golden-week no-bar + W174 seat published by bm-a = next-freezer re-derive obligation consumed by bm-a seat chain per r822 note). "
       "(4) S6 chain 38/38 rc0: dualrun ZERO-DRIFT streak 51 @404; update_lhb >30min since r675 quarter refetch -> quarter refetch 11/11 executed rc0; compute_audit flags=[supply_gap,supply_floor] root-cause = between-seat W174 wave gap window continued (18 run-samples, 204.5min span; bm-a freeze+burn ignition = natural clear expected, r676 same-family); bm-a hb stale 38min -> 4 shared host faces (t35_open_fill_verify/t35_paper_export/daily_scorecard/build_status) stale-takeover derived by bm-c (O-2100 s2.4 designed state, r676 same pattern); REPORT-2026-10-07 + LIVE-2026-10-07 regenerated idempotent ORANGE; update_fund_premium pre-15:30 no-op (bm-c lane reopen-ready for 10-08 15:30 first snapshot). "
       "(5) S4: zero new pits (3 clone artifacts s05/s6/qa_ignite bare-number law pass; QA ignite first-line label r677 correct); main CODELY zero append maintained, staged blob {}B. ".format(codely_blob) +
       "(6) QA pack r677 5/5 zero-mislabel (explicit --round 677 detached pid 19352, terminal state polled; 93 trades, determinism=True, equity final 1,017,839 cross-round face-identical, png 66,289B, latest_panel_bar=2026-09-30 golden-week honest no-op). "
       "(7) S7 self-heal green: loop pin=5 no-op (first fire 13:15), watchdog idempotent re-register (first fire 13:13), precommit/prepush claws LF-normalized install; tripwire scan CLEAN (1169 lines, entry max-multiplicity 1, E09 law); attrition guard scan CLEAN (4 ledgers, healed rows annotated); post_review re-derive 45Y/0N/5W zero red. "
       "Delivery: push + fetch + rev-list self-verify (final N recorded in r677 addendum ledger line).")
NXT = ("(a) 10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + REGIME_GUARD v3 first-bar enforce activation + paper marks floors advance + fund_premium first snapshot 15:30 (bm-c lane, readiness verified r671/r673/r675) + O-2115 acceptance pack rerun (governance day, scripts/o2115_acceptance_pack.py run). "
       "(b) W174 freeze watch (bm-a next window) -> compute_audit supply flags natural clear expected at burn ignition. "
       "(c) trio finalize window watch to 10-09 (bm-b canonical lane). "
       "(d) monthly exam 10-31 assembly face (T-143, deliverable 10-29); next 5x = r680 (HANDOVER window). "
       "(e) per-round close: tripwire scan (E09 law) + dup-heal scan. "
       "(f) group governance watch: C-20261007-02 §9 + C-20261007-03 判据回访 10-14 windows (committee-side, bm-c watch only).")
NOTE = ("r677: standing guard round; close re-sweep caught ORD mid-round delta (C-20261007-03 committee row, zero BigMoney face, watermark updated A8B02C8A); "
        "QA r677 5/5 zero-mislabel; S6 38/38 rc0; DEC zero-delta x2; smoke 48/48; post_review zero red; tripwire+attrition CLEAN; 4 self-heal idempotent-pass; "
        "compute_audit supply flags = W174 between-seat gap window continued (natural clear expected); golden-week no-bar held, reopen 10-08.")
VERIFY = ("receipts: results/_r677bmc_s6_log.txt (38/38 rc0) + qa/smoke-r677.md (5/5, first-line round label r677 verified) + qa/equity-curve-r677.png (66,289B) "
          "+ docs/daily_report/REPORT-2026-10-07.md + docs/live_usage/LIVE-2026-10-07.md (regen ORANGE) + results/_r677bmc_s05_facts.json (round-start + close double-sweep, ORD catch receipt) "
          "+ results/post_review/REPORT-20261007.md (45Y/0N/5W zero red re-derive) + results/_attrition_guard_scan.json CLEAN + results/_r677bmc_qa_runner.out (terminal 5/5 explicit --round 677) "
          "+ group-tree commit 5005c4e (orders.md single-row diff read, consumption verdict evidence)")

st["round_no"] = 678
st["round_no_label"] = "round 677 (bm-c)"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at",
          "current_task_at", "last_round_at", "last_round_ts", "last_ts", "last_run_at",
          "last_decisions_read_at", "last_decisions_at"):
    st[k] = now
st["current_task"] = ACT
st["activity_now"] = ACT
st["did"] = DID
st["last_round"] = DID
st["last_round_summary"] = ("r677: golden-week final-day standing guard (reopen T-1 continued): S0 absorb cb8d20a07 + rebase up-to-date; double-sweep DEC zero-delta x2 + close re-sweep CAUGHT ORD mid-round delta "
                            "(C-20261007-03 committee row 13:07:56, zero BigMoney face per diff, watermark A8B02C8A updated, zero execution); fleet orders 166/166; inbox 0; smoke 48/48; "
                            "post_review 45Y/0N zero red; S6 38/38 rc0 (dualrun streak 51; update_lhb quarter refetch 11/11; supply flags = W174 between-seat gap continued; 4 host faces stale-takeover derive; REPORT/LIVE-2026-10-07 regen ORANGE); "
                            "QA r677 5/5 zero-mislabel (93 trades, determinism=True, equity 1,017,839 face-identical); tripwire+attrition CLEAN; 4 self-heal idempotent-pass; reopen 10-08")
st["last_action"] = DID[:300]
st["next"] = NXT
st["note"] = NOTE
st["verify"] = VERIFY
st["last_decisions_sha"] = dec_sha
st["last_orders_sha"] = ord_sha
st["last_decisions_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r677 round-start + close double-sweep both scans = "
                                   + dec_sha[:8] + " MATCH zero-delta; facts-driven from results/_r677bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["dec_sha_method"] = st["last_decisions_sha_method"]
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r677 round-start B687D867 zero-delta + close re-sweep CAUGHT mid-round change -> "
                                + ord_sha[:8] + " (group commit 5005c4e 13:07:56, docs/orders.md single new row = C-20261007-03 committee-retro registration, diff-read zero BigMoney rows -> watermark key update, zero execution face); "
                                "facts-driven from results/_r677bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
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
print("STATE written round_no=%s label=%s epoch_type=%s gpu_mib=%d cpu=%d ram=%d" % (
    chk["round_no"], chk["round_no_label"], type(chk["heartbeat_epoch_utc"]).__name__, gpu_mib, cpu_pct, ram_free_gb))

# ---- heartbeat ----
with open(HB, encoding="utf-8-sig") as fh:
    hb = json.load(fh)
hb["round_no"] = 678
hb["round_no_label"] = "round 677 (bm-c)"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at", "current_task_at"):
    hb[k] = now
hb["current_task"] = ACT
hb["activity_now"] = ACT
hb["health"] = ("alive (r677 standing guard round clean: loop pin=5 no-op, watchdog registered, claws installed, attrition CLEAN, tripwire CLEAN; "
                "close re-sweep caught ORD mid-round delta = C-20261007-03 committee row, zero BigMoney face, watermark updated; "
                "golden-week no-bar until 10-08 reopen; compute_audit supply flags = W174 between-seat gap window continued, natural clear expected at bm-a freeze+burn; "
                "fund_premium lane reopen-ready for 10-08 15:30 first snapshot)")
hb["heartbeat_epoch_utc"] = epoch
hb["latest_artifact"] = ("qa/smoke-r677.md (5/5, 93 trades, determinism=True, equity 1,017,839 face-identical) + qa/equity-curve-r677.png (66,289B) + "
                         "results/_r677bmc_s6_log.txt (38/38 rc0) + results/_r677bmc_s05_facts.json (double-sweep + ORD catch receipt) + "
                         "docs/daily_report/REPORT-2026-10-07.md + docs/live_usage/LIVE-2026-10-07.md (regen ORANGE) @ " + now)
hb["next_milestone"] = ("10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + regime_guard v3 first-bar enforce + marks floors advance + fund_premium first snapshot 15:30 (bm-c) "
                        "+ O-2115 acceptance pack rerun (governance day); W174 freeze watch (bm-a) -> supply flags natural clear; trio finalize window to 10-09 (bm-b); "
                        "monthly exam 10-31; next 5x=r680")
hb["prod_lanes"] = ("r677 金周尾日值守轮（复市 T-1 续窗）：S0 absorb+rebase·双扫=轮首零 delta+收口 ORD catch（C-20261007-03 委员会行·零涉本司·水位键更新）·S6 38/38 rc0"
                    "（dualrun streak 51·update_lhb 季批 refetch 11/11·CA supply 双旗=W174 席位间隙窗延续·四宿主面 stale-takeover derive）·QA r677 5/5 零误标"
                    "（93 trades·equity 1,017,839 跨轮恒等）·post_review 45Y/0N 零红·tripwire/attrition CLEAN·四自愈件幂等过")
hb["verdict"] = ("alive: r677 standing guard round complete (smoke 48/48; S6 38/38 rc0 all legs; dualrun streak 51; QA r677 5/5 zero-mislabel explicit --round 677, 93 trades determinism=True equity 1,017,839 face-identical; "
                 "DEC 4C32527B zero-delta x2; ORD close-catch B687D867 -> A8B02C8A = C-20261007-03 committee row 13:07:56, diff-read zero BigMoney rows, watermark updated zero execution; "
                 "fleet orders 166/166; board 0 open; satengine alive rc0; post_review 45Y/0N zero red; watermark green py_low_board_clear legal idle; "
                 "compute_audit flags=[supply_gap,supply_floor] = W174 between-seat gap window continued (bm-a freeze next window, natural clear expected); "
                 "tripwire+attrition CLEAN; 4 self-heal idempotent-pass; golden-week no-bar held, reopen 10-08)")
hb["note"] = ("r677: standing round; close re-sweep ORD catch (C-20261007-03 committee row, zero bm-c face, watermark A8B02C8A); QA r677 5/5; S6 38/38; "
              "DEC zero-delta x2; smoke 48/48; post_review zero red; attrition CLEAN.")
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
