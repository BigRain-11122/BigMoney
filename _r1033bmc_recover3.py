# -*- coding: utf-8 -*-
import io, json

TP = r"C:\Users\Dasheng\.codely-cli\tmp\e1b4f173cfe4a591921d6662e76a6bbf5f86cdfd3692b53069018f24a422c551\chats\72bb474b-3157-483e-a91f-e01ec9d84d5f.jsonl"
lines = io.open(TP, encoding="utf-8", errors="replace").read().splitlines()

for n in (113, 119):
    d = json.loads(lines[n - 1])
    for tc in d.get("msg", {}).get("toolCalls", []):
        if tc.get("name") == "write_file":
            args = tc.get("args", {})
            fp = args.get("file_path") or args.get("path") or "?"
            c = args.get("content") or ""
            print("line", n, "file:", fp, "len:", len(c))
            if "jayredo_v4_r1032" in str(fp) and len(c) > 5000:
                out = r"K:\Fluxgroup\FluxGroup\media\MV\mv0001\jayredo\jayredo_v4_r1032_RECOVERED.py"
                io.open(out, "w", encoding="utf-8", newline="").write(c)
                print("RECOVERED ->", out)
