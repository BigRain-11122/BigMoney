import json
h = json.load(open(r"fleet\machines\bm-c.json", encoding="utf-8"))
print("round_no", h["round_no"])
print("epoch", h["heartbeat_epoch_utc"], type(h["heartbeat_epoch_utc"]).__name__)
print("ack_len", len(h["orders_ack"]))
print("readme_in_ack", "README.md" in h["orders_ack"])
print("clock", h["clock_read"])
