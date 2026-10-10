"""r827 bm-b close-out: state.json + heartbeat load-modify-save (r818 law:
never hand-retype large-list fields like orders_ack) + round-report append."""
import io
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW_ISO = __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")
NOW_EPOCH = int(time.time())

DID = ("r827: T-18 queue-head collision probe FIRST FLEET-LIVE enforcement round: verdict "
       "DECLARED_INTENT_RISK on E6 head (bm-a declared intent, dual-tier capture) -> yielded per "
       "law -> next row E7 claimed (origin heartbeat dual-check clean, claim commit 2bbb0fecb "
       "pushed as lock) -> E7 DELIVERED: scripts/etf_grid_candidates.py (sector-rotation ETF "
       "grid-family candidate scan, selftest 17/17 hermetic; sina list universe 1694 via "
       "ak.fund_etf_category_sina + klc_kl.js direct deep-history x12, EM spot dead on this "
       "machine per r280 family) + evidence results/etf_grid_candidates/{candidates.json, "
       "shortlist.csv, grid_ref.json} + digest research/digests/DIGEST-20261010-e7-etf-grid-"
       "candidates.md; funnel 1694->662 sector->639 ex-core48->622 ex-QDII->225 amount-floor->"
       "top12 deep-probe 0 failures -> PASS_ALL shortlist 4: 515880 comm / 588200 STAR-chip / "
       "159516 semi-equip (vol 0.61-0.70, range 2.9-3.3%, mdd -70~-83% high-vol face) + 159981 "
       "NEV (vol 0.254 closest to incumbent family profile); incumbent 5-cell reference same-"
       "metrics table (511010 itself LOW_VOL honest face); HISTORY_SHORT watch pool 8 (HK-connect "
       "innovative-medicine x3 etc, 2027-window rescan); D6 prereg-time correlation debt "
       "registered; zero judged claim zero prereg; explore.md E7->done + consumption record, P3 "
       "queue 9->8 | S6 41 legs rc0 two-pass (run-1 driver died at GBK console print = pit-"
       "encoding known family, patched sanitize+resume SKIP=7; legs 0-6 rc0 session-console "
       "evidenced); dualrun ZERO-DRIFT streak 12; zt_pool_crosscheck soft-warns strong x dtgc "
       "10-08/10-09 (known face); thermo+DUALARM-2026-09-30 index=BEAR regen; market_clock "
       "ORANGE_COOL; REPORT/LIVE-2026-10-10 regen CEO faces | S7 quartet green: loop pin=2 "
       "no-op; watchdog re-registered logon=default -- verified vs D-20261002-02 decisions.md: "
       "InteractiveToken = documented CEO-authorized exception (S4U 0x80070005 evidence), no "
       "fix needed; claws IN-SYNC; attrition CLEAN 4 ledgers; orders double-sweep 0 unacked; "
       "inbox empty; idle_trigger --worked cleared")

VERDICT = ("r827: product round - E7 sector-rotation ETF grid-candidate scan delivered (T-18 probe "
           "first fleet-live enforcement: E6 DECLARED_INTENT_RISK yielded -> E7 claimed+done; "
           "PASS_ALL shortlist 4/12 with incumbent reference); smoke 49/49; S6 41 legs rc0 "
           "ZERO-DRIFT streak 12; watermark green (py_low_board_clear legal-idle whitelist); "
           "orders 60/60 zero unacked double sweep; DEC/ORD MATCH; attrition CLEAN; orphans=0")

NOW_ACTIVE = "r827: E7 sector-rotation ETF grid-candidate scan delivered + T-18 probe first fleet-live enforcement (E6 yielded to bm-a per probe)"
LATEST_ARTIFACT = ("r827: scripts/etf_grid_candidates.py (selftest 17/17) + results/etf_grid_candidates/"
                   "{candidates.json,shortlist.csv,grid_ref.json} + research/digests/DIGEST-20261010-e7-etf-grid-candidates.md, 2026-10-10 10:2x")
NEXT_MILESTONE = ("r828+: E8 explore head (futures calendar-spread face, claim via T-18 probe only) + "
                  "W18 drafting window once W17-JUDGE drains (bm-c pinned lane); Monday 2026-10-12 09:15 "
                  "minute_feed first gated run backfills 10-08/10-09")
CURRENT_TASK = ("r828: E6 stays bm-a's (probe DECLARED_INTENT_RISK); next claimable explore row E8 "
                "(commodity futures calendar-spread face) -- run T-18 probe before claiming; W17 "
                "drain watch (bm-c lane-pinned checkpoint locality r429, pool tick alive 08:29); "
                "Monday 2026-10-12 09:15 minute_feed first gated run backfills 10-08/10-09")
LAST_ACTION = "r827: E7 scan delivered (4-candidate shortlist + incumbent reference) + S6 41 legs rc0 + S7 quartet green"


def save(path, obj):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


# --- state.json (bm-b carrier) ---
sp = os.path.join(ROOT, "state.json")
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 827
st["round"] = 825
st["round_no_label"] = "r827"
st["note"] = VERDICT
st["did"] = DID
st["verdict"] = VERDICT
st["current_task"] = CURRENT_TASK
st["next"] = CURRENT_TASK
st["now_active"] = NOW_ACTIVE
st["latest_artifact"] = LATEST_ARTIFACT
st["next_milestone"] = NEXT_MILESTONE
st["task"] = CURRENT_TASK
st["last_action"] = LAST_ACTION
for k in ("last_round_at", "ts", "updated_at", "last_seen", "clock_read", "last_round_ts", "updated_at"):
    st[k] = NOW_ISO
st["last_decisions_read_at"] = NOW_ISO
st["last_orders_read_at"] = NOW_ISO
save(sp, st)

# --- heartbeat fleet/machines/bm-b.json ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
h = json.load(io.open(hp, encoding="utf-8"))
h["round"] = 826
h["round_no"] = 827
h["now_active"] = NOW_ACTIVE
h["current_task"] = CURRENT_TASK
h["task"] = CURRENT_TASK
h["latest_artifact"] = LATEST_ARTIFACT
h["next_milestone"] = NEXT_MILESTONE
h["verdict"] = VERDICT
h["last_action"] = LAST_ACTION
for k in ("last_round_at", "last_seen", "updated", "ts", "clock_read", "updated_at"):
    h[k] = NOW_ISO
h["heartbeat_epoch_utc"] = NOW_EPOCH
assert isinstance(h["heartbeat_epoch_utc"], int)
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["orphan_faces"] = 0
h["orphan_face_note"] = "r827: orphan probe 16 py faces, 0 orphans"
h["sync"] = {"ahead": 0, "behind": 0, "last_push_ts": NOW_ISO,
             "note": "r827: E7 claim commit 2bbb0fecb early lock-push + round commit push self-proof post-push"}
# orders_ack list + count: UNTOUCHED (sweep clean, zero new)
save(hp, h)

# re-verify epoch int face
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("close-out written:", NOW_ISO, "epoch", NOW_EPOCH)
