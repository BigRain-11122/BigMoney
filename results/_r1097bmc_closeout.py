# -*- coding: utf-8 -*-
# r1097 bm-c closeout: state advance 1097->1098 + heartbeat + round-report row (canonical
# root path per r750 law, lean clone of _r1095bmc_closeout.py). Fresh-read-modify-write both
# faces; read-back asserts (R170/R178 epoch int law).
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
    gu, gm, gt = 0, 7000, 16384

DID = ("r1097: W271 CYCLE COMPLETE -- five-face freeze chain executed as r1096-pointer FIRST ACTION in ONE "
       "window: needle preflight MEASURED (results/_r1097bmc_needle_preflight.py/json: canon triple "
       "fbbcc7d68a9afcbf 62,142B wt==HEAD==origin + W271 prereg frozen face git-object-verified "
       "f8b4a755d81bfbe5 23,336B HEAD==origin, disk CRLF-smudged norm-eq per r1093 EOL law) -> derive "
       "editor E63 15th-gen (2 gone-list authoring heals caught PRE-splice fail-closed [18:2x header-stamp "
       "producer-news + if w<270) anti-gate producer-news, r1091 gone-list law family], zero pollution) -> "
       "freeze edits 62,154B py_compile OK -> SPLICE LANDED origin 7dd091eef1 push first-try behind=0 "
       "(gate0.5 green W270 upstream 1,018,335/K=591,920 in place; dual-sha16 pf ac69ecefdd9af8f7 / n1 "
       "d8b052161c11e25d; pf selftest 9/9 + n1 selftest PASS + banned ADMIT) -> engine mtime-watch "
       "self-burn 12/12 (batched self-commits a035552321+037445477b) -> sixgate PRE-FINALIZE ALL PASS "
       "34th consecutive CLEAN-AT-BIRTH 4th gen (_set_wave(271):1/(270):0/(269):0 segment + CR-normalized "
       "worktree==landed) -> finalize one-pass ledger 1,018,335+2,200=1,020,535 EXACT / K "
       "591,920+2,200=594,120 EXACT (w271-only mu -0.1028 / merged -0.0928 / sigma 0.2451 / K-lift +0.0001) "
       "-> fivekeys 6/6 ALL PASS [key3 A p95 0.3268->0.3042 double-direction in-band / key5 se_mu "
       "0.000319->0.000318 narrowed; anchors FULL-PRECISION machine-read from n1_w270_results.json per "
       "r1093 pit law] -> sec.7/8 backfilled placeholders=0 -> cycle estate e0a21b817d pushed behind=0; "
       "S0.5: O-20261018-1810-bm-c all-resume broadcast CONSUMED (resume verified machine-state 18:06:57 "
       "resumed + SatEngine ALIVE; loop checkbox ticked in-order; orders_ack two-face append 228; 1 "
       "self-inflicted --help bogus-entry pit [orders_ack_append positional-arg tool treats --help as ack "
       "target] cleaned both faces same-window, disclosed); S6 light 10/10 rc0; S7: attrition 4 CLEAN + "
       "idle --worked rc0 + quad green (loop pin=5 no-op + watchdog adjudicated-default face [S4U flip "
       "access-denied, manual re-pass backlog] + claws x2 installed) + tail dual-scan FALSE both (ord "
       "c8b328c1 / dec 4cfdd17c hold, zero d19 action) + orphan face=0")

NEXT = ("r1098: (1) W272 SEAT PUBLISH = FIRST ACTION (seat-first supply O-20261010-2350 sec.2: probe "
        "_w272bmc_20261018_probe.py canon-clone of _w271bmc_20261018_probe.py per E63 age() machine-needle "
        "law; pre-disclosed staircase per W271 seat receipt leg4: naive W272 A 613_501..615_500 REFUSED at "
        "registered W271 B 613_501..613_700 -> A first-clean past 613_700 [TWENTY-FIRST consecutive A-hop "
        "expected] / B own-A reservation cascade lands above own-A; live re-derive governs never transcribe "
        "r587; seed_admit + origin vacancy four-check + seat MSG + push) + W272 PREREG DERIVE SAME WINDOW "
        "(r1094 seat+prereg one-window precedent; SUB source = W271 prereg frozen face @ f75b18c862 "
        "PRE-backfill [HEAD twin = post-backfill, NOT used per r1049/r1052 law]; anchors FULL-PRECISION "
        "machine-read from n1_w271_results.json per r1093 pit law; ledger head 1,020,535 / K 594,120); "
        "(2) Monday 10-20 15:30 bars window: full papers chain (weekend 10-18/19 no bars, cutoff 10-16 "
        "current, debt=0); (3) xq32 S5-27 PENDING-bmc-reroll: physical GPU re-roll queued behind PACK-A "
        "i2v drain (GPU KF lane, loop CPU-only standing); (4) RAM watch standing (MV PACK-A GPU lane; loop "
        "CPU-only); (5) watchdog S4U manual re-pass backlog face (adjudicated default-principal standing)")

ARTIFACT = ("W271 cycle estate origin e0a21b817d (results/perpetual_faces/n1_w271_results.json finalize "
            "one-pass ledger 1,020,535 / merged K 594,120 EXACT + sixgate/fivekeys receipts + sec.7/8-"
            "backfilled research/PERPETUAL_N1_W271_PREREG.md) + splice estate 7dd091eef1 (derive editor + "
            "freeze edits + freeze receipt + needle preflight)")

VERDICT = ("green r1097 product window (W271 full five-face cycle landed e0a21b817d in ONE window; splice "
           "push first-try behind=0; S0.5 O-20261018-1810 all-resume consumed + acked two-face; CEO "
           "full-mobilization resume standing post game-window; loop CPU-only, GPU=MV PACK-A per "
           "O-20261018-1810 sec.2)")

# ---- state face ----
sp = os.path.join(REPO, "state-bm-c.json")
with open(sp, encoding="utf-8") as f:
    st = json.load(f)
assert st["round_no"] in (1097, 1098), "counter precondition: %r (1098 = idempotent re-run)" % st["round_no"]
st.update({
    "round_no": 1098, "round_no_label": "r1097 closeout -> counter 1098",
    "last_round": "r1097", "last_round_at": NOWISO, "last_round_ts": NOWISO,
    "last_seen": NOWISO, "last_seen_at": NOWISO, "ts": NOWISO, "updated": NOWISO,
    "updated_at": NOWISO, "clock_read": NOWISO, "activity_now": NOWISO, "now_active": NOWISO,
    "last_round_closed": NOWISO, "last_round_closed_at": NOWISO,
    "last_round_label": "r1097",
    "current_task": "r1097 closeout: W271 cycle landed origin e0a21b817d; next = W272 seat publish + prereg derive r1098 FIRST ACTION",
    "current_task_at": NOWISO, "current_task_ts": EPOCH,
    "did": DID, "last_round_summary": DID[:1200], "last_round_summary_at": NOWISO,
    "last_action": "r1097 closeout (W271 cycle complete; counter 1097->1098)",
    "last_action_at": NOWISO, "head_sha": "r1097 closeout (W271 cycle complete; counter 1097->1098)",
    "verdict": VERDICT, "verify": ("W271 sixgate PRE-FINALIZE ALL PASS + finalize one-pass ledger 1,020,535 EXACT / "
             "K 594,120 EXACT + fivekeys 6/6 (anchors full-precision machine-read) + sec.7/8 placeholders=0 + "
             "cycle push e0a21b817d behind=0 + splice push 7dd091eef1 behind=0 + O-20261018-1810 acked "
             "two-face 228 + S6 light 10/10 + attrition 4 CLEAN + s05 tail dual-scan FALSE both (ord "
             "c8b328c1/dec 4cfdd17c hold) + unacked=0 + idle --worked rc0 + quad green (loop pin=5 + "
             "watchdog adjudicated-default + claws x2) + heartbeat epoch int + clock_read ISO-T read-back + "
             "本地未达 origin commit 数=0"),
    "next": NEXT, "next_pointer": NEXT,
    "latest_artifact": ARTIFACT, "last_artifact": ARTIFACT, "recent_artifact": ARTIFACT,
    "next_milestone": ("W272 seat publish + prereg derive (r1098 FIRST ACTION, within 48h); Monday 10-20 "
                       "15:30 papers chain; xq32 S5-27 GPU re-roll behind PACK-A drain"),
    "prod_lanes": ("CPU=engine W272 seat+prereg armed (r1098 FIRST ACTION on the post-W271-REGISTERED "
                   "universe); GPU=MV PACK-A i2v lane per O-20261018-1810 sec.2 (CEO full-mobilization "
                   "resume standing; loop CPU-only); short-video lane DISABLED standing per O-20261017-1741"),
    "note": ("r1097: product window (state round_no=1097 at open, executed r1097, advanced 1097->1098 so "
             "next=r1098); zero absorb owed (r1096 closeout landed clean 17:59, zero dead window between -- "
             "this window executed the W271 five-face splice chain in direct continuation per the r1096 "
             "pointer); zero double-count: S0.5 opening dual-delta FALSE both scans (ord c8b328c1 / dec "
             "4cfdd17c per r1096 tail pins) + S7 tail re-scan FALSE both; the S0.5 consumption this window "
             "= O-20261018-1810-bm-c BM-repo order (all-resume broadcast acked two-face + checkbox ticked)"),
    "orphan_face": 0, "orphan_faces": 0,
    "free_ram_gb": FREE_RAM, "ram_free_gb": FREE_RAM, "idle_ram_gb": FREE_RAM,
    "cpu_pct": CPU_PCT, "cpu_util_pct": CPU_PCT, "cpu_idle_pct": round(100 - CPU_PCT, 1),
    "gpu_util_pct": gu, "gpu_mem_used_mib": gm, "gpu_total_vram_mib": gt,
    "gpu_free_vram_mib": gt - gm, "gpu_free_vram_mb": gt - gm, "free_vram_mb": gt - gm,
    "orders_ack_receipt": ("r1097: S0.5 opening scan found 1 unacked BM-repo order O-20261018-1810-bm-c.md "
                           "(18:10 all-resume broadcast via bm-c interactive) -> CONSUMED same-window "
                           "(resume verified machine-state 18:06:57 resumed + SatEngine ALIVE + S6 10/10; "
                           "in-order checkbox ticked; orders_ack_append two-face 228; 1 self-inflicted "
                           "--help bogus-entry pit [positional-arg tool, --help treated as ack target] "
                           "cleaned both faces same-window, disclosed); group faces: opening dual FALSE "
                           "(ord c8b328c1 / dec 4cfdd17c hold per r1096 pins) + S7 tail FALSE both, zero "
                           "d19 action owed"),
    "last_orders_read_note": "r1097: ORD delta FALSE at open+tail both (content-sha1 c8b328c1 hold; zero rows owed)",
    "last_decisions_read_note": "r1097: DEC delta FALSE at open+tail both (raw-blob sha256 4cfdd17c hold; zero rows owed)",
    "ram_critical_face": ("MV PACK-A i2v GPU-lane python squeeze watch standing; loop CPU-only; free=%.2fGB "
                          "at r1097 closeout (cycle survived at this level)" % FREE_RAM),
    "sync": {"origin_tip": "r1097 W271 CYCLE COMPLETE e0a21b817d landed (push first-try, behind=0); closeout commit rides this window",
             "ts": NOWISO},
})
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
with open(sp, encoding="utf-8") as f:
    st2 = json.load(f)
assert st2["round_no"] == 1098 and st2["last_round"] == "r1097"

# ---- heartbeat face ----
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
hb.update({
    "clock_read": NOWISO, "cpu_pct": CPU_PCT, "cpu_idle_pct": round(100 - CPU_PCT, 1),
    "current_task": st["current_task"], "current_task_at": NOWISO, "current_task_ts": EPOCH,
    "did": DID, "free_ram_gb": FREE_RAM, "idle_ram_gb": FREE_RAM, "ram_free_gb": FREE_RAM,
    "heartbeat_epoch_utc": EPOCH, "last_round": "r1097", "last_round_at": NOWISO,
    "last_round_ts": NOWISO, "last_seen": NOWISO, "last_seen_at": NOWISO, "ts": NOWISO,
    "round_no": 1098, "round_no_label": "r1097 closeout -> counter 1098",
    "last_round_summary": DID[:1200], "last_round_summary_at": NOWISO,
    "last_action": st["last_action"], "last_action_at": NOWISO,
    "last_round_closed": NOWISO, "last_round_closed_at": NOWISO, "last_round_label": "r1097",
    "verdict": VERDICT, "next_pointer": NEXT, "next": NEXT, "next_milestone": st["next_milestone"],
    "latest_artifact": ARTIFACT, "last_artifact": ARTIFACT, "recent_artifact": ARTIFACT,
    "activity_now": NOWISO, "now_active": NOWISO, "updated": NOWISO, "updated_at": NOWISO,
    "idle_rounds": 0, "agenda_starved": False,
    "gpu_util_pct": gu, "gpu_mem_used_mib": gm, "gpu_total_vram_mib": gt,
    "gpu_free_vram_mib": gt - gm, "gpu_free_vram_mb": gt - gm, "free_vram_mb": gt - gm,
    "gpu_free_mb": gt - gm, "gpu_idle_mb": gt - gm,
    "prod_lanes": st["prod_lanes"],
    "note": st["note"], "ram_critical_face": st["ram_critical_face"],
    "sync": st["sync"],
    "head_sha": st["head_sha"], "verify": st["verify"],
    "orders_ack_receipt": st["orders_ack_receipt"],
    "last_orders_read_note": st["last_orders_read_note"],
    "last_decisions_read_note": st["last_decisions_read_note"],
    "orphan_face": 0, "orphan_faces": 0,
})
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
with open(hp, encoding="utf-8") as f:
    hb2 = json.load(f)
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
assert hb2["round_no"] == 1098 and len(hb2["orders_ack"]) == len(hb["orders_ack"]), \
    "heartbeat read-back: list length must hold (orders_ack_count FIELD is a known stale mirror r1052-family face)"

# ---- round report row (canonical root path per r750 law) ----
rp = os.path.join(REPO, "round_reports-bm-c.md")
ROW = ("| %s | r1097 | bm-c | watermark verdict=green (red=false lane healthy; S0.5 opening dual FALSE ord "
       "c8b328c1/dec 4cfdd17c hold per r1096 tail pins + 1 unacked BM-repo order O-20261018-1810-bm-c "
       "all-resume broadcast CONSUMED same-window [resume verified 18:06:57 + checkbox ticked + orders_ack "
       "two-face 228 + 1 self-inflicted --help bogus-entry pit cleaned disclosed]; S7 tail dual-scan FALSE "
       "both; unacked=0; satengine ALIVE burns 12/12; dualrun streak 51) | r1097: W271 CYCLE COMPLETE "
       "origin e0a21b817d (ONE-window five-face chain per r1096 pointer: needle preflight MEASURED [canon "
       "triple fbbcc7d68a9afcbf 62,142B + prereq frozen face f8b4a755d81bfbe5 git-object-verified per r1093 "
       "EOL law] -> derive editor E63 15th-gen with 2 gone-list authoring heals caught PRE-splice "
       "fail-closed [18:2x header-stamp + if w<270) anti-gate, zero pollution] -> SPLICE LANDED 7dd091eef1 "
       "first-try [gate0.5 green; pf ac69ecefdd9af8f7 / n1 d8b052161c11e25d; pf 9/9 + n1 selftest + banned "
       "ADMIT] -> engine mtime-watch self-burn 12/12 [a035552321+037445477b] -> sixgate PRE-FINALIZE ALL "
       "PASS 34th consecutive CLEAN-AT-BIRTH 4th gen -> finalize one-pass ledger 1,018,335+2,200=1,020,535 "
       "EXACT / K 591,920+2,200=594,120 EXACT [w271-only -0.1028 / merged -0.0928 / sigma 0.2451 / K-lift "
       "+0.0001] -> fivekeys 6/6 [key3 A p95 0.3268->0.3042 in-band / key5 se_mu 0.000319->0.000318 "
       "narrowed; anchors FULL-PRECISION machine-read n1_w270_results.json per r1093 pit law] -> sec.7/8 "
       "backfilled placeholders=0 -> estate e0a21b817d behind=0) + S6 light 10/10 rc0 + S7 attrition 4 "
       "CLEAN + idle --worked + quad green [loop pin=5 no-op + watchdog adjudicated-default face + claws "
       "x2] + orphan face=0 | 验证: cycle estate e0a21b817d + splice estate 7dd091eef1 both on origin "
       "behind=0 push first-try + sixgate/finalize/fivekeys receipts on disk + attrition scan rc0 + "
       "unacked=0 + epoch int + 本地未达 origin commit 数=0 | 下步: r1098 W272 SEAT PUBLISH FIRST ACTION "
       "[seat-first supply; naive W272 A 613_501..615_500 refused at registered W271 B 613_501..613_700 -> "
       "live re-derive never transcribe r587] + W272 prereg derive same window (r1094 one-window "
       "precedent); Monday 10-20 15:30 papers chain; xq32 S5-27 GPU re-roll behind PACK-A drain |\n\n" % NOWISO)
with io.open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(ROW)
print("CLOSEOUT OK r1097->1098 @ %s | ram=%.2fGB gpu=%d%%/%dMiB | epoch=%d" % (NOWISO, FREE_RAM, gu, gm, EPOCH))
