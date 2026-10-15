# -*- coding: utf-8 -*-
# r1020 bm-a: pre-count analysis for the W247 freeze editor generator.
# Dumps exact counts of every chain/VMAP old-side needle in the W246 editor
# (SRC physical bytes) + r10xx stamp inventory + block anchor presence checks.
import io, re, sys
sys.stdout.reconfigure(encoding="utf-8")

SRC = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\_w246bma_freeze_edits.py"
T0 = io.open(SRC, encoding="utf-8", newline="").read()

CHAIN_NEEDLES = [
    "W246", "W245", "W244", "w246bma", "w245bma",
    '246: {"batch"', '245: {"batch"', '246: {"a"', '245: {"a"',
    '246: {{"batch"', '246: {{"a"',
    "_set_wave(246)", "WAVE_CONFIGS[246]", "WAVE_CONFIGS[245]",
    "N1_BANDS.get(245)", "N1_BANDS[245]", "N1_BANDS[244]", "N1_BANDS[243]",
    "n1_w246", "n1_w245", "n1w246", "PERPETUAL_N1_W245_PREREG",
]
print("== CHAIN needle counts in W246 editor ==")
for s in CHAIN_NEEDLES:
    print("%-28r %d" % (s, T0.count(s)))

VMAP_NEEDLES = [
    "15:1x bm-a r1017 freeze window",
    "r1013 window; engine self-burn 12/12 + finalize one-pass verified r1015)",
    "bm-a splice generation r1013 window",
    "r1015, pre-seat probe",
    "bm-a r1015 own-wave closeout 13:2x",
    "finalize landing 13:2x",
    "the bm-a r1017 window",
    "bm-a r1015 own-wave closeout",
    "own-wave closeout r1015",
    "own-seat continuity (bm-a landed the W245 chain same-window r1015: freeze 29d3ab761 + engine self-burn 12/12 + finalize one-pass ledger 963,335 / K=536,920; no takeover lane this wave, no declared external turn, origin vacancy four-check green at publish)",
    "785936d84",
    "MSG-20261015-1328-bma-w246-seat",
    "r1015, queue-depth supply depth-1 at publish",
    "(r1015 MSG-",
    " r1015 BEFORE this freeze",
    "(r1016 derive landed pre-freeze expected)",
    "r1016 window machine-SUB derive landed pre-freeze",
    "r1016 window derive landed pre-freeze commit",
    "and committed at origin 4a001a96d, machine-SUB from the frozen W245 prereg 6473fb7f8)",
    "derived by the bm-a r1016 window",
    "and committed same-window",
    "machine-SUB from the frozen W246 tpl 260ffd3f8",
    "963,335", "536,920", "963_335", "536_920",
    "owner_rows=235", "bma_rows=127",
    "len(owner_rows_live) == 235", "len(bma_rows_live) == 127",
    "expect 235/127/67",
    "rows 127", "rows 235", "236th", "128th", "bma_ordinal=128",
    'probe_receipt_bma_ordinal_face": 127',
    "one hundred and twenty-eighth",
    "ONE HUNDRED AND TWENTY-SEVENTH",
    "TWO HUNDRED AND FORTY-SIXTH",
    "thirty-fifth consecutive window", "thirty-fourth consecutive",
    "eighth consecutive seed-gap", "gap face eighth consecutive",
    "557_501", "559_500", "542_201", "542_400",
    "w245_a_tail", "w245_b_tail",
    "arith_a245/arith_b245",
    "arith_a246", "arith_b246",
    "W247p_",
    "the W246 block appends ONE fresh W245 leg -> 103 rows.",
    'assert par_full.count("assert pf.N1_BANDS[") == 103',
    "!= 103 (90 estate",
    "W232..W244 legs 13",
    "extracted verbatim (13)",
    'assert legs_sec.count("assert pf.N1_BANDS[") == 13',
    "thirteen legs",
    "list(range(232, 245))",
    "= 104 rows ending",
    "-> 104 parity rows",
    "range(209, 247)", "range(16, 246)", "range(17, 246)",
    "if w < 246)", "if w < 245)",
    "w<246", "w<245",
    "below 246", "below-245",
    "range(16,245)", "range(17,245)",
    '"wave": 245',
    "sixth consecutive seed-gap",
]
print("== VMAP needle counts ==")
for s in VMAP_NEEDLES:
    print("%-60r %d" % (s[:60], T0.count(s)))

print("== r10xx stamp inventory ==")
for m in sorted(set(re.findall(r"r10\d\d", T0))):
    print("%-8s %d" % (m, T0.count(m)))

print("== block anchor presence (raw T0 forms) ==")
ANCHORS = [
    "# NEW FACE vs the W245 editor (honest disclosure): the W246 B band returns",
    "# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.",
    "# W246 FACE (probe receipt leg1 relation_asserts):",
    "B naive continuation drift vs probe receipt leg1 ARITH_B",
    '"    # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail",',
    '"    # W247+ projection (gate-derived pre-seat probe leg4, pre-W246",',
    ' "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN arithmetic ',
    '"ADMIT convention); W247+ projection per this window gate: ",',
    '"        # band facts (law sec.4 W246 row): A = FIRST-CLEAN arithmetic",',
    'assert _entry_shard_of(0, 12) == (\\"PERPETUAL-N1-W246-SHARD-0\\",',
    '          "+ B=FIRST-CLEAN arithmetic continuation of the prior-wave B tail (double-clean face, "',
    '                     "B": "FIRST-CLEAN arithmetic continuation of the prior-wave B tail (CLEAN at naive start',
    '  "downstream_seat": "W247 seat NOT YET PUBLISHED',
    " law sec.4 W246 B:",
    '"wave": 245',
]
for a in ANCHORS:
    print("%-70r %d" % (a[:70], T0.count(a)))

print("== count-gate lines (raw, for bump loop) ==")
for n, c in [(242, 4), (241, 5), (240, 6), (239, 7), (238, 8), (237, 9), (236, 10)]:
    pat = 'N1_BANDS[%d]["a"][1])}),\') == %d' % (n, c)
    print("[%d]==%d raw-count %d" % (n, c, T0.count(pat)))
_line244 = ("assert n1_t4.count(f'assert pf.N1_BANDS[244] == {{\"a\": ({fmt(pf_mod.N1_BANDS[244][\"a\"][0])}"
            ", {fmt(pf_mod.N1_BANDS[244][\"a\"][1])}),') == 2")
print("[244]==2 full-line count %d" % T0.count(_line244))
_line243 = ("assert n1_t4.count(f'assert pf.N1_BANDS[243] == {{\"a\": ({fmt(pf_mod.N1_BANDS[243][\"a\"][0])}"
            ", {fmt(pf_mod.N1_BANDS[243][\"a\"][1])}),') == 3")
print("[243]==3 full-line count %d" % T0.count(_line243))
