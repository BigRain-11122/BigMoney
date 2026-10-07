# -*- coding: utf-8 -*-
# r713 bm-c S7 close: state bump + heartbeat nine-fields (python JSON surgery)
import json, time, datetime, psutil

now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

# fresh resource reads
vm = psutil.virtual_memory()
ram_free_gb = round(vm.available / 1024**3, 1)
cpu_pct = psutil.cpu_percent(interval=1.0)
gpu_free_mib = 0
try:
    import subprocess
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=0x08000000)
    if r.returncode == 0 and r.stdout.strip():
        gpu_free_mib = int(float(r.stdout.decode().strip().splitlines()[0]))
except Exception:
    gpu_free_mib = 0

CTA = ("r713 bm-c CTA-P1 paper-lane wiring harness landed (O-2215 deliverable 2): "
       "scripts/cta_p1_paper.py bar-gated marks lane (no-op until 10-08 first bar, "
       "S6 chain leg 39 auto-fires at first-bar round), selftest 12/12, "
       "E44 temp-panel rehearsal 11/11, S6 39/39 rc0, QA 5/5 det-34th")

did = ("r713 bm-c: (1) MAIN PRODUCT O-20261007-2215 deliverable-(2): CTA_P1 "
       "paper-trial wiring harness -- scripts/cta_p1_paper.py: bar-gated marks "
       "lane (O-2215 no-blind-wiring law structural: panel cutoff 2026-09-30 < "
       "paper_start 2026-10-08 -> honest no-op rc0, zero state write; S6 chain "
       "new leg auto-fires the wiring at the first-bar round tonight). "
       "Construction = verbatim imports from frozen batch carrier (cta_p1_screen "
       "sig_vol_target_tsmom + build_weights; engine/futures_runner run/load_panel; "
       "O-2250 ETF engine untouched); universe pinned to frozen nine varieties "
       "(TS = CTA_WAVE1 post-freeze FUT_META addition trap, universe-pin selftest "
       "face); sizing 10M batch-parity; account CTA-P1 #28 (27-pool external slot "
       "per O-2215); lane results/cta_paper/ (PROS-* whitelist paradigm, excluded "
       "from t35/scorecard/CEO faces by construction); shadow guard, zero canon "
       "touch, live.paper registration face untouched; honest-history 6 "
       "disclosures in state (G1' v2 0/16 honest loss + GM release basis + V0 "
       "roll-gap + AU-beta suspicion + 7-10x margin profile + REGIME-5 promotion "
       "pending bm-a judge). selftest 12/12 PASS; E44 temp-panel rehearsal 11/11 "
       "PASS (real cmd_run twice: accrual full chain + idempotent no-op, zero "
       "repo-data touch, tempdir cleaned; evidence results/_r713bmc_cta_paper_"
       "rehearsal.json). (2) S0 integration: behind=3 (bm-a r853 OSS ledger + "
       "W180 shards) -> bm-c-owned churn absorb pre-rebase (27201a6e4) -> clean "
       "rebase zero conflict -> push dd65d6749 delivered. (3) S0.5 sweep 1: "
       "orders 51 disk/176 ack unacked=0; DEC EE659451 / ORD 17accc40 both "
       "UNCHANGED (hex-case normalized per r711 law; facts results/_r713bmc_s05_"
       "facts.json). (4) S1 smoke 48/48; S3 satengine rc0 alive (W180 shards "
       "11/12 in engine queue = supply disposition); idle NOT-GREEN (RAM "
       "16.7%<40% resident load, idle_rounds=0, --worked declared); compute_audit "
       "rc0 flags pool_starvation+supply_floor recorded with disposition (W180 "
       "in-flight + W16 runner landed = never-dry double supply cover; W16 berth "
       "= bm-a T-172). (5) S6 39/39 rc0 (+cta_p1_paper new leg; dualrun "
       "ZERO-DRIFT streak 33; golden-week no-op legs legal, latest panel bar "
       "2026-09-30 pre-open expected). (6) QA 5/5 34th determinism (93 trades, "
       "sharpe 0.1586, equity 1,017,839 frozen identity, png 66,186B, --round "
       "713 explicit per r758 law). (7) orphan face=1 ComfyUI idle server "
       "(CEO-owned, no-kill documented). (8) attrition CLEAN; quartet green "
       "(loop pin=5 no-op, watchdog in place, pre-commit + pre-push claws "
       "in-place). (9) methodology capture: E44 bar-gated lane pre-launch "
       "temp-panel rehearsal method appended to knowledge/METHODOLOGY_ASSETS.md. "
       "(10) inbox zero unread.")

verdict = ("r713 bm-c: CTA-P1 paper-lane wiring harness round clean. Product = "
           "scripts/cta_p1_paper.py (bar-gated marks lane, O-2215 deliverable 2) "
           "+ selftest 12/12 + E44 rehearsal 11/11 + S6 chain 39 legs rc0 with "
           "new cta_p1_paper leg; wiring auto-fires at tonight's first-bar round. "
           "S0 behind=3 churn-absorb rebase clean, push dd65d6749; both watermarks "
           "unchanged zero action; pool flags recorded with disposition; QA 5/5 "
           "det-34th; smoke 48/48; orders sweep unacked=0; orphan face=1 no-kill; "
           "idle not green-idle, idle_rounds=0 worked-declared.")

next_ptr = ("r714: (a) watch continuation (10-08 reopen first trading day, "
            "intraday marks lane live 09:15, pre-open zero blind action); "
            "(b) tonight post-close face: data-chain full re-arm + CTA-P1 "
            "first-bar auto-wiring + first-marks verification (S6 cta_p1_paper "
            "leg; verify = marks 1 row + state trial-live + compounding "
            "identity) + REGIME_GUARD v3 first-new-bar enforce + fund_premium "
            "15:30 first snapshot (bm-c lane) + QDII watch rerun holiday-delta; "
            "(c) O-2245 bm-c lane three items (OSS pool-ledger wiring "
            "source/permit/adapt_status fields + engineering-class scan list + "
            "negative-results-library linkage, window <=10-12~10-16); "
            "(d) O-2215 item-1 matrix spec + switching law v1 (<=10-16 12:00, "
            "consumes bm-a REGIME-5 <=10-14 + bm-b five-state router); "
            "(e) cloudF row collection window <=10-14; (f) next 5x = r715 "
            "HANDOVER. [via bm-c r713]")

cur_task = ("当前活: r713 bm-c CTA-P1 纸盘接线 harness 落地轮（O-2215 ②·盘前值守第 33 连守轮·"
            "bar-门控禁盲接·首 bar 轮 S6 自动点火） | 最近实物: scripts/cta_p1_paper.py + "
            "results/_r713bmc_cta_paper_rehearsal.json（selftest 12/12+演练 11/11·"
            "O-20261007-2215 交付②） @ " + ts + " | 下个里程碑: 今晚盘后（10-08 15:30+）"
            "CTA-P1 首 bar 自动接线+首 marks 验证+数据链 re-arm+REGIME_GUARD v3 enforce+"
            "fund_premium 首采；next 5x=r715 HANDOVER")

latest_art = ("scripts/cta_p1_paper.py + results/_r713bmc_cta_paper_rehearsal.json "
              "(CTA-P1 paper-lane wiring harness, O-2215 deliverable 2: selftest "
              "12/12, rehearsal 11/11, S6 leg 39) @ " + ts)
next_ms = ("tonight post-close: CTA-P1 first-bar auto-wiring + first-marks verify + "
           "data-chain re-arm + REGIME_GUARD v3 enforce + fund_premium first "
           "snapshot (<= 10-08 23:59)")

# ---- state-bm-c.json ----
sp = "state-bm-c.json"
st = json.load(open(sp, encoding="utf-8-sig"))
st["round_no"] = 714
st["round_no_label"] = "round 713 (bm-c)"
st["last_round"] = 713
st["last_round_at"] = ts
st["clock_read"] = ts
st["ts"] = ts
st["updated"] = ts
st["updated_at"] = ts
st["last_run_at"] = ts
st["current_task"] = cur_task
st["current_task_at"] = ts
st["latest_artifact"] = latest_art
st["next_milestone"] = next_ms
st["did"] = did
st["verdict"] = verdict
st["note"] = ("r713: CTA-P1 paper-lane wiring harness landed (O-2215 deliverable 2, "
              "bar-gated, first-bar auto-wiring tonight); S0 behind=3 churn-absorb "
              "rebase clean; both watermarks unchanged; E44 methodology captured.")
st["last_round_summary"] = ("r713: CTA-P1 harness + selftest 12/12 + rehearsal 11/11; "
                            "S6 39 rc0 streak 33; QA 5/5 det-34th; smoke 48/48; "
                            "orders sweep unacked=0; pool flags dispositioned.")
st["last_action"] = st["last_round_summary"]
st["activity_now"] = verdict
st["next_pointer"] = next_ptr
st["verify"] = ("scripts/cta_p1_paper.py + results/_r713bmc_cta_paper_rehearsal.json "
                "(11/11) + qa/smoke-r713.md 5/5 + qa/equity-curve-r713.png 66,186B "
                "(determinism=True 34th, 93 trades, equity 1,017,839 frozen identity) "
                "+ results/_r713bmc_s6_log.txt (39 legs rc0, dualrun streak 33) + "
                "results/_r713bmc_s05_facts.json (sweep 1 unacked=0) + "
                "knowledge/METHODOLOGY_ASSETS.md E44 row")
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---- fleet/machines/bm-c.json (heartbeat, nine-fields law) ----
hp = "fleet/machines/bm-c.json"
hb = json.load(open(hp, encoding="utf-8-sig"))
hb["last_seen"] = ts
hb["clock_read"] = ts
hb["ts"] = ts
hb["updated_at"] = ts
hb["updated"] = ts
hb["last_run_at"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["cpu_idle_pct"] = round(100.0 - cpu_pct, 1)
hb["free_ram_gb"] = ram_free_gb
hb["idle_ram_gb"] = ram_free_gb
hb["ram_free_gb"] = ram_free_gb
hb["gpu_free_vram_mb"] = gpu_free_mib
hb["gpu_free_vram_mib"] = gpu_free_mib
for k in ("gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_vram_free_mb",
          "gpu_free_mb", "gpu_idle_mb", "gpu_free_mib", "gpu_idle_mib"):
    hb[k] = gpu_free_mib
hb["round_no"] = 714
hb["round_no_label"] = "round 713 (bm-c)"
hb["last_round"] = 713
hb["last_round_at"] = ts
hb["current_task"] = cur_task
hb["current_task_at"] = ts
hb["latest_artifact"] = latest_art
hb["next_milestone"] = next_ms
hb["did"] = did
hb["verdict"] = verdict
hb["note"] = st["note"]
hb["last_round_summary"] = st["last_round_summary"]
hb["last_action"] = st["last_round_summary"]
hb["activity_now"] = verdict
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["health"] = "ok"
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# self-assert: epoch is int (R170/R178 law)
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb["clock_read"], "clock_read must be T-separated ISO8601"
print("state+heartbeat written: round_no=714 last_round=713 epoch=%d "
      "cpu=%.1f%% ram_free=%.1fGB gpu_free=%dMiB" %
      (epoch, cpu_pct, ram_free_gb, gpu_free_mib))
