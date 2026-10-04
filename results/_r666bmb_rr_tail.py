# -*- coding: utf-8 -*-
# r666 bm-b round-reports tail reader: mixed-encoding file -> try utf-8 then gbk per line, write UTF-8 out
import io

lines = io.open(r"logs\iteration-loop\round_reports.md", "rb").read().split(b"\n")
out = io.open(r"results\_r666bmb_rr_tail.txt", "w", encoding="utf-8")
for l in lines[-16:]:
    for enc in ("utf-8", "gbk"):
        try:
            s = l.decode(enc)
            break
        except UnicodeDecodeError:
            s = l.decode("utf-8", "replace")
    out.write(s[:400] + "\n")
out.close()
print("written", len(lines))
