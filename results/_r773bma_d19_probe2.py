# -*- coding: utf-8 -*-
"""r773 D-19 probe2: extract group-repo decisions.md + orders.md rows newer than
the 09:22 consumption watermark; classify BigMoney-relevant lines."""
import re
import subprocess

GRP = r"C:\Users\sjs20\Desktop\FluxGroup"
CREAT = 0x08000000


def show(path):
    return subprocess.run(["git", "-C", GRP, "show", f"origin/main:{path}"],
                          capture_output=True, creationflags=CREAT
                          ).stdout.decode("utf-8", errors="replace")

dec = show("docs/decisions.md")
ordr = show("docs/orders.md")
# rows mentioning 10-06 with times >= 09:22 or any undated-new markers
def recent_rows(text, label):
    print(f"=== {label} rows mentioning 10-06 ===")
    for ln in text.splitlines():
        if "10-06" in ln or "10-05 2" in ln:
            t = ln.strip()
            print(" *", t[:200])
recent_rows(dec, "decisions.md")
print()
# BigMoney dispatch-board rows in decisions.md
print("=== decisions.md rows mentioning BigMoney/量化 ===")
seen = 0
for ln in dec.splitlines():
    if ("BigMoney" in ln or "量化" in ln) and ("10-06" in ln or "10-05" in ln):
        print(" *", ln.strip()[:260])
        seen += 1
        if seen > 8:
            break
print()
print("=== orders.md rows 10-05 2x / 10-06 (post-0922 candidates) ===")
for ln in ordr.splitlines():
    s = ln.strip()
    if re.match(r"\|\s*10-0[56]", s):
        print(" *", s[:230])
