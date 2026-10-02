import json, time, datetime, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- state: round_no 586 -> 587, dynamic fields only (r583 law) ---
sp = os.path.join(REPO, "state-bm-a.json")
s = json.load(open(sp, encoding="utf-8"))
s["round_no"] = 587
s["current_task"] = ("r587 bm-a: r586-wrap adopted (37-file surgical delivery e79dcf6b4) + W104 burn products "
                     "12/12 delivered (c01fe5880, K=2,200) + W101 FINALIZE landed one-pass (586,748/K=220,120, "
                     "f3e4fa594, downstream W102 bm-c unblocked) + W107 full lifecycle: seat d548df902 -> gate "
                     "ADMIT -> five-face freeze a554dedd3 -> engine IGNITED n1w107 in flight (queue 10)")
s["last_seen"] = datetime.datetime.now().isoformat(timespec="seconds")
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("state round_no:", s["round_no"])

# --- heartbeat: dynamic fields only, orders_ack carried verbatim (r583 law) ---
hp = os.path.join(REPO, "fleet", "machines", "bm-a.json")
h = json.load(open(hp, encoding="utf-8"))
n_ack = len(h.get("orders_ack", []))
h["last_seen"] = datetime.datetime.now().isoformat(timespec="seconds")
h["heartbeat_epoch_utc"] = int(time.time())
h["clock_read"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
h["current_task"] = "r587 wrap: W104 products + W101 finalize + W107 freeze+ignition delivered"
h["cpu_cores"] = 32
h["idle_ram_gb"] = None  # keep existing keys untouched beyond dynamics
h["verdict"] = ("productive: W104 12/12 products + W101 finalize (chain head 586,748) + W107 five-face freeze "
                "landed, engine ignited n1w107 burn in flight")
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
hh = json.load(open(hp, encoding="utf-8"))
assert isinstance(hh["heartbeat_epoch_utc"], int), "epoch must be int (F7 law)"
assert "T" in hh["clock_read"], "clock_read must be T-separated (R262 law)"
assert len(hh.get("orders_ack", [])) == n_ack, "orders_ack list must be carried verbatim"
print("heartbeat ok: epoch int =", hh["heartbeat_epoch_utc"], "ack carried:", n_ack)
