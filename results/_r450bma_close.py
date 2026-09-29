"""r450 bm-a close: state bump + heartbeat + round report append."""
import json
import time
from datetime import datetime

NOW = datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

# --- state-bm-a.json: round_no +1 ---
with open("state-bm-a.json", encoding="utf-8") as fh:
    st = json.load(fh)
st["round_no"] = 451
st["did"] = ("r450(-close): dead-tick adoption r240 law (23:44-23:58 killed pre-S7) -- "
             "A13 duplicate-burn incident: fail-closed single-shot guard installed in "
             "t101_v4_a13_predface runner (selftest 9 legs); stale-blob repair clobbered "
             "lane ledger (-4 entries A10-A13 vs HEAD) caught by S7 guard rc1, restored "
             "byte-identical from HEAD blob (zero worktree-unique keys, rescan CLEAN); "
             "r450 S6 37-leg 09-29 chain products adopted; W12 rsqr-berth MSG processed")
st["verify"] = ("smoke 26/26; orders 122/122 diff 0; attrition guard rescan CLEAN x4 "
                "(historical shrinks [healed]); ledger worktree==HEAD byte-identical; "
                "A13 guard diff reviewed + selftest leg9 adopted; epoch int")
st["next"] = ("r451+: (a) fresh S6 chain 09-30 date rollover (r450 chain adopted, not rerun); "
              "(b) W11 verdict watch / W12 adoption freeze window; (c) 10-01 month trio + "
              "REGIME_GUARD v3 hands-off; (d) 16 root cloud-sync conflict copies = CEO-physical "
              "(untracked per r443 discipline); (e) update_lhb chronic source-restated watch")
st["last_round_at"] = NOW
st["current_task"] = ("r450 closed: dead-tick adoption + lane ledger byte restore + A13 "
                     "single-shot guard landed; next = 09-30 fresh S6 chain + W12 freeze + 10-01 trio")
st["updated"] = NOW
with open("state-bm-a.json", "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)

# --- heartbeat fleet/machines/bm-a.json ---
hp = "fleet/machines/bm-a.json"
with open(hp, encoding="utf-8") as fh:
    hb = json.load(fh)
hb["last_seen"] = NOW
hb["verdict"] = "healthy"
hb["current_task"] = st["current_task"]
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
with open(hp, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)

# --- round report ---
wm = "n/a"
try:
    with open("results/watermark.jsonl", encoding="utf-8") as fh:
        for ln in fh:
            if ln.strip():
                last = ln
        wm = json.loads(last).get("verdict", "n/a")
except Exception as exc:
    wm = "unreadable(%s)" % exc.__class__.__name__

line = (f"{NOW} | r450(-close) | WM={wm}: dead-tick adoption (23:44-23:58 killed pre-S7, "
        "r240 law): A13 incident guard installed+adopted (fail-closed single-shot, selftest 9), "
        "stale-blob lane-ledger clobber (-4 A10-A13) caught by S7 guard rc1 -> HEAD-blob byte "
        "restore rescan CLEAN; r450 S6 37-leg 09-29 products adopted (chain not rerun this close-tick); "
        "W12 rsqr-berth MSG processed; HANDOVER 5x + r450 memory adopted; 16 root conflict copies "
        "left untracked (r443 discipline) | smoke 26/26 + orders 122/122 + guard CLEAN x4 + ledger "
        "worktree==HEAD byte-identical | next: 09-30 fresh S6 chain + W12 freeze window + 10-01 trio\n")
with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8") as fh:
    fh.write(line)

# --- self-verify epoch int ---
assert isinstance(json.load(open(hp, encoding="utf-8"))["heartbeat_epoch_utc"], int), "epoch must be int"
print(f"closed: round_no=451 epoch={EPOCH} clock={NOW} wm={wm}")
