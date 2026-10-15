# -*- coding: utf-8 -*-
# r1033 recovery: extract original jayredo_v4_r1032.py content from r1032 session transcript
import io, json, sys

TP = r"C:\Users\Dasheng\.codely-cli\tmp\e1b4f173cfe4a591921d6662e76a6bbf5f86cdfd3692b53069018f24a422c551\chats\72bb474b-3157-483e-a91f-e01ec9d84d5f.jsonl"
best = None
for ln, line in enumerate(io.open(TP, encoding="utf-8", errors="replace"), 1):
    if "jayredo_v4_r1032.py" not in line:
        continue
    if '"content"' not in line and "write" not in line.lower():
        continue
    try:
        d = json.loads(line)
    except Exception:
        continue
    s = json.dumps(d, ensure_ascii=False)
    # walk for tool_use blocks containing write_file with file_path jayredo_v4_r1032.py
    def walk(o):
        global best
        if isinstance(o, dict):
            if o.get("name") in ("write_file", "write") and isinstance(o.get("input"), dict):
                inp = o["input"]
                fp = str(inp.get("file_path", "")) + str(inp.get("path", ""))
                if "jayredo_v4_r1032.py" in fp and inp.get("content"):
                    if best is None or len(inp["content"]) > len(best[0]):
                        best = (inp["content"], ln, inp.get("file_path") or inp.get("path"))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(d)
if best:
    content, ln, fp = best
    print("FOUND line %d path=%s len=%d" % (ln, fp, len(content)))
    out = r"K:\Fluxgroup\FluxGroup\media\MV\mv0001\jayredo\jayredo_v4_r1032_RECOVERED.py"
    io.open(out, "w", encoding="utf-8", newline="").write(content)
    print("written:", out)
else:
    print("NO write_file content found")
    sys.exit(2)
