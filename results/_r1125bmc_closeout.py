# -*- coding: utf-8 -*-
# r1125 bm-c closeout: state advance 1125->1126 + heartbeat + round-report row.
# Per r750 law the round row lands in the CANONICAL root round_reports-bm-c.md.
import io, os, json, time, datetime, subprocess, psutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())

DID = ("r1125: (1) S0-1 anchor bm-c + round-zero probe py_faces=3 orphans=0 resident_servers=1 zero-kill "
       "+ S0 pull --rebase refused on own probe face -> targeted commit dbe7b3568 + pull up-to-date; "
       "(2) S0.5 D-19 dual-delta FALSE both scans (ORD content-sha1 4f2a5c3b / DEC raw-blob sha256 60a98a02 "
       "hold, pinned-method probes; unacked=0, repo orders files all inside ack-230); "
       "(3) S1 smoke 49/49; "
       "(4) P0 PRODUCT = W280 PREP landed (two PREP legs combined one window per r1120+r1121 precedent): "
       "frozen W279 template face extracted+byte-verified 23,681B sha256_16 c2fc7c34d0e41a68 @ ba5c725b42 "
       "PRE-backfill face (HEAD post-backfill twin b98e85926 28,043B disclosed NOT used per r1049/r1052) + "
       "prep facts _w280bmc_prep_facts.json (chain anchors machine-frozen: prereg ba5c725b42 18:51 / splice "
       "3810f4a7ac 19:33 / burn batches 498d178d0b+332e8e8656 / finalize estate 6bdbdb9a07 / W279 seat "
       "900c23fe7d / W280 seat f96272d8b9 + MSG-20261019-200x carried verified + W279 actuals fivekeys "
       "full-precision [merged mu -0.09282362698620283 / sigma 0.24506025197871714 / se_mu@611,720 0.000313 / "
       "A p95 0.3104 / K-lift +0.0000 / w279-only -0.10331555 / ledger 1,038,135 EXACT / n_eff_held 1,035,935] "
       "+ projections computed in-script K 613,920 / ledger 1,040,335 / n_eff_held 1,038,135 / se_mu W280 0.000313) "
       "+ needle floors _w280bmc_needle_floors.json MEASURED on T0 (r1077 law: stamp faces 15:1x=4 / 13:5x=2; "
       "legitimate present roll-faces W280p_ x2 / 631_301 x3 / 0.000313 x1 / 29th-A-hop x3 ground-truthed; "
       "ALL G+2 zero-floors pass fail-closed: W281p_ / 633_300 / 633_500 / -0.09282363 / 0.24506025 / 0.3104 / "
       "f96272d8b9 / 20:0x / 19:3x / engine_owner==bm-c 98 etc all count=0); "
       "(5) 5x HANDOVER duty discharged: r1125 row landed research/HANDOVER.md (five-window r1121-r1125 summary); "
       "(6) 10-19 bar sina-lag honest: update_daily 0 rows cutoff 10-16 (~20:4x evening window; papers debt=0, "
       "re-arm = the window that sees the bar); "
       "(7) S6 light 10/10 rc0 (driver _r1125bmc_s6_light.py canon-clone r1124: dualrun ZERO-DRIFT streak 51 "
       "[461] / compute_audit rc0 / py_watermark probe / market_regime shadow / market_clock CALL-2026-10-16 "
       "ORANGE_COOL idempotent / fund_premium no-op / b_layer all_pass / REPORT-2026-10-19 faces=5 token=1 / "
       "token delta=0); "
       "(8) S7: attrition 4 CLEAN + loop next-fire live + watchdog Ready + claws identical both (python "
       "CR-normalized verify) + idle --worked rc0 + own W280 seat MSG swept to processed; counter 1125->1126")

VERDICT = ("green r1125 product window: W280 PREP landed (frozen W279 face byte-verified c2fc7c34d0e41a68 + "
           "prep facts chain-frozen + needle floors T0-measured, two PREP legs combined one window) + 5x "
           "HANDOVER row r1121-r1125 + S0.5 dual FALSE both scans + smoke 49/49 + S6 10/10 + attrition CLEAN "
           "+ quad green + 10-19 bars sina-lag honest 0 rows cutoff 10-16")

NEXT = ("r1126 FIRST ACTIONS: (1) W280 prereg derive = P0 first action (E63 canon-clone of "
        "_r1122bmc_build_w279_derive.py bloodline -> _r1126bmc_build_w280_derive.py -> "
        "_w280bmc_prereg_derive.py -> research/PERPETUAL_N1_W280_PREREG.md freeze; anchors = PREP facts "
        "_w280bmc_prep_facts.json machine-frozen zero-transcription: frozen W279 tpl 23,681B sha16 "
        "c2fc7c34d0e41a68 PRE-backfill @ ba5c725b42 [HEAD twin b98e85926 28,043B NOT used]; W279 actuals "
        "fivekeys full-precision; W280 seat bands A 631_301..633_300 / B 633_301..633_500 verbatim in-gate; "
        "floors = _w280bmc_needle_floors.json measured: stamp rolls 15:1x->20:0x x4 [W279 finalize 6bdbdb9a07 "
        "20:06] + 13:5x->19:3x x2 [W279 splice 3810f4a7ac 19:33]; roll-faces W280p_ x2 / 631_301 x3 / "
        "0.000313 x1 / 29th-A-hop x3; descending-chains shift one generation: MSG 145x->200x, seat "
        "900c23fe7d->f96272d8b9, K 611,720->613,920, ledger 1,038,135->1,040,335, n_eff 1,038,135 held, "
        "A-hop 29th, above-own-A 30th, ordinal 270th/271st, bmc_rows 98->99, wave 279->280; after derive: "
        "banned_direction_gate ADMIT + freeze commit + push); (2) 10-19 bar sina evening-lag -> papers full "
        "chain re-arm when bar lands (live.paper enforce + t35_open_fill_verify + t24_prospect_paper + "
        "t24_prospect_promotion + aggressive_lab + grid_paper + t35_paper_export); (3) splice chain r1127 / "
        "cycle+W281 seat r1128 per cadence")

VERIFY = ("PREP gates ALL PASS (T0 23,681B sha256_16 c2fc7c34d0e41a68 == heartbeat machine-frozen anchor; "
          "freeze blob 51d7ca52a811; fivekeys asserts full-precision; seat receipt asserts verbatim bands; "
          "chain commits exist+ts-gated 7/7; projections computed in-script; zero-floors fail-closed all "
          "count=0) + HANDOVER row assert-verified single-append + smoke 49/49 + S6 10/10 rc0 + attrition 4 "
          "CLEAN + claws identical both + loop/watchdog alive + D-19 dual FALSE both scans + orphan face=0 + "
          "本地未达 origin commit 数=0 (post-push fetch-verified)")

RAM = round(psutil.virtual_memory().available / 1024**3, 2)
try:
    _nvs = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader,nounits"],
                          capture_output=True, text=True).stdout.strip()
    _util, _vram = [x.strip() for x in _nvs.split(",")]
    GPU_FACE = "nvidia-smi %s%%·%s MiB used / 16384 MiB" % (_util, _vram)
except Exception:
    GPU_FACE = "nvidia-smi unreadable"

def upd_state():
    p = os.path.join(REPO, "state-bm-c.json")
    s = json.load(io.open(p, encoding="utf-8"))
    s["round_no"] = 1126
    s["round_no_label"] = "r1125 closeout -> counter 1126"
    for k in ("last_round", "last_round_label"):
        s[k] = "r1125"
    for k in ("last_round_at", "last_round_closed", "last_round_closed_at", "last_action_at",
              "last_round_summary_at", "last_round_ts"):
        s[k] = TS
    s["last_action"] = "r1125 closeout"
    s["did"] = DID
    s["verdict"] = VERDICT
    s["last_round_summary"] = VERDICT
    s["next"] = NEXT
    s["next_pointer"] = NEXT
    s["next_milestone"] = "W280 prereg derive+freeze (r1126 FIRST ACTION); splice r1127; cycle+W281 seat r1128"
    s["verify"] = VERIFY
    s["r1125_closeout_note"] = DID
    s["full_load_selfproof"] = {
        "占用一行": "CPU=W280 PREP (frozen face+facts+floors) + 5x HANDOVER + S6 10/10; GPU=idle (resident ComfyUI listener only); NATS 心跳任务常设在役",
        "最近实物": "results/_w280bmc_w279_frozen_face.txt + results/_w280bmc_prep_facts.json + results/_w280bmc_needle_floors.json + results/_r1125bmc_prep_w280.py + research/HANDOVER.md r1125 row",
        "下个里程碑": "W280 prereg derive+freeze (r1126 FIRST ACTION); splice r1127; cycle+W281 seat r1128",
    }
    art = ("results/_w280bmc_w279_frozen_face.txt + results/_w280bmc_prep_facts.json + "
           "results/_w280bmc_needle_floors.json + research/HANDOVER.md (r1125 5x row)")
    s["last_artifact"] = art
    s["recent_artifact"] = art
    s["latest_artifact"] = art
    s["last_artifact_at"] = TS
    s["prod_lanes"] = "CPU=W280 derive builder next-window P0 (PREP complete); GPU=idle day; NATS bus node live (every:1m standing)"
    s["ram_critical_face"] = "none (loop CPU-only, GPU idle day)"
    s["orphan_face"] = 0
    s["orphan_faces"] = 0
    s["idle_rounds"] = 0
    for k in ("ts", "updated", "updated_at", "now_active", "clock_read"):
        s[k] = TS
    io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(s, ensure_ascii=False, indent=1))

def upd_heartbeat():
    p = os.path.join(REPO, "fleet", "machines", "bm-c.json")
    h = json.load(io.open(p, encoding="utf-8"))
    h["activity_now"] = TS
    h["clock_read"] = TS
    h["ts"] = TS
    h["now_active"] = TS
    h["updated"] = TS
    h["updated_at"] = TS
    h["last_seen"] = TS
    h["last_seen_at"] = TS
    h["heartbeat_epoch_utc"] = EPOCH
    h["current_task"] = "r1126 FIRST ACTION = W280 prereg derive (builder canon-clone, PREP facts in-gate) + 10-19 bar papers re-arm when bar lands"
    h["current_task_at"] = TS
    h["current_task_ts"] = EPOCH
    h["did"] = DID
    h["last_action"] = "r1125 closeout"
    h["last_action_at"] = TS
    art = ("results/_w280bmc_w279_frozen_face.txt + results/_w280bmc_prep_facts.json + "
           "results/_w280bmc_needle_floors.json + research/HANDOVER.md r1125 5x row")
    for k in ("last_artifact", "recent_artifact", "latest_artifact"):
        h[k] = art
    h["last_artifact_at"] = TS
    h["last_round"] = "r1125"
    h["last_round_label"] = "r1125"
    h["last_round_at"] = TS
    h["last_round_closed"] = TS
    h["last_round_closed_at"] = TS
    h["last_round_summary"] = VERDICT
    h["last_round_summary_at"] = TS
    h["verdict"] = VERDICT
    h["next"] = NEXT
    h["next_pointer"] = NEXT
    h["next_milestone"] = "W280 prereg derive+freeze (r1126 FIRST ACTION); splice r1127; cycle+W281 seat r1128"
    h["verify"] = VERIFY
    h["full_load_selfproof"] = {
        "占用一行": "CPU=W280 PREP (frozen face+facts+floors) + 5x HANDOVER + S6 10/10; GPU=idle (resident ComfyUI listener only); NATS 心跳任务常设在役",
        "最近实物": "results/_w280bmc_w279_frozen_face.txt + results/_w280bmc_prep_facts.json + results/_w280bmc_needle_floors.json + results/_r1125bmc_prep_w280.py + research/HANDOVER.md r1125 row @ %s" % TS,
        "下个里程碑": "W280 prereg derive+freeze (r1126 FIRST ACTION, window <=30min after open); splice r1127; cycle+W281 seat r1128",
    }
    h["head_sha"] = "r1125 closeout (W280 PREP + 5x HANDOVER; W280 derive = r1126 first)"
    h["orphan_face"] = 0
    h["orphan_faces"] = 0
    h["idle_rounds"] = 0
    h["agenda_starved"] = False
    h["free_ram_gb"] = RAM
    h["idle_ram_gb"] = RAM
    h["ram_free_gb"] = RAM
    h["gpu_face"] = GPU_FACE
    io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(h, ensure_ascii=False, indent=1))
    # post-write self-assert (R170/R178 law: epoch must be int)
    h2 = json.load(io.open(p, encoding="utf-8"))
    assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch not int"

def append_report():
    p = os.path.join(REPO, "round_reports-bm-c.md")
    row = ("%s | r1125 | W280 PREP landed one-window (frozen W279 tpl face 23,681B sha16 c2fc7c34d0e41a68 "
           "byte-verified @ ba5c725b42 PRE-backfill [HEAD twin b98e85926 28,043B disclosed NOT used] + prep "
           "facts chain-frozen [prereg ba5c725b42/splice 3810f4a7ac/burn 498d178d0b+332e8e8656/finalize "
           "6bdbdb9a07/W280 seat f96272d8b9 + W279 actuals full-precision + projections K 613,920 / ledger "
           "1,040,335 / se_mu 0.000313] + needle floors T0-measured [15:1x=4/13:5x=2 + roll-faces W280p_ x2/"
           "631_301 x3 + all G+2 zero-floors count=0 fail-closed]) + 5x HANDOVER row r1121-r1125 + D-19 dual "
           "FALSE + smoke 49/49 + S6 10/10 rc0 (dualrun streak 51; bars sina-lag 0 rows cutoff 10-16 honest, "
           "papers re-arm next-bar window) + attrition 4 CLEAN + quad green + claws identical | PREP gates "
           "ALL PASS assert-verified + S6 log _r1125bmc_s6_log.txt 10x rc0 + smoke 49/49 + attrition receipt "
           "+ claw identical True/True | r1126 FIRST ACTION = W280 prereg derive builder (E63 canon-clone "
           "_r1122bmc bloodline, PREP facts in-gate) + 10-19 bar papers re-arm; splice r1127; cycle r1128\n")
    t = io.open(p, encoding="utf-8", newline="").read()
    assert "r1125 | W280 PREP" not in t, "row already present"
    io.open(p, "a", encoding="utf-8", newline="").write(row)

upd_state()
upd_heartbeat()
append_report()
print("closeout writes OK @ %s" % TS)
print("counter 1125->1126 | epoch %d (int) | RAM free %.2fGB | %s" % (EPOCH, RAM, GPU_FACE))
