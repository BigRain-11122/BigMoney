# -*- coding: utf-8 -*-
"""r490 bm-c closeout: state round_no + heartbeat (programmatic write +
reparse self-proof per r678; epoch int + clock T-format per R170/R262/r641).
Lineage: _r489bmc_closeout.py pattern (read per r461), bm-c schema preserved,
orders_ack untouched (0 new orders this round)."""
import json, time, datetime, io, subprocess

now = datetime.datetime.now().astimezone()
clock = now.isoformat(timespec="seconds")          # T-separated, +08:00
ts_short = now.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())
assert "T" in clock and clock[10] == "T", "clock T-format violation"

import psutil
cpu_pct = round(psutil.cpu_percent(interval=0.3), 1)
vm = psutil.virtual_memory()
idle_gb = round((vm.total - vm.used) / 2**30, 1)
gpu_free = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, timeout=20,
                       creationflags=0x08000000)
    gpu_free = int(r.stdout.decode().strip().splitlines()[0])
except Exception as e:
    print("nvidia-smi read skipped:", str(e)[:80])

# ---- state: round_no + bookkeeping faces ----
sp = "state-bm-c.json"
st = json.load(open(sp, encoding="utf-8-sig"))
st["round_no"] = 490
st["clock_read"] = clock
st["last_seen"] = clock
st["updated"] = clock
st["updated_at"] = clock
st["last_round_at"] = clock
st["last_round_ts"] = ts_short
st["last_ts"] = ts_short
st["heartbeat_epoch_utc"] = epoch
st["last_round"] = ("r490 bm-c: third custody/maintenance round -- S0 FF 8aa513a7a + "
                    "S0.5 double MATCH + smoke 48/48 + S6 38-face rc0 + custody probe "
                    "IN_FLIGHT rerun; product = W3 judge finalize still in flight (ETA ~22:1x)")
st["current_task"] = ("当前活: W3 judge finalize --wave 3 看护（pid 33768·17:44:04 起·ETA ~22:1x·"
                      "end-only writes）——r490=第三次看护维护轮（S0 FF 8aa513a7a+S0.5 双 MATCH+"
                      "S1 48/48+S6 38 面 rc0+custody IN_FLIGHT 复核）| 最近实物: r490 S6 全链 38 面 rc0 再生"
                      "（REPORT/LIVE 双面刷新+dualrun ZERO-DRIFT streak 51·377 entries）@ " + clock + " | 下个里程碑: "
                      "w3_judge.json 判决产品落地（777 格）→ADOPT_PASS 收养→48h CEO 报告钟（≤10-06 晚）；"
                      "fund-trio 10-05 10:30（bm-b）；验收 10-08；开市 10-09")
st["did"] = ("r490 bm-c custody round (rule-2 single custody line, no re-scan of same waiting "
             "object): (1) S0 fetch + 8-behind zero-intersection check + merge FF 8aa513a7a "
             "(88 files, zero UU, daemon lane faces preserved); (2) S0.5 _r490bmc_s05_check "
             "double MATCH (decisions 4E5BE321 + orders 68947C17, r458 per-key calibers) + 0 "
             "unacked (ack_extra README historical) + inbox 1 = MSG-2026-10-04-1845 (bm-b->bm-a "
             "N2 slice-2 seat transfer plan-A effective, cc ALL, bm-c non-party zero action, "
             "left in inbox for bm-a); (3) S1 smoke 48/48; (4) S2 boards empty (job_list 0 / "
             "fleet 0 open / 45 claimed); (5) S3 satengine rc0 alive (Tools face r467) + "
             "watermark green (red=false healthy, next_pick=claimed advisory) + custody probe "
             "IN_FLIGHT rc0 + post_review official face 45/0/5 zero active red; (6) S6 38/38 "
             "rc0 (dualrun ZERO-DRIFT streak 51, 377 entries; REPORT/LIVE regen; update_lhb "
             "refetch 0-new honest no-op, zero shared-data writes; lane guards honored); (7) "
             "S7 quartet 4/4 (loop pin5 no-op first-fire 19:05 / watchdog present / both claws "
             "match) + attrition CLEAN 4 ledgers.")
st["next"] = ("(a) product lands ~22:1x -> python results/_r487bmc_w3_judge_verify.py -> "
              "ADOPT_PASS receipt (complete=true + 777 cells + prev 646799 + total 647576 + "
              "single chain block + seed 20285600 + ckpt 0 dup + pool 4/4) -> targeted "
              "commit+push -> 48h CEO report clock starts (<=10-06 evening) -> treasure-capture "
              "question (TREASURE_REGISTRY + METHODOLOGY_ASSETS) -> prereg sec.7/8 judge-phase "
              "backfill (w2 precedent lines). (b) MSG-2026-10-04-1845 = N2 slice-2 seat "
              "transferred to bm-a (plan-A effective 18:4x); bm-c zero N2 action per "
              "zero-duplicate red line. (c) fund-trio finalize 10-05 10:30 (bm-b owner, watch "
              "only). (d) O-2115/O-2030 acceptance 10-08. (e) market reopen 10-09. (f) CODELY "
              "hot-layer ~94.5KB sweep candidate window after W3 judge closure (group surface "
              "per r504).")
st["verify"] = ("r490: S0 merge FF zero-UU (8aa513a7a, intersection=0, daemon lane preserved); "
               "S0.5 _r490bmc_s05_out.txt double MATCH + 0 unacked; S1 48/48; S6 all rc0 "
               "(FAILS empty, log _r490bmc_s6_log.txt, parity 38==canon); satengine status rc0 "
               "(Tools face r467); custody probe VERIFY_RC=0 IN_FLIGHT; attrition CLEAN 4 "
               "ledgers; quartet (loop pin5 no-op / watchdog present / both claws match); "
               "post_review face 45/0/5; state+hb reparse self-proof + epoch int + clock T-sep "
               "(this script)")
st["cpu_pct"] = cpu_pct
st["cpu_util_pct"] = cpu_pct
st["idle_ram_gb"] = idle_gb
st["ram_free_gb"] = idle_gb
st["free_ram_gb"] = idle_gb
if gpu_free is not None:
    st["gpu_free_vram_mib"] = gpu_free
with io.open(sp, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
re_st = json.load(open(sp, encoding="utf-8-sig"))
assert re_st["round_no"] == 490, "round_no write failed"
assert isinstance(re_st["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in re_st["clock_read"], "clock T-format reparse FAIL"
print("state r490 OK: epoch=%d clock=%s cpu=%s%% ram=%sGB gpu=%s" %
      (re_st["heartbeat_epoch_utc"], re_st["clock_read"], cpu_pct, idle_gb, gpu_free))

# ---- heartbeat: fresh sampling + epoch int + clock T-format ----
hp = "fleet/machines/bm-c.json"
hb = json.load(open(hp, encoding="utf-8-sig"))
hb["clock_read"] = clock
hb["last_seen"] = clock
hb["last_seen_at"] = clock
hb["updated"] = clock
hb["updated_at"] = clock
hb["ts"] = ts_short
hb["heartbeat_epoch_utc"] = epoch
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be JSON int"
hb["round_no"] = 490
hb["round_no_label"] = "r490"
hb["activity_now"] = ("r490 custody: judge-finalize wave-3 in flight (pid 33768, ETA ~22:1x per "
                      "w2 calibration), custody probe rerun IN_FLIGHT VERIFY_RC=0; S1 48/48; S6 "
                      "38-face rc0; quartet green; boards empty; post_review 45/0/5")
hb["current_task"] = st["current_task"]
hb["latest_artifact"] = ("r490 S6 maintenance regen faces (REPORT-2026-10-04 + LIVE-2026-10-04, "
                         "dualrun streak 51 zero-drift) + custody probe IN_FLIGHT receipt "
                         "_r487bmc_w3_judge_verify.json + D-19 double MATCH probe "
                         "_r490bmc_s05_out.txt")
hb["next_milestone"] = ("w3_judge.json lands ~22:1x -> ADOPT_PASS -> commit+push -> 48h CEO report "
                        "clock (<=10-06 evening); fund-trio finalize 10-05 10:30 (bm-b); MSG-1845 "
                        "N2 seat = bm-a (plan-A effective); acceptance 10-08; market reopen 10-09")
hb["prod_lanes"] = ("W3-JUDGE lane: 4/4 shards done+flipped, judge-finalize --wave 3 in flight on "
                    "bm-c (pid 33768, sole finalize per MSG-1810 yield receipt closed r487); pool "
                    "ready=4 = bm-b keepalive trio NULLS (owner_since 18:48 fresh) + "
                    "CONTEST-0OF1 revcensus unclaimed autofill face (no manual burn per r487); "
                    "N2-W15 slice-2 = bm-a seat per MSG-2026-10-04-1845 plan-A effective, bm-c "
                    "zero N2 action (zero-duplicate red line); boards empty; 0 new orders")
hb["health"] = "healthy"
hb["verdict"] = ("r490 bm-c: third custody round -- S0 FF-merge 8aa513a7a + S6 38-face rc0 + "
                 "custody probe IN_FLIGHT (VERIFY_RC=0) + watermark green (red=false healthy); "
                 "product lands ~22:1x")
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["cpu_idle_pct"] = round(100 - cpu_pct, 1)
hb["idle_ram_gb"] = idle_gb
hb["free_ram_gb"] = idle_gb
hb["ram_free_gb"] = idle_gb
if gpu_free is not None:
    for k in ("gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib",
              "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_vram_free_mb",
              "gpu_idle_mb"):
        hb[k] = gpu_free
with io.open(hp, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
re_hb = json.load(open(hp, encoding="utf-8-sig"))
assert isinstance(re_hb["heartbeat_epoch_utc"], int), "reparse epoch int FAIL"
assert "T" in re_hb["clock_read"], "reparse clock T FAIL"
assert re_hb["round_no"] == 490, "reparse round_no FAIL"
print("heartbeat OK: epoch=%d int, clock=%s, cpu=%s%%, ram_free=%sGB, gpu_free=%sMB" %
      (re_hb["heartbeat_epoch_utc"], re_hb["clock_read"], re_hb["cpu_pct"],
       re_hb["idle_ram_gb"], gpu_free))
