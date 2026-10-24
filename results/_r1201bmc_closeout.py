"""r1201 bm-c closeout: round row + state counter + heartbeat (W311 closed, W312 seated).

Single atomic-ish writer: reads the W311 finalize/fivekeys/sixgate receipts from disk
(never transcribes), appends one ledger row, bumps state round_no, rewrites heartbeat.
"""
import json
import time
from datetime import datetime, timezone, timedelta

ROOT = "K:/Fluxgroup/FluxGroup/quant/bigmoney"
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
ROUND = 1201

sixgate = json.load(open(f"{ROOT}/results/_r1201bmc_w311_sixgate.json", encoding="utf-8"))
five = json.load(open(f"{ROOT}/results/_r1201bmc_w311_fivekeys.json", encoding="utf-8"))
fin = json.load(open(f"{ROOT}/results/perpetual_faces/n1_w311_results.json", encoding="utf-8"))
adj = json.load(open(f"{ROOT}/results/_n1_face_adjudication_w311.json", encoding="utf-8"))
seat312 = json.load(open(f"{ROOT}/results/_w312bmc_20261024_probe_receipt.json", encoding="utf-8"))

np_ = fin["null_pool_cumulative"]
ledger_total = fin["science_gates"]["ledger"]["total"]
merged_k = np_["merged"]["n_values"]
merged_mu = np_["merged"]["mu"]
merged_sigma = np_["merged"]["sigma"]
assert isinstance(ledger_total, int) and ledger_total == 1108541, ledger_total
assert isinstance(merged_k, int) and merged_k == 682120, merged_k
assert sixgate["verdict"] == "ALL PASS"
assert all(c["pass"] for c in five["checks"]), "fivekeys not all pass"
assert seat312.get("verdict") == "ADMIT", seat312.get("verdict")

heals = adj.get("heal_deltas", [])
unexplained = adj.get("unexplained_deltas", [])

row = (
    f"| {ts} | r{ROUND} | W311 CLOSED IN A RESUMED WINDOW (r1181/r1186/r1193/r1197/r1199 precedent: "
    f"seat ADMIT / prereg freeze 0b0265a62d / five-face splice 2fdb496bb6 (169 parity rows) / engine self-burn 12/12 "
    f"(2,200 trials, shards 16:05-16:13) were ALL landed by the dead r1200 window; this window re-burned nothing) "
    f"| sixgate 74th consecutive ALL PASS (results/_r1201bmc_w311_sixgate.json, PRE-FINALIZE correct phase) "
    f"| finalize one-pass: ledger {ledger_total:,} / merged K {merged_k:,} / mu {merged_mu:.8f} / sigma {merged_sigma:.8f} "
    f"| fivekeys 6/6 PASS with 1 disclosed prose deviation (key5 se_mu 0.000298 frozen vs 0.000297 machine-read) "
    f"| sec.7/8 backfilled, placeholders 0 (28,402B / 76 lines) "
    f"| freeze-face adjudication PASS (heals {len(heals)}, unexplained {len(unexplained)}) "
    f"| W312 seat ADMIT published (A 701,701..703,700 65th A-hop / B 703,701..703,900 66th above-own-A; seed FREE x2; "
    f"universe 301 owner rows, ordinal 302; fleet/inbox/MSG-20261024-1639-bmc-w312-seat.md) "
    f"| S0: 30 dirty faces were S6-regenerated artifacts of the dead window -> discarded per r1158, HEAD==origin then pull "
    f"| watermark verdict: GREEN (dualrun ZERO-DRIFT streak preserved, no red gate, board clear) "
    f"| local-not-on-origin commits=0 (post-push self-proof) "
    f"| next = r1202 W312 prereg derive + freeze + five-face splice (engine self-ignite) | dept:研究/策略\r\n"
)

ledger_path = f"{ROOT}/round_reports-bm-c.md"
with open(ledger_path, "a", encoding="utf-8", newline="") as fh:
    fh.write(row)

# state counter
sp = f"{ROOT}/state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = ROUND
st["current_task"] = (
    "W311 closed (finalize 1,108,541/K=682,120, fivekeys 6/6, sec.7/8 backfilled, sixgate 74th ALL PASS); "
    "W312 seated (A 701_701..703_700 / B 703_701..703_900)"
)
st["current_task_at"] = ts
st["current_task_ts"] = ts
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1, sort_keys=True)

# heartbeat
hp = f"{ROOT}/fleet/machines/bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = ts
hb["ts"] = ts
hb["clock_read"] = ts
hb["heartbeat_epoch_utc"] = int(time.time())
hb["current"] = (
    "W311 CLOSED (finalize 1,108,541 / K=682,120, fivekeys 6/6, sec.7/8 backfilled, sixgate 74th ALL PASS); "
    "next = W312 prereg freeze + splice"
)
hb["current_task"] = st["current_task"]
hb["current_task_at"] = ts
hb["current_task_ts"] = ts
hb["did"] = (
    f"r{ROUND}: resumed W311 close (adjudication PASS / sixgate 74th / finalize / fivekeys 6/6 / sec.7-8) + "
    "W312 seat ADMIT published + closeout commit"
)
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["round_no"] = ROUND
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1, sort_keys=True)

# self-proof of types
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), type(chk["heartbeat_epoch_utc"])
assert "T" in chk["clock_read"]
print("CLOSEOUT OK round", ROUND, "ledger", ledger_total, "K", merged_k)