# -*- coding: utf-8 -*-
# r923 bm-c closeout: state round_no 922->923 + heartbeat write-back (epoch int law).
import json, time, datetime

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

verdict = ("green: W220 FULL CYCLE landed same-window (freeze a9aee1d05 + engine self-burn 12/12 "
           "[engine ledger appends ce73fc399+f0abb96f6] + six-gate PRE-FINALIZE ALL GREEN in burn window "
           "(3rd consecutive correct-phase wave) + finalize one-pass 905,589+2,200=907,789 EXACT, "
           "merged K=481,920 EXACT, mu -0.09280/sigma 0.24512, five-key ALL PASS "
           "(key1 0.000055/key2 -0.0028pct/key3 0.0022/key4 -0.0001), prereg sec.7/8 backfilled; "
           "smoke 49/49; engine alive; ORD watermark advanced 765af33b->7643d0520 "
           "(O-20261012-1115 CEO yong-ji lane-pause order consumed: bm-a pauses, bm-c = full-load per order, "
           "already at full load via never-dry wave chain, zero extra action)")

cur_task = ("W220 full cycle landed; W221 seat probe + publication = next window FIRST ACTION "
            "(post-W220 universe re-derive mandated by W220 prereg sec.8 projection; "
            "staircase A-hops-prior-B EIGHTY-FIRST instance expected: naive A 500_804..502_803 "
            "refused by W220 B band 500_804..501_003; B own-A exclusion reserve)")

did = ("2026-10-12 12:1x | r923 | bm-c absorb r922/r923 dead-window estate (both zero-commit, zero "
       "round-number debt, this window IS r923) + PRODUCT: W220 FULL CYCLE completed same-window -- "
       "editor_gen two find-string bugs fixed (parfull-msg tail leg W217->W218 + prereg-note chain "
       "3->4 levels: transform-gen find strings must be written against POST-BLANKET text, not raw "
       "source) -> five-face freeze splice LANDED (a9aee1d05 pushed; bands A 498_804..500_803 staircase "
       "EIGHTIETH E36 hops=1 + B 500_804..501_003 own-A exclusion hops=1; banned ADMIT rc0; pf selftest "
       "9/9 + n1 selftest PASS) -> engine daemon mtime-watch hot-reload self-burned 12/12 (shards on disk "
       "11:4x-11:5x, engine ledger append commits ce73fc399+f0abb96f6) -> six-gate PRE-FINALIZE ALL GREEN "
       "in burn window (_r923bmc_w220_sixgate_receipt.json: banned+pf 9/9+n1 PASS+shards 12/12+seed_admit "
       "FREE x2 seat-time r921+freeze-time+WAVE_CONFIGS[220] engine_owner=bm-c a_seed_base=498804/"
       "b_exit=500804+ledger_pre 905,589) -> finalize one-pass LANDED (ledger identity 905,589+2,200=907,789 "
       "EXACT; merged K=481,920 EXACT; merged mu -0.09279922 sigma 0.24511808; w220-only mu -0.09285445; "
       "skill_line 1.1911->1.191 delta -0.0001; se_mu@K481920 0.000353 narrowing chain held; voids "
       "LOWAMP-P1/P2) -> five-key probe ALL PASS (_r923bmc_w220_fivekey_receipt.json) -> prereg sec.7/8 "
       "backfilled machine-read -> pushed 372706f0c | 220th engine wave / bm-c 50th own | M11 stale row "
       "done-flip (queue hygiene, W211 mission complete evidence) | own W220 seat MSG archived to "
       "inbox/processed | S6 freshness legs rc0 (pool_dualrun+compute_audit+py_watermark+token_meter, "
       "8 disclosed skips new-bar/monthly; full 38-leg chain ran r914 window this morning; Monday 15:30 "
       "new-bar full chain = today close window) | S0.5: orders unacked=0 (all 79 files acked); ORD "
       "watermark advanced 765af33b->7643d0520 (rows 10-12 10:1x/10:5x/11:0x BigStream-only zero BigMoney "
       "action + O-20261012-1115 CEO lane-pause order: bm-a pause face, bm-c full-load per order text = "
       "already satisfied by never-dry chain); DEC 94c93393 held zero action | smoke 49/49 | "
       "orphan-faces=3 (MV-lane i2v x2 + album serve; probe read-only zero-kill per lane-attribution law; "
       "ComfyUI server alive cpuDelta17 = clients plausibly long-polling, not zombies) | S7: idle --worked "
       "(idle_rounds=0) + attrition 4 CLEAN + loop pin=5 no-op + watchdog re-registered + precommit/prepush "
       "claws reinstalled + d19 advance read-back OK")

for path in (r"state-bm-c.json", r"fleet\machines\bm-c.json"):
    d = json.load(open(path, encoding="utf-8"))
    d["round_no"] = 923
    d["round_no_label"] = "r923"
    d["clock_read"] = now_iso
    d["ts"] = now_iso
    d["current_task"] = cur_task
    d["current_task_at"] = now_iso
    d["current_task_ts"] = now_iso
    d["heartbeat_epoch_utc"] = epoch
    d["last_seen"] = now_iso
    d["last_seen_at"] = now_iso
    d["verdict"] = verdict
    d["did"] = did
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["last_round"] = "r923"
    d["last_round_at"] = now_iso
    d["loop_round"] = 923
    d["orphan_faces"] = 3
    d["head_sha"] = "372706f0c"
    d["last_round_summary"] = "W220 full cycle landed (freeze+burn 12/12+sixgate+finalize 907,789/K=481,920+five-key ALL PASS)"
    json.dump(d, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    # verify epoch int + clock T-format laws (R170/R178/R262)
    v = json.load(open(path, encoding="utf-8"))
    assert isinstance(v["heartbeat_epoch_utc"], int), path
    assert "T" in v["clock_read"] and "+" in v["clock_read"], path
print("closeout write OK: state+heartbeat r923, epoch", epoch, "clock", now_iso)
