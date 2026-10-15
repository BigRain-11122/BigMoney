# -*- coding: utf-8 -*-
# inspect r1032 transcript lines mentioning the runner: what tool created it?
import io, json

TP = r"C:\Users\Dasheng\.codely-cli\tmp\e1b4f173cfe4a591921d6662e76a6bbf5f86cdfd3692b53069018f24a422c551\chats\72bb474b-3157-483e-a91f-e01ec9d84d5f.jsonl"
lines = io.open(TP, encoding="utf-8", errors="replace").read().splitlines()
print("total lines:", len(lines))
for n in (78, 80, 81, 83, 84, 86):
    try:
        d = json.loads(lines[n - 1])
    except Exception as e:
        print(n, "PARSE FAIL", e); continue
    def summarize(o, depth=0):
        out = []
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("name",):
                    out.append("name=%s" % v)
                if k in ("file_path", "path", "command", "description") and isinstance(v, str):
                    out.append("%s=%s" % (k, v[:100]))
                if isinstance(v, (dict, list)) and depth < 6:
                    out.extend(summarize(v, depth + 1))
        elif isinstance(o, list):
            for v in o:
                out.extend(summarize(v, depth + 1))
        return out
    print("== line", n, "==")
    for s in summarize(d)[:8]:
        print("  ", s)
