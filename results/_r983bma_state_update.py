# -*- coding: utf-8 -*-
"""r983 bm-a state closeout update: round heal 979->983 (r980-982 estates landed but never advanced state,
r861-family 4th instance honest), verdict + verify lines for W238 prereg freeze."""
import json, datetime

p = "state-bm-a.json"
d = json.load(open(p, encoding="utf-8"))
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

d["round_no"] = 983
d["last_round"] = 983
d["last_round_at"] = now
d["updated_at"] = now
d["last_orders_seen"] = (
    "r983: ORD db08b85b consumed (delta bde2e581->db08b85b tail = 10-14 MV/BigStream/bm-c/bm-b "
    "software-copyright rows, zero BigMoney directives); DEC 86187eff unchanged; dual-delta FALSE opening+tail"
)
d["last_decisions_seen"] = d.get("last_decisions_seen", "")
d["verdict"] = (
    "green (red=false lane=healthy; engine ALIVE idle queue0 post-W237-finalize; "
    "W238 PREREG FROZEN+DELIVERED this round (27558B, 47 SUB pairs, derive_v2 r982-count-fixes re-verified "
    "fail-closed full-assert pass r983); splice next round; S6 41-leg chain detached pid 44360)"
)
d["verify"] = (
    "green (prereg re-derive byte-stable 27558B all asserts PASS + receipt facts ledger 945,189/K 519,320/"
    "bands A 538404-540403 B 540404-540603 + watermark --advance read-back OK + state heal 979->983 honest"
)
d["d19_watermark_guard"]["round_ref"] = 983
d["d19_watermark_guard"]["ts"] = now

json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state written round_no=", d["round_no"], "at", now)
