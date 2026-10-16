# -*- coding: utf-8 -*-
# r1057 bm-c closeout writer: round_reports-bm-c.md row + state-bm-c.json + fleet/machines/bm-c.json
import io, json, time, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")  # 2026-10-17T0X:XX:XX+08:00 (T separator, UTC offset included)
epoch = int(time.time())
STATE = ROOT + r"\state-bm-c.json"
HB = ROOT + r"\fleet\machines\bm-c.json"
RR = ROOT + r"\round_reports-bm-c.md"

DID = ("r1057 (48th-gen absorb continuation): (1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=1 zero-kill; "
       "S0 fetch HEAD==origin f931cf102 behind=0 (dead-window splice e166afc6c + engine self-burn ledger appends "
       "b1414b81a+f931cf102 already landed by the dead window); 62 dirty faces at open = daemon live-faces + dead-window "
       "uncommitted estate + prior scratch -- targeted pathspec add per 提交纪律 (no bare add -A on a dirty-open tree); "
       "(2) S0.5 ORD delta TRUE consumed: 1 new row (02:1x @bm-a xq-T1 对审签章 receipt -- BigStream MV lane via bm-a r1026, "
       "26 帧位签章 + 7 帧位回炉 T1-1R + A 批 KF=GO; POOL-0013 card drift note = dispatcher 写手席 lane; zero bm-c loop "
       "action) / DEC delta FALSE hold 881b6dcb; watermark advanced d19 update --advance read-back-verified "
       "ord=02bd38be->6ec75f9b; unacked=0; "
       "(3) S1 smoke 49/49; satengine ALIVE (burns_active=[] queue_next=[] -- W255 cycle closed THIS window, W256 seat "
       "published, prereg derive = r1058 first action); "
       "(4) ABSORB 48th: dead r1057 window (self-labeled, fired ~02:0x after r1056 closeout 01:47) landed the W255 five-face "
       "freeze splice e166afc6c (editor derive canon-clone _w254bmc_derive_editor.py->_w255bmc_derive_editor.py + freeze_edits "
       "+ splice; 2 disclosed needle heals + 2 blanket-duplication sub heals caught PRE-splice per commit msg; dual-sha16 "
       "receipt pf 924e87b3f02afb72->d4a9d7164ba9490e / n1 7b550e65716e0ada->c6dfb4291c09be1e; bands A 576_301..578_300 "
       "FOURTH consecutive A-hop / B 578_301..578_500 FIFTH consecutive above-own-A) and pushed, after which the resident "
       "engine mtime-watch self-burned 12/12 (ledger appends b1414b81a+f931cf102 batched 6+6 self-commit), then died "
       "pre-closeout (state frozen round_no=1057) -- this session machine-verified the estate BEFORE continuing "
       "(sixgate gate-1 TRIPLE identity n1 worktree==receipt post==LANDED git blob c6dfb4291c09be1e @ e166afc6c + pf face "
       "d4a9d7164ba9490e git-diff-empty + shards 12/12 on origin) and completed the cycle THIS window; "
       "(5) P0 PRODUCT: W255 CYCLE COMPLETE -- sixgate PRE-FINALIZE ALL PASS (results/_r1057bmc_w255_sixgate.json, "
       "17th consecutive correct phase; row_faces 5/5, family faces 1/1, W254 boundary 574101/576101 kept, banned rc0, "
       "pf+n1 selftest rc0, shards 12/12 sizes>100k, seed_admit FREE verbatim base=576301 span=2000 / base=578301 span=200) + "
       "finalize one-pass ledger 983,135+2,200=985,335 EXACT / merged pool K=556,720+2,200=558,920 EXACT "
       "(W255-only mu -0.08525445/sigma 0.247112; merged mu -0.09270819/sigma 0.245039; skill_line @n_eff held 983,135: "
       "1.1945->1.1946 K-lift +0.0001 in-band; voids LOWAMP-P1/P2; evidence_cutoff 2026-09-22) + fivekeys 6/6 ALL PASS "
       "(results/_r1057bmc_w255_fivekeys.json: key1 W255-only vs merged gap 0.007454<0.02 CHAIN-MAX disclosed honestly / "
       "key1b merged vs W254 key 0.0000295 / key2 sigma rel +0.0000345% / key3 A p95 0.3422 delta +0.0330<0.05 chain-max "
       "positive swing disclosed / key4 K-lift +0.0001<=0.02 / key5 se_mu 0.000328<=0.000328 HELD-FLAT -- first non-narrowing "
       "in the W250..W254 chain, measurement-face honest note) + sec.7/8 backfill (results/_r1057bmc_w255_sec78_backfill.py; "
       "placeholders 0 after replace, prereg 40,964B->45,795B) + W256 SEAT PUBLISHED (probe results/_w256bmc_20261017_probe.py "
       "live re-derive on the post-W255-REGISTERED universe ADMIT: A 578_501..580_500 hops=1 FIFTH consecutive A-hop "
       "[naive 578_301..580_300 refused at the registered W255 B band 578_301..578_500] / B 580_501..580_700 hops=1 own-A "
       "reservation cascade SIXTH consecutive above-own-A [naive 578_501..578_700 refused inside the own-A window]; "
       "seed_admit_gate rc0 FREE x2 base=578501 span=2000 / base=580501 span=200; origin vacancy four-check green "
       "no seat/row/configs/prereg; chain-relation anchors W254->W255 ledger 983,135->985,335 + K 556,720->558,920 both "
       "EXACT; owner rows 245 -> W256=246th wave candidate = bm-c 76th own; seat MSG-20261017-023x-bmc-w256-seat.md rides "
       "this closeout push per r565 law; W257+ projection: naive A 580_501..582_500 hops=0 pre-W256 BUT refused at the "
       "registered W256 B 580_501..580_700 post-registration = SIXTH consecutive A-hop expected, live re-derive governs); "
       "(6) S6 43/43 rc0 (driver Tools/_r1057bmc_s6.py canon clone of r1056, log results/_r1057bmc_s6_log.txt): dualrun "
       "ZERO-DRIFT streak 16 (461 entries) + compute_audit FLAG pool_starvation/supply_floor structural answered-by-chain "
       "(W-wave chain = standing supply lane, engine queue never-dry via the W256 seat; ready 0<floor 3 = pool lane face, "
       "not the engine lane) + py_watermark insufficient_history weekend honest (bars_present=false, cutoff 10-16 current, "
       "next trading day 10-19) + update_daily 0 rows weekend no-op + collectors lane no-ops honest (bm-a/bm-b lanes R31) + "
       "fund_premium snapshot rc0 (bm-c lane) + papers no-op (no new bar Saturday) + daily_report/ceo_live_usage 10-17 faces "
       "fresh + token delta 0; "
       "(7) S7: idle_trigger --worked (idle_rounds=0, agenda_starved=false) + attrition 4 CLEAN (healed notes as-is) + "
       "d19 advance read-back + quad green (loop pin=5 no-op / watchdog S4U flip access-denied = adjudicated default-principal "
       "standing face D-20261002-02 / precommit claw + prepush claw installed LF-normalized) + stray zero-byte 'bm-c' root "
       "file (10-16 22:08 redirect artifact) left untracked non-swept; "
       "zero double-count: ORD row consumed THIS window with watermark advanced by this session; dead-window debts were "
       "handled by its own splice+burn commits")

VERDICT = ("green: r1057 = 48th-gen absorb continuation -- W255 CYCLE COMPLETE (dead-window splice e166afc6c + engine "
           "self-burn 12/12 absorbed; sixgate PRE-FINALIZE ALL PASS 17th consecutive + finalize one-pass 985,335/K=558,920 "
           "EXACT + fivekeys 6/6 + sec.7/8 backfilled) + W256 SEAT published (A 578_501..580_500 FIFTH consecutive A-hop / "
           "B 580_501..580_700 SIXTH consecutive above-own-A, live re-derive ADMIT, seed_admit FREE x2, origin vacancy held) + "
           "ORD 1-row consumed (watermark 6ec75f9b) + S6 43/43 rc0 weekend honest + smoke 49/49 + attrition CLEAN + quad green")

VERIFY = ("sixgate ALL PASS (n1 TRIPLE identity c6dfb4291c09be1e worktree==receipt==LANDED @ e166afc6c / pf "
          "d4a9d7164ba9490e git-diff-empty) + finalize ledger identity 983,135+2,200=985,335 EXACT / K "
          "556,720+2,200=558,920 EXACT + fivekeys 6/6 receipt + sec78 placeholders=0 (assert count==1 pre-replace) + "
          "W256 probe ADMIT receipt (hops=1/1, relations, seed_admit FREE x2, origin vacancy four-check) + smoke 49/49 + "
          "S6 log 43x rc=0 + d19 advance read-back equality (dec=881b6dcb ord=6ec75f9b) + idle_trigger worked rc0 + "
          "attrition 4 CLEAN + epoch int readback")

NEXT = ("r1058: (1) W256 prereg derive per seat-first law (FIRST ACTION on the post-W255-REGISTERED universe; seat bands "
        "A 578_501..580_500 / B 580_501..580_700 -- live re-derive governs r587, never transcribe; editor canon = "
        "_w255bmc_prereg_derive.py shift-map clone; prereg keys = W255 finalize actuals: merged mu -0.09270819 / sigma "
        "0.24503942 / se_mu@K558,920 0.000328 / W255-only mu -0.08525445 / A p95 0.3422 / K-lift +0.0001 / line_merged "
        "1.1946; ledger prev 985,335 / prev K 556,720+2,200) -> freeze -> five-face splice -> engine self-burn 12/12 -> "
        "sixgate PRE-FINALIZE (18th consecutive target) -> finalize one-pass 985,335+2,200=987,535 / K=561,120 -> fivekeys "
        "vs W255 keys -> sec.7/8 backfill -> W257 seat publish (live re-derive; naive W257 A 580_501..582_500 expected "
        "REFUSED by registered W256 B 580_501..580_700 = SIXTH consecutive A-hop face per seat leg4); "
        "(2) V5 assembly-station watch (bm-a lane, DIRECTOR-REVIEW-V5-PASS gate); (3) GPU lane = interactive window owns "
        "POOL-0016/0017 per O-20261017-0131 sec.3 lane-split -- loop stays CPU-only, no double-open; "
        "(4) Monday 10-19 15:30 bars window: full papers chain fires on the new bar; ORD/DEC tail re-scan + backlog "
        "claimable face")

NOTE = ("r1057: 48th-gen absorb continuation (dead splice window estate verified) + W255 CYCLE COMPLETE (sixgate 17th + "
        "finalize 985,335/K=558,920 + fivekeys 6/6 + sec78) + W256 SEAT published + ORD 1-row consumed + S6 43/43 + "
        "smoke 49/49 + quad green")

ARTIFACT = ("results/perpetual_faces/n1_w255_results.json (ledger 985,335 / K=558,920) + research/PERPETUAL_N1_W255_PREREG.md "
            "(sec.7/8 backfilled, 45,795B) + results/_w256bmc_20261017_probe_receipt.json (W256 seat ADMIT) + "
            "results/_r1057bmc_s6_log.txt (43 legs rc0)")

MILESTONE = "W256 prereg derive -> freeze -> splice -> self-burn -> sixgate -> finalize 987,535/K=561,120 (r1058-r1060, 48h window)"

CURRENT = ("CPU=engine lane W256 seat published (prereg derive = r1058 first action) ; GPU=llm fill-gap mode 27b resident "
           "(C-03 dual-mode, free ~1.7GiB; GPU burns = interactive window lane per O-0131 sec.3; loop CPU-only)")

LANES = ("CPU=engine W256 seat published A 578_501..580_500 / B 580_501..580_700 (prereg derive = r1058 first action) ; "
         "GPU=interactive window owns POOL-0016/0017 per O-20261017-0131 sec.3 lane-split (loop CPU-only, no double-open)")

ROW = "%s | r1057 | bm-c | watermark verdict=绿 (red=false / satengine ALIVE queue idle / tickets 0 / engine-queue never-dry W256 seat published) | %s | r1057 | %s | 证据链: %s | 当前活: %s | 最近实物: %s | 下个里程碑: %s | 本地未达 origin commit 数=closeout push rides this window (fetch-verify at push) | 下轮指针: %s" % (ts, ts, DID, VERIFY, CURRENT, ARTIFACT, MILESTONE, NEXT)

def update(path, updates, ack_orders):
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    for k, v in updates.items():
        d[k] = v
    ack = d.get("orders_ack") or []
    for o in ack_orders:
        if o not in ack:
            ack.append(o)
    d["orders_ack"] = ack
    d["orders_ack_count"] = len(ack)
    if ack_orders:
        d["orders_ack_last"] = ack_orders[-1]
    d["orders_ack_ts"] = ts
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    return d

common = {
    "machine_id": "bm-c",
    "clock_read": ts, "ts": ts, "updated": ts, "updated_at": ts,
    "last_seen": ts, "last_seen_at": ts, "last_round_at": ts, "last_round_closed": ts,
    "now_active": ts, "activity_now": ts, "current_task_ts": epoch,
    "heartbeat_epoch_utc": epoch,
    "idle_rounds": 0, "agenda_starved": False,
    "did": DID, "note": NOTE, "verdict": VERDICT, "verify": VERIFY,
    "next": NEXT, "next_pointer": NEXT,
    "last_round": "r1057", "last_round_label": "r1057", "round_no_label": "r1057",
    "last_round_summary": "r1057: 48th-gen absorb continuation + W255 CYCLE COMPLETE (985,335/K=558,920) + W256 SEAT published + ORD 1-row consumed + S6 43/43",
    "last_round_summary_at": ts,
    "last_action": "r1057 closeout (W255 cycle completion + W256 seat publish + ORD consume + S6 + watermark advance)",
    "latest_artifact": ARTIFACT, "last_artifact": ARTIFACT, "recent_artifact": ARTIFACT,
    "next_milestone": MILESTONE,
    "prod_lanes": LANES,
    "orphan_face": 1, "orphan_faces": 1,
    "full_load_selfproof": {"占用一行": CURRENT},
    "free_ram_gb": 2.6, "idle_ram_gb": 2.6, "ram_free_gb": 2.6,
    "gpu_free_vram_mib": 1716, "gpu_free_vram_mb": 1800, "gpu_vram_free_mb": 1800, "free_vram_mb": 1800,
    "gpu_free_mib": 1716, "gpu_free_mb": 1800, "gpu_free_vram_gb": 1.68,
    "gpu_idle_vram_mb": 1800, "gpu_idle_vram_mib": 1716, "gpu_idle_mb": 1800, "gpu_idle_mib": 1716,
    "gpu_mem_used_mib": 14668, "gpu_used_vram_mib": 14668, "gpu_util_pct": 1, "gpu_mem_total_mib": 16384, "gpu_total_vram_mib": 16384,
    "cpu_pct": 5.0, "cpu_util_pct": "5", "cpu_idle_pct": 95.0,
    "head_sha": "W255 cycle complete + W256 seat (this window's closeout commit rides this window)",
    "r1057_absorb_note": ("r1057 absorb note: dead window (self-labeled r1057, fired ~02:0x after the r1056 closeout 01:47) "
                          "executed the W255 five-face freeze splice chain: editor derive (canon-clone "
                          "_w254bmc_derive_editor.py->_w255bmc_derive_editor.py per age() machine-needle law + 2 disclosed "
                          "needle heals + 2 blanket-duplication sub heals) + freeze_edits + splice landed commit e166afc6c "
                          "AND pushed, with dual-sha16 receipt pf 924e87b3f02afb72->d4a9d7164ba9490e / n1 "
                          "7b550e65716e0ada->c6dfb4291c09be1e and bands A 576_301..578_300 (FOURTH consecutive A-hop) / "
                          "B 578_301..578_500 (FIFTH consecutive above-own-A); the resident engine then mtime-watch "
                          "self-burned 12/12 (batched ledger appends b1414b81a + f931cf102 self-committed). The window died "
                          "pre-closeout (state frozen round_no=1057). This session (per bm-c absorb precedent lineage "
                          "r894..r1056, 48th instance) machine-verified the estate BEFORE continuing (sixgate triple-identity "
                          "+ shard presence on origin + pf git-diff-empty) and completed the cycle THIS window: sixgate "
                          "PRE-FINALIZE ALL PASS (17th consecutive) + finalize one-pass 985,335/K=558,920 EXACT + fivekeys "
                          "6/6 + sec.7/8 backfill + W256 seat publish; zero double-count: the dead window consumed no ORD/DEC "
                          "rows (no watermark writes), the single 02:1x ORD row was consumed THIS window"),
    "r1057_closeout_note": ("r1057: 48th-gen absorb continuation (dead splice window estate verified) + W255 CYCLE COMPLETE "
                            "(sixgate 17th consecutive PRE-FINALIZE + finalize one-pass 985,335/K=558,920 EXACT + fivekeys "
                            "6/6 [key1 gap 0.007454 chain-max + key3 p95 swing +0.0330 chain-max + key5 se_mu held-flat, all "
                            "in-band disclosed] + sec.7/8 backfill placeholders=0) + W256 SEAT published (A 578_501..580_500 "
                            "FIFTH A-hop / B 580_501..580_700 SIXTH above-own-A, live re-derive ADMIT) + ORD 1-row consumed "
                            "(watermark 6ec75f9b advanced read-back) + S6 43/43 rc0 weekend honest + smoke 49/49 + "
                            "attrition 4 CLEAN + quad green (watchdog S4U flip = adjudicated default-principal face); "
                            "counter 1057->1058"),
}

st = update(STATE, dict(common, round_no=1058), [])
update(HB, dict(common, round_no=1057), [])

with io.open(RR, "a", encoding="utf-8", newline="\n") as f:
    f.write(ROW + "\n")

# self-assertions
chk = json.load(io.open(STATE, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert chk["round_no"] == 1058
assert "T" in chk["clock_read"] and "+08:00" in chk["clock_read"]
assert chk["last_decisions_sha"] == "881b6dcb2c2c8f7e23a7a85af00b4ac8d233cd4e0b776315a0ec9491d5126e05"
assert chk["last_orders_sha"] == "6ec75f9b338874aad1fbd8e57a26e55e38a70d37"
print("STATE OK round_no=1058 epoch=%d ord_wm=%s" % (chk["heartbeat_epoch_utc"], chk["last_orders_sha"][:8]))
hb = json.load(io.open(HB, encoding="utf-8"))
assert isinstance(hb["heartbeat_epoch_utc"], int)
print("HB OK epoch=%d round_no=%d" % (hb["heartbeat_epoch_utc"], hb["round_no"]))
print("RR appended: %d chars" % len(ROW))
