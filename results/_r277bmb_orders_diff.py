import json
ack = set(json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))["orders_ack"].split())
import os
files = set(f for f in os.listdir("fleet/orders") if f.endswith(".md") and f.startswith("O-"))
print("files", len(files), "ack", len(ack))
print("UNACKED:", sorted(files - ack))
print("ACK-WITHOUT-FILE:", sorted(ack - files))
