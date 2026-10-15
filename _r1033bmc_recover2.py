# -*- coding: utf-8 -*-
import io, json

TP = r"C:\Users\Dasheng\.codely-cli\tmp\e1b4f173cfe4a591921d6662e76a6bbf5f86cdfd3692b53069018f24a422c551\chats\72bb474b-3157-483e-a91f-e01ec9d84d5f.jsonl"
lines = io.open(TP, encoding="utf-8", errors="replace").read().splitlines()

def walk(o, found):
    if isinstance(o, dict):
        if o.get("name") == "write_file" and isinstance(o.get("input"), dict):
            inp = o["input"]
            found.append((inp.get("file_path") or inp.get("path"), len(str(inp.get("content", ""))), inp.get("content", "")))
        for v in o.values():
            walk(v, found)
    elif isinstance(o, list):
        for v in o:
            walk(v, found)

for n in (113, 119):
    d = json.loads(lines[n - 1])
    found = []
    walk(d, found)
    for fp, cl, content in found:
        print("line", n, "file:", fp, "content_len:", cl)
        if "jayredo" in str(fp) and cl > 5000:
            out = r"K:\Fluxgroup\FluxGroup\media\MV\mv0001\jayredo\jayredo_v4_r1032_RECOVERED.py"
            io.open(out, "w", encoding="utf-8", newline="").write(content)
            print("RECOVERED ->", out, cl, "bytes")
