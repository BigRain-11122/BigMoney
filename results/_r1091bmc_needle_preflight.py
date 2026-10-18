# -*- coding: utf-8 -*-
# r1091 bm-c: W268 five-face splice editor -- MEASURED needle preflight
# (r1077 measured-counts law; canon = results/_w267bmc_freeze_edits.py,
# blob sha16 0b39fb0f20c8aa6e per the r1089 handoff receipt
# results/_r1089bmc_w268_editor_handoff.json; this probe re-measures EVERY
# candidate needle at authoring time + dumps ambiguous-face contexts
# (r-window numbers / seat shas / parity counts) for precise editor design.
# Read-only. Zero mutation. Receipt -> results/_r1091bmc_needle_preflight.json
import hashlib, io, json, subprocess, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = REPO + r"\results\_w267bmc_freeze_edits.py"

def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, encoding="utf-8", errors="replace")

blob_wt = git("hash-object", CANON).stdout.strip()
blob_head = git("rev-parse", "HEAD:results/_w267bmc_freeze_edits.py").stdout.strip()
sha256_full = hashlib.sha256(open(CANON, "rb").read()).hexdigest()

t = io.open(CANON, encoding="utf-8", newline="").read()
lines = t.split("\n")

faces = [
    # ---- projections (phase1) ----
    "W268p", "W268", "W269p", "W269", "W270", "W267p",
    # ---- bands (phase1, consumers then producers) ----
    "604_701", "604_900", "602_701", "604_700", "602_900", "604_500",
    "602_501", "602_700", "604_901", "605_100", "606_700", "606_900",
    "606_901", "607_100", "602_500", "600_501", "600_301", "600_500",
    "600_700", "602_300", "598_101", "598_300", "598_301", "600_300",
    "598_500", "600_100", "593901",
    # ---- ledger/K anchors (phase1) ----
    "1,009,535", "583,120", "1_009_535", "583_120", "1,011,735", "585,320",
    "1,007,335", "580,920", "1_007_335", "580_920",
    # ---- lowercase machine tokens (phase1) ----
    "n1_w267", "n1_w266", "n1w267-", "n1w266-", "w267_", "w266_",
    "n1_w268", "w268_", "_w267bmc_", "_w268bmc_", "_w266bmc_",
    "n1_w267_results.json", "n1_w266_results.json",
    # ---- seat/sha faces (phase1) ----
    "MSG-20261018-1025-bmc-w267-seat", "MSG-20261018-1229-bmc-w268-seat",
    "942ebd5885", "b9ad2f1119", "dc71ecc3f9", "7b9e9377", "df55e3fab9",
    "f1ec8231c7", '"wave": 266', '"wave": 267', '"wave": 268',
    "942ebd5885 r1086", "origin 942ebd5885", "942ebd5885 BEFORE",
    # ---- setwave aging faces ----
    "_set_wave(267)", "_set_wave(266)", "_set_wave(265)", "_set_wave(268)",
    "_set_wave(2)",
    # ---- phase2 blanket raws ----
    "W267", "W266", "W265", "W264",
    # ---- relation-assert / bands-respected (pre+post blanket forms) ----
    "W264_W265_W266_bands_respected", "W265_W266_W267_bands_respected",
    "A_staircase_hop_past_W266_B", "B_base_above_W266_tail",
    "A_staircase_hop_past_W267_B", "B_base_above_W267_tail",
    # ---- parity/legs faces ----
    "W211..W247 legs (37)", "W211..W247 verbatim (37 legs)",
    "W211..W247 thirty-seven legs", "W211..W265 legs (55)",
    "W211..W266 legs 55", "own W248..W265 legs (18)", "own W248..W265",
    "W248..W266 legs (19", "W248..W265 eighteen legs",
    "W248..W267 legs", "W249..W267", "block = 125 rows", "125 parity rows",
    "block parity = 121 rows", "block parity = 125 rows", "121 rows",
    "fifty-five legs", "fifty-six legs", "fifty-fifth", "fifty-sixth",
    '"fresh_legs_row_asserts": 19', '"fresh_legs_row_asserts": 20',
    "+ 19,", "+ 20,",
    # ---- count-gate numerals ----
    'N1_BANDS[") == 124,', 'N1_BANDS[") == 125,', '!= 124', '!= 125',
    'N1_BANDS[") == 55', 'N1_BANDS[") == 56', 'N1_BANDS[") == 37',
    "== 123", "!= 123",
    # ---- ranges ----
    "range(248, 267)", "range(248, 266)", "range(248, 268)",
    "range(211, 248)", "range(211, 266)", "range(211, 267)",
    "range(16, 267)", "range(16, 268)", "range(17, 267)", "range(17, 268)",
    "range(209, 268)", "range(209, 269)", "range(138, 207)",
    "if w < 267)", "if w < 266)", "if w < 268)",
    "267 - _lw", "268 - _lw", "m248", "m247", "m211",
    "N1_BANDS[248] ==", "N1_BANDS\\[248\\]",
    # ---- cfg/dict faces ----
    'WAVE_CONFIGS[267]', 'WAVE_CONFIGS[266]', 'WAVE_CONFIGS[268]',
    'N1_BANDS[266]', 'get(266)', 'get(267)', '_c266', '_c267',
    '267: {"batch"', '266: {"batch"', '268: {"batch"',
    '267: {{"batch"', '268: {{"batch"', '267: {"a"', '266: {"a"',
    '267: {{"a"', '268: {{"a"', '265: {"batch"',
    "arith_a267", "arith_b267", "arith_a268", "arith_b268",
    "(263, 262, 261, 260, 259, 258, 257, 256, 255, 254)",
    "(264, 263, 262, 261, 260, 259, 258, 257, 256, 255)",
    "W254..W263", "W255..W264",
    # ---- ordinals ----
    "len(owner_rows_live) == 256", "len(owner_rows_live) == 257",
    "256/130/85", "257/130/86", "bmc_rows=85", "bmc_rows=86",
    "rows 256 + candidate = 257th", "rows 257 + candidate = 258th",
    "owner_rows=256 / bma_rows=130 / bmc_rows=85",
    "; bm-c rows 85 +", "bm-c rows 85 + candidate = 86th owned",
    "bm-c rows 86 + candidate = 87th owned",
    "# candidate = 86th EXACT", "# candidate = 87th EXACT",
    "engine_owner==bm-c rows 85 + candidate",
    "(86th own wave", "(87th own wave",
    "bm-c's 86th own wave", "bm-c's 87th own wave",
    "EIGHTY-SIXTH owned", "EIGHTY-SEVENTH owned",
    "TWO HUNDRED AND SIXTY-SEVENTH", "TWO HUNDRED AND SIXTY-EIGHTH",
    "SEVENTEENTH", "SIXTEENTH", "EIGHTEENTH",
    "seventeenth", "sixteenth", "eighteenth", "fifty-fourth",
    "bma rows 129 + candidate 130th",
    '"probe_receipt_bmc_ordinal_face": 85',
    '"probe_receipt_bmc_ordinal_face": 86',
    # ---- wave-number narrative ----
    "wave 267 engine_owner=bm-c", '"wave 267: "', "wave 267 = first free number",
    "wave 268 engine_owner=bm-c", '"wave 268: "', "wave 268 = first free number",
    # ---- prereg/commitment faces ----
    "PERPETUAL_N1_W267_PREREG", "PERPETUAL_N1_W268_PREREG",
    "PERPETUAL-N1-W267", "PERPETUAL-N1-W268",
    "bm-c r1087 window", "bm-a r1087 window", "# r1087 window", "r1087 commit",
    "bm-c r1090 window", "authored 10:5x", "authored 09:0x",
    "2026-10-18 11:2x bm-c r1088 freeze window",
    # ---- cycle/lineage window stamps (measure + context dump) ----
    "r1085", "r1086", "r1087", "r1088", "r1089", "r1090", "r1091", "r1081", "r1084",
    "10:2x", "10:5x", "11:2x", "12:3x", "13:1x", "13:4x",
    "cycle COMPLETE bm-c r1085+r1086 closeout 10:5x",
    "the bm-c r1086 splice window", "bm-c r1086 splice window",
    "own-wave full cycle r1086", "bm-c splice generation r1086 window",
    "r1086, pre-seat probe", "verified r1087", "# r1086 splice window",
    "(bm-c r1086", "r1086 BEFORE this freeze", "r1086 MSG-",
    "finalize one-pass bm-c r1086 closeout, ledger",
    "finalize one-pass bm-c r1086 closeout ledger",
    "finalize one-pass bm-c r1086",
    "(R266: ", "(R267: ", "_w == 266", "_w == 267",
    "_w266bmc_freeze_edits.py template", "_w267bmc_freeze_edits.py template",
    "W267 FREEZE UNBLOCKED", "W268 FREEZE UNBLOCKED",
    "was published AFTER", "bm-a own-seat continuity",
    "bm-c own-seat continuity", "registered wave below 263 composes",
    "w244_a holds wave-263 bands", "w244_a", "w244_b", "n3r1_used245",
    "PENDING at seat", "waits-upstream face disclosed honest",
    "20261017", "20261018", "editor template",
]
counts = {f: t.count(f) for f in faces}

# ---- context dumps for ambiguous faces ----
def ctx(needle, maxhits=40):
    out = []
    for i, ln in enumerate(lines, 1):
        if needle in ln:
            out.append({"line": i, "text": ln.strip()[:200]})
    return out[:maxhits]

contexts = {}
for needle in ("r1085", "r1086", "r1087", "942ebd5885", "own W248..W265",
               "block parity", "fresh_legs", "+ 19,", "authored 10:5x",
               "r1086 MSG-", "pre-seat probe", "121 rows", "125 rows",
               "eighteen legs", "bm-a r1087"):
    contexts[needle] = ctx(needle)

# ---- W268 prereg commit timestamp (authored-stamp basis) ----
prereg_ci = git("show", "-s", "--format=%ci", "f1ec8231c7").stdout.strip()
prereg_cf = git("show", "-s", "--format=%cI", "f1ec8231c7").stdout.strip()

receipt = {
    "probe": "r1091 bm-c W268 editor needle preflight (r1077 measured-counts law, authoring-time re-measure)",
    "canon": {"path": "results/_w267bmc_freeze_edits.py", "blob_wt": blob_wt,
              "blob_head": blob_head, "sha256_full": sha256_full,
              "sha16": sha256_full[:16], "bytes": len(t.encode("utf-8")),
              "wt_eq_head": blob_wt == blob_head},
    "handoff_expect": {"sha16": "0b39fb0f20c8aa6e", "blob": "05ae8eeb2c8a0e2de5444560ba0aa62a4e60a5d8", "bytes": 62156},
    "w268_prereg_commit": {"sha": "f1ec8231c7", "ci": prereg_ci, "cI": prereg_cf},
    "counts": counts,
    "contexts": contexts,
    "verdict": "MEASURED",
}
io.open(REPO + r"\results\_r1091bmc_needle_preflight.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print(json.dumps({"wt_eq_head": blob_wt == blob_head, "sha16": sha256_full[:16],
                  "bytes": len(t.encode("utf-8")), "blob_wt": blob_wt[:16],
                  "prereg_ci": prereg_ci}, indent=1))
print("KEY COUNTS:", json.dumps({k: counts[k] for k in (
    "W268p", "W268", "W267", "W266", "604_701", "604_900", "602_701", "604_700",
    "602_900", "604_500", "602_501", "602_700", "n1_w267", "n1_w266", "w267_",
    "w266_", "_w267bmc_", "r1085", "r1086", "r1087", "r1088", "942ebd5885",
    "SEVENTEENTH", "SIXTEENTH", "seventeenth", "sixteenth", "W269p", "W269",
    "_set_wave(267)")}, indent=1))
