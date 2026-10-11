import json
p = "state-bm-c.json"
s = json.load(open(p, encoding="utf-8"))
s["last_decisions_sha"] = "31e219a914c256ba6be82f0ae48576b06c6aeafc1c009474fda61b8a5532e97c"
json.dump(s, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("watermark updated:", s["last_decisions_sha"][:16])
print("round_no:", s.get("round_no"))
