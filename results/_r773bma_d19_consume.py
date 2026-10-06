# -*- coding: utf-8 -*-
"""r773 D-19 dual consumption (group-tree real-path fallback per D-20261004-02③;
byte-exact python subprocess hash per r583/r760 law -- zero PS pipeline)."""
import hashlib
import json
import subprocess

GRP = r"C:\Users\sjs20\Desktop\FluxGroup"
CREAT = 0x08000000

subprocess.run(["git", "-C", GRP, "fetch", "origin"], capture_output=True,
               creationflags=CREAT)


def blob_sha(path):
    out = subprocess.run(["git", "-C", GRP, "show", f"origin/main:{path}"],
                          capture_output=True, creationflags=CREAT).stdout
    return hashlib.sha256(out).hexdigest(), out


dec_sha, dec_bytes = blob_sha("docs/decisions.md")
ord_sha, ord_bytes = blob_sha("docs/orders.md")
s = json.load(open("state-bm-a.json", encoding="utf-8"))
print("decisions:", dec_sha[:8], "== watermark" if dec_sha == s["last_decisions_sha"] else "CHANGED vs " + s["last_decisions_sha"][:8])
print("orders:   ", ord_sha[:8], "== watermark" if ord_sha == s["last_orders_sha"] else "CHANGED vs " + s["last_orders_sha"][:8])

# consume new rows: the O-20261006-1207 order line + any newer lines
ord_text = ord_bytes.decode("utf-8", errors="replace")
i = ord_text.find("O-20261006-1207")
print("--- O-20261006-1207 group-repo row ---")
print(ord_text[max(0, i - 80):i + 900] if i >= 0 else "ROW NOT FOUND")
# tail scan: lines newer than the last consumed watermark timestamp
print("--- orders.md last 3 rows ---")
rows = [r for r in ord_text.splitlines() if r.strip().startswith("|") or r.strip().startswith("- ") or "O-2026" in r]
for r in rows[-3:]:
    print(r[:240])
