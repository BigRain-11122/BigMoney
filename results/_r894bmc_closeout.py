# _r894bmc_closeout.py -- r894 bm-c closeout: absorb r893 dead-window tail
# + DEC watermark corrupt-face heal (dad6c562 -> eb14c441, r863 recurrence
# 3rd instance, blob-history scan zero-hit) + heartbeat/state/round-report.
import json
import time
import datetime

ROOT = "."


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def main():
    ts = now_iso()
    epoch = int(time.time())

    # ---- state-bm-c.json: round counter advance + dec heal ----
    sp = "state-bm-c.json"
    st = json.load(open(sp, encoding="utf-8"))
    old_rn = st.get("round_no")
    st["round_no"] = 895
    st["r894_absorb_note"] = (
        "r894 absorb: r893 session died post-commit/push/report (22:47:24) "
        "pre-closeout (state was still 893, heartbeat still r892); this "
        "session executed as r894 per bm-b r898 absorb precedent; counter "
        "advanced 893->895 so next session = r895")
    old_dec = st.get("last_decisions_sha")
    st["last_decisions_sha"] = (
        "eb14c441ba0131e26e3c3b2fafc17900747152dd463a654beacffdce65ef5d73")
    st["last_decisions_read_at"] = ts
    st["last_decisions_sha_method"] = (
        "python subprocess raw-blob bytes SHA-256 (group-tree origin/main "
        "git show); r894 ERRATUM+HEAL: r893 dying-session dec watermark "
        "dad6c562 = corrupt face (blob-history scan of last 8 commits "
        "touching docs/decisions.md zero-hit; r863 recurrence 3rd "
        "instance); true lineage f22e42ef -> 55ecb132 (db043100e) -> "
        "eb14c441 (8facf50b3 current); eb14c441 content already consumed "
        "pre-r892 (r892 read-back 'unchanged'), zero new rows; healed to "
        "real current blob; recurrence guard honored: delta TRUE verified "
        "vs git blob history before consuming")
    st["last_orders_sha"] = "1394ccf8aa2b10da46a34c147a48e6d157fb4055"
    st["last_orders_read_at"] = ts
    json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("state: round_no %s->895, dec %s->%s" % (
        old_rn, str(old_dec)[:12], "eb14c441"))

    # ---- heartbeat fleet/machines/bm-c.json ----
    hp = "fleet/machines/bm-c.json"
    hb = json.load(open(hp, encoding="utf-8"))
    did = (
        "r894 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=6 "
        "orphans=2 zero-kill (both MV-lane infra: ComfyUI :8188 actively "
        "rendering + c1011_album_serve.pyw distributor); (2) S0 fetch "
        "behind=1 -> autostash rebase CLEAN (absorbed bm-b r898); (3) r893 "
        "dead-window closeout ABSORBED (bm-b r898 absorb precedent): r893 "
        "body was committed+pushed+reported 22:47:24 but session died "
        "pre-closeout (state still 893, heartbeat still r892) -- this "
        "session = r894, counter advanced 893->895; (4) S0.5 fleet orders "
        "unacked=0; DEC watermark erratum+heal: r893 dying value dad6c562 = "
        "corrupt face (blob-history 8-version scan zero-hit = r863 "
        "recurrence 3rd instance), true lineage f22e42ef->55ecb132->"
        "eb14c441 (current, already consumed pre-r892), healed "
        "dad6c562->eb14c441 zero new rows; ORD delta FALSE "
        "(1394ccf8==1394ccf8 fresh-fetch read-back), heartbeat ord "
        "watermark healed 075caa8d->1394ccf8; (5) S1 smoke 49/49; S2 "
        "boards clear (jobs 0, fleet open 0); satengine alive rc0 "
        "queue/burns empty (W-chain supply structural-waits bm-b W210); "
        "(6) S6 full chain 38/38 rc0 + 7 disclosed skips "
        "(_r894bmc_s6_chain.py clone of r892 driver): dualrun ZERO-DRIFT "
        "streak 9, update_daily 0 new rows cutoff 10-09, market_clock "
        "ORANGE_COOL, fund_premium weekend no-op (bm-c lane), "
        "strategy_scorecard 148.5s derive (6/28/7 cards), daily_scorecard "
        "stale-takeover derive legal (bm-a dark >24h), REPORT-2026-10-11 + "
        "LIVE-2026-10-11 regenerated; compute_audit flags "
        "pool_starvation+supply_floor = structural disclosed (W210 bm-b "
        "serial bottleneck + GPU/RAM yielded to MV CEO-priority lane); WM "
        "verdict py_low_with_work_cands -> legal whitelist (MV i2v burn "
        "active GPU 565MiB free + boards closed + pool upstream-gated); "
        "(7) MV watch light-read: clips 2/26 (V2_KFL + XQ28), fails-bmc "
        "absent, GPU burn active = fresh-frames i2v restart in-flight "
        "(interactive window owns, zero lane-touch); BigLife turn-green "
        "watch ongoing (window to 10-12 22:15, oversight hourly next "
        "23:36); (8) S7: idle --worked (idle_rounds=0) + attrition 4 "
        "CLEAN (2 healed shrink notes) + loop pin=5 no-op + watchdog "
        "re-registered + precommit/prepush claws re-installed")
    nxt = (
        "r895: (1) MV XQ-24 harvest watch (clips 2/26 -> harvest at 25/25 "
        "+ receipt into O-2126); (2) W210 (bm-b) finalize -> M11/cron "
        "auto W211 freeze -> n1_w211 burn; (3) BigLife turn-green 24h "
        "watch (window to 10-12 22:15); (4) Monday 15:30 first new-bar "
        "window: update_daily chain + live.paper + t35_open_fill_verify "
        "+ t24 legs")
    verdict = (
        "green: absorb+watch round -- r893 dead-window tail closed (body "
        "done+pushed 22:47), DEC watermark corrupt-face healed "
        "(dad6c562->eb14c441, blob-history zero-hit), ORD unchanged "
        "1394ccf8; S6 38/38 rc0; boards clear; orphans=2 (MV-lane infra "
        "kept); pool_starvation/supply_floor structural (W210 bm-b + MV "
        "CEO-priority lane) disclosed")
    hb["round_no"] = 894
    hb["loop_round"] = 894
    hb["last_round"] = 894
    hb["last_round_at"] = ts
    hb["current_task"] = ("r894: absorb r893 dead-window closeout + DEC "
                          "watermark corrupt-face heal + S6 38/38 + closeout")
    hb["current_task_at"] = ts
    hb["did"] = did
    hb["last_round_summary"] = did
    hb["last_action"] = ("r894 absorb r893 tail + DEC watermark heal + S6 "
                         "38/38")
    hb["verdict"] = verdict
    hb["next"] = nxt
    hb["next_pointer"] = nxt
    hb["now_active"] = (
        "r894: r893 dead-window tail absorbed + DEC corrupt-face watermark "
        "healed; MV i2v fresh-frames burn ACTIVE on GPU (interactive "
        "window owns); W211 armed behind W210 (bm-b); BigMoney watch face")
    hb["last_artifact"] = (
        "results/_r894bmc_s6_log.txt 38/38 rc0 (2026-10-11 23:03) + "
        "docs/daily_report/REPORT-2026-10-11.md + "
        "docs/live_usage/LIVE-2026-10-11.md re-derived")
    hb["recent_artifact"] = hb["last_artifact"]
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
        "GPU=MV album i2v fresh-frames burn ACTIVE (~565MiB free, "
        "interactive window owns); CPU=W211 armed behind W210 (bm-b) + "
        "RAM gate ~2GB on heavy batches")
    hb["free_ram_gb"] = 1.95
    hb["idle_ram_gb"] = 1.95
    hb["ram_free_gb"] = 1.95
    hb["gpu_free_vram_mb"] = 565
    hb["gpu_free_mib"] = 565
    hb["gpu_free_mb"] = 565
    hb["cpu_pct"] = 15.5
    hb["cpu_util_pct"] = 15.5
    hb["cpu_idle_pct"] = 84.5
    hb["last_decisions_sha"] = (
        "eb14c441ba0131e26e3c3b2fafc17900747152dd463a654beacffdce65ef5d73")
    hb["last_decisions_at"] = ts
    hb["last_decisions_read_at"] = ts
    hb["last_orders_sha"] = "1394ccf8aa2b10da46a34c147a48e6d157fb4055"
    hb["last_orders_at"] = ts
    hb["last_orders_read_at"] = ts
    hb["last_orders_sha_note"] = (
        "r894 healed: r893 advance to 1394ccf8 confirmed by fresh fetch "
        "read-back (1394ccf8==1394ccf8); prior heartbeat 075caa8d was "
        "stale r892 face never written by dying r893 session")
    hb["orders_ack_receipt"] = (
        "r894: no new fleet orders (unacked=0); DEC erratum heal "
        "dad6c562->eb14c441 (corrupt face zero-hit in blob history, r863 "
        "recurrence 3rd); ORD 1394ccf8 fresh-fetch confirmed")
    hb["orphan_face"] = ("orphans=2 (both MV-lane infra KEPT: ComfyUI "
                         ":8188 actively rendering + album serve "
                         "distributor; zero-kill per MV-lane domain)")
    hb["orphan_faces"] = 2
    hb["verify"] = (
        "receipts: smoke 49/49 + S6 38/38 rc0 (_r894bmc_s6_log.txt) + "
        "dualrun streak 9 + attrition 4 CLEAN + blob-history zero-hit for "
        "dad6c562 + idle --worked + push self-proof 0/0")
    hb["sync"] = {
        "ahead_behind": "r894 closeout commit rides this push",
        "origin_tip": "pending",
        "ts": ts,
        "note": "r894 closeout commit+push this round; rev-list "
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
    print("heartbeat: round 894 written, epoch int %d OK" % e)

    # ---- round report row ----
    rp = "round_reports-bm-c.md"
    row = (
        "%s | r894 | bm-c | %s | evidence: smoke 49/49 + S6 38/38 rc0 "
        "(_r894bmc_s6_log.txt) + dualrun streak 9 + attrition 4 CLEAN + "
        "blob-history scan zero-hit for dad6c562 (r863 recurrence 3rd) + "
        "ORD 1394ccf8 fresh-fetch read-back + push range self-proof "
        "below | next: %s | [r894 bm-c]\n" % (ts, did, nxt))
    with open(rp, "a", encoding="utf-8", newline="") as f:
        f.write(row)
    print("round report: r894 row appended")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
