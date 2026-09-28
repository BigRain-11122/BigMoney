"""r391 bm-b: T-103 claim (O-1730 claim-and-start same round, unclaimed CEO
immediate ticket, any healthy machine per ticket note) + O-20260928-1555
universe/boundary note sync on T-103 + T-104 (bm-b-owned).

T-106 note sync LEFT TO OWNER bm-c (single-writer discipline, claimed r172).
"""
import datetime as dt
import json

now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
UNIVERSE_NOTE = (
    "O-20260928-1555 (CEO direct order, P0) universe sync: ETF line universe "
    "= 5 members, tier-1 huijin-high-control {510050 SSE50, 510300 HS300}, "
    "tier-2 {510500 CSI500, 512100 CSI1000, 588000 STAR50}; ChiNext excluded; "
    "cross-category (sector-theme/QDII/bond/gold) stays excluded per "
    "O-1533. Two-line separation law: ETF line strategy families "
    "(T-103 ops chains / T-104 grid chains / T-106 control-degree face) "
    "independent research faces, stock-line verdicts non-transferable; "
    "all-A stock data = measurement face only (temperature/sentiment, e.g. "
    "H2' sentiment-gate arm), NEVER ETF-line deployment targets. No-dup "
    "boundary within window: T-103=per-member ops chain "
    "(entry/exit/trailing), T-104=grid chain family, T-106=control-degree "
    "quant + event ledger. Pool order unchanged: V2-P1 -> T-101 first, "
    "ETF ops-chain batch follows (O-1555 sec.3)."
)

# --- T-103: claim + universe note sync
p103 = "fleet/tasks/T-2026-09-28-103-P1.json"
d = json.load(open(p103, encoding="utf-8"))
assert d["status"] == "open", d["status"]
d["status"] = "claimed"
d["claimed_by"] = ("bm-b (OS iteration loop, round 391; unclaimed CEO "
                   "immediate ticket per O-20260928-1524 + O-1730 "
                   "claim-and-start same round; git fetch immediately "
                   "before claim per r239 collision law)")
d["claimed_at"] = now
d["note"] = (d.get("note", "") + " || " + UNIVERSE_NOTE +
             " || r391 bm-b claim: s0 start this round (classification map "
             "+ in-repo ETF evidence census), domain research/etf_ops/ "
             "created on claim per ticket note.")
with open(p103, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
back = json.load(open(p103, encoding="utf-8"))
assert back["status"] == "claimed" and back["claimed_by"].startswith("bm-b")
print(f"{p103}: claimed by bm-b @ {now} + O-1555 universe note synced")

# --- T-104: universe note sync (already bm-b-owned since r390)
p104 = "fleet/tasks/T-2026-09-28-104-P1.json"
d4 = json.load(open(p104, encoding="utf-8"))
assert d4["status"] == "claimed" and "bm-b" in d4["claimed_by"], d4["status"]
d4["note"] = (d4.get("note", "") + " || " + UNIVERSE_NOTE +
              " || r391 bm-b application face: minute-feed active universe "
              "extends 3->5 codes (add 512100 + 588000, v1.3), 5 T+0 "
              "archives stay frozen; s2 broad-grid prereg will draft "
              "against the 5-member universe directly (not yet frozen, "
              "zero burn).")
with open(p104, "w", encoding="utf-8") as f:
    json.dump(d4, f, ensure_ascii=False, indent=2)
back4 = json.load(open(p104, encoding="utf-8"))
assert "O-20260928-1555" in back4["note"]
print(f"{p104}: O-1555 universe note synced (bm-b-owned ticket)")
