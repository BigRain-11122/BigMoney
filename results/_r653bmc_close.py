# -*- coding: utf-8 -*-
# r653 bm-c close driver: (a) NO new pit this round -> zero CODELY.md append
# (law: pits land in main only when real); (b) S5 ledger line to canonical
# per-machine path (r645 epoch law); (c) state-bm-c round_no increment +
# summaries; (d) heartbeat with live metrics + 3-line CEO face; epoch int
# self-assert (smoke F7). ASCII-only console output. Pattern: _r652bmc_close.py.
import json, os, time, datetime, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---------- live metrics ----------
try:
    import psutil
    cpu = round(psutil.cpu_percent(interval=1.0), 1)
    ram_free = round(psutil.virtual_memory().available / (1 << 30), 1)
except Exception:
    cpu, ram_free = 0.0, 0.0
gpu_free = 0
try:
    g = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=0x08000000)
    gpu_free = int(g.stdout.decode("ascii", "replace").strip().splitlines()[0])
except Exception:
    gpu_free = 0

def load_json(p):
    raw = open(p, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return json.loads(raw.decode("utf-8-sig")), bom

def save_json(p, obj, bom):
    with open(p, "w", encoding="utf-8-sig" if bom else "utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)

# ---------- three-line CEO face ----------
face3 = ("当前活: r653 值守轮收口（黄金周无 bar：S0 定向 checkpoint+bm-b 波 rebase 干净+S6 38/38+QA 包 r653 显式轮标 5/5·零新坑零 CODELY append）"
         " | 最近实物: qa/smoke-r653.md（5/5·93 trades·determinism=True·equity 终值 1,017,839 面恒等 r642-652）"
         "+results/_r653bmc_s6_log.txt（38/38 rc0）+docs/live_usage/LIVE-2026-10-07.md（当日幂等再生成）"
         " @ {ts} | 下个里程碑: fund-trio Q 完成窗 pool dual-flip watch（r668 律）+D finalize ~10-08（bm-b 车道）；"
         "10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；月界首考 10-31；下个 5x=r655〔HANDOVER 窗〕").format(ts=TS)
latest = ("qa/smoke-r653.md 5/5 (explicit --round 653, pid 13300, 93 trades, determinism=True, equity 800 pts final 1,017,839 "
          "face-identical r642-652) + qa/equity-curve-r653.png + results/_r653bmc_s6_log.txt 38/38 rc0 "
          "+ results/_r653bmc_trio_watch.json (V 2000 complete, Q 1918, D 1590) @ {ts}").format(ts=TS)
milestone = ("fund-trio Q completion pool dual-flip watch (r668 law) + D finalize ~10-08 (bm-b lane); 10-09 market reopen "
             "(data-chain re-arm + regime_guard v3 first bar); monthly exam 10-31; next 5x = r655")

did = ("r653 bm-c: golden-week standing-guard round (zero new pits; no P0 tail). (1) S0: round-start dirty = r652 close-tail "
       "addendum + 2 sat-engine/autofill daemon faces + 2 r652 tail receipts -> targeted checkpoint (r642 law, post-rebase "
       "face 2f5df6eb7); pull brought bm-b in-flight wave (d18154b5e churn-absorb + autofill keepalive), rebase 1/1 clean. "
       "(2) S0.5 double-sweep (s05 + s7close): DEC 635C3024 / ORD 437E9CDD both MATCH zero-delta at both sweeps; fleet "
       "orders 163/163 zero unacked at both sweeps; inbox empty. (3) S1 smoke 48/48. S3: board open=0 (Codely jobs 0, fleet "
       "176 zero open, 46 claimed); watermark green (red=false, next_pick=claimed moneyflow IC source-blocked bm-a lane "
       "legal; py_watermark py_low_board_clear golden-week legal idle); SAT alive (Tools face status rc0, heartbeat 65s, "
       "queue present). Trio watch r653: V 2000/2000 COMPLETE, Q 1918/2000 (+10), D 1590/2000 (+9) -- bm-b rightful burner "
       "lane, pool FUND-QUALITY-P1-NULLS + FUND-DIVLOWVOL-P1-NULLS ready for bm-b (+ TRIAL-LABOR-W14-GENERATE waiting), no "
       "proxy burn by bm-c; trial-labor line satisfied by in-flight trio judge batches, no new drafting. (4) S6 chain 38/38 "
       "rc0 (dualrun ZERO-DRIFT streak 51 @403 unchanged face since 10-05 cutoff; compute_audit FLAG supply_gap,supply_floor "
       "= known golden-week structural face re-eval 10-09+; regime ORANGE shadow asof 09-30; bm-a heartbeat stale 72min -> "
       "bm-c stale-takeover derive per O-2100 s2.4 STALE_MIN law; CEO faces LIVE-2026-10-07 + REPORT-2026-10-07 + "
       "CALL-2026-09-30 cell ORA regenerated idempotent). (5) QA pack r653: detached pid 13300 with EXPLICIT --round 653 "
       "(r758/r640 law), polled terminal before close -- 5/5, 93 trades, determinism=True, equity 800 pts final 1,017,839 "
       "face-identical r642-r652. (6) Attrition guard CLEAN (4 ledgers, historical shrinks healed-annotated); loop pin=5 "
       "no-op; watchdog registered; claws reinstalled idempotent. Zero new pits this round; zero CODELY.md append (blob "
       "face 27,396B unchanged).")

verdict = ("alive: r653 standing-guard round complete (zero new pits, zero CODELY append, blob 27,396B headroom 3,324B; QA pack "
           "r653 5/5 explicit --round; S6 38/38 rc0; smoke 48/48; board open=0; satengine alive; DEC/ORD double-sweep "
           "zero-delta 163/163; attrition CLEAN; trio V complete Q1918/D1590 bm-b rightful lane; golden-week no-bar until 10-09)")

# ---------- (b) S5 ledger line (canonical path, r645 law) ----------
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
rb = open(RR, "rb").read()
assert rb.endswith(b"\r\n")
row = ("{ts} | r653 bm-c | dept:工程/舰队 | watermark verdict=绿（red=false·next_pick=claimed moneyflow IC source-blocked bm-a "
       "车道合法·py_watermark py_low_board_clear=黄金周合法 idle 白名单）+SAT 引擎活（Tools face rc0·心跳 65s）+板 open=0"
       "（Codely jobs 0·fleet 176 零 open·46 claimed） | 值守面：S0 定向 checkpoint（r652 收口尾行+sat-engine/autofill daemon 面"
       "+r652 尾件 2 枚·r642 零 autostash 律）+pull 带 bm-b 在途波 d18154b5e rebase 1/1 干净 | trio watch r653："
       "V 2000/2000 COMPLETE·Q 1918/2000（+10）·D 1590/2000（+9）=bm-b 正主车道在烧·pool FUND-QUALITY+FUND-DIVLOWVOL 2 批 "
       "ready 待 bm-b·bm-c 零代烧 | S6 38/38 rc0（dualrun ZERO-DRIFT streak 51@403·compute_audit FLAG supply_gap/supply_floor"
       "=黄金周已知结构面 re-eval 10-09+·regime ORANGE shadow·bm-a 心跳 stale 72min→bm-c stale-takeover derive 合法"
       "〔O-2100 s2.4 STALE_MIN〕·CEO 面 LIVE-2026-10-07+REPORT-2026-10-07+CALL-2026-09-30〔cell ORA〕当日幂等再生成） | "
       "QA 包 r653 显式 --round 653 分离 pid 13300 终态 5/5·93 trades·determinism=True·equity 800pts 终值 1,017,839 面恒等 "
       "r642-652 | S0.5 双扫（s05+s7close）DEC 635C3024/ORD 437E9CDD 双 MATCH 零 delta·fleet 163/163 零未回执双扫·inbox 空 | "
       "attrition CLEAN（4 账本·历史 shrink 全 healed 注记照录）·loop pin=5 no-op·watchdog 在册·双爪幂等重装 | "
       "token_meter delta=0（L2 本地腿 0 今日） | 零新坑零 CODELY append（主件 27,396B blob 面不变·余量 3,324B） | "
       "本地未达 origin commit 数=见 S7 close addendum 行（commit+push+fetch 自证） | 下轮指针：r654 值守（trio Q/D 进度 "
       "watch·Q 完成窗 dual-flip watch per r668 律）+10-09 复市数据链 re-arm 预检+REGIME_GUARD v3 首 bar·下个 5x=r655"
       "〔HANDOVER 窗〕\n").format(ts=TS)
open(RR, "wb").write(rb + row.encode("utf-8").replace(b"\n", b"\r\n"))

# ---------- (c) state-bm-c.json ----------
SP = os.path.join(ROOT, "state-bm-c.json")
st, bom = load_json(SP)
for k in ("clock_read", "ts", "last_seen", "last_seen_at", "updated", "updated_at", "last_round_at",
          "last_run_at", "last_ts", "last_decisions_read_at", "last_decisions_at", "last_round_ts",
          "current_task_at"):
    st[k] = TS
st["round_no"] = 654
st["round_no_label"] = "round 653 (bm-c)"
st["did"] = did
st["last_round"] = did
st["last_round_summary"] = ("r653: clean standing-guard round, zero new pits (blob 27,396B unchanged, headroom 3,324B); "
                            "QA r653 5/5 explicit --round; S6 38/38; DEC/ORD double-sweep zero-delta 163/163; attrition "
                            "CLEAN; trio V complete Q1918/D1590 bm-b lane; smoke 48/48")
st["last_action"] = did
st["current_task"] = face3
st["activity_now"] = face3
st["next"] = ("(a) fund-trio Q ~2000 completion window: pool dual-flip watch per r668 law; D finalize ~10-08 (bm-b lane). "
              "(b) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar. (c) watch bm-a reply to "
              "MSG-2026-10-07-0250 (marker-pollution self-audit). (d) monthly exam 10-31 assembly face. (e) next 5x = r655 "
              "(HANDOVER window).")
st["note"] = ("r653: clean standing-guard round, zero new pits (blob 27,396B unchanged, headroom 3,324B); QA r653 5/5 "
              "explicit --round; S6 38/38; DEC/ORD double-sweep MATCH 163/163; attrition CLEAN; trio V complete, Q 1918, "
              "D 1590 (bm-b lane).")
st["verify"] = ("receipts: qa/smoke-r653.md 5/5 (explicit --round 653, pid 13300) + qa/equity-curve-r653.png + "
                "results/_r653bmc_s6_log.txt 38/38 rc0 + results/_r653bmc_s05_facts.json (double-sweep s05+s7close: "
                "DEC 635C3024 + ORD 437E9CDD) + results/_attrition_guard_scan.json CLEAN + results/_r653bmc_trio_watch.json "
                "+ results/_r653bmc_qa_runner.out (terminal 5/5)")
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r653 double-sweep "
                        "s05+s7close both scans = 635C3024 MATCH zero-delta; value facts-driven from "
                        "results/_r653bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["ord_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r653 double-sweep s05+s7close "
                        "both scans = 437E9CDD MATCH zero-delta; fleet orders 163/163 ack at BOTH sweeps (double-sweep "
                        "law); value facts-driven from results/_r653bmc_s05_facts.json, 40hex shape-asserted, never "
                        "hand-typed (r583 S4 law))")
st["cpu_pct"] = st["cpu_util_pct"] = cpu
st["cpu_idle_pct"] = round(100 - cpu, 1)
st["free_ram_gb"] = st["idle_ram_gb"] = st["ram_free_gb"] = ram_free
for k in ("gpu_free_vram_mib", "gpu_free_vram_mb", "gpu_idle_vram_mib", "gpu_idle_vram_mb", "gpu_free_mb",
          "gpu_idle_mb", "gpu_vram_free_mb", "gpu_free_mib"):
    st[k] = gpu_free
save_json(SP, st, bom)

# ---------- (d) heartbeat ----------
HP = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb, bom2 = load_json(HP)
for k in ("clock_read", "ts", "last_seen", "last_seen_at", "updated", "updated_at", "current_task_at"):
    hb[k] = TS
hb["heartbeat_epoch_utc"] = EPOCH
hb["round_no"] = 654
hb["round_no_label"] = "round 653 (bm-c)"
hb["current_task"] = face3
hb["activity_now"] = face3
hb["latest_artifact"] = latest
hb["next_milestone"] = milestone
hb["verdict"] = verdict
hb["prod_lanes"] = ("r653 值守轮（黄金周无 bar：S0 定向 checkpoint+S6 38/38+QA r653 5/5 显式轮标；板 open=0；watermark 绿；"
                    "SAT 引擎活；零新坑零 CODELY append；下个 5x=r655〔HANDOVER 窗〕")
hb["health"] = ("alive (r653 standing-guard clean round: S0 targeted checkpoint + bm-b wave clean rebase, claws "
                "reinstalled idempotent, loop pin=5, watchdog registered; golden-week no-bar until 10-09)")
hb["cpu_pct"] = hb["cpu_util_pct"] = cpu
hb["cpu_idle_pct"] = round(100 - cpu, 1)
hb["free_ram_gb"] = hb["idle_ram_gb"] = hb["ram_free_gb"] = ram_free
for k in ("gpu_free_vram_mib", "gpu_free_vram_mb", "gpu_idle_vram_mib", "gpu_idle_vram_mb", "gpu_free_mb",
          "gpu_idle_mb", "gpu_vram_free_mb", "gpu_free_mib"):
    hb[k] = gpu_free
save_json(HP, hb, bom2)

# ---------- self-verify (smoke F7 face) ----------
hb2 = json.loads(open(HP, "rb").read().decode("utf-8-sig"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb2["clock_read"] and hb2["clock_read"].endswith("+08:00")
st2 = json.loads(open(SP, "rb").read().decode("utf-8-sig"))
assert st2["round_no"] == 654
print("CLOSE_OK ts=%s cpu=%s ram=%s gpu=%d" % (TS, cpu, ram_free, gpu_free))
