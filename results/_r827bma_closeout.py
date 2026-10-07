# r827 closeout: state increment + heartbeat + round-report append
# (python single-file fresh read-modify-write, 10-06 multi-writer law)
import json, time, datetime

NOW = datetime.datetime.now().astimezone()
ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2] + ":" + NOW.strftime("%z")[-2:]
EPOCH = int(time.time())

# 1. state-bm-a.json: 825 -> 827 (dead-r826 consumed + own round r827)
with open("state-bm-a.json", encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 827
st["current_task"] = ("W174 finalize adoption closeout DELIVERED (488f56837: ledger 788,212/K 380,720 EXACT, "
                      "K-lift +0.0000, four pre-keys PASS, three-gate PASS; dead-r826 25min-decap estate); "
                      "next: r828 = W175 pre-seat probe + seat MSG chain (post-W174 re-derive MANDATORY)")
st["ts"] = ISO
st["clock_read"] = ISO
st["heartbeat_epoch_utc"] = EPOCH
st["last_round"] = "r827"
st["last_round_at"] = ISO
st["latest_artifact"] = "results/perpetual_faces/n1_w174_results.json + research/PERPETUAL_N1_W174_PREREG.md sec7/sec8 @2026-10-07T14:2x"
with open("state-bm-a.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# 2. heartbeat fleet/machines/bm-a.json
with open("fleet/machines/bm-a.json", encoding="utf-8") as f:
    hb = json.load(f)
hb["round_no"] = 827
hb["last_seen"] = ISO
hb["clock_read"] = ISO
hb["ts"] = ISO
hb["heartbeat_epoch_utc"] = EPOCH
hb["current_task"] = "W174 finalize delivered; next W175 seat chain"
hb["verdict"] = "healthy"
hb["last_action"] = "r827 adoption closeout push 488f56837"
with open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
print("state 827 + heartbeat written; epoch int OK:", EPOCH, ISO)
