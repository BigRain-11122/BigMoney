import json, glob, os

disk = [os.path.basename(f) for f in glob.glob("fleet/orders/O-*.md")]
ack = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))["orders_ack"]
diff = [x for x in disk if x not in ack]
print(f"orders double-scan: disk={len(disk)} ack={len(ack)} unacked={len(diff)} {diff}")
