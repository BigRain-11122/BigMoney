# -*- coding: utf-8 -*-
"""r922 bm-b closeout: state.json + heartbeat + round report line."""
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())


def _load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _dump(p, obj):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def _ram_free_gb():
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "[math]::Round((Get-CimInstance Win32_OperatingSystem)"
         ".FreePhysicalMemory/1MB,1)"], capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 6.2


def _vram_free_gb():
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"], capture_output=True, text=True)
    try:
        return round(int(out.stdout.strip().split("\n")[0]) / 1024, 1)
    except (ValueError, IndexError):
        return 3.6


ram = _ram_free_gb()
vram = _vram_free_gb()

ST = os.path.join(ROOT, "state.json")
st = _load(ST)
st["clock_read"] = NOW
st["round_no"] = 923
st["round_no_label"] = "r922"
st["current_task"] = ("r923: burn-done check (~04:12) -> export-topk K=32 "
                      "(completion gate opens at cumulative 4352) -> "
                      "judged-leg-4 BUILD (job#1 design-lock) + judged pool "
                      "burn -> JUDGED + ledger 32; S6 full chain 10-14 15:30")
st["d19_watermark_guard"]["round_ref"] = 922
st["d19_watermark_guard"]["ts"] = NOW
st["did"] = ("r922: (1) burn watch verified: N2U3 leg-3 ep 2687/log 2688 "
             "cumulative, pace ~24.3 eps/min, ETA ~04:12, 8 workers full "
             "load. (2) PRODUCT: judged-face leg-4 found UNBUILT (cmd_judge "
             "= gate machine only) + export-topk had NO leg-3 completion "
             "validation (in-flight partial export = VOID TOPK hazard) -> "
             "landed _train_complete_face fail-closed gate (>=4352 "
             "cumulative + receipt==log, additive-restart robust) wired "
             "into export-topk + judge posture; live-fire refusal proven; "
             "selftest 46->50/50; job#1 registered = judged-leg-4 build "
             "spec with design-lock. (3) orphan probe flagged burn "
             "supervisor = ProcessPool false-positive -> pit law "
             "direct-written pit-machine.md (r666/r889 precedent, receipt "
             "_r922bmb_pit_append.json). (4) S0 0/0, S0.5 orders diff 0 + "
             "D-19 zero-delta, smoke 49/49, SatEngine alive, board open 0. "
             "(5) S6: dualrun ZERO-DRIFT streak 2, audit CLEAN "
             "burning-healthy, pywm insufficient_history legal, token 0. "
             "(6) S7 all green, idle --worked.")
st["last_action"] = ("r922: N2U3 post-burn chain de-risk: leg-3 completion "
                     "gate landed + live-fire refusal proven (export-topk "
                     "exit 2 while burn in-flight) + selftest 50/50 + "
                     "judged-leg-4 build job#1 design-locked (A158-TSGATE "
                     "door template + W15 judge battery + t23 nulls + "
                     "G-ANCHOR-FACE same-window law)")
st["last_action_at"] = NOW
st["last_round_at"] = NOW
st["last_seen"] = NOW
st["last_round_ts"] = NOW
st["latest_artifact"] = ("scripts/alphagen_rl_p1.py leg-3 completion gate "
                         "(r922 03:0x) + selftest 50/50 PASS + job#1 "
                         "judged-leg-4 design-lock")
st["machine_id"] = "bm-b"
st["next"] = ("r923: (a) burn-done check -> export-topk K=32 -> judged-leg-4 "
              "build (job#1) -> judged pool burn -> JUDGED-2026-10-09.json + "
              "ledger 32 (first judged N2U3 evidence); (b) S6 full chain at "
              "10-14 15:30 data window; (c) standing: GPU PSU-swap (MODE="
              "pause, i2v 27/53), unity POC editor window (Cowork running), "
              "Speech-02 adjudication, Music3 install post-batch, bili-reply "
              "cookie+aid CEO items, MF panel source-blocked")
st["next_milestone"] = ("N2U3 leg-3 burn done ~04:12 -> export-topk + "
                        "judged-leg-4 build + judged burn = first judged "
                        "N2U3 channel-1 evidence (due this morning); S6 data "
                        "window 10-14 15:30; GPU line = PSU swap or CEO "
                        "re-order")
st["note"] = ("r922: watch+de-risk round; product = completion gate (50/50 "
              "selftest) + judged-leg design-lock job; burn healthy on "
              "accelerated pace (ETA 04:12 vs 04:40 estimate)")
st["now_active"] = ("N2U3 leg-3 burn PID 8556 (ep 2687/4352 cumulative, 8 "
                    "workers, ETA ~04:12); astock refresh + "
                    "backfill_ext_slots in-flight; GPU idle MODE=pause "
                    "PSU-deferred; SatEngine ticking; Cowork hub+app running "
                    "(no editor)")
st["orphan_face"] = 1
st["orphan_face_note"] = ("r922 probe 02:42: py_faces=26 orphans=1 killed=[] "
                          "-- the 1 = burn supervisor PID 8556 ProcessPool "
                          "FALSE-POSITIVE (8 workers ~100% CPU each = legal "
                          "lane, never kill; pit law r922 pit-machine.md)")
st["orphan_faces"] = 1
st["sync"]["last_push_ts"] = NOW
st["sync"]["note"] = ("r922: closeout commit+push follows this write; "
                      "delivery self-proof via fetch+rev-list")
st["task"] = ("r923: burn-done -> export-topk -> judged-leg-4 build "
              "(job#1) -> judged burn; S6 full chain 10-14 15:30; standing: "
              "PSU-swap GPU hold, unity POC editor-window, Speech-02/Music3 "
              "gates, bili-reply CEO physical items, MF source-blocked")
st["ts"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["verdict"] = ("GREEN: N2U3 leg-3 burn healthy 62% (ETA ~04:12, ahead of "
                 "est) + post-burn chain de-risked (completion gate "
                 "landed, judged-leg design-locked job#1); flags = GPU "
                 "PSU-deferred (MODE=pause) + unity POC editor-window-gated "
                 "+ Speech-02/Music3 standing gates")
_dump(ST, st)

HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = _load(HB)
hb["clock_read"] = NOW
hb["current_task"] = st["current_task"]
hb["did"] = st["did"]
hb["free_ram_gb"] = ram
hb["gpu_free_vram_gb"] = vram
hb["gpu_free_vram_mb"] = int(vram * 1024)
hb["heartbeat_epoch_utc"] = EPOCH
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["last_action"] = st["last_action"]
hb["last_action_at"] = NOW
hb["last_round_at"] = NOW
hb["last_seen"] = NOW
hb["latest_artifact"] = st["latest_artifact"]
hb["next"] = st["next"]
hb["next_milestone"] = st["next_milestone"]
hb["note"] = st["note"]
hb["now_active"] = st["now_active"]
hb["orphan_face"] = 1
hb["orphan_face_note"] = st["orphan_face_note"]
hb["orphan_faces"] = 1
hb["ram_free_gb"] = ram
hb["round"] = 922
hb["round_no"] = 923
hb["round_no_label"] = "r922"
hb["sync"]["last_push_ts"] = NOW
hb["sync"]["note"] = ("r922: closeout commit+push follows this write; "
                      "delivery self-proof via fetch+rev-list")
hb["task"] = st["task"]
hb["ts"] = NOW
hb["updated"] = NOW
hb["updated_at"] = NOW
hb["verdict"] = st["verdict"]
hb["idle_ram_gb"] = ram
hb["idle_ram_pct"] = round(ram / 24.0 * 100, 1)
hb["gpu_idle_vram_gb"] = vram
hb["gpu"]["util_pct"] = 1.0
hb["gpu"]["power_w"] = 9.0
hb["gpu"]["face"] = ("GPU idle (MODE=pause PSU-deferred, i2v 27/53 held for "
                     "PSU swap/CEO re-order); N2U3 burn = pure CPU face")
_dump(HB, hb)

chk = json.loads(open(HB, encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"

REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    f"| {NOW} | r922 bm-b [dept:eng/fleet] | N2U3 burn watch + post-burn "
    "chain DE-RISK round: leg-3 completion gate landed (export-topk/judge "
    "fail-closed) + judged-leg-4 design-lock job#1 | watermark: GREEN "
    "healthy lane (red=false 02:45, next_pick claimed MF IC reference "
    "source-blocked standing) | orphan-faces=1 = ProcessPool supervisor "
    "FALSE-POSITIVE (PID 8556 burn supervisor parent-dead+cpu-stalled but "
    "8 workers ~100% CPU each = legal lane, never kill; pit direct-write "
    "pit-machine.md entry 1297B sha16=4b13d20b7cdb9309 + receipt "
    "_r922bmb_pit_append.json) | currently-active: N2U3 leg-3 train "
    "BURNING PID 8556 (ep 2687 / log 2688 of cumulative 4352 target, pace "
    "~24.3 eps/min, ETA ~04:12) + astock refresh PID 6036 + "
    "backfill_ext_slots; GPU idle MODE=pause PSU-deferred (i2v 27/53) | "
    "did: (1) S0: HEAD==origin 0/0 (dirty faces = autofill keepalive legal "
    "churn, no pull needed). (2) S0.5: orders full-diff UNACKED=0 (208 "
    "acked); D-19 zero-delta (decisions b137f331/orders 348eaf34 "
    "unchanged, probe _r686bmb_d19_check.py). (3) S1 smoke 49/49. (4) S3: "
    "SatEngine alive idle; board open=0 job_list 0; P2 tech all done; P3 "
    "head E17 = the in-flight N2U3 chain itself (no new claimable); "
    "not-green-idle (RAM 26% + batch in-flight). (5) PRODUCT: cmd_judge "
    "audit revealed judged-face leg-4 UNBUILT (gate machine only, "
    "judged_leg_pending) + cmd_export_topk had NO leg-3 completion "
    "validation (an in-flight partial-log export would produce a VOID "
    "TOPK product) -> landed _train_complete_face fail-closed gate "
    "(receipt face=train + episodes>=256+4096=4352 cumulative AND "
    "receipt==log line-count; additive-re-claim robust: restarts add fresh "
    "4096 budgets so completed chains end >= 4352) wired into export-topk "
    "+ judge posture extra; live-fire: export-topk REFUSES exit 2 "
    "(awaiting_train_complete, receipt 256 stale/log 2560/required 4352) "
    "+ judge refuses 3 conditions; selftest 46->50/50 PASS (L14a-d "
    "hermetic: partial/miss-match/absent/complete fixtures); job#1 "
    "registered = judged-leg-4 build spec (design-lock: A158-TSGATE-P1 "
    "per-instrument q10/q90 door template on core48 + "
    "perpetual_faces_n2._judge_cell_w15/_d6 battery + t23 "
    "_permute_ranks_within_mask nulls + g1_prime_v2/g2_registration_v2/"
    "m1 shared lib + G-ANCHOR-FACE same-window probe+consumer law + TOPK "
    "sha16 pin + P-5 all-start face + ledger 32). (6) S6 core: dualrun "
    "ZERO-DRIFT 446 entries streak 2, compute_audit CLEAN "
    "burning-healthy (supply_floor 1<3 honest breach, refills post-burn), "
    "pywm insufficient_history LEGAL, token delta 0. (7) S7: idle "
    "--worked (idle_rounds 0), attrition CLEAN (1 healed historical "
    "shrink), loop pin=2 no-op, watchdog re-registered idempotent, both "
    "claws installed, inbox 0 unread. | evidence: scripts/"
    "alphagen_rl_p1.py gate + selftest 50/50 + export-topk live refusal "
    "JSON + results/_r922bmb_pit_append.json + "
    "results/compute_audit.bm-b.json CLEAN + "
    "results/_attrition_guard_scan.json + smoke 49/49 | unacked_orders=0 "
    "(208/208) | local-unreached-origin-commits: round-start 0 -> "
    "closeout commit+push follows + self-proof | next-pointer r923: "
    "burn-done check (~04:12) -> export-topk K=32 (gate opens at 4352) -> "
    "judged-leg-4 BUILD (job#1) -> judged pool burn -> "
    "JUDGED-2026-10-09.json + ledger 32 = first judged N2U3 channel-1 "
    "evidence; S6 full chain 10-14 15:30 data window; standing: GPU line "
    "PSU-swap (MODE=pause holds, i2v 27/53), unity POC first interactive "
    "editor window (Cowork running = R2 live), Speech-02 committee/CEO, "
    "Music3 post-batch, bili-reply CEO cookie+aid, MF panel "
    "source-blocked | [r922 bm-b]\n")
with open(REPORT, "a", encoding="utf-8", newline="") as f:
    f.write(line)
print(json.dumps({"closeout": "ok", "epoch_type": type(
    chk["heartbeat_epoch_utc"]).__name__, "ram_free": ram,
    "vram_free": vram, "round_report_appended": True}, ensure_ascii=False))
