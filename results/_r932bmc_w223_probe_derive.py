# -*- coding: utf-8 -*-
# r932 bm-c: derive the W223 pre-seat probe from the W222 probe (r587 never-transcribe
# law: the derivation MACHINERY is cloned verbatim; every FACT is re-derived live from
# the post-W222-REGISTERED universe; ordered token replacements + assert sweep).
import io, sys

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w222bmc_20261012_probe.py"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w223bmc_20261012_probe.py"
t = open(SRC, encoding="utf-8").read()
orig = t

# -- ordered replacements (cascade-safe: protect candidate token first) ----------
t = t.replace("W222", "W__CAND__").replace("w222", "w__cand__")
t = t.replace("W221", "W222").replace("w221", "w222")
t = t.replace("W__CAND__", "W223").replace("w__cand__", "w223")
# ordinals / staircase instances (order matters: THIRD->FOURTH before SECOND->THIRD)
t = t.replace("EIGHTY-THIRD", "EIGHTY-FOURTH").replace("EIGHTY-SECOND", "EIGHTY-THIRD")
t = t.replace("82nd", "83rd")
# registry shape: candidate tail up to 223 (W223 unregistered at probe time)
t = t.replace("list(range(16, 222))", "list(range(16, 223))")
t = t.replace("'222: {\"a\": ('", "'223: {\"a\": ('")
t = t.replace('assert \'222: {"a": (\' not in out_pf', 'assert \'223: {"a": (\' not in out_pf')
t = t.replace('"PERPETUAL-N1-W222"', '"PERPETUAL-N1-W223"')
t = t.replace("PERPETUAL_N1_W222_PREREG.md", "PERPETUAL_N1_W223_PREREG.md")
# upstream anchor numbers (W222 finalize landed)
t = t.replace("led.get(\"total\") == 909_989", "led.get(\"total\") == 912_189")
t = t.replace("led.get(\"total\") == 909,989", "led.get(\"total\") == 912,189")
t = t.replace("led.get(\"prev_total\") == 907_789", "led.get(\"prev_total\") == 909_989")
t = t.replace("== 484_120", "== 486_320")
t = t.replace("909,989 = prev 907,789", "912,189 = prev 909,989")
t = t.replace("ledger head 909,989", "ledger head 912,189")
t = t.replace("ledger 909,989", "ledger 912,189")
t = t.replace("K=484,120", "K=486,320")
t = t.replace("K=484120", "K=486320")
t = t.replace("mu=-0.09279 sigma=0.24512", "mu=-0.0928 sigma=0.2451")
# owner-ordinal faces (post-W222-splice: owner 212 / bmc 52; candidate 213th / 53rd)
t = t.replace("owner_total == 211 and len(bmc_rows) == 51",
              "owner_total == 212 and len(bmc_rows) == 52")
t = t.replace("(expect 211/51", "(expect 212/52")
t = t.replace('"ordinal": 212, "bmc_ordinal": 52,', '"ordinal": 213, "bmc_ordinal": 53,')
t = t.replace("52nd owned", "53rd owned")
t = t.replace("51st owned", "52nd owned")
t = t.replace("50 live rows", "51 live rows")
t = t.replace("this candidate = 52nd per the same continuity", "this candidate = 53rd per the same continuity")
# upstream band facts (W222 registered bands)
t = t.replace("W222_A == (501_004, 503_003) and W222_B == (503_004, 503_203)",
              "W222_A == (503_204, 505_203) and W222_B == (505_204, 505_403)")
# receipt path + header narrative refresh
t = t.replace("_w223bmc_20261012_probe_receipt.json", "_w223bmc_20261012_probe_receipt.json")
t = t.replace('receipt = {"probe": "W223 pre-seat probe (bm-c loop r929, 2026-10-12 14:3x, CEO fill-order standing + seat-first law + never-dry supply line; post-W222-REGISTERED single-state universe, upstream W222 full cycle landed r924/r925/r927/r928-absorb)"',
              'receipt = {"probe": "W223 pre-seat probe (bm-c loop r932 absorb window, 2026-10-12 16:0x, CEO fill-order standing + seat-first law + never-dry supply line; post-W222-REGISTERED single-state universe, upstream W222 full cycle landed r929 seat/r930 prereg/r931 dead-window splice/r932 absorb)"')
t = t.replace('"""W223 pre-seat probe (bm-c loop window r929, 2026-10-12 14:3x; standing CEO',
              '"""W223 pre-seat probe (bm-c loop window r932, 2026-10-12 16:0x; standing CEO')
t = t.replace("SINGLE STATE: W2..W222 ALL REGISTERED, zero in-flight declared seats.",
              "SINGLE STATE: W2..W222 ALL REGISTERED, zero in-flight declared seats.")
t = t.replace("the W222 seat MSG leg4 projection anticipated W223+ --",
              "the W222 seat MSG leg4 projection anticipated W223+ --")

# -- mandatory residue sweep: no stale tokens may survive ------------------------
for bad in ["W__CAND__", "w__cand__", "EIGHTY-SECOND", "909_989 +", "907_789 +",
            "(501_004", "(503_004, 503_203)", "== 211 and", '"ordinal": 212, "bmc_ordinal": 52,',
            "_w222bmc_20261012_probe_receipt"]:
    assert bad not in t, "stale token survived: %r" % bad
# upstream narrative tokens that MUST survive the shift
for keep in ["W222_A == (503_204, 505_203)", "led.get(\"total\") == 912_189",
            "== 486_320", "owner_total == 212", '"ordinal": 213',
            "list(range(16, 223))", "EIGHTY-THIRD"]:
    assert keep in t, "expected token missing: %r" % keep

open(DST, "w", encoding="utf-8", newline="\n").write(t)
print("W223 probe derived: %d bytes (src %d)" % (len(t.encode()), len(orig.encode())))
