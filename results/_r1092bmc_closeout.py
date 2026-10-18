# -*- coding: utf-8 -*-
# r1092 bm-c closeout: state round 1092->1093 + heartbeat two-face + round-report row.
# Product = W269 PREREG FREEZE landed origin 67fe12710c (after bm-a r1058 / bm-b r1007
# push-race rebase, watermark_red UU theirs live-wins). Zero absorb owed (r1091 closed clean
# 14:15:30, this session opened 14:26 solo). Watermarks ORD 913b8097 / DEC 4cfdd17c held
# both scans (d19 probe FALSE x2, unacked=0). Heartbeat mirrors must stay == state (r1052 law).
import json, io, os, time, datetime, subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(REPO, "state-bm-c.json")
HEART = os.path.join(REPO, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(REPO, "round_reports-bm-c.md")

now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")            # 2026-10-18T14:5x:xx+08:00 (T-format, R262)
epoch = int(time.time())

ram_free = round(__import__("psutil").virtual_memory().available / (1024 ** 3), 2)
try:
    g = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                         "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20)
    util, used, total = [x.strip() for x in g.stdout.strip().split(",")]
    gpu_face = "util %s%% / %s MiB used of %s" % (util, used, total)
except Exception:
    gpu_face = "nvidia-smi unavailable"

did = ("r1092: W269 PREREG FREEZE LANDED origin 67fe12710c (machine-SUB from frozen W268 tpl @ f1ec8231c7 "
       "pre-backfill face; needle facts-probe MEASURED 53 floors/47 zeros rc0 r1077 law with T1-sim "
       "block-interior classification; derive ALL GATES PASS first-try vmap39+floors91+post-legs13+8blocks"
       "+MUST78/MUST_NOT74+pinned+residue; 13 disclosed one-generation heals: stamp roll 12:2x->14:0x + "
       "sec5 item1/2/3/4 W268 actuals (W268-only diff 0.0002 honest in-band) + se_mu chain true-history + "
       "RAM face ~1.4GB live + precedent ledger W268 ~1.4G anchor + seat legs MSG-1407/d630d043b9/r1091 + "
       "engine live-read r1092; banned_direction_gate ADMIT rc0; idempotent re-run byte-identical "
       "sha256_16 cc13880752beb39e; bands A 607_101..609_100 EIGHTEENTH consecutive A-hop / B "
       "609_101..609_300 NINETEENTH consecutive above-own-A; sec7/8 placeholders intact) + push-race "
       "rebase over bm-a r1058 + bm-b r1007 (watermark_red UU resolved theirs live-wins; machine-health "
       "stash-bridge dropped live-wins; conflict-marker scan zero on own faces) + S0.5 dual-delta FALSE "
       "both scans (ord 913b8097 / dec 4cfdd17c hold, unacked=0) + smoke 49/49 + S6 light 10/10 rc0 "
       "(dualrun ZERO-DRIFT streak 49 [461] / bars cutoff 10-16 weekend honest 0 rows / ORANGE 6th day / "
       "CALL-2026-10-16 ORANGE_COOL idempotent / fundprem weekend no-op / REPORT-2026-10-18 faces=5 / "
       "token delta=0 / audit FLAG supply_floor answered-by-chain W269-splice-next) + attrition 4 CLEAN "
       "(2 healed historical as-is) + idle --worked rc0 + quad green (loop pin=5 no-op + watchdog S4U "
       "flip=adjudicated default-principal standing face + claws x2 installed) + orphan face=2 zero-kill")

next_ptr = ("r1093: (1) W269 FIVE-FACE SPLICE = FIRST ACTION (editor derive canon-clone of "
            "_w268bmc_freeze_edits.py via E63 age() machine-needle law + MEASURED needle preflight per "
            "r1077 law at authoring time; setwave aging law rep('_set_wave(268)','_set_wave(269)',1) + "
            "phase5 presence gates _set_wave(269):1/_set_wave(268):0; W269 prereg frozen THIS window "
            "origin 67fe12710c; blocked faces until splice = NONE); (2) xq32 ticket watch: chain step-3 "
            "(t1r1hd) ETA ~17:10 + S5-27 director ruling -> author follow-on chain step for the 8 "
            "remaining slots per staging map results/_r1090bmc_xq32_staging.json; if MV ops seat "
            "returns, 查重律 yields the lane; (3) Monday 10-20 15:30 bars window: full papers chain "
            "(papers debt=0); (4) RAM watch standing (MV PACK-A GPU burn in flight, loop CPU-only; "
            "GPU " + gpu_face + "; free RAM %.2fGB); (5) short-video lane DISABLED standing per "
            "O-20261017-1741" % ram_free)

summary = ("r1092: W269 PREREG FREEZE LANDED origin 67fe12710c (derive ALL GATES PASS first-try + "
           "facts-probe MEASURED 53/47 rc0 + 13 disclosed heals + banned ADMIT + idempotent "
           "cc13880752beb39e; bands A 607_101..609_100 18th A-hop / B 609_101..609_300 19th "
           "above-own-A) + push-race rebase clean + S0.5 dual FALSE both + smoke 49/49 + S6 light "
           "10/10 + attrition 4 CLEAN + quad green | counter 1092->1093")

verify = ("prereg on origin ls-tree blob d7ae1195 + push 67fe12710c behind=0 fetch-verified + banned rc0 "
          "+ derive idempotent byte-identical + smoke 49/49 + sixgate face n/a (pre-splice) + attrition 4 "
          "CLEAN + idle --worked + dual FALSE tail scan + 本地未达 origin commit 数=0")

# ---------- state ----------
with io.open(STATE, encoding="utf-8") as f:
    st = json.load(f)
assert st["round_no"] == 1092, "round_no unexpected: %r" % st.get("round_no")
st["round_no"] = 1093
st["round_no_label"] = "r1092 closeout -> counter 1093"
st["last_round"] = "r1092"
st["last_round_at"] = ts
st["last_round_ts"] = ts
st["last_round_closed"] = ts
st["last_round_closed_at"] = ts
st["last_round_summary"] = summary
st["last_round_summary_at"] = ts
st["last_action"] = "r1092 closeout (W269 prereg freeze; counter 1092->1093)"
st["last_action_at"] = ts
st["head_sha"] = "r1092 closeout (W269 prereg freeze; counter 1092->1093)"
st["current_task"] = "r1092 closeout: W269 prereg frozen origin 67fe12710c; next = W269 five-face splice r1093 FIRST ACTION"
st["current_task_at"] = ts
st["current_task_ts"] = epoch
st["activity_now"] = ts
st["now_active"] = ts
st["updated"] = ts
st["updated_at"] = ts
st["last_seen"] = ts
st["last_seen_at"] = ts
st["ts"] = ts
st["did"] = did
st["verify"] = verify
st["next"] = next_ptr
st["next_pointer"] = next_ptr
st["verdict"] = ("green r1092 product window (W269 prereg freeze landed origin 67fe12710c; clean "
                 "continuation; CEO weekend-use standing loop CPU-only, GPU=MV PACK-A gen lane")
st["latest_artifact"] = ("research/PERPETUAL_N1_W269_PREREG.md (origin 67fe12710c, 23,207B sha256_16 "
                        "cc13880752beb39e) + results/_w269bmc_prereg_derive.py + facts-probe evidence "
                        "(53 floors/47 zeros MEASURED)")
st["last_artifact"] = st["latest_artifact"]
st["recent_artifact"] = st["latest_artifact"]
st["next_milestone"] = ("W269 splice + engine self-burn + finalize + W270 seat (r1093-r1095, within 48h); "
                        "Monday 10-20 15:30 papers chain; xq32 remaining-8 on chain step-3 + director ruling")
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["orphan_face"] = 2
st["orphan_faces"] = 2
st["free_ram_gb"] = ram_free
st["ram_free_gb"] = ram_free
st["idle_ram_gb"] = ram_free
st["prod_lanes"] = ("CPU=engine W269 prereg frozen (supply armed: W269 five-face splice r1093 FIRST "
                    "ACTION); GPU=MV PACK-A i2v wave-1 burn in flight (CEO weekend production standing: "
                    "gen-only, loop CPU-only); short-video lane DISABLED standing per O-20261017-1741")
st["full_load_selfproof"] = {"占用一行": ("CPU=engine W269 prereg frozen (supply armed: W269 five-face "
                       "splice r1093 FIRST ACTION); GPU=MV PACK-A i2v wave-1 burn in flight (gen-only "
                       "standing, loop CPU-only); short-video lane DISABLED standing per O-20261017-1741")}
st["sync"] = {"origin_tip": "r1092 prereg-freeze push 67fe12710c landed (behind=0 fetch-verified same window)",
              "ts": ts}
st["r1092_closeout_note"] = ("r1092: (1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=2 "
    "zero-kill (legal resident faces family, adjudicated) + S0 fetch 0/0 clean open; (2) S0.5 "
    "dual-delta FALSE both scans (ord 913b8097 / dec 4cfdd17c pinned-probe hold; unacked=0; "
    "orders_ack_scan CLEAN 102/227/0 zero face divergence); (3) S1 smoke 49/49; (4) P0 PRODUCT = "
    "W269 PREREG FREEZE (facts gather _r1092bmc_facts_gather.py: frozen face byte-verified 23,158B "
    "sha1 7b08409b @ f1ec8231c7 + HEAD twin f770b46b disclosed NOT used + W268 fivekeys/receipts "
    "machine-read zero-transcription; needle facts-probe 53 floors/47 zeros rc0 MEASURED r1077 law; "
    "derive ALL GATES PASS first-try + banned ADMIT rc0 + idempotent byte-identical cc13880752beb39e); "
    "(5) push race: origin advanced 3 mid-window (bm-a r1058 W269-seat-yield confirmation + bm-b "
    "r1007) -> non-FF once -> machine-health stash-bridge + rebase (1 UU watermark_red.json shared "
    "regenerable, resolved theirs live-wins same-day idempotent) -> conflict-marker scan zero on own "
    "faces -> push LANDED 67fe12710c behind=0; (6) S6 light 10/10 rc0; (7) S7: attrition 4 CLEAN + "
    "idle --worked + quad green (loop pin=5 no-op + watchdog S4U flip access-denied = adjudicated "
    "default-principal standing face + claws x2) + tail dual-scan FALSE; counter 1092->1093 so next "
    "session = r1093")
with io.open(STATE, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
with io.open(STATE, encoding="utf-8") as f:
    chk = json.load(f)
assert isinstance(chk["round_no"], int) and chk["round_no"] == 1093

# ---------- heartbeat (mirror law r1052: mirrors must == state) ----------
with io.open(HEART, encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = ts
hb["last_seen_at"] = ts
hb["ts"] = ts
hb["clock_read"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = st["current_task"]
hb["current_task_at"] = ts
hb["did"] = did
hb["verdict"] = st["verdict"]
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["last_round"] = "r1092"
hb["last_round_at"] = ts
hb["round_no"] = 1093
hb["free_ram_gb"] = ram_free
hb["ram_free_gb"] = ram_free
hb["last_orders_sha"] = st.get("last_orders_sha")
hb["last_decisions_sha"] = st.get("last_decisions_sha")
hb["last_orders_seen"] = ts
hb["last_decisions_seen"] = ts
hb["last_orders_at"] = ts
hb["last_decisions_at"] = ts
hb["last_orders_read_at"] = ts
hb["last_decisions_read_at"] = ts
hb["prod_lanes"] = st["prod_lanes"]
with io.open(HEART, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
with io.open(HEART, encoding="utf-8") as f:
    hchk = json.load(f)
assert isinstance(hchk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in hchk["clock_read"], "clock_read must be T-separated ISO8601 (R262 law)"
assert hchk["last_orders_sha"] == chk["last_orders_sha"], "ORD mirror divergence (r1052 law)"
assert hchk["last_decisions_sha"] == chk["last_decisions_sha"], "DEC mirror divergence (r1052 law)"

# ---------- round report row ----------
row = ("| %s | r1092 | bm-c | watermark verdict=green (red=false / ORD-DEC dual FALSE both scans "
       "913b8097/4cfdd17c hold / satengine ALIVE rc0 burns=[] queue=[] / dualrun ZERO-DRIFT streak 49) "
       "| r1092: W269 PREREG FREEZE LANDED origin 67fe12710c (machine-SUB from frozen W268 tpl @ "
       "f1ec8231c7 pre-backfill; facts-probe MEASURED 53 floors/47 zeros rc0 r1077 law; derive ALL "
       "GATES PASS first-try; 13 disclosed one-generation heals incl. stamp roll 12:2x->14:0x + sec5 "
       "W268 actuals diff 0.0002 honest + se_mu chain true-history + RAM ~1.4GB live + ledger W268 "
       "~1.4G anchor + seat legs + engine live-read r1092; banned ADMIT rc0; idempotent "
       "byte-identical cc13880752beb39e; bands A 607_101..609_100 18th A-hop / B 609_101..609_300 19th "
       "above-own-A) + push-race rebase over bm-a r1058 + bm-b r1007 (watermark_red UU theirs "
       "live-wins + machine-health stash-bridge drop + marker scan zero) + smoke 49/49 + S6 light "
       "10/10 rc0 (dualrun streak 49 [461] / bars cutoff 10-16 weekend honest / ORANGE 6th day / CALL "
       "idempotent / fundprem no-op / REPORT faces=5 / token delta=0 / audit FLAG supply_floor "
       "answered-by-chain) + attrition 4 CLEAN + idle --worked + quad green (loop pin=5 no-op + "
       "watchdog S4U flip=adjudicated face + claws x2) + orphan face=2 zero-kill | 验证: prereg on "
       "origin ls-tree blob d7ae1195 + push 67fe12710c behind=0 fetch-verified + 本地未达 origin commit "
       "数=0 | 下轮: W269 five-face splice r1093 FIRST ACTION (editor canon _w268bmc_freeze_edits.py + "
       "setwave aging law) + xq32 chain step-3 watch + Monday 10-20 15:30 papers chain |" % ts)
with io.open(REPORT, "a", encoding="utf-8", newline="\n") as f:
    f.write("\n" + row + "\n")

print("r1092 closeout OK: round 1092->1093 | ts %s | epoch %d | RAM %.2fGB | %s" % (ts, epoch, ram_free, gpu_face))
