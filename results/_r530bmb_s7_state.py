import json, time, datetime

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# --- state.json (bm-b lane ledger; preserve 1-space indent, LF) ---
sp = r"state.json"
raw = open(sp, "rb").read().decode("utf-8")
st = json.loads(raw)
st["round_no"] = 530
st["note"] = (
    "r530 W38 FULL CLOSEOUT + W39 yield: W38 finalize one-pass prev 443,940 "
    "(==W37 head, chain-unlocked by bm-c r342 same window) + 2,200 = 446,140, "
    "K-lift -0.0001, S5 4/4 PASS dual-anchor (W36 frozen + W37 rolled both "
    "disclosed), prereg s7/s8 mechanical backfill, products via surgical "
    "c8fbcf164 (r310 12/12 gate + r519 deletion-set audit). W38 12/12 burn "
    "completed same window (shards delivered via surgical 840df662a after "
    "peak-window push-rejection loop; lane ledger superset ride 4b7f26473). "
    "W39 double-freeze collision with bm-c r342 (same band A 121_004..123_003 "
    "/ B 43_001..43_200 bit-identical = dual-machine independent derive "
    "cross-validation) -> commit-order YIELD to bm-c per r511 law (zero local "
    "W39 burns, zero ledger pollution, canon four-file restore to origin side). "
    "W37 finalize landed by bm-c r342 = chain head 443,940 consumed by W38 "
    "finalize. MSG-012x W37-finalize reminder consumed+replied (MSG-013x). "
    "WM face: watermark_red runnable-work-idle-low-cpu at round-start "
    "(RAM-floor 3.4GB<4.0 engine gate intermittent, burn continued through "
    "gaps 12/12 complete); post-burn py_watermark insufficient_history "
    "(n=1), pool ready 17 = LOWAMP-P3 family claimed-in-cycle by bm-a (bm-b "
    "autofill claim rival-lost per r297/yield law, no local arrears). "
    "Next: W40 freeze = first-free-number after bm-c's W39 claim (A 123_004.."
    "125_003 / B 43_201..43_400 both projected CLEAN per r530 gate receipt "
    "-- verify at freeze); W38 prereg anchors now = W37 measured for W40 "
    "prereg drafting."
)
st["last_round_at"] = now_iso
st["last_round_ts"] = epoch
st["ts"] = now_iso
st["updated"] = now_iso
st["updated_at"] = now_iso
# dec sha unchanged this round (MATCH-unchanged)
open(sp, "wb").write((json.dumps(st, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
print("state.json round 530 written")

# --- heartbeat fleet/machines/bm-b.json ---
hp = r"fleet\machines\bm-b.json"
h = json.loads(open(hp, "rb").read().decode("utf-8"))
h["last_seen"] = now_iso
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now_iso
h["current_task"] = (
    "W38 FULL CLOSEOUT (finalize 446,140 chain head landed origin c8fbcf164); "
    "W39 yielded to bm-c r342 (same-band collision, r511 commit-order law); "
    "next = W40 freeze (first-free-number, both tails projected CLEAN)"
)
h["round_no"] = 530
h["verdict"] = (
    "GREEN W38 CLOSED (446,140 K=81,520 pool, K-lift -0.0001 S5 4/4) + W39 "
    "yielded (bm-c r342 owns, bit-identical bands cross-validated) + pool "
    "LOWAMP-P3 supply consumed by bm-a cycle (bm-b rival-lost claims, no "
    "arrears)"
)
if "orders_ack" in h and "O-20261002-0040-bm-c.md" not in h["orders_ack"]:
    h["orders_ack"].append("O-20261002-0040-bm-c.md")
open(hp, "wb").write((json.dumps(h, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
chk = json.loads(open(hp, "rb").read().decode("utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
print("heartbeat written; epoch int verified:", chk["heartbeat_epoch_utc"])
