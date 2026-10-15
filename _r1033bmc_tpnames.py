# -*- coding: utf-8 -*-
import io, re

TP = r"C:\Users\Dasheng\.codely-cli\tmp\e1b4f173cfe4a591921d6662e76a6bbf5f86cdfd3692b53069018f24a422c551\chats\72bb474b-3157-483e-a91f-e01ec9d84d5f.jsonl"
names = {}
for ln, line in enumerate(io.open(TP, encoding="utf-8", errors="replace"), 1):
    for m in re.finditer(r'"name":\s*"([a-z_]+)"', line):
        names.setdefault(m.group(1), []).append(ln)
for k, v in names.items():
    print(k, len(v), v[:8])
