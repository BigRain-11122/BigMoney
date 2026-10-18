# -*- coding: utf-8 -*-
# r1090 bm-c closeout: state counter 1090->1091 + round-report row + heartbeat faces.
# In-process (U060 zero-window law); atomic-ish json writes with read-back assertions.
import io, json, datetime, subprocess, os

TS = datetime.datetime.now().astimezone()
T = TS.isoformat(timespec="seconds")
EPOCH = int(TS.timestamp())

did = ("r1090: W268 PREREG FREEZE LANDED origin f1ec8231c7 (machine-SUB from frozen W267 tpl @ df55e3fab9 pre-backfill; "
       "derive ALL GATES PASS vmap39+floors84+post-legs13+8blocks+MUST75/MUST_NOT63+pinned+residue; banned ADMIT rc0; "
       "idempotent re-run byte-identical 83076bf5b0e4a989; 4 heals disclosed incl. RAM-critical ~0.1G live face + W267-face b6 "
       "ordinal defect caught at birth station; bands A 604_901..606_900 17th A-hop / B 606_901..607_100 18th above-own-A) + "
       "d19 TWO-FACE PATCH LANDED (state+heartbeat same-update write + read-back asserts + honest-skip + zero-fabrication; "
       "selftest 20/20; live-fire dual advance f235aa83->3bd12e4e->d0bb09f6->913b8097 with 8-key mirror equality TRUE both "
       "advances -- r1051 family manual-sync debt mechanized away) + ORD triple-delta consumed (12:4x 自查互查令 "
       "committee-executed zero-new-mechanism standing-faces-green / 12:4x 41曲加速令 BigStream bm-a executing / 12:5x @bm-c "
       "xq32 CDN dispatch CLAIMED by this loop [census: no live MV carrier] then REVISED by 13:5x 本地算力优先令 -> local "
       "INT8 768P burn primary via standing chain + CDN secondary; machine-staged 32-frame map results/_r1090bmc_xq32_staging.json "
       "24 READY-NOW + 8 BLOCKED [7 T1R1 chain step-3 ETA ~17:10 + 1 S5-27 director re-ruling]; 物理依赖票内留痕 per CEO 即时律) + "
       "DEC 4cfdd17c hold + smoke 49/49 + S6 light 10/10 rc0 (dualrun ZERO-DRIFT streak 47 [461] / bars cutoff 10-16 weekend "
       "honest 0 rows / ORANGE 6th day / CALL idempotent / fundprem no-op / REPORT-2026-10-18 faces=5 / token delta=0) + "
       "attrition 4 CLEAN + idle --worked + quad green (loop pin=5 no-op + watchdog registered [S4U flip=adjudicated face] + claws x2)")

nxt = ("r1091: (1) W268 FIVE-FACE SPLICE = FIRST ACTION (editor canon _w267bmc_freeze_edits.py blob 0b39fb0f20c8aa6e per the "
       "r1089-addendum handoff receipt; setwave aging law rep('_set_wave(267)','_set_wave(268)',1) + phase5 presence gates "
       "_set_wave(268):1/_set_wave(267):0; E63 11th-gen replay chain; MEASURED needle preflight per r1077 law at authoring time; "
       "blocked faces until freeze = NONE, W268 prereg frozen THIS window origin f1ec8231c7); (2) xq32 ticket continuation: on "
       "chain step-3 (t1r1hd) landing ~17:10 + S5-27 director ruling -> author the follow-on chain step for the 8 remaining "
       "slots (V5 redo runner 模式 INT8 768P) + secondary CDN delivery per staging map results/_r1090bmc_xq32_staging.json + "
       "receipt MSG + poke bm-a; if MV ops seat returns, 查重律 yields the lane; (3) Monday 10-20 15:30 bars window: full papers "
       "chain fires (papers debt=0); (4) RAM-critical watch standing (MV PACK-A python 4.5G squeeze, loop CPU-only survived "
       "all-light window; if available<0.05GB loop legs may fail -- next window recheck); (5) 24h died-pre-closeout watch per "
       "O-20261018-0948 sec.3.4; (6) GPU lane = MV PACK-A wave-1 in flight ETA ~17:00 (CEO weekend production standing: gen-only, "
       "loop CPU-only); short-video lane DISABLED standing per O-20261017-1741")

verdict = ("green r1090 product window (W268 prereg frozen + d19 two-face patch landed + xq32 ticket claimed/staged with "
           "physical-dependency disclosure; clean continuation; CEO weekend-use standing loop CPU-only)")

art = ("research/PERPETUAL_N1_W268_PREREG.md (origin f1ec8231c7, 23,158B sha256_16 83076bf5b0e4a989) + "
       "scripts/d19_watermark.py two-face patch (selftest 20/20) + results/_r1090bmc_xq32_staging.json (32-slot map 24 READY/8 BLOCKED)")

note = ("r1090: (1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=2 zero-kill (legal resident faces family) + S0 "
        "fetch behind=1 bm-b r1006 (stash-bridge 3 regenerables live-wins, zero conflict) + r1089-addendum W268-editor "
        "handoff baseline in-tree (canon _w267bmc_freeze_edits.py blob 0b39fb0f20c8aa6e); (2) S0.5 ORD triple-delta consumed "
        "f235aa83->3bd12e4e->d0bb09f6->913b8097 via the PATCHED d19 (dual-face live-fire x2) + DEC 4cfdd17c hold + unacked=0 "
        "+ orders_ack scan CLEAN 102/227 zero face divergence + judgment results/_r1090bmc_ord_judgment.json (amended by "
        "in-report delta-2/3 faces: 自查互查令+41曲加速令+xq32 dispatch+本地算力修订); (3) smoke 49/49; (4) P0 W268 PREREG "
        "FREEZE (facts probe = needle evidence r1077 law; four derive-run heals disclosed: 注记/注释 one-char needle, b_title "
        "double-bracket end-marker, hop_chain refuser_pts key, sec8 同窗回填 gate expectation; final ALL GATES PASS + "
        "byte-identity); (5) P1 d19 two-face patch (selftest 20/20 incl. L18/L19/L20 new legs; two unpack-site fixer scripts "
        "committed as evidence); (6) xq32 @bm-c ticket: census no-live-carrier -> loop claim -> staging map 24/8 + 13:5x "
        "revision documented (local burn primary via standing chain); partial upload rejected by 32/32 acceptance spec; "
        "(7) S6 light 10/10 rc0; (8) S7: attrition 4 CLEAN (healed notes as-is) + idle --worked rc0 idle_rounds->0 + quad "
        "green (watchdog S4U flip = adjudicated default-principal standing face) + xq MSG-1200 ignite swept into closeout "
        "commit; counter 1090->1091")

# --- state ---
sp = "state-bm-c.json"
s = json.load(io.open(sp, encoding="utf-8"))
assert s["round_no"] == 1090, "counter at open expected 1090, got %r" % s["round_no"]
s["round_no"] = 1091
s["round_no_label"] = "r1090 closeout -> counter 1091"
for k in ("last_round", "last_round_label"):
    s[k] = "r1090"
for k in ("last_round_at", "last_round_ts", "last_round_closed", "last_round_summary_at",
          "last_seen", "last_seen_at", "updated", "updated_at", "ts", "activity_now",
          "now_active", "last_action_at", "last_round_closed_at"):
    if k in s or True:
        s[k] = T
s["last_round_summary"] = did[:600]
s["last_round_summary_at"] = T
s["current_task"] = ("r1090 closeout: W268 prereg frozen + d19 two-face patch + xq32 staged; next = W268 five-face splice r1091 FIRST ACTION")
s["current_task_at"] = T
s["current_task_ts"] = EPOCH
s["did"] = did
s["last_action"] = "r1090 closeout (W268 prereg freeze + d19 two-face patch + xq32 staging; counter 1090->1091)"
s["next"] = nxt
s["next_pointer"] = nxt
s["verdict"] = verdict
s["latest_artifact"] = art
s["last_artifact"] = art
s["recent_artifact"] = art
s["next_milestone"] = ("W268 five-face splice + burn + finalize + W269 seat (r1091-r1093, within 48h); Monday 10-20 15:30 papers chain; xq32 remaining-8 on chain step-3 + director ruling")
s["prod_lanes"] = ("CPU=engine W267 complete (supply armed: W268 five-face splice r1091 FIRST ACTION); GPU=MV PACK-A i2v wave-1 in flight (CEO weekend production standing: gen-only, loop CPU-only); short-video lane DISABLED standing per O-20261017-1741")
s["r1090_closeout_note"] = note
s["orphan_face"] = 2
s["orphan_faces"] = 2
s["loop_round"] = s.get("loop_round", 0) + 1
io.open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(s, indent=1, ensure_ascii=False))
s2 = json.load(io.open(sp, encoding="utf-8"))
assert s2["round_no"] == 1091, "counter write failed"

# --- round report (canonical path) ---
row = ("| %s | r1090 | bm-c | watermark verdict=green (red=false / satengine ALIVE rc0 burns=[] queue=[] W268 prereg frozen "
       "supply armed / dualrun ZERO-DRIFT streak 47 / ORD triple-delta consumed 913b8097 tail-scan FALSE) | %s | next: W268 "
       "five-face splice r1091 FIRST ACTION (editor canon 0b39fb0f20c8aa6e + setwave aging law) + xq32 remaining-8 on chain "
       "step-3/S5-27 ruling + Monday 10-20 15:30 papers + RAM-critical watch | origin-N=0 (post-push fetch verified) |"
       % (T, did))
rp = "round_reports-bm-c.md"
t = io.open(rp, encoding="utf-8", newline="").read()
io.open(rp, "w", encoding="utf-8", newline="").write(t.rstrip("\n") + "\n" + row + "\n")
t2 = io.open(rp, encoding="utf-8", newline="").read()
assert row[:60] in t2, "round-report row missing"

# --- heartbeat ---
hp = "fleet/machines/bm-c.json"
h = json.load(io.open(hp, encoding="utf-8"))
h["machine_id"] = "bm-c"
h["last_seen"] = T
h["last_seen_at"] = T
h["ts"] = T
h["updated"] = T
h["updated_at"] = T
h["activity_now"] = T
h["now_active"] = T
h["clock_read"] = T
h["heartbeat_epoch_utc"] = EPOCH
h["current_task"] = s["current_task"]
h["current_task_ts"] = EPOCH
h["verdict"] = verdict
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["did"] = did
h["next"] = nxt
h["next_milestone"] = s["next_milestone"]
h["prod_lanes"] = s["prod_lanes"]
h["orphan_face"] = 2
h["orphan_faces"] = 2
try:
    import psutil
    h["free_ram_gb"] = round(psutil.virtual_memory().available / (1024 ** 3), 2)
    h["ram_free_gb"] = h["free_ram_gb"]
    h["idle_ram_gb"] = h["free_ram_gb"]
except Exception:
    pass
h["ram_critical_face"] = "MV PACK-A i2v GPU-lane python 4.5G squeeze (CEO weekend production legal occupant); loop CPU-only survived all-light window; watch standing"
io.open(hp, "w", encoding="utf-8", newline="\n").write(json.dumps(h, indent=1, ensure_ascii=False))
h2 = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in h2["clock_read"][:19], "clock_read must be T-separated ISO8601 (R262 law)"
s3 = json.load(io.open(sp, encoding="utf-8"))
mok = all(h2.get(k) == s3.get(k) for k in ("last_orders_sha", "last_decisions_sha",
          "last_orders_read_at", "last_decisions_read_at", "last_orders_at",
          "last_decisions_at", "last_orders_seen", "last_decisions_seen"))
assert mok, "heartbeat mirror 8-key equality broke during closeout (r1052 law)"
print("CLOSEOUT OK: counter 1090->1091 | round-report row landed | heartbeat epoch=%d int | mirrors 8-key equal | ts=%s" % (EPOCH, T))
