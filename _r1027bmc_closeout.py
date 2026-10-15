# -*- coding: utf-8 -*-
# r1027 bm-c closeout: state + heartbeat + round report (canonical ROOT path per r750 law)
import io, json, time, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
ORD_SHA = "3b1ca198bdd95a57635bab465f0c8bcb9c7d4cf8"
DEC_SHA = "ab3f0cc9f4cb9bbb1f23c5e5a98bd5bed540a272b0b111bb481120ea7e0ba8fd"

DID = ("r1027 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=2 zero-kill + S0 stash-bridge ff 6c838862c "
       "(bm-a r1016 estate; 6 overlapping regenerable faces stash-dropped live-wins, rerun by this window's S6); "
       "(2) DEAD-WINDOW ESTATE VERIFIED LANDED (zero absorb owed -- commit+push were done by the dead window itself): "
       "W20 FREEZE funnel 3/5 = research/TRIAL_LABOR_W20_PREREG.md FROZEN (31-cell roster) + kin-orthogonality probe + "
       "SEED_REGISTRY 3 keys 20650000/20650500/20651000 + ticket T-2026-10-15-187-P1 + F-04 MSG + E69 card, commit 06f323b92 13:27:46 origin-landed; "
       "(3) S0.5 dual-delta TRUE both consumed: ORD 1 row (10-15 13:1x O-20261015-1250 memory-mechanism batch, leg-5 fleet-promotion @bm-c) + "
       "DEC D-20261015-04/05/06 (all committee memory-law rows; bm-c leg = fleet promotion); watermarks advanced ord=@@ORD@@ dec=@@DEC@@ read-back OK; unacked=[]; "
       "(4) S1 smoke 49/49; (5) P0 CEO-order leg-5 EXECUTED: memory-budget-gate v1.1 promoted on bm-c -- origin blob f37162be materialized to "
       "bigmoney Tools/ (hash-verified) + enforced 298,454B/247 entries -> 119,202B/104 entries (143 entries verbatim-routed to 9 topic files, "
       "zero deletion, double snapshot: manual + script) + HQ-MemoryBudgetGate schtasks registered (every 4h pythonw --scheduled silent chain, "
       "next run 17:41) + /run live-fire PASS + gate-log lines landed; DEFECT FOUND+FIXED SAME-WINDOW: gate v1.1 index-block non-idempotent "
       "compounding leak (+814B per enforcement run: '- [memory-gate]' header hits KEEP whitelist kept as Reference entry while rebuild re-appends "
       "fresh block) -- empirically proven (3 runs +814/+814/0), surgical patch (skip index-block entries in keep loop), idempotence verified "
       "delta=0B index_blocks=1, F-20261015-02 filed in HQ-FEEDBACK.md (origin canonical needs same patch -- any over-budget machine leaks "
       "~4.9KB/day continuous); (6) S3: satengine ALIVE rc0 queue 0; W245 cycle CLOSED by bm-a r1015 (finalize landed) + W246 seat published by "
       "bm-a same-window (chain theirs per own-seat continuity); wm red=false; jobs 0; idle green_idle=false RAM 3.5 percent honest (U256 deferred); "
       "MV V4 GPU lane: no bm-a director-review row on origin as of 13:2x fetch -> POOL-0014 i2v batch still gated upstream; "
       "(7) S6 43/43 rc0 full chain (dualrun streak 51 drift=False; collectors pre-15:30 no-op; papers legs gated no-new-bar); "
       "(8) S7: attrition CLEAN + loop pin + watchdog + claws x2 + inbox sweep (own W20-freeze MSG + W246-seat MSG -> processed; 2 bm-b->bm-a "
       "MSGs left) + counter 1027->1028").replace("@@ORD@@", ORD_SHA).replace("@@DEC@@", DEC_SHA)

VERDICT = ("green: W20 freeze landed (funnel 3/5 by dead window, verified) -> runner build = r1028 first action per prereg sec.8; "
           "memory-gate promotion leg executed full (enforce+task+live-fire+defect-fix+HQ-feedback); "
           "W246 = bm-a seat in-flight (chain theirs); MV V4 i2v gated on bm-a director review (POOL-0014, structural-wait honest); "
           "RAM gate 3.5% closed -> U256 claims deferred honest")

NEXT = ("r1028: (1) W20 runner build = FIRST ACTION (funnel 4/5 per prereg sec.8: clone trial_labor_w19.py base + _entry_load CRLF-canonical "
        "verbatim + sec.3 three fn-family definitions verbatim + three gates embedded + reform-face blocks + G-face assertion battery + GBK "
        "reconfigure + selftest hermetic all-green -> identity-face three-command first run -> announce runner landed; 31-cell B-side param "
        "enumerator + mask_days probe alignment) -> GENERATE/SCREEN/JUDGE/intake (funnel 5/5, >5min into pool per O-2100); "
        "(2) bars 10-15 due 15:30 -> update_daily gate -> papers full chain (live.paper REGIME_GUARD enforce + t35 + t24 x2 + aggr/alloc/grid/"
        "system_v1 + export + faces); (3) MV V4 GPU lane: watch origin for bm-a director review of JAY-REDO-KF-BOARD-r1025.jpg -> i2v INT8 768P "
        "full batch (batch-sampling law per O-20261014-1325); (4) RAM gate opens -> U256 bmc-w001/w003 claims; (5) S8 prompt wiring: re-check "
        "bm-b sentinel edit on origin (Tools/sentinel_bm-c.py foreign edit still uncommitted locally)")

ARTIFACT = ("r1027: memory-budget-gate bm-c promotion (Tools/memory-budget-gate.py v1.1+idempotence patch + HQ-MemoryBudgetGate 4h task + "
            "gate-log 4 lines + injection face 298,454->119,202B) + F-20261015-02 HQ-FEEDBACK row + results/_r1027bmc_s6chain_rc.log (this commit)")

PROD_LANES = ("CPU=N1 W246=bm-a seat in-flight (prereg derive = their next action; chain theirs) ; SUPPLY=W20 FROZEN funnel 3/5 -> runner "
              "build = r1028 first action (ticket T-2026-10-15-187-P1 locked bm-c) ; GPU=MV V4 POOL-0014 awaiting bm-a director review -> i2v "
              "INT8 768P full batch next ; MEMORY-GATE=HQ-MemoryBudgetGate deployed+armed every 4h (bm-c leg of O-20261015-1250 closed)")

VERIFY = ("receipts: smoke 49/49 + S6 43/43 rc0 (results/_r1027bmc_s6chain_rc.log) + dualrun streak 51 drift=False + attrition CLEAN + "
          "gate enforcement 298454->119202B / 247->104 entries + idempotence delta=0B + HQ-MemoryBudgetGate registered (next run 17:41) + "
          "gate-log 4 lines + F-20261015-02 filed + d19 advance ord/dec read-back full-string OK + orphan face=2 zero-kill + W20 freeze "
          "origin-landed 06f323b92")

NOW_ACTIVE = "%s | r1027 | bm-c: O-1250 leg-5 memory-gate promotion (enforce+task+defect-fix+HQ-FB) + W20 freeze estate verified + S6 43/43 | counter 1027->1028 (r1027 exec)" % NOW

def load(p):
    with io.open(p, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save(p, d):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")

# --- state-bm-c.json ---
sp = "state-bm-c.json"
st = load(sp)
st["round_no"] = 1028
st["last_round"] = "r1027"
st["last_round_label"] = "r1027"
st["round_no_label"] = "r1027"
st["last_round_at"] = NOW
st["last_round_closed"] = NOW
st["last_seen"] = NOW
st["last_seen_at"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["clock_read"] = NOW
st["heartbeat_epoch_utc"] = EPOCH
st["current_task"] = "r1027 closeout: O-1250 leg-5 memory-gate promotion on bm-c + W20 freeze estate verified landed"
st["current_task_at"] = NOW
st["current_task_ts"] = EPOCH
st["did"] = DID
st["verdict"] = VERDICT
st["next"] = NEXT
st["next_pointer"] = NEXT
st["note"] = NEXT
st["next_milestone"] = "r1028: W20 runner build (funnel 4/5) + bars 15:30 papers full chain + MV V4 i2v batch on director review"
st["latest_artifact"] = ARTIFACT
st["recent_artifact"] = ARTIFACT
st["last_artifact"] = ARTIFACT
st["now_active"] = NOW_ACTIVE
st["activity_now"] = NOW_ACTIVE
st["last_action"] = "r1027 closeout (O-1250 leg-5 memory-gate promotion + W20 freeze estate verification)"
st["last_action_at"] = NOW
st["last_round_summary"] = ("r1027: W20 freeze (funnel 3/5) dead-window estate verified landed 06f323b92 + O-1250 leg-5 memory-gate promotion "
                           "executed full (298->119KB + 4h task + live-fire + v1.1 index-leak defect found/fixed/F-20261015-02 filed) + S0.5 "
                           "ORD/DEC consumed + S6 43/43 + S7 quad green")
st["last_round_summary_at"] = NOW
st["prod_lanes"] = PROD_LANES
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["last_orders_sha"] = ORD_SHA
st["last_orders_at"] = NOW
st["last_orders_read_at"] = NOW
st["last_orders_seen"] = NOW
st["last_decisions_sha"] = DEC_SHA
st["last_decisions_at"] = NOW
st["last_decisions_read_at"] = NOW
st["last_decisions_seen"] = NOW
st["last_orders_sha_note"] = ("r1027: ORD delta 5b0dd02b->3b1ca198 consumed (1 new row = 10-15 13:1x O-20261015-1250 memory-mechanism batch "
                              "executed+dispatched row; bm-c leg-5 fleet-promotion executed THIS window: gate+task+defect-fix+HQ-FB; rows 12:2x/"
                              "12:3x were consumed by the dead-window 12:41 probe advance); watermark self-advanced")
st["verify"] = VERIFY
st["d19_watermark_guard"]["ts"] = NOW
st["d19_watermark_guard"]["round_ref"] = 1028
st["r1027_closeout_note"] = ("r1027 closeout: clean continuation window after dead r1027-predecessor (self-labeled r1027, committed+pushed the "
                             "W20 freeze four-piece 06f323b92 13:27:46, then died pre-closeout with counter still 1027; its S0.5 probe at 12:41 "
                             "advanced ORD->5b0dd02b/DEC->6d917806 consuming the 12:2x/12:3x committee rows) -- this session executed as r1027 "
                             "continuation per bm-c absorb precedent lineage (30th instance, zero estate owed: freeze commit origin-landed), "
                             "advanced counter 1027->1028 so next session = r1028; zero double-count: ORD rows after 5b0dd02b (13:1x O-1250) + "
                             "DEC rows after 6d917806 (D-04/05/06) consumed THIS window with watermarks advanced read-back-verified; W246 seat = "
                             "bm-a (own-seat continuity, prereg derive theirs); O-1250 leg-5 receipts = Tools/memory-budget-gate.py + "
                             "HQ-MemoryBudgetGate task + gate-log.txt + F-20261015-02 + this commit")
save(sp, st)

# --- heartbeat fleet/machines/bm-c.json ---
hp = "fleet/machines/bm-c.json"
hb = load(hp)
hb["round_no"] = 1028
hb["round_no_label"] = "r1027"
hb["last_round"] = "r1027"
hb["last_round_at"] = NOW
hb["last_seen"] = NOW
hb["last_seen_at"] = NOW
hb["clock_read"] = NOW
hb["ts"] = NOW
hb["updated"] = NOW
hb["updated_at"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["current_task"] = "r1027 closeout: O-1250 leg-5 memory-gate promotion + W20 freeze estate verified"
hb["current_task_at"] = NOW
hb["did"] = DID
hb["verdict"] = VERDICT
hb["next"] = NEXT
hb["next_pointer"] = NEXT
hb["note"] = NEXT
hb["next_milestone"] = "r1028: W20 runner build (funnel 4/5) + bars 15:30 papers + MV V4 i2v on director review"
hb["latest_artifact"] = ARTIFACT
hb["last_artifact"] = ARTIFACT
hb["recent_artifact"] = ARTIFACT
hb["now_active"] = NOW_ACTIVE
hb["activity_now"] = NOW_ACTIVE
hb["last_action"] = "r1027 closeout (memory-gate promotion + W20 estate verification)"
hb["last_round_summary"] = st["last_round_summary"]
hb["prod_lanes"] = PROD_LANES
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["last_orders_sha"] = ORD_SHA
hb["last_orders_at"] = NOW
hb["last_orders_read_at"] = NOW
hb["last_orders_seen"] = NOW
hb["last_decisions_sha"] = DEC_SHA
hb["last_decisions_at"] = NOW
hb["last_decisions_read_at"] = NOW
hb["last_decisions_seen"] = NOW
hb["verify"] = VERIFY
hb["sync"] = {"origin_tip": "closeout commit+push rides this window", "ts": NOW, "ahead_behind": "0/0 pre-closeout"}
hb["d19_watermark_guard"]["ts"] = NOW
hb["d19_watermark_guard"]["round_ref"] = 1028
hb["full_load_selfproof"] = {
    "占用一行": "CPU=W20 runner build queued (r1028 first action, ticket locked bm-c) + W246=bm-a chain in-flight; GPU=ComfyUI resident idle (MV V4 POOL-0014 i2v gated on bm-a director review); MEMORY-GATE=HQ-MemoryBudgetGate armed every 4h",
    "当前活": "r1027 closeout: O-1250 leg-5 memory-gate promotion executed full + W20 freeze estate verified landed",
    "最近实物": "Tools/memory-budget-gate.py (v1.1+幂等补丁) + HQ-MemoryBudgetGate schtasks + F-20261015-02 HQ-FEEDBACK row (13:4x)",
    "下个交付物": "W20 runner build (funnel 4/5) -> GENERATE/SCREEN/JUDGE -> 48h CEO 呈报钟; bars 15:30 papers full chain",
    "队列水位": "N1 engine 0 burning (W246=bm-a wave) · MV V4 i2v gated upstream · P2/P3 queues clear · U256 w001/w003 deferred RAM gate 3.5% · bars 10-15 due 15:30"
}
save(hp, hb)

# --- round report row (canonical ROOT path, r750 law) ---
ROW = "@@NOW@@ | r1027 | bm-c | r1027: (1) S0-1 anchor + probe 6/2 zero-kill + S0 stash-bridge ff 6c838862c (bm-a r1016); (2) W20 FREEZE funnel 3/5 dead-window estate VERIFIED LANDED (06f323b92 13:27:46 origin: prereg 31-cell FROZEN + SEED_REGISTRY 3 keys + ticket T-2026-10-15-187-P1 + F-04 MSG + E69); (3) S0.5 ORD 1 row (O-20261015-1250 leg-5) + DEC D-04/05/06 consumed, watermarks ord=3b1ca198/dec=ab3f0cc9 read-back OK, unacked=0; (4) smoke 49/49; (5) P0 CEO-order leg-5 EXECUTED: memory-budget-gate v1.1 promoted (origin blob f37162be hash-verified -> bigmoney Tools/) + enforced 298454B/247 -> 119202B/104 entries (143 verbatim->9 topics zero-deletion double-snapshot) + HQ-MemoryBudgetGate schtasks 4h pythonw registered + /run live-fire + gate-log; DEFECT found+fixed same-window: v1.1 index-block non-idempotent leak (+814B/run, 3-run proof) -> surgical patch -> idempotence delta=0B -> F-20261015-02 filed (origin canonical needs same patch); (6) S3: satengine ALIVE rc0; W245 closed bm-a + W246 seat bm-a (chain theirs); wm red=false; idle RAM-gate 3.5pct honest; MV V4 POOL-0014 i2v still gated upstream (no director-review row); (7) S6 43/43 rc0 (dualrun streak 51, collectors pre-15:30 no-op, papers gated no-new-bar); (8) S7 quad green + inbox sweep (own+seat MSGs processed) + counter 1027->1028 | verify: results/_r1027bmc_s6chain_rc.log + gate-log.txt + smoke 49/49 + d19 read-back | next: r1028 W20 runner build FIRST ACTION (funnel 4/5 per prereg sec.8) + bars 15:30 papers full chain + MV V4 i2v on director review\n".replace("@@NOW@@", NOW)
rp = "round_reports-bm-c.md"
with io.open(rp, "r", encoding="utf-8-sig") as f:
    txt = f.read()
assert " | r1027 | " not in txt.split("\n")[-2] if len(txt.split("\n")) > 1 else True
txt += ROW
with io.open(rp, "w", encoding="utf-8", newline="") as f:
    f.write(txt)

# --- read-back asserts ---
st2 = load(sp)
hb2 = load(hp)
assert st2["round_no"] == 1028 and st2["last_round"] == "r1027", "state face mismatch"
assert isinstance(st2["heartbeat_epoch_utc"], int), "epoch not int"
assert hb2["heartbeat_epoch_utc"] == EPOCH and isinstance(hb2["heartbeat_epoch_utc"], int), "hb epoch mismatch"
assert st2["last_orders_sha"] == ORD_SHA and st2["last_decisions_sha"] == DEC_SHA, "watermark mismatch"
print("CLOSEOUT-OK state+heartbeat+roundreport written; epoch=%d now=%s" % (EPOCH, NOW))
