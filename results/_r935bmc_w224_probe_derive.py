# -*- coding: utf-8 -*-
# r935 bm-c: derive the W224 pre-seat probe from the W223 probe (r587 never-transcribe
# law: derivation MACHINERY cloned verbatim; every FACT re-derived live from the
# post-W223-REGISTERED universe; ordered token replacements + regex narrative
# refresh + assert sweep).
import re

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w223bmc_20261012_probe.py"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w224bmc_20261012_probe.py"
t = open(SRC, encoding="utf-8").read()
orig = t

# -- wave token shifts (cascade-safe: protect candidate first) ------------------
t = t.replace("W223", "W__CAND__").replace("w223", "w__cand__")
t = t.replace("W222", "W223").replace("w222", "w223")
t = t.replace("W__CAND__", "W224").replace("w__cand__", "w224")
# ordinals (order matters: FOURTH->FIFTH before THIRD->FOURTH)
t = t.replace("EIGHTY-FOURTH", "EIGHTY-FIFTH").replace("EIGHTY-THIRD", "EIGHTY-FOURTH")

# -- header upstream narrative refresh (W223 cycle facts, regex span) -----------
m = re.search(r"Upstream face = W223 FULL CYCLE LANDED \(r924.*?machine-read\)", t, re.S)
assert m, "header span not found"
new_hdr = ("Upstream face = W223 FULL CYCLE LANDED (r932 seat\n"
           "8f2d79147 + r933 per-wave prereg derive b7d46427d + r934 dead-window five-face\n"
           "freeze splice 448c4d8c2 pushed 17:4x + engine self-burn 12/12 batched\n"
           "ledger appends 7b4236f85/0a8e2ba00 [shard-9/10 landed by r935 estate] +\n"
           "PRE-FINALIZE six-gate ALL GREEN _r934bmc_w223_sixgate_receipt.json\n"
           "17:24:44 [correct phase 3rd consecutive; boundary-pair-scan gate leg\n"
           "in-force first landing = W222 sec.8 escalation proposal] + finalize\n"
           "one-pass 17:2x: ledger 912,189+2,200=914,389 EXACT, merged pool K=488,520,\n"
           "results/perpetual_faces/n1_w223_results.json machine-read)")
t = t[:m.start()] + new_hdr + t[m.end():]

# -- anchor-face paragraph facts (W223 finalize landed) --------------------------
t = t.replace("ledger head 912,189 = prev 909,989 +\n2,200; merged pool K=486,320 machine-read in leg0; five-key ALL PASS\n_r928bmc_w223_fivekey_receipt.json)",
              "ledger head 914,389 = prev 912,189 + 2,200; merged pool K=488,520 machine-read in leg0; five-key ALL PASS _r934bmc_w223_fivekey_receipt.json)")

# -- receipt anchor tuple segments (concatenated string parts) -------------------
t = t.replace('(ledger 912,189 = prev 909,989 + 2,200, "', '(ledger 914,389 = prev 912,189 + 2,200, "')
t = t.replace('"K=486,320, mu=-0.0928 sigma=0.2451 machine-read; r925/r927 dead-window bodies "',
              '"K=488,520, mu=-0.0928 sigma=0.2451 machine-read; r934 dead-window body "')
t = t.replace('"absorbed and landed by r928; six-gate POST-HOC all-green with W212-family 4th-instance "',
              '"(splice+burn+six-gate+finalize) landed by r935 absorb; PRE-FINALIZE six-gate all-green "')
t = t.replace('"debt disclosed; W224 burn window = PRE-FINALIZE standing law); upstream "',
              '"correct-phase 3rd consecutive; W224 burn window = PRE-FINALIZE standing law); upstream "')

# -- bmc ordinal note segments (concatenated string parts) -----------------------
t = t.replace('W223 freeze receipt = 52nd owned "', 'W223 freeze receipt = 53rd owned "')
t = t.replace('(51 live rows + W223 candidate at r928 splice); this "',
              '(52 live rows + W223 candidate at r934 splice); this "')
t = t.replace('"candidate = 52nd per the same continuity; live derive governs r359"',
              '"candidate = 54th per the same continuity; live derive governs r359"')

# -- window/round faces ----------------------------------------------------------
t = t.replace("bm-c loop window r932, 2026-10-12 16:0x", "bm-c loop window r935, 2026-10-12 17:5x")
t = t.replace("bm-c loop r932 absorb window, 2026-10-12 16:0x", "bm-c loop r935 window, 2026-10-12 17:5x")
t = t.replace("upstream W223 full cycle landed r929 seat/r930 prereg/r931 dead-window splice/r932 absorb",
              "upstream W223 full cycle landed r932 seat/r933 prereg/r934 dead-window splice+burn+finalize/r935 absorb")
t = t.replace("W209..W223 thirteen faces all registered bm-c continuous",
              "W209..W223 fifteen faces all registered bm-c continuous")
t = t.replace("bm-c 53rd owned (continuity)", "bm-c 54th owned (continuity)")
t = t.replace("owner={owner_total} -> 212th wave", "owner={owner_total} -> 213th wave")
t = t.replace('"W223 finalize LANDED (ledger 912,189 = prev 909,989 + 2,200, K=486,320, mu=-0.0928 sigma=0.2451 machine-read; r925/r927 dead-window bodies absorbed and landed by r928; six-gate POST-HOC all-green with W212-family 4th-instance debt disclosed;',
              '"W223 finalize LANDED (ledger 914,389 = prev 912,189 + 2,200, K=488,520, mu=-0.0928 sigma=0.2451 machine-read; r934 dead-window body (splice+burn+six-gate+finalize) landed by r935 absorb; PRE-FINALIZE six-gate all-green correct-phase 3rd consecutive;')
t = t.replace('"bm-c attempt-continuity: W223 freeze receipt = 52nd owned (51 live rows + W223 candidate at r928 splice); this candidate = 52nd per the same continuity; live derive governs r359"',
              '"bm-c attempt-continuity: W223 freeze receipt = 53rd owned (52 live rows + W223 candidate at r934 splice); this candidate = 54th per the same continuity; live derive governs r359"')

# -- registry shape: candidate tail up to 224 (W224 unregistered at probe time) --
t = t.replace("list(range(16, 223))", "list(range(16, 224))")
# upstream row digit-ref (W-token shift does not move bare digits; W223 probe
# lineage bugface: prior derive inherited [222] without an explicit replace)
t = t.replace("N1_BANDS[222]", "N1_BANDS[223]")
# origin-vacancy digit-string (W223 is now REGISTERED -- its row MUST be on origin)
t = t.replace("'223: {\"a\": (' not in out_pf", "'224: {\"a\": (' not in out_pf")
# -- upstream band facts (W223 registered bands) ----------------------------------
t = t.replace("W223_A == (503_204, 505_203) and W223_B == (505_204, 505_403)",
              "W223_A == (505_404, 507_403) and W223_B == (507_404, 507_603)")
t = t.replace('"leg0 failed: W223 row drift (bm-c r928 splice face)"',
              '"leg0 failed: W223 row drift (bm-c r934 splice face)"')
# -- ledger anchors (W223 finalize landed) ----------------------------------------
t = t.replace('led.get("total") == 912_189 and led.get("prev_total") == 909_989',
              'led.get("total") == 914_389 and led.get("prev_total") == 912_189')
t = t.replace("assert w223_merged_n == 486_320", "assert w223_merged_n == 488_520")
# -- owner ordinals (post-W223-splice: owner 213 / bmc 53; candidate 214th / 54th) --
t = t.replace("assert owner_total == 212 and len(bmc_rows) == 52",
              "assert owner_total == 213 and len(bmc_rows) == 53")
t = t.replace("(expect 212/52 post-W223-splice per the r928 splice receipt ordinal faces)",
              "(expect 213/53 post-W223-splice per the r934 splice receipt ordinal faces)")
t = t.replace('"ordinal": 213, "bmc_ordinal": 53,', '"ordinal": 214, "bmc_ordinal": 54,')

# -- residue sweep: no stale tokens may survive ----------------------------------
for bad in ["W__CAND__", "w__cand__", "EIGHTY-THIRD", "r924\nseat", "MSG-20261012-1225",
            "2e251d084", "cf0b51d21", "98da27a40", "01ac36bad", "1461e9f22",
            'led.get("total") == 912_189', "== 486_320", "K=486,320",
            "owner_total == 212", '"ordinal": 213,', "list(range(16, 223))",
            "(503_204, 505_203)", "(505_204, 505_403)", "_r928bmc", "_r924", "_r925", "_r927", "_r928",
            "_w223bmc_20261012_probe_receipt", "907,789", "909,989", "r929 seat/r930",
            "212/52", "212th wave", "52nd", "(51 live rows", "N1_BANDS[222]",
            "'223: {\"a\": ('"]:
    assert bad not in t, "stale token survived: %r" % bad
# -- expected tokens that MUST survive the shift ---------------------------------
for keep in ["W223_A == (505_404, 507_403)", 'led.get("total") == 914_389',
            "== 488_520", "K=488,520", "owner_total == 213", '"ordinal": 214',
            "list(range(16, 224))", "EIGHTY-FOURTH", "EIGHTY-FIFTH",
            '"PERPETUAL-N1-W224"', "PERPETUAL_N1_W224_PREREG.md",
            "_w224bmc_20261012_probe_receipt.json", "W224p_A",
            "bm-c 54th owned", "53rd owned"]:
    assert keep in t, "expected token missing: %r" % keep

open(DST, "w", encoding="utf-8", newline="\n").write(t)
print("W224 probe derived: %d bytes (src %d)" % (len(t.encode("utf-8")), len(orig.encode("utf-8"))))
