# -*- coding: utf-8 -*-
# r938 bm-c: derive the W225 pre-seat probe from the W224 probe (r587 never-transcribe
# law: derivation MACHINERY cloned verbatim; every FACT re-derived live from the
# post-W224-REGISTERED universe; ordered token replacements + regex narrative
# refresh + checked-rep helper (silent-miss impossible) + assert sweep).
import re

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w224bmc_20261012_probe.py"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w225bmc_20261012_probe.py"
t = open(SRC, encoding="utf-8").read()
orig = t


def rep(old, new, expect=1):
    global t
    n = t.count(old)
    assert n == expect, "rep target %r found %d times (expect %d)" % (old, n, expect)
    t = t.replace(old, new)


# -- wave token shifts (cascade-safe: protect candidate first) ------------------
rep("W224", "W__CAND__", None) if False else None
n_w224 = t.count("W224"); n_w224l = t.count("w224")
assert n_w224 > 0 and n_w224l > 0
t = t.replace("W224", "W__CAND__").replace("w224", "w__cand__")
t = t.replace("W223", "W224").replace("w223", "w224")
t = t.replace("W__CAND__", "W225").replace("w__cand__", "w225")
assert t.count("W__CAND__") == 0 and t.count("w__cand__") == 0
# ordinals (order matters: FIFTH->SIXTH before FOURTH->FIFTH; FOURTH occurs 3x:
# leg1 assert msg + leg1 A_semantics + docstring derivation-faces)
rep("EIGHTY-FIFTH", "EIGHTY-SIXTH", 1)
rep("EIGHTY-FOURTH", "EIGHTY-FIFTH", 3)
# docstring stale ordinal remnant (W224 derive left "83rd"; W225 staircase = 85th)
rep("A-hops-prior-B 83rd", "A-hops-prior-B 85th")

# -- header upstream narrative refresh (W224 cycle facts, regex span) -----------
m = re.search(r"Upstream face = W224 FULL CYCLE LANDED \(r932.*?machine-read\)", t, re.S)
assert m, "header span not found"
new_hdr = ("Upstream face = W224 FULL CYCLE LANDED (r935 seat\n"
           "e2676c8eb + r936 per-wave prereg derive ac1b1de64 + r937-dead-window five-face\n"
           "freeze splice executed 18:56 landed by r937 d307e3d1d + engine self-burn 12/12\n"
           "batched ledger appends 7ae27e58b/9ad2edbf5 self-committed +\n"
           "PRE-FINALIZE six-gate ALL GREEN _r937bmc_w224_sixgate_receipt.json\n"
           "19:0x [correct phase post-miss run 2; boundary-pair-scan gate leg\n"
           "in-force] + finalize one-pass 19:15: ledger 914,389+2,200=916,589 EXACT,\n"
           "merged pool K=490,720, results/perpetual_faces/n1_w224_results.json\n"
           "machine-read)")
t = t[:m.start()] + new_hdr + t[m.end():]

# -- anchor-face docstring paragraph (W224 finalize landed facts) ----------------
rep("(ledger head 914,389 = prev 912,189 + 2,200; merged pool K=488,520 machine-read in leg0; five-key ALL PASS _r934bmc_w224_fivekey_receipt.json)",
    "(ledger head 916,589 = prev 914,389 + 2,200; merged pool K=490,720 machine-read in leg0; five-key ALL PASS _r937bmc_w224_fivekey_receipt.json)")

# -- receipt anchor tuple segments (concatenated string parts) -------------------
rep('(ledger 914,389 = prev 912,189 + 2,200, "', '(ledger 916,589 = prev 914,389 + 2,200, "')
rep('"K=488,520, mu=-0.0928 sigma=0.2451 machine-read; r934 dead-window body "',
    '"K=490,720, mu=-0.0928 sigma=0.2451 machine-read; r937-dead-window body "')
rep('"(splice+burn+six-gate+finalize) landed by r935 absorb; PRE-FINALIZE six-gate all-green "',
    '"(splice+burn) landed by r937 absorb; PRE-FINALIZE six-gate all-green "')
rep('"correct-phase 3rd consecutive; W225 burn window = PRE-FINALIZE standing law); upstream "',
    '"correct-phase post-miss run 2; W225 burn window = PRE-FINALIZE standing law); upstream "')

# -- bmc ordinal note segments (concatenated string parts) -----------------------
rep('W224 freeze receipt = 53rd owned "', 'W224 freeze receipt = 54th owned "')
rep('(52 live rows + W224 candidate at r934 splice); this "',
    '(53 live rows + W224 candidate at r937 splice); this "')
rep('"candidate = 54th per the same continuity; live derive governs r359"',
    '"candidate = 55th per the same continuity; live derive governs r359"')

# -- window/round faces ----------------------------------------------------------
rep("bm-c loop window r935, 2026-10-12 17:5x", "bm-c loop window r938, 2026-10-12 19:4x")
rep("bm-c loop r935 window, 2026-10-12 17:5x", "bm-c loop r938 window, 2026-10-12 19:4x")
rep("upstream W224 full cycle landed r932 seat/r933 prereg/r934 dead-window splice+burn+finalize/r935 absorb",
    "upstream W224 full cycle landed r935 seat/r936 prereg/r937-dead-window splice+burn landed by r937 absorb")
rep("W209..W224 fifteen faces all registered bm-c continuous",
    "W209..W224 sixteen faces all registered bm-c continuous")
rep("bm-c 54th owned (continuity)", "bm-c 55th owned (continuity)")
rep("owner={owner_total} -> 213th wave", "owner={owner_total} -> 214th wave")

# -- registry shape: candidate tail up to 225 (W225 unregistered at probe time) --
rep("list(range(16, 224))", "list(range(16, 225))")
# upstream row digit-ref (W-token shift does not move bare digits; W223 probe
# lineage bugface: prior derive inherited [222] without an explicit replace;
# 3 occurrences = W224_A tuple + W224_B tuple + engine_owner check)
rep("N1_BANDS[223]", "N1_BANDS[224]", 3)
# origin-vacancy digit-string (W224 is now REGISTERED -- its row MUST be on origin)
rep("'224: {\"a\": (' not in out_pf", "'225: {\"a\": (' not in out_pf")
# -- upstream band facts (W224 registered bands) ----------------------------------
rep("W224_A == (505_404, 507_403) and W224_B == (507_404, 507_603)",
    "W224_A == (507_604, 509_603) and W224_B == (509_604, 509_803)")
rep('"leg0 failed: W224 row drift (bm-c r934 splice face)"',
    '"leg0 failed: W224 row drift (bm-c r937 splice face)"')
# -- ledger anchors (W224 finalize landed) ----------------------------------------
rep('led.get("total") == 914_389 and led.get("prev_total") == 912_189',
    'led.get("total") == 916_589 and led.get("prev_total") == 914_389')
rep("assert w224_merged_n == 488_520", "assert w224_merged_n == 490_720")
# -- owner ordinals (post-W224-splice: owner 214 / bmc 54; candidate 215th / 55th) --
rep("assert owner_total == 213 and len(bmc_rows) == 53",
    "assert owner_total == 214 and len(bmc_rows) == 54")
rep("(expect 213/53 post-W224-splice per the r934 splice receipt ordinal faces)",
    "(expect 214/54 post-W224-splice per the r937 splice receipt ordinal faces)")
rep('"ordinal": 214, "bmc_ordinal": 54,', '"ordinal": 215, "bmc_ordinal": 55,')

# -- residue sweep: no stale tokens may survive ----------------------------------
for bad in ["W__CAND__", "w__cand__", "EIGHTY-FOURTH", "8f2d79147",
            "b7d46427d", "448c4d8c2", "7b4236f85", "0a8e2ba00", "_r934bmc",
            '== 914_389 and led.get("prev_total") == 912_189', "== 488_520", "K=488,520",
            "owner_total == 213", '"ordinal": 214,', "list(range(16, 224))",
            "(505_404, 507_403)", "(507_404, 507_603)", "N1_BANDS[223]",
            "'224: {\"a\": ('", "r934 splice", "912,189", "912_189", "17:5x",
            "fifteen faces", "53rd owned", "(52 live rows", "candidate = 54th",
            "213th wave", "54th owned (continuity)", "correct-phase 3rd consecutive",
            "r932 seat/r933", "loop r935", "r935 absorb", "A-hops-prior-B 83rd"]:
    assert bad not in t, "stale token survived: %r" % bad
# -- expected tokens that MUST survive the shift ---------------------------------
for keep in ["W224_A == (507_604, 509_603)", 'led.get("total") == 916_589',
            "== 490_720", "K=490,720", "owner_total == 214", '"ordinal": 215',
            "list(range(16, 225))", "EIGHTY-FIFTH", "EIGHTY-SIXTH",
            '"PERPETUAL-N1-W225"', "PERPETUAL_N1_W225_PREREG.md",
            "_w225bmc_20261012_probe_receipt.json", "W225p_A",
            "bm-c 55th owned (continuity)", "54th owned", "N1_BANDS[224]",
            "'225: {\"a\": ('", "_r937bmc_w224_sixgate_receipt.json",
            "_r937bmc_w224_fivekey_receipt.json", "e2676c8eb", "ac1b1de64",
            "7ae27e58b", "9ad2edbf5", "916,589", "post-miss run 2",
            "A-hops-prior-B 85th"]:
    assert keep in t, "expected token missing: %r" % keep

open(DST, "w", encoding="utf-8", newline="\n").write(t)
print("W225 probe derived: %d bytes (src %d)" % (len(t.encode("utf-8")), len(orig.encode("utf-8"))))
