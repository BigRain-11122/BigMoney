# -*- coding: utf-8 -*-
# r975 closeout heal: clock offset face bug (+20:29 -> +08:00) in state/heartbeat/round-report.
# Root cause: strftime("%H:%M") on aware datetime returns wall time, not UTC offset.
# Fix law: strftime("%z") -> "+0800" -> insert colon -> "+08:00" (ISO 8601, smoke F7 contract).
import json, datetime
off = datetime.datetime.now().astimezone().strftime("%z")  # e.g. +0800
assert off == "+0800", f"unexpected offset {off}"
iso_off = off[:3] + ":" + off[3:]  # +08:00

for p in (r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json",
          r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-c.json"):
    t = open(p, encoding="utf-8").read()
    n = t.count("+20:29")
    t = t.replace("+20:29", iso_off)
    open(p, "w", encoding="utf-8").write(t)
    json.loads(t)  # validate
    print(p.split("\\")[-1], "replaced", n)

rp = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\round_reports-bm-c.md"
t = open(rp, encoding="utf-8").read()
n = t.count("+20:29")
t = t.replace("+20:29", iso_off)
open(rp, "w", encoding="utf-8").write(t)
print("round_reports replaced", n)

# verify the smoke F7 contract face on both JSONs
st = json.load(open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json", encoding="utf-8"))
assert st["clock_read"].endswith("+08:00"), st["clock_read"]
assert isinstance(st["heartbeat_epoch_utc"], int)
h = json.load(open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-c.json", encoding="utf-8"))
assert h["clock_read"].endswith("+08:00"), h["clock_read"]
assert isinstance(h["heartbeat_epoch_utc"], int)
print("F7 contract verified | clock_read:", st["clock_read"])
