# -*- coding: utf-8 -*-
# r1035 bm-c closeout: state advance 1035->1036 + round-report row + heartbeat write
import io, json, time

NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

ABS = ("r1035 absorb note: TWO dead sessions absorbed (35th gen). S-0 (20:05 firing): jayredo harvest repair "
       "authored+run 20:05:35 (SaveVideo mp4 lands under outputs['15']['images'] animated flag; runner checked only "
       "gifs/videos = 11 clips burned ok but marked ok:False) -> 11/11 harvested to bmc/i2v/jayredo + delivered "
       "origin b845cc7 (+board/verdict rows 1d32046) + runner harvest line patched defense-in-depth. "
       "S-A (20:25 firing): s05 probe 20:28:48 dual-delta FALSE + t1 lintscan + SHOTLIST S3-20 VAGUE remnant fix "
       "(origin 8fdc832, lint 0/33) + xingqing T1 wave-1 ignition 20:45:29 pid 92704 (39+/264 @21:03 all ok, ETA ~23:1x) "
       "+ S6 43-leg chain 20:49-20:59:16 rc=0 DONE. Both died pre-commit with zero own commits; this window "
       "machine-verified estate BEFORE landing (S6 log 43x rc=0 + ffprobe 5 small clips VALID h264 1344x768 5.17s = "
       "500KB harvest threshold false-negative, healed in progress json 11/11 ok + delivery commit b845cc7 byte-equal "
       "11/11).")
DID = ("r1035 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=8 orphans=1 zero-kill; (2) ABSORB 35th gen two "
       "dead sessions (see absorb note) landed; (3) S6 absorbed: bars 10-15 LANDED (update_daily +36 rows cutoff "
       "10-15, 7th sina-lag window resolved) + LHB +66 cutoff 10-15 + live.paper enforce rc0 + t35_openfill PASS "
       "2026-10-15 zero-pending + t24 22/22 + papers chain rc0 + daily_scorecard + daily_report + ceo_live_usage "
       "(ORANGE cap 50%) + build_status stale-takeover (bm-a hb stale 292min) + token delta=0; (4) S0.5 ORD "
       "dfc48f1c->d24c2750 advanced rows judged zero bm-c action (3 own-receipts executed by dead sessions + BigStream "
       "patrol dispatch non-our-lane + CEO bm-a stop order O-20261015-1845 clause-5 bm-c out of scope + 1 steward "
       "ts-format edit), DEC ab3f0cc9 hold, unacked=0 both scans; (5) S1 smoke 49/49; (6) P0 PRODUCT = W248 prereg "
       "derive LANDED (authored 20:00:36 r1034-continuation, this window verified + banned_direction_gate rc0 + "
       "committed+pushed; splice = r1036 FIRST ACTION); (7) jayredo 11/11 delivered origin b845cc7 + poke rerouted "
       "to group orders receipts (waking bm-a = O-1845 verbal-gate violation; assembly waits CEO kaigong); (8) W20 "
       "SCREEN shard-0 RUNNING pid 32676 (autofill self-serve face works), shards 1-3 RAM-gate park-honest ~2GB<4GB; "
       "(9) watermark red=pool-batch-runnable-idle-low-cpu answered (RAM gate + MV priority + W248 next); "
       "(10) S7 quad green + attrition 4 CLEAN (1 healed note); counter 1035->1036")
VER = ("green: r1035 = ABSORB 35th (jayredo 11/11 delivered + xq T1 burning 39+/264 + S6 43/43 rc0 bars-10-15 landed) "
       "+ W248 prereg LANDED (banned gate rc0) + ORD d24c2750 advanced zero-action + smoke 49/49 + S7 quad green + "
       "shard-0 self-serve ignition (W20 autofill works)")
NXT = ("r1036: (1) W248 five-face freeze splice = FIRST ACTION (template _w247bma_freeze_edits.py; gate0.5: W247 row + "
       "finalize present; post-W247-universe re-derive per prereg; splice -> engine mtime-watch self-burn 12/12 (RAM "
       "~2G precedents W239 1.0G OK) -> six-gate PRE-FINALIZE -> finalize); (2) xq T1 wave-1 harvest watch ~23:1x "
       "(264 board + tier-1 multimodal sea-review 24/board -> tier-2 expert pick 2/frame); (3) jayredo 6 reshake slots "
       "= bm-a director review (verbal-gate; bm-c zero action); (4) W20 shard-0 runner watch + shards 1-3 RAM recheck; "
       "(5) bars next window 10-16 15:30 (10-15 papers debt=0); (6) ORD/DEC tail re-scan")

# ---- state-bm-c.json ----
sp = ROOT + r"\state-bm-c.json"
st = json.load(io.open(sp, encoding="utf-8"))
st.update({
    "round_no": 1036, "last_round": "r1035", "last_round_label": "r1035",
    "last_round_at": NOW, "last_seen": NOW, "last_seen_at": NOW, "ts": NOW,
    "updated": NOW, "updated_at": NOW, "now_active": NOW, "activity_now": NOW,
    "clock_read": NOW, "heartbeat_epoch_utc": EPOCH,
    "current_task": "r1035 closeout (absorb 35th + W248 prereg landed + estate commit)",
    "current_task_at": NOW, "did": DID, "verdict": VER,
    "next": NXT, "next_pointer": NXT,
    "note": "r1035: absorb 35th (jayredo 11/11 origin-delivered + xq T1 burning + S6 43/43 bars-10-15) | W248 prereg LANDED splice=r1036 | ORD d24c2750 zero-action | shard-0 self-serve running",
    "last_round_summary": "r1035: absorb 35th two dead sessions + W248 prereg landed + S6 43/43 rc0 (bars 10-15) + smoke 49/49 + S7 quad green",
    "latest_artifact": "r1035: research/PERPETUAL_N1_W248_PREREG.md (banned gate rc0) + S6 43/43 rc0 log + jayredo 11/11 delivered origin b845cc7",
    "last_artifact": "r1035: research/PERPETUAL_N1_W248_PREREG.md (banned gate rc0) + S6 43/43 rc0 log + jayredo 11/11 delivered origin b845cc7",
    "recent_artifact": "r1035: research/PERPETUAL_N1_W248_PREREG.md (banned gate rc0) + S6 43/43 rc0 log + jayredo 11/11 delivered origin b845cc7",
    "next_milestone": "r1036+: W248 splice+burn+finalize chain + xq T1 264-board sea-review (~23:1x) + jayredo 6 reshake director review (bm-a verbal-gate)",
    "orphan_face": 1, "orphan_faces": 1, "codely_live_count": 1,
    "r1035_absorb_note": ABS,
    "r1035_closeout_note": ("r1035: absorb 35th gen two dead sessions estate landed (S-0 jayredo harvest/delivery + S-A "
                            "xq-T1 ignition + SHOTLIST fix + S6 chain) + W248 prereg landed + bars 10-15 7th window resolved "
                            "papers full chain rc0 + ORD advanced d24c2750 zero-action + S7 quad green | " + NOW),
    "prod_lanes": ("CPU=W20 SCREEN shard-0 RUNNING pid 32676 (autofill self-serve) + shards 1-3 RAM-gate park-honest (~2GB<4GB) ; "
                   "GPU=MV xingqing T1 wave-1 BURNING pid 92704 (39+/264 @21:03 all ok, Krea2 672x384 8seed/frame, ETA ~23:1x, "
                   "self-poke bm-a on done) + ComfyUI resident + jayredo 11/11 delivered (b845cc7) 6 reshake slots await bm-a director "
                   "(verbal-gate) ; N1=W248 prereg LANDED this window -> splice=r1036 first action -> engine self-burn -> finalize ; "
                   "U256 w001/w003 RAM gate deferred ; SPAWN-GATE=codely cap2 live (C-20261015-03)"),
    "full_load_selfproof": {
        "占用一行": ("CPU=W20 shard-0 running pid 32676 + shards 1-3 RAM-gated ; GPU=xq T1 wave-1 burning pid 92704 39+/264 ; "
                    "N1=W248 prereg landed, splice r1036 ; jayredo 11/11 delivered origin"),
        "当前活": "r1035 closeout (absorb 35th + W248 prereg landed + estate commit)",
        "最近实物": "research/PERPETUAL_N1_W248_PREREG.md (banned gate rc0·20:0x derive·本窗 landed) + bars 10-15 S6 全链 rc0 + jayredo 11 i2v origin b845cc7",
        "下个交付物": "W248 splice+burn+finalize 链（r1036 起）+ xq T1 264 帧海选板 sea-review（~23:1x）+ jayredo 6 重摇槽导演复检（候 bm-a 开工口令）",
        "队列水位": "池 ready=W20 screen shard-0 running/1-3 RAM 门 park-honest·N1 W248 splice queued·P2/P3 空·jobs 0·U256 候 RAM 门",
    },
    "idle_rounds": 0, "agenda_starved": False,
})
json.dump(st, io.open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state ok round_no=", st["round_no"])

# ---- round_reports-bm-c.md (canonical root path, r750 law) ----
rp = ROOT + r"\round_reports-bm-c.md"
row = ("%s | r1035 | bm-c | absorb 35th gen (S-0: jayredo SaveVideo-images-key harvest repair 11/11 + delivery origin "
       "b845cc7/1d32046; S-A: xq T1 wave-1 ignition pid 92704 39+/264 + SHOTLIST S3-20 fix 8fdc832 + S6 43/43 rc0 bars-10-15 "
       "landed papers-chain-rc0) + P0 product W248 prereg LANDED (banned gate rc0) + ORD dfc48f1c->d24c2750 rows judged "
       "zero-action + DEC hold + smoke 49/49 + shard-0 self-serve ignition + S7 quad green + attrition 4 CLEAN | "
       "evidence: results/_r1035bmc_s6_log.txt 43x rc=0 + _r1035bmc_orddiff.txt + ffprobe 5 clips h264 1344x768 5.17s + "
       "b845cc7 byte-equal 11/11 + banned gate rc0 + d19 read-back equality | next: W248 splice FIRST ACTION r1036 + xq T1 "
       "harvest ~23:1x + ORD/DEC tail rescan | 本地未达 origin commit 数=见 sync 字段 | 孤儿面=1\n" % NOW)
with io.open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(row)
print("report row ok")

# ---- heartbeat fleet/machines/bm-c.json ----
hp = ROOT + r"\fleet\machines\bm-c.json"
h = json.load(io.open(hp, encoding="utf-8"))
h.update({
    "last_seen": NOW, "ts": NOW, "clock_read": NOW, "heartbeat_epoch_utc": EPOCH,
    "current_task": "r1035 closeout (absorb 35th + W248 prereg landed)",
    "verdict": VER, "did": DID, "next": NXT,
    "idle_rounds": 0, "agenda_starved": False, "codely_live_count": 1,
    "prod_lanes": st["prod_lanes"], "full_load_selfproof": st["full_load_selfproof"],
})
json.dump(h, io.open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print("heartbeat ok epoch-int verified")
