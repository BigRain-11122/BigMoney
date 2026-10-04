# -*- coding: utf-8 -*-
"""r479 bm-c S7-close receipt: orders re-scan (S7 double-scan law) + round-report
receipt line append (delivery proof + local-behind count discharge)."""
import datetime
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NOW = datetime.datetime.now()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S")
TS_OFF = TS + "+08:00"

# --- orders S7 re-scan (same-caliber same-form set-diff, r646 law) ---
orders_dir = os.path.join("fleet", "orders")
orders = sorted(f for f in os.listdir(orders_dir)
                if f.startswith("O-") and f.endswith(".md"))
with open(r"fleet\machines\bm-c.json", encoding="utf-8") as f:
    hb = json.load(f)
acks = set(hb.get("orders_ack", []))
unacked = sorted(set(orders) - acks)
assert len(hb["orders_ack"]) == 155, "ack count %s" % len(hb["orders_ack"])
print("ORDERS_RESCAN total=%d acks=%d unacked=%s" % (len(orders), len(acks), unacked))
assert unacked == [], "S7 re-scan found un-acked orders"

LINE = (TS_OFF + "｜r479 S7-close｜dept:工程｜push_verify DELIVERED two-leg: round close "
        "cfac31447 + canon merge 5dc8ab019 (15 UU faces resolved per law: CODELY.md "
        "block-union w/ superseded-variant drop [r675/r417 bullet-less 2B family], "
        "token_usage per-key union [r456/r466], compute_audit hist ts-identity union, "
        "12 S6 regen twins embedded-ts newer-wins = origin bm-b r676 per r440), "
        "tip==remote 5dc8ab01918f4caf55fd3e8b1f067ce3fb00f889, ahead=0/behind=0, zero "
        "force, pre-commit/pre-push claws passed｜race disclosure: bm-b r676 same-CEO-order "
        "concurrent execution wave (their O-1440 receipt + trio V801/Q623/D468 newer sync "
        "+ N1-W116 r677 grain declared) merged clean; my probe face V796/Q619/D464 @14:51 "
        "honest dual-read kept in r479 line｜ORDERS_RESCAN 155/155 zero un-acked｜"
        "本地未达 origin commit 数=0（push_verify 单源证）")

rp = os.path.join("round_reports-bm-c.md")
with open(rp, "rb") as f:
    raw = f.read()
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
needle = "r479 S7-close".encode("utf-8")
assert raw.count(needle) == 0, "receipt line already present"
line = LINE.encode("utf-8") + eol
with open(rp, "ab") as f:
    f.write(line)
with open(rp, "rb") as f:
    raw2 = f.read()
assert raw2.count(needle) == 1 and raw2 == raw + line
print("RECEIPT OK " + TS_OFF)
