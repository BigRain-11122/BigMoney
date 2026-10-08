# -*- coding: utf-8 -*-
"""r904 bm-a closeout: report lines (r903 estate + r904) + state heal
902->904 + heartbeat.  Fresh-read-modify-write per multi-writer law."""
import io
import json
import time
import datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

# ---------- 1. round report lines (ROOT canonical) ----------
REPORT = "round_reports-bm-a.md"
R903_ESTATE = (
    "2026-10-09T07:0x+08:00 | r903 | bm-a | dept:research (W193 burn "
    "products landing + W193 finalize one-pass + W194 buildgen v1 draft; "
    "ESTATE LINE reconstructed by r904 successor from commit+workfile "
    "evidence -- r903 session fired ~06:38 pin, committed 06:59:26 "
    "(n1_w193 12/12 shard landing e2a679b90-rebased + daemon churn "
    "7de62af48-rebased), created W193 finalize product 07:00:46 + "
    "w193fin peek 07:02:05, then died WITHOUT closeout: no "
    "report/state/heartbeat writes; engine ledger zero materializer rows "
    "-- finalize = session one-pass after seeing bm-c W192 finalize "
    "land on origin; products machine-verified and adopted by r904 per "
    "r899/r902 estate law) | [r903 estate via bm-a r904]\n")
R904_LINE = (
    NOW + " | r904 | bm-a | dept:research (N1 perpetual supply line: "
    "r903 estate absorption + W193 finalize closeout + W194 prereg "
    "build window) | WM-VERDICT: green (red=false lane healthy; engine "
    "ALIVE rc0 idle queue0 post-W193-close; board open=0; DEC "
    "83813196/ORD 861949ca python-raw UNCHANGED via C: real-path "
    "fetch+show; orders diff double-scan unacked=0) | Current activity: "
    "r903 dead-session estate absorbed + W193 finalize landed on origin "
    "+ W194 prereg built | Recent artifacts: (1) results/perpetual_"
    "faces/n1_w193_results.json (07:00:46 r903 one-pass, adopted+pushed "
    "r904 origin 1316ab9e7; ledger 836,745+2,200=838,945 EXACT prev=="
    "W192 total; K=422,520 projection EXACT; mu -0.0929 4dp hold; A p95 "
    "0.2957; four pred keys ALL PASS; prereg sec7/sec8 cross-window "
    "machine backfill r864-exception honest note) (2) research/"
    "PERPETUAL_N1_W194_PREREG.md (origin e85717ec9; anchor rolled to "
    "W193 actuals per r590; bands A 441_604..443_603 / B 443_604.."
    "443_803; pool proj 424,720; banned gate rc0 zero hits) | Next "
    "milestone: r905=W194 five-face freeze window (probe selfcheck "
    "re-derive + N1_BANDS row 194 + WAVE_CONFIGS + materializer face + "
    "selftest W194 face + freeze commit -> engine tick self-ignites "
    "burn; window <=24h) + 10-09 15:30 bars -> evening marks chain "
    "(REGIME_GUARD enforce + live.paper + t35/t24 family) + pool "
    "replenish bm-c lane F-2026109-01 (window 10-10 00:00) | did: S0-1 "
    "anchored bm-a + orphan probe 0 (23 py faces) + dead-session "
    "census (no r903 codely process alive; workfile mtime 07:02:05 "
    "last; three-face estate verdict) + S0 writer-pause r832 (4 "
    "repo-writer schtasks disabled -> churn-absorb commit 42810524d -> "
    "pull --rebase clean 3/3 onto bm-c autofill tick 7f21c3ca8 -> "
    "writers re-enabled) + S1 smoke 49/49 + S0.5 orders double-scan "
    "0 unacked + DEC/ORD watermarks UNCHANGED + S3 main products: "
    "W193 finalize estate closeout (verify->sec7/sec8 machine "
    "backfill->commit+push 1316ab9e7) + W194 buildgen v2 (v1 in-flight "
    "asserts detonated BY DESIGN per r590 when W192/W193 finalize "
    "landed mid-window; v2 re-derived anchor=W193 actuals 838,945/"
    "422,520/-0.0929/0.245100/0.2957/0.000377/line 1.1873->1.1872/"
    "K-lift -0.0001; REG_N live 194 with band-zero-overlap machine "
    "check; DRY gate 40/40 old-sides count==1; FINPRE needle fixed "
    "drafted-window + n1_w193/ stale semantics; emitted build ran "
    "clean; push e85717ec9) + S6 39 legs rc0 bad NONE (panel 10-08 "
    "pre-market no-new-bar family honest; paper/report/CEO-page legs "
    "rc0) + attrition CLEAN (4 ledgers, 1 pre-existing healed note "
    "588d4c160) + quartet GREEN (loop pin=8 no-op next-fire 07:38 / "
    "watchdog present / precommit+prepush claws match) + "
    "idle_trigger --worked (idle_rounds=0) | verification: smoke "
    "49/49 + W193 four-pred-keys machine PASS + buildgen DRY 40/40 + "
    "banned gate rc0 + S6 bad NONE + attrition CLEAN + orphan face=0 "
    "+ engine ALIVE rc0 + quartet GREEN + local not reaching origin "
    "commit count=0 (post-push fetch+rev-list self-verified) | "
    "scoring: 2 (W193 finalize closeout + W194 prereg = engine "
    "perpetual supply line continuous supply tangible artifacts) | "
    "bookkeeping budget: 5/5 (state + two report lines + heartbeat + "
    "watermark receipts) | treasure capture question: this batch has "
    "no new methods, no new treasures (estate absorption=r899/r902 "
    "verbatim precedent reuse; v1 self-detonation=r590 law by-design "
    "non-pit) TREASURE/METHODOLOGY zero append | orphan_face=0 | "
    "unacked_orders=0 | local_vs_origin=0 | token: L1 zero API "
    "[via bm-a r904]\n")
raw = io.open(REPORT, encoding="utf-8", newline="").read()
eol = "\r\n" if raw.count("\r\n") > (raw.count("\n") - raw.count("\r\n")) \
    else "\n"
assert raw.rstrip().endswith("[via bm-a r902]"), \
    "report tail drift: %r" % raw.rstrip()[-40:]
raw = raw.rstrip("\r\n") + eol + R903_ESTATE + R904_LINE
io.open(REPORT, "w", encoding="utf-8", newline="").write(raw)
print("report: r903 estate + r904 lines appended")

# ---------- 2. state heal 902 -> 904 ----------
ST = "state-bm-a.json"
st = json.load(open(ST, encoding="utf-8"))
assert st.get("round_no") == 902, "unexpected state base: %r" % st.get("round_no")
DID = ("r904: r903 dead-session estate absorption (census no-r903-process "
       "+ workfile 07:02:05 + zero closeout; r899/r902 precedent) + W193 "
       "finalize estate closeout (07:00:46 one-pass product adopted; "
       "ledger 838,945 EXACT; K 422,520; four pred keys PASS; sec7/8 "
       "cross-window backfill; origin 1316ab9e7) + W194 prereg build "
       "window (buildgen v2 anchor rolled to W193 actuals per r590; v1 "
       "detonated by design; DRY 40/40; banned gate rc0; origin "
       "e85717ec9) + S6 39-leg rc0 + quartet green + writer-pause "
       "rebase clean onto bm-c 7f21c3ca8")
NXT = ("r905: W194 five-face freeze window (probe selfcheck re-derive + "
       "N1_BANDS row 194 + WAVE_CONFIGS + materializer + selftest W194 "
       "face + freeze commit -> engine self-ignites W194 burn); 10-09 "
       "15:30 bars -> evening marks chain (REGIME_GUARD enforce + "
       "live.paper + t35/t24 family); pool replenish bm-c lane "
       "F-2026109-01 (window 10-10 00:00); XASSET-ROT P1 ticket pending "
       "GM signature")
VER = ("smoke 49/49 + W193 four pred keys machine PASS + buildgen DRY "
       "40/40 + banned gate rc0 + S6 39-leg bad NONE + attrition CLEAN "
       "(4) + orphan face=0 (23 py faces) + engine ALIVE rc0 idle "
       "queue0 + quartet green (loop pin=8 no-op / watchdog / claws) + "
       "ORD/DEC watermarks UNCHANGED (861949ca/83813196 python-raw) + "
       "orders unacked=0 double-scan + not-at-origin=0")
ART = ("r904 products: results/perpetual_faces/n1_w193_results.json "
       "(origin 1316ab9e7) + research/PERPETUAL_N1_W193_PREREG.md "
       "sec7/sec8 backfilled + research/PERPETUAL_N1_W194_PREREG.md "
       "(origin e85717ec9) + buildgen receipts "
       "(_r904bma_w194_buildgen.py/_r904bma_w194_prereg_build.py)")
NOTES_APPEND = (
    "r904: dead-session estate absorption THIRD instance (r901+r902 "
    "takeover, r903 one-pass) -- finalize provenance separation method: "
    "engine ledger zero-materializer-rows + product mtime inside "
    "session window = session one-pass verdict. r904: r590 anchor-roll "
    "realized in-flight (v1 buildgen in-flight-seat asserts detonated "
    "by design when W192/W193 finalize landed mid-window; v2 = "
    "landed-seat re-derive; FINPRE needle drafted-vs-drafted-window "
    "char defect in never-run v1 caught by DRY gate).")
for k in ("round_no", "round", "loop_round", "last_round"):
    st[k] = 904
for k in ("clock_read", "ts", "updated", "last_seen", "last_round_at",
          "last_run", "last_round_closed", "last_round_ts",
          "last_decisions_at", "last_orders_at"):
    st[k] = NOW
st["did"] = DID
st["last_action"] = "r904 closeout: estate absorb + W193 finalize closeout + W194 prereg build + S6 39-leg + commit/push"
st["now_active"] = ("r904 closed: r903 estate absorbed (W193 finalize "
                    "LANDED origin 1316ab9e7) + W194 prereg build LANDED "
                    "(e85717ec9·anchor=W193 actuals); engine idle queue0 "
                    "awaiting W194 freeze")
st["current"] = st["now_active"]
st["task"] = NXT
st["current_task"] = NXT
st["next"] = NXT
st["next_milestone"] = NXT
st["last_artifact"] = ART
st["latest_artifact"] = ART
st["verify"] = VER
st["heartbeat_epoch_utc"] = EPOCH
st["last_heartbeat_epoch_utc"] = EPOCH
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["last_decisions_seen"] = ("r904 double-scan: DEC 83813196 python-raw "
                             "UNCHANGED (zero action)")
st["last_orders_seen"] = ("r904 double-scan: unacked=0; ORD 861949ca "
                          "python-raw UNCHANGED; tail rows all 10-08, "
                          "zero new BigMoney rows")
st["notes"] = st.get("notes", "") + " " + NOTES_APPEND
st["push_verified"] = {"ts": NOW, "origin_tip": "e85717ec9",
                       "ahead_behind": "0/0",
                       "note": "r904 W194 prereg push verified (estate "
                               "closeout push 1316ab9e7 earlier same "
                               "round; final closeout push follows)"}
st["sync"] = dict(st["push_verified"])
json.dump(st, open(ST, "w", encoding="utf-8"), ensure_ascii=False,
          indent=1)
chk = json.load(open(ST, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert chk["round_no"] == 904
print("state healed 902->904, epoch int self-check PASS")

# ---------- 3. heartbeat ----------
HB = r"fleet\machines\bm-a.json"
hb = json.load(open(HB, encoding="utf-8"))
hb["last_seen"] = NOW
hb["ts"] = NOW
hb["clock_read"] = NOW
hb["current_task"] = NXT
hb["task"] = NXT
hb["next"] = NXT
hb["cpu_cores"] = 32
hb["ram_free_gb"] = 57.6
try:
    it = json.load(open(r"results\idle_trigger.bm-a.json", encoding="utf-8"))
    vram = it.get("vram_free_gb", hb.get("gpu_idle_vram_gb", "n/a"))
except Exception:
    vram = hb.get("gpu_idle_vram_gb", "n/a")
hb["gpu_idle_vram_gb"] = vram
hb["verdict"] = "green"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["heartbeat_epoch_utc"] = EPOCH
hb["last_action"] = st["last_action"]
hb["last_artifact"] = ART
hb["last_decisions_sha"] = "8381319617dd5225cfc144e041ffb1cce94903277fee4219d8e80a24c1dc289a"
hb["last_orders_sha"] = "861949ca7db707d1585edc6379e2ddc461574d0896f08efc499e11fbe3d716bf"
hb["last_decisions_at"] = NOW
hb["last_orders_at"] = NOW
json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk2 = json.load(open(HB, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "hb epoch must be int"
assert "T" in chk2["clock_read"] and " " not in chk2["clock_read"].split("+")[0]
print("heartbeat updated, epoch int + T-sep self-check PASS")
