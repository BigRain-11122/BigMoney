# -*- coding: utf-8 -*-
# r1058 bm-c closeout writer: round_reports-bm-c.md row + state-bm-c.json + fleet/machines/bm-c.json
import io, json, time, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")  # 2026-10-17T0X:XX:XX+08:00 (T separator, UTC offset included)
epoch = int(time.time())
STATE = ROOT + r"\state-bm-c.json"
HB = ROOT + r"\fleet\machines\bm-c.json"
RR = ROOT + r"\round_reports-bm-c.md"

DID = ("r1058 (49th-gen absorb continuation): (1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=2 zero-kill; "
       "S0 fetch HEAD==origin 1c7112fd9 behind=0 (dead-window estate already landed+pushed: prereg freeze 5996e2c93 + "
       "five-face splice aa6102e35 + engine self-burn ledger appends 31c9e4872+1c7112fd9); dirty faces at open = daemon "
       "live-faces + dead-window S6 products + prior scratch -- targeted pathspec add per 提交纪律 (no bare add -A on a "
       "dirty-open tree); "
       "(2) S0.5 dual-delta FALSE both scans vs the CURRENT watermark (opening + S7 tail; unacked=0) + disclosed: the "
       "dead-window d19 advance (record ts 02:43:51, advance=true orders=true) consumed the SINGLE ORD delta row "
       "6ec75f9b->d89163fb = the 03:2x interactive-window GPU-lane receipt (POOL-0016 LivePortrait 表演栈收官 + "
       "POOL-0017 画质链半路试烧 done + V2《法务部》成片闸 PASS 盲评 9.66/10 -- BigStream MV lane receipts by the "
       "interactive window itself, zero loop action owed, lane-split honored per O-20261017-0131 sec.3); watermark "
       "honored read-back; record-ts 02:43:51 vs row-label 03:2x ordering oddity disclosed honest -- the content-sha "
       "equality probe-verified (dual FALSE scans) is the authoritative face; DEC 881b6dcb hold all scans; "
       "(3) S1 smoke 49/49; satengine ALIVE rc0; "
       "(4) ABSORB 49th: dead windows self-labeled r1058 executed the W256 chain body: S6 43-leg chain 03:06:18 rc0 "
       "(driver Tools/_r1058bmc_s6.py authored by dead window, log results/_r1058bmc_s6_log.txt) + W256 PREREG FREEZE "
       "5996e2c93 LANDED+pushed (machine-SUB from frozen W255 tpl f353e49f @ 72d292ea3; needle-probe preflight ALL "
       "floors pre-verified; 1 disclosed same-window gate-heal count-gate 4->5 b8 连续跳 face; banned_direction_gate "
       "ADMIT rc0 re-run at splice; staircase FIFTH A-hop A 578_501..580_500 / SIXTH above-own-A B 580_501..580_700; "
       "W255 finalize actuals mu -0.09270819/K 558,920/ledger 985,335 carried; freeze window r1058 2026-10-17 03:0x) + "
       "five-face freeze splice aa6102e35 LANDED+pushed (editor derive canon-clone "
       "_w255bmc_derive_editor.py->_w256bmc_derive_editor.py via age() machine-needle law + 3 disclosed needle heals; "
       "dual-sha16 receipt pf d4a9d7164ba9490e->ad9776287dd52280 / n1 c6dfb4291c09be1e->986e9162b86e0c7f) + engine "
       "mtime-watch self-burn 12/12 (ledger appends 31c9e4872+1c7112fd9 batched 6+6 self-commit) -- died pre-closeout "
       "(state counter 1058 frozen). This session machine-verified the estate BEFORE continuing (n1 TRIPLE identity "
       "worktree==receipt post==LANDED git blob 986e9162b86e0c7f @ aa6102e35 + pf ad9776287dd52280 git-diff-empty + "
       "shards 12/12 + prereg worktree==committed blob 4503bf5d @ 5996e2c93 placeholders intact) and completed the "
       "cycle THIS window; "
       "(5) P0 PRODUCT: W256 CYCLE COMPLETE -- sixgate PRE-FINALIZE ALL PASS (results/_r1058bmc_w256_sixgate.json, 18th "
       "consecutive correct phase; row_faces 5/5, family faces 1/1, W255 boundary 576301/578301 kept, banned rc0, "
       "pf+n1 selftest rc0, shards 12/12 sizes>100k, seed_admit FREE verbatim base=578501 span=2000 / base=580501 "
       "span=200) + finalize one-pass ledger 985,335+2,200=987,535 EXACT / merged pool K=558,920+2,200=561,120 EXACT "
       "(W256-only mu -0.090659/sigma 0.244814; merged mu -0.09270015/sigma 0.24503835; skill_line @n_eff held 985,335: "
       "1.1947->1.1947 K-lift 0.0000 in-band; voids LOWAMP-P1/P2; evidence_cutoff 2026-09-22) + fivekeys 6/6 ALL PASS "
       "(results/_r1058bmc_w256_fivekeys.json: key1 W256-only vs merged gap 0.0020412<0.02 tightened back from the W255 "
       "chain-max 0.007454 / key1b merged vs W255 key 0.000008 / key2 sigma rel -0.0000044% / key3 A p95 0.3107 delta "
       "-0.0315<0.05 negative back-swing after the W255 +0.0330 chain-max positive swing = two-sided oscillation chain "
       "6th proof / key4 K-lift 0.0000<=0.02 / key5 se_mu 0.000327<0.000328 NARROWING RESUMED after the W255 held-flat "
       "-- measurement-face honest note) + sec.7/8 backfill (results/_r1058bmc_w256_sec78_backfill.py; placeholders 0 "
       "after replace, prereg 40,964B->46,690B) + W257 SEAT PUBLISHED (probe results/_w257bmc_20261017_probe.py live "
       "re-derive on the post-W256-REGISTERED universe ADMIT: A 580_701..582_700 hops=1 SIXTH consecutive A-hop "
       "[naive 580_501..582_500 refused at the registered W256 B band 580_501..580_700] / B 582_701..582_900 hops=1 "
       "own-A reservation cascade SEVENTH consecutive above-own-A [naive 580_701..580_900 refused inside the own-A "
       "window]; seed_admit_gate rc0 FREE x2 base=580701 span=2000 / base=582701 span=200; origin vacancy four-check "
       "green; chain-relation anchors W255->W256 ledger 985,335->987,535 + K 558,920->561,120 both EXACT; owner rows "
       "246 -> W257=247th wave candidate = bm-c 77th own; seat MSG-20261017-03xx-bmc-w257-seat.md rides this closeout "
       "push per r565 law; W258+ projection: naive A 582_701..584_700 hops=0 pre-W257 BUT refused at the registered "
       "W257 B 582_701..582_900 post-registration = SEVENTH consecutive A-hop expected, live re-derive governs); "
       "(6) S6 43/43 rc0 absorbed-not-rerun per same-round law (dead-window chain 03:06:18, log 43x rc=0; bars cutoff "
       "10-16 current weekend honest, next trading day 10-19; faces on disk regenerated fresh 03:06); "
       "(7) S7: W256 seat MSG swept to processed + idle_trigger --worked (idle_rounds=0, agenda_starved=false) + "
       "attrition 4 CLEAN (healed notes as-is) + quad green (loop pin=5 no-op / watchdog S4U flip access-denied = "
       "adjudicated default-principal standing face D-20261002-02 / precommit claw + prepush claw installed "
       "LF-normalized)")

VERDICT = ("green: r1058 = 49th-gen absorb continuation -- W256 CYCLE COMPLETE (dead-window prereg 5996e2c93 + splice "
           "aa6102e35 + engine self-burn 12/12 absorbed; sixgate PRE-FINALIZE ALL PASS 18th consecutive + finalize "
           "one-pass 987,535/K=561,120 EXACT + fivekeys 6/6 + sec.7/8 backfilled) + W257 SEAT published (A "
           "580_701..582_700 SIXTH consecutive A-hop / B 582_701..582_900 SEVENTH consecutive above-own-A, live "
           "re-derive ADMIT, seed_admit FREE x2, origin vacancy held) + S6 43/43 absorbed + smoke 49/49 + attrition "
           "CLEAN + quad green")

VERIFY = ("sixgate ALL PASS (n1 TRIPLE identity 986e9162b86e0c7f worktree==receipt==LANDED @ aa6102e35 / pf "
          "ad9776287dd52280 git-diff-empty) + finalize ledger identity 985,335+2,200=987,535 EXACT / K "
          "558,920+2,200=561,120 EXACT + fivekeys 6/6 receipt + sec78 placeholders=0 (assert count==1 pre-replace) + "
          "W257 probe ADMIT receipt (hops=1/1, relations, seed_admit FREE x2, origin vacancy four-check) + smoke 49/49 + "
          "S6 log 43x rc=0 + s05 probe dual FALSE both scans (ord d89163fb current-hold / dec 881b6dcb hold) + idle_trigger worked "
          "rc0 + attrition 4 CLEAN + epoch int readback")

NEXT = ("r1059: (1) W257 prereg derive per seat-first law (FIRST ACTION on the post-W256-REGISTERED universe; seat "
        "bands A 580_701..582_700 / B 582_701..582_900 -- live re-derive governs r587, never transcribe; editor canon "
        "= _w256bmc_prereg_derive.py shift-map clone; prereg keys = W256 finalize actuals: merged mu -0.09270015 / "
        "sigma 0.24503835 / se_mu@K561,120 0.000327 / W256-only mu -0.090659 / A p95 0.3107 / K-lift 0.0000 / "
        "line_merged 1.1947; ledger prev 987,535 / prev K 561,120+2,200) -> freeze -> five-face splice -> engine "
        "self-burn 12/12 -> sixgate PRE-FINALIZE (19th consecutive target) -> finalize one-pass 987,535+2,200=989,735 / "
        "K=563,320 -> fivekeys vs W256 keys -> sec.7/8 backfill -> W258 seat publish (live re-derive; naive W258 A "
        "582_701..584_700 expected REFUSED by registered W257 B 582_701..582_900 = SEVENTH consecutive A-hop face per "
        "seat leg4); (2) V5 assembly-station watch (bm-a lane, DIRECTOR-REVIEW-V5-PASS gate); (3) GPU lane = "
        "interactive window per O-20261017-0131 sec.3 lane-split -- loop stays CPU-only, no double-open; "
        "(4) Monday 10-19 15:30 bars window: full papers chain fires on the new bar; ORD/DEC tail re-scan + backlog "
        "claimable face")

NOTE = ("r1058: 49th-gen absorb continuation (dead prereg+splice+burn windows estate verified) + W256 CYCLE COMPLETE "
        "(sixgate 18th + finalize 987,535/K=561,120 + fivekeys 6/6 + sec78) + W257 SEAT published + S6 43/43 absorbed "
        "+ smoke 49/49 + quad green")

ARTIFACT = ("results/perpetual_faces/n1_w256_results.json (ledger 987,535 / K=561,120) + "
            "research/PERPETUAL_N1_W256_PREREG.md (sec.7/8 backfilled, 46,690B) + "
            "results/_w257bmc_20261017_probe_receipt.json (W257 seat ADMIT) + results/_r1058bmc_w256_sixgate.json + "
            "results/_r1058bmc_w256_fivekeys.json")

MILESTONE = "W257 prereg derive -> freeze -> splice -> self-burn -> sixgate -> finalize 989,735/K=563,320 (r1059-r1061, 48h window)"

CURRENT = ("CPU=engine lane W257 seat published (prereg derive = r1059 first action) ; GPU=llm fill-gap mode 27b "
           "resident (C-03 dual-mode, free ~1.8GiB; GPU burns = interactive window lane per O-0131 sec.3; loop "
           "CPU-only)")

LANES = ("CPU=engine W257 seat published A 580_701..582_700 / B 582_701..582_900 (prereg derive = r1059 first "
         "action) ; GPU=interactive window per O-20261017-0131 sec.3 lane-split (loop CPU-only, no double-open)")

ROW = "%s | r1058 | bm-c | watermark verdict=绿 (red=false / satengine ALIVE / tickets 0 / engine-queue never-dry W257 seat published) | %s | r1058 | %s | 证据链: %s | 当前活: %s | 最近实物: %s | 下个里程碑: %s | 本地未达 origin commit 数=closeout push rides this window (fetch-verify at push) | 下轮指针: %s" % (ts, ts, DID, VERIFY, CURRENT, ARTIFACT, MILESTONE, NEXT)

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
    "last_round": "r1058", "last_round_label": "r1058", "round_no_label": "r1058",
    "last_round_summary": "r1058: 49th-gen absorb continuation + W256 CYCLE COMPLETE (987,535/K=561,120) + W257 SEAT published + S6 43/43 absorbed",
    "last_round_summary_at": ts,
    "last_action": "r1058 closeout (W256 cycle completion + W257 seat publish + MSG sweep + quad green)",
    "latest_artifact": ARTIFACT, "last_artifact": ARTIFACT, "recent_artifact": ARTIFACT,
    "next_milestone": MILESTONE,
    "prod_lanes": LANES,
    "orphan_face": 2, "orphan_faces": 2,
    "full_load_selfproof": {"占用一行": CURRENT},
    "free_ram_gb": 3.7, "idle_ram_gb": 3.7, "ram_free_gb": 3.7,
    "gpu_free_vram_mib": 1741, "gpu_free_vram_mb": 1800, "gpu_vram_free_mb": 1800, "free_vram_mb": 1800,
    "gpu_free_mib": 1741, "gpu_free_mb": 1800, "gpu_free_vram_gb": 1.7,
    "gpu_idle_vram_mb": 1800, "gpu_idle_vram_mib": 1741, "gpu_idle_mb": 1800, "gpu_idle_mib": 1741,
    "gpu_mem_used_mib": 14643, "gpu_used_vram_mib": 14643, "gpu_util_pct": 1, "gpu_mem_total_mib": 16384, "gpu_total_vram_mib": 16384,
    "cpu_pct": 5.0, "cpu_util_pct": "5", "cpu_idle_pct": 95.0,
    "head_sha": "W256 cycle complete + W257 seat (this window's closeout commit rides this window)",
    "r1058_absorb_note": ("r1058 absorb note: dead windows self-labeled r1058 (fired 03:0x-03:4x after the r1057 "
                          "closeout 02:42) executed the W256 chain body: S6 43-leg chain 03:06:18 rc0 + W256 PREREG "
                          "FREEZE 5996e2c93 committed+pushed (machine-SUB from frozen W255 tpl f353e49f @ 72d292ea3; "
                          "needle-probe preflight; 1 disclosed gate-heal count-gate 4->5; banned ADMIT rc0 re-run; "
                          "bands A 578_501..580_500 FIFTH consecutive A-hop / B 580_501..580_700 SIXTH consecutive "
                          "above-own-A; freeze window stamp 2026-10-17 03:0x) + five-face freeze splice aa6102e35 "
                          "committed+pushed (editor derive canon-clone via age() machine-needle law + 3 disclosed "
                          "needle heals caught PRE-splice by count-asserted gates; dual-sha16 receipt pf "
                          "d4a9d7164ba9490e->ad9776287dd52280 / n1 c6dfb4291c09be1e->986e9162b86e0c7f; engine "
                          "mtime-watch self-burn IN FLIGHT at commit time -- burn-ahead-of-commit face disclosed "
                          "honest, engine reads worktree bytes == commit bytes) + engine self-burn 12/12 (ledger "
                          "appends 31c9e4872+1c7112fd9 batched 6+6 self-commit) -- died pre-closeout (state counter "
                          "1058 frozen). This session (per bm-c absorb precedent lineage r894..r1057, 49th instance) "
                          "machine-verified the estate BEFORE continuing (n1 TRIPLE identity 986e9162b86e0c7f "
                          "worktree==receipt post==LANDED git blob @ aa6102e35 + pf ad9776287dd52280 git-diff-empty + "
                          "shards 12/12 + prereg worktree==committed blob 4503bf5d @ 5996e2c93 with sec.7/8 "
                          "placeholders intact) and completed the cycle THIS window: sixgate PRE-FINALIZE ALL PASS "
                          "(18th consecutive) + finalize one-pass 987,535/K=561,120 EXACT + fivekeys 6/6 + sec.7/8 "
                          "backfill + W257 seat publish; zero double-count: the dead windows consumed no ORD/DEC rows "
                          "(no watermark writes), S6 chain absorbed same-cycle (03:06:18 log, bars cutoff 10-16 "
                          "current, faces regenerated fresh)"),
    "r1058_closeout_note": ("r1058: 49th-gen absorb continuation (dead prereg 5996e2c93 + splice aa6102e35 + burn "
                            "12/12 estate verified) + W256 CYCLE COMPLETE (sixgate 18th consecutive PRE-FINALIZE + "
                            "finalize one-pass 987,535/K=561,120 EXACT + fivekeys 6/6 [key1 gap 0.0020412 "
                            "tightened-back / key3 p95 -0.0315 negative back-swing / key5 se_mu 0.000327 "
                            "narrowing-resumed, all in-band disclosed] + sec.7/8 backfill placeholders=0) + W257 SEAT "
                            "published (A 580_701..582_700 SIXTH A-hop / B 582_701..582_900 SEVENTH above-own-A, live "
                            "re-derive ADMIT) + W256 seat MSG swept processed + S6 43/43 absorbed + smoke 49/49 + "
                            "attrition 4 CLEAN + quad green (watchdog S4U flip = adjudicated default-principal face); "
                            "counter 1058->1059"),
}

st = update(STATE, dict(common, round_no=1059), [])
update(HB, dict(common, round_no=1058), [])

rr_tail = io.open(RR, encoding="utf-8").read()[-400:]
if "| r1058 |" in rr_tail:
    print("RR row already appended this window (idempotent skip)")
else:
    with io.open(RR, "a", encoding="utf-8", newline="\n") as f:
        f.write(ROW + "\n")
    print("RR appended: %d chars" % len(ROW))

# self-assertions
chk = json.load(io.open(STATE, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert chk["round_no"] == 1059
assert "T" in chk["clock_read"] and "+08:00" in chk["clock_read"]
assert chk["last_decisions_sha"] == "881b6dcb2c2c8f7e23a7a85af00b4ac8d233cd4e0b776315a0ec9491d5126e05"
assert chk["last_orders_sha"] == "d89163fb0a141ad568ddba7662c80abdb92db877"
print("STATE OK round_no=1059 epoch=%d ord_wm=%s" % (chk["heartbeat_epoch_utc"], chk["last_orders_sha"][:8]))
hb = json.load(io.open(HB, encoding="utf-8"))
assert isinstance(hb["heartbeat_epoch_utc"], int)
print("HB OK epoch=%d round_no=%d" % (hb["heartbeat_epoch_utc"], hb["round_no"]))
print("RR appended: %d chars" % len(ROW))
