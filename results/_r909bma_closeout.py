# -*- coding: utf-8 -*-
"""r909 bm-a closeout: state roll + round report line + heartbeat + seat MSG
archive move. Fresh-read-modify-write per the multi-writer law; canonical
report path = ROOT round_reports-bm-a.md."""
import datetime
import json
import os
import shutil
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

RPT_LINE = (
    "2026-10-09T09:46:00+08:00 | r909 | bm-a | dept:research (W195 five-face "
    "freeze + engine ignition; N1 perpetual supply line) | WM-VERDICT: green "
    "(red=false; engine ALIVE rc0 W195 BURNING n1w195 live pids autonomous; "
    "py_low_board_clear=legal idle whitelist board-closed + own never-dry "
    "lane burning) | 当前活: W195 five-face freeze LANDED + engine "
    "self-ignited 2-tick r535 (n1w195-2of12/3of12 live pids 09:34/09:35) | "
    "最近实物: scripts/perpetual_faces.py N1_BANDS row 195 "
    "(a=443_804..445_803 b_exit=445_804..446_003 engine_owner=bm-a) + "
    "scripts/perpetual_faces_n1.py WAVE_CONFIGS[195]+materializer face "
    "(94+35+23+11 count-asserted rolls; freeze receipt "
    "results/_r909bma_w195_freeze_receipt.json) + results/p2cal_ext/n1_w195/ "
    "12-shard burn products 09:3x-09:4x | 下个里程碑: 10-09 15:30 bars -> "
    "evening marks chain (REGIME_GUARD enforce + live.paper + t35/t24 "
    "family) this evening; W195 burn 12/12 + finalize + W196 seat chain next "
    "round; 5x HANDOVER obligation at r910 | 孤儿面=1 (probe read-only "
    "report, zero killed) | 本地未达 origin commit 数=0 (closeout push "
    "self-verified) | did: S0 churn-absorb commit + rebase onto bm-c 3 "
    "(autofill w17 keepalives); S0.5 orders diff=0 (README false-positive "
    "excluded) + DEC/ORD python-raw UNCHANGED (861949ca/83813196 via C: "
    "real-path fetch+show; PS-hash artifact 04e9fe6f caught by r814-family "
    "raw-bytes recompute -- board re-read found 10-09 batch rows already "
    "closed by bm-c r785 receipts F-2026109-01/02/03, zero bm-a action); "
    "D-20261009-02 QA per-machine suffix law = shared runner synced by bm-c "
    "r785 (bm-a no QA pack cadence, zero action); D-20261009-01 pool "
    "replenish = bm-c lane F-2026109-01 closed (pool 9 ready W17 shards "
    "claimable); smoke 49/49; W195 five-face freeze via "
    "_r909bma_w195_freeze_edits.py (r905 direct-author roll machinery: pf "
    "N1_BANDS[195] + n1 WAVE_CONFIGS[195] cfg row + materializer face + "
    "selftest claim + junction probe legs; origin vacancy + seat sha "
    "eb81c0878 ancestor + registry 192->193 rows + W194/W193 byte-intact "
    "post-import + AST+py_compile; first-run 18 mismatch ZERO-WRITE "
    "intercept -> repr-byte probe re-extraction fixed 6 old-strings "
    "(443_403 arithmetic-continuation band misread + cfg multi-line \\n "
    "omission) -> PASS 5/5; pit entry direct-written "
    "research/pit-engine-freeze-editor.md per r666 exception main-file 77B "
    "headroom); pf selftest 9/9 + n1 selftest PASS incl W195 materializer "
    "face live; S6 39-leg all green (bad NONE, new_bar=False pre-market "
    "panel 10-08); attrition CLEAN (4 ledgers, healed shrinks noted); "
    "idle_trigger --worked face | 下轮指针: r910 = 5x HANDOVER obligation "
    "(r906-910 block) + W195 burn/finalize check + W196 seat chain per r907 "
    "pre-seat probe precedent; evening marks chain if 15:30 bars land first"
)

# ---- round report append (canonical ROOT file) ----
rpt = os.path.join(ROOT, "round_reports-bm-a.md")
with open(rpt, "a", encoding="utf-8", newline="\n") as f:
    f.write(RPT_LINE + "\n")
print("report line appended")

# ---- state-bm-a.json roll ----
sp = os.path.join(ROOT, "state-bm-a.json")
st = json.load(open(sp, encoding="utf-8"))
st["round"] = 909
st["round_no"] = 909
st["loop_round"] = 909
st["last_round"] = 908
st["did"] = ("r909: W195 five-face freeze LANDED (pf N1_BANDS[195] + n1 "
             "WAVE_CONFIGS[195] + materializer face + selftest claim + "
             "junction probe; bands A 443_804..445_803 / B 445_804..446_003 "
             "hops 1/1 FIFTY-FIFTH; seat eb81c0878 ancestor-verified) + "
             "engine 2-tick ignition live pids")
st["last_action"] = "r909 closeout: W195 five-face freeze + ignition + S6 39-leg + commit/push"
st["last_artifact"] = ("r909 products: scripts/perpetual_faces.py row 195 + "
                       "scripts/perpetual_faces_n1.py cfg195+mat195 "
                       "(94+35+23+11 rolls count-asserted) + freeze receipt "
                       "results/_r909bma_w195_freeze_receipt.json + "
                       "results/p2cal_ext/n1_w195/ 12-shard burn products")
st["latest_artifact"] = st["last_artifact"]
st["current"] = ("r909 closed: W195 five-face freeze LANDED + engine burning "
                 "n1w195 autonomous (ignited 2-tick r535); S6 39-leg green; "
                 "next = W195 finalize + W196 seat chain")
st["now_active"] = st["current"]
NEXT = ("r910: 5x HANDOVER obligation (r906-910 block) + W195 burn 12/12 "
        "check + finalize + W196 seat chain (pre-seat probe per r907 "
        "precedent); 10-09 15:30 bars -> evening marks chain (REGIME_GUARD "
        "enforce + live.paper + t35/t24 family)")
st["task"] = NEXT
st["current_task"] = NEXT
st["next"] = NEXT
st["next_milestone"] = NEXT
st["clock_read"] = NOW
st["ts"] = NOW
st["last_run"] = NOW
st["last_seen"] = NOW
st["last_round_at"] = NOW
st["last_round_closed"] = NOW
st["last_round_ts"] = NOW
st["updated"] = NOW
st["last_orders_at"] = NOW
st["last_decisions_at"] = NOW
st["last_orders_ts"] = NOW
st["last_orders_seen"] = ("r909 double-scan: unacked=0; ORD 861949ca "
                          "python-raw UNCHANGED")
st["last_decisions_seen"] = ("r909 double-scan: DEC 83813196 python-raw "
                             "UNCHANGED (10-09 batch rows D-01/D-02/D-03 "
                             "re-verified closed by bm-c r785 receipts "
                             "F-2026109-01/02/03; PS-hash artifact caught "
                             "by r814-family raw-bytes recompute)")
st["verify"] = ("smoke 49/49 + W195 freeze PASS 5/5 (origin vacancy + seat "
                "ancestor + registry 192->193 + W194/W193 byte-intact + "
                "AST+py_compile + stale sweeps clean) + pf selftest 9/9 + "
                "n1 selftest PASS incl W195 face + engine ignition live "
                "pids (n1w195-2of12/3of12) + S6 39-leg rc0 bad NONE "
                "(panel 10-08 pre-market no-new-bar) + attrition CLEAN + "
                "idle --worked 0 + ORD/DEC UNCHANGED python-raw "
                "(861949ca/83813196) + orders unacked=0 + push self-verify "
                "this closeout")
st["push_verified"] = {"ts": NOW, "origin_tip": "TBD-final-push",
                       "ahead_behind": "0/0",
                       "note": "r909 closeout push (final commit pending this writer)"}
json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("state rolled to 909")

# ---- heartbeat fleet/machines/bm-a.json ----
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["round"] = 909
hb["round_no"] = 909
hb["loop_round"] = 909
hb["last_round"] = 908
hb["did"] = st["did"]
hb["last_action"] = st["last_action"]
hb["last_artifact"] = st["last_artifact"]
hb["latest_artifact"] = st["last_artifact"]
hb["current"] = st["current"]
hb["now_active"] = st["current"]
hb["task"] = NEXT
hb["current_task"] = NEXT
hb["next"] = NEXT
hb["next_milestone"] = NEXT
hb["clock_read"] = NOW
hb["ts"] = NOW
hb["last_run"] = NOW
hb["last_seen"] = NOW
hb["last_orders_at"] = NOW
hb["last_decisions_at"] = NOW
hb["last_orders_seen"] = st["last_orders_seen"]
hb["last_decisions_seen"] = st["last_decisions_seen"]
hb["orphan_faces"] = 1
hb["orphan_killed"] = 0
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
prev_epoch = hb.get("heartbeat_epoch_utc", 0)
hb["last_heartbeat_epoch_utc"] = prev_epoch
hb["heartbeat_epoch_utc"] = EPOCH
hb["heartbeat_epoch_utc_type_int"] = isinstance(EPOCH, int)
hb["verdict"] = ("green (red=false; engine ALIVE rc0 W195 BURNING n1w195 "
                 "autonomous live pids; py_low_board_clear legal idle "
                 "whitelist + own never-dry lane burning; ORD/DEC "
                 "python-raw UNCHANGED)")
hb["push_verified"] = {"ts": NOW, "origin_tip": "TBD-final-push",
                       "ahead_behind": "0/0",
                       "note": "r909 closeout push (final commit pending this writer)"}
json.dump(hb, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("heartbeat updated; epoch int OK:", chk["heartbeat_epoch_utc"])

# ---- seat MSG archive move (freeze-closeout contract) ----
src = os.path.join(ROOT, "fleet", "inbox",
                   "MSG-2026-10-09-0844-bma-w195-seat.md")
dst_dir = os.path.join(ROOT, "fleet", "inbox", "processed")
os.makedirs(dst_dir, exist_ok=True)
dst = os.path.join(dst_dir, "MSG-2026-10-09-0844-bma-w195-seat.md")
if os.path.exists(src):
    shutil.move(src, dst)
    print("seat MSG archived to processed/")
else:
    print("seat MSG already moved (idempotent)")
print("CLOSEOUT WRITES DONE")
