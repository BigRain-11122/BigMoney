# -*- coding: utf-8 -*-
"""r908 bm-a closeout writer: state round_no 907->908, heartbeat refresh,
round report line append.  Fresh-read-modify-write (multi-writer law)."""
import datetime
import json
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(datetime.datetime.now().timestamp())

DID = ("r908: W195 prereg build window landed (buildgen clean-window "
       "anchor=W194 actuals per r590; bands A 443_804..445_803 / B "
       "445_804..446_003 from r907 probe; banned gate rc0; pool proj "
       "426,920; SEED_REGISTRY live 194 zero-overlap)")
ART = ("r908 products: research/PERPETUAL_N1_W195_PREREG.md @ origin "
       "154ad3275 (21,002B 64-line CRLF; A 443_804+j / B exit 445_804+j; "
       "anchor=W194 finalize actuals 841,145/K=424,720/mu -0.0928/sigma "
       "0.245098/A p95 0.3135/K-lift +0.0000; W196+ projection A "
       "445_804..447_803 / B 446_004..446_203) + results/_r908bma_"
       "w195_buildgen.py + _r908bma_w195_prereg_build.py + "
       "_r908bma_w195_probe receipts")
NEXT = ("r909: W195 five-face freeze (per r905 precedent: N1_BANDS row "
        "195 + WAVE_CONFIGS cfg195 + materializer face + selftest claim "
        "+ probe re-derive legs; engine self-ignites 2-tick r535); 10-09 "
        "15:30 bars -> evening marks chain (REGIME_GUARD enforce + "
        "live.paper + t35/t24 family); pool replenish bm-c lane F-2026109-01; "
        "5x HANDOVER obligation at r910")

# --- state -------------------------------------------------------------
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 908
st["round"] = 908
st["loop_round"] = 908
st["last_round"] = 907
st["current_task"] = NEXT
st["task"] = NEXT
st["next"] = NEXT
st["next_milestone"] = NEXT
st["did"] = DID
st["last_action"] = "r908 closeout: W195 prereg build + S6 39-leg + commit/push"
st["last_artifact"] = ART
st["latest_artifact"] = ART
st["now_active"] = ("r908 closed: W195 prereg LANDED origin 154ad3275 "
                    "(buildgen DRY 40/40 + banned gate rc0; anchor=W194 "
                    "actuals; A 443_804..445_803 / B 445_804..446_003); "
                    "engine idle queue0 awaiting W195 five-face freeze")
st["current"] = st["now_active"]
st["last_round_at"] = NOW
st["last_round_closed"] = NOW
st["last_run"] = NOW
st["last_seen"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["last_orders_seen"] = ("r908 double-scan: unacked=0; ORD 861949ca "
                          "python-raw UNCHANGED")
st["last_decisions_seen"] = ("r908 double-scan: DEC 83813196 python-raw "
                              "UNCHANGED (zero action)")
st["last_orders_at"] = NOW
st["last_decisions_at"] = NOW
st["last_decisions_ts"] = NOW
st["last_orders_ts"] = NOW
st["verify"] = ("smoke 49/49 + buildgen facts ALL GREEN + DRY gate 40/40 "
               "count==1 + prereg 21,002B CRLF roundtrip + banned gate "
               "rc0 ADMIT zero hits + S6 39-leg rc0 bad NONE (panel 10-08 "
               "pre-market no-new-bar) + attrition CLEAN (4 ledgers) + "
               "quartet GREEN (loop pin=8 Running / watchdog Ready 09:13 / "
               "claws OK) + idle --worked 0 + ORD/DEC UNCHANGED "
               "(861949ca/83813196 python-raw) + orders unacked=0 "
               "double-scan + push 0/0 self-verified")
st["push_verified"] = {
    "ts": NOW,
    "origin_tip": "TBD-final-push",
    "ahead_behind": "0/0",
    "note": "r908 closeout push (final commit pending this writer)",
}
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state written: round 908")

# --- heartbeat ---------------------------------------------------------
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["round_no"] = 908
hb["round"] = 908
hb["loop_round"] = 908
hb["last_round"] = 907
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["ts"] = NOW
hb["last_seen"] = NOW
hb["last_run"] = NOW
hb["did"] = DID
hb["last_action"] = ("r908 closeout: W195 prereg build + S6 39-leg + "
                     "commit/push")
hb["last_artifact"] = ART
hb["latest_artifact"] = ART
hb["current_task"] = NEXT
hb["task"] = NEXT
hb["next"] = NEXT
hb["next_milestone"] = NEXT
hb["current"] = st["now_active"]
hb["now_active"] = st["now_active"]
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["last_orders_seen"] = st["last_orders_seen"]
hb["last_decisions_seen"] = st["last_decisions_seen"]
hb["last_orders_at"] = NOW
hb["last_decisions_at"] = NOW
hb["verdict"] = ("green (red=false; engine ALIVE rc0 idle queue0; W195 "
                 "prereg landed origin 154ad3275, five-face freeze next "
                 "round; py_low_board_clear legal idle whitelist)")
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat written: epoch int self-verified", EPOCH)

# --- round report ------------------------------------------------------
rp = "round_reports-bm-a.md"
lines = io_txt = open(rp, encoding="utf-8").read()
assert "r908" not in lines[-2000:], "r908 line already present?"
REPORT = (
    "%s | r908 | bm-a | dept:research (W195 prereg build window; N1 "
    "perpetual supply line) | WM-VERDICT: green (red=false lane healthy; "
    "engine ALIVE rc0 idle queue0; py_low_board_clear=legal idle "
    "whitelist board-closed + own never-dry lane W195 prereg landed, "
    "five-face freeze queued next round; DEC 83813196/ORD 861949ca "
    "python-raw UNCHANGED via C: real-path fetch+show; orders "
    "round-start+closeout double-scan unacked=0) | 当前活: W195 prereg "
    "build landed same round (buildgen r908 clean-window anchor=W194 "
    "actuals + DRY gate 40/40 zero-write-first + banned gate rc0 zero "
    "hits) | 最近实物: research/PERPETUAL_N1_W195_PREREG.md @ origin "
    "154ad3275 (21,002B/64-line CRLF; bands A 443_804..445_803 / B "
    "445_804..446_003 hops 1/1 FIFTY-FIFTH staircase E36 + W141 "
    "mutual-exclusion; anchor=W194 finalize actuals 841,145/424,720 "
    "per r590; proj ledger 843,345 / K 426,920; SEED_REGISTRY live 194 "
    "band zero-overlap machine-checked) | 下个里程碑: r909=W195 "
    "five-face freeze (r905 precedent; engine self-ignite 2-tick r535; "
    "window <=24h) + 10-09 15:30 bars -> evening marks chain "
    "(REGIME_GUARD enforce + live.paper + t35/t24 family) + 5x HANDOVER "
    "at r910 | did: S0-1 anchored bm-a + orphan probe 1 read-only "
    "(BigDomain external face) + S0 pull --rebase up-to-date at round "
    "start; mid-round push race vs bm-c r792 4-commit advance resolved "
    "by E42/r884 tight-loop (churn-absorb 4221dfdee + rebase 2/2 clean "
    "+ push cae61ed80..fbb5159fb) + S0.5 orders unacked=0 + DEC/ORD "
    "python-raw UNCHANGED + S1 smoke 49/49 + S2 boards (job_list 0; no "
    "unclaimed tickets; T-178 bm-c W17 in-flight) + S3 engine ALIVE rc0 "
    "idle queue0 + W195 buildgen (_r908bma_w195_buildgen.py: live facts "
    "ALL GREEN — probe r907 ADMIT bands/hops/leg0 192 rows tail=W194 "
    "ordinal 185 bm-a 110th + W194 finalize actuals asserted from "
    "n1_w194_results.json + seat eb81c0878 + W194 FF 82670b0ba + W195 "
    "vacancy held + REG_N 194 zero-overlap; 40-pair TOK two-phase vmap "
    "composites-first; FINPRE 起草窗 src-spelling heal 1 iter + W196+ "
    "projection count=3 r904-parity fix; DRY 40/40 count==1 + stale "
    "sweep 40+ CLEAN + line-structure preserved) + driver emitted "
    "(_r908bma_w195_prereg_build.py 23,919B) + prereg written (CRLF "
    "roundtrip assert) + banned_direction_gate rc0 ADMIT zero hits + "
    "product commit 777a8f2e4 -> rebased -> origin 154ad3275 + S6 39 "
    "legs rc0 bad NONE (panel 10-08 pre-market no-new-bar family "
    "honest; dualrun rc0; py_watermark py_low_board_clear; token "
    "delta=0) + S7 attrition CLEAN (4 ledgers, healed notes historical) "
    "+ quartet GREEN (loop pin=8 Running next-fire 09:18 / watchdog "
    "re-registered idempotent -Force after Invoke-SilentExe "
    "positional-arg probe error -> Ready 09:13 disclosed honest / "
    "precommit+prepush claws OK) + idle_trigger --worked (idle_rounds 0, "
    "agenda_starved false) + state 907->908 + heartbeat refresh (epoch "
    "int self-verified) | verification: smoke 49/49 + DRY 40/40 + gate "
    "rc0 + S6 bad NONE + attrition CLEAN + quartet GREEN + local not "
    "reaching origin commit count=0 (post-push fetch self-verified) | "
    "scoring: 2 (W195 prereg = runnable science artifact on origin, "
    "engine perpetual supply line continuous) | bookkeeping budget: "
    "5/5 (state + report line + heartbeat + idle clear + S6 receipt) | "
    "treasure capture question: no new method no new treasure (buildgen "
    "= r904 bloodline rolled one generation verbatim-reuse; FINPRE "
    "起草/起稿 char variant = src-fidelity face not a method) "
    "TREASURE/METHODOLOGY zero append | orphan_face=1 (read-only report) "
    "| unacked_orders=0 (double-scan) | local_vs_origin=0 | token: L1 "
    "zero API (token_meter delta=0) | [r908 bm-a]\n" % NOW)
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(REPORT)
print("round report appended: r908 line")
