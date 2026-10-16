# -*- coding: utf-8 -*-
# r1048 bm-c: leg0 faces of the W251 probe receipt + supplementary needle counts
import io, json

rec = json.load(open("results/_w251bmc_20261016_probe_receipt.json", encoding="utf-8"))
print("leg0 full:", json.dumps(rec["legs"].get("leg0"), ensure_ascii=False)[:1000])
print()
print("legs keys:", sorted(rec["legs"].keys()))
print()
print("top-level keys:", sorted(rec.keys()))

t = io.open("results/_w250bmc_freeze_edits.py", encoding="utf-8").read()
for n in [
    "108", "107", "109",
    "owner rows 239 + candidate = 240th EXACT",
    "bm-c rows 69 +",
    "240th", "241", "69 + candidate",
    "70th EXACT", "70th own", "70th owned",
    "leg0 ordinal", "bmc_ordinal_face",
    "probe_receipt_bmc_ordinal_face",
    "post-W249 registration: bm-c rows 69 + candidate = 70th owned",
    "owner_rows=239 / bmc_rows=69 / bmc_ordinal=70",
    "queue-head supply -- W249 complete",
    "W249+W245..W236 finalize products present",
    "post-W246-REGISTERED universe",
    "superseded W245-bmc seat claim",
    "quarantined 20261015T0924",
    "thirty-eighth", "thirty-ninth",
    "W1..W249", "W2..W249", "W17..W249",
    "estate 91 rows", "estate 92",
    "W211..W232 legs (estate 91)",
    "W233..W237 legs extracted verbatim",
    "W238..W248 legs (11) EXCLUDED",
    "fresh W238..W249 legs (12) machine-derived",
    "-> W250 block = 108 rows",
    "108 parity rows", "107 parity rows",
    "109 rows",
    "total_parity_rows",
    "SEVENTIETH owned", "SEVENTY",
    "4f7a130ff", "07:2x", "07:5x", "05:5x",
    "2026-10-16 07:5x",
    "r1035", "r1036",
    "derive landed pre-freeze commit",
    "bm-c r1045 window",
    "w250_prereg_sha",
    '"prereg derived by',
    "attempt-continuity face",
    "P-5C",
    "evidence_cutoff",
]:
    print(t.count(n), "|", n)
