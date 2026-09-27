"""R304 bm-a wrap: state round_no -> 304, heartbeat (epoch int + astimezone
clock_read, r302 law), round report line. Self-verify gate built in."""
import json
import os
import time
from datetime import datetime

now = datetime.now().astimezone()
iso = now.isoformat()
epoch = int(time.time())

# ---- state-bm-a.json
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 304
st["did"] = ("R304: CN_MKTNEUTRAL_P1 runner build DONE per R99 lane (T-87 s2 "
             "queue #5): scripts/cn_mkneutral_p1.py built (prereg 3c71ddb4 "
             "frozen R303 -> runner -> pool; engine zero-touch, FUT_META IC "
             "direct-read) -- selftest 42/42 hermetic (B7b r297 + hedge "
             "machinery asserts: beta OLS/caps/fallback, lots rounding+short "
             "sign, margin gate, blocked/absent exec, roll proxy, NAV "
             "identity vs hand loop, V2 cost twins + x2=2x identity) + "
             "real-data gate PASS (universe 3106 exact, skip ledger == "
             "sector probe shared face, IC 2353 first/last exact, cutoff "
             "truncation 2 bars, joint window 2352d K=118, carry 1d, roll "
             "proxy 47d, 28.9s); POOL SUBMITTED CN-MKTNEUTRAL-P1 ready "
             "single-shard mkneutral-0of1 (shards non-empty r301 law) = "
             "pool-hunger supply per O-1137; T-90/T-89 anti-dup respected "
             "(bm-b owner lanes per yield notes + MSG-0816)")
st["verdict"] = "ok"
st["next"] = ("R305: harvest CN-MKTNEUTRAL-P1 burn when landed (autofill "
              "picks up; done-flip FIRST action r302 law) -> judged readout "
              "G1'v2 own-null + D6 + prereg s5 prediction audit + s7/s8 "
              "backfill + gate_attrition row + SCHOOL row-16 verdict "
              "closure; watch T-90 bm-b prereg v1.1 refreeze flow (MSG-0814 "
              "ruling, GM lane, zero touch from OS loop)")
st["ts"] = iso
st["last_round_ts"] = iso
st["updated_at"] = iso
st["current_task"] = "R304 done: CN_MKTNEUTRAL_P1 runner built + pooled"
st["last_run"] = iso
st["last_round_at"] = iso
st["last_round"] = 303
st["updated"] = iso[:19]
st["last_seen"] = iso
st["task"] = "R305: CN_MKTNEUTRAL harvest (done-flip first)"
json.dump(st, open(sp + ".tmp", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
os.replace(sp + ".tmp", sp)

# ---- heartbeat fleet/machines/bm-a.json
hp = os.path.join("fleet", "machines", "bm-a.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = iso
hb["current_task"] = ("R304 done: CN_MKTNEUTRAL_P1 runner built+selftest "
                      "42/42+real-gate PASS+pool submitted (ready); next R305 "
                      "harvest done-flip first")
hb["heartbeat_epoch_utc"] = epoch          # JSON int (R170/R178 law)
hb["clock_read"] = iso                      # astimezone, T-sep (R262 law)
hb["round_no"] = 304
hb["verdict"] = "ok"
hb["task"] = "R305: CN_MKTNEUTRAL harvest"
json.dump(hb, open(hp + ".tmp", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
os.replace(hp + ".tmp", hp)

# ---- round report line
rp = os.path.join("logs", "iteration-loop", "round_reports-bm-a.md")
line = (
    f"{iso} | R304 bm-a: watermark first-line: insufficient_history->"
    "py_low_board_clear@08:09 (pool submit 08:1x = next probe "
    "py_low_with_work_cands face, supply lane ACTIVE = legal) | "
    "S0.5 both-scans clean (93 orders / 97 acks; decisions.md no new rows "
    "since D-20260927-05) | smoke 25/25 | T-90 collision-resolved "
    "confirmation: bm-b owner (yield notes R303), bm-a lane = CN_MKTNEUTRAL "
    "runner ONLY per anti-dup guard -- honored, zero T-90/T-89 touch | "
    "MAIN: scripts/cn_mkneutral_p1.py built per R99 (frozen 3c71ddb4 -> "
    "runner -> pool; engine zero-touch): selftest 42/42 hermetic (B7b "
    "contract r297 + hedge machinery asserts: beta OLS exact 1.2/caps "
    "1.5+0.5/fallback 2, lots short-sign+rounding, margin budget gate "
    "-10000->-714 unit, blocked +13% open keeps old lots, IC-absent carry, "
    "roll proxy, NAV identity vs independent hand loop ALL-PASS, V2 cost "
    "twins pointwise-equal incl x2=2x) + real-data gate PASS (universe 3106 "
    "EXACT + skip ledger == sector probe shared face + IC 2353 first/last "
    "exact + truncation 2 bars + joint 2352d K=118 carry 1d rollproxy 47d, "
    "28.9s) | kenglu caught by selftest: int() truncation of float Sobol "
    "cap grid (1.25->1) fixed + memory entry | POOL SUBMIT "
    "CN-MKTNEUTRAL-P1 ready shard mkneutral-0of1 non-empty (r301), "
    "autofill picks next tick = pool-hunger supply O-1137 | S6 30/30 rc=0 "
    "(_r304bma_s6_chain.ps1 r300-lineage copy, difflib delta=header-only "
    "per r298; Sunday legal no-bar, collectors honest no-ops, ORANGE_COOL "
    "clock face, astock lane bm-b honest no-op) | inbox: MSG-0757+0816 "
    "bm-b F-04 declarations processed zero-collision (moved processed/); "
    "MSG-0814 GM->bm-b T-90 v1.1 refreeze ruling left for bm-b (addressee "
    "law) | next R305: harvest done-flip FIRST (r302) then judged readout + "
    "s7/s8 + SCHOOL row-16 closure\n")
with open(rp, "a", encoding="utf-8") as fh:
    fh.write(line)

# ---- self-verify gate (r302 law: built-in, pre-commit)
s2 = json.load(open(sp, encoding="utf-8"))
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in h2["clock_read"] and ("+08:00" in h2["clock_read"]
                                    or "-" in h2["clock_read"][10:]), \
    "clock_read must be astimezone ISO with offset"
assert s2["round_no"] == 304
print("wrap ok: round 304 | epoch", epoch, "| clock", iso)
