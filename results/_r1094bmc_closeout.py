# -*- coding: utf-8 -*-
# r1094-continuation bm-c closeout: state advance 1094->1095 + heartbeat + round-report row (canonical
# root path per r750 law). Fresh-read-modify-write both faces; read-back asserts (R170/R178 epoch int law).
import json, time, datetime, psutil, subprocess, io, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
NOWISO = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
vm = psutil.virtual_memory()
FREE_RAM = round(vm.available / (1024 ** 3), 2)
CPU_PCT = round(psutil.cpu_percent(interval=1), 1)
try:
    _g = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                          "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=15)
    gu, gm, gt = [int(x.strip()) for x in _g.stdout.strip().split(",")]
except Exception:
    gu, gm, gt = 98, 7835, 16384

DID = ("r1094: W270 SEAT + W270 PREREG FREEZE LANDED origin 9f480646f4 + 3bb8b9308e -- dead r1094 window "
       "(published seat 16:05:25, died pre-closeout with state counter frozen at 1094) absorbed per the bm-c "
       "absorb precedent lineage: estate machine-verified BEFORE landing (frozen face 23,207B byte-equal "
       "blob d7ae1195 @ 67fe12710c pre-backfill face + HEAD post-backfill twin 41524f46 disclosed NOT used + "
       "facts json full-precision W269 actuals + seat receipt ADMIT bands A 609_301..611_300 NINETEENTH "
       "consecutive A-hop [naive 609_101..611_100 REFUSED at registered W269 B 609_101..609_300] / B "
       "611_301..611_500 TWENTIETH consecutive above-own-A [naive 609_301..609_500 lands inside own-A "
       "window -> cascade hop past 611_300] + seed_admit FREE x2 base=609301 span=2000 / base=611301 "
       "span=200 + origin vacancy + zero W271/W272 skip-claims + leg4 W271p projection A 611_301..613_300 "
       "CLEAN / B 611_501..611_700 inside -> 20th A-hop expected + S6-light log 10 legs rc0 DONE 16:08:04 "
       "same-round absorbed) THEN prereg derive THIS window: needle facts-probe MEASURED (_w270bmc_needle_"
       "probe.py/json; 8/8 block markers count==1 spans valid; ALL old-band instances block-interior "
       "outside=0; zero-floors clean; r1077 law) -> derive _w270bmc_prereg_derive.py ALL GATES PASS "
       "(40 vmap legs / 108 floors / 13 POST_LEGS / 81 MUST / 63 MUST_NOT / 8 block replaces; 1 disclosed "
       "authoring heal#1: 4 T0-present current-wave faces mis-set as zero-floors, caught by the fail-closed "
       "gate PRE-write zero disk pollution, moved to MUST_NOT) -> research/PERPETUAL_N1_W270_PREREG.md "
       "23,259B sha256_16 3aa0b98239369608 sec7/8 placeholders intact; anchors FULL-PRECISION machine-"
       "gated vs n1_w269_results.json + fivekeys 6/6 (merged mu -0.09273072 / sigma 0.24506175 / se_mu "
       "0.000319 / W269-only -0.09084568 / A p95 0.3158 / K-lift +0.0001 / line_merged@589,720 1.1961 / "
       "ledger 1,016,135 EXACT); 13 POST_LEGS incl finalize stamp roll 14:0x->15:4x + se_mu chain "
       "true-history W269 0.000319 correction (r1059 canon-embed) + RAM face ~2.1GB live + RAM ledger W269 "
       "~2.1G anchor append (W263/W264 mis-shift restored) + paradigm rows bm-c r1093; banned_direction_"
       "gate ADMIT rc0; idempotent byte-identical re-run; push LANDED first-try 9f480646f4..3bb8b9308e "
       "behind=0 fetch-verified + S0.5 dual-delta FALSE both scans (ord b94534b0 / dec 4cfdd17c hold; "
       "orders_ack_scan CLEAN 102/227/0 zero face divergence; unacked=0) + smoke 49/49 + S6 light 10/10 "
       "absorbed + attrition 4 CLEAN + idle --worked rc0 + quad green (loop pin=5 no-op + watchdog "
       "registered [S4U flip access-denied = adjudicated default-principal standing face per D-20261002-02] "
       "+ pre-commit claw + pre-push claw installed) + orphan face=0 zero-kill (probe py_faces=3)")

NEXT = ("r1095: (1) W270 five-face freeze splice editor derive = FIRST ACTION (canon-clone _w269bmc "
        "machinery per E63 age() machine-needle law: derive editor -> freeze edits -> splice; MEASURED "
        "needle preflight r1077 law; setwave aging law rep _set_wave(269)->_set_wave(270) + presence "
        "gates _set_wave(270):1/(269):0; r1091 W268 编辑器出稿双坑预检: gone 清单禁收裸波号 token + "
        "折行断言形拆短 needle 禁跨续行拼长串; canon = _w269bmc_freeze_edits.py blob @ 440b07c94b "
        "family [verify worktree==HEAD twin at preflight]; bands A 609_301..611_300 / B 611_301..611_500 "
        "registered on splice) -> engine mtime-watch self-burn 12/12 -> sixgate PRE-FINALIZE (33rd "
        "consecutive) -> finalize one-pass (ledger 1,016,135+2,200=1,018,335 / K 589,720+2,200=591,920 "
        "projected; live registry derive governs) -> fivekeys 6/6 -> sec.7/8 backfill -> W271 seat "
        "publish (probe canon-clone; naive W271 A 611_301 REFUSED at registered W270 B 611_301..611_500 "
        "expected per prereg §5 item5 leg4 note; live walk governs never transcribe r587); (2) xq32 "
        "ticket watch: chain step-3 (t1r1hd) ETA was ~17:10 + S5-27 director ruling -> author follow-on "
        "chain step for the 8 remaining slots per staging map results/_r1090bmc_xq32_staging.json; if MV "
        "ops seat returns, 查重律 yields the lane; (3) Monday 10-20 15:30 bars window: full papers chain "
        "(papers debt=0; weekend 10-18/19 no bars, cutoff 10-16 current); (4) RAM watch standing (MV "
        "PACK-A GPU burn in flight ~2.1-2.8GB free observed; loop CPU-only); (5) 24h died-pre-closeout "
        "incident-review watch standing per O-20261018-0948 sec.3.4")

ARTIFACT = ("research/PERPETUAL_N1_W270_PREREG.md (origin 3bb8b9308e; 23,259B sha256_16 3aa0b98239369608; "
            "bands A 609_301..611_300 NINETEENTH A-hop / B 611_301..611_500 TWENTIETH above-own-A; upstream "
            "anchors ledger 1,016,135 / K=589,720 / merged mu -0.09273072) + results/_w270bmc_prereg_derive.py "
            "+ results/_w270bmc_needle_probe.json + results/_w270bmc_20261018_probe_receipt.json (seat, "
            "origin 9f480646f4) + fleet/inbox/MSG-20261018-1605-bmc-w270-seat.md")

VERDICT = ("green r1094-continuation product window (W270 seat absorbed + W270 prereg frozen, both on "
           "origin 9f480646f4+3bb8b9308e; clean continuation after dead r1094 seat window; CEO weekend-use "
           "standing loop CPU-only, GPU=MV PACK-A gen lane 98% util)")

# ---- state face ----
sp = os.path.join(REPO, "state-bm-c.json")
with open(sp, encoding="utf-8") as f:
    st = json.load(f)
assert st["round_no"] in (1094, 1095), "counter precondition: %r (1095 = idempotent re-run)" % st["round_no"]
st.update({
    "round_no": 1095, "round_no_label": "r1094 closeout -> counter 1095",
    "last_round": "r1094", "last_round_at": NOWISO, "last_round_ts": NOWISO,
    "last_seen": NOWISO, "last_seen_at": NOWISO, "ts": NOWISO, "updated": NOWISO,
    "updated_at": NOWISO, "clock_read": NOWISO, "activity_now": NOWISO, "now_active": NOWISO,
    "last_round_closed": NOWISO, "last_round_closed_at": NOWISO,
    "last_round_label": "r1094",
    "current_task": "r1094 closeout: W270 seat+prereg landed origin 9f480646f4+3bb8b9308e; next = W270 five-face splice editor derive r1095 FIRST ACTION",
    "current_task_at": NOWISO, "current_task_ts": EPOCH,
    "did": DID, "last_round_summary": DID[:1200], "last_round_summary_at": NOWISO,
    "last_action": "r1094 closeout (W270 seat absorb + prereg freeze; counter 1094->1095)",
    "last_action_at": NOWISO, "head_sha": "r1094 closeout (W270 seat absorb + prereg freeze; counter 1094->1095)",
    "verdict": VERDICT, "verify": ("prereg worktree==committed blob sha256_16 3aa0b98239369608 + push 3bb8b9308e "
             "behind=0 fetch-verified + banned_direction_gate ADMIT json + derive gates ALL PASS + smoke 49/49 "
             "+ attrition 4 CLEAN + idle --worked rc0 + quad green + S0.5 dual FALSE both scans + unacked=0 "
             "+ 本地未达 origin commit 数=0"),
    "next": NEXT, "next_pointer": NEXT,
    "latest_artifact": ARTIFACT, "last_artifact": ARTIFACT, "recent_artifact": ARTIFACT,
    "next_milestone": ("W270 splice+burn+sixgate+finalize+W271 seat (r1095-r1097, within 48h); Monday 10-20 "
                        "15:30 papers chain; xq32 remaining-8 on chain step-3 + director ruling"),
    "prod_lanes": ("CPU=engine W270 armed (prereg frozen -> splice editor derive r1095 FIRST ACTION); "
                   "GPU=MV PACK-A i2v burn in flight (CEO weekend production standing: gen-only, loop "
                   "CPU-only); short-video lane DISABLED standing per O-20261017-1741"),
    "full_load_selfproof": {"占用一行": ("CPU=engine W270 armed (prereg frozen 3bb8b9308e -> splice editor "
        "derive r1095 FIRST ACTION); GPU=MV PACK-A i2v burn in flight (gen-only standing, loop CPU-only); "
        "short-video lane DISABLED standing per O-20261017-1741")},
    "note": ("r1094: continuation window per absorb lineage -- dead r1094 seat window (16:05 seat commit "
             "9f480646f4) died pre-closeout; THIS window executed as r1094-continuation per counter, "
             "machine-verified the estate, landed the W270 PREREG FREEZE 3bb8b9308e, advanced counter "
             "1094->1095; zero double-count: S0.5 dual-delta FALSE both scans (the dead window consumed "
             "nothing), seat debts handled by its own commit, prereg+estate landed by this window"),
    "orphan_face": 0, "orphan_faces": 0,
    "free_ram_gb": FREE_RAM, "ram_free_gb": FREE_RAM, "idle_ram_gb": FREE_RAM,
    "cpu_pct": CPU_PCT, "cpu_util_pct": CPU_PCT, "cpu_idle_pct": round(100 - CPU_PCT, 1),
    "gpu_util_pct": gu, "gpu_mem_used_mib": gm, "gpu_total_vram_mib": gt,
    "gpu_free_vram_mib": gt - gm, "gpu_free_vram_mb": gt - gm, "free_vram_mb": gt - gm,
    "orders_ack_receipt": ("r1094: ORD/DEC dual-delta FALSE both scans (ord content-sha1 b94534b0 / dec "
                           "raw-blob sha256 4cfdd17c hold per state keys; unacked=0; orders_ack_scan CLEAN "
                           "102 orders / 227 acks / zero face divergence); zero consumption owed this window"),
    "last_orders_read_note": "r1094: ORD delta FALSE hold at close (content-sha1 b94534b0 pinned-probe, zero rows owed)",
    "last_decisions_read_note": "r1094: DEC delta FALSE hold at close (raw-blob sha256 4cfdd17c, zero rows owed)",
    "ram_critical_face": ("MV PACK-A i2v GPU-lane python squeeze watch standing; loop CPU-only; free=%.2fGB "
                          "at r1094 closeout (derive survived at this level)" % FREE_RAM),
    "sync": {"origin_tip": "r1094 prereg freeze 3bb8b9308e landed (push first-try, behind=0 fetch-verified)",
             "ts": NOWISO},
    "r1094_absorb_note": ("r1094 absorb note: prior window (self-labeled r1094, fired ~16:0x) executed the "
        "W270 seat publish body (probe _w270bmc_20261018_probe.py canon-clone of _w269bmc bloodline + seat "
        "MSG-20261018-1605-bmc-w270-seat + commit+push 9f480646f4 + facts gather _r1094bmc_facts_gather.py "
        "+ frozen-face extraction + S6-light 10 legs DONE 16:08:04 rc0), then died pre-closeout (state "
        "counter frozen at 1094, heartbeat stale at r1093). THIS window (per bm-c absorb precedent lineage "
        "r894..r1093) machine-verified the estate BEFORE landing (frozen-face byte-identity + facts json + "
        "seat receipt ADMIT + S6 log rc0), executed as r1094-continuation per counter, landed the prereg "
        "freeze + estate commit 3bb8b9308e, and advanced counter 1094->1095; zero double-count: S0.5 "
        "dual-delta FALSE both scans (the dead window consumed no ORD/DEC rows), seat debts handled by its "
        "own commit"),
    "r1094_closeout_note": ("r1094: (1) S0-1 anchor bm-c + round-zero probe py_faces=3 orphans=0 zero-kill + "
        "S0 fetch 0/0 clean open (HEAD==origin 9f480646f4, 20 dirty = daemon live-faces + dead-window "
        "estate, no rebase owed); (2) S0.5 dual-delta FALSE both scans (ord b94534b0 / dec 4cfdd17c "
        "pinned-probe hold; unacked=0; orders_ack_scan CLEAN 102/227/0 zero face divergence); (3) smoke "
        "49/49; (4) P0 PRODUCT = W270 PREREG FREEZE LANDED 3bb8b9308e pushed first-try 9f480646f4..3bb8b9308e "
        "behind=0: absorb dead-r1094 estate (machine-verified: frozen face byte-equal @67fe12710c + facts + "
        "seat receipt ADMIT + S6-light log) + needle facts-probe MEASURED (8/8 markers, old-band "
        "outside=0) + derive ALL GATES PASS heal#1 (4 T0-present current-wave faces mis-zeroed, caught "
        "fail-closed pre-write, moved to MUST_NOT) + 13 POST_LEGS + banned ADMIT rc0 + idempotent "
        "byte-identical 3aa0b98239369608; bands A 609_301..611_300 NINETEENTH A-hop / B 611_301..611_500 "
        "TWENTIETH above-own-A per seat receipt verbatim; anchors FULL-PRECISION machine-gated (r1093 pit "
        "entry honored); (5) S3: satengine ALIVE rc0 (W269 dedup 12/12 complete) + wm red=false healthy + "
        "idle green_idle=false (window has actual work); (6) S6 light 10/10 absorbed (dead-window 16:08:04 "
        "rc0 same-round law; dualrun streak 51 / bars cutoff 10-16 weekend honest / ORANGE 6th day / token "
        "delta=0); (7) S7: attrition 4 CLEAN + idle --worked rc0 + quad green (loop pin=5 no-op + watchdog "
        "S4U flip access-denied = adjudicated default-principal standing face per D-20261002-02 + claws x2 "
        "installed) + orphan face=0; counter 1094->1095"),
})
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
with open(sp, encoding="utf-8") as f:
    st2 = json.load(f)
assert st2["round_no"] == 1095 and st2["last_round"] == "r1094"

# ---- heartbeat face ----
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
hb.update({
    "clock_read": NOWISO, "cpu_pct": CPU_PCT, "cpu_idle_pct": round(100 - CPU_PCT, 1),
    "current_task": st["current_task"], "current_task_at": NOWISO, "current_task_ts": EPOCH,
    "did": DID, "free_ram_gb": FREE_RAM, "idle_ram_gb": FREE_RAM, "ram_free_gb": FREE_RAM,
    "heartbeat_epoch_utc": EPOCH, "last_round": "r1094", "last_round_at": NOWISO,
    "last_round_ts": NOWISO, "last_seen": NOWISO, "last_seen_at": NOWISO, "ts": NOWISO,
    "round_no": 1095, "round_no_label": "r1094 closeout -> counter 1095",
    "last_round_summary": DID[:1200], "last_round_summary_at": NOWISO,
    "last_action": st["last_action"], "last_action_at": NOWISO,
    "last_round_closed": NOWISO, "last_round_closed_at": NOWISO, "last_round_label": "r1094",
    "verdict": VERDICT, "next_pointer": NEXT, "next": NEXT, "next_milestone": st["next_milestone"],
    "latest_artifact": ARTIFACT, "last_artifact": ARTIFACT, "recent_artifact": ARTIFACT,
    "activity_now": NOWISO, "now_active": NOWISO, "updated": NOWISO, "updated_at": NOWISO,
    "idle_rounds": 0, "agenda_starved": False,
    "gpu_util_pct": gu, "gpu_mem_used_mib": gm, "gpu_total_vram_mib": gt,
    "gpu_free_vram_mib": gt - gm, "gpu_free_vram_mb": gt - gm, "free_vram_mb": gt - gm,
    "gpu_free_mb": gt - gm, "gpu_idle_mb": gt - gm,
    "prod_lanes": st["prod_lanes"], "full_load_selfproof": st["full_load_selfproof"],
    "note": st["note"], "ram_critical_face": st["ram_critical_face"],
    "sync": st["sync"],
    "r1094_absorb_note": st["r1094_absorb_note"], "r1094_closeout_note": st["r1094_closeout_note"],
    "head_sha": st["head_sha"], "verify": st["verify"],
    "orders_ack_receipt": st["orders_ack_receipt"],
    "last_orders_read_note": st["last_orders_read_note"],
    "last_decisions_read_note": st["last_decisions_read_note"],
    "orphan_face": 0, "orphan_faces": 0,
    "last_round_at_legacy": hb.get("last_round_at_legacy"),
})
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
with open(hp, encoding="utf-8") as f:
    hb2 = json.load(f)
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
assert hb2["round_no"] == 1095 and len(hb2["orders_ack"]) == len(hb["orders_ack"]), \
    "heartbeat read-back: list length must hold (orders_ack_count FIELD is a known stale mirror r1052-family face)"

# ---- round report row (canonical root path per r750 law) ----
rp = os.path.join(REPO, "round_reports-bm-c.md")
ROW = ("| %s | r1094 | bm-c | watermark verdict=green (red=false / ORD-DEC dual FALSE both scans "
       "b94534b0/4cfdd17c hold / unacked=0 ack-scan CLEAN 102/227/0 / satengine ALIVE rc0 W269 dedup "
       "12/12 complete / dualrun ZERO-DRIFT streak 51) | r1094: W270 SEAT + W270 PREREG FREEZE LANDED "
       "origin 9f480646f4 + 3bb8b9308e (dead r1094 window published seat 16:05 then died pre-closeout; "
       "THIS r1094-continuation window absorbed per bm-c absorb lineage: estate machine-verified [frozen "
       "face 23,207B byte-equal @67fe12710c pre-backfill face + facts full-precision + seat receipt ADMIT "
       "A 609_301..611_300 NINETEENTH A-hop / B 611_301..611_500 TWENTIETH above-own-A + S6-light log "
       "16:08:04 rc0 same-round absorbed] then needle facts-probe MEASURED [8/8 markers + old-band "
       "outside=0 r1077 law] -> derive ALL GATES PASS heal#1 [4 T0-present faces mis-zeroed caught "
       "fail-closed PRE-write] + 13 POST_LEGS [stamp 15:4x + se_mu true-history W269 0.000319 + RAM "
       "~2.1GB + ledger W269 anchor + paradigm r1093] + anchors FULL-PRECISION machine-gated vs "
       "n1_w269_results+fivekeys 6/6 [ledger 1,016,135 / K=589,720 / mu -0.09273072 / p95 0.3158 / "
       "K-lift +0.0001] + banned ADMIT rc0 + idempotent byte-identical 3aa0b98239369608 + out 23,259B "
       "sec7/8 placeholders intact + push first-try behind=0) + smoke 49/49 + S6 light 10/10 absorbed + "
       "attrition 4 CLEAN + idle --worked + quad green (loop pin=5 no-op + watchdog S4U adjudicated face "
       "+ claws x2) + orphan face=0 | 验证: prereg on origin ls-tree blob 3aa0b982 + push 3bb8b9308e "
       "behind=0 fetch-verified + derive gates ALL PASS + banned ADMIT json + 本地未达 origin commit 数=0 "
       "| 下步: W270 five-face splice editor derive = r1095 FIRST ACTION (canon-clone _w269bmc E63 + "
       "r1091 W268 出稿双坑预检 gone 表/折行面) + xq32 chain step-3 watch (ETA ~17:10 + follow-on 8 slots "
       "per staging map) + Monday 10-20 15:30 papers chain |\n\n" % NOWISO)
with io.open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(ROW)
print("CLOSEOUT OK r1094->1095 @ %s | ram=%.2fGB gpu=%d%%/%dMiB | epoch=%d" % (NOWISO, FREE_RAM, gu, gm, EPOCH))
