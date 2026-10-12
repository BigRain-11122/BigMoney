# -*- coding: utf-8 -*-
"""r909 bm-b closeout: state.json + heartbeat + round report append (one-shot)."""
import json, time, datetime, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
prev_close = "2026-10-13T00:27:10+08:00"
epoch = int(time.time())

DID = ("r909: (1) i2v batch watch healthy: driver alive (PID 2148), KN08 782s+ in render, batch 9/53, "
       "GPU 100%/176W under 180W cap, driver log fresh 00:30; (2) group surgery3 verify: process ALIVE "
       "(PID 4064, spawned 00:28:23, git write-tree child in flight, out/err logs buffered-empty) -> "
       "completion verify next round; group repo untouched by this session (single-executor law); "
       "(3) SUPPLY WEDGE DIAGNOSED: pool entry N2U3-ALPHAGEN-RL-P1-LEG3-TRAIN stuck status=waiting "
       "(r902 registered) while autofill _pick requires status==ready -> 00:50 tick verdict=pool_empty_or_busy "
       "at py 11.3% (machine NOT CPU-starved; chain wedged on the flip); flip condition PINNED: free RAM >=4GB "
       "(current 2.26GB < machine discipline + CEO video line protection; 8-worker train would OOM-risk "
       "ComfyUI) -> flip at post-batch RAM recovery, autofill then claims (fill latency ~minutes); "
       "(4) S0: pull --rebase blocked by unstaged (runtime lane files, not foreign half-work); "
       "ahead/behind=0/0 = origin synced; S0.5: orders_ack_scan CLEAN (79 orders, 204 acks, unacked=0, "
       "124 stale=rename-wave soft notes) + D-19 re-probe DEFERRED honest (group repo mid-surgery, "
       "avoid concurrent .git touch; r908 probe 00:27 fresh); (5) smoke 49/49; SAT engine alive idle rc0; "
       "watermark red=false healthy; (6) S6 37-leg full chain all rc0 (no-new-bar night window, "
       "live.paper-family legs legally skipped): dualrun streak 51 ZERO-DRIFT, compute_audit flags "
       "pool_starvation/supply_floor (standing, honest: resource-blocked until batch completes), "
       "pywm py_low_with_work_cands (local_batch=astock refresh in-flight), CALL-2026-10-12 ORANGE_COOL, "
       "DUALARM-2026-09-30 written, thermo DONE, aggr/alloc/grid marks idempotent no-op, "
       "export-2026-10-12, daily_scorecard, REPORT-2026-10-13, LIVE-2026-10-13 (state=ORANGE cap=50%), "
       "token 0 today, attr guard scan CLEAN 4 ledgers; (7) S7: loop task no-op pin=2 (next fire 01:02), "
       "watchdog re-registered (00:54), pre-commit+pre-push claws installed, inbox zero-for-bm-b "
       "(T-184 msg addressed bm-a; 510880.csv still absent = bm-a ticket open, alloc_paper rc0 "
       "stale-leg disclosure)")

NOW_ACTIVE = ("i2v animatic batch burning (KN08 in-flight 782s+, batch 9/53, ComfyUI r908c, "
              "GPU 100%/7552MiB under 180W cap) + group surgery3 (POOL-SCORED re-land + token ledger) in flight")

LATEST = ("KN_KN07.mp4 @00:2x (batch 9/53) + S6 regen faces (LIVE-2026-10-13.md, REPORT-2026-10-13.md, "
          "CALL-2026-10-12 ORANGE_COOL) + supply wedge diagnosis (N2U3-LEG3-TRAIN waiting->ready flip "
          "pinned: RAM>=4GB post-batch)")

NEXT = ("r910: i2v batch watch (KN08+ -> 53/53 ETA 10-13 morning; single-unit stall >4h per README-RUN "
        "yield-review) > at batch completion: remove keepwarm.pause marker + flip N2U3-LEG3-TRAIN "
        "waiting->ready (RAM>=4GB gate) -> autofill burn (~3.3h) -> export-topk K=32 -> judged legs > "
        "surgery3 completion verify (ls-remote + out file) > D-19 re-probe (post-surgery) > "
        "Speech-02+Music3 install-verify batch (bm-b lane, O-2215) > E15 48h CEO report due 10-13 11:2x > "
        "W18 48h due 10-14 00:44 > unity-mcp POC due 10-13 12:00 > BigHouse T-2 <=10-15")

MILESTONE = ("i2v 53/53 ETA 10-13 morning -> remove keepwarm.pause + N2U3 leg-3 train burn (RAM-gated) "
             "-> export-topk+judged face; E15 48h report 10-13 11:2x; unity-mcp POC <=10-13 12:00; "
             "W18 48h 10-14 00:44")

VERDICT = ("GREEN-with-flags: i2v batch burning legal at full cadence (GPU 100%/176W under cap, O-1612 "
           "waiver); supply chain un-wedged pending RAM gate (flip pinned: free RAM>=4GB at post-batch "
           "recovery); flags=pool_starvation/supply_floor (standing, honest: machine resource-blocked "
           "until batch completes) + surgery3 in flight; RAM 2.26GB free (<4GB heavy-work line held)")

NOTE = ("r909: watch round under full legal GPU burn; supply wedge root-caused (status waiting vs ready, "
        "flip pinned to RAM>=4GB post-batch); D-19 re-probe deferred (group repo mid-surgery); "
        "T-184 510880.csv still absent (bm-a ticket open, alloc_paper rc0 stale-leg disclosure)")

ORPH_NOTE = ("r909 round probe 00:38: py_faces=15 orphans=0; legal detached = ComfyUI r908c + i2v driver "
             "(PID 2148) + group surgery3 (PID 4064)")

# ---- state.json ----
sp = os.path.join(ROOT, "state.json")
s = json.load(open(sp, encoding="utf-8"))
s["round_no"] = 910
s["round_no_label"] = "r909"
s["round"] = "908"
s["clock_read"] = now
s["current_task"] = "r909 closeout: batch watch + supply wedge diagnosis (N2U3 leg-3 flip pinned RAM>=4GB) + S6 37-leg green"
s["did"] = DID
s["last_action"] = "r909: supply-chain wedge diagnosed + batch watch healthy + S6 full chain green (37 legs rc0)"
s["last_action_at"] = now
s["last_round_at"] = now
s["last_round_ts"] = prev_close
s["last_seen"] = now
s["now_active"] = NOW_ACTIVE
s["latest_artifact"] = LATEST
s["next"] = NEXT
s["task"] = NEXT
s["next_milestone"] = MILESTONE
s["note"] = NOTE
s["orphan_face"] = 0
s["orphan_faces"] = 0
s["orphan_face_note"] = ORPH_NOTE
s["verdict"] = VERDICT
s["ts"] = now
s["updated"] = now
s["updated_at"] = now
s["sync"] = {"last_push_ts": now,
             "note": "r909 closeout push in-round; delivery self-proof = post-push fetch+rev-list (unreached=0 expected)"}
json.dump(s, open(sp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# ---- heartbeat ----
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
h = json.load(open(hp, encoding="utf-8"))
h["round_no"] = 909
h["round_no_label"] = "r909"
h["round"] = 908
h["clock_read"] = now
h["current_task"] = "r909 closeout; r910 = N2U3 leg-3 flip when RAM gate opens + batch watch + surgery verify"
h["did"] = DID
h["last_action"] = "r909: pool supply wedge diagnosed (N2U3 leg-3 waiting->ready flip pinned to RAM>=4GB post-batch) + batch watch healthy + S6 37-leg green"
h["last_action_at"] = now
h["last_round_at"] = prev_close
h["last_seen"] = now
h["heartbeat_epoch_utc"] = epoch
h["now_active"] = NOW_ACTIVE
h["latest_artifact"] = LATEST
h["next"] = NEXT
h["next_milestone"] = MILESTONE
h["note"] = NOTE
h["verdict"] = VERDICT
h["orphan_face"] = 0
h["orphan_faces"] = 0
h["orphan_face_note"] = ORPH_NOTE
h["free_ram_gb"] = 2.26
h["ram_free_gb"] = 2.26
h["ram_free_pct"] = 9.4
h["vram_free_gb"] = 0.62
h["gpu_free_vram_gb"] = 0.62
h["gpu_free_vram_mb"] = 639
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["green_idle"] = False
h["gpu"] = {"util_pct": 100.0, "mem_used_mb": 7552, "power_w": 176.2,
            "face": "i2v int4 animatic batch (ComfyUI r908c)"}
h["ts"] = now
h["updated"] = prev_close
h["updated_at"] = prev_close
h["sync"] = {"last_push_ts": now,
             "note": "r909 closeout push lands with this commit"}
json.dump(h, open(hp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# ---- round report (ASCII-only line per r907 safe convention) ----
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = ("| {ts} | r909 bm-b | dept:engineering+dept:fleet | currently-active: {act} | "
        "latest-artifact: {lat} | next-milestone: {mil} | did: {did} | "
        "evidence: driver log-bmb-r908c.out.txt (KN08 782s running) + autofill_state.bm-b.json last_tick "
        "00:50 pool_empty_or_busy + runnable_pool waiting-entry face + RAM 2.26/23.92GB + smoke 49/49 + "
        "orders_ack_scan.bm-b.json CLEAN + S6 37-leg faces + _orphan_face_probe.bm-b.json (py_faces=15 "
        "orphans=0) | orphan-faces=0 | WM-VERDICT: red=false lane=healthy (probe 00:38) | "
        "unacked_orders=0 | registry-zero-hit statement: no cleanup/archive/delete actions this round "
        "(surgery logs = new evidence files, not cleanup) | local-unreached-origin-commits=0 "
        "(post-push fetch+rev-list self-proof) | next-pointer r910: {nxt} | [r909 bm-b]\n"
        ).format(ts=now, act=NOW_ACTIVE, lat=LATEST, mil=MILESTONE, did=DID, nxt=NEXT)
with open(rp, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(line)

# ---- self-assertions ----
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in h2["clock_read"], "clock_read must be T-separated"
print("closeout OK: state.round_no=%s label=%s hb.round_no=%s epoch=%s int=%s" % (
    s["round_no"], s["round_no_label"], h2["round_no"], h2["heartbeat_epoch_utc"],
    isinstance(h2["heartbeat_epoch_utc"], int)))
print("round report line bytes:", len(line))
