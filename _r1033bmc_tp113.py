# -*- coding: utf-8 -*-
import io, json

TP = r"C:\Users\Dasheng\.codely-cli\tmp\e1b4f173cfe4a591921d6662e76a6bbf5f86cdfd3692b53069018f24a422c551\chats\72bb474b-3157-483e-a91f-e01ec9d84d5f.jsonl"
lines = io.open(TP, encoding="utf-8", errors="replace").read().splitlines()
d = json.loads(lines[112])
print("top keys:", list(d.keys()))
s = json.dumps(d, ensure_ascii=False)
print("line113 len:", len(s))
i = s.find("write_file")
print("write_file ctx:", s[max(0, i - 200):i + 300])
