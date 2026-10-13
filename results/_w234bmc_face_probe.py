# -*- coding: utf-8 -*-
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")
r = json.load(open(r"results\_w234bmc_20261013_probe_receipt.json", encoding="utf-8"))
print("LEG4:", json.dumps(r["legs"]["leg4"], ensure_ascii=False))
print("LEG0 note:", r["legs"]["leg0"]["bmc_ordinal_note"][:130])
print("bands:", r.get("bands"), "| verdict:", r.get("verdict"))
t = open(r"results\_w234bmc_base_face.txt", encoding="utf-8").read()
for pat in ["注册后将拒", "splice", "pre-W233 宇宙", "波号 233=", "W232 **0.000344**】", "W231 **0.000344**】",
            "r968 freeze receipt", "第 63 枚 EXACT", "A base=527404", "n1_w232/ 分片计数增长",
            "batch_name=", "line_merged@K", "K=508,320", "508,320+2,200", "净账本锚头",
            "pre-W233", "W233 freezer 承接面", "engine_owner==bm-c 62 行"]:
    hits = [m.start() for m in re.finditer(re.escape(pat), t)]
    print(f"[{pat}] x{len(hits)}")
    for h in hits[:2]:
        print("   ...", t[max(0,h-70):h+len(pat)+50].replace("\n", " | "))
