# r703 bm-a S6 log digest (encoding-agnostic read per pit-encoding)
import re

raw = open(r"results/_r703bma_s6_chain.txt", "rb").read()
for enc in ("utf-8-sig", "utf-16", "gbk"):
    try:
        t = raw.decode(enc)
        break
    except Exception:
        continue
rcs = re.findall(r"RC=(\d+)\s+(.+)", t)
print("RC lines:", len(rcs))
bad = [(rc, name.strip()[:60]) for rc, name in rcs if rc != "0"]
print("NONZERO:", bad if bad else "none")
shown = set()
for kw in ("ZERO-DRIFT", "verdict", "delta", "streak", "no-op", "skip", "GREEN", "ORANGE", "RED"):
    for ln in t.splitlines():
        if kw in ln and len(ln) < 220 and kw not in shown:
            print(f"[{kw}]", ln[:180])
            shown.add(kw)
            break
