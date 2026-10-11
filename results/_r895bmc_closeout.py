# _r895bmc_closeout.py -- r895 bm-c closeout: watch round bookkeeping
# (ORD watermark advance 1394ccf8->0513e9e7 consumed BigStream-only row,
# zero BigMoney action) + heartbeat/state/round-report.
import json
import time
import datetime

ROOT = "."


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def main():
    ts = now_iso()
    epoch = int(time.time())

    # ---- state-bm-c.json: round counter advance ----
    sp = "state-bm-c.json"
    st = json.load(open(sp, encoding="utf-8"))
    old_rn = st.get("round_no")
    st["round_no"] = 896
    st["last_orders_sha"] = "0513e9e7c79aa12f45f0fd273007ada18e742d57"
    st["last_orders_read_at"] = ts
    st["last_orders_at"] = ts
    st["last_decisions_read_at"] = ts
    st["last_round"] = 895
    st["last_round_at"] = ts
    st["last_round_ts"] = ts
    json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False,
              indent=1)
    print("state: round_no %s->896 (r895 executed)" % old_rn)

    # ---- heartbeat fleet/machines/bm-c.json ----
    hp = "fleet/machines/bm-c.json"
    hb = json.load(open(hp, encoding="utf-8"))
    did = (
        "r895 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=8 "
        "orphans=1 zero-kill (MV-lane infra kept); (2) S0 fetch 0/0 "
        "synced clean (r894 closeout commit confirmed delivered, zero "
        "rebase needed); (3) S0.5 fleet orders unacked=0; ORD watermark "
        "delta TRUE -> new group orders tail row = 10-11 23:0x CEO "
        "道具席/导演席失职纠偏令 (BigStream lane, zero BigMoney repo "
        "action), advanced ord 1394ccf8->0513e9e7 (read-back full-string "
        "equality OK); DEC delta FALSE eb14c441 unchanged zero action; "
        "(4) S1 smoke 49/49; S2 boards clear (jobs 0, fleet open 0); "
        "satengine alive front=209 all-complete queue empty (W211 armed "
        "behind W210 bm-b, structural wait disclosed); (5) S6 full chain "
        "38/38 rc0 + 7 disclosed skips (_r895bmc_s6_chain.py clone of "
        "r894 driver): dualrun ZERO-DRIFT streak 10, update_daily 0 new "
        "rows (cutoff 10-09, Sunday no-op), market_clock ORANGE_COOL, "
        "strategy_scorecard 139.8s derive (6/28/7 cards), daily_scorecard "
        "+ REPORT-2026-10-11 + LIVE-2026-10-11 re-derived idempotent; "
        "compute_audit + py_watermark rc0 (GPU/RAM yielded to MV "
        "CEO-priority i2v burn, structural flags disclosed); (6) MV watch "
        "light-read: clips-local-768 = 3 mp4 (V2_KFL 21:38 + XQ_XQ28 "
        "22:14 + XQ_XQ02 23:15 NEW = first BICYCLE reshake clip landed), "
        "fails-bmc absent = zero fails; interactive window owns burn, "
        "zero lane-touch; (7) BigLife turn-green watch ongoing (window "
        "to 10-12 22:15, oversight hourly); (8) S7: idle --worked "
        "(idle_rounds=0) + attrition 4 CLEAN (healed shrink notes "
        "recorded) + loop pin=5 no-op + watchdog re-registered + "
        "precommit/prepush claws re-installed")
    nxt = (
        "r896: (1) MV XQ-24 harvest watch (clips 3/26, interactive window "
        "owns burn; harvest + receipt into O-2126 when lane completes); "
        "(2) W210 (bm-b) finalize -> M11/cron auto W211 freeze -> n1_w211 "
        "burn; (3) BigLife turn-green 24h watch (window to 10-12 22:15); "
        "(4) Monday 15:30 first new-bar window: update_daily chain + "
        "live.paper + t35_open_fill_verify + t24 legs")
    verdict = (
        "green: watch round -- ORD watermark advanced 1394ccf8->0513e9e7 "
        "(new row BigStream-only, zero BigMoney action), DEC unchanged; "
        "S6 38/38 rc0; boards clear; orphans=1 (MV-lane infra kept); "
        "GPU/RAM yielded to MV CEO-priority i2v burn (structural "
        "pool_starvation/supply_floor disclosed); MV clips 3/26 zero "
        "fails")
    hb["round_no"] = 895
    hb["loop_round"] = 895
    hb["last_round"] = 895
    hb["last_round_at"] = ts
    hb["current_task"] = ("r895: watch round -- ORD watermark advance "
                          "(BigStream-only row) + S6 38/38 + MV lane "
                          "light-watch + closeout")
    hb["current_task_at"] = ts
    hb["did"] = did
    hb["last_round_summary"] = did
    hb["last_action"] = ("r895 ORD watermark advance (0513e9e7) + S6 "
                         "38/38 + closeout")
    hb["verdict"] = verdict
    hb["next"] = nxt
    hb["next_pointer"] = nxt
    hb["next_milestone"] = nxt
    hb["now_active"] = (
        "r895: MV i2v fresh-frames burn ACTIVE on GPU (interactive window "
        "owns, XQ02 bicycle clip landed 23:15); W211 armed behind W210 "
        "(bm-b); BigMoney watch face; BigLife turn-green watch ongoing")
    hb["activity_now"] = hb["now_active"]
    hb["last_artifact"] = (
        "results/_r895bmc_s6_log.txt 38/38 rc0 (2026-10-11 23:2x) + "
        "docs/daily_report/REPORT-2026-10-11.md + "
        "docs/live_usage/LIVE-2026-10-11.md idempotent re-derive")
    hb["recent_artifact"] = hb["last_artifact"]
    hb["latest_artifact"] = hb["last_artifact"]
    hb["last_round_closed"] = ts
    hb["last_action_at"] = ts
    hb["last_round_summary_at"] = ts
    hb["heartbeat_epoch_utc"] = epoch
    hb["clock_read"] = ts
    hb["ts"] = ts
    hb["last_seen"] = ts
    hb["last_seen_at"] = ts
    hb["updated_at"] = ts
    hb["updated"] = ts
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    hb["prod_lanes"] = (
        "GPU=MV album i2v fresh-frames burn ACTIVE (~655MiB free, "
        "interactive window owns); CPU=W211 armed behind W210 (bm-b) + "
        "RAM gate ~1.9GB on heavy batches")
    hb["free_ram_gb"] = 1.93
    hb["idle_ram_gb"] = 1.93
    hb["ram_free_gb"] = 1.93
    hb["gpu_free_vram_mb"] = 655
    hb["gpu_free_vram_mib"] = 655
    hb["gpu_free_mb"] = 655
    hb["gpu_free_mib"] = 655
    hb["cpu_pct"] = 24.0
    hb["cpu_util_pct"] = 24.0
    hb["cpu_idle_pct"] = 76.0
    hb["last_decisions_sha"] = (
        "eb14c441ba0131e26e3c3b2fafc17900747152dd463a654beacffdce65ef5d73")
    hb["last_decisions_at"] = ts
    hb["last_decisions_read_at"] = ts
    hb["last_orders_sha"] = "0513e9e7c79aa12f45f0fd273007ada18e742d57"
    hb["last_orders_at"] = ts
    hb["last_orders_read_at"] = ts
    hb["last_orders_sha_note"] = (
        "r895 advanced: 1394ccf8->0513e9e7 via d19_watermark update "
        "--advance (legal path, facts-driven from _s05_probe.bm-c.json, "
        "read-back full-string equality OK); new row = 10-11 23:0x "
        "BigStream 道具令 face, zero BigMoney action")
    hb["orders_ack_receipt"] = (
        "r895: no new fleet orders (unacked=0); ORD group-tree delta "
        "consumed (BigStream-only row, zero repo action); DEC unchanged "
        "eb14c441")
    hb["orphan_face"] = ("orphans=1 (MV-lane infra KEPT: ComfyUI :8188 "
                         "actively rendering; zero-kill per MV-lane "
                         "domain)")
    hb["orphan_faces"] = 1
    hb["verify"] = (
        "receipts: smoke 49/49 + S6 38/38 rc0 (_r895bmc_s6_log.txt) + "
        "dualrun streak 10 + attrition 4 CLEAN + WM advance read-back OK "
        "+ idle --worked + push self-proof below")
    hb["sync"] = {
        "ahead_behind": "r895 closeout commit rides this push",
        "origin_tip": "pending",
        "ts": ts,
        "note": "r895 closeout commit+push this round; rev-list "
                "self-proof logged in round report",
    }
    json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False,
              indent=1)
    # epoch int self-proof
    chk = json.load(open(hp, encoding="utf-8"))
    e = chk.get("heartbeat_epoch_utc")
    assert isinstance(e, int) and not isinstance(e, bool), (
        "epoch must be JSON int, got %r" % type(e))
    assert "T" in chk.get("clock_read", ""), "clock_read must be ISO8601 T"
    print("heartbeat: round 895 written, epoch int %d OK" % e)

    # ---- round report row ----
    rp = "round_reports-bm-c.md"
    row = (
        "%s | r895 | bm-c | %s | evidence: smoke 49/49 + S6 38/38 rc0 "
        "(_r895bmc_s6_log.txt) + dualrun streak 10 + attrition 4 CLEAN + "
        "ORD advance 1394ccf8->0513e9e7 read-back OK (BigStream-only row) "
        "+ MV clips 3/26 light-read + push range self-proof below | "
        "next: %s | [r895 bm-c]\n" % (ts, did, nxt))
    with open(rp, "a", encoding="utf-8", newline="") as f:
        f.write(row)
    print("round report: r895 row appended")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
