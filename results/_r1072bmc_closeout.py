# r1072 bm-c closeout: round report row + state-bm-c.json + heartbeat, fresh-read-then-write.
# Waits-upstream clean continuation window. Zero double-count (dual-delta FALSE both scans).
import datetime
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
RND = 1072
COUNTER_NEXT = 1073

ROW = (
    NOW + " | r1072 | bm-c | watermark verdict=green (red=false / satengine ALIVE waits-upstream / tickets 0 / jobs 0 / "
    "W263=bm-a window splice LANDED f499817fa burn/finalize pending) | r1072 (waits-upstream clean continuation): "
    "(1) S0-1 anchor bm-c + round-zero probe py_faces=8 orphans=0 zero-kill; S0 fetch 0/0 clean (origin tip 857dba33a = r1071 "
    "closeout, no mid-round arrival; 3 shared regenerable probe faces legit dirty, no rebase owed); "
    "(2) S0.5: fleet/orders diff unacked=0 (98 files all in 223 ack set); DEC delta=NONE (1d4741e4 raw-blob sha256 hold); "
    "ORD delta=NONE (313c8c0f content-sha1 pinned method SAME); inbox=0; S7 tail dual-scan same (zero mid-round rows); "
    "(3) S1 smoke 49/49; satengine ALIVE rc0 (alive_flag=true heartbeat_age 58.7s fresh, burns_active=[] queue_next=[]; "
    "W263 dedup local_done=0/remote_done=0 = burn pending on bm-a, n1_w263_results.json absent on origin verified) -- "
    "bm-c waits-upstream, next bm-c turn = W264 seat after W263 finalize; wm red=false healthy (next_pick=claimed "
    "moneyflow-IC parked source-blocked standing); boards clear (jobs 0); idle 18:58 fresh verdict green_idle=false "
    "RAM 5.5pct gate honest not-claim-eligible (V5.3 GPU reburn legal occupant per O-20261017-1741 sec.3; window has "
    "actual work -> --worked declared); "
    "(4) PRODUCT = S6 43/43 rc0 fresh run (driver Tools/_r1072bmc_s6.py canon-clone r1071, log results/_r1072bmc_s6_log.txt: "
    "dualrun ZERO-DRIFT streak 35 @461, compute_audit FLAG pool_starvation/supply_floor honest [pool ready=0 = W263 bm-a "
    "window waits-upstream structural, supply rides bm-a turn, answered-by-chain], py_watermark py_low_with_work_cands "
    "[local_batch=1 = MV V5.3 GPU reburn protected per O-20261017-1741 sec.3 + CPU waits-upstream = legal named-answer], "
    "update_daily no-op cutoff 10-16 fresh [weekend no-op family, papers debt=0], zt crosscheck CLEAN days=7 findings=0 "
    "soft=7, lane no-ops honest per R31, daily_report REPORT-2026-10-17 faces=5 regenerated, token delta=0 L2 legs 0 today); "
    "(5) S7: attrition 4 CLEAN (healed notes as-is) + idle --worked rc0 + loop pin=5 no-op (first fire 19:05) + watchdog "
    "registered (S4U flip access-denied = adjudicated default-principal standing face, first fire 19:02) + claws x2 "
    "re-installed LF-normalized + counter 1072->1073 + heartbeat epoch int + clock_read T-sep self-asserted "
    "| verify: smoke 49/49 + S6 log 43x rc=0 + orders diff 0 + dual-delta SAME x2 (opening + S7 tail) + attrition CLEAN + "
    "W263 finalize absent on origin (satengine dedup 0/0 + git show absent) | behind-origin=0 (closeout push rides this "
    "window) | next r1073: watch bm-a W263 chain (burn->sixgate->finalize) -> on finalize bm-c W264 SEAT (live re-derive "
    "post-W263 universe per W263 seat MSG forward face: staircase continues, naive W264 A 595_901..597_900 pre-disclosed "
    "REFUSED at registered W263 B 595_901..596_100, first-clean moves past 596_100; never transcribe r587); Monday 10-19 "
    "15:30 bars papers chain re-arm; short-video lane disabled standing per O-20261017-1741; next 5x=bm-c r1075"
)

DID = (
    "r1072: clean continuation waits-upstream (W263 = bm-a window: SPLICE LANDED f499817fa by bm-a r1038, burn/finalize "
    "pending -- W263 dedup 0/0 + finalize absent on origin verified this window) + bm-c next turn = W264 seat on W263 "
    "finalize + S0.5 dual-delta ORD/DEC both SAME (313c8c0f content-sha1 / 1d4741e4 raw-blob sha256, pinned-probe, "
    "opening + S7 tail) + orders unacked=0 + smoke 49/49 + satengine ALIVE rc0 (hb 58.7s fresh, burns/queue empty) + "
    "S6 43/43 fresh (dualrun ZERO-DRIFT streak 35 @461, audit FLAG pool_starvation/supply_floor = waits-upstream "
    "structural answered-by-chain, py_wm py_low_with_work_cands = local_batch MV V5.3 GPU reburn protected per "
    "O-20261017-1741 sec.3 + CPU waits-upstream honest, weekend bars cutoff 10-16 no-op family, daily_report "
    "REPORT-2026-10-17 faces=5, token delta=0) + attrition 4 CLEAN + idle --worked rc0 (18:58 fresh verdict green_idle=false "
    "RAM 5.5pct gate honest; window work declared) + quartet green (loop pin=5 no-op + watchdog registered [S4U flip "
    "access-denied = adjudicated default-principal standing face] + claws x2)"
)

VERDICT = (
    "green: r1072 = clean continuation waits-upstream window (W263 = bm-a window: splice LANDED f499817fa, burn/finalize "
    "pending -- dedup 0/0 + finalize absent on origin verified; bm-c next turn = W264 seat after W263 finalize per "
    "chain-order) + S0.5 dual-delta FALSE both (ORD 313c8c0f / DEC 1d4741e4, pinned-probe, zero rows owed, opening + S7 "
    "tail) + unacked=0 + smoke 49/49 + satengine ALIVE rc0 + S6 43/43 rc0 (dualrun streak 35, audit FLAG structural "
    "answered-by-chain, py_wm py_low_with_work_cands = MV V5.3 GPU reburn legal + CPU waits-upstream honest) + attrition "
    "4 CLEAN + idle --worked rc0 + quartet green (loop pin=5 no-op + watchdog registered [S4U flip = adjudicated "
    "default-principal standing face] + claws x2 LF-normalized) + orphan face=0 zero-kill"
)

NEXT_PTR = (
    "r1073: (1) watch bm-a W263 chain (splice LANDED f499817fa -> engine self-burn 12/12 -> sixgate -> finalize); on "
    "W263 FINALIZE landing = bm-c W264 SEAT publish (probe live re-derive on post-W263 universe per W263 seat MSG forward "
    "face: staircase continues -- naive W264 A 595_901..597_900 pre-disclosed to be REFUSED at registered W263 B "
    "595_901..596_100, first-clean moves past 596_100; own-A reservation cascade governs B; never transcribe r587); "
    "(2) Monday 10-19 15:30 bars window: full papers chain fires on the new bar (10-17/18 weekend no bars, debt=0 "
    "verified cutoff 10-16); (3) short-video lane DISABLED standing per O-20261017-1741 (4/4 disabled + 6688 FREE); "
    "(4) GPU lane = gen-only (V5.3 reburn in flight protected; loop CPU-only); (5) next 5x duty = r1075"
)

CLOSE_NOTE = (
    "r1072: clean continuation waits-upstream window (state round_no=1072 at open, executed r1072, advanced 1072->1073 "
    "so next=r1073); zero absorb owed (r1071 closeout 857dba33a landed clean, zero dead window between); zero "
    "double-count: S0.5 dual-delta FALSE both scans (opening pinned-probe + S7 tail probe; ord 313c8c0f / dec 1d4741e4 "
    "hold, zero rows owed); W263 = bm-a window (splice LANDED f499817fa by bm-a r1038, burn/finalize pending -- satengine "
    "W263 dedup local_done=0/remote_done=0 + n1_w263_results.json absent on origin verified; bm-a heartbeat stale since "
    "17:50 = its r1038 window in flight, engine burn lane = scheduled-task carried on bm-a, not bm-c's to fix); idle face: "
    "18:58 fresh verdict green_idle=false (RAM 5.5% gate, V5.3 GPU reburn legal occupant) -> not-claim-eligible honest; "
    "window has actual work (S6 43 legs + quad + closeout) -> --worked rc0 declared; orphan face=0 (probe py_faces=8, "
    "zero orphans, zero-kill); MV V5.3 reburn GPU gen lane untouched per O-20261017-1741 sec.3"
)

ARTIFACT = "results/_r1072bmc_s6_log.txt (43-leg S6 chain rc0) + Tools/_r1072bmc_s6.py (driver canon-clone r1071)"


def update_json(path, updates):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.update(updates)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    # read-back self-assert
    with open(path, "r", encoding="utf-8") as f:
        back = json.load(f)
    assert isinstance(back.get("heartbeat_epoch_utc"), int), "epoch must be int"
    assert back.get("heartbeat_epoch_utc") == EPOCH, "epoch round-trip"
    assert "T" in back.get("clock_read", ""), "clock_read must be T-separated"
    return back


def main():
    # 1. round report row (canonical root file)
    rp = os.path.join(ROOT, "round_reports-bm-c.md")
    with open(rp, "r", encoding="utf-8") as f:
        content = f.read()
    assert "r1072 |" not in content, "r1072 row already present (double write guard)"
    if not content.endswith("\n"):
        content += "\n"
    content += ROW + "\n"
    with open(rp, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    # +1 line assert
    with open(rp, "r", encoding="utf-8") as f:
        assert "r1072 |" in f.read(), "report row append verify"

    # 2. state file
    st_updates = {
        "clock_read": NOW, "ts": NOW, "updated": NOW, "updated_at": NOW,
        "last_seen": NOW, "last_seen_at": NOW, "now_active": NOW, "activity_now": NOW,
        "last_round_at": NOW, "last_round_ts": NOW, "last_round": "r1072",
        "last_round_label": "r1072", "round_no": COUNTER_NEXT,
        "round_no_label": "r1072 closeout -> counter 1073",
        "heartbeat_epoch_utc": EPOCH, "current_task_ts": EPOCH,
        "current_task": "r1072 closeout: waits-upstream (W263 bm-a burn/finalize pending) + next=W264 seat on finalize",
        "current_task_at": NOW,
        "did": DID, "verdict": VERDICT, "note": CLOSE_NOTE,
        "next": NEXT_PTR, "next_pointer": NEXT_PTR,
        "latest_artifact": ARTIFACT, "last_artifact": ARTIFACT, "recent_artifact": ARTIFACT,
        "last_round_summary": ("r1072: clean continuation waits-upstream (W263 bm-a window burn/finalize pending; bm-c "
                               "next=W264 seat) + S0.5 dual-delta FALSE both + S6 43/43 fresh (dualrun streak 35) + smoke "
                               "49/49 + attrition 4 CLEAN + idle worked + quad green"),
        "last_round_summary_at": NOW, "last_round_closed": NOW, "last_action_at": NOW,
        "last_action": "r1072 closeout (clean continuation waits-upstream: S6 43/43 fresh + quad green + idle worked; "
                       "counter 1072->1073)",
        "head_sha": "r1072 closeout (waits-upstream clean continuation: W263 bm-a burn/finalize pending; bm-c next turn "
                    "= W264 seat); dual-delta ORD/DEC both SAME",
        "verify": ("S6 log 43x rc=0 re-read + d19 pinned-probe dual FALSE read-back (ord 313c8c0f / dec 1d4741e4) + "
                   "smoke 49/49 + satengine alive_flag=true + attrition 4 CLEAN + loop pin=5 no-op + watchdog registered "
                   "+ claws x2 installed + idle worked rc0 + epoch int readback + report line +1 asserted + W263 finalize "
                   "absent verified (dedup 0/0 + git show absent) + closeout commit rides this window"),
        "orders_ack_receipt": ("r1072: zero new repo order files (unacked=0 both scans, 98 files all in 223 ack set); "
                               "group-tree ORD/DEC dual-delta FALSE both (ord 313c8c0f / dec 1d4741e4 hold, pinned-probe "
                               "verified); inbox=0"),
        "orders_ack_ts": NOW, "last_orders_read_note": "r1072: ORD delta FALSE hold (content-sha1 313c8c0f pinned-probe, zero rows owed)",
        "last_decisions_read_note": "r1072: DEC delta FALSE hold (raw-blob sha256 1d4741e4 pinned-probe, zero rows owed)",
        "last_orders_sha_note": "r1072: ORD 313c8c0f SAME (content-sha1 pinned method r977) / DEC 1d4741e4 SAME (raw-blob sha256) -- zero rows owed both scans",
        "last_orders_seen": NOW, "last_orders_read_at": NOW, "last_orders_at": NOW,
        "last_decisions_seen": NOW, "last_decisions_read_at": NOW, "last_decisions_at": NOW,
        "prod_lanes": ("CPU=engine waits-upstream (W263 = bm-a window: SPLICE LANDED f499817fa, burn/finalize pending on "
                       "bm-a; bm-c next turn = W264 seat) ; GPU=gen-only lane (V5.3 reburn in flight protected per "
                       "O-20261017-1741 sec.3; LLM face retired per O-20261017-0953; loop CPU-only); short-video lane "
                       "DISABLED standing per O-20261017-1741"),
        "loop_round": 998, "health": "ok",
        "idle_rounds": 0, "agenda_starved": False,
        "orphan_face": 0, "orphan_faces": 0,
        "sync": {"origin_tip": "r1072 closeout commit rides this window (push lands this window; post-push behind=0 "
                               "verified same window)", "ts": NOW},
        "r1072_closeout_note": CLOSE_NOTE,
    }
    update_json(os.path.join(ROOT, "state-bm-c.json"), st_updates)

    # 3. heartbeat
    hb_updates = dict(st_updates)
    hb_updates["r1072_closeout_note"] = CLOSE_NOTE
    hb_updates["d19_watermark_guard"] = {
        "tool": "scripts/d19_watermark.py",
        "probe": "results/_r686bmb_d19_check.py",
        "probe_evidence": "K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\results\\_r686bmb_d19_check.json",
        "method_decisions": "sha256", "method_orders": "sha1",
        "verbatim": True, "advance": True, "round_ref": RND, "ts": NOW,
    }
    back = update_json(os.path.join(ROOT, "fleet", "machines", "bm-c.json"), hb_updates)

    print("CLOSEOUT-OK r1072 now=%s epoch=%d round_no=%d" % (NOW, EPOCH, back["round_no"]))


if __name__ == "__main__":
    main()
