# -*- coding: utf-8 -*-
# r1088 bm-c: W267 splice-editor needle preflight (r1077 measured-counts law).
# Measures EVERY candidate needle face on the committed canon
# results/_w266bmc_freeze_edits.py (W266 freeze editor, landed dc71ecc3f9 chain)
# BEFORE authoring results/_w267bmc_derive_editor.py. Zero assumption:
# all counts + all ambiguous line contexts printed/dumped for editor authoring.
import io, json, re, subprocess, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = REPO + r"\results\_w266bmc_freeze_edits.py"
OUT = REPO + r"\results\_r1088bmc_needle_counts.json"

blob_wt = subprocess.run(["git", "-C", REPO, "hash-object", CANON],
                         capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "-C", REPO, "rev-parse",
                            "HEAD:results/_w266bmc_freeze_edits.py"],
                           capture_output=True, text=True).stdout.strip()
t = io.open(CANON, encoding="utf-8", newline="").read()
lines = t.split("\n")
print(f"canon bytes {len(t.encode('utf-8'))} lines {len(lines)}")
print(f"blob wt={blob_wt[:16]} head={blob_head[:16]} eq={blob_wt == blob_head}")

def C(s):
    return t.count(s)

tokens = [
 # projections + wave forms
 "W268p", "W267p", "W267", "W266p", "W266", "W265", "W264", "W263", "W262",
 # band tokens (current W266 + prior W265 + projection + new W267)
 "602_501", "602_700", "600_501", "602_500", "600_700", "602_300",
 "600_301", "600_500", "598_101", "598_300", "598_301", "600_300",
 "598_500", "600_100",
 "604_701", "604_900", "602_701", "604_700", "602_900", "604_500",
 "605_100", "606_700", "604_901",
 # ledger / K anchors
 "1,007,335", "580,920", "1_007_335", "580_920",
 "1,009,535", "583,120", "1_009_535", "583_120", "996,335",
 # lowercase machine-file tokens
 "n1_w266", "n1_w265", "n1_w264", "n1w266-", "n1w265-",
 "w266_", "w265_", "w264_", "w267_", "w244_a", "w244_b", "n3r1_used245",
 # receipt / script path prefixes
 "_w266bmc_", "_w267bmc_", "_w265bmc_", "_w265bmc_freeze_edits_TOL.py template",
 # seat / origins / shas (prose refs)
 "MSG-20261018-0719-bmc-w266-seat", "MSG-20261018-1025-bmc-w267-seat",
 "ace19ba85b", "942ebd5885", "595433d63c", "df55e3fab9",
 "a47517f79", "dc71ecc3f9", "7343e3650", "216b578b0",
 # dates
 "20261018", "20261017", "2026-10-18 10:2x bm-c r1086 freeze window",
 # relkey
 "W263_W264_W265_bands_respected", "W264_W265_W266_bands_respected",
 # parity narratives
 "W211..W246 legs (36)", "W211..W264 legs (54)", "W211..W265 legs (54)",
 "W247..W264 legs (18)", "own W247..W264", "W247..W264 eighteen legs",
 "W247..W265 legs (19", "W211..W246 verbatim (36 legs)",
 "W211..W246 thirty-six legs", "W211..W264 fifty-four legs",
 "W211..W266", "W248", "thirty-seven", "fifty-five", "fifty-fourth",
 "fifty-four legs", "fifty-fifth",
 # counts / ranges
 "block = 124 rows", "124 parity rows", "block = 123 rows", "123 parity rows",
 'N1_BANDS[") == 123,', "!= 123", 'N1_BANDS[") == 122,', 'N1_BANDS[") == 54',
 'N1_BANDS[") == 36', 'N1_BANDS[") == 53', 'N1_BANDS[") == 35',
 "range(211, 247)", "range(211, 246)", "range(211, 265)", "range(211, 264)",
 "range(247, 265)", "range(246, 264)", "range(247, 266)", "range(246, 265)",
 "range(16, 266)", "range(16, 265)", "range(17, 266)", "range(17, 265)",
 "range(209, 267)", "range(209, 266)", "range(138, 207)", "range(247, 266)",
 "if w < 266)", "if w < 265)", "if w < 264)", "if w < 267)",
 "266 - _lw", "265 - _lw",
 "N1_BANDS\\[247\\]", "m247", "m246", "N1_BANDS[247] ==", "N1_BANDS[246] ==",
 "N1_BANDS\\[248\\]", "m248", "N1_BANDS[248] ==",
 # cfg / row dict faces
 "WAVE_CONFIGS[266]", "WAVE_CONFIGS[265]", "WAVE_CONFIGS[264]",
 "N1_BANDS[265]", "N1_BANDS[264]", "N1_BANDS[266]", "get(265)", "get(264)",
 "_c265", "_c264",
 '266: {"batch"', '265: {"batch"', '264: {"batch"',
 '266: {{"batch"', '266: {"a"', '265: {"a"', '266: {{"a"', '265: {{"a"',
 '264: {"a"', '267: {"batch"',
 "arith_a266", "arith_b266", "arith_a265", "arith_b265",
 "(262, 261, 260, 259, 258, 257, 256, 255, 254, 253)",
 "(263, 262, 261, 260, 259, 258, 257, 256, 255, 254)",
 "W253..W262", "W254..W263",
 # ordinals
 "len(owner_rows_live) == 255 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 84",
 "len(owner_rows_live) == 256 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 85",
 "255/130/84", "256/130/85",
 "owner_rows=255 / bma_rows=130 / bmc_rows=84",
 "owner_rows=256 / bma_rows=130 / bmc_rows=85",
 "rows 255 + candidate = 256th", "rows 256 + candidate = 257th",
 "; bm-c rows 84 +", "; bm-c rows 85 +",
 "bm-c rows 84 + candidate = 85th owned", "bm-c rows 85 + candidate = 86th owned",
 "# candidate = 85th EXACT", "# candidate = 86th EXACT",
 "engine_owner==bm-c rows 84 + candidate", "engine_owner==bm-c rows 85 + candidate",
 "(84th own wave", "(85th own wave", "(86th own wave",
 "bm-c's 85th own wave", "bm-c's 86th own wave", "bm-c's 84th own wave",
 "EIGHTY-FIFTH owned", "EIGHTY-SIXTH owned", "EIGHTY-FOURTH owned",
 "TWO HUNDRED AND SIXTY-SIXTH", "TWO HUNDRED AND SIXTY-SEVENTH",
 "TWO HUNDRED AND SIXTY-FIFTH",
 "bmc_rows=84", "bmc_rows=85", 'bmc_rows=85": 85',
 '"probe_receipt_bmc_ordinal_face": 84', '"probe_receipt_bmc_ordinal_face": 85',
 "SIXTEENTH", "SEVENTEENTH", "FIFTEENTH", "FOURTEENTH",
 "sixteenth", "seventeenth", "fifteenth",
 # wave-number narrative
 "wave 265 engine_owner=bm-c", "wave 266 engine_owner=bm-c",
 '"wave 265: "', '"wave 266: "',
 "wave 265 = first free number", "wave 266 = first free number",
 # cycle lineage windows
 "cycle COMPLETE bm-c r1081+r1084 closeout 07:0x",
 "cycle COMPLETE bm-c r1085+r1086 closeout",
 "the bm-c r1084 splice window", "the bm-c r1086 splice window",
 "own-wave full cycle r1084", "own-wave full cycle r1086",
 "bm-c splice generation r1084 window", "bm-c splice generation r1086 window",
 "bm-c r1076", "r1084, pre-seat probe", "r1086, pre-seat probe",
 "verified r1085", "verified r1087",
 "seat itself r1084; queue-head", "seat itself r1086; queue-head",
 "(r1084, queue-head seat-first supply", "(r1086, queue-head seat-first supply",
 "finalize one-pass bm-c r1084 closeout, ledger",
 "finalize one-pass bm-c r1084 closeout ledger",
 "finalize one-pass bm-c r1086 closeout",
 "(r1084 MSG-", "(r1086 MSG-",
 "r1084 BEFORE this freeze", "r1086 BEFORE this freeze",
 "bm-c r1085 window", "bm-c r1087 window", "# r1085 window", "# r1087 window",
 "r1085 commit", "r1087 commit",
 "authored 09:0x", "authored 10:4x", "authored 10:5x",
 "(R265: ", "(R266: ", "_w == 265", "_w == 266",
 "anchors W265 1,007,335 / K=580,920 at draft",
 "w244_a holds wave-263 bands", "w244_a holds wave-266 bands",
 # misc structural
 "wave\": 265", "wave\": 266", "wave\": 264",
 "PENDING at seat", "waits-upstream face disclosed honest",
 "bm-a five-face freeze upstream seat", "bm-c five-face freeze upstream seat",
 "bm-a (upstream seat honored)", "bm-c (upstream seat honored)",
 "owner=bm-a seat honored", "owner=bm-c seat honored",
 "was published BEFORE", "was published AFTER",
 "fourteen-wave", "post-W265-REGISTERED", "post-W266-REGISTERED",
 "W267 FREEZE UNBLOCKED", "W268 FREEZE UNBLOCKED",
 "dual-window parity", "W267 walk", "W268 walk",
 "PERPETUAL_N1_W266_PREREG", "PERPETUAL_N1_W267_PREREG",
 "PERPETUAL-N1-W266", "PERPETUAL-N1-W267",
 "W266 materializer face", "W267 materializer face",
 "W266 block parity", "121 rows", "125 rows",
 "fifty-fourth consecutive", "fifty-fifth consecutive",
 "gate0.5", "W265 finalize product", "W266 finalize product",
 "n1_w266_results.json", "n1_w265_results.json", "n1_w267_results.json",
]
counts = {k: C(k) for k in tokens}
print("\n== COUNTS ==")
for k, v in counts.items():
    print(f"{v:5d}  {k!r}")

# ambiguous band tokens: print every containing line (numbered)
amb = ["600_301", "600_501", "600_700", "602_300", "602_501", "602_500",
       "602_700", "598_101", "598_300", "598_500", "600_100"]
print("\n== AMBIGUOUS LINE CONTEXTS ==")
for i, ln in enumerate(lines):
    for a in amb:
        if a in ln:
            print(f"[{i+1}] [{a}] {ln.strip()[:240]}")
            break

# downstream_seat + receipt wave + own_seat_face verbatim
m = re.search(r'"downstream_seat": "(.*?)",\n', t, re.S)
print("\n== downstream_seat verbatim ==")
print(m.group(1) if m else "NOT FOUND")
m2 = re.search(r'"wave": (\d+),', t)
print("receipt wave field:", m2.group(1) if m2 else "NOT FOUND")

# prior receipt wave field (stale-face adjudication)
try:
    prev = json.load(open(REPO + r"\results\_w265bmc_freeze_receipt.json",
                         encoding="utf-8"))
    print("W265 receipt wave field:", prev.get("wave"))
except Exception as e:
    print("W265 receipt read fail:", e)

json.dump({"canon_bytes": len(t.encode("utf-8")), "blob_wt": blob_wt,
           "blob_head": blob_head, "counts": counts},
          open(OUT, "w", encoding="utf-8"), indent=1)
print("\nPREFLIGHT OK ->", OUT)
