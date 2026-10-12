# -*- coding: utf-8 -*-
# r940 bm-c: derive the W226 pre-seat probe from the W225 probe (r587 never-transcribe
# law: derivation MACHINERY cloned verbatim; every FACT re-derived live from the
# post-W225-REGISTERED universe; ordered token replacements + regex narrative
# refresh + checked-rep helper (silent-miss impossible) + assert sweep).
import re

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w225bmc_20261012_probe.py"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w226bmc_20261012_probe.py"
t = open(SRC, encoding="utf-8").read()
orig = t


def rep(old, new, expect=1):
    global t
    n = t.count(old)
    assert n == expect, "rep target %r found %d times (expect %d)" % (old, n, expect)
    t = t.replace(old, new)


# -- wave token shifts (cascade-safe: protect candidate first) ------------------
n_w225 = t.count("W225"); n_w225l = t.count("w225")
assert n_w225 > 0 and n_w225l > 0
t = t.replace("W225", "W__CAND__").replace("w225", "w__cand__")
t = t.replace("W224", "W225").replace("w224", "w225")
t = t.replace("W__CAND__", "W226").replace("w__cand__", "w226")
assert t.count("W__CAND__") == 0 and t.count("w__cand__") == 0
# ordinals (order matters: SIXTH->SEVENTH before FIFTH->SIXTH; FIFTH occurs 3x:
# docstring staircase-geometry + leg1 assert msg + leg1 A_semantics)
rep("EIGHTY-SIXTH", "EIGHTY-SEVENTH", 1)
rep("EIGHTY-FIFTH", "EIGHTY-SIXTH", 3)
# docstring A-walk remnant ordinal (W225 staircase = 85th; W226 = 86th)
rep("A-hops-prior-B 85th", "A-hops-prior-B 86th")

# -- header upstream narrative refresh (W225 cycle facts, regex span) -----------
m = re.search(r"Upstream face = W225 FULL CYCLE LANDED \(r935.*?machine-read\)", t, re.S)
assert m, "header span not found"
new_hdr = ("Upstream face = W225 FULL CYCLE LANDED (r938 seat\n"
           "c78dd1a44 + r939 per-wave prereg derive 4b22941a7 + r939 five-face\n"
           "freeze splice 84ecb3a3a (family-6 LHS/RHS/comment triple absorbed at\n"
           "editor derive = W224 sec.8 upgrade executed, first zero-repair window)\n"
           "+ engine self-burn 12/12\n"
           "batched ledger appends 641efeb69/4b4946df6 self-committed +\n"
           "PRE-FINALIZE six-gate ALL GREEN _r939bmc_w225_sixgate_receipt.json\n"
           "20:2x [correct phase run 3 consecutive; splice integrity BOTH faces\n"
           "clean-equal] + finalize one-pass 20:26: ledger 916,589+2,200=918,789 EXACT,\n"
           "merged pool K=492,920, results/perpetual_faces/n1_w225_results.json\n"
           "machine-read; six-gate+finalize+fivekey landed by r940 8b12ace73)")
t = t[:m.start()] + new_hdr + t[m.end():]

# -- anchor-face docstring paragraph (W225 finalize landed facts) ----------------
rep("(ledger head 916,589 = prev 914,389 + 2,200; merged pool K=490,720 machine-read in leg0; five-key ALL PASS _r937bmc_w225_fivekey_receipt.json)",
    "(ledger head 918,789 = prev 916,589 + 2,200; merged pool K=492,920 machine-read in leg0; five-key ALL PASS _r939bmc_w225_fivekey_receipt.json)")

# -- receipt anchor tuple segments (concatenated string parts) -------------------
rep('(ledger 916,589 = prev 914,389 + 2,200, "', '(ledger 918,789 = prev 916,589 + 2,200, "')
rep('"K=490,720, mu=-0.0928 sigma=0.2451 machine-read; r937-dead-window body "',
    '"K=492,920, mu=-0.0928 sigma=0.2451 machine-read; r939-dead-window body "')
rep('"(splice+burn) landed by r937 absorb; PRE-FINALIZE six-gate all-green "',
    '"(splice+burn) landed at r939; PRE-FINALIZE six-gate all-green "')
rep('"correct-phase post-miss run 2; W226 burn window = PRE-FINALIZE standing law); upstream "',
    '"correct-phase run 3 consecutive; W226 burn window = PRE-FINALIZE standing law); upstream "')

# -- bmc ordinal note segments (concatenated string parts) -----------------------
rep('W225 freeze receipt = 54th owned "', 'W225 freeze receipt = 55th owned "')
rep('(53 live rows + W225 candidate at r937 splice); this "',
    '(54 live rows + W225 candidate at r939 splice); this "')
rep('"candidate = 55th per the same continuity; live derive governs r359"',
    '"candidate = 56th per the same continuity; live derive governs r359"')

# -- window/round faces ----------------------------------------------------------
rep("bm-c loop window r938, 2026-10-12 19:4x", "bm-c loop window r940, 2026-10-12 20:3x")
rep("bm-c loop r938 window, 2026-10-12 19:4x", "bm-c loop r940 window, 2026-10-12 20:3x")
rep("upstream W225 full cycle landed r935 seat/r936 prereg/r937-dead-window splice+burn landed by r937 absorb",
    "upstream W225 full cycle landed r938 seat c78dd1a44/r939 prereg 4b22941a7+r939 splice 84ecb3a3a+engine self-burn/six-gate+finalize+fivekey landed by r940 8b12ace73")
rep("W209..W225 sixteen faces all registered bm-c continuous",
    "W209..W225 seventeen faces all registered bm-c continuous")
rep("bm-c 55th owned (continuity)", "bm-c 56th owned (continuity)")
rep("owner={owner_total} -> 214th wave", "owner={owner_total} -> 215th wave")

# -- registry shape: candidate tail up to 226 (W226 unregistered at probe time) --
rep("list(range(16, 225))", "list(range(16, 226))")
# upstream row digit-ref (W-token shift does not move bare digits; 3 occurrences =
# W225_A tuple + W225_B tuple + engine_owner check)
rep("N1_BANDS[224]", "N1_BANDS[225]", 3)
# origin-vacancy digit-string (W225 is now REGISTERED -- its row MUST be on origin)
rep("'225: {\"a\": (' not in out_pf", "'226: {\"a\": (' not in out_pf")
# -- upstream band facts (W225 registered bands) ----------------------------------
rep("W225_A == (507_604, 509_603) and W225_B == (509_604, 509_803)",
    "W225_A == (509_804, 511_803) and W225_B == (511_804, 512_003)")
rep('"leg0 failed: W225 row drift (bm-c r937 splice face)"',
    '"leg0 failed: W225 row drift (bm-c r939 splice face)"')
# -- ledger anchors (W225 finalize landed) ----------------------------------------
rep('led.get("total") == 916_589 and led.get("prev_total") == 914_389',
    'led.get("total") == 918_789 and led.get("prev_total") == 916_589')
rep("assert w225_merged_n == 490_720", "assert w225_merged_n == 492_920")
# -- owner ordinals (post-W225-splice: owner 215 / bmc 55; candidate 216th / 56th) --
rep("assert owner_total == 214 and len(bmc_rows) == 54",
    "assert owner_total == 215 and len(bmc_rows) == 55")
rep("(expect 214/54 post-W225-splice per the r937 splice receipt ordinal faces)",
    "(expect 215/55 post-W225-splice per the r939 splice receipt ordinal faces)")
rep('"ordinal": 215, "bmc_ordinal": 55,', '"ordinal": 216, "bmc_ordinal": 56,')

# -- residue sweep: no stale tokens may survive ----------------------------------
for bad in ["W__CAND__", "w__cand__", "EIGHTY-FIFTH", "e2676c8eb",
            "ac1b1de64", "d307e3d1d", "7ae27e58b", "9ad2edbf5", "_r937bmc",
            "r937", '== 916_589 and led.get("prev_total") == 914_389', "== 490_720", "K=490,720",
            "owner_total == 214", '"ordinal": 215,', "list(range(16, 225))",
            "(507_604, 509_603)", "(509_604, 509_803)", "N1_BANDS[224]",
            "'225: {\"a\": ('", "914,389", "914_389", "19:4x", "19:0x",
            "sixteen faces", "54th owned", "(53 live rows", "candidate = 55th",
            "214th wave", "55th owned (continuity)", "post-miss run 2",
            "r935 seat/r936", "loop r938", "A-hops-prior-B 85th", "18:56"]:
    assert bad not in t, "stale token survived: %r" % bad
# -- expected tokens that MUST survive the shift ---------------------------------
for keep in ["W225_A == (509_804, 511_803)", 'led.get("total") == 918_789',
            "== 492_920", "K=492,920", "owner_total == 215", '"ordinal": 216',
            "list(range(16, 226))", "EIGHTY-SIXTH", "EIGHTY-SEVENTH",
            '"PERPETUAL-N1-W226"', "PERPETUAL_N1_W226_PREREG.md",
            "_w226bmc_20261012_probe_receipt.json", "W226p_A",
            "bm-c 56th owned (continuity)", "55th owned", "N1_BANDS[225]",
            "'226: {\"a\": ('", "_r939bmc_w225_sixgate_receipt.json",
            "_r939bmc_w225_fivekey_receipt.json", "c78dd1a44", "4b22941a7",
            "84ecb3a3a", "641efeb69", "4b4946df6", "8b12ace73", "918,789",
            "run 3 consecutive", "A-hops-prior-B 86th", "seventeen faces",
            "r940 8b12ace73"]:
    assert keep in t, "expected token missing: %r" % keep

open(DST, "w", encoding="utf-8", newline="\n").write(t)
print("W226 probe derived: %d bytes (src %d)" % (len(t.encode("utf-8")), len(orig.encode("utf-8"))))
